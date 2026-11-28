"""Log the Sabres-Penguins call (Nov 27, 2026) before puck drop. Run once, on Charlie's go-ahead.

Probability recomputed here from NHL game model v0.1 with ratings from games through Nov 25 (no games Nov 26), the same inputs the pregame story uses.
Puck drop 8:00 PM ET (01:00 UTC Nov 28), per the league schedule.
"""
from datetime import datetime, timezone

from src.ledger import nhl_game_model as m
from src.ledger.ledger import add_prediction, load_to_db

GAME = "NHL_20262027_2026-11-27_PIT_at_BUF"
PUCK_DROP = datetime(2026, 11, 28, 1, 0, tzinfo=timezone.utc)


def main():
    t, coef, p_ot, _ = m.train()
    off, de, lg, ratio = m.ratings(t, 20262027, "2026-11-27")
    mb, mn = m.mu(coef, m.raw(off, de, lg, ratio, "BUF", "PIT"), 1), m.mu(coef, m.raw(off, de, lg, ratio, "PIT", "BUF"), 0)
    p_b, p_tie = m.win_prob(mb, mn, p_ot)
    pid = add_prediction(game_id=GAME, subject="Penguins at Sabres", claim_text="Sabres beat the Penguins (any result: regulation, OT or shootout)",
                         metric="BUF_win", threshold="win", probability=round(p_b, 2), model_version=m.VERSION, sport="NHL",
                         kickoff=PUCK_DROP, season="20262027", week="",
                         notes=f"expected goals BUF {mb:.2f}, PIT {mn:.2f}; tie after 60 {p_tie:.3f}; data through 2026-11-25; puck drop 8:00 PM ET; story: Sabres vs. Penguins")
    print(pid, f"{p_b:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
