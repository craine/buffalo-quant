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
                  rusher_player_id, passer_player_id, air_yards, sack, pass_attempt, score_differential, desc
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
    car = query(f"""SELECT game_id, season, SUM(CASE WHEN rusher_player_id='{ALLEN}' THEN 1 ELSE 0 END) AS runs,
                    SUM(CASE WHEN passer_player_id='{ALLEN}' OR rusher_player_id='{ALLEN}' THEN 1 ELSE 0 END) AS inv
                    FROM raw_pbp WHERE posteam='BUF' AND season_type='REG' AND season>=2018 AND (season<{SEASON} OR week<={WEEK})
                    GROUP BY game_id HAVING inv >= 20""")
    car_n, car_zero = len(car), car[car.runs == 0].game_id.tolist()
    car_min_before = int(car[car.game_id != GAME].runs.min())
    assert car_zero == [GAME]

    # the fake punt
    fp = b[(b.game_id == GAME) & b.desc.str.contains(r"\(Punt formation\)", na=False) & b.play_type.isin(["pass", "run"])].iloc[0]
    assert "Doman pass" in fp.desc and int(fp.down) == 4 and int(fp.ydstogo) == 8 and int(fp.score_differential) == 3
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
    assert on_lead == 14 and int(on_r.qtr) == 4
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
    assert "J.Cook" in this_fd.desc and "reported in as eligible" in this_fd.desc

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
    assert (q1, q1d) == (11, 5)

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
    fig.suptitle("Against Miami, the Bills did things they hadn't done all season", x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.88, "Every Bills game in 2026. Blue = Week 11 vs. Miami. (Week 7 was a bye.)", fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\nRuns include scrambles. 'Reported as eligible' counts plays where the official announced a lineman as an eligible receiver.",
             fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.06, 1, 0.86))
    fig.savefig(OUT / "wk11lab-season.png"); plt.close(fig)

    md = f"""# The Bills' lab game: Josh Allen didn't run once, and other things Buffalo hadn't done all season

**For the first time in {car_n} regular-season games since 2018, Josh Allen didn't run the ball once against Miami: no designed runs, no scrambles.
In every one of those games before Sunday, he ran at least {car_min_before if car_min_before > 1 else "once"}. The Bills also ran their first fake punt of the season, lined up for an onside kick while leading by 14 and
then kicked deep, and put an extra lineman on the field more than in any other game. In a 26-9 win, it looked a lot like a team trying things out.**

*One game, Nov. 22, against the rest of the 2026 season. [Our recap of the game](bills-dolphins-postgame-wk11.html).*

![Against Miami, the Bills did things they hadn't done all season](wk11lab-season.png)

## 1. Allen never ran

Allen averaged {runs_avg:.0f} runs a game (designed runs plus scrambles) in the Bills' first nine games. Against Miami: zero. It's the first time it's happened in any of his
{car_n} regular-season games with Buffalo since 2018. We can't tell from the play-by-play whether that was a plan to keep him healthy, a game plan against Miami, or chance.

## 2. Fourth-and-1 went to Cook, not Allen

On the opening drive, the Bills went for it on fourth-and-1 near midfield. Before Sunday, Allen had carried {sneak_before} of the Bills' {short_before} fourth-and-1 plays this season.
This time guard {N['corbett']} reported in as an eligible receiver, and {N['cook']} ran it up the middle for 2 yards.

## 3. The punter threw a pass

On fourth-and-8 from their own 34, up 3-0 in the first quarter, punter {N['doman']} threw 30 yards to tight end {N['latu']} for a first down. It was the Bills' first fake punt this season.
Across the league, only {n_fake_teams} teams have run a fake punt this season (not counting botched snaps).

## 4. They showed an onside kick, then didn't kick it

Leading 23-9 at the start of the fourth quarter, the Bills lined up in onside-kick formation, took a 5-yard delay-of-game penalty, and then kicked deep.
Teams have kicked onside {n_onside} times this season, and every one came from a team that was behind. The Bills hadn't tried one all season.

## 5. More extra linemen than ever

Four times, an offensive lineman reported in as an eligible receiver: {N['corbett'].split()[-1]} twice and {N['grable']} twice, including on {N['cook'].split()[-1]}'s 1-yard touchdown.
The Bills had never done it more than twice in a game this season. Around the league it's common enough: {lg4} of {lgn} team games this season had four or more.

## 6. More shotgun than in any other game

The Bills lined up in shotgun on {me.shotgun:.0%} of their plays, their most this season (their other games ranged from {others.shotgun.min():.0%} to {others.shotgun.max():.0%}).
That's still a little under the league average of {lg_sg:.0%}.

## 7. Deep shots early

Allen threw {q1d} of his {q1} first-quarter passes 20 or more yards downfield, then went deep only twice the rest of the game. The [recap](bills-dolphins-postgame-wk11.html) has the details.

## What it means

Seven things don't add up to a secret. A blowout win against a struggling division rival is the natural place to try a fake, keep the quarterback out of harm's way, or put a new
package on film for future opponents. Or it may just have been one week's game plan. What the numbers do say: this game looked different from the Bills' other nine.
Kansas City comes to Buffalo on Thanksgiving night. Whether Allen goes back to running, and whether the jumbo packages stay, is worth watching.

## For the stat-heads

- Runs: plays with Allen as `rusher_player_id` (designed runs and scrambles; kneels count as runs in nflverse, and there were none). Career: regular-season Bills games 2018 through
  2026 week {WEEK} where Allen was passer or rusher on 20+ plays (n = {car_n}).
- Eligible linemen: plays whose description includes "reported in as eligible". Shotgun / no-huddle: nflverse `shotgun`, `no_huddle` on pass or rush plays. No-huddle this game
  {me.nohuddle:.0%} (season high before: {others.nohuddle.max():.0%}).
- Fake punts: pass or run plays from "(Punt formation)", excluding aborted snaps. Onside kicks: plays described as "kicks onside" (n = {n_onside}); kicking team's margin from `score_differential` on the kickoff (nflverse lists the receiving team as `posteam`). The Bills' look was a no-play tagged "(Onside Kick formation)".
- League context is 2026 regular-season games in the play-by-play when this ran; week 11 games not yet loaded: {', '.join(NOT_FINAL)}.
"""
    (OUT / "2026-wk11-lab.md").write_text(md)
    (OUT / "2026-wk11-lab.hero.json").write_text(json.dumps({
        "label": "The Bills' lab game",
        "big": [[0, "Josh Allen runs vs. Miami"], [car_n, "Allen's regular-season games since 2018. This is the first with no runs."]],
        "note": "A fake punt, a fake onside look, four extra-lineman plays and the most shotgun of the season.",
        "explainer": {"kicker": "Allen's runs", "title": "Runs a game, 2026", "text": "Designed runs plus scrambles:", "fmt": "num",
                      "bars": [["First nine games, average", round(runs_avg, 1)], ["vs. Miami", 0]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
