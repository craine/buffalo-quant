"""The xG fingerprint check: exact on the training data, tolerant of runner-hardware noise in the model output."""
from collections import namedtuple

import pandas as pd

from src.metrics.nhl_xg import FEATURES
from src.metrics.xg_fingerprint import XG_REL_TOL, compare, data_hash

Row = namedtuple("Row", "season xg n")
FP = {"data_sha256": "abc", "seasons": {"20232024": {"xg_sum": 7469.241811, "n": 114059},
                                        "20242025": {"xg_sum": 7301.361765, "n": 111304}}}


def test_hardware_noise_passes():
    # the totals a different GitHub runner produced on Nov 13-14, 2026, from identical shots
    assert compare([Row(20232024, 7468.655, 114059), Row(20242025, 7301.590, 111304)], FP, "abc") == []


def test_real_model_change_fails():
    # reordering the training rows moved 2023-24 to 7480.734 (+0.15%)
    fail = compare([Row(20232024, 7480.734, 114059), Row(20242025, 7301.362, 111304)], FP, "abc")
    assert len(fail) == 1 and "shot model changed for 20232024" in fail[0]


def test_tolerance_edge():
    ref = FP["seasons"]["20232024"]["xg_sum"]
    ok = Row(20232024, ref * (1 + XG_REL_TOL * 0.99), 114059)
    bad = Row(20232024, ref * (1 + XG_REL_TOL * 1.01), 114059)
    other = Row(20242025, 7301.361765, 111304)
    assert compare([ok, other], FP, "abc") == []
    assert len(compare([bad, other], FP, "abc")) == 1


def test_data_change_fails_even_with_same_totals():
    fail = compare([Row(20232024, 7469.241811, 114059), Row(20242025, 7301.361765, 111304)], FP, "def")
    assert len(fail) == 1 and "training data changed" in fail[0]


def test_shot_count_and_missing_season_fail():
    assert any("shot count changed" in f for f in compare([Row(20232024, 7469.24, 114058), Row(20242025, 7301.36, 111304)], FP, "abc"))
    assert any("completed seasons" in f for f in compare([Row(20232024, 7469.24, 114059)], FP, "abc"))


def _rows():
    d = {c: [1.5, 0.0, 30.25] for c in FEATURES}
    d.update(game_id=[1, 1, 2], eventId=[10, 11, 5], goal=[0, 1, 0], season=[20232024] * 3, shot_type=["wrist", "snap", "slap"])
    return pd.DataFrame(d)


def test_hash_is_order_sensitive_and_ignores_float_noise():
    r = _rows()
    h = data_hash(r)
    assert data_hash(r.iloc[[1, 0, 2]]) != h  # row order changes the model, so it changes the hash
    noisy = r.copy()
    noisy[FEATURES] = noisy[FEATURES] + 1e-12  # a 1-ulp-scale difference in the computed features
    noisy.loc[1, FEATURES] = -0.0
    assert data_hash(noisy) == h
    edited = r.copy()
    edited.loc[2, "dist"] = 31.0  # the NHL moves one shot
    assert data_hash(edited) != h
