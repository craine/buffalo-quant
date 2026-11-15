"""Playoff simulation: format logic (always) and schedule-derived divisions and standings (when NHL tables are built)."""
import numpy as np
import pandas as pd
import pytest

from src.db import query
from src.metrics import nhl_playoffs as P


def _div():
    """Two conferences x two divisions x 8 teams, named C{conf}D{div}T{n}."""
    return {f"C{c}D{d}T{n}": (c, 2 * c + d) for c in (0, 1) for d in (0, 1) for n in range(8)}


def test_qualify_top3_per_division_plus_two_wildcards():
    div = _div(); teams = sorted(div)
    score = np.array([[100 - int(t[-1]) + (1.5 if t.startswith("C0D1") else 0) for t in teams]], float)
    made = P.qualify(score, teams, div)[0]
    picked = {t for t, m in zip(teams, made) if m}
    assert len(picked) == 16
    for c in (0, 1):
        assert sum(t.startswith(f"C{c}") for t in picked) == 8
    # in conference 0, division 1 scores higher, so both wild cards come from it (its 4th and 5th)
    assert {"C0D1T3", "C0D1T4"} <= picked and "C0D0T3" not in picked


def test_qualify_wildcard_cannot_take_a_division_spot_twice():
    div = _div(); teams = sorted(div)
    rng = np.random.default_rng(0)
    made = P.qualify(rng.random((500, len(teams))), teams, div)
    assert (made.sum(1) == 16).all()


def _has(table):
    try:
        return len(query(f"SELECT 1 FROM {table} LIMIT 1")) > 0
    except Exception:
        return False


@pytest.mark.skipif(not _has("raw_nhl_games"), reason="NHL tables not built")
def test_divisions_and_standings_from_past_schedule():
    g = query("SELECT * FROM raw_nhl_games WHERE season = 20252026")
    div = P.divisions(g)
    assert len(div) == 32 and len({v for v in div.values()}) == 4
    buf_div = sorted(t for t, v in div.items() if v == div["BUF"])
    assert buf_div == ["BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR"]
    s = P.standings(g)
    assert (s.gp == 82).all() and (s.w + s.l + s.otl == s.gp).all()
    assert s.loc["BUF", "pts"] == 109


@pytest.mark.skipif(not _has("raw_nhl_schedule"), reason="NHL schedule not built")
def test_current_schedule_is_complete_and_balanced():
    sc = query("SELECT * FROM raw_nhl_schedule WHERE season = 20262027")
    n = pd.concat([sc.home, sc.away]).value_counts()
    assert n.nunique() == 1 and len(n) == 32
    assert len(P.divisions(sc)) == 32
