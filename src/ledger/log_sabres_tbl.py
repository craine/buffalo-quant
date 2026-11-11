"""Log the Sabres-Lightning call (Nov 11, 2026) before puck drop. Run once, only on Charlie's go-ahead.

Probability recomputed here from NHL game model v0.1 with ratings as of Nov 11, the same inputs the pregame story uses.
Puck drop 7:00 PM ET (00:00 UTC Nov 12), per the league schedule.
"""
from datetime import datetime, timezone

from src.ledger import nhl_game_model as m
from src.ledger.ledger import add_prediction, load_to_db

GAME = "NHL_20262027_2026-11-11_TBL_at_BUF"   # graded by date + teams once the game is ingested
PUCK_DROP = datetime(2026, 11, 12, 0, 0, tzinfo=timezone.utc)


def main():
    t, coef, p_ot, _ = m.train()
    off, de, lg, ratio = m.ratings(t, 20262027, "2026-11-11")
    mb, mt = m.mu(coef, m.raw(off, de, lg, ratio, "BUF", "TBL"), 1), m.mu(coef, m.raw(off, de, lg, ratio, "TBL", "BUF"), 0)
    p_b, p_tie = m.win_prob(mb, mt, p_ot)
    pid = add_prediction(game_id=GAME, subject="Sabres vs. Tampa Bay", claim_text="Sabres beat the Lightning (any result: regulation, OT or shootout)",
                         metric="BUF_win", threshold="win", probability=round(p_b, 2), model_version=m.VERSION, sport="NHL",
                         kickoff=PUCK_DROP, season="20262027", week="",
                         notes=f"expected goals BUF {mb:.2f}, TBL {mt:.2f}; tie after 60 {p_tie:.3f}; data through 2026-11-10; puck drop 7:00 PM ET")
    print(pid, f"{p_b:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
