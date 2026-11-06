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
