from datetime import datetime, timezone

import pytest

import src.ledger.ledger as L
from src.db import DB_PATH

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="needs raw_schedules")
GAME = "2026_09_BUF_MIN"


@pytest.fixture(autouse=True)
def tmp_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "LEDGER_DIR", tmp_path)
    monkeypatch.setattr(L, "PRED_CSV", tmp_path / "predictions.csv")
    monkeypatch.setattr(L, "GRADE_CSV", tmp_path / "grades.csv")


def add(now, p=0.6):
    return L.add_prediction(game_id=GAME, subject="BUF defense", claim_text="test", metric="m",
                            threshold="0", probability=p, model_version="t", now=now)


def test_rejects_after_kickoff():
    ko = L.kickoff_utc(GAME)
    with pytest.raises(ValueError, match="Rejected"):
        add(ko)


def test_accepts_before_kickoff_and_grades_once():
    pid = add(datetime(2026, 11, 6, tzinfo=timezone.utc))
    assert pid == "P0001"
    L.grade(pid, 1, "x", "q", now=datetime(2026, 11, 10, tzinfo=timezone.utc))
    with pytest.raises(ValueError, match="append-only"):
        L.grade(pid, 0, "x", "q")
    s = L.summary()
    assert s["graded"] == 1 and abs(s["brier"] - 0.16) < 1e-9


def test_probability_bounds():
    with pytest.raises(ValueError):
        add(datetime(2026, 11, 6, tzinfo=timezone.utc), p=1.0)


def test_kickoff_is_monday_night_et():
    assert L.kickoff_utc(GAME).strftime("%Y-%m-%d %H:%M") == "2026-11-10 01:15"


def test_off_override_matches_team_mean_when_equal():
    from src.ledger.model_v01 import game_values, prob_over
    base = prob_over("MIN", "BUF", "dropback_epa", 0.0)
    rel = base["off_mean"] - base["league"]
    same = prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=rel)
    assert abs(same["expected"] - base["expected"]) < 1e-12 and same["p"] == base["p"]


def test_off_override_moves_expected_by_half():
    from src.ledger.model_v01 import SHRINK, prob_over
    a = prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=0.0)
    b = prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=0.10)
    assert abs((b["expected"] - a["expected"]) - SHRINK * 0.10) < 1e-12 and b["p"] >= a["p"]


def test_qb_relative_wentz():
    from src.ledger.model_v01 import qb_relative
    rel, n = qb_relative("00-0032950", "dropback_epa", [2025, 2026])
    assert n > 200 and -0.3 < rel < 0.3


def test_max_week_pins_model_inputs():
    """Pinning to week 8 must reproduce the unpinned week-9 card while the data only runs through week 8,
    and must never include later weeks."""
    from src.ledger.model_v01 import game_values, prob_over, qb_relative
    gv = game_values(2026, "dropback_epa", max_week=8)
    assert gv.week.max() <= 8
    a = prob_over("MIN", "BUF", "sack_rate", 0.06, max_week=8)
    full = game_values(2026, "sack_rate")
    if full.week.max() <= 8:
        b = prob_over("MIN", "BUF", "sack_rate", 0.06)
        assert a["p"] == b["p"] and abs(a["expected"] - b["expected"]) < 1e-12
    rel8, n8 = qb_relative("00-0032950", "dropback_epa", [2025, 2026], max_week=8)
    rel1, n1 = qb_relative("00-0032950", "dropback_epa", [2025, 2026], max_week=1)
    assert n1 <= n8
