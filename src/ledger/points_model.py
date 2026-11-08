"""Points model v0.1: how many points a team scores in a game, from drives.

Pregame inputs only (games before the one being predicted):
  - the offense's points per drive and the defense's points allowed per drive, this season to date,
    blended with last season's value (shrunk toward the league) while the current sample is small
  - how many drives each team usually gets per game
  - home field
Expected points = (league + offense edge + defense edge) points per drive x expected drives, then a linear
calibration to real final scores (drive points count every offensive TD as 7 and miss defensive and punt-return TDs,
safeties, missed PATs and 2-pt tries; kickoff-return TDs are credited to the receiving team's drive).
Chances come from the empirical spread of past misses around the prediction.

Never uses betting lines (brand rule).
"""
import numpy as np
import pandas as pd

from src.db import query

VERSION = "points-v0.1"
K, PRIOR_KEEP = 60, 0.7          # chosen on 2019-22 fits (scripts/tune_points_model.py); test misses barely move across K 30-120, keep 0.5-0.9
TRAIN = range(2019, 2024)
TEST = {2024: 99, 2025: 99, 2026: 8}  # season -> last week used (2026 pinned to week 8)


def _drives(con=None):
    d = query("""SELECT season, week, game_id, posteam, defteam, points FROM clean_drives WHERE season_type='REG'""", con=con)
    g = d.groupby(["season", "week", "game_id", "posteam", "defteam"]).agg(pts=("points", "sum"), n=("points", "size")).reset_index()
    return g


def _scores(con=None):
    s = query("""SELECT game_id, season, week, home_team, away_team, home_score, away_score, roof FROM raw_schedules
                 WHERE game_type='REG' AND home_score IS NOT NULL""", con=con)
    h = s.rename(columns={"home_team": "team", "away_team": "opp", "home_score": "score"}).assign(home=1)
    a = s.rename(columns={"away_team": "team", "home_team": "opp", "away_score": "score"}).assign(home=0)
    cols = ["game_id", "season", "week", "team", "opp", "score", "home"]
    return pd.concat([h[cols], a[cols]], ignore_index=True)


def _to_date(g, side, season, week):
    """Points and drives for each team's offense ('posteam') or defense ('defteam') in season before week."""
    x = g[(g.season == season) & (g.week < week)]
    t = x.groupby(side).agg(pts=("pts", "sum"), n=("n", "sum"), games=("game_id", "nunique"))
    return t


def ratings(g, season, week, k=K, prior_keep=PRIOR_KEEP):
    """Pregame points-per-drive ratings for every team, season `season` before `week`."""
    cur = g[(g.season == season) & (g.week < week)]
    prev = g[g.season == season - 1]
    lg_cur = cur.pts.sum() / cur.n.sum() if len(cur) else np.nan
    lg_prev = prev.pts.sum() / prev.n.sum() if len(prev) else np.nan
    lg = lg_cur if len(cur) and cur.n.sum() > 2000 else (lg_prev if not np.isnan(lg_prev) else lg_cur)
    out = {}
    for side in ("posteam", "defteam"):
        c = _to_date(g, side, season, week)
        p = prev.groupby(side).agg(pts=("pts", "sum"), n=("n", "sum"))
        teams = set(c.index) | set(p.index)
        r = {}
        for t in teams:
            prior = lg
            if t in p.index:
                prior = lg + prior_keep * (p.loc[t, "pts"] / p.loc[t, "n"] - lg_prev)
            if t in c.index:
                n = c.loc[t, "n"]
                r[t] = (c.loc[t, "pts"] + k * prior) / (n + k)
            else:
                r[t] = prior
        out[side] = pd.Series(r)
    # drives per game (pace), team-level, shrunk toward league
    pace = cur.groupby("posteam").agg(n=("n", "sum"), games=("game_id", "nunique"))
    lg_pace = (cur.n.sum() / cur.game_id.nunique() / 2) if len(cur) else prev.n.sum() / prev.game_id.nunique() / 2
    pace_r = ((pace.n + 3 * lg_pace) / (pace.games + 3)).to_dict()
    return out["posteam"], out["defteam"], lg, pace_r, lg_pace


def raw_prediction(off_r, def_r, lg, pace_r, lg_pace, team, opp):
    ppd = lg + (off_r.get(team, lg) - lg) + (def_r.get(opp, lg) - lg)
    drives = (pace_r.get(team, lg_pace) + pace_r.get(opp, lg_pace)) / 2
    return ppd * drives, ppd, drives


def build_frame(seasons, min_week=2, con=None, k=K, prior_keep=PRIOR_KEEP, max_week=None):
    """One row per team-game with the pregame raw prediction and the real score."""
    g = _drives(con)
    sc = _scores(con)
    rows = []
    for s in seasons:
        last = (max_week or {}).get(s, 99)
        for w in sorted(sc[(sc.season == s) & (sc.week >= min_week) & (sc.week <= last)].week.unique()):
            o, d, lg, pace, lgp = ratings(g, s, w, k, prior_keep)
            for r in sc[(sc.season == s) & (sc.week == w)].itertuples():
                raw, ppd, drv = raw_prediction(o, d, lg, pace, lgp, r.team, r.opp)
                rows.append(dict(game_id=r.game_id, season=s, week=w, team=r.team, opp=r.opp, home=r.home,
                                 score=r.score, raw=raw, ppd=ppd, drives=drv))
    return pd.DataFrame(rows)


def fit(frame):
    """Least squares: score = a + b*raw + c*home."""
    X = np.column_stack([np.ones(len(frame)), frame.raw, frame.home])
    coef, *_ = np.linalg.lstsq(X, frame.score.to_numpy(float), rcond=None)
    pred = X @ coef
    return coef, frame.score.to_numpy(float) - pred


def predict(coef, raw, home):
    return coef[0] + coef[1] * raw + coef[2] * home


def prob_at_least(pred, threshold, resid):
    """Chance of scoring >= threshold, from the empirical distribution of past misses."""
    return float(np.mean(pred + resid >= threshold - 1e-9))


def add_baselines(f):
    """Naive pregame guesses: league average points, and the team's own points per game, both season to date."""
    b1, b2 = [], []
    for (s, w), grp in f.groupby(["season", "week"]):
        x = f[(f.season == s) & (f.week < w)]
        lg = x.score.mean() if len(x) else f[f.season == s - 1].score.mean()
        ppg = x.groupby("team").score.mean()
        for r in grp.itertuples():
            b1.append((r.Index, lg)); b2.append((r.Index, ppg.get(r.team, lg)))
    f = f.copy()
    f["b_league"] = pd.Series(dict(b1)); f["b_team_ppg"] = pd.Series(dict(b2))
    return f


def backtest(con=None, test=None):
    """Fit on TRAIN, score each test season blind (season -> last week). Returns coef, training misses, test rows, summary."""
    test = test or TEST
    tr = build_frame(TRAIN, con=con)
    coef, res = fit(tr)
    te = add_baselines(build_frame(list(test) + [min(test) - 1], con=con, max_week=test))
    te = te[te.season.isin(list(test))]
    te["model"] = predict(coef, te.raw, te.home)
    summ = te.groupby("season").apply(lambda x: pd.Series(dict(
        n=len(x), model=(x.score - x.model).abs().mean(), league=(x.score - x.b_league).abs().mean(),
        team_ppg=(x.score - x.b_team_ppg).abs().mean(), within7=((x.score - x.model).abs() <= 7).mean())))
    return coef, res, te, summ


def paired_misses(con=None):
    """Training-season (home miss, away miss) pairs from the same game, so the two teams' misses keep their link."""
    tr = build_frame(TRAIN, con=con)
    coef, _ = fit(tr)
    tr = tr.assign(miss=tr.score - predict(coef, tr.raw, tr.home))
    h = tr[tr.home == 1].set_index("game_id").miss
    a = tr[tr.home == 0].set_index("game_id").miss
    j = pd.concat([h.rename("h"), a.rename("a")], axis=1).dropna()
    return coef, j.to_numpy()


def win_chance(pred_home, pred_away, pairs):
    """Chance the home team wins: replay every training game's pair of misses on top of today's projections.
    A tie after regulation is split 50/50 (overtime)."""
    hs = pred_home + pairs[:, 0]
    as_ = pred_away + pairs[:, 1]
    return float(np.mean(hs > as_) + 0.5 * np.mean(np.isclose(hs, as_, atol=0.5)))


def backtest_win(con=None, test=None):
    """Win-chance test on the same blind seasons as backtest(): Brier vs a 50/50 guess and vs the training home-win rate."""
    test = test or TEST
    coef, pairs = paired_misses(con)
    te = build_frame(list(test), con=con, max_week=test)
    te["pred"] = predict(coef, te.raw, te.home)
    h = te[te.home == 1].set_index("game_id"); a = te[te.home == 0].set_index("game_id")
    g = h.join(a[["pred", "score"]], rsuffix="_a").dropna(subset=["pred_a"])
    g["p"] = [win_chance(x, y, pairs) for x, y in zip(g.pred, g.pred_a)]
    g["won"] = (g.score > g.score_a).astype(float).where(g.score != g.score_a, 0.5)
    tr = build_frame(TRAIN, con=con)
    th = tr[tr.home == 1].set_index("game_id").score; ta = tr[tr.home == 0].set_index("game_id").score
    home_rate = float(((th > ta.reindex(th.index)) + 0.5 * (th == ta.reindex(th.index))).mean())
    return g, home_rate
