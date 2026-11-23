"""Grade Ledger P0021 (Bills beat the Dolphins, Week 11, Nov 22, 2026). Run once; grades are append-only.

Outcome: final score in raw_schedules (a tie counts as a miss, as logged).
"""
from src.db import query
from src.ledger.ledger import grade, load_to_db

GAME = "2026_11_MIA_BUF"
SCORE_SQL = f"SELECT away_team, away_score, home_team, home_score FROM raw_schedules WHERE game_id='{GAME}'"


def main():
    s = query(SCORE_SQL).iloc[0]
    assert s.home_team == "BUF" and s.away_team == "MIA" and s.home_score == s.home_score, s
    buf, mia = int(s.home_score), int(s.away_score)
    o = int(buf > mia)
    grade("P0021", o, f"BUF {buf}, MIA {mia}", SCORE_SQL)
    print("P0021", o, buf, mia)
    load_to_db()


if __name__ == "__main__":
    main()
