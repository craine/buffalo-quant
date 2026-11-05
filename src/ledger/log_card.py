"""Log the approved week 9 card. Edit CARD (remove rows Charlie kills), then run once before kickoff.

Each call's probability is recomputed live from model v0.1 at logging time, so the logged
number is always traceable to the code and data at that moment.
"""
from src.ledger.ledger import add_prediction, load_to_db
from src.ledger.model_v01 import VERSION, prob_over

GAME = "2026_09_BUF_MIN"
CARD = [  # (subject, claim, offense, defense, metric, threshold, direction)
    ("BUF pass defense", "Vikings post positive EPA per dropback vs. the Bills", "MIN", "BUF", "dropback_epa", 0.0, "over"),
    ("BUF run defense", "Vikings designed-rush EPA stays below zero", "MIN", "BUF", "rush_epa", 0.0, "under"),
    ("BUF pass rush", "Bills sack rate of 6% or higher", "MIN", "BUF", "sack_rate", 0.06, "over"),
    ("BUF offense", "Bills EPA per dropback under +0.15", "BUF", "MIN", "dropback_epa", 0.15, "under"),
]


def main():
    for subject, claim, off, deff, metric, t, direction in CARD:
        r = prob_over(off, deff, metric, t)
        p = r["p"] if direction == "over" else 1 - r["p"]
        pid = add_prediction(game_id=GAME, subject=subject, claim_text=claim,
                             metric=f"{off}_off_{metric}_{direction}", threshold=str(t), probability=round(p, 2),
                             model_version=VERSION, notes=f"expected={r['expected']:.3f}")
        print(pid, f"{p:.0%}", claim)
    load_to_db()


if __name__ == "__main__":
    main()
