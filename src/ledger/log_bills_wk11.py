"""Log the Bills-Dolphins win call (Week 11, Sun Nov 22, 2026) before kickoff. Run once, on Charlie's go-ahead (given Nov 20).

The 81% was published in the Nov. 19 story (src/reports/nfl_mismatches.py). Recomputed here with the same points model
v0.1 functions and the same data pin (through 2026 Week 10), so the Ledger matches the published number. Kickoff comes
from raw_schedules.
"""
from src.ledger import points_model as pm
from src.ledger.ledger import add_prediction, load_to_db
from src.reports.wk10_prediction import WIN_VERSION

GAME, SEASON, WEEK_DONE = "2026_11_MIA_BUF", 2026, 10


def main():
    coef, pairs = pm.paired_misses()
    o, de, lg, pace, lgp = pm.ratings(pm._drives(), SEASON, WEEK_DONE + 1)
    rb, *_ = pm.raw_prediction(o, de, lg, pace, lgp, "BUF", "MIA")
    rm, *_ = pm.raw_prediction(o, de, lg, pace, lgp, "MIA", "BUF")
    pb, pmi = float(pm.predict(coef, rb, 1)), float(pm.predict(coef, rm, 0))
    p = pm.win_chance(pb, pmi, pairs)
    assert round(p, 2) == 0.81, p          # must match the published story
    pid = add_prediction(game_id=GAME, subject="BUF win", claim_text="Bills beat the Dolphins (any result; a tie counts as a miss)",
                         metric="BUF_win", threshold="win", probability=round(p, 2), model_version=WIN_VERSION,
                         notes=f"projections BUF {pb:.1f}, MIA {pmi:.1f}; paired training misses; data through 2026 week {WEEK_DONE}; story: NFL mismatches (Nov. 19)")
    print(pid, f"{p:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
