"""Grade Ledger P0023 (Sabres beat the Rangers, Nov 25, 2026, 49%). Run once; grades are append-only."""
from src.db import query
from src.ledger.ledger import grade, load_to_db

GAME_ID = 2026020387
SQL = f"SELECT home, home_score, away, away_score, last_period_type, game_state FROM raw_nhl_games WHERE game_id={GAME_ID}"


def main():
    g = query(SQL).iloc[0]
    assert g.game_state in ("OFF", "FINAL") and g.home == "BUF" and g.away == "NYR", g
    outcome = int(g.home_score > g.away_score)  # any result counts (regulation, OT or shootout)
    grade("P0023", outcome, f"{g.home} {g.home_score}, {g.away} {g.away_score} ({g.last_period_type})", SQL)
    load_to_db()
    print("graded P0023 outcome", outcome)


if __name__ == "__main__":
    main()
