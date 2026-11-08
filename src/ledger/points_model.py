"""Points model v0.1: how many points a team scores in a game, from drives.

Pregame inputs only (games before the one being predicted):
  - the offense's points per drive and the defense's points allowed per drive, this season to date,
    blended with last season's value (shrunk toward the league) while the current sample is small
  - how many drives each team usually gets per game
  - home field
Expected points = (league + offense edge + defense edge) points per drive x expected drives, then a linear
calibration to real final scores (drive points ignore defensive/return TDs, missed PATs, 2-pt tries and safeties).
Chances come from the empirical spread of past misses around the prediction.

Never uses betting lines (brand rule).
"""
import numpy as np
import pandas as pd

from src.db import query

VERSION = "points-v0.1"


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


def ratings(g, season, week, k=60, prior_keep=0.5):
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


def build_frame(seasons, min_week=2, con=None, k=60, prior_keep=0.5):
    """One row per team-game with the pregame raw prediction and the real score."""
    g = _drives(con)
    sc = _scores(con)
    rows = []
    for s in seasons:
        for w in sorted(sc[(sc.season == s) & (sc.week >= min_week)].week.unique()):
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
