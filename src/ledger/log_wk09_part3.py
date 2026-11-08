"""Log week 9 part 3's seven calls (Bills at Vikings) before kickoff. Run once, only on Charlie's go-ahead, when part 3 publishes.

Probabilities are recomputed with the exact functions the story uses (src/reports/wk09_prediction.py), data pinned
through 2026 week 8, so the Ledger matches the published numbers. Includes part 1's Vikings 20+ call; supersedes
log_card.py and log_points_wk09a.py (do not run those). The sack-rate call failed its backtest and is not logged.
"""
from src.ledger import points_model as pm
from src.ledger.ledger import add_prediction, load_to_db
from src.ledger.model_v01 import VERSION as V01
from src.reports.wk09_prediction import GAME, THRU, WIN_VERSION, matchup_calls, points_block

DATA = f"data through 2026 week {THRU}; story: week 9 part 3"


def calls():
    P = points_block()
    C, _, n_db = matchup_calls()
    return [
        ("BUF win", "Bills beat the Vikings (any result; a tie counts as a miss)", "BUF_win", "win", P["p_buf"], WIN_VERSION,
         f"projections BUF {P['proj']['BUF']:.1f}, MIN {P['proj']['MIN']:.1f}; paired training misses"),
        ("BUF points", "Bills score 20 or more points vs. the Vikings", "BUF_points_over", "20", P["p20"]["BUF"], pm.VERSION,
         f"projection={P['proj']['BUF']:.1f}"),
        ("MIN points", "Vikings score 20 or more points vs. the Bills", "MIN_points_over", "20", P["p20"]["MIN"], pm.VERSION,
         f"projection={P['proj']['MIN']:.1f}; first published in part 1"),
        ("BUF pass offense", "Bills' pass plays add points overall (EPA per dropback above zero)", "BUF_off_dropback_epa_over", "0.0",
         C["buf_db"]["p"], V01, f"expected={C['buf_db']['expected']:.3f}"),
        ("BUF pass defense", "Vikings' pass plays add points overall (EPA per dropback above zero), with Carson Wentz at QB",
         "MIN_off_dropback_epa_over", "0.0", C["min_db"]["p"], V01,
         f"expected={C['min_db']['expected']:.3f}; Wentz override, {n_db} dropbacks 2025-26"),
        ("BUF run offense", "Bills' designed runs lose points overall (rush EPA below zero)", "BUF_off_rush_epa_under", "0.0",
         1 - C["buf_ru"]["p"], V01, f"expected={C['buf_ru']['expected']:.3f}"),
        ("BUF run defense", "Vikings' designed runs lose points overall (rush EPA below zero)", "MIN_off_rush_epa_under", "0.0",
         1 - C["min_ru"]["p"], V01, f"expected={C['min_ru']['expected']:.3f}"),
    ]


def main():
    for subject, claim, metric, t, p, ver, note in calls():
        pid = add_prediction(game_id=GAME, subject=subject, claim_text=claim, metric=metric, threshold=t,
                             probability=round(float(p), 2), model_version=ver, notes=f"{note}; {DATA}")
        print(pid, f"{p:.0%}", claim)
    load_to_db()


if __name__ == "__main__":
    main()
