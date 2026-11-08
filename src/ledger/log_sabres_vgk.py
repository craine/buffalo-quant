"""Log the Sabres-Vegas call (Nov 8, 2026) before puck drop. Run once, only on Charlie's go-ahead.

Probability recomputed here from NHL game model v0.1 with games before Nov 8, the same inputs the pregame story uses.
Puck drop 3:30 PM ET (20:30 UTC), from the league schedule as listed by the NHL.com game preview.
"""
from datetime import datetime, timezone

from src.ledger import nhl_game_model as m
from src.ledger.ledger import add_prediction, load_to_db

GAME = "NHL_20262027_2026-11-08_VGK_at_BUF"   # NHL game id assigned when the game is ingested; graded by date + teams
PUCK_DROP = datetime(2026, 11, 8, 20, 30, tzinfo=timezone.utc)


def main():
    t, coef, p_ot, _ = m.train()
    off, de, lg, ratio = m.ratings(t, 20262027, "2026-11-08")
    mb, mv = m.mu(coef, m.raw(off, de, lg, ratio, "BUF", "VGK"), 1), m.mu(coef, m.raw(off, de, lg, ratio, "VGK", "BUF"), 0)
    p_b, p_tie = m.win_prob(mb, mv, p_ot)
    pid = add_prediction(game_id=GAME, subject="Sabres vs. Vegas", claim_text="Sabres beat the Golden Knights (any result: regulation, OT or shootout)",
                         metric="BUF_win", threshold="win", probability=round(p_b, 2), model_version=m.VERSION, sport="NHL",
                         kickoff=PUCK_DROP, season="20262027", week="",
                         notes=f"expected goals BUF {mb:.2f}, VGK {mv:.2f}; tie after 60 {p_tie:.3f}; data through 2026-11-07; puck drop 3:30 PM ET per NHL.com game preview")
    print(pid, f"{p_b:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
