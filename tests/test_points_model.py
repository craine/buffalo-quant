import numpy as np

from src.ledger import points_model as pm


def test_chances_fall_as_threshold_rises():
    res = np.array([-10.0, -3.0, 0.0, 4.0, 9.0])
    ps = [pm.prob_at_least(22, t, res) for t in (10, 17, 20, 24, 30)]
    assert ps == sorted(ps, reverse=True)
    assert pm.prob_at_least(22, 12, res) == 1.0


def test_ratings_use_only_pregame_games():
    g = pm._drives()
    o1, *_ = pm.ratings(g, 2025, 5)
    g2 = g[~((g.season == 2025) & (g.week >= 5))]
    o2, *_ = pm.ratings(g2, 2025, 5)
    assert np.allclose(o1.sort_index(), o2.sort_index())


def test_backtest_beats_league_average_every_test_season():
    coef, res, te, summ = pm.backtest()
    assert (summ.model < summ.league).all()
    assert (summ.model < summ.team_ppg).all()
    assert te[te.season == 2026].week.max() <= 8
