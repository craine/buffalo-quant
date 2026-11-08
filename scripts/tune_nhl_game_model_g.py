"""Pick G_SHRINK for v0.2 (starting goalie): fit on 2023-24, score win-chance Brier on 2024-25. v0.1 on the same split: 0.2375."""
import sys
sys.path.insert(0, ".")
from src.ledger import nhl_game_model as m

t = m.team_games(); gg = m.goalie_games()
_, _, p_ot, _ = m.train(t, train_seasons=(20232024,))
for sh in (300, 1000, 3000, 10000):
    tr = m.build_frame_g(t, gg, [20232024], shrink=sh)
    coef = m.fit_g(tr)
    v = m.build_frame_g(t, gg, [20242025], shrink=sh)
    g = m.game_rows_g(v, coef, p_ot)
    print(sh, coef.round(3), round(m.brier(g.p_home, g.home_won), 4), flush=True)
