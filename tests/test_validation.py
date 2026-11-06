"""Data validation. Must pass before any report is generated."""
import pytest
import yaml

from src.db import DB_PATH, ROOT, query

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="run `make ingest` first")


def test_no_duplicate_plays():
    n = query("SELECT COUNT(*) n FROM (SELECT game_id, play_id FROM raw_pbp GROUP BY 1, 2 HAVING COUNT(*) > 1)").n[0]
    assert n == 0


def test_all_configured_seasons_present():
    lo, hi = yaml.safe_load(open(ROOT / "config" / "seasons.yaml"))["pbp"]
    have = set(query("SELECT DISTINCT season FROM raw_pbp").season)
    assert set(range(lo, hi + 1)) <= have


def test_full_seasons_have_expected_rows():
    c = query("SELECT season, COUNT(*) n, COUNT(DISTINCT game_id) g FROM raw_pbp WHERE season < 2026 GROUP BY season")
    assert c.n.between(45000, 52000).all()
    exp = c.season.map(lambda s: 267 if s <= 2020 else 284)  # 16-game seasons through 2020
    assert (c.g >= exp).all(), c.to_dict("records")


def test_pbp_scores_match_schedule():
    m = query("""
        SELECT s.game_id, s.home_score, s.away_score, MAX(p.total_home_score) h, MAX(p.total_away_score) a
        FROM raw_schedules s LEFT JOIN raw_pbp p ON p.game_id = s.game_id
        WHERE s.season >= 2018 AND s.home_score IS NOT NULL GROUP BY s.game_id""")
    assert m.h.notna().all(), "completed games missing from pbp"
    bad = m[(m.h != m.home_score) | (m.a != m.away_score)]
    assert bad.empty, bad.head().to_dict("records")


def test_bills_games_reconcile():
    s = query("""SELECT season, COUNT(*) n FROM raw_schedules WHERE season >= 2018 AND game_type = 'REG'
                 AND home_score IS NOT NULL AND (home_team='BUF' OR away_team='BUF') GROUP BY season""")
    p = query("""SELECT season, COUNT(DISTINCT game_id) n FROM raw_pbp WHERE season_type = 'REG'
                 AND (home_team='BUF' OR away_team='BUF') GROUP BY season""")
    assert s.set_index("season").n.equals(p.set_index("season").n)


def test_no_nulls_in_key_columns():
    r = query("""SELECT SUM(game_id IS NULL) + SUM(posteam IS NULL) + SUM(defteam IS NULL) + SUM(epa IS NULL) n
                 FROM clean_plays""")
    assert r.n[0] == 0


def test_league_mean_epa_near_zero():
    e = query("SELECT season, AVG(epa) m FROM clean_plays GROUP BY season")
    assert (e.m.abs() < 0.1).all(), e.to_dict("records")


def test_clean_team_week_two_sides_per_game():
    r = query("SELECT game_id, COUNT(*) n FROM clean_team_week GROUP BY game_id HAVING COUNT(*) != 4")
    assert r.empty  # 2 teams x (off, def)
