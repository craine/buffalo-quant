"""NFL card file and built pages agree. Needs only reports/cards/nfl_players.json and the built site."""
import json
import re

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
    assert d["meta"]["unlinked_snap_players"] <= 10


def test_numbers_hang_together():
    for c in load()["cards"]:
        assert c["gp"] >= 1 and c["snaps"] >= 1, c["name"]   # off+def snaps; games include special-teams-only games
        assert len(c["spark"]) == c["gp"] and c["spark"][-1] == c["big"], c["name"]
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
        name = re.search(r"<h1>([^<]*)</h1>", html).group(1).replace("&#x27;", "'").replace("&amp;", "&")
        dek = re.search(r'<p class="dek">([^<]*)', html).group(1)
        m = re.search(r"(-?[\d.]+) ([a-z ]+?) in (\d+) games?", dek)
        assert m, (stem, dek)
        assert any(f"{c['big']:g}" == m.group(1) and c["gp"] == int(m.group(3)) for c in byname[name]), (stem, dek)
        assert f"Week {week}" in dek, stem


def test_index_links_resolve():
    idx = (SITE / "cards" / "nfl" / "index.html").read_text()
    links = set(re.findall(r'href="([a-z0-9-]+)\.html"', idx))
    assert len(links) >= len(load()["cards"])
    assert not [s for s in links if not (SITE / "cards" / "nfl" / f"{s}.html").exists()]
