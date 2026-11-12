"""Log the Sabres-Blackhawks call (Nov 12, 2026) before puck drop. Run once, only on Charlie's go-ahead.

Probability recomputed here from NHL game model v0.1 with ratings as of Nov 12, the same inputs the pregame story uses.
Puck drop 8:00 PM ET (01:00 UTC Nov 13), per the league schedule.
"""
from datetime import datetime, timezone

from src.ledger import nhl_game_model as m
from src.ledger.ledger import add_prediction, load_to_db

GAME = "NHL_20262027_2026-11-12_BUF_at_CHI"   # graded by date + teams once the game is ingested
PUCK_DROP = datetime(2026, 11, 13, 1, 0, tzinfo=timezone.utc)


def main():
    t, coef, p_ot, _ = m.train()
    off, de, lg, ratio = m.ratings(t, 20262027, "2026-11-12")
    mb, mc = m.mu(coef, m.raw(off, de, lg, ratio, "BUF", "CHI"), 0), m.mu(coef, m.raw(off, de, lg, ratio, "CHI", "BUF"), 1)
    p_c, p_tie = m.win_prob(mc, mb, p_ot)
    p_b = 1 - p_c
    pid = add_prediction(game_id=GAME, subject="Sabres at Chicago", claim_text="Sabres beat the Blackhawks (any result: regulation, OT or shootout)",
                         metric="BUF_win", threshold="win", probability=round(p_b, 2), model_version=m.VERSION, sport="NHL",
                         kickoff=PUCK_DROP, season="20262027", week="",
                         notes=f"expected goals BUF {mb:.2f}, CHI {mc:.2f}; tie after 60 {p_tie:.3f}; data through 2026-11-11; puck drop 8:00 PM ET; "
                               "BUF on 2nd night of back-to-back (model has no rest term)")
    print(pid, f"{p_b:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
