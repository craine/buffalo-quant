"""Goalie cards: one baseball-card-style record per goalie, pinned to AS_OF. Every number computed here.

Writes reports/cards/goalies.json, which src/site/build.py renders as /cards/.
Goals saved vs. average = expected goals against minus goals against, on unblocked non-empty-net shots, xG rescaled
per season so league xG = league goals. The blended rate mixes this season with past seasons and shrinks toward
average, so a hot or cold dozen games doesn't dominate; it moves toward this season as shots pile up.
"""
import json

import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots

AS_OF = "2026-11-10"
SEASON = 20262027
TEAMS = ["BUF", "VGK"]          # cards built for every goalie who has played for these teams this season
SHRINK_SHOTS = 600              # shots of "average" added to the blend
PAST_WEIGHT = 0.5               # each past season's shots count half
OUT = ROOT / "reports" / "cards"
SEASON_LABEL = lambda s: f"{str(s)[:4]}-{str(s)[6:]}"


def main(as_of=AS_OF, league=False):
    s = shots()
    gm = query(f"SELECT game_id, game_date FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(gm.game_id))].copy()
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0)].copy()
    cal = u.groupby("season").goal.sum() / u.groupby("season").xg.sum()
    u["xg"] = u.xg * u.season.map(cal)
    u = u[u.goalie_id.notna()].merge(gm, on="game_id")
    ros = query("SELECT player_id, season, team_id, first, last, number, pos FROM raw_nhl_rosters")
    name = ros.groupby("player_id").apply(lambda x: f"{x['first'].iloc[-1]} {x['last'].iloc[-1]}")

    by = u.groupby(["season", "goalie_id", "opp"]).agg(gp=("game_id", "nunique"), sog=("on_goal", "sum"),
                                                       xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    by["gsax"] = by.xga - by.ga
    cur = by[by.season == SEASON].groupby("goalie_id").agg(gp=("gp", "sum"), sog=("sog", "sum"), xga=("xga", "sum"), ga=("ga", "sum"))
    cur["gsax"] = cur.xga - cur.ga
    cur["rk"] = cur.gsax.rank(ascending=False, method="min").astype(int)
    n_cur = len(cur)
    lg_sv = 1 - u[u.season == SEASON].goal.sum() / u[u.season == SEASON].on_goal.sum()
    close = u[(u.season == SEASON) & (u.dist < 20)]
    lg_close_sv = 1 - close.goal.sum() / close.on_goal.sum()

    # blended goals saved per 100 shots, for every goalie with current-season shots (so the rank is comparable)
    def blend(gid):
        x = by[by.goalie_id == gid]
        c, p = x[x.season == SEASON], x[x.season < SEASON]
        num = c.gsax.sum() + PAST_WEIGHT * p.gsax.sum()
        den = c.sog.sum() + PAST_WEIGHT * p.sog.sum() + SHRINK_SHOTS
        return 100 * num / den
    cur["blend"] = [blend(g) for g in cur.index]
    cur["blend_rk"] = cur.blend.rank(ascending=False, method="min").astype(int)

    cards = []
    cu = u[u.season == SEASON]
    latest = cu.sort_values(["game_date", "game_id"]).groupby("goalie_id").opp.last()     # team he played for most recently
    teams = sorted(cu.opp.unique()) if league else TEAMS
    for team in teams:
        ids = by[(by.season == SEASON) & (by.opp == team)].sort_values("gp", ascending=False).goalie_id.unique()
        if league:
            ids = [g for g in ids if latest.get(g) == team]
        for gid in ids:
            gid = int(gid)
            c = cur.loc[gid]
            mine = u[(u.season == SEASON) & (u.goalie_id == gid)]
            g_close = mine[mine.dist < 20]
            # cumulative goals saved vs average, game by game, this season
            pg = mine.groupby(["game_date", "game_id"]).apply(lambda x: x.xg.sum() - x.goal.sum()).cumsum()
            num = ros[(ros.player_id == gid) & (ros.season == SEASON)].number.dropna()
            seasons = []
            for r in by[by.goalie_id == gid].sort_values("season").itertuples():
                seasons.append(dict(season=SEASON_LABEL(r.season), team=r.opp, gp=int(r.gp), sog=int(r.sog),
                                    sv=round(1 - r.ga / r.sog, 3) if r.sog else None, gsax=round(float(r.gsax), 1)))
            cards.append(dict(
                id=gid, name=name.get(gid, str(gid)), team=team, number=int(num.mode().iloc[0]) if len(num) else None,
                gp=int(c.gp), sog=int(c.sog), sv=round(1 - c.ga / c.sog, 3), xsv=round(1 - c.xga / c.sog, 3),
                gsax=round(float(c.gsax), 1), rk=int(c.rk), of=n_cur,
                close_sv=round(1 - g_close.goal.sum() / g_close.on_goal.sum(), 3) if g_close.on_goal.sum() else None,
                close_sog=int(g_close.on_goal.sum()),
                blend=round(float(c.blend), 2), blend_rk=int(c.blend_rk),
                spark=[round(float(v), 2) for v in pg.values], seasons=seasons,
                small=bool(c.sog < 300)))
    OUT.mkdir(parents=True, exist_ok=True)
    meta = dict(as_of=as_of, season=SEASON_LABEL(SEASON), lg_sv=round(float(lg_sv), 3), lg_close_sv=round(float(lg_close_sv), 3),
                n_goalies=n_cur, shrink=SHRINK_SHOTS, past_weight=PAST_WEIGHT, teams=teams)
    (OUT / ("goalies_league.json" if league else "goalies.json")).write_text(json.dumps(dict(meta=meta, cards=cards), indent=1))
    for c in (cards if not league else []):
        print(c["team"], c["name"], c["number"], c["gp"], c["sog"], c["sv"], c["gsax"], c["rk"], "blend", c["blend"], c["blend_rk"], c["close_sv"])
    print(meta)


if __name__ == "__main__":
    import sys
    main(league="--league" in sys.argv)
