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
        assert c["snaps"] + c["st_snaps"] >= 1 or not c["snap_data"], c["name"]   # box-score-only players have no snap rows
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


def _sched(rows):
    import pandas as pd
    return pd.DataFrame(rows, columns=["week", "game_id", "gameday", "home_score"])


def test_week_status_normal_week_waits_for_monday_night():
    from src.reports.nfl_cards import weeks_from_schedule
    rows = [(1, "2026_01_A_B", "2026-09-10", 20), (1, "2026_01_C_D", "2026-09-13", 17), (1, "2026_01_E_F", "2026-09-14", None)]
    st = weeks_from_schedule(_sched(rows))[1]
    assert not st["complete"] and st["open"] == ["2026_01_E_F"] and st["postponed"] == []
    rows[-1] = (1, "2026_01_E_F", "2026-09-14", 24)
    assert weeks_from_schedule(_sched(rows))[1]["complete"]


def test_week_status_postponed_game_does_not_hold_the_week():
    from src.reports.nfl_cards import weeks_from_schedule
    rows = [(10, "2026_10_A_B", "2026-11-12", 20), (10, "2026_10_C_D", "2026-11-15", 17),
            (10, "2026_10_BUF_MIA", "2026-11-25", None)]          # moved 13 days later, not played yet
    st = weeks_from_schedule(_sched(rows))[10]
    assert st["complete"] and st["postponed"] == ["2026_10_BUF_MIA"] and st["open"] == []
    rows[-1] = (10, "2026_10_BUF_MIA", "2026-11-25", 31)       # once played it's no longer listed
    assert weeks_from_schedule(_sched(rows))[10]["postponed"] == []


def test_latest_week_stops_at_first_incomplete_week():
    from src.reports.nfl_cards import ready_week
    st = {8: dict(complete=True, final=["a"]), 9: dict(complete=False, final=["b"]), 10: dict(complete=True, final=["c"])}
    assert ready_week(st, {"a", "b", "c"}) == 8


def test_postponed_note_wording():
    from src.site.nfl_cards import postponed_note
    assert postponed_note([]) == ""
    one = postponed_note(["2026_10_BUF_MIA"])
    assert "The Bills at Dolphins game from Week 10 was postponed" in one and "after it's played" in one
    two = postponed_note(["2026_10_BUF_MIA", "2026_11_SF_KC"])
    assert " and the 49ers at Chiefs game from Week 11 were postponed" in two and "They aren't" in two


def test_week_waits_until_every_final_game_has_stats():
    from src.reports.nfl_cards import ready_week, schedule_week, weeks_from_schedule
    rows = [(8, "2026_08_A_B", "2026-11-01", 20), (9, "2026_09_A_B", "2026-11-05", 20), (9, "2026_09_C_D", "2026-11-09", 17)]
    st = weeks_from_schedule(_sched(rows))
    assert schedule_week(st) == 9
    assert ready_week(st, {"2026_08_A_B", "2026_09_A_B"}) == 8            # Monday night final, stats not posted yet
    assert ready_week(st, {"2026_08_A_B", "2026_09_A_B", "2026_09_C_D"}) == 9


def test_postponed_game_is_skipped_until_played_and_loaded():
    from src.reports.nfl_cards import ready_week, skipped_games, weeks_from_schedule
    rows = [(9, "2026_09_A_B", "2026-11-05", 20), (9, "2026_09_BUF_MIN", "2026-11-25", None)]
    st = weeks_from_schedule(_sched(rows))
    assert ready_week(st, {"2026_09_A_B"}) == 9
    assert skipped_games(st, {"2026_09_A_B"}, 9) == ["2026_09_BUF_MIN"]
    played = weeks_from_schedule(_sched([rows[0], (9, "2026_09_BUF_MIN", "2026-11-25", 24)]))
    assert skipped_games(played, {"2026_09_A_B"}, 9) == ["2026_09_BUF_MIN"]   # final but stats not loaded: still skipped
    assert skipped_games(played, {"2026_09_A_B", "2026_09_BUF_MIN"}, 9) == []
    assert skipped_games(st, {"2026_09_A_B"}, 8) == []                       # only weeks the cards cover


def test_game_moved_within_its_week_still_holds_the_week():
    from src.reports.nfl_cards import weeks_from_schedule
    rows = [(5, "2026_05_A_B", "2026-10-08", 20), (5, "2026_05_C_D", "2026-10-13", None)]   # Sunday game moved to Tuesday
    st = weeks_from_schedule(_sched(rows))[5]
    assert not st["complete"] and st["open"] == ["2026_05_C_D"] and st["postponed"] == []


def test_ingest_rejects_unknown_source():
    import pytest
    from src.ingest.nflverse import main
    with pytest.raises(SystemExit):
        main(["--only", "snapcounts"])


def test_stall_check_timing():
    import datetime as dt
    from src.reports.nfl_cards import stall_check, weeks_from_schedule
    rows = [(8, "2026_08_A_B", "2026-11-01", 20),
            (9, "2026_09_A_B", "2026-11-05", 20), (9, "2026_09_C_D", "2026-11-09", 17)]          # Thursday start, Monday night
    st, have = weeks_from_schedule(_sched(rows)), {"2026_08_A_B", "2026_09_A_B"}
    assert stall_check(st, 8, dt.date(2026, 11, 10), have) is None                                  # Tuesday run: early is fine
    msg = stall_check(st, 8, dt.date(2026, 11, 11), have)                                            # Wednesday run: fail
    assert msg and "2026_09_C_D" in msg and "2026_09_A_B" not in msg
    assert stall_check(st, 9, dt.date(2026, 11, 11), have) is None                                  # cards caught up
    wed = [(11, "2026_11_A_B", "2026-11-22", 20), (12, "2026_12_A_B", "2026-11-25", 20), (12, "2026_12_C_D", "2026-11-30", 17)]
    assert stall_check(weeks_from_schedule(_sched(wed)), 11, dt.date(2026, 12, 1), {"2026_11_A_B"}) is None   # Wednesday-start week, Tuesday run
    w18 = [(17, "2026_17_A_B", "2027-01-03", 20), (18, "2026_18_A_B", "2027-01-10", 20)]          # Sunday-only final week
    assert stall_check(weeks_from_schedule(_sched(w18)), 17, dt.date(2027, 1, 12), {"2026_17_A_B"})          # caught by the Tuesday run


def test_week_date_ignores_a_postponed_game_played_later():
    from src.reports.nfl_cards import weeks_from_schedule
    rows = [(9, "2026_09_A_B", "2026-11-05", 20), (9, "2026_09_C_D", "2026-11-08", 17), (9, "2026_09_BUF_MIN", "2026-11-18", 24)]
    assert str(weeks_from_schedule(_sched(rows))[9]["last"]) == "2026-11-08"
