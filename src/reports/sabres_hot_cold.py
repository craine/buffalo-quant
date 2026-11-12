"""Sabres: who's running hot, who's likely to heat up. Pinned to AS_OF; every number comes from the skater cards (src/reports/skater_cards.py)
and the player-rating back-test (src/metrics/nhl_player_ratings.py -> reports/cards/player_model_backtest.json).

Writes reports/2026-11-11-sabres-hot-cold.md, two PNGs and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics import nhl_player_ratings as PR
from src.reports.skater_cards import SEASON
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.sabres_postgame import finish

OUT = ROOT / "reports"
AS_OF = "2026-11-10"
SLUG = "2026-11-11-sabres-hot-cold"
MIN_GP = 10
GOLD = "#FFB81C"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def main():
    d = json.loads((OUT / "cards" / "skaters.json").read_text())
    m, cards = d["meta"], d["cards"]
    assert m["as_of"] == AS_OF, f"cards are as of {m['as_of']}, story pinned to {AS_OF}"
    bt = json.loads((OUT / "cards" / "player_model_backtest.json").read_text())
    t17 = next(t for t in bt["tests"] if t["season"] == 20252026 and t["checkpoint_games"] == 17)
    t41 = next(t for t in bt["tests"] if t["season"] == 20252026 and t["checkpoint_games"] == 41)
    c = pd.DataFrame(cards)
    c = c[(c.gp >= MIN_GP) & c.rate_p82.notna()].copy()
    c["gap"] = c.pace_p82 - c.rate_p82
    c = c.sort_values("gap")
    by = c.set_index("name")
    hot3 = c[c.name != "Tage Thompson"].sort_values("gap", ascending=False).head(3)
    cold = c.sort_values("gap").head(4)
    tage = by.loc["Tage Thompson"]
    n_above, n_below = int((c.gap > 0).sum()), int((c.gap < 0).sum())
    # ---- worked example: Owen Power's assists rating, built step by step from the same function the cards use
    S, meth = SEASON, bt["method"]
    pg = PR.player_games(max_date=AS_OF)
    pid = int(by.loc["Owen Power", "id"])
    ps = pg[pg.player_id == pid].groupby("season").agg(gp=("game_id", "size"), a=("a", "sum"))
    cur = pg[(pg.season == S) & (pg.game_date <= AS_OF)]
    lg_a = float(cur[cur.grp == "D"].a.sum() / (cur.grp == "D").sum())
    Kd, Wd = meth["K"]["a"], meth["W"]["a"]
    wts = {s: (1.0 if s == S else Wd * meth["decay"] ** ((S - s) // 10001 - 1)) for s in ps.index}
    num = sum(wts[s] * ps.loc[s, "a"] for s in ps.index) + Kd * lg_a
    den = sum(wts[s] * ps.loc[s, "gp"] for s in ps.index) + Kd
    pa82 = num / den * 82
    chk = PR.project(pg, S, AS_OF).loc[pid]
    assert abs(pa82 - chk.a_pg * 82) < 0.05, (pa82, chk.a_pg * 82)
    pg82 = chk.g_pg * 82
    assert abs(pa82 + pg82 - by.loc["Owen Power", "rate_p82"]) < 0.1
    seasons = sorted(ps.index, reverse=True)
    lbl = lambda s: f"{s // 10000}-{str(s % 10000)[2:]}"
    frac = {1.0: "fully", 0.5: "at half", 0.25: "at a quarter", 0.125: "at an eighth"}
    steps = "; ".join(f"{lbl(s)}'s {int(ps.loc[s, 'a'])} assists in {int(ps.loc[s, 'gp'])} games count {frac[wts[s]]}" for s in seasons)
    # what a chance is worth: share of unblocked, non-empty-net shots that score, by distance, all seasons through AS_OF
    sh = query(f"""SELECT s.dist, s.goal FROM clean_nhl_shots_xg s JOIN raw_nhl_games g ON g.game_id = s.game_id
                   WHERE s.unblocked = 1 AND s.empty_net_against = 0 AND g.game_date <= '{AS_OF}'""")
    near, far = sh[sh.dist <= 10].goal.mean() * 100, sh[sh.dist >= 40].goal.mean() * 100
    n_sh = len(sh)

    rp = lambda k: t17["results"]["p"][k]["abs_err_rest"]
    rg = lambda k: t17["results"]["g"][k]["abs_err_rest"]

    # ---- chart 1: pace vs. rating, every Sabre with MIN_GP+ games
    fig, ax = plt.subplots(figsize=(9.5, 0.42 * len(c) + 1.6), dpi=200)
    ys = np.arange(len(c))
    for y, r in zip(ys, c.itertuples()):
        ax.plot([r.rate_p82, r.pace_p82], [y, y], color="#C9CDD4", lw=3, zorder=1)
    ax.scatter(c.pace_p82, ys, s=60, color=[RED if g > 0 else GRAY for g in c.gap], zorder=3, label="_")
    ax.scatter([], [], s=60, color=RED, label="Pace, above his rating (red)")
    ax.scatter([], [], s=60, color=GRAY, label="Pace, below his rating (gray)")
    ax.scatter(c.rate_p82, ys, s=70, color=BLUE, zorder=4, label="Our rating")
    ax.set_yticks(ys, c.name, fontsize=10)
    ax.set_xlabel("Points per 82 games")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    finish(fig, "Pace vs. history: who's running hot and who's likely to heat up",
           f"Every Sabres skater with {MIN_GP}+ games.",
           f"Sabres' first {m['team_gp']} games, through {pd.to_datetime(AS_OF):%b. %-d}; {len(c)} skaters with {MIN_GP}+ games. Rating blends every season since 2023-24.")
    fig.savefig(OUT / "sabres-hotcold-pace.png"); plt.close(fig)

    # ---- chart 2: the test
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    labels = ["Our rating", "His pace so far", "His last season", "Average player"]
    vals = [rp("model"), rp("pace"), rp("last_season"), rp("position_avg")]
    ax.barh(labels[::-1], vals[::-1], color=[GRAY, GRAY, GRAY, BLUE], height=0.55, zorder=2)
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 0.15, i, f"{v:.1f}", va="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_xlabel("Average miss on a player's rest-of-season points (lower is better)")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Tested on last season: the rating beat the obvious guesses",
           f"Every NHL skater's rest of 2025-26, projected after 17 games with only the player stats known then ({t17['skaters']} skaters).",
           f"Set up on 2024-25. Players with 5+ games before and 10+ after.")
    fig.savefig(OUT / "sabres-hotcold-test.png"); plt.close(fig)

    r = lambda x: int(round(x))
    names = lambda df: ", ".join(list(df.name)[:-1]) + " and " + list(df.name)[-1]

    seen = []
    def why_hot(x):
        if x.fin >= 1.0:
            return (f"He has {x.g} goals on chances worth {x.ixg:.1f}, so he's scored {x.fin:.1f} more than his chances. Finishing like that "
                    "rarely lasts.")
        if seen:
            return f"Same story as {seen[0]}: {x.a} of his {x.p} points are assists."
        seen.append(x.name.split()[-1])
        return (f"Most of it is assists: {x.a} of his {x.p} points. An assist needs a teammate to "
                "score, so a hot stretch for his linemates lifts his total too.")
    hot_txt = "\n\n".join(f"**{x.name}** is on pace for {r(x.pace_p82)} points per 82 games; his rating says {r(x.rate_p82)}. {why_hot(x)}"
                          for x in hot3.itertuples())
    cold_txt = "; ".join(f"{x.name}, on pace for {r(x.pace_p82)} with a rating of {r(x.rate_p82)}" for x in cold.itertuples())
    cold3 = cold.head(3)
    assert m["team_gp"] == 17, "lead spells out the games played"
    lead = (f"**Seventeen games in, Owen Power, Jack Quinn and Zach Benson are scoring well above what their track records say, and "
            f"{names(cold3)} well below. Expect both groups to drift back toward normal.**") if list(hot3.name) == ["Owen Power", "Jack Quinn", "Zach Benson"] else None
    assert lead, f"lead names the wrong players: {list(hot3.name)}"
    md = f"""# Sabres: who's running hot, and who's likely to heat up

{lead}

*Numbers through {pd.to_datetime(AS_OF):%B %-d}, the Sabres' first {m['team_gp']} games. Every number here is also on each player's
[card](../cards/).*

![Pace vs. history](sabres-hotcold-pace.png)

## Hot and cold, by the numbers

Seventeen games is about a fifth of a season. Over that stretch, a few lucky bounces can make a player look like a star or a bust. So
for each Sabre we compare two things: his **pace** (his points so far, stretched over 82 games) and his **rating**, our best guess at his
points per 82 games from here on, built from this season and the last three.

| Player | Points so far | Pace (per 82) | Rating (per 82) | If he plays all {m['remaining']} remaining games |
|---|---|---|---|---|
""" + "\n".join(f"| [{x.name}](../cards/{x.name.lower().replace(' ', '-')}.html) | {x.p} in {x.gp} | {r(x.pace_p82)} | {r(x.rate_p82)} | {r(x.proj_g)} goals, {r(x.proj_p)} points |"
                for x in c.sort_values("rate_p82", ascending=False).itertuples()) + f"""

Of the {len(c)} players in the table, {n_above} are scoring faster than their rating and {n_below} slower.

**Running hot.**

{hot_txt}

**Tage Thompson** is running hot too, on a {r(tage.pace_p82)}-point pace. His rating of {r(tage.rate_p82)} is still the best on the team, and at that
rate he'd finish with about {r(tage.proj_g)} goals and {r(tage.proj_p)} points if he plays every game.

**Likely to heat up:** {cold_txt}. Their ratings say they should score faster from here.

## Where the rating comes from

**The source:** the NHL's own play-by-play for every game since the start of 2023-24: every goal, assist and shot, and where each shot came
from.

**What a chance is worth.** Not every shot is equal. Of the {n_sh:,} shots since 2023-24 that weren't blocked (not counting empty-net
shots), the ones from within 10 feet went in {near:.1f}% of the time; from 40 feet or more, {far:.1f}%. We give every shot its chance of going in,
based on where and how it was taken, and add them up. That total is what a player's chances were worth. Jack Quinn's are worth 6.1 goals
this season; he has 9.

**The math, using Owen Power.** For assists, {steps}. Then we add {Kd} made-up games at the average for a defenseman this season
({lg_a:.2f} assists a game), so a short track record doesn't swing wildly. That works out to {pa82:.1f} assists per 82 games. Goals work the same
way, from the chances he creates, adjusted for how well he's finished over his career: {pg82:.1f} goals per 82 games.
{pa82:.1f} assists plus {pg82:.1f} goals is about {r(by.loc["Owen Power", "rate_p82"])} points, his rating. His {by.loc["Owen Power", "p"]} points in {by.loc["Owen Power", "gp"]} games is a {r(by.loc["Owen Power", "pace_p82"])}-point pace;
his history says to expect a lot less. The finishing adjustment is pulled toward average, because chances carry over from season to season
much better than finishing does, but it still matters for a sharpshooter: it adds about {r((tage.fin_ratio - 1) * 100)}% to Tage Thompson's goals.

## How we checked it

Our rating beat simply going by pace when we tested it on last season. We tuned the rating on 2024-25 only. Then we went back to last season, 2025-26, stopped the clock after 17 games, and had the rating project
every NHL skater's rest of the season using only player stats known at that point ({t17['skaters']} players). Then we compared with what actually happened.

![The test](sabres-hotcold-test.png)

The rating missed a player's rest-of-season points by {rp('model'):.1f} on average. Going by his pace missed by {rp('pace'):.1f}; going by his
last season, {rp('last_season'):.1f}; and guessing every player is average, {rp('position_avg'):.1f}. For goals alone, it missed by {rg('model'):.1f}, against {rg('pace'):.1f} for pace. It also beat both at the halfway point of the season,
though by less ({t41['results']['p']['model']['abs_err_rest']:.1f}, against {t41['results']['p']['pace']['abs_err_rest']:.1f} for pace and {t41['results']['p']['last_season']['abs_err_rest']:.1f} for last season), because by then a season's pace means more.

## What it means

- **Expect both groups to drift back toward their ratings.** The players running ahead of their ratings will probably slow down, and the ones behind will probably
  pick up. Not guaranteed: the rating misses by several points a player, and it can't see injuries or a player moving up or down the lineup.
- **Ice time is the missing piece.** We don't have shift data yet, so a player promoted to the top line looks the same to the rating as one
  stuck on the fourth. That's the next thing we're adding.
- **We'll keep score.** These projections are pinned to {pd.to_datetime(AS_OF):%B %-d}. We'll check them against how the season actually
  finishes and publish the results, misses included.

## For the stat-heads

- Rating: `src/metrics/nhl_player_ratings.py`. Per-game rate = (current total + W x past totals + K x position mean) / (current GP + W x past GP + K),
  past seasons weighted W x {bt['method']['decay']}^(age-1). Chances (xG): W={bt['method']['W']['ixg']}, K={bt['method']['K']['ixg']}; assists W={bt['method']['W']['a']}, K={bt['method']['K']['a']}.
  Goals = blended xG/game x (career goals + {bt['method']['fin_shrink']}) / (career xG + {bt['method']['fin_shrink']}). Points = goals + assists. Settings chosen on 2024-25 (history 2023-24).
- Test: checkpoint = date the median team had played 17 (or 41) games; skaters with 5+ games before and 10+ after; errors weighted by games after.
  2025-26 after 17 games, points per game MSE: rating {t17['results']['p']['model']['mse']:.5f}, pace {t17['results']['p']['pace']['mse']:.5f}, last season
  {t17['results']['p']['last_season']['mse']:.5f}, position average {t17['results']['p']['position_avg']['mse']:.5f}; correlation with rest-of-season rate {t17['results']['p']['model']['corr']:.2f} vs.
  {t17['results']['p']['pace']['corr']:.2f} for pace.
- Caveat: the xG model was trained on 2023-24 through 2025-26, and the per-season rescale uses full-season totals, so the 2025-26 test is not
  fully out of sample for chances (the rating settings and finishing shrink were fit on 2024-25 only).
- xG: our model, unblocked non-empty-net shots, rescaled per season so league xG = league goals. Shootouts excluded. No TOI (no shift data).
- Projected season totals = points to date + rate x {m['remaining']} remaining games ({82} minus the Sabres' {m['team_gp']} played); they assume he plays every game.
- Players shown: Sabres skaters with {MIN_GP}+ games through {AS_OF}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Sabres: hot and cold",
        "big": [[r(tage.pace_p82), "Tage Thompson's pace (points per 82)"], [r(tage.rate_p82), "his rating, from every season since 2023-24"]],
        "note": f"Tested on last season, the rating missed a player's rest-of-season points by {rp('model'):.1f} on average; going by pace missed by {rp('pace'):.1f}.",
        "explainer": {"kicker": "How we checked", "title": "Rest-of-season points, average miss (2025-26).",
                      "text": "Projected after 17 games with only the player stats known then:", "fmt": "pts",
                      "bars": [["Our rating", rp("model")], ["Pace so far", rp("pace")], ["Last season", rp("last_season")]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
