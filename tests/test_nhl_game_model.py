import numpy as np

from src.ledger import nhl_game_model as m


def test_win_prob_symmetric_and_bounded():
    p, tie = m.win_prob(3.0, 3.0, 0.5)
    assert abs(p - 0.5) < 1e-6 and 0 < tie < 1
    p2, _ = m.win_prob(3.5, 2.5, 0.5)
    assert p2 > 0.5


def test_ratings_use_only_games_before_date():
    t = m.team_games()
    o1, d1, *_ = m.ratings(t, 20252026, "2026-01-15")
    o2, d2, *_ = m.ratings(t[~((t.season == 20252026) & (t.game_date >= "2026-01-15"))], 20252026, "2026-01-15")
    assert all(np.isclose(o1[k], o2[k]) for k in o1)


def test_beats_coin_and_home_rate_on_test_season():
    t, coef, p_ot, hr = m.train()
    g = m.baselines(t, m.game_rows(m.build_frame(t, [m.TEST]), coef, p_ot), hr)
    assert m.brier(g.p_home, g.home_won) < min(0.25, m.brier(g.b_home, g.home_won), m.brier(g.b_record, g.home_won))
