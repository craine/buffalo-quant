"""Out-of-sample test of Ledger model v0.1 (location shift) on the three week-9 call types.

For every 2023-2025 regular-season team-game from week 8 on, compute the call's probability with only games before that
week (same math as model_v01.prob_over), then compare with what happened. Baseline: the league's share of team-games
over the threshold so far that season.
"""
import numpy as np
import pandas as pd
from src.ledger.model_v01 import SHRINK, game_values

CALLS = [("dropback_epa", 0.0), ("rush_epa", 0.0), ("sack_rate", 0.06)]


def run(metric, t, seasons=(2023, 2024, 2025), min_week=8):
    rows = []
    for s in seasons:
        gv = game_values(s, metric)
        off = gv[gv.side == "off"].dropna(subset=["v"])
        de = gv[gv.side == "def"]
        opp = de[["game_id", "team"]].rename(columns={"team": "defteam"})
        games = off.merge(opp, on="game_id")
        games = games[games.team != games.defteam]
        for w in sorted(games.week.unique()):
            if w < min_week:
                continue
            prior = off[off.week < w]; prior_d = de[de.week < w]
            lg = prior.v.mean()
            om = prior.groupby("team").v.mean(); dm = prior_d.groupby("team").v.mean()
            dist = (prior.v - prior.groupby("team").v.transform("mean")).to_numpy()
            base = float(np.mean(prior.v > t))
            for r in games[games.week == w].itertuples():
                if r.team not in om or r.defteam not in dm:
                    continue
                exp = lg + SHRINK * ((om[r.team] - lg) + (dm[r.defteam] - lg))
                rows.append(dict(season=s, week=w, p=float(np.mean(dist + exp > t)), base=base, y=int(r.v > t)))
    return pd.DataFrame(rows)



def summary(d):
    """Brier for model and base rate, plus said-vs-happened by probability bucket."""
    b = lambda c: float(((d[c] - d.y) ** 2).mean())
    bk = pd.cut(d.p, [0, .3, .45, .55, .7, 1.0], include_lowest=True)
    cal = d.groupby(bk, observed=True).agg(n=("y", "size"), said=("p", "mean"), happened=("y", "mean"))
    return dict(n=len(d), brier=b("p"), brier_base=b("base"), rate=float(d.y.mean())), cal
