"""Compare page: builds from the committed card files, every configured column exists, Buffalo players are present."""
import json

import pytest

from src.db import ROOT
from src.site import compare


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from src.site.build import CSS_V, card_slugs, page
    site = tmp_path_factory.mktemp("site")
    compare.build_compare(site, page, card_slugs(), CSS_V)
    assert "/compare/ /rankings/ 301" in (site / "_redirects").read_text()
    return site / "rankings"


def test_files(built):
    for f in ("index.html", "nhl.json", "nfl.json"):
        assert (built / f).exists()
    assert "Where every Sabre and Bill ranks" in (built / "index.html").read_text()


@pytest.mark.parametrize("sport", ["nhl", "nfl"])
def test_columns_and_buffalo(built, sport):
    d = json.loads((built / f"{sport}.json").read_text())
    rows = d["rows"]
    assert d["meta"]["label"]
    for g in compare.config()[sport]:
        grp = [r for r in rows if r["grp"] == g["id"]]
        assert grp, g["id"]
        keys = {c["k"] for c in g["cols"]}
        assert g["rank"] in keys and g["y"] in keys
        for r in grp:
            assert keys <= set(r), (g["id"], keys - set(r))
    assert any(r["t"] == "BUF" for r in rows)


def test_numbers_match_cards(built):
    sk = {c["id"]: c for c in json.loads((ROOT / "reports" / "cards" / "skaters_league.json").read_text())["cards"]}
    for r in json.loads((built / "nhl.json").read_text())["rows"]:
        if r["grp"] == "G":
            continue
        c = sk[r["id"]]
        assert (r["g"], r["a"], r["p"], r["gp"]) == (c["g"], c["a"], c["p"], c["gp"])
        assert r["p_pg"] == round(c["p"] / c["gp"], 2)
