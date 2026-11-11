"""NHL skater ratings from multi-season history, and an honest test of whether they predict.

Rating (per game) for a stat m (chances created, goals, assists, points):
    rate = (this season's total + W x past seasons' totals + K x position average) / (this season's games + W x past games + K)
Past seasons are weighted W for last season, W x DECAY for the one before, and so on. W and K are chosen on 2024-25 only
(history: 2023-24), then the method is tested on 2025-26 (history: 2023-24 and 2024-25), which it never saw.

Test: at a checkpoint in the season (the date the median team has played N games), project each skater's per-game rate
for the rest of the season from what was known on that date, and compare with what he actually did afterwards.
Baselines: this season's pace so far, last season's rate, and the position average.
Data: NHL play-by-play (raw_nhl_plays), game rosters, our xG model (clean_nhl_shots_xg). Regular season; shootouts excluded.
No ice time (no shift data yet).
"""
import itertools

import numpy as np
import pandas as pd

from src.db import query
from src.metrics.nhl_team import shots

FWD = {"C", "L", "R"}
STATS = ["ixg", "g", "a", "p"]
DECAY = 0.5                      # each earlier season counts half as much as the one after it
GRID_W = [0.25, 0.5, 0.75, 1.0]
GRID_K = [5, 10, 20, 40, 80]


def player_games(max_date=None):
    """One row per skater per game dressed: chances created, goals, assists, points. Team abbreviation included."""
    gm = query("SELECT game_id, season, game_date, home_id, home, away_id, away FROM raw_nhl_games")
    if max_date:
        gm = gm[gm.game_date <= max_date]
    ids = set(gm.game_id)
    ros = query("SELECT game_id, team_id, player_id, pos FROM raw_nhl_rosters")
    ros = ros[ros.game_id.isin(ids) & (ros.pos != "G")].drop_duplicates(["game_id", "player_id"])
    pl = query("""SELECT game_id, details_scoringPlayerId AS sc, details_assist1PlayerId AS a1, details_assist2PlayerId AS a2,
                  periodDescriptor_periodType AS pt FROM raw_nhl_plays WHERE typeDescKey='goal'""")
    pl = pl[pl.game_id.isin(ids) & (pl.pt != "SO")]
    cnt = lambda col: pl.dropna(subset=[col]).assign(player_id=lambda d: d[col].astype(int)).groupby(["game_id", "player_id"]).size()
    s = shots()
    s = s[s.game_id.isin(ids) & s.shooter_id.notna()]
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0)].copy()
    cal = u.groupby("season").goal.sum() / u.groupby("season").xg.sum()
    u["xg"] = u.xg * u.season.map(cal)
    ixg = u.assign(player_id=u.shooter_id.astype(int)).groupby(["game_id", "player_id"]).xg.sum()
    x = ros.set_index(["game_id", "player_id"])
    x["g"] = cnt("sc").reindex(x.index).fillna(0)
    x["a"] = (cnt("a1").reindex(x.index).fillna(0) + cnt("a2").reindex(x.index).fillna(0))
    x["ixg"] = ixg.reindex(x.index).fillna(0)
    x = x.reset_index().merge(gm[["game_id", "season", "game_date"]], on="game_id")
    x["p"] = x.g + x.a
    pos = x.groupby("player_id").pos.agg(lambda p: p.mode().iloc[0])
    x["grp"] = x.player_id.map(lambda i: "F" if pos.get(i) in FWD else "D")
    return x


def checkpoint_date(season, n_games):
    """Date by which the median team had played n_games in that season."""
    g = query(f"SELECT game_id, game_date, home, away FROM raw_nhl_games WHERE season={season}")
    long = pd.concat([g[["game_date", "home"]].rename(columns={"home": "t"}), g[["game_date", "away"]].rename(columns={"away": "t"})])
    nth = long.sort_values("game_date").groupby("t").game_date.apply(lambda d: d.iloc[n_games - 1] if len(d) >= n_games else None)
    return nth.dropna().sort_values().iloc[len(nth.dropna()) // 2]


def rate(pg, season, cut, w, k, stat, lg):
    """Blended per-game rate for every skater who played in `season` up to `cut`."""
    cur = pg[(pg.season == season) & (pg.game_date <= cut)].groupby("player_id").agg(gp=("game_id", "size"), tot=(stat, "sum"), grp=("grp", "first"))
    past = pg[pg.season < season].groupby(["player_id", "season"]).agg(gp=("game_id", "size"), tot=(stat, "sum")).reset_index()
    past["wt"] = w * DECAY ** ((season - past.season) // 10001 - 1)
    pw = past.assign(wg=past.gp * past.wt, wt_tot=past.tot * past.wt).groupby("player_id")[["wg", "wt_tot"]].sum()
    cur = cur.join(pw).fillna({"wg": 0, "wt_tot": 0})
    prior = cur.grp.map(lg)
    return (cur.tot + cur.wt_tot + k * prior) / (cur.gp + cur.wg + k)


def evaluate(pg, season, n_games, w, k, min_before=5, min_after=10):
    cut = checkpoint_date(season, n_games)
    before = pg[(pg.season == season) & (pg.game_date <= cut)]
    after = pg[(pg.season == season) & (pg.game_date > cut)]
    a = after.groupby("player_id").agg(gp_after=("game_id", "size"), **{f"{s}_after": (s, "sum") for s in STATS})
    b = before.groupby("player_id").agg(gp_before=("game_id", "size"), grp=("grp", "first"), **{f"{s}_before": (s, "sum") for s in STATS})
    last = pg[pg.season == season - 10001].groupby("player_id").agg(gp_last=("game_id", "size"), **{f"{s}_last": (s, "sum") for s in STATS})
    d = b.join(a, how="inner").join(last)
    d = d[(d.gp_before >= min_before) & (d.gp_after >= min_after)].copy()
    out = {}
    for s in STATS:
        lg = (before.groupby("grp")[s].sum() / before.groupby("grp").size()).to_dict()   # position average to date, this season
        actual = d[f"{s}_after"] / d.gp_after
        preds = {"model": rate(pg, season, cut, w[s], k[s], s, lg).reindex(d.index),
                 "pace": d[f"{s}_before"] / d.gp_before,
                 "last_season": (d[f"{s}_last"] / d.gp_last).where(d.gp_last >= 20).fillna(d.grp.map(lg)),
                 "position_avg": d.grp.map(lg)}
        wts = d.gp_after
        out[s] = {name: float(np.average((p - actual) ** 2, weights=wts)) for name, p in preds.items()}
        out[s]["n"] = int(len(d))
        out[s]["mae_rest"] = {name: float(np.average((p - actual).abs() * d.gp_after, weights=wts)) for name, p in preds.items()}
    return out, cut, d


def fit(pg, season=20242025, checkpoints=(17, 41)):
    """Choose W and K per stat on one season (sum of squared errors across checkpoints)."""
    best = {}
    for s in STATS:
        scores = {}
        for w, k in itertools.product(GRID_W, GRID_K):
            scores[(w, k)] = sum(evaluate(pg, season, n, {x: w for x in STATS}, {x: k for x in STATS})[0][s]["model"] for n in checkpoints)
        best[s] = min(scores, key=scores.get)
    return {s: best[s][0] for s in STATS}, {s: best[s][1] for s in STATS}


# ---- final method (settings chosen on 2024-25, tested on 2025-26)
W_FIT = {"ixg": 0.5, "a": 0.5}
K_FIT = {"ixg": 5, "a": 10}
FIN_SHRINK = 40      # chances of league-average finishing mixed into each player's own goals/chances ratio


def project(pg, season, cut):
    """Per-game projections for every skater who has played in `season` up to `cut`:
    chances (blended), goals = chances x shrunk personal finishing, assists (blended), points = goals + assists."""
    before = pg[(pg.season == season) & (pg.game_date <= cut)]
    lg = lambda s: (before.groupby("grp")[s].sum() / before.groupby("grp").size()).to_dict()
    ixg = rate(pg, season, cut, W_FIT["ixg"], K_FIT["ixg"], "ixg", lg("ixg"))
    h = pg[(pg.season < season) | ((pg.season == season) & (pg.game_date <= cut))].groupby("player_id")[["g", "ixg"]].sum()
    fin = ((h.g + FIN_SHRINK) / (h.ixg + FIN_SHRINK)).reindex(ixg.index).fillna(1.0)
    a = rate(pg, season, cut, W_FIT["a"], K_FIT["a"], "a", lg("a")).reindex(ixg.index)
    out = pd.DataFrame({"ixg_pg": ixg, "fin_ratio": fin, "g_pg": ixg * fin, "a_pg": a})
    out["p_pg"] = out.g_pg + out.a_pg
    return out


def backtest(pg, season, n_games, min_before=5, min_after=10):
    """Final method vs. baselines, at the date the median team had played n_games."""
    _, cut, d = evaluate(pg, season, n_games, {s: 0.5 for s in STATS}, {s: 10 for s in STATS}, min_before, min_after)
    before = pg[(pg.season == season) & (pg.game_date <= cut)]
    pr = project(pg, season, cut).reindex(d.index)
    res = {}
    for s, col in (("ixg", "ixg_pg"), ("g", "g_pg"), ("a", "a_pg"), ("p", "p_pg")):
        lg = (before.groupby("grp")[s].sum() / before.groupby("grp").size()).to_dict()
        actual = d[f"{s}_after"] / d.gp_after
        preds = {"model": pr[col], "pace": d[f"{s}_before"] / d.gp_before,
                 "last_season": (d[f"{s}_last"] / d.gp_last).where(d.gp_last >= 20).fillna(d.grp.map(lg)), "position_avg": d.grp.map(lg)}
        wts = d.gp_after
        res[s] = {k: dict(mse=round(float(np.average((p - actual) ** 2, weights=wts)), 5),
                          abs_err_rest=round(float(np.average((p - actual).abs() * d.gp_after, weights=wts)), 2),
                          corr=round(float(np.corrcoef(p, actual)[0, 1]), 3)) for k, p in preds.items()}
    return dict(season=season, checkpoint_games=n_games, cut=cut, skaters=int(len(d)),
                median_games_after=int(d.gp_after.median()), results=res)


if __name__ == "__main__":
    import json
    from src.db import ROOT
    pg = player_games()
    tests = [backtest(pg[pg.season <= ss], ss, n) for ss in (20242025, 20252026) for n in (17, 41)]
    (ROOT / "reports" / "cards" / "player_model_backtest.json").write_text(json.dumps(
        dict(method=dict(W=W_FIT, K=K_FIT, decay=DECAY, fin_shrink=FIN_SHRINK, fit_on="2024-25", tested_on="2025-26"), tests=tests), indent=1))
    for t in tests:
        print(f"\n{t['season']} after {t['checkpoint_games']} games ({t['cut']}), {t['skaters']} skaters, median {t['median_games_after']} games after")
        for s, r in t["results"].items():
            print(f"  {s:4} rest-of-season abs err: model {r['model']['abs_err_rest']:.2f} | pace {r['pace']['abs_err_rest']:.2f} | "
                  f"last {r['last_season']['abs_err_rest']:.2f} | pos {r['position_avg']['abs_err_rest']:.2f}   corr model {r['model']['corr']:.2f} pace {r['pace']['corr']:.2f}")
