"""Log the Sabres-Lightning call (Nov 22, 2026) before puck drop. Run once, on Charlie's go-ahead.

Probability recomputed here from NHL game model v0.1 with ratings from games through Nov 21, the same inputs the pregame story uses.
Puck drop 5:00 PM ET (22:00 UTC Nov 22), per the league schedule.
"""
from datetime import datetime, timezone

from src.ledger import nhl_game_model as m
from src.ledger.ledger import add_prediction, load_to_db

GAME = "NHL_20262027_2026-11-22_BUF_at_TBL"   # graded by date + teams once the game is ingested
PUCK_DROP = datetime(2026, 11, 22, 22, 0, tzinfo=timezone.utc)


def main():
    t, coef, p_ot, _ = m.train()
    off, de, lg, ratio = m.ratings(t, 20262027, "2026-11-22")
    mb, mf = m.mu(coef, m.raw(off, de, lg, ratio, "BUF", "TBL"), 0), m.mu(coef, m.raw(off, de, lg, ratio, "TBL", "BUF"), 1)
    p_f, p_tie = m.win_prob(mf, mb, p_ot)
    p_b = 1 - p_f
    pid = add_prediction(game_id=GAME, subject="Sabres at Tampa Bay", claim_text="Sabres beat the Lightning (any result: regulation, OT or shootout)",
                         metric="BUF_win", threshold="win", probability=round(p_b, 2), model_version=m.VERSION, sport="NHL",
                         kickoff=PUCK_DROP, season="20262027", week="",
                         notes=f"expected goals BUF {mb:.2f}, TBL {mf:.2f}; tie after 60 {p_tie:.3f}; data through 2026-11-21; puck drop 5:00 PM ET; story: Sabres at Lightning")
    print(pid, f"{p_b:.0%}")
    load_to_db()


if __name__ == "__main__":
    main()
