"""Grade Ledger P0002-P0008 (Bills at Vikings, Nov 9, 2026). Run once; grades are append-only.

Outcomes use the same definitions the models used:
- points: final scores in raw_schedules;
- pass/run calls: the game's value in clean_team_week (model_v01.game_values), offense side.
"""
from src.db import query
from src.ledger.ledger import grade, load_to_db
from src.ledger.model_v01 import game_values

GAME = "2026_09_BUF_MIN"
SCORE_SQL = f"SELECT away_team, away_score, home_team, home_score FROM raw_schedules WHERE game_id='{GAME}'"


def outcomes():
    s = query(SCORE_SQL).iloc[0]
    assert s.away_team == "BUF" and s.home_team == "MIN" and s.away_score == s.away_score, s
    buf, mn = int(s.away_score), int(s.home_score)

    def val(team, metric):
        v = game_values(2026, metric)
        r = v[(v.game_id == GAME) & (v.team == team) & (v.side == "off")]
        assert len(r) == 1, (team, metric, r)
        return float(r.v.iloc[0])
    db_buf, db_min = val("BUF", "dropback_epa"), val("MIN", "dropback_epa")
    ru_buf, ru_min = val("BUF", "rush_epa"), val("MIN", "rush_epa")
    tw = "game_values(2026, metric) from clean_team_week, offense side, game_id=" + GAME
    return {
        "P0002": (int(buf > mn), f"BUF {buf}, MIN {mn}", SCORE_SQL),
        "P0003": (int(buf >= 20), f"BUF {buf}", SCORE_SQL),
        "P0004": (int(mn >= 20), f"MIN {mn}", SCORE_SQL),
        "P0005": (int(db_buf > 0), f"BUF EPA/dropback {db_buf:+.3f}", tw),
        "P0006": (int(db_min > 0), f"MIN EPA/dropback {db_min:+.3f}", tw),
        "P0007": (int(ru_buf < 0), f"BUF EPA/rush {ru_buf:+.3f}", tw),
        "P0008": (int(ru_min < 0), f"MIN EPA/rush {ru_min:+.3f}", tw),
    }


def main():
    for pid, (o, actual, src) in outcomes().items():
        grade(pid, o, actual, src)
        print(pid, o, actual)
    load_to_db()


if __name__ == "__main__":
    main()
