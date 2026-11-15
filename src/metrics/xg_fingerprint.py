"""Reproducibility check for the NHL xG model (config/xg_fingerprint.json).

The model trains only on completed seasons, so a rerun should reproduce it. Two separate checks:

1. The training data, exactly: shot counts per season and a hash of every training row (features rounded to 4 places, in the
   order the model sees them; row order matters because the model holds out a slice for early stopping). Any NHL edit to old
   play-by-play, a dropped game or a reordered fetch changes the hash.
2. The model output, within a small relative tolerance. The same data, code and library versions give xG totals that differ by
   about 0.01% depending on which GitHub runner machine does the work (seen Nov 13-14, 2026: 7,468.655 vs 7,469.242 for
   2023-24, identical shots). The tolerance absorbs that hardware noise; a real model or library change moves totals far more
   (reordering the rows alone moves 2023-24 by 0.15%).
"""
import hashlib

import numpy as np

XG_REL_TOL = 5e-4  # 0.05%: 5x the hardware noise seen, a third of the smallest real change measured


def training_rows(shots):
    """The rows the xG model fits on, in fit order: unblocked, non-empty-net shots from completed seasons."""
    from src.metrics.nhl_xg import FULL
    u = shots[(shots.unblocked == 1) & (shots.empty_net_against == 0)]
    return u[u.season.isin(FULL)]


def data_hash(rows):
    """sha256 of the training rows (features, shot type, goal, ids), order-sensitive, machine-independent."""
    from src.metrics.nhl_xg import FEATURES
    h = hashlib.sha256()
    num = np.round(rows[FEATURES].astype(float).to_numpy(), 4)  # coarse enough that 1-ulp math differences almost never flip it
    num[num == 0] = 0.0  # -0.0 and 0.0 hash the same
    h.update(np.ascontiguousarray(num).tobytes())
    for col in ("game_id", "eventId", "goal", "season"):
        h.update(rows[col].astype("int64").to_numpy().tobytes())
    h.update("\x1f".join(rows.shot_type.astype(str)).encode())
    return h.hexdigest()


def compare(now, fp, digest):
    """now: rows of (season, xg, n) for completed seasons; fp: the fingerprint doc. Returns a list of failure messages."""
    fail = []
    if fp.get("data_sha256") != digest:
        fail.append("xG training data changed (NHL edited old play-by-play, a game was dropped, or rows came in a different "
                    f"order): hash {digest[:12]} vs. fingerprint {str(fp.get('data_sha256'))[:12]}")
    seasons = fp["seasons"]
    for x in now:
        ref = seasons.get(str(int(x.season)))
        if ref is None or ref["n"] != x.n:
            fail.append(f"shot count changed for {x.season}: {x.n} shots vs. fingerprint {ref}")
        elif abs(x.xg - ref["xg_sum"]) > XG_REL_TOL * ref["xg_sum"]:
            fail.append(f"shot model changed for {x.season}: xG {x.xg:.3f} vs. fingerprint {ref['xg_sum']:.3f} "
                        f"({(x.xg / ref['xg_sum'] - 1):+.3%}, tolerance {XG_REL_TOL:.2%})")
    if {str(int(x.season)) for x in now} != set(seasons):
        fail.append(f"completed seasons {sorted(str(int(x.season)) for x in now)} vs. fingerprint {sorted(seasons)}")
    return fail
