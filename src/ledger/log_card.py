"""Log the approved week 9 card. Edit CARD (remove rows Charlie kills), then run once before kickoff.

Each call's probability is recomputed live from model v0.1 at logging time, so the logged
number is always traceable to the code and data at that moment.
"""
from src.ledger.ledger import add_prediction, load_to_db
from src.ledger.model_v01 import VERSION, prob_over, qb_relative

GAME = "2026_09_BUF_MIN"
WENTZ = "00-0032950"  # Carson Wentz starts; Kyler Murray ruled out (hamstring), ESPN Nov 5, 2026
CARD = [  # (subject, claim, offense, defense, metric, threshold, direction, QB override metric or None)
    ("BUF pass defense", "Vikings' pass plays add points overall (EPA per dropback above zero), with Carson Wentz at QB",
     "MIN", "BUF", "dropback_epa", 0.0, "over", "dropback_epa"),
    ("BUF run defense", "Vikings' designed runs lose points overall (rush EPA below zero)",
     "MIN", "BUF", "rush_epa", 0.0, "under", None),
    ("BUF pass rush", "Bills sack the Vikings' QB on more than 6% of dropbacks",
     "MIN", "BUF", "sack_rate", 0.06, "over", "sack_rate"),
]


def main():
    for subject, claim, off, deff, metric, t, direction, qb in CARD:
        ov = qb_relative(WENTZ, qb, [2025, 2026])[0] if qb else None
        r = prob_over(off, deff, metric, t, off_override=ov) if qb else prob_over(off, deff, metric, t)
        p = r["p"] if direction == "over" else 1 - r["p"]
        pid = add_prediction(game_id=GAME, subject=subject, claim_text=claim,
                             metric=f"{off}_off_{metric}_{direction}", threshold=str(t), probability=round(p, 2),
                             model_version=VERSION, notes=f"expected={r['expected']:.3f}" + (f"; Wentz override {ov:+.4f} (2025-26)" if qb else ""))
        print(pid, f"{p:.0%}", claim)
    load_to_db()


if __name__ == "__main__":
    main()
