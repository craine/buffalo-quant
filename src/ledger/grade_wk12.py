"""Grade Ledger P0024 (Bills beat the Chiefs, 55%) and P0025 (Josh Allen 4+ runs, 80%), Nov. 26, 2026. Run once; append-only."""
from src.db import query
from src.ledger.ledger import grade, load_to_db

GAME = "2026_12_KC_BUF"
ALLEN_PFR = "AlleJo02"
SCORE_SQL = f"SELECT home_team, home_score, away_team, away_score FROM raw_schedules WHERE game_id = '{GAME}'"


def runs_sql(gsis):
    return (f"SELECT SUM(CASE WHEN rush = 1 AND rusher_player_id = '{gsis}' THEN 1 ELSE 0 END) "
            f"+ SUM(CASE WHEN qb_scramble = 1 AND COALESCE(rusher_player_id, passer_player_id) = '{gsis}' THEN 1 ELSE 0 END) AS runs "
            f"FROM raw_pbp WHERE game_id = '{GAME}' AND play_type <> 'no_play' AND COALESCE(qb_kneel, 0) = 0 AND COALESCE(two_point_attempt, 0) = 0")


def main():
    s = query(SCORE_SQL).iloc[0]
    assert s.home_team == "BUF" and s.home_score == s.home_score and s.away_score == s.away_score
    win = int(s.home_score > s.away_score)          # a tie is a miss
    grade("P0024", win, f"BUF {int(s.home_score)}, KC {int(s.away_score)}", SCORE_SQL)
    gsis = query(f"SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = '{ALLEN_PFR}'").gsis_id.iloc[0]
    q = runs_sql(gsis)
    runs = int(query(q).runs.iloc[0])
    grade("P0025", int(runs >= 4), f"{runs} runs (designed runs + scrambles, no kneels)", q)
    load_to_db()
    print("graded P0024", win, "P0025", int(runs >= 4))


if __name__ == "__main__":
    main()
