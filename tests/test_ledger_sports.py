from datetime import datetime, timedelta, timezone

import pytest

import src.ledger.ledger as L

KO = datetime(2026, 11, 8, 20, 30, tzinfo=timezone.utc)
ARGS = dict(game_id="NHL_20262027_2026-11-08_VGK_at_BUF", subject="s", claim_text="c", metric="m", threshold="t",
            probability=0.46, model_version="v", sport="NHL", kickoff=KO, season="20262027")


@pytest.fixture(autouse=True)
def tmp_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "PRED_CSV", tmp_path / "p.csv")
    monkeypatch.setattr(L, "LEDGER_DIR", tmp_path)


def test_nhl_before_puck_drop_accepted_and_at_puck_drop_rejected():
    assert L.add_prediction(**ARGS, now=KO - timedelta(minutes=1)) == "P0001"
    with pytest.raises(ValueError):
        L.add_prediction(**ARGS, now=KO)


def test_nhl_needs_aware_kickoff():
    with pytest.raises(ValueError):
        L.add_prediction(**{**ARGS, "kickoff": KO.replace(tzinfo=None)}, now=KO - timedelta(hours=1))
    with pytest.raises(ValueError):
        L.add_prediction(**{**ARGS, "kickoff": None}, now=KO - timedelta(hours=1))


def test_unknown_sport_and_nfl_id_disguise_rejected():
    with pytest.raises(ValueError):
        L.add_prediction(**{**ARGS, "sport": "MLB"}, now=KO - timedelta(hours=1))
    with pytest.raises(ValueError):
        L.add_prediction(**{**ARGS, "game_id": "2026_10_BUF_NYJ"}, now=KO - timedelta(hours=1))
