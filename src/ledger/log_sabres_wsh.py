"""Log the Sabres-Capitals call (Nov 19, 2026) before puck drop. Run once, on Charlie's go-ahead (given Nov 18).

Probability recomputed here from NHL game model v0.1 with ratings from games through Nov 17, the same inputs the pregame story uses.
Puck drop 7:00 PM ET (00:00 UTC Nov 20), per the league schedule.
"""
from datetime import datetime, timezone

from src.ledger import nhl_game_model as m
from src.ledger.ledger import add_prediction, load_to_db

GAME = "NHL_20262027_2026-11-19_BUF_at_WSH"   # graded by date + teams once the game is ingested
PUCK_DROP = datetime(2026, 11, 20, 0, 0, tzinfo=timezone.utc)


def main():
    t, coef, p_ot, _ = m.train()
    off, de, lg, ratio = m.ratings(t, 20262027, "2026-11-18")
    mb, mw = m.mu(coef, m.raw(off, de, lg, ratio, "BUF", "WSH"), 0), m.mu(coef, m.raw(off, de, lg, ratio, "WSH", "BUF"), 1)
    p_w, p_tie = m.win_prob(mw, mb, p_ot)
    p_b = 1 - p_w
    pid = add_prediction(game_id=GAME, subject="Sabres at Washington", claim_text="Sabres beat the Capitals (any result: regulation, OT or shootout)",
                         metric="BUF_win", threshold="win", probability=round(p_b, 2), model_version=m.VERSION, sport="NHL",
                         kickoff=PUCK_DROP, season="20262027", week="",
                         notes=f"expected goals BUF {mb:.2f}, WSH {mw:.2f}; tie after 60 {p_tie:.3f}; data through 2026-11-17; puck drop 7:00 PM ET; story: Sabres at Capitals")
    print(pid, f"{p_b:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
