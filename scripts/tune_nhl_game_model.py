"""Pick K / PRIOR_KEEP for the NHL game model: fit on 2023-24, score win-chance Brier on 2024-25 (never on test seasons)."""
import itertools
import sys
sys.path.insert(0, ".")
from src.ledger import nhl_game_model as m

t = m.team_games()
for k, keep in itertools.product((5, 10, 20, 40), (0.3, 0.5, 0.7)):
    _, coef, p_ot, hr = m.train(t, train_seasons=(20232024,), k=k, prior_keep=keep)
    v = m.build_frame(t, [20242025], k=k, prior_keep=keep)
    g = m.game_rows(v, coef, p_ot)
    print(k, keep, round(m.brier(g.p_home, g.home_won), 4))
