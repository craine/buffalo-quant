"""SUPERSEDED by src/ledger/log_wk09_part3.py, do not run. Log part 1's call (Minnesota scores 20+ vs. Buffalo, week 9) before kickoff. Run once, only on Charlie's go-ahead.

The probability is recomputed here from points model v0.1 with data pinned to 2026 week 8, the same inputs the story uses.
"""
from src.ledger import points_model as pm
from src.ledger.ledger import add_prediction, load_to_db

GAME = "2026_09_BUF_MIN"
SEASON, THRU, THRESHOLD = 2026, 8, 20


def main():
    coef, res, _, _ = pm.backtest(test={2024: 99, 2025: 99, SEASON: THRU})
    o, d, lg, pace, lgp = pm.ratings(pm._drives(), SEASON, THRU + 1)
    raw, ppd, drives = pm.raw_prediction(o, d, lg, pace, lgp, "MIN", "BUF")
    proj = pm.predict(coef, raw, 1)
    p = round(pm.prob_at_least(proj, THRESHOLD, res), 2)
    pid = add_prediction(game_id=GAME, subject="MIN points", claim_text=f"Vikings score {THRESHOLD} or more points vs. the Bills",
                         metric="MIN_points_over", threshold=str(THRESHOLD), probability=p, model_version=pm.VERSION,
                         notes=f"projection={proj:.1f}; ppd={ppd:.3f}; drives={drives:.2f}; data through {SEASON} week {THRU}")
    print(pid, f"{p:.0%}", f"projection {proj:.1f}")
    load_to_db()


if __name__ == "__main__":
    main()
