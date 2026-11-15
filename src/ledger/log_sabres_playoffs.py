"""Log the Sabres playoff call (Nov 15, 2026) before their next game. Run once, only on Charlie's go-ahead (given Nov 15).

Probability recomputed here exactly as the story does it: src/metrics/nhl_playoffs.simulate with nhl-game-v0.1 ratings from games
through Nov 14, the NHL's remaining schedule (raw_nhl_schedule), 20,000 seasons, seed 7. The cutoff time is the puck drop of the
Sabres' next game (from the NHL schedule's startTimeUTC); the call resolves after the last regular-season game (2027-04-10).
"""
from datetime import datetime, timezone

from src.db import query
from src.ledger import nhl_game_model as M
from src.ledger.ledger import add_prediction, load_to_db
from src.metrics import nhl_playoffs as P

SEASON, AS_OF, NEXT = 20262027, "2026-11-14", "2026-11-15"
GAME = "NHL_20262027_season_BUF_playoffs"


def main():
    t, coef, p_ot, _ = M.train()
    sched = query(f"SELECT * FROM raw_nhl_schedule WHERE season = {SEASON}")
    played = query(f"SELECT * FROM raw_nhl_games WHERE season = {SEASON} AND game_date <= '{AS_OF}'")
    rem = sched[~sched.game_id.isin(played.game_id)]
    div = P.divisions(sched)
    teams, made, _ = P.simulate(t, coef, p_ot, SEASON, NEXT, played, rem, div, n_sims=20000)
    p = float(made[:, teams.index("BUF")].mean())
    nxt = rem[(rem.home == "BUF") | (rem.away == "BUF")].sort_values("start_utc").iloc[0]
    ko = datetime.fromisoformat(nxt.start_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
    pid = add_prediction(game_id=GAME, subject="Sabres 2026-27 season",
                         claim_text="Sabres make the 2026-27 playoffs (top 3 in their division or one of the East's 2 wild cards)",
                         metric="BUF_playoffs", threshold="qualify", probability=round(p, 2), model_version=f"{M.VERSION}+playoff-sim",
                         sport="NHL", kickoff=ko, season=str(SEASON), week="",
                         notes=f"simulated 20,000 seasons, seed 7; data through {AS_OF}; logged before {nxt.away} at {nxt.home} "
                               f"({nxt.start_utc}, NHL schedule); resolves after the last regular-season game, {sched.game_date.max()}; "
                               f"p unrounded {p:.4f}; story: Are the Sabres done?")
    print(pid, f"{p:.4f}")
    load_to_db()


if __name__ == "__main__":
    main()
