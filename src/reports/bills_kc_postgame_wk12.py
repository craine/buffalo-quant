"""Bills-Chiefs recap (Week 12, Thursday Nov. 26, 2026): Josh Allen's fewest passing yards in a win, the run game, the rain, the kick.

Writes reports/2026-wk12-kc-postgame.md, one PNG (bills-kc-wk12-postgame.png) and a hero JSON.
Sources: nflverse play-by-play and schedules (2018 on; 2026 through Week 12, fingerprint asserted), the Ledger, and the published
part 4 / preview hero files for the numbers we're grading ourselves against.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.wk11_postgame import finish, ordn

OUT = ROOT / "reports"
SLUG = "2026-wk12-kc-postgame"
PNG = "bills-kc-wk12-postgame.png"
GAME = "2026_12_KC_BUF"
WK = 12
PBP26_FINGERPRINT = (28843, -180.1391)
PLAYS = """(p.pass = 1 OR p.rush = 1) AND p.epa IS NOT NULL AND p.play_type <> 'no_play' AND COALESCE(p.two_point_attempt, 0) = 0
           AND COALESCE(p.qb_kneel, 0) = 0 AND COALESCE(p.qb_spike, 0) = 0"""
SCOPE = f"(p.season BETWEEN 2018 AND 2025 OR (p.season = 2026 AND p.week <= {WK}))"


def gsis(pfr):
    g = query(f"SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = '{pfr}'").gsis_id
    assert len(g) == 1
    return g.iloc[0]


def main():
    fp = query(f"SELECT COUNT(*) n, ROUND(SUM(epa), 4) s FROM raw_pbp WHERE season = 2026 AND season_type = 'REG' AND week <= {WK} AND epa IS NOT NULL").iloc[0]
    if PBP26_FINGERPRINT is not None:
        assert (int(fp.n), float(fp.s)) == PBP26_FINGERPRINT, f"2026 play-by-play changed: {tuple(fp)}"
    allen, mahomes = gsis("AlleJo02"), gsis("MahoPa00")

    # ---- the game
    sc = query(f"SELECT home_score, away_score FROM raw_schedules WHERE game_id = '{GAME}'").iloc[0]
    bs, ks = int(sc.home_score), int(sc.away_score)
    wx = query(f"SELECT MAX(weather) w FROM raw_pbp WHERE game_id = '{GAME}'").w.iloc[0]
    wind_note = int(wx.split("Wind:")[1].split("mph")[0].split()[-1])
    t = query(f"""SELECT p.posteam, SUM(p.rush) ru, SUM(p.pass) db, COUNT(*) plays,
                  SUM(CASE WHEN p.pass = 1 AND p.yards_gained >= 20 THEN 1 ELSE 0 END) big,
                  AVG(CASE WHEN p.rush = 1 AND COALESCE(p.qb_scramble, 0) = 0 THEN p.success END) run_sr
                  FROM raw_pbp p WHERE p.game_id = '{GAME}' AND {PLAYS} GROUP BY 1""").set_index("posteam")
    kick = query(f"""SELECT kicker_player_name k, kick_distance d, game_seconds_remaining s, score_differential sdiff, qtr
                     FROM raw_pbp WHERE game_id = '{GAME}' AND field_goal_result = 'made' AND posteam = 'BUF' ORDER BY qtr, game_seconds_remaining DESC""")
    winner = kick.iloc[-1]
    assert (bs, ks) == (13, 10) and int(winner.d) == 57 and int(winner.s) == 4 and int(winner.sdiff) == 0 and wind_note == 19

    # ---- Allen: passing yards in every game with 15+ throws, wins and losses, regular season and playoffs, 2018 on
    py = query(f"""SELECT p.game_id, p.season_type, SUM(CASE WHEN p.passer_player_id = '{allen}' THEN p.passing_yards END) y,
                   SUM(CASE WHEN p.passer_player_id = '{allen}' AND p.pass_attempt = 1 AND p.sack = 0 THEN 1 ELSE 0 END) att,
                   SUM(CASE WHEN p.passer_player_id = '{allen}' THEN p.complete_pass END) cmp,
                   SUM(CASE WHEN p.passer_player_id = '{allen}' THEN p.interception END) ints
                   FROM raw_pbp p WHERE {SCOPE} AND p.play_type <> 'no_play' GROUP BY 1, 2 HAVING att >= 15""")
    s = query("SELECT game_id, home_team, home_score, away_score FROM raw_schedules WHERE home_team = 'BUF' OR away_team = 'BUF'")
    s["won"] = np.where(s.home_team == "BUF", s.home_score > s.away_score, s.away_score > s.home_score)
    py = py.merge(s[["game_id", "won"]], on="game_id")
    me = py[py.game_id == GAME].iloc[0]
    wins = py[py.won]
    rank_w = int((wins.y < me.y).sum()) + 1
    below_any = py[py.y < me.y]
    second = wins[wins.game_id != GAME].y.min()
    assert (int(me.y), int(me.cmp), int(me.att), int(me.ints), len(py), len(wins), rank_w, len(below_any)) == (81, 10, 21, 2, 151, 105, 1, 1)
    runs = query(f"""SELECT SUM(CASE WHEN rush = 1 AND rusher_player_id = '{allen}' THEN 1 ELSE 0 END) d,
                     SUM(CASE WHEN qb_scramble = 1 AND COALESCE(rusher_player_id, passer_player_id) = '{allen}' THEN 1 ELSE 0 END) sc
                     FROM raw_pbp WHERE game_id = '{GAME}' AND play_type <> 'no_play' AND COALESCE(qb_kneel, 0) = 0
                     AND COALESCE(two_point_attempt, 0) = 0""").iloc[0]
    a_runs = int(runs.d + runs.sc)

    # ---- the run game: share of plays that were designed runs, every Bills game 2018 on (regular season)
    bg = query(f"""SELECT p.game_id, SUM(p.rush) ru, COUNT(*) n, SUM(CASE WHEN p.pass = 1 AND p.yards_gained >= 20 THEN 1 ELSE 0 END) big
                   FROM raw_pbp p WHERE p.posteam = 'BUF' AND p.season_type = 'REG' AND {SCOPE} AND {PLAYS} GROUP BY 1""")
    bg["share"] = bg.ru / bg.n
    g0 = bg[bg.game_id == GAME].iloc[0]
    share_rank = int((bg.share > g0.share).sum()) + 1
    no_big = int((bg.big == 0).sum())
    cook = query(f"""SELECT rusher_player_id, COUNT(*) n, SUM(yards_gained) y FROM raw_pbp WHERE game_id = '{GAME}' AND posteam = 'BUF'
                     AND rush = 1 AND play_type <> 'no_play' AND rusher_player_name = 'J.Cook' GROUP BY 1""").iloc[0]
    streak = query(f"""SELECT s.week, MAX(CASE WHEN (p.rusher_player_id = '{cook.rusher_player_id}' AND p.rush_touchdown = 1)
                       OR (p.receiver_player_id = '{cook.rusher_player_id}' AND p.pass_touchdown = 1) THEN 1 ELSE 0 END) td
                       FROM raw_pbp p JOIN raw_schedules s USING (game_id) WHERE p.season = 2026 AND p.season_type = 'REG' AND p.posteam = 'BUF'
                       AND s.week <= {WK} GROUP BY 1 ORDER BY 1""").td.tolist()
    cook_streak = next((i for i, v in enumerate(reversed(streak)) if v == 0), len(streak))
    ties = int((bg.share == g0.share).sum()) - 1
    assert (int(g0.ru), share_rank, len(bg), no_big, int(cook.n), int(cook.y), cook_streak) == (40, 6, 143, 5, 32, 117, 10)

    # ---- Mahomes: how often Kansas City scored 10 or fewer in his regular-season starts (2018 on)
    ms = query(f"""SELECT p.game_id FROM raw_pbp p WHERE COALESCE(p.passer_player_id, p.rusher_player_id) = '{mahomes}' AND p.pass = 1
                   AND p.season_type = 'REG' AND {SCOPE} GROUP BY 1 HAVING COUNT(*) >= 15""")
    kc = query("SELECT game_id, home_team, home_score, away_score FROM raw_schedules").merge(ms, on="game_id")
    kc["pts"] = np.where(kc.home_team == "KC", kc.home_score, kc.away_score)
    low10 = int((kc.pts <= 10).sum())
    # part 3's measures for this game: big pass plays and run success, against Mahomes' typical game (2023 on, as in part 3)
    m3 = query(f"""SELECT p.game_id, AVG(CASE WHEN p.pass = 1 THEN (p.yards_gained >= 20) * 1.0 END) big,
                   AVG(CASE WHEN p.rush = 1 AND COALESCE(p.qb_scramble, 0) = 0 THEN p.success END) run_sr
                   FROM raw_pbp p WHERE p.posteam = 'KC' AND p.season_type = 'REG' AND p.season >= 2023 AND {SCOPE} AND {PLAYS}
                   AND p.game_id IN ({",".join(repr(x) for x in ms.game_id)}) GROUP BY 1""")
    med_big, med_run = float(m3[m3.game_id != GAME].big.median()), float(m3[m3.game_id != GAME].run_sr.median())
    kc_big, kc_run = float(t.loc["KC", "big"] / t.loc["KC", "db"]), float(t.loc["KC", "run_sr"])
    assert (len(kc), low10) == (135, 5) and kc_big < med_big and kc_run > med_run

    # ---- our numbers: model projection, part 4 rain finding, Ledger
    pv = json.loads((OUT / "2026-wk12-kc-preview.hero.json").read_text())
    p4 = json.loads((OUT / "2026-wk12-kc-weather.hero.json").read_text())
    rain_pts, rain_usual = p4["big"][0][0], p4["big"][1][0]
    import re
    proj_b, proj_k = map(float, re.search(r"Buffalo (\d+\.\d), Kansas City (\d+\.\d)", pv["note"]).groups())
    p3 = json.loads((OUT / "2026-wk12-kc-mahomes.hero.json").read_text())
    run_rank = int(re.search(r"(\d+)(?:st|nd|rd|th) against the run", p3["note"]).group(1))
    assert (proj_b, proj_k, run_rank) == (25.6, 23.9, 27)
    led = pd.read_csv(ROOT / "ledger" / "predictions.csv").merge(pd.read_csv(ROOT / "ledger" / "grades.csv"), left_on="id", right_on="prediction_id")
    g24, g25 = led[led.id == "P0024"].iloc[0], led[led.id == "P0025"].iloc[0]
    led = led[led.id <= "P0025"]
    right = int((((led.probability > 0.5) & (led.outcome == 1)) | ((led.probability < 0.5) & (led.outcome == 0))).sum())
    assert (int(g24.outcome), int(g25.outcome), right, len(led)) == (1, 1, 15, 24)

    # ---- chart: Allen's passing yards in each of his wins
    wy = wins.sort_values("y").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(11, 5.0), dpi=200)
    rng = np.random.default_rng(12)
    jit = rng.uniform(-0.28, 0.28, len(wy))
    is_me = wy.game_id == GAME
    ax.scatter(wy.y[~is_me], jit[~is_me], s=34, color=GRAY, alpha=0.8, edgecolor="white", linewidth=0.6, zorder=2, label="Other wins")
    ax.scatter(wy.y[is_me], [0], s=150, color=BLUE, edgecolor="white", linewidth=1.5, zorder=3, label="Thursday vs. Kansas City")
    ax.annotate(f"{int(me.y)} yards", (me.y, 0), xytext=(0, 22), textcoords="offset points", ha="center", fontsize=11, color=BLUE, fontweight="bold")
    med = float(wins.y.median())
    ax.axvline(med, color=MUTED, lw=1, ls="--", zorder=1)
    ax.text(med, 0.42, f"Typical win: {med:.0f}", ha="center", fontsize=9, color=MUTED)
    ax.set_yticks([]); ax.set_ylim(-0.5, 0.55)
    ax.set_xlabel("Josh Allen passing yards")
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    for sp in ("left", "top", "right"):
        ax.spines[sp].set_visible(False)
    fig.subplots_adjust(left=0.04, right=0.98, bottom=0.17, top=0.78)
    finish(fig, f"{int(me.y)} yards: the fewest Josh Allen has thrown for in any of his {len(wins)} wins",
           f"Each dot is a Bills win with Allen throwing 15+ passes, regular season and playoffs, 2018 through Week {WK} of 2026.", "x")
    fig.texts[-1].set_text(f"Source: nflverse play-by-play. {len(py)} Allen games with 15+ throws; {len(wins)} wins.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    md = f"""# Bills {bs}, Chiefs {ks}: Josh Allen threw for {int(me.y)} yards, the fewest in any of his {len(wins)} wins, and Buffalo won anyway

**In the rain, with the wind listed at {wind_note} mph, the Bills beat Kansas City on Tyler Bass's {int(winner.d)}-yard field goal with {int(winner.s)} seconds left.
Josh Allen completed {int(me.cmp)} of {int(me.att)} passes for {int(me.y)} yards with {int(me.ints)} interceptions, his lowest total in any win of his career.
Buffalo ran instead: {int(g0.ru)} designed runs, {g0.share:.0%} of its plays, and James Cook carried {int(cook.n)} times for {int(cook.y)} yards. The defense
held Patrick Mahomes' Chiefs to {ks} points, something that has happened in only {low10} of his {len(kc)} regular-season starts.**

![{int(me.y)} yards: the fewest Josh Allen has thrown for in any of his {len(wins)} wins]({PNG})

## A different kind of win

Allen has thrown 15 or more passes in {len(py)} games, regular season and playoffs. Only {len(below_any)} of them had fewer passing yards than Thursday, and that
one was a loss. His next-lowest total in a win is {int(second)}. Buffalo didn't complete a pass of 20 yards or more, the {ordn(no_big)} time that's happened in
{len(bg)} Bills regular-season games since 2018.

What it did instead: {int(g0.ru)} designed runs, {g0.share:.0%} of its plays, the {"tied for " if ties else ""}{ordn(share_rank)}-highest share in those {len(bg)} games. Cook scored the only Bills
touchdown, his {ordn(cook_streak)} straight game with a touchdown.

## The rain, as forecast

Our model, which doesn't know about weather, projected {proj_b} to {proj_k}. The teams scored {bs} and {ks}. In [part 4](bills-chiefs-rain-and-wind.html)
we found teams in rain and a 10+ mph wind had scored about {rain_pts} points each, against {rain_usual} expected in dry games. Thursday came in well below even
that. One game proves nothing, but it was the kind of game the forecast pointed to.

## The recipe from part 3

[Part 3](bills-chiefs-slowing-mahomes.html) named three things that slowed Mahomes: pressure, no big pass plays, and stopping the run.

- **Big plays:** {int(t.loc['KC', 'big'])} of Kansas City's {int(t.loc['KC', 'db'])} dropbacks gained 20 or more yards ({kc_big:.0%}). In Mahomes' typical game since
  2023 it's {med_big:.0%}. Buffalo did this one.
- **The run:** Kansas City's runs worked {kc_run:.0%} of the time, above Mahomes' typical game ({med_run:.0%}). Buffalo, {ordn(run_rank)} against the run in part 3, didn't stop it.
- **Pressure:** the charting data isn't out yet. We'll add it when it is.

## Receipts

Both of our calls hit. The Bills won ({g24.probability:.0%}), and Allen ran {a_runs} times ({int(runs.d)} designed runs, {int(runs.sc)} scrambles), so "4 or more"
({g25.probability:.0%}) came in. Scores: {g24.brier:.2f} and {g25.brier:.2f}, where 0 is perfect. Our record is now {right} of {len(led)}.

## For the stat-heads

- Allen games: passer with 15+ attempts (sacks excluded), regular season and playoffs, 2018 through 2026 Week {WK}. Wins: {len(wins)}. Median passing yards in wins {med:.0f}.
- Designed run share: `rush` = 1 over pass + rush plays (no kneels, spikes, two-point tries, no-plays). 20+ passes: dropbacks with `yards_gained` >= 20.
- Mahomes starts: 15+ dropbacks, regular season, 2018 on. Part 3 measures use 2023 on, as part 3 did; run "worked" = nflverse `success`.
- Weather from nflverse's game note ("{wx}").
- Ledger: P0024 Brier {g24.brier:.4f}; P0025 Brier {g25.brier:.4f}. 2026 play-by-play fingerprint through Week {WK}: {(int(fp.n), float(fp.s))}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": f"Bills {bs}, Chiefs {ks}",
        "big": [[int(me.y), "Josh Allen passing yards, his fewest in any of his wins"], [int(g0.ru), "Bills designed runs"]],
        "note": f"Rain, a {wind_note} mph wind and a {int(winner.d)}-yard field goal with {int(winner.s)} seconds left. Both of our Ledger calls hit.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
