"""Out-of-sample test of the NHL game model: fit on 2023-25, predict 2025-26 and 2026-27 (to date) blind."""
import sys
sys.path.insert(0, ".")
import numpy as np, pandas as pd
from src.ledger import nhl_game_model as m

t, coef, p_ot, hr = m.train()
print("coef", coef.round(3), "p_ot_home", round(p_ot, 3), "train home win", round(hr, 3))
for s, mx in ((20252026, None), (20262027, "2026-11-07")):
    f = m.build_frame(t, [s], max_date=mx)
    g = m.baselines(t, m.game_rows(f, coef, p_ot), hr)
    y = g.home_won
    print(s, len(g), "Brier model", round(m.brier(g.p_home, y), 4), "| coin", 0.25, "| home rate", round(m.brier(g.b_home, y), 4),
          "| record", round(m.brier(g.b_record, y), 4), "| picks right", round(((g.p_home > .5) == y).mean(), 3))
    g["b"] = pd.cut(g.p_home, [0, .4, .45, .5, .55, .6, .65, 1])
    print(g.groupby("b", observed=True).agg(n=("p_home", "size"), said=("p_home", "mean"), happened=("home_won", "mean")).round(3))
    gl = f.dropna(subset=["raw"]); pr = np.array([m.mu(coef, r, h) for r, h in zip(gl.raw, gl.home)])
    print("goals MAE model", round(np.abs(gl.gf - pr).mean(), 3), "league-avg", round(np.abs(gl.gf - gl.gf.mean()).mean(), 3))
