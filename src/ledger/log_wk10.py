"""Log week 10's five calls (Bills at Jets) before kickoff. Run once, only on Charlie's go-ahead, when the story publishes.

Probabilities are recomputed with the exact functions the story uses (src/reports/wk10_prediction.py), data pinned
through 2026 week 9, so the Ledger matches the published numbers. No 20-point calls this week: week 9's story said the
points model's 20+ chances run a few points low and that we'd fix that before using those lines again; it isn't fixed yet.
"""
from src.ledger.ledger import add_prediction, load_to_db
from src.ledger.model_v01 import VERSION as V01
from src.reports.wk10_prediction import GAME, OPP, THRU, WIN_VERSION, matchup_calls, points_block

DATA = f"data through 2026 week {THRU}; story: week 10 Bills at Jets"


def calls():
    P = points_block()
    C, _ = matchup_calls()
    return [
        ("BUF win", "Bills beat the Jets (any result; a tie counts as a miss)", "BUF_win", "win", P["p_buf"], WIN_VERSION,
         f"projections BUF {P['proj']['BUF']:.1f}, {OPP} {P['proj'][OPP]:.1f}; paired training misses"),
        ("BUF pass offense", "Bills' pass plays add points overall (EPA per dropback above zero)", "BUF_off_dropback_epa_over", "0.0",
         C["buf_db"]["p"], V01, f"expected={C['buf_db']['expected']:.3f}"),
        ("BUF pass defense", "Jets' pass plays add points overall (EPA per dropback above zero)", "NYJ_off_dropback_epa_over", "0.0",
         C["opp_db"]["p"], V01, f"expected={C['opp_db']['expected']:.3f}"),
        ("BUF run offense", "Bills' designed runs lose points overall (rush EPA below zero)", "BUF_off_rush_epa_under", "0.0",
         1 - C["buf_ru"]["p"], V01, f"expected={C['buf_ru']['expected']:.3f}"),
        ("BUF run defense", "Jets' designed runs lose points overall (rush EPA below zero)", "NYJ_off_rush_epa_under", "0.0",
         1 - C["opp_ru"]["p"], V01, f"expected={C['opp_ru']['expected']:.3f}"),
    ]


def main():
    for subject, claim, metric, t, p, ver, note in calls():
        pid = add_prediction(game_id=GAME, subject=subject, claim_text=claim, metric=metric, threshold=t,
                             probability=round(float(p), 2), model_version=ver, notes=f"{note}; {DATA}")
        print(pid, f"{p:.0%}", claim)
    load_to_db()


if __name__ == "__main__":
    main()
