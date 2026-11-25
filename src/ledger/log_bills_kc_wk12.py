"""Log the two Bills-Chiefs calls (Thursday, Nov. 26, 2026, 8:20 p.m. ET) before kickoff. Run once, on Charlie's go-ahead.

- Bills win: points model (points-win-v0.1), ratings from games through 2026 week 11, Buffalo at home. Same functions as the
  week 10 story (src/reports/wk10_prediction.py).
- Josh Allen 4+ runs: the share of his 2026 games (15+ plays as passer or runner) with 4 or more runs, counting designed runs
  and scrambles, not kneel-downs. A plain season rate, not a fitted model.
"""
from src.db import query
from src.ledger import points_model as pm
from src.ledger.ledger import add_prediction, load_to_db

GAME = "2026_12_KC_BUF"
THRU = 11
ALLEN_PFR = "AlleJo02"


def win_call():
    coef, res, te, summ = pm.backtest(test={2024: 99, 2025: 99, 2026: THRU})
    g = pm._drives()
    o, d, lg, pace, lp = pm.ratings(g, 2026, THRU + 1)
    rb, _, _ = pm.raw_prediction(o, d, lg, pace, lp, "BUF", "KC")
    rk, _, _ = pm.raw_prediction(o, d, lg, pace, lp, "KC", "BUF")
    pb, pk = pm.predict(coef, rb, 1), pm.predict(coef, rk, 0)       # Buffalo at home
    _, pairs = pm.paired_misses()
    return pm.win_chance(pb, pk, pairs), pb, pk


def allen_call():
    allen = query(f"SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = '{ALLEN_PFR}'").gsis_id
    assert len(allen) == 1
    a = allen.iloc[0]
    r = query(f"""SELECT p.game_id,
                  SUM(CASE WHEN p.rush = 1 AND p.rusher_player_id = '{a}' THEN 1 ELSE 0 END)
                  + SUM(CASE WHEN p.qb_scramble = 1 AND COALESCE(p.rusher_player_id, p.passer_player_id) = '{a}' THEN 1 ELSE 0 END) runs,
                  SUM(CASE WHEN COALESCE(p.passer_player_id, p.rusher_player_id) = '{a}' THEN 1 ELSE 0 END) plays
                  FROM raw_pbp p WHERE p.season = 2026 AND p.week <= {THRU} AND p.season_type = 'REG' AND p.posteam = 'BUF'
                  AND p.play_type <> 'no_play' AND COALESCE(p.qb_kneel, 0) = 0 AND COALESCE(p.two_point_attempt, 0) = 0
                  GROUP BY 1 HAVING plays >= 15""")
    return float((r.runs >= 4).mean()), len(r), int((r.runs >= 4).sum())


def main():
    p_win, pb, pk = win_call()
    p_run, n, k = allen_call()
    assert round(p_win, 2) == 0.55 and (round(pb, 1), round(pk, 1)) == (25.6, 23.9)
    assert (n, k) == (10, 8)
    data = f"data through 2026 week {THRU}; story: Bills-Chiefs week"
    for subject, claim, metric, t, p, ver, note in [
        ("BUF win", "Bills beat the Chiefs (any result; a tie counts as a miss)", "BUF_win", "win", p_win, "points-win-v0.1",
         f"projections BUF {pb:.1f}, KC {pk:.1f}; paired training misses"),
        ("Josh Allen runs", "Josh Allen runs the ball 4 or more times (designed runs plus scrambles; kneel-downs don't count)",
         "ALLEN_runs_4plus", "4", p_run, "season-rate-v0",
         f"{k} of {n} 2026 games (15+ plays) had 4+ runs"),
    ]:
        pid = add_prediction(game_id=GAME, subject=subject, claim_text=claim, metric=metric, threshold=t,
                             probability=round(float(p), 2), model_version=ver, notes=f"{note}; {data}")
        print(pid, f"{p:.0%}", claim)
    load_to_db()


if __name__ == "__main__":
    main()
