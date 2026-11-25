"""Bills-Chiefs series, part 3 (Nov. 25, 2026): how teams have slowed Patrick Mahomes.

Every regular-season Mahomes start since 2023 (20+ dropbacks), split by three things the defense did: pressure, big pass plays allowed,
and the Chiefs' running game. Then where Buffalo's 2026 defense stands on each.

Writes reports/2026-wk12-kc-mahomes.md, one PNG (bills-kc-wk12-mahomes.png) and a hero JSON.

Sources and pins:
- Plays: nflverse play-by-play; pass and run plays, EPA not null, no two-point tries, kneels, spikes or no-plays; regular season.
- Pressure on Mahomes: PFR `times_pressured` (raw_pfr_pass), per Kansas City dropback. Team pressure: PFR `def_pressures` (raw_pfr_def).
- Extra rushers: FTN charting.
- 2023-2025 full seasons; 2026 pinned to weeks 1-10 (every game charted by PFR and FTN).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED
from src.reports.wk11_postgame import finish, ordn as _ordn

OUT = ROOT / "reports"
SLUG = "2026-wk12-kc-mahomes"
PNG = "bills-kc-wk12-mahomes.png"
MAHOMES, MAHOMES_PFR = "00-0033873", "MahoPa00"
WK26 = 10
KC_RED = "#E31837"
PLAYS = """p.season_type = 'REG' AND (p.pass = 1 OR p.rush = 1) AND p.epa IS NOT NULL AND p.play_type <> 'no_play'
           AND COALESCE(p.two_point_attempt, 0) = 0 AND COALESCE(p.qb_kneel, 0) = 0 AND COALESCE(p.qb_spike, 0) = 0
           AND (p.season BETWEEN 2023 AND 2025 OR (p.season = 2026 AND p.week <= {wk}))"""


def ordn(n):
    return _ordn(int(n))


# nflverse re-posted 2026 play-by-play on Nov. 25, 2026 (10:02 GMT) with new EPA values. Pin the version this story uses.
PBP26_FINGERPRINT = (25946, -222.5969)


def main():
    fp = query(f"SELECT COUNT(*) n, ROUND(SUM(epa), 4) s FROM raw_pbp WHERE season = 2026 AND season_type = 'REG' AND week <= {WK26} AND epa IS NOT NULL").iloc[0]
    assert (int(fp.n), float(fp.s)) == PBP26_FINGERPRINT, f"2026 play-by-play changed since publication: {tuple(fp)}"
    p = query(f"""SELECT p.season, p.week, p.game_id, p.posteam, p.defteam, p.epa, p.pass AS ps, p.rush AS ru, p.qb_scramble,
                  p.yards_gained, p.success, p.passer_player_id, p.rusher_player_id, f.n_pass_rushers AS nr
                  FROM raw_pbp p LEFT JOIN raw_ftn f ON f.nflverse_game_id = p.game_id AND f.nflverse_play_id = p.play_id
                  WHERE p.posteam = 'KC' AND {PLAYS.format(wk=WK26)}""")
    p.loc[p.nr > 11, "nr"] = np.nan
    qb = p.passer_player_id.fillna(p.rusher_player_id)
    n_db = p[(qb == MAHOMES) & (p.ps == 1)].groupby("game_id").size()
    games = n_db[n_db >= 20].index
    p = p[p.game_id.isin(games)]
    d = p[p.ps == 1]
    r = p[(p.ru == 1) & (p.qb_scramble.fillna(0) == 0)]                     # designed runs only

    sc = query("SELECT game_id, home_team, home_score, away_score FROM raw_schedules WHERE season BETWEEN 2023 AND 2026")
    sc["kc"] = np.where(sc.home_team == "KC", sc.home_score, sc.away_score)
    sc["opp"] = np.where(sc.home_team == "KC", sc.away_score, sc.home_score)
    sc = sc.set_index("game_id")
    pf = query(f"""SELECT game_id, times_pressured FROM raw_pfr_pass WHERE pfr_player_id = '{MAHOMES_PFR}' AND game_type = 'REG'
                   AND season BETWEEN 2023 AND 2026""").set_index("game_id")

    G = pd.DataFrame(index=pd.Index(games, name="game_id"))
    G["season"] = p.groupby("game_id").season.first()
    G["kc"], G["opp"] = sc.kc, sc.opp
    G["win"] = G.kc > G.opp
    G["db"] = d.groupby("game_id").size()
    G["pr"] = pf.times_pressured
    G["pr_rt"] = G.pr / G.db
    G["expl"] = d.groupby("game_id").yards_gained.apply(lambda x: (x >= 20).mean())
    G["run_sr"] = r.groupby("game_id").success.mean()
    G["five"] = d.groupby("game_id").nr.apply(lambda x: (x >= 5).mean())
    assert G.pr.notna().all() and G.run_sr.notna().all(), "every Mahomes start needs PFR pressure and at least one run"
    n_g, n_w = len(G), int(G.win.sum())
    by_season = G.groupby("season").size().to_dict()
    assert (n_g, n_w) == (55, 38) and by_season == {2023: 16, 2024: 16, 2025: 14, 2026: 9}

    # the three things, each split at the typical (median) game
    med = {c: float(G[c].median()) for c in ("pr_rt", "expl", "run_sr", "five")}
    did = {"pr_rt": G.pr_rt > med["pr_rt"], "expl": G.expl < med["expl"], "run_sr": G.run_sr < med["run_sr"], "five": G.five > med["five"]}
    S = {}
    for c, m in did.items():
        S[c] = dict(pts_y=float(G[m].kc.mean()), win_y=float(G[m].win.mean()), n_y=int(m.sum()),
                    pts_n=float(G[~m].kc.mean()), win_n=float(G[~m].win.mean()), n_n=int((~m).sum()))
    allk = did["pr_rt"] & did["expl"] & did["run_sr"]
    nonek = ~did["pr_rt"] & ~did["expl"] & ~did["run_sr"]
    all_pts, all_win, all_n = float(G[allk].kc.mean()), float(G[allk].win.mean()), int(allk.sum())
    none_pts, none_win, none_n = float(G[nonek].kc.mean()), float(G[nonek].win.mean()), int(nonek.sum())
    rest_pts, rest_win, rest_n = float(G[~allk].kc.mean()), float(G[~allk].win.mean()), int((~allk).sum())
    all_w = int(G[allk].win.sum())
    assert all_n == 8 and round(all_pts, 1) == 16.5 and round(all_win, 2) == 0.5
    for c in ("pr_rt", "expl", "run_sr"):
        assert S[c]["pts_y"] < S[c]["pts_n"] and S[c]["win_y"] < S[c]["win_n"]
    assert abs(S["five"]["pts_y"] - S["five"]["pts_n"]) < 1.5                  # extra rushers: no real difference

    # second check: all four at once (points per one standard deviation)
    X = G[["pr_rt", "expl", "run_sr", "five"]]
    Z = (X - X.mean()) / X.std()
    Z["c"] = 1.0
    coef, *_ = np.linalg.lstsq(Z.values, G.kc.values.astype(float), rcond=None)
    fit = dict(zip(Z.columns, coef))
    assert fit["pr_rt"] < -1.5 and fit["expl"] > 2 and fit["run_sr"] > 1.5 and abs(fit["five"]) < 1.5

    # low-scoring games: the run game
    low = G.kc <= 20
    low_run, hi_run, n_low = float(G[low].run_sr.mean()), float(G[~low].run_sr.mean()), int(low.sum())

    # ---- Buffalo's 2026 defense, weeks 1-10
    a = query(f"""SELECT p.defteam, p.game_id, p.pass AS ps, p.rush AS ru, p.qb_scramble, p.yards_gained, p.success, p.sack
                  FROM raw_pbp p WHERE p.season = 2026 AND {PLAYS.format(wk=WK26)}""")
    adb = a[a.ps == 1]
    ar = a[(a.ru == 1) & (a.qb_scramble.fillna(0) == 0)]
    pfd = query(f"SELECT team, SUM(def_pressures) pr FROM raw_pfr_def WHERE season = 2026 AND game_type = 'REG' AND week <= {WK26} GROUP BY 1").set_index("team").pr
    T = pd.DataFrame({"db": adb.groupby("defteam").size(), "expl": adb.groupby("defteam").yards_gained.apply(lambda x: (x >= 20).mean()),
                      "run_sr": ar.groupby("defteam").success.mean()})
    T["pr_rt"] = pfd / T.db
    T["pr_rk"] = T.pr_rt.rank(ascending=False, method="min").astype(int)     # 1 = most pressure
    T["expl_rk"] = T.expl.rank(method="min").astype(int)                    # 1 = fewest big plays allowed
    T["run_rk"] = T.run_sr.rank(method="min").astype(int)                   # 1 = stingiest against the run
    B = T.loc["BUF"]
    lgT = dict(pr_rt=float(pfd.sum() / T.db.sum()), expl=float((adb.yards_gained >= 20).mean()), run_sr=float(ar.success.mean()))
    assert (int(B.pr_rk), int(B.expl_rk), int(B.run_rk)) == (4, 20, 27)
    # what counts as a successful run: real examples, designed runs 2023-26
    ex = query(f"""SELECT p.down, p.ydstogo, p.yards_gained, p.success, p.first_down FROM raw_pbp p
                   WHERE p.rush = 1 AND COALESCE(p.qb_scramble, 0) = 0 AND p.play_type = 'run' AND {PLAYS.format(wk=WK26)}""")
    f10 = ex[(ex.down == 1) & (ex.ydstogo == 10)]
    s4, s5, s6 = (float(f10[f10.yards_gained == y].success.mean()) for y in (4, 5, 6))
    t2 = ex[(ex.down == 3) & (ex.ydstogo == 2) & (ex.first_down == 1)]
    s32 = float(t2.success.mean())
    assert s4 < 0.15 and s5 > 0.6 and s6 > 0.9 and s32 > 0.95

    # Kansas City's 2026 offense, same three
    k26 = G[G.season == 2026]
    kc_expl, kc_run, kc_pr = float(d[d.season == 2026].yards_gained.ge(20).mean()), float(r[r.season == 2026].success.mean()), float(k26.pr.sum() / k26.db.sum())
    off = query(f"""SELECT p.posteam, p.pass AS ps, p.rush AS ru, p.qb_scramble, p.yards_gained, p.success FROM raw_pbp p
                    WHERE p.season = 2026 AND {PLAYS.format(wk=WK26)}""")
    odb = off[off.ps == 1]
    orr = off[(off.ru == 1) & (off.qb_scramble.fillna(0) == 0)]
    kc_expl_rk = int(odb.groupby("posteam").yards_gained.apply(lambda x: (x >= 20).mean()).rank(ascending=False, method="min")["KC"])
    kc_run_rk = int(orr.groupby("posteam").success.mean().rank(ascending=False, method="min")["KC"])

    # ---- chart: three panels, KC points per game
    panels = [("Pressured Mahomes\nmore than usual", "pr_rt", f"Bills 2026: {ordn(B.pr_rk)} in pressure"),
              ("Allowed fewer\n20-yard passes", "expl", f"Bills 2026: {ordn(B.expl_rk)} against big plays"),
              ("Stopped the Chiefs'\nrunning game", "run_sr", f"Bills 2026: {ordn(B.run_rk)} against the run")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.0), dpi=200, sharey=True)
    for ax, (ttl, c, note) in zip(axes, panels):
        vals = [S[c]["pts_y"], S[c]["pts_n"]]
        ax.bar([0, 1], vals, 0.6, color=[BLUE, GRAY], zorder=2)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.5, f"{v:.1f}", ha="center", fontsize=12, fontweight="bold", color=INK)
        ax.set_xticks([0, 1], [f"Yes\n({S[c]['n_y']} games)", f"No\n({S[c]['n_n']} games)"], fontsize=9.5)
        ax.set_title(ttl, fontsize=11, color=INK, loc="left")
        ax.text(0.5, -0.27, note, transform=ax.transAxes, ha="center", fontsize=9.5, color=BLUE, fontweight="bold")
        ax.tick_params(axis="x", length=0)
        ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    axes[0].set_ylabel("Chiefs points per game")
    axes[0].set_ylim(0, 32)
    fig.subplots_adjust(bottom=0.27, top=0.74, wspace=0.12)
    finish(fig, "Three things that have slowed Patrick Mahomes. Buffalo does one of them",
           f"Bars: Chiefs points per game. Every regular-season Mahomes start, 2023 through Week {WK26} of 2026 ({n_g} games). 'Yes' = the defense did better than in a typical Mahomes game.",
           "x")
    fig.texts[-1].set_text(f"Source: nflverse play-by-play; pressure charted by Pro Football Reference. All three in one game ({all_n} games): Chiefs {all_pts:.1f} points, won {all_win:.0%}.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    md = f"""# How to slow down Patrick Mahomes: three things that have worked, and Buffalo does one

**In {n_g} regular-season starts since 2023, Mahomes and the Chiefs have won {n_w}. Defenses that slowed them down tended to do three things: pressure Mahomes, keep him
from hitting big passes, and stop the Chiefs' running game. In the only {all_n} games where a defense did all three, Kansas City scored {all_pts:.1f} points a game and went
{all_w}-{all_n - all_w}. Buffalo's defense gets pressure as well as almost anyone. Against big plays it ranks {ordn(B.expl_rk)}, and against the run it ranks {ordn(B.run_rk)}.**

*A "dropback" is any pass play: completions, incompletions, sacks and scrambles.*

*Part 3 of our Bills-Chiefs series. [Part 1: Rousseau and the pass rush](bills-chiefs-leonhard-file.html). [Part 2: who's left](bills-chiefs-whos-left.html).*

![Three things that have slowed Patrick Mahomes. Buffalo does one of them]({PNG})

## 1. Pressure him

When a defense pressured Mahomes more than in a typical game, Kansas City scored {S['pr_rt']['pts_y']:.1f} points and won {S['pr_rt']['win_y']:.0%}. When it didn't,
{S['pr_rt']['pts_n']:.1f} points and {S['pr_rt']['win_n']:.0%}.

Sending extra rushers didn't make the difference. In games where defenses sent five or more rushers more often than usual, the Chiefs scored {S['five']['pts_y']:.1f}
points; otherwise {S['five']['pts_n']:.1f}. About the same.

**Buffalo:** {ordn(B.pr_rk)} in the NFL in pressure this season ({B.pr_rt * 100:.0f} pressures for every 100 dropbacks; league average {lgT['pr_rt'] * 100:.0f}), led by Greg Rousseau.

## 2. Take away the big play

When a defense allowed fewer 20-yard pass plays than usual, Kansas City scored {S['expl']['pts_y']:.1f} points and won {S['expl']['win_y']:.0%}.
Otherwise, {S['expl']['pts_n']:.1f} and {S['expl']['win_n']:.0%}.

**Buffalo:** opponents gain 20 or more yards on {B.expl:.1%} of dropbacks, {ordn(B.expl_rk)} in the NFL (league average {lgT['expl']:.1%}). This season the Chiefs
hit one on {kc_expl:.1%} of Mahomes' dropbacks ({ordn(kc_expl_rk)} among offenses).

## 3. Stop the run

When a defense stopped the Chiefs' runs more often than usual, Kansas City scored {S['run_sr']['pts_y']:.1f} points and won {S['run_sr']['win_y']:.0%}.
Otherwise, {S['run_sr']['pts_n']:.1f} and {S['run_sr']['win_n']:.0%}. In the {n_low} games where they scored 20 or fewer, their runs worked {low_run:.0%} of the time,
against {hi_run:.0%} in the rest.

**Buffalo:** opponents' designed runs work {B.run_sr:.0%} of the time, {ordn(B.run_rk)} in the NFL (league average {lgT['run_sr']:.0%}). Kansas City's runs
work {kc_run:.0%} of the time this season ({ordn(kc_run_rk)}).

## All three at once

In the {all_n} games where a defense did all three, the Chiefs averaged {all_pts:.1f} points and went {all_w}-{all_n - all_w}. That's a small sample.
In their other {rest_n} games: {rest_pts:.1f} points, and they won {rest_win:.0%}. Mahomes still wins plenty of games where defenses do things right. But it's the closest thing to a recipe in the data.

## What it means Thursday

Buffalo's pass rush gives it a real shot at the first part. The question is everything else. Buffalo is {ordn(B.expl_rk)} at stopping big pass plays and {ordn(B.run_rk)} against the run,
and Kansas City runs the ball well ({ordn(kc_run_rk)}).
Watch two things early: whether the Chiefs can run the ball, and whether Mahomes finds anything deep.

## How we measured it

We took every regular-season game Mahomes started since 2023 (at least 20 dropbacks), {n_g} in all: {by_season[2023]} in 2023, {by_season[2024]} in 2024, {by_season[2025]} in 2025,
and {by_season[2026]} this season through Week {WK26}. For each, we measured three things against a typical Mahomes game (the middle game of the {n_g}):

- **Pressure:** pressures charted by Pro Football Reference, per dropback. Typical: {med['pr_rt'] * 100:.0f} for every 100.
- **Big plays:** share of dropbacks that gained 20 or more yards. Typical: {med['expl']:.1%}.
- **Running game:** share of designed runs (not quarterback scrambles) that left the Chiefs more likely to score than before the snap. On first-and-10 that usually takes 5 yards:
  a 4-yard run counted {s4:.0%} of the time, 5 yards {s5:.0%}, 6 yards {s6:.0%}. On third-and-2, a run that got the first down counted {s32:.0%} of the time. Typical: {med['run_sr']:.0%}.

We checked it a second way, putting all four measures (including extra rushers) into one calculation of Kansas City's points. Each of the three mattered on its own: a typical swing in any one was worth
2 to 3 points. Extra rushers added nothing. These are patterns from {n_g} games, not proof that any one tactic causes a loss.

## For the stat-heads

- Games: Mahomes as passer or scrambler on 20+ dropbacks, regular season, 2023 to 2026 Week {WK26} (n = {n_g}; KC {n_w}-{n_g - n_w}).
- Data: nflverse play-by-play as re-posted Nov. 25, 2026 (2026 EPA changed in that update; fingerprint asserted). Run "worked" = nflverse `success` (EPA > 0). Ties at the median count as "No".
- Medians: pressure rate {med['pr_rt']:.3f} (PFR `times_pressured` / nflverse dropbacks), 20+ yard dropback rate {med['expl']:.3f}, designed-run success {med['run_sr']:.3f}, FTN 5+ rushers {med['five']:.3f}.
- Split results (KC pts, win rate, n): pressure {S['pr_rt']['pts_y']:.1f}/{S['pr_rt']['win_y']:.3f}/{S['pr_rt']['n_y']} vs {S['pr_rt']['pts_n']:.1f}/{S['pr_rt']['win_n']:.3f}/{S['pr_rt']['n_n']};
  explosives {S['expl']['pts_y']:.1f}/{S['expl']['win_y']:.3f} vs {S['expl']['pts_n']:.1f}/{S['expl']['win_n']:.3f}; run {S['run_sr']['pts_y']:.1f}/{S['run_sr']['win_y']:.3f} vs {S['run_sr']['pts_n']:.1f}/{S['run_sr']['win_n']:.3f};
  5+ rushers {S['five']['pts_y']:.1f}/{S['five']['win_y']:.3f} vs {S['five']['pts_n']:.1f}/{S['five']['win_n']:.3f}.
- OLS of KC points on standardized measures (points per 1 SD): pressure {fit['pr_rt']:+.2f}, 20+ rate {fit['expl']:+.2f}, run success {fit['run_sr']:+.2f}, 5+ rushers {fit['five']:+.2f}. n = {n_g}; descriptive.
- BUF 2026 wk 1-{WK26} defense: pressure {B.pr_rt:.3f} ({int(B.pr_rk)}), 20+ allowed {B.expl:.3f} ({int(B.expl_rk)}), run success allowed {B.run_sr:.3f} ({int(B.run_rk)}). League {lgT['pr_rt']:.3f}, {lgT['expl']:.3f}, {lgT['run_sr']:.3f}.
- KC 2026 offense: 20+ rate {kc_expl:.3f} ({kc_expl_rk}), run success {kc_run:.3f} ({kc_run_rk}), pressure on Mahomes {kc_pr:.3f}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Slowing down Mahomes, 2023-26",
        "big": [[round(all_pts, 1), f"Chiefs points a game when the defense did all three ({all_n} games)"],
                [round(float(G.kc.mean()), 1), f"Chiefs points a game in all {n_g} Mahomes starts since 2023"]],
        "note": f"Pressure him, take away big plays, stop the run. Buffalo is {ordn(B.pr_rk)} in pressure, {ordn(B.expl_rk)} against big plays and {ordn(B.run_rk)} against the run.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
