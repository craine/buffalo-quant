"""Grade Ledger P0012-P0016 (Bills at Jets, Nov 15, 2026). Run once; grades are append-only.

Outcomes use the same definitions the models used:
- win: final score in raw_schedules (a tie counts as a miss, as logged);
- pass/run calls: the game's value in clean_team_week (model_v01.game_values), offense side.
"""
from src.db import query
from src.ledger.ledger import grade, load_to_db
from src.ledger.model_v01 import game_values

GAME = "2026_10_BUF_NYJ"
SCORE_SQL = f"SELECT away_team, away_score, home_team, home_score FROM raw_schedules WHERE game_id='{GAME}'"


def outcomes():
    s = query(SCORE_SQL).iloc[0]
    assert s.away_team == "BUF" and s.home_team == "NYJ" and s.away_score == s.away_score, s
    buf, nyj = int(s.away_score), int(s.home_score)

    def val(team, metric):
        v = game_values(2026, metric)
        r = v[(v.game_id == GAME) & (v.team == team) & (v.side == "off")]
        assert len(r) == 1, (team, metric, r)
        return float(r.v.iloc[0])
    db_buf, db_nyj = val("BUF", "dropback_epa"), val("NYJ", "dropback_epa")
    ru_buf, ru_nyj = val("BUF", "rush_epa"), val("NYJ", "rush_epa")
    tw = "game_values(2026, metric) from clean_team_week, offense side, game_id=" + GAME
    return {
        "P0012": (int(buf > nyj), f"BUF {buf}, NYJ {nyj}", SCORE_SQL),
        "P0013": (int(db_buf > 0), f"BUF EPA/dropback {db_buf:+.3f}", tw),
        "P0014": (int(db_nyj > 0), f"NYJ EPA/dropback {db_nyj:+.3f}", tw),
        "P0015": (int(ru_buf < 0), f"BUF EPA/rush {ru_buf:+.3f}", tw),
        "P0016": (int(ru_nyj < 0), f"NYJ EPA/rush {ru_nyj:+.3f}", tw),
    }


def main():
    for pid, (o, actual, src) in outcomes().items():
        grade(pid, o, actual, src)
        print(pid, o, actual)
    load_to_db()


if __name__ == "__main__":
    main()
