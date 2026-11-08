"""NHL game model v0.1: each team's goals from the chances it creates and allows, then a win chance.

Pregame inputs only (games before the predicted date):
  - team chances created and allowed per game (expected goals, unblocked, empty net excluded), this season to date,
    blended with last season's value (shrunk toward the league) while the current sample is small
  - the league's goals-per-expected-goal ratio to date (the xG model drifts by season)
  - home ice
Each team's expected goals -> linear calibration to real goals (fit on training seasons) -> independent Poisson
scores -> win chance, with regulation ties split by the training-season home overtime/shootout win rate.

Never uses betting lines (brand rule).
"""
import numpy as np
import pandas as pd
from scipy.stats import poisson

from src.db import query

VERSION = "nhl-game-v0.1"
K, PRIOR_KEEP = 10, 0.5      # games of prior; share of last season's edge kept (chosen on 2024-25 only)
TRAIN = (20232024, 20242025)
TEST = 20252026


def team_games(con=None):
    """One row per team-game: expected goals for/against and real goals (shootout goals excluded)."""
    s = query("""SELECT game_id, season, team, opp, is_home, xg, goal, unblocked, empty_net_against FROM clean_nhl_shots_xg""", con=con)
    g = query("SELECT game_id, season, game_date, home, away, home_score, away_score, last_period_type FROM raw_nhl_games", con=con)
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0)]
    xf = u.groupby(["game_id", "team"]).xg.sum().rename("xgf")
    gf = s[s.goal == 1].groupby(["game_id", "team"]).size().rename("gf")
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        x = g.rename(columns={side: "team", opp: "opp", f"{side}_score": "score", f"{opp}_score": "opp_score"})
        x["home"] = int(side == "home")
        rows.append(x[["game_id", "season", "game_date", "team", "opp", "home", "score", "opp_score", "last_period_type"]])
    t = pd.concat(rows, ignore_index=True)
    t = t.join(xf, on=["game_id", "team"]).join(gf, on=["game_id", "team"])
    t["xga"] = t.join(xf.rename("xx"), on=["game_id", "opp"]).xx
    t["xgf"] = t.xgf.fillna(0); t["xga"] = t.xga.fillna(0); t["gf"] = t.gf.fillna(0)
    t["won"] = (t.score > t.opp_score).astype(int)
    return t.sort_values(["game_date", "game_id", "home"]).reset_index(drop=True)


def ratings(t, season, date, k=K, prior_keep=PRIOR_KEEP):
    cur = t[(t.season == season) & (t.game_date < date)]
    prev = t[t.season == season - 10001]
    lg_prev = prev.xgf.mean() if len(prev) else np.nan
    lg_cur = cur.xgf.mean() if len(cur) else np.nan
    lg = lg_cur if len(cur) >= 200 else (lg_prev if not np.isnan(lg_prev) else lg_cur)
    ratio_pool = cur if len(cur) >= 200 else prev
    ratio = ratio_pool.gf.sum() / ratio_pool.xgf.sum() if len(ratio_pool) else 1.0
    c = cur.groupby("team").agg(gp=("xgf", "size"), xgf=("xgf", "sum"), xga=("xga", "sum"))
    p = prev.groupby("team").agg(xgf=("xgf", "mean"), xga=("xga", "mean"))
    teams = set(c.index) | set(p.index)
    off, de = {}, {}
    for tm in teams:
        po = lg + prior_keep * (p.loc[tm, "xgf"] - lg_prev) if tm in p.index else lg
        pd_ = lg + prior_keep * (p.loc[tm, "xga"] - lg_prev) if tm in p.index else lg
        n = c.loc[tm, "gp"] if tm in c.index else 0
        off[tm] = ((c.loc[tm, "xgf"] if n else 0) + k * po) / (n + k)
        de[tm] = ((c.loc[tm, "xga"] if n else 0) + k * pd_) / (n + k)
    return off, de, lg, ratio


def raw(off, de, lg, ratio, team, opp):
    return (off.get(team, lg) + de.get(opp, lg) - lg) * ratio


def build_frame(t, seasons, max_date=None, **kw):
    rows = []
    for s in seasons:
        x = t[t.season == s]
        if max_date:
            x = x[x.game_date <= max_date]
        for d in sorted(x.game_date.unique()):
            off, de, lg, ratio = ratings(t, s, d, **kw)
            for r in x[x.game_date == d].itertuples():
                rows.append(dict(game_id=r.game_id, season=s, game_date=d, team=r.team, opp=r.opp, home=r.home,
                                 gf=r.gf, won=r.won, raw=raw(off, de, lg, ratio, r.team, r.opp)))
    return pd.DataFrame(rows)


def fit(f):
    f = f.dropna(subset=["raw"])
    X = np.column_stack([np.ones(len(f)), f.raw, f.home])
    coef, *_ = np.linalg.lstsq(X, f.gf.to_numpy(float), rcond=None)
    return coef


def mu(coef, rawv, home):
    return max(0.3, coef[0] + coef[1] * rawv + coef[2] * home)


def win_prob(mu_home, mu_away, p_ot_home):
    gmax = 15
    ph = poisson.pmf(np.arange(gmax), mu_home)
    pa = poisson.pmf(np.arange(gmax), mu_away)
    m = np.outer(ph, pa)
    p_h = np.tril(m, -1).sum()
    p_tie = np.trace(m)
    return p_h + p_tie * p_ot_home, p_tie


def game_rows(f, coef, p_ot):
    """One row per game (home view) with model win chance."""
    h = f[f.home == 1].set_index("game_id")
    a = f[f.home == 0].set_index("game_id")
    out = []
    for gid in h.index.intersection(a.index):
        if np.isnan(h.loc[gid, "raw"]) or np.isnan(a.loc[gid, "raw"]):
            continue
        mh, ma = mu(coef, h.loc[gid, "raw"], 1), mu(coef, a.loc[gid, "raw"], 0)
        p, pt = win_prob(mh, ma, p_ot)
        out.append(dict(game_id=gid, season=h.loc[gid, "season"], game_date=h.loc[gid, "game_date"], home=h.loc[gid, "team"],
                        away=a.loc[gid, "team"], mu_h=mh, mu_a=ma, p_home=p, p_tie=pt, home_won=h.loc[gid, "won"]))
    return pd.DataFrame(out)


def train(t=None, con=None, train_seasons=TRAIN, **kw):
    t = team_games(con) if t is None else t
    tr = build_frame(t, train_seasons, **kw)
    coef = fit(tr)
    g = t[(t.season.isin(train_seasons)) & (t.home == 1)]
    ties = g[g.last_period_type.isin(["OT", "SO"])]
    p_ot = ties.won.mean()
    home_rate = g.won.mean()
    return t, coef, p_ot, home_rate


def baselines(t, games, home_rate):
    """Pregame naive win chances: home-team rate, and log5 of points share to date (shrunk 10 games toward .500)."""
    b = []
    for r in games.itertuples():
        cur = t[(t.season == r.season) & (t.game_date < r.game_date)]
        def pct(tm):
            x = cur[cur.team == tm]
            return (x.won.sum() + 5) / (len(x) + 10)
        ph, pa = pct(r.home), pct(r.away)
        l5 = ph * (1 - pa) / (ph * (1 - pa) + pa * (1 - ph))
        b.append(l5)
    games = games.copy()
    games["b_home"] = home_rate
    games["b_record"] = games.b_home * 0 + b
    return games


def brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


# ---------------------------------------------------------------- v0.2: starting goalie
VERSION_G = "nhl-game-v0.2"
G_SHRINK = 1000       # unblocked shots of league-average goaltending in each goalie's rating (chosen on 2024-25)
G_PAST = 0.5          # weight on shots from earlier seasons


def goalie_games(con=None):
    """One row per goalie-game: unblocked non-empty-net shots faced, xG faced, goals allowed, and whether he started
    (faced his team's first shot of the game). xG rescaled per season so league xG = goals."""
    s = query("""SELECT game_id, season, period, t, eventId, opp AS team, goalie_id, xg, goal FROM clean_nhl_shots_xg
                 WHERE unblocked = 1 AND empty_net_against = 0 AND goalie_id IS NOT NULL""", con=con)
    cal = s.groupby("season").goal.sum() / s.groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    first = s.sort_values(["game_id", "period", "t", "eventId"]).drop_duplicates(["game_id", "team"])[["game_id", "team", "goalie_id"]]
    first["started"] = 1
    g = s.groupby(["game_id", "season", "team", "goalie_id"]).agg(shots=("xg", "size"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    g = g.merge(first, on=["game_id", "team", "goalie_id"], how="left").fillna({"started": 0})
    dates = query("SELECT game_id, game_date FROM raw_nhl_games", con=con)
    return g.merge(dates, on="game_id")


def goalie_rating(gg, goalie_id, season, date, shrink=G_SHRINK, past=G_PAST):
    """Goals saved vs. average per unblocked shot, from games before `date` only."""
    x = gg[(gg.goalie_id == goalie_id) & (gg.game_date < date)]
    c, p = x[x.season == season], x[x.season < season]
    num = (c.xga.sum() - c.ga.sum()) + past * (p.xga.sum() - p.ga.sum())
    den = c.shots.sum() + past * p.shots.sum() + shrink
    return num / den


def starters(gg):
    return gg[gg.started == 1].set_index(["game_id", "team"]).goalie_id


def build_frame_g(t, gg, seasons, max_date=None, shrink=G_SHRINK, past=G_PAST, override=None, **kw):
    """v0.1 frame plus the opposing starter's rating x the league's unblocked shots per team-game to date.
    override: {(game_id, team): goalie_id} to set a starter (e.g. today's expected starter)."""
    f = build_frame(t, seasons, max_date=max_date, **kw)
    st = starters(gg)
    shots_pg = gg.groupby(["game_id", "team"]).shots.sum().reset_index().merge(gg[["game_id", "game_date", "season"]].drop_duplicates(), on="game_id")
    adj = []
    for r in f.itertuples():
        key = (r.game_id, r.opp)
        gid = (override or {}).get(key, st.get(key))
        if gid is None or (isinstance(gid, float) and np.isnan(gid)):
            adj.append(0.0); continue
        prior = shots_pg[(shots_pg.season == r.season) & (shots_pg.game_date < r.game_date)]
        spg = prior.shots.mean() if len(prior) >= 100 else shots_pg[shots_pg.season == r.season - 10001].shots.mean()
        spg = 37.0 if np.isnan(spg) else spg
        adj.append(goalie_rating(gg, gid, r.season, r.game_date, shrink, past) * spg)
    f["opp_g"] = adj   # goals the opposing starter is expected to save vs. average
    return f


def fit_g(f):
    f = f.dropna(subset=["raw"])
    X = np.column_stack([np.ones(len(f)), f.raw, f.home, f.opp_g])
    coef, *_ = np.linalg.lstsq(X, f.gf.to_numpy(float), rcond=None)
    return coef


def mu_g(coef, rawv, home, opp_g):
    return max(0.3, coef[0] + coef[1] * rawv + coef[2] * home + coef[3] * opp_g)


def game_rows_g(f, coef, p_ot):
    h = f[f.home == 1].set_index("game_id"); a = f[f.home == 0].set_index("game_id")
    out = []
    for gid in h.index.intersection(a.index):
        if np.isnan(h.loc[gid, "raw"]) or np.isnan(a.loc[gid, "raw"]):
            continue
        mh = mu_g(coef, h.loc[gid, "raw"], 1, h.loc[gid, "opp_g"]); ma = mu_g(coef, a.loc[gid, "raw"], 0, a.loc[gid, "opp_g"])
        p, pt = win_prob(mh, ma, p_ot)
        out.append(dict(game_id=gid, season=h.loc[gid, "season"], game_date=h.loc[gid, "game_date"], home=h.loc[gid, "team"],
                        away=a.loc[gid, "team"], mu_h=mh, mu_a=ma, p_home=p, p_tie=pt, home_won=h.loc[gid, "won"]))
    return pd.DataFrame(out)
