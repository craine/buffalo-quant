"""Bills-Chiefs recap (Week 12, Thursday Nov. 26, 2026): Cook carried it, the kicking game won it, Bass finished it.

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
PNG = "bills-kc-wk12-postgame-wp.png"
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
    kc = query(f"""SELECT game_id, home_team, home_score, away_score FROM raw_schedules WHERE game_type = 'REG' AND home_score IS NOT NULL
                   AND (home_qb_id = '{mahomes}' OR away_qb_id = '{mahomes}') AND (season < 2026 OR week <= {WK})""")
    kc["pts"] = np.where(kc.home_team == "KC", kc.home_score, kc.away_score)
    low10 = int((kc.pts <= 10).sum())
    # part 3's measures for this game: big pass plays and run success, against Mahomes' typical game (2023 on, as in part 3)
    m3 = query(f"""SELECT p.game_id, AVG(CASE WHEN p.pass = 1 THEN (p.yards_gained >= 20) * 1.0 END) big,
                   AVG(CASE WHEN p.rush = 1 AND COALESCE(p.qb_scramble, 0) = 0 THEN p.success END) run_sr
                   FROM raw_pbp p WHERE p.posteam = 'KC' AND p.season_type = 'REG' AND p.season >= 2023 AND {SCOPE} AND {PLAYS}
                   AND p.game_id IN ({",".join(repr(x) for x in ms.game_id)}) GROUP BY 1""")
    med_big, med_run = float(m3[m3.game_id != GAME].big.median()), float(m3[m3.game_id != GAME].run_sr.median())
    kc_big, kc_run = float(t.loc["KC", "big"] / t.loc["KC", "db"]), float(t.loc["KC", "run_sr"])
    kc_runs = int(t.loc["KC", "ru"])
    assert (len(kc), low10) == (137, 5) and kc_big < med_big and kc_run > med_run

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

    # ---- special teams and the kicks. nflverse flags field goals special = 1 but special_teams_play = 0, so use `special`.
    gp = query(f"""SELECT play_id, qtr, game_seconds_remaining gs, posteam, play_type, special, pass, rush, interception, wpa, home_wp_post,
                   kicker_player_id, kick_distance, field_goal_result, punt_returner_player_name, return_yards, fumble, punter_player_name, "desc" d
                   FROM raw_pbp WHERE game_id = '{GAME}' ORDER BY play_id""")
    gp["bw"] = np.where(gp.posteam == "BUF", gp.wpa, -gp.wpa)
    w_st = float(gp[gp.special == 1].bw.sum())
    w_pass = float(gp[(gp.special == 0) & (gp.play_type != "no_play") & (gp["pass"] == 1)].bw.sum())
    w_run = float(gp[(gp.special == 0) & (gp.play_type != "no_play") & (gp.rush == 1)].bw.sum())
    w_int = float(gp[gp.interception == 1].bw.sum())
    fgs = gp[gp.field_goal_result.notna()]
    b54 = fgs[(fgs.posteam == "BUF") & (fgs.kick_distance == 54)].iloc[0]
    b57 = fgs[(fgs.posteam == "BUF") & (fgs.kick_distance == 57)].iloc[0]
    miss = fgs[(fgs.posteam == "KC") & (fgs.field_goal_result == "missed")].iloc[0]
    ret = gp[(gp.play_type == "punt") & (gp.posteam == "KC") & (gp.qtr == 4) & (gp.gs == 15)].iloc[0]
    muff = gp[(gp.play_type == "punt") & (gp.posteam == "KC") & (gp.fumble == 1)].iloc[0]
    yl = query(f"SELECT play_id, posteam, yardline_100 FROM raw_pbp WHERE game_id = '{GAME}' AND yardline_100 IS NOT NULL ORDER BY play_id")
    import re as _re0
    end_spot = int(_re0.search(r"punts \d+ yards to KC (\d+)", muff.d).group(1))  # where the punt ended, before a 5-yard KC penalty
    muff_net = end_spot - (100 - int(yl[yl.play_id == muff.play_id].yardline_100.iloc[0]))
    bass = b57.kicker_player_id
    assert (int(miss.kick_distance), int(ret.return_yards), int(b57.gs), int(b54.gs), muff_net, int(miss.gs) // 60) == (46, 17, 4, 723, 13, 6)
    med = float(wins.y.median())
    wp0 = float(query(f"SELECT home_wp FROM raw_pbp WHERE game_id = '{GAME}' AND home_wp IS NOT NULL ORDER BY play_id LIMIT 1").home_wp.iloc[0])
    w_other = float(gp.bw.sum()) - w_st - w_pass - w_run
    pre57 = float(gp[gp.play_id < b57.play_id].home_wp_post.dropna().iloc[-1])
    assert (round(wp0, 2), round(pre57, 2), round(float(b57.bw), 2), round(float(ret.bw), 2)) == (0.55, 0.76, 0.24, 0.22)
    assert abs(wp0 + w_st + w_pass + w_run + w_other - 1) < 0.005
    assert (round(w_st, 2), round(w_pass, 2), round(w_run, 2), round(w_int, 2)) == (0.64, -0.36, 0.20, -0.33)
    # every field goal since 1999, for how rare the finish was
    fga = query("""SELECT game_id, season, kicker_player_id kid, kick_distance d, field_goal_result r, game_seconds_remaining s, score_differential sd
                   FROM raw_pbp WHERE field_goal_attempt = 1""")
    assert int(fga.season.min()) == 2018  # raw_pbp starts in 2018; raw_pbp_history (1999-2017) has no kick columns
    fga["made"] = fga.r == "made"
    long_ = fga[(fga.d >= 57) & fga.season.between(2023, 2026)]
    p57 = float(long_.made.mean())
    late = fga[fga.made & (fga.s <= 10) & fga.sd.between(-2, 0) & (fga.d >= 57)]  # tied or down 1-2: a make puts them ahead
    late_bass = late[late.kid == bass]
    two54 = fga[fga.made & (fga.d >= 54) & (fga.kid == bass)].groupby("game_id").size()
    assert (len(late), len(late_bass), int(late.kid.value_counts().max()), int((two54 >= 2).sum())) == (11, 2, 2, 2)
    assert round(p57, 2) == 0.60 and len(long_) == 205
    bass_prev = late_bass[late_bass.game_id != GAME].iloc[0]
    prev_opp = query(f"SELECT home_team, away_team FROM raw_schedules WHERE game_id = '{bass_prev.game_id}'").iloc[0]
    prev_opp = {"MIA": "Miami"}[prev_opp.away_team if prev_opp.home_team == "BUF" else prev_opp.home_team]
    import re as _re
    ret_spot = int(_re.search(r"to KC (\d+) for", ret.d).group(1))
    tie = query(f"SELECT total_home_score h, total_away_score a FROM raw_pbp WHERE game_id = '{GAME}' AND play_id = {int(b54.play_id)}").iloc[0]
    assert (ret_spot, int(tie.h), int(tie.a), int(bass_prev.d), bass_prev.season) == (39, 10, 10, 61, 2024)
    # ---- Cook: carries in every Bills game since 1999, and how often his runs worked vs. the league this season
    car = pd.concat([query(f"""SELECT game_id, rusher_player_id rid, MAX(rusher_player_name) nm, COUNT(*) n FROM {tb} WHERE posteam = 'BUF' AND rush = 1
                               AND play_type <> 'no_play' AND rusher_player_id IS NOT NULL GROUP BY 1, 2""") for tb in ("raw_pbp_history", "raw_pbp")])
    assert car.game_id.str[:4].astype(int).min() == 1999
    big_car = car[car.n >= int(cook.n)]
    more = car[car.n > int(cook.n)].sort_values("game_id").iloc[-1]
    more_yr = int(more.game_id[:4])
    ck = query(f"""SELECT AVG(success) sr FROM raw_pbp p WHERE p.game_id = '{GAME}' AND p.rusher_player_id = '{cook.rusher_player_id}' AND {PLAYS}""").sr.iloc[0]
    lg = query(f"""SELECT AVG(success) sr FROM raw_pbp p WHERE p.season = 2026 AND p.season_type = 'REG' AND p.week <= {WK} AND p.rush = 1
                   AND COALESCE(p.qb_scramble, 0) = 0 AND {PLAYS}""").sr.iloc[0]
    prev_ck = car[(car.rid == cook.rusher_player_id) & (car.n == int(cook.n)) & (car.game_id != GAME)].game_id.iloc[0]
    prev_ck_opp = {"PIT": "Pittsburgh"}[prev_ck.split("_")[2] if prev_ck.split("_")[3] == "BUF" else prev_ck.split("_")[3]]
    assert prev_ck[:4] == "2025"
    assert (len(big_car), int(more.n), more.nm, more_yr, int(car[car.rid == cook.rusher_player_id].n.max())) == (7, 33, "F.Jackson", 2009, 32)
    assert round(ck, 2) == 0.56 and ck > lg

    # ---- chart: Buffalo's win chance through the game, with the kicking plays marked
    wc = gp[gp.home_wp_post.notna()].copy()
    wc["t"] = (3600 - wc.gs) / 60
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=200)
    ax.plot(np.r_[0, wc.t], np.r_[wp0, wc.home_wp_post], color=BLUE, lw=2, zorder=2)
    ax.axhline(0.5, color="#D5D8DE", lw=1, zorder=1)
    marks = [(muff, f"Chiefs punter fumbles;\npunt nets {muff_net} yards", RED, (20, 0.95), "left"),
             (b54, "Bass, 54 yards: tied 10-10", BLUE, (42, 0.22), "right"),
             (miss, "Butker misses from 46", RED, (52.0, 0.76), "right"),
             (ret, f"Dortch returns a punt {int(ret.return_yards)} yards", BLUE, (59.6, 0.30), "right"),
             (b57, f"Bass, 57 yards, {int(b57.gs)} seconds left", BLUE, (57.6, 0.93), "right")]
    for r_, lab, col, (tx, ty), ha in marks:
        x_ = (3600 - r_.gs) / 60
        y_ = float(r_.home_wp_post)
        ax.scatter([x_], [y_], s=60, color=col, edgecolor="white", lw=1.2, zorder=4)
        ax.annotate(lab, (x_, y_), xytext=(tx, ty), textcoords="data", fontsize=9.5, color=INK, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=4))
    for q in (15, 30, 45):
        ax.axvline(q, color="#EEF0F3", lw=1, zorder=0)
    ax.set_xlim(0, 60.5); ax.set_ylim(0, 1.02)
    ax.set_xticks([0, 15, 30, 45, 60]); ax.set_xticklabels(["Kickoff", "End of 1st", "Half", "End of 3rd", "Final"])
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_ylabel("Bills' chance to win")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.12, top=0.80)
    finish(fig, "The kicking game won it",
           "Buffalo's chance to win after every play, Bills vs. Chiefs, Nov. 26, 2026. Blue dots: Bills kicks and returns. Red: Chiefs mistakes.", "y")
    fig.texts[-1].set_text(f"Source: nflverse play-by-play and win-probability model. {len(wc)} plays.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    md = f"""# Bills {bs}, Chiefs {ks}: James Cook carried it, the kicking game won it, Tyler Bass finished it

**Buffalo beat Kansas City in the rain without much of a passing game. James Cook carried {int(cook.n)} times for {int(cook.y)} yards and scored the only Bills
touchdown. Tyler Bass tied the game from {int(b54.kick_distance)} yards and won it from {int(b57.kick_distance)} with {int(b57.gs)} seconds left. By our count, the
kicks, punts and returns, by both teams, added about {w_st * 100:.0f} percentage points to the Bills' chance to win, far more than the passing game took away ({abs(w_pass) * 100:.0f}).**

![The kicking game won it]({PNG})

## The kicking game

Every play changes a team's chance to win. Buffalo started Thursday at {wp0:.0%} and finished at 100%. The 57-yarder alone took it from about {pre57:.0%} to 100%,
and the punt return just before it was worth about {ret.bw * 100:.0f} percentage points. Add up every play by type and the game splits cleanly: the kicks, punts and
returns, by both teams, were worth about **{w_st * 100:+.0f} percentage points** to Buffalo, the runs about {w_run * 100:+.0f}, and the passing game about {w_pass * 100:+.0f},
most of that from Josh Allen's two interceptions ({w_int * 100:+.0f}). Penalties that wiped out plays account for the last {w_other * 100:+.0f}.

- **Bass from {int(b54.kick_distance)}**, early in the fourth quarter, tied it {int(tie.h)}-{int(tie.a)}.
- **Harrison Butker missed from {int(miss.kick_distance)}** with {int(miss.gs) // 60} minutes left and the game still tied.
- **Kansas City's punting:** Matt Araiza fumbled in the second quarter, and the punt netted only {muff_net} yards. With {int(ret.gs)} seconds left,
  Greg Dortch returned a punt {int(ret.return_yards)} yards to the Kansas City {ret_spot} and put Bass in range.
- **Bass from {int(b57.kick_distance)}**, {int(b57.gs)} seconds left, won it.

Kicks from 57 yards or more have been good {p57:.0%} of the time since 2023 ({len(long_)} tries). Since 2018, there have been {len(late)} field goals of 57 yards or more that
won a game in its last 10 seconds. Bass has {len(late_bass)} of them, this one and his {int(bass_prev.d)}-yarder against {prev_opp} in {bass_prev.season}. No other kicker has more than one.
It was also only the {ordn(int((two54 >= 2).sum()))} game of his career with two makes from 54 or longer.

## Cook

Cook's {int(cook.n)} carries tied his career high, set at {prev_ck_opp} in {prev_ck[:4]}. No Bill has carried more in a game since Fred Jackson's {int(more.n)} in {more_yr}. His runs worked, leaving
Buffalo more likely to score, {ck:.0%} of the time; the average NFL run this season works {lg:.0%} of the time. He scored the only Bills touchdown, his {ordn(cook_streak)}
straight game with a touchdown.

Buffalo ran {int(g0.ru)} designed runs, {g0.share:.0%} of its plays, the {"tied for " if ties else ""}{ordn(share_rank)}-highest share in its {len(bg)} regular-season games since 2018.

## Allen's quiet day

The flip side: Allen completed {int(me.cmp)} of {int(me.att)} passes for {int(me.y)} yards with {int(me.ints)} interceptions, the fewest passing yards in any of his {len(wins)}
career wins. Only {len(below_any)} of his {len(py)} games with 15 or more throws had fewer yards, and that one was a loss. Buffalo didn't complete a pass of 20 yards
or more, the {ordn(no_big)} time that's happened in those {len(bg)} games.

## The rain, as forecast

Our model, which doesn't know about weather, projected {proj_b} to {proj_k}. The teams scored {bs} and {ks}. In [part 4](bills-chiefs-rain-and-wind.html)
we found teams in rain and a 10+ mph wind had scored about {rain_pts} points each, against the {rain_usual} we'd expect from the same teams in dry weather. Thursday came in well below even
that. One game proves nothing, but it was the kind of game the forecast pointed to.

## The recipe from part 3

[Part 3](bills-chiefs-slowing-mahomes.html) named three things that slowed Mahomes: pressure, no big pass plays, and stopping the run.

- **Big plays:** {int(t.loc['KC', 'big'])} of Kansas City's {int(t.loc['KC', 'db'])} pass plays gained 20 or more yards ({kc_big:.0%}). In Mahomes' typical game since
  2023 it's {med_big:.0%}. That's close to normal, so call this one even, not a win for Buffalo.
- **The run:** Kansas City's runs worked, leaving it more likely to score, {kc_run:.0%} of the time ({kc_runs} runs), above Mahomes' typical game ({med_run:.0%}). Buffalo, {ordn(run_rank)} against the run in part 3, didn't stop it.
- **Pressure:** the charting data isn't out yet. We'll add it when it is.

This is one game, {int(t.loc['KC', 'db'])} pass plays and {kc_runs} runs, so it's a small sample.

## Receipts

Both of our calls hit. The Bills won ({g24.probability:.0%}), and Allen ran {a_runs} times ({int(runs.d)} designed runs, {int(runs.sc)} scrambles), so "4 or more"
({g25.probability:.0%}) came in. Our accuracy scores: {g24.brier:.2f} and {g25.brier:.2f}, where 0 is a perfect call. Our record is now {right} of {len(led)}.

## For the stat-heads

- Win chance by play type: nflverse `wpa` from Buffalo's side, summed by play type; pregame {wp0:.3f} + {w_st:+.3f} + {w_run:+.3f} + {w_pass:+.3f} + {w_other:+.3f} (no-plays) = 1. Kicking game = nflverse `special` = 1 (field goals,
  extra points, punts, kickoffs; nflverse leaves `special_teams_play` = 0 on field goals). Passing = `pass` = 1, runs = `rush` = 1, no-plays left out.
- Long field goals: every attempt in our play-by-play, 2018 on (kick details aren't in our 1999-2017 table). Late winner = made, 10 seconds or fewer left,
  kicking team tied or down 1-2 before the kick.
  57+ make rate {p57:.3f} on {len(long_)} attempts, 2023 through Week {WK} of 2026. Bass's earlier one: {bass_prev.game_id}, {int(bass_prev.d)} yards.
- Cook: 32 carries tie his max in nflverse; Bills games with a 32+ carry rusher since 1999: {len(big_car)}, most recently above 32: {more.game_id}. Run "worked" = nflverse `success`;
  league = 2026 designed runs through Week {WK} ({lg:.3f}).
- Allen games: passer with 15+ attempts (sacks excluded), regular season and playoffs, 2018 through 2026 Week {WK}. Wins: {len(wins)}. Median passing yards in wins {med:.0f}.
- Designed run share: `rush` = 1 over pass + rush plays (no kneels, spikes, two-point tries, no-plays). 20+ passes: dropbacks with `yards_gained` >= 20.
- Part 3 measures use Mahomes games since 2023, as part 3 did; run "worked" = nflverse `success`.
- Weather from nflverse's game note ("{wx}").
- Ledger: P0024 Brier {g24.brier:.4f}; P0025 Brier {g25.brier:.4f}. 2026 play-by-play fingerprint through Week {WK}: {(int(fp.n), float(fp.s))}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": f"Bills {bs}, Chiefs {ks}",
        "big": [[int(b57.kick_distance), f"yards: Tyler Bass's winning field goal, {int(b57.gs)} seconds left"], [int(cook.n), f"James Cook carries; no Bill has had more since {more_yr}"]],
        "note": f"Kicks, punts and returns added about {w_st * 100:.0f} percentage points to Buffalo's chance to win; the passing game took away {abs(w_pass) * 100:.0f}. Both of our Ledger calls hit.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
