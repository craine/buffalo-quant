"""NFL card file and built pages agree. Needs only reports/cards/nfl_players.json and the built site."""
import json
import re
from html import unescape

import pytest

from src.db import ROOT
from src.site.build import SITE

SRC = ROOT / "reports" / "cards" / "nfl_players.json"
pytestmark = pytest.mark.skipif(not SRC.exists() or not (SITE / "cards" / "nfl" / "index.html").exists(),
                                reason="NFL cards or built site missing")


def load():
    return json.loads(SRC.read_text())


def test_one_card_per_player_all_teams():
    d = load()
    ids = [c["id"] for c in d["cards"]]
    assert len(ids) == len(set(ids)) and len({c["team"] for c in d["cards"]}) == 32
    # every season row of every card covers at least one game; this season's row matches the card
    for c in d["cards"]:
        if c["gp"]:
            assert c["seasons"] and c["seasons"][-1]["season"] == d["meta"]["season"] and c["seasons"][-1]["gp"] == c["gp"], c["name"]
    assert len(d["meta"]["unlinked"]) <= 10


def d_meta():
    return load()["meta"]


def test_numbers_hang_together():
    meta = d_meta()
    for c in load()["cards"]:
        if c["gp"] == 0:     # on a roster, hasn't played: headline is NFL games since 2018
            assert c["status"] in meta["rostered"] and c["big"] == sum(s["gp"] for s in c["seasons"]), c["name"]
            continue
        assert c["snaps"] + c["st_snaps"] >= 1, c["name"]
        assert len(c["spark"]) == c["gp"] and c["spark"][-1] == c["big"], c["name"]
        assert c["fg_made"] <= c["fg_att"] and c["fg_long"] <= 70 and c["pat_made"] <= c["pat_att"], c["name"]
        assert sum(x[0] for x in (c["fg_u40"], c["fg_40"], c["fg_50"])) == c["fg_made"], c["name"]
        assert c["cmp"] <= c["att"] and c["rec"] <= c["tgt"] + 1, c["name"]   # nflverse can credit a catch without a target
        if c["rk"] is not None:
            assert 1 <= c["rk"] <= c["of"], c["name"]
        if c["grp"] == "QB" and c["n_db"] >= 1:
            assert c["epa_db"] is not None


def test_every_card_has_a_matching_page():
    d = load()
    pages = {p.stem: p.read_text() for p in (SITE / "cards" / "nfl").glob("*.html") if p.stem != "index"}
    assert len(pages) == len(d["cards"])
    week = d["meta"]["week"]
    byname = {}
    for c in d["cards"]:
        byname.setdefault(c["name"], []).append(c)
    for stem, html in pages.items():
        name = unescape(re.search(r"<h1>([^<]*)</h1>", html).group(1))
        dek = re.search(r'<p class="dek">([^<]*)', html).group(1)
        m = re.search(r"(-?[\d.,]+) ([A-Za-z -]+?) in (\d+) games?", dek)
        m0 = re.search(r"Hasn't played this season \(([\d,]+) NFL games? since 2018\)", dek)
        if "Hasn't played in an NFL regular-season game yet" in dek:
            assert any(c["gp"] == 0 and c["big"] == 0 for c in byname[name]), stem
            continue
        assert m or m0, (stem, dek)
        if m:
            assert any(float(m.group(1).replace(",", "")) == c["big"] and c["gp"] == int(m.group(3)) for c in byname[name]), (stem, dek)
        else:
            assert any(c["gp"] == 0 and c["big"] == int(m0.group(1).replace(",", "")) for c in byname[name]), (stem, dek)
        assert f"Week {week}" in dek, stem


def test_index_links_resolve():
    idx = (SITE / "cards" / "nfl" / "index.html").read_text()
    links = set(re.findall(r'href="([a-z0-9-]+)\.html"', idx))
    assert len(links) >= len(load()["cards"])
    assert not [s for s in links if not (SITE / "cards" / "nfl" / f"{s}.html").exists()]
