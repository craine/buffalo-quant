import numpy as np

from src.metrics import nfl_playoffs as NP


def _season_from_rank(order):
    """A round-robin season where a better-ranked team always wins: every team plays every other once."""
    t, o, w = [], [], []
    for i, a in enumerate(order):
        for b in order[i + 1:]:
            t += [NP.TI[a], NP.TI[b]]; o += [NP.TI[b], NP.TI[a]]; w += [1.0, 0.0]
    return NP.Season(np.array(t), np.array(o), np.array(w))


def test_seeding_shape_and_division_winners():
    order = sorted(NP.TEAMS)  # alphabetical strength
    S = _season_from_rank(order)
    seeds, winners = NP.seed(S, np.random.default_rng(0))
    for c in (0, 1):
        s = sorted(seeds[(NP.CONF_IDX == c) & (seeds > 0)])
        assert s == [1, 2, 3, 4, 5, 6, 7]
    for d, w in winners.items():
        assert seeds[w] in (1, 2, 3, 4)
        best = min(np.where(NP.DIV_IDX == d)[0], key=lambda i: order.index(NP.TEAMS[i]))
        assert w == best


def test_head_to_head_breaks_two_way_tie():
    # BUF and MIA both 1-1 in a three-team mini-season; BUF beat MIA, so BUF ranks first.
    T = np.array([NP.TI["BUF"], NP.TI["MIA"], NP.TI["BUF"], NP.TI["NE"], NP.TI["MIA"], NP.TI["NE"]])
    O = np.array([NP.TI["MIA"], NP.TI["BUF"], NP.TI["NE"], NP.TI["BUF"], NP.TI["NE"], NP.TI["MIA"]])
    W = np.array([1.0, 0.0, 0.0, 1.0, 1.0, 0.0])
    S = NP.Season(T, O, W)
    ranked = NP._rank([NP.TI["BUF"], NP.TI["MIA"]], S, np.random.default_rng(0), division=True)
    assert ranked[0] == NP.TI["BUF"]


def test_absence_draw_respects_minimum():
    rng = np.random.default_rng(1)
    for _ in range(200):
        k = NP.draw_absence(rng, missed_so_far=1, at_least=4)
        assert k >= 3   # IR: at least 4 games in all, 1 already missed
        assert NP.draw_absence(rng, missed_so_far=0) >= 1
