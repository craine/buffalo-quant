"""Fetch NHL regular-season play-by-play from the public NHL API (api-web.nhle.com).

Runs in GitHub Actions (the analysis workspace cannot reach the NHL API directly).
Writes, per season, to out/:
  nhl_plays_{season}.parquet   every play event, flattened (pd.json_normalize), plus game_id
  nhl_games_{season}.parquet   one row per game: ids, date, teams, final score, game state, period count
  nhl_rosters_{season}.parquet one row per (game, player): team, position, name
Only completed games (gameState OFF or FINAL) are kept. Nothing is imputed.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

BASE = "https://api-web.nhle.com/v1/gamecenter/{gid}/play-by-play"
OUT = Path("out")
SEASONS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["20232024", "20242025", "20252026", "20262027"]
MAX_GAMES = 1400  # 32 teams x 82 / 2 = 1312 regular-season games


def get(gid, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE.format(gid=gid), headers={"User-Agent": "buffalo-quant-ingest"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    raise RuntimeError(f"failed {gid}")


def fetch_season(season):
    start = season[:4]
    ids = [int(f"{start}02{n:04d}") for n in range(1, MAX_GAMES + 1)]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(get, ids))
    games, plays, rosters = [], [], []
    for gid, g in zip(ids, results):
        if g is None or g.get("gameState") not in ("OFF", "FINAL"):
            continue
        games.append({
            "game_id": gid, "season": int(season), "game_date": g.get("gameDate"),
            "home_id": g["homeTeam"]["id"], "home": g["homeTeam"]["abbrev"], "home_score": g["homeTeam"].get("score"),
            "away_id": g["awayTeam"]["id"], "away": g["awayTeam"]["abbrev"], "away_score": g["awayTeam"].get("score"),
            "game_state": g.get("gameState"),
            "last_period_type": (g.get("gameOutcome") or {}).get("lastPeriodType"),
            "n_periods": max((p.get("periodDescriptor", {}).get("number", 0) for p in g.get("plays", [])), default=0),
        })
        p = pd.json_normalize(g.get("plays", []), sep="_")
        p["game_id"] = gid
        plays.append(p)
        for r in g.get("rosterSpots", []):
            rosters.append({"game_id": gid, "team_id": r.get("teamId"), "player_id": r.get("playerId"),
                            "first": (r.get("firstName") or {}).get("default"),
                            "last": (r.get("lastName") or {}).get("default"),
                            "pos": r.get("positionCode"), "number": r.get("sweaterNumber")})
    OUT.mkdir(exist_ok=True)
    pd.DataFrame(games).to_parquet(OUT / f"nhl_games_{season}.parquet", index=False)
    pl = pd.concat(plays, ignore_index=True)
    for c in pl.columns:  # mixed object columns -> string so parquet is stable
        if pl[c].dtype == object:
            pl[c] = pl[c].astype("string")
    pl.to_parquet(OUT / f"nhl_plays_{season}.parquet", index=False)
    pd.DataFrame(rosters).to_parquet(OUT / f"nhl_rosters_{season}.parquet", index=False)
    print(season, "games", len(games), "plays", len(pl), flush=True)


if __name__ == "__main__":
    for s in SEASONS:
        fetch_season(s)
