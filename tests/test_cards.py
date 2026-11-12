"""Card files and built card pages agree with each other. Needs only the committed JSON and the built site, no database."""
import json
import re

import pandas as pd
import pytest

from src.db import ROOT
from src.site.build import SITE, card_slugs

C = ROOT / "reports" / "cards"
LEAGUE = C / "skaters_league.json"
pytestmark = pytest.mark.skipif(not LEAGUE.exists() or not (SITE / "cards" / "index.html").exists(),
                                reason="league cards or built site missing")


def load(name):
    return json.loads((C / name).read_text())


def test_one_card_per_player_and_32_teams():
    sk, gl = load("skaters_league.json"), load("goalies_league.json")
    for d in (sk, gl):
        ids = [c["id"] for c in d["cards"]]
        assert len(ids) == len(set(ids))
    assert len({c["team"] for c in sk["cards"]}) == 32
    assert sk["meta"]["as_of"] == gl["meta"]["as_of"]


def test_card_numbers_are_consistent():
    for c in load("skaters_league.json")["cards"]:
        assert c["p"] == c["g"] + c["a"], c["name"]
        assert c["gp"] >= 1 and c["ppg"] <= c["g"] and c["en_g"] <= c["g"]
        assert len(c["spark"]) == c["gp"] and (not c["spark"] or c["spark"][-1] == c["p"]), c["name"]
        if c.get("proj_p") is not None:
            season_p = c.get("season_p", c["p"])
            assert c["proj_p"] >= season_p - 0.05, c["name"]
            assert abs(c["remaining"] + c["team_gp"] - 82) == 0
    for c in load("goalies_league.json")["cards"]:
        assert 0 < c["sv"] <= 1 and c["sog"] > 0, c["name"]


def test_every_card_has_a_page_that_matches_it():
    slugs = card_slugs()
    as_of = load("skaters_league.json")["meta"]["as_of"]
    stamp = f"{pd.to_datetime(as_of):%B} {pd.to_datetime(as_of).day}, {pd.to_datetime(as_of).year}"
    pat = re.compile(r"(\d+) goals? and (\d+) assists? in (\d+) games?")
    for c in load("skaters_league.json")["cards"]:
        page = (SITE / "cards" / f"{slugs[('S', c['id'])]}.html").read_text()
        dek = re.search(r'<p class="dek">([^<]*)', page).group(1)
        m = pat.search(dek)
        assert m and tuple(map(int, m.groups())) == (c["g"], c["a"], c["gp"]), (c["name"], dek)
        assert stamp in page, c["name"]
    for c in load("goalies_league.json")["cards"]:
        page = (SITE / "cards" / f"{slugs[('G', c['id'])]}.html").read_text()
        assert f"{c['gsax']:.1f} goals saved" in page or f"{c['gsax']:+.1f} goals saved" in page, c["name"]
        assert stamp in page, c["name"]


def test_index_links_resolve():
    idx = (SITE / "cards" / "index.html").read_text()
    links = set(re.findall(r'href="([a-z0-9-]+)\.html"', idx))
    assert len(links) >= len(load("skaters_league.json")["cards"]) + len(load("goalies_league.json")["cards"])
    missing = [s for s in links if not (SITE / "cards" / f"{s}.html").exists()]
    assert not missing, missing[:5]
