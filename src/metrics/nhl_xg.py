"""Expected goals (xG) for NHL unblocked shot attempts.

Model: gradient-boosted trees (sklearn HistGradientBoostingClassifier) on shot geometry and context.
Train 2023-24 + 2024-25, validate out-of-sample on 2025-26. Final model refit on all three full seasons
and applied to every season (2026-27 is never in the training set).
Empty-net shots are excluded from the model (they are near-certain goals and distort goalie metrics).
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score

from src.db import connect, query, write

FEATURES = ["dist", "angle", "behind_net", "rebound", "rush", "dt_prev", "skaters_for", "skaters_against",
            "is_home", "period"]
CAT = ["shot_type"]
TRAIN, VALID = [20232024, 20242025], 20252026
FULL = [20232024, 20242025, 20252026]


def design(df, cats=None):
    X = df[FEATURES].astype(float).copy()
    cats = cats or sorted(df.shot_type.unique())
    for c in cats:
        X["st_" + c] = (df.shot_type == c).astype(int)
    return X, cats


def model():
    return HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05, max_leaf_nodes=31,
                                          min_samples_leaf=200, l2_regularization=1.0, random_state=7)


def validate(s):
    tr, va = s[s.season.isin(TRAIN)], s[s.season == VALID]
    Xtr, cats = design(tr); Xva, _ = design(va, cats)
    m = model().fit(Xtr, tr.goal)
    p = m.predict_proba(Xva)[:, 1]
    base = np.full(len(va), tr.goal.mean())
    lr = LogisticRegression(max_iter=1000).fit(tr[["dist", "angle"]], tr.goal)
    p_lr = lr.predict_proba(va[["dist", "angle"]])[:, 1]
    dec = pd.qcut(p, 10, labels=False, duplicates="drop")
    cal = pd.DataFrame({"pred": p, "obs": va.goal.values, "d": dec}).groupby("d").mean()
    return {"n_valid": len(va), "logloss_gbm": log_loss(va.goal, p), "logloss_dist_angle": log_loss(va.goal, p_lr),
            "logloss_base": log_loss(va.goal, base), "auc_gbm": roc_auc_score(va.goal, p),
            "auc_dist_angle": roc_auc_score(va.goal, p_lr), "xg_sum": p.sum(), "goals": int(va.goal.sum()),
            "calibration": cal}


def fit_and_score():
    con = connect()
    s = query("SELECT * FROM clean_nhl_shots", con=con)
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0)].copy()
    v = validate(u)
    full = u[u.season.isin(FULL)]
    Xf, cats = design(full)
    m = model().fit(Xf, full.goal)
    Xa, _ = design(u, cats)
    u["xg"] = m.predict_proba(Xa)[:, 1]
    s = s.merge(u[["game_id", "eventId", "xg"]], on=["game_id", "eventId"], how="left")
    s.loc[(s.unblocked == 1) & (s.empty_net_against == 1), "xg"] = np.nan  # not modeled
    write(s, "clean_nhl_shots_xg", con, if_exists="replace")
    con.commit()
    return v, s


if __name__ == "__main__":
    v, s = fit_and_score()
    for k, val in v.items():
        if k != "calibration":
            print(k, round(val, 4) if isinstance(val, float) else val)
    print(v["calibration"].round(4).to_string())
    print(s.groupby("season").apply(lambda x: pd.Series({"xg": x.xg.sum(), "g_nonEN": x.goal[(x.unblocked == 1) & (x.empty_net_against == 0)].sum()}), include_groups=False).round(0))
