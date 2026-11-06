"""NHL data validation. Skips when the NHL tables have not been ingested."""
import pytest

from src.db import query


def _has(table):
    try:
        return len(query(f"SELECT 1 FROM {table} LIMIT 1")) > 0
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _has("clean_nhl_shots_xg"), reason="NHL tables not built")


def test_no_duplicate_games_or_events():
    assert query("SELECT COUNT(*) n FROM (SELECT game_id FROM raw_nhl_games GROUP BY 1 HAVING COUNT(*)>1)").n[0] == 0
    assert query("SELECT COUNT(*) n FROM (SELECT game_id, eventId FROM clean_nhl_shots GROUP BY 1,2 HAVING COUNT(*)>1)").n[0] == 0


def test_complete_seasons_have_1312_games():
    g = query("SELECT season, COUNT(*) n FROM raw_nhl_games WHERE season < 20262027 GROUP BY 1")
    assert (g.n == 1312).all(), g


def test_shot_goals_match_final_scores():
    """Play-by-play goals per team-game equal the final score, except shootout winners (+1 goal, no event)."""
    m = query("""
        SELECT g.game_id, g.home_score, g.away_score, g.last_period_type,
               SUM(CASE WHEN s.goal=1 AND s.team=g.home THEN 1 ELSE 0 END) hg,
               SUM(CASE WHEN s.goal=1 AND s.team=g.away THEN 1 ELSE 0 END) ag
        FROM raw_nhl_games g LEFT JOIN clean_nhl_shots s ON s.game_id=g.game_id GROUP BY 1,2,3,4""")
    diff = (m.home_score - m.hg).abs() + (m.away_score - m.ag).abs()
    so = m.last_period_type == "SO"
    assert (diff[~so] == 0).mean() > 0.999, m[~so & (diff != 0)].head()
    assert (diff[so] == 1).mean() > 0.99


def test_sabres_2025_26_record_matches_official():
    from src.metrics.nhl_team import records
    r = records()
    b = r[(r.team == "BUF") & (r.season == 20252026)]
    assert (len(b), b.w.sum(), b.l.sum(), b.otl.sum()) == (82, 50, 23, 9)
    assert (b.gf.sum(), b.ga.sum()) == (288, 241)


def test_xg_totals_close_to_goals():
    t = query("""SELECT season, SUM(xg) xg, SUM(goal) g FROM clean_nhl_shots_xg
                 WHERE unblocked=1 AND empty_net_against=0 AND season<20262027 GROUP BY 1""")
    assert ((t.xg / t.g - 1).abs() < 0.05).all(), t


def test_xg_bounded():
    r = query("SELECT MIN(xg) lo, MAX(xg) hi, SUM(xg IS NULL) nn FROM clean_nhl_shots_xg WHERE unblocked=1 AND empty_net_against=0")
    assert r.lo[0] > 0 and r.hi[0] < 1 and r.nn[0] == 0
