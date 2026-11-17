"""Streak Watch: find every active NFL streak worth talking about and rank it against every streak since 1999.

Data: raw_pbp_history (1999-2017) + raw_pbp (2018 on), regular season and playoffs in date order. Team abbreviations
are mapped to today's (OAK->LV, SD->LAC, STL->LA) so franchises carry their history.

A streak is a run of consecutive units (drives or games) that meet a test. For each kind we return:
- every team's (or player's) active streak, with
- its rank among ALL streaks of that kind since 1999 (league), and among that franchise's own (franchise),
- the last time the franchise had one at least this long ("longest since").
Counts can differ from team PR departments: the NFL's drive charts merge or drop some short possessions that the
play-by-play counts as drives. We say so wherever we publish a drive count.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.db import query

ERA = {"OAK": "LV", "SD": "LAC", "STL": "LA"}
COLS = ("season, season_type, week, game_id, game_date, play_id, posteam, defteam, fixed_drive, fixed_drive_result, "
        "play_type, pass, rush, qb_dropback, sack, interception, fumble_lost, touchdown, pass_touchdown, rush_touchdown, "
        "return_touchdown, td_team, passer_player_id, rusher_player_id, receiver_player_id, td_player_id, two_point_attempt, "
        "total_home_score, total_away_score, home_team, away_team")


def plays(min_season=1999):
    p = query(f"SELECT {COLS} FROM raw_pbp_history WHERE season >= {min_season} UNION ALL SELECT {COLS} FROM raw_pbp")
    for c in ("posteam", "defteam", "td_team", "home_team", "away_team"):
        p[c] = p[c].replace(ERA)
    return p.sort_values(["game_date", "game_id", "play_id"]).reset_index(drop=True)


# ---------------------------------------------------------------- units
def defensive_drives(p):
    """One row per drive faced, in order: team (defense), allowed_td."""
    d = (p.dropna(subset=["posteam", "fixed_drive"]).groupby(["game_date", "game_id", "fixed_drive"], sort=False)
         .agg(team=("defteam", "first"), res=("fixed_drive_result", "last"), season=("season", "first")).reset_index())
    d["ok"] = d.res != "Touchdown"
    d["label"] = d.game_id
    return d[["team", "season", "game_id", "game_date", "ok", "label"]]


def team_games(p):
    """One row per team-game: points for/against, takeaways, sacks made, giveaways."""
    last = p.groupby("game_id").agg(home=("home_team", "first"), away=("away_team", "first"), hs=("total_home_score", "max"),
                                     as_=("total_away_score", "max"), date=("game_date", "first"), season=("season", "first"))
    rows = []
    for g, r in last.iterrows():
        rows.append((g, r.date, r.season, r.home, r.away, r.hs, r.as_))
        rows.append((g, r.date, r.season, r.away, r.home, r.as_, r.hs))
    t = pd.DataFrame(rows, columns=["game_id", "game_date", "season", "team", "opp", "pf", "pa"])
    s = p.groupby(["game_id", "defteam"]).agg(sacks=("sack", "sum"), ints=("interception", "sum"), fum=("fumble_lost", "sum"))
    s["takeaways"] = s.ints + s.fum
    t = t.merge(s.reset_index().rename(columns={"defteam": "team"}), on=["game_id", "team"], how="left")
    gv = p.groupby(["game_id", "posteam"]).agg(gints=("interception", "sum"), gfum=("fumble_lost", "sum")).reset_index()
    gv["give"] = gv.gints + gv.gfum
    t = t.merge(gv.rename(columns={"posteam": "team"})[["game_id", "team", "give"]], on=["game_id", "team"], how="left")
    return t.fillna({"sacks": 0, "takeaways": 0, "give": 0}).sort_values(["game_date", "game_id"]).reset_index(drop=True)


def player_games(p, ids=None):
    """One row per player-game where he took part as passer, rusher or receiver: TDs scored, pass TDs thrown."""
    parts = []
    for col in ("passer_player_id", "rusher_player_id", "receiver_player_id"):
        x = p.dropna(subset=[col])[["game_id", "game_date", "season", "posteam", col]].rename(columns={col: "player"})
        parts.append(x)
    g = pd.concat(parts).drop_duplicates(["game_id", "player"])
    if ids is not None:
        g = g[g.player.isin(ids)]
    sc = (p[(p.touchdown == 1) & p.td_player_id.notna() & (p.td_team == p.posteam)].groupby(["game_id", "td_player_id"]).size()
          .rename("tds").reset_index().rename(columns={"td_player_id": "player"}))
    pt = (p[(p.pass_touchdown == 1)].groupby(["game_id", "passer_player_id"]).size().rename("ptd").reset_index()
          .rename(columns={"passer_player_id": "player"}))
    g = g.merge(sc, on=["game_id", "player"], how="left").merge(pt, on=["game_id", "player"], how="left").fillna({"tds": 0, "ptd": 0})
    return g.rename(columns={"posteam": "team"}).sort_values(["game_date", "game_id"]).reset_index(drop=True)


# ---------------------------------------------------------------- runs
def runs(units, key, ok_col="ok", latest=None):
    """All runs of consecutive ok units per key: key, team, length, start/end game, end season, active.

    `team` is the team at the run's last unit. A run is active only if it reaches the key's last unit AND that unit is
    in its team's latest game (`latest`: team -> game_id); otherwise a retired player's last run would count as alive.
    """
    out = []
    for k, u in units.groupby(key, sort=False):
        ok = u[ok_col].to_numpy(); gid = u.game_id.to_numpy(); sea = u.season.to_numpy(); tm = u.team.to_numpy()
        n, start = 0, None
        for i, v in enumerate(ok):
            if v:
                if n == 0:
                    start = i
                n += 1
            elif n:
                out.append((k, tm[i - 1], n, gid[start], gid[i - 1], int(sea[i - 1]), False)); n = 0
        if n:
            j = len(ok) - 1
            alive = latest is None or latest.get(tm[j]) == gid[j]
            out.append((k, tm[j], n, gid[start], gid[j], int(sea[j]), bool(alive)))
    return pd.DataFrame(out, columns=["key", "team", "length", "start_game", "end_game", "end_season", "active"])


@dataclass
class Kind:
    name: str          # plain-English name
    unit: str          # "drives" or "games"
    who: str           # "team" or "player"


def ranked(r, kind):
    """Active runs with league rank (all runs since 1999), franchise rank (all runs for that team, by anyone), and
    the last season the franchise had a run at least this long ("longest since")."""
    rows = []
    for x in r[r.active].itertuples():
        mine = r[r.team == x.team]
        prev = mine[(~mine.active) & (mine.length >= x.length)]
        rows.append(dict(kind=kind.name, unit=kind.unit, who=kind.who, key=x.key, team=x.team, length=int(x.length),
                         league_rank=int((r.length > x.length).sum()) + 1, league_runs=len(r),
                         franchise_rank=int((mine.length > x.length).sum()) + 1,
                         last_as_long=(int(prev.end_season.max()) if len(prev) else None),
                         last_as_long_len=(int(prev.sort_values("end_season").length.iloc[-1]) if len(prev) else None),
                         start_game=x.start_game, end_game=x.end_game))
    return pd.DataFrame(rows)


def scan(p=None):
    """Every active streak of every kind, ranked. Team keys are abbreviations; player keys are gsis ids."""
    p = plays() if p is None else p
    latest = p.groupby("posteam").game_id.last().to_dict()
    out = []
    dd = defensive_drives(p)
    out.append(ranked(runs(dd, "team", latest=latest), Kind("drives without allowing a touchdown", "drives", "team")))
    tg = team_games(p)
    tests = [("games with a takeaway", tg.takeaways > 0), ("games with a sack", tg.sacks > 0),
             ("games scoring 20 or more points", tg.pf >= 20), ("games without a turnover", tg.give == 0),
             ("games allowing 20 points or fewer", tg.pa <= 20)]
    for name, ok in tests:
        out.append(ranked(runs(tg.assign(ok=ok.to_numpy(), key=tg.team), "key", latest=latest), Kind(name, "games", "team")))
    pg = player_games(p)
    for name, ok in (("games with a touchdown", pg.tds > 0), ("games with a touchdown pass", pg.ptd > 0)):
        u = pg.assign(ok=ok.to_numpy())
        if name == "games with a touchdown pass":   # passers only
            passers = set(p.passer_player_id.dropna())
            u = u[u.player.isin(passers)]
        out.append(ranked(runs(u, "player", latest=latest), Kind(name, "games", "player")))
    return pd.concat(out, ignore_index=True)


MIN_LEN = {"drives": 15, "games": 4}


def notable(a, team=None, top_league=10, since_years=10, this_season=2026):
    """Streaks worth a post (all three need a minimum length so 3-game runs don't flood it):
    franchise-best since 1999, top-`top_league` league-wide since 1999, or the franchise's longest in `since_years`+."""
    long_enough = a.length >= a.unit.map(MIN_LEN)
    since = a.last_as_long.isna() | (this_season - a.last_as_long >= since_years)
    x = a[long_enough & ((a.franchise_rank == 1) | (a.league_rank <= top_league) | since)]
    if team:
        x = x[x.team == team]
    return x.sort_values(["league_rank", "franchise_rank"])
