"""Grade Ledger P0018 (Sabres beat the Flyers, Nov 17, 2026, 48%). Run once; grades are append-only."""
from src.db import query
from src.ledger.ledger import grade, load_to_db

GAME_ID = 2026020337
SQL = f"SELECT home, home_score, away, away_score, last_period_type, game_state FROM raw_nhl_games WHERE game_id={GAME_ID}"


def main():
    g = query(SQL).iloc[0]
    assert g.game_state in ("OFF", "FINAL") and g.home == "PHI" and g.away == "BUF", g
    outcome = int(g.away_score > g.home_score)  # any result counts (regulation, OT or shootout)
    grade("P0018", outcome, f"{g.away} {g.away_score}, {g.home} {g.home_score} ({g.last_period_type})", SQL)
    load_to_db()
    print("graded P0018 outcome", outcome)


if __name__ == "__main__":
    main()
