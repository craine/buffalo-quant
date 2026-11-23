"""The Bills' "lab game": Week 11 vs. Miami (Nov. 22, 2026) next to the rest of the season.

Writes reports/2026-wk11-lab.md, one PNG (wk11lab-season.png) and a hero JSON. Every number is computed here from raw_pbp
(nflverse). Pinned to 2026 regular-season games through week 11 that were in the play-by-play when this ran (same pin as
src/reports/wk11_postgame.py). Allen's career runs cover every regular-season Bills game since 2018.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED

OUT = ROOT / "reports"
SEASON, WEEK, GAME, ALLEN = 2026, 11, "2026_11_MIA_BUF", "00-0034857"
NOT_FINAL = ("2026_11_NYJ_LAC", "2026_11_JAX_NYG", "2026_11_LV_DEN", "2026_11_MIN_SF", "2026_11_CIN_WAS")  # not in play-by-play when built
SRC = "Source: nflverse play-by-play. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 10})


def main():
    p = query(f"""SELECT game_id, week, play_id, qtr, time, posteam, play_type, down, ydstogo, rush, pass, shotgun, no_huddle,
                  rusher_player_id, passer_player_id, air_yards, sack, pass_attempt, score_differential, desc,
                  yards_gained, yardline_100, posteam_score, defteam_score, touchdown, qb_kneel, two_point_attempt
                  FROM raw_pbp WHERE season={SEASON} AND season_type='REG' AND week<={WEEK}""")
    p = p[~p.game_id.isin(NOT_FINAL)]
    b = p[p.posteam == "BUF"]
    pl = b[(b.rush == 1) | (b["pass"] == 1)]
    g = pl.groupby("game_id").agg(week=("week", "first"), plays=("rush", "size"),
                                 runs=("rusher_player_id", lambda x: int((x == ALLEN).sum())),
                                 shotgun=("shotgun", "mean"), nohuddle=("no_huddle", "mean"),
                                 elig=("desc", lambda x: int(x.str.contains("reported in as eligible", na=False).sum()))).sort_values("week")
    assert len(g) == 10 and g.index[-1] == GAME
    me, others = g.loc[GAME], g.drop(GAME)
    assert me.runs == 0 and others.runs.min() == 2 and me.elig == 4 and others.elig.max() == 2
    assert me.shotgun > others.shotgun.max()
    runs_avg = float(others.runs.mean())

    # Allen's career: regular-season games since 2018 where he was involved in 20+ plays
    # runs exclude kneel-downs and two-point tries (same definition as the season numbers, which use rush == 1 plays)
    carall = query(f"""SELECT game_id, season,
                    SUM(CASE WHEN rusher_player_id='{ALLEN}' AND COALESCE(qb_kneel,0)=0 AND COALESCE(two_point_attempt,0)=0 THEN 1 ELSE 0 END) AS runs,
                    SUM(CASE WHEN passer_player_id='{ALLEN}' OR rusher_player_id='{ALLEN}' THEN 1 ELSE 0 END) AS inv
                    FROM raw_pbp WHERE posteam='BUF' AND season_type='REG' AND season>=2018 AND (season<{SEASON} OR week<={WEEK})
                    GROUP BY game_id HAVING inv >= 1""")
    car = carall[carall.inv >= 20]
    left_out = carall[carall.inv < 20]
    car_n, car_zero = len(car), car[car.runs == 0].game_id.tolist()
    before = car[car.game_id != GAME]
    car_min_before = int(before.runs.min())
    car_min_n = int((before.runs == car_min_before).sum())
    assert car_zero == [GAME] and len(carall) == 136 and len(left_out) == 1
    lo = left_out.iloc[0]
    assert lo.game_id.startswith("2019_17") and int(lo.inv) == 5 and (car_min_before, car_min_n) == (1, 6)
    assert others.runs.min() >= 2 and round(float(others.runs.mean()), 1) == 6.2

    # the fake punt
    fp = b[(b.game_id == GAME) & b.desc.str.contains(r"\(Punt formation\)", na=False) & b.play_type.isin(["pass", "run"])].iloc[0]
    assert "Doman pass" in fp.desc and int(fp.down) == 4 and int(fp.ydstogo) == 8 and int(fp.score_differential) == 3
    fp_gain, fp_own = int(fp.yards_gained), 100 - int(fp.yardline_100)
    assert (fp_gain, fp_own, int(fp.air_yards)) == (30, 34, 27)
    lg_fake = p[p.desc.str.contains(r"\(Punt formation\)", na=False) & p.play_type.isin(["pass", "run"])]
    lg_fake_real = lg_fake[~lg_fake.desc.str.contains("Aborted", na=False)]
    buf_fake_before = int(((lg_fake_real.posteam == "BUF") & (lg_fake_real.game_id != GAME)).sum())
    assert buf_fake_before == 0
    n_fake_teams = lg_fake_real.posteam.nunique()

    # the onside look (kickoff plays have the receiving team as posteam in nflverse)
    on = p[(p.game_id == GAME) & p.desc.str.contains("Onside Kick formation", na=False)]
    assert len(on) == 1 and "PENALTY on BUF, Delay of Game" in on.desc.iloc[0]
    on_r = on.iloc[0]
    on_lead = -int(on_r.score_differential)
    assert on_lead == 14 and int(on_r.qtr) == 4 and "5 yards" in on_r.desc
    on_buf, on_mia = int(on_r.defteam_score), int(on_r.posteam_score)        # BUF kicking: defteam on a kickoff
    assert (on_buf, on_mia) == (23, 9)
    ok = p[p.desc.str.lower().str.contains("kicks onside", na=False)].copy()
    ok["kick_lead"] = -ok.score_differential           # kicking team's lead
    n_onside, n_onside_lead = len(ok), int((ok.kick_lead > 0).sum())
    buf_onside = int(ok.desc.str.contains("from BUF 35", na=False).sum())
    assert n_onside_lead == 0 and buf_onside == 0

    # fourth-and-short: who carried it
    fd = b[(b.down == 4) & b.play_type.isin(["run", "pass"]) & ~b.desc.str.contains(r"Punt formation", na=False)]
    fd_short = fd[fd.ydstogo <= 1]
    sneak_before = int(((fd_short.game_id != GAME) & (fd_short.rusher_player_id == ALLEN)).sum())
    short_before = int((fd_short.game_id != GAME).sum())
    this_fd = fd_short[fd_short.game_id == GAME].iloc[0]
    assert "J.Cook" in this_fd.desc and "reported in as eligible" in this_fd.desc and "Corbett" in this_fd.desc
    fd_gain = int(this_fd.yards_gained)
    assert fd_gain == 2
    # the four eligible-lineman plays: who and which one scored
    el = pl[(pl.game_id == GAME) & pl.desc.str.contains("reported in as eligible", na=False)]
    n_cor, n_gra = int(el.desc.str.contains("Corbett").sum()), int(el.desc.str.contains("Grable").sum())
    td = el[el.touchdown == 1]
    assert (len(el), n_cor, n_gra, len(td)) == (4, 2, 2, 1) and "Corbett" in td.desc.iloc[0] and "J.Cook" in td.desc.iloc[0]
    td_yds = int(td.yards_gained.iloc[0])
    assert td_yds == 1
    final = query(f"SELECT home_score, away_score FROM raw_schedules WHERE game_id='{GAME}'").iloc[0]
    fin = f"{int(final.home_score)}-{int(final.away_score)}"
    assert fin == "26-9"
    n_plays_me = int(me.plays)

    # league context for eligible-lineman games
    lgq = p[(p.rush == 1) | (p["pass"] == 1)].groupby(["game_id", "posteam"]).desc.apply(lambda x: int(x.str.contains("reported in as eligible", na=False).sum()))
    lg4, lgn = int((lgq >= 4).sum()), len(lgq)
    lg_sg = float(p[(p.rush == 1) | (p["pass"] == 1)].shotgun.mean())

    # player names from raw_players by gsis id (never typed)
    ids = {"cook": "00-0037248", "corbett": "00-0034261", "doman": "00-0041126", "grable": "00-0039882", "latu": "00-0040363"}
    nm = query("SELECT gsis_id, display_name, latest_team FROM raw_players WHERE gsis_id IN (" + ",".join(f"'{v}'" for v in ids.values()) + ")").set_index("gsis_id")
    assert (nm.latest_team == "BUF").all() and len(nm) == 5
    N = {k: nm.loc[v, "display_name"] for k, v in ids.items()}
    # deep shots early
    a = b[(b.game_id == GAME) & (b.passer_player_id == ALLEN) & (b.pass_attempt == 1) & (b.sack == 0) & b.air_yards.notna()]
    q1, q1d = int((a.qtr == 1).sum()), int(((a.qtr == 1) & (a.air_yards >= 20)).sum())
    deep_rest = int(((a.qtr > 1) & (a.air_yards >= 20)).sum())
    assert (q1, q1d, deep_rest) == (11, 5, 2)

    # ---- chart: three things, every game this season
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.4), dpi=200)
    wk = g.week.astype(int).tolist()
    cols = [BLUE if gid == GAME else GRAY for gid in g.index]
    for ax, col, ttl, fmt in ((axes[0], "runs", "Josh Allen runs\n(designed runs + scrambles)", "{:.0f}"),
                              (axes[1], "elig", "Plays with a lineman\nreporting as eligible", "{:.0f}"),
                              (axes[2], "shotgun", "Share of plays\nfrom shotgun", "{:.0%}")):
        vals = g[col].tolist()
        ax.bar(range(len(vals)), vals, 0.7, color=cols, zorder=2)
        ax.set_xticks(range(len(vals)), [str(w) for w in wk], fontsize=8.5)
        ax.set_title(ttl, fontsize=10.5, color=INK, loc="left")
        ax.text(len(vals) - 1, vals[-1] + (max(vals) * 0.03), fmt.format(vals[-1]), ha="center", fontsize=10, fontweight="bold", color=BLUE)
        ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True); ax.tick_params(axis="x", length=0)
        ax.set_xlabel("Week")
    axes[2].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    fig.suptitle("Against Miami: zero Allen runs, most extra linemen, most shotgun", x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.88, "Every Bills game in 2026. Blue = Week 11 vs. Miami. (Week 7 was a bye.)", fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC} {len(g)} games; {n_plays_me} Bills pass and run plays vs. Miami.\nRuns include scrambles, not kneel-downs. 'Reported as eligible' counts plays where the official announced a lineman as an eligible receiver.",
             fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.06, 1, 0.86))
    fig.savefig(OUT / "wk11lab-season.png"); plt.close(fig)

    md = f"""# Josh Allen didn't run once, and six more signs the Bills were trying things out against Miami

**For the first time in {car_n} regular-season games since 2018 where he played more than a handful of plays, Josh Allen didn't run the ball once against Miami:
no designed runs, no scrambles. The Bills also ran their first fake punt of the season. They lined up for an onside kick with a {on_lead}-point lead, then kicked deep.
And they sent in an extra lineman more often than in any other game this season. In a {fin} win, it looked a lot like a team trying things out.**

*One game, Nov. 22, against the rest of the 2026 season. [Our recap of the game](bills-dolphins-postgame-wk11.html).*

![Against Miami: zero Allen runs, most extra linemen, most shotgun of the season](wk11lab-season.png)

## 1. Allen never ran

Allen averaged {runs_avg:.0f} runs a game (designed runs plus scrambles) in the Bills' first nine games. Against Miami: zero. That had never happened in any of his
{car_n} regular-season games since 2018 where he played more than a handful of plays. We can't tell from the play-by-play whether that was a plan to keep him healthy,
a game plan against Miami, or chance.

How we counted: we went through the play-by-play of every Bills regular-season game since 2018 and counted each play where Allen carried the ball, not counting
kneel-downs. We kept the {car_n} games where he threw, ran or was sacked at least 20 times. That leaves out one game, the 2019 finale, when he was in for {int(lo.inv)} plays.
Before Sunday, his fewest runs in any of those games was {car_min_before}, and that happened {car_min_n} times. Never zero.

## 2. Fourth-and-1 went to Cook, not Allen

On the opening drive, the Bills went for it on fourth-and-1 near midfield. Before Sunday, Allen had carried {sneak_before} of the Bills' {short_before} fourth-and-1 plays this season.
This time guard {N['corbett']} checked in with the referee as an eligible receiver, an extra blocker on the field, and {N['cook']} ran it up the middle for {fd_gain} yards.

## 3. The punter threw a pass

On fourth-and-8 from their own {fp_own}, up 3-0 in the first quarter, punter {N['doman']} threw to tight end {N['latu']} for a {fp_gain}-yard gain and a first down.
It was the Bills' first fake punt this season. Buffalo is one of only {n_fake_teams} teams to run a fake punt this season (not counting botched snaps).

## 4. They showed an onside kick, then didn't kick it

Leading {on_buf}-{on_mia} at the start of the fourth quarter, the Bills lined up in onside-kick formation, took a 5-yard delay-of-game penalty, and then kicked deep.
Teams have kicked onside {n_onside} times this season, and every one came from a team that was behind. The Bills hadn't tried one all season.

## 5. More extra linemen than in any game this season

Four times, an offensive lineman reported in as an eligible receiver: {N['grable']} twice and {N['corbett'].split()[-1]} twice, including on {N['cook'].split()[-1]}'s {td_yds}-yard touchdown.
The Bills had never done it more than twice in a game this season. Around the league it's common enough: {lg4} of {lgn} team games this season had four or more.

## 6. More shotgun than in any other game this season

The Bills lined up in shotgun on {me.shotgun:.0%} of their plays, their most this season (their other games ranged from {others.shotgun.min():.0%} to {others.shotgun.max():.0%}).
That's still a little under the league average of {lg_sg:.0%}.

## 7. Deep shots early

Allen threw {q1d} of his {q1} first-quarter passes 20 or more yards downfield, then went deep only {"twice" if deep_rest == 2 else deep_rest} the rest of the game. The [recap](bills-dolphins-postgame-wk11.html) has the details.

## What it means

None of this proves a plan. A home game against a struggling division rival is a natural place to try a fake, keep the quarterback out of harm's way, or show future
opponents something new to study. Or it may just have been one week's game plan. What the numbers do say: this game looked different from the Bills' other nine.
Kansas City comes to Buffalo on Thanksgiving night. Whether Allen goes back to running, and whether the extra linemen stay, is worth watching.

## For the stat-heads

- Runs: plays with Allen as `rusher_player_id` (designed runs and scrambles, not kneel-downs or two-point tries; Josh Allen had none, and backup Kyle Allen took the final kneel).
  Career: regular-season Bills games 2018 through 2026 week {WEEK} where Allen was passer or rusher on 20+ plays (n = {car_n} of {len(carall)}; the one left out, {lo.game_id}, had {int(lo.inv)} plays and no runs).
- Eligible linemen: plays whose description includes "reported in as eligible". Shotgun: nflverse `shotgun` on pass or rush plays.
  Fake punt: {int(fp.air_yards)} air yards, {fp_gain}-yard gain.
- Fake punts: pass or run plays from "(Punt formation)", excluding aborted snaps. Onside kicks: plays described as "kicks onside" (n = {n_onside}); kicking team's margin from `score_differential` on the kickoff (nflverse lists the receiving team as `posteam`). The Bills' look was a no-play tagged "(Onside Kick formation)".
- League context is 2026 regular-season games in the play-by-play when this ran; week 11 games not yet loaded: {', '.join(NOT_FINAL)}.
"""
    (OUT / "2026-wk11-lab.md").write_text(md)
    (OUT / "2026-wk11-lab.hero.json").write_text(json.dumps({
        "label": "Bills vs. Miami: trying things out?",
        "big": [[0, "Josh Allen runs vs. Miami"], [car_n, "Allen's regular-season games since 2018 with more than a handful of plays. First with no runs."]],
        "note": f"A fake punt, an onside-kick formation with a {on_lead}-point lead, four extra-lineman plays and the most shotgun of the season.",
        "explainer": {"kicker": "Allen's runs", "title": "Runs a game, 2026", "text": "Designed runs plus scrambles:", "fmt": "num",
                      "bars": [["First nine games, average", round(runs_avg, 1)], ["vs. Miami", 0]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
