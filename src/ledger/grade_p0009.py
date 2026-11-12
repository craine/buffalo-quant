"""Grade Ledger P0009 (Sabres beat the Lightning, Nov 11, 2026, 47%). Run once; grades are append-only."""
from src.db import query
from src.ledger.ledger import grade, load_to_db

GAME_ID = 2026020293
SQL = f"SELECT home, home_score, away, away_score, last_period_type, game_state FROM raw_nhl_games WHERE game_id={GAME_ID}"


def main():
    g = query(SQL).iloc[0]
    assert g.game_state in ("OFF", "FINAL") and g.home == "BUF" and g.away == "TBL", g
    outcome = int(g.home_score > g.away_score)  # any result counts (regulation, OT or shootout)
    grade("P0009", outcome, f"{g.away} {g.away_score}, {g.home} {g.home_score} ({g.last_period_type})", SQL)
    load_to_db()
    print("graded P0009 outcome", outcome)


if __name__ == "__main__":
    main()
