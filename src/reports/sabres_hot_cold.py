"""Sabres: who's running hot, who's due. Pinned to AS_OF; every number comes from the skater cards (src/reports/skater_cards.py)
and the player-rating back-test (src/metrics/nhl_player_ratings.py -> reports/cards/player_model_backtest.json).

Writes reports/2026-11-11-sabres-hot-cold.md, two PNGs and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT
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
    rp = lambda k: t17["results"]["p"][k]["abs_err_rest"]
    rg = lambda k: t17["results"]["g"][k]["abs_err_rest"]

    # ---- chart 1: pace vs. rating, every Sabre with MIN_GP+ games
    fig, ax = plt.subplots(figsize=(9.5, 0.42 * len(c) + 1.6), dpi=200)
    ys = np.arange(len(c))
    for y, r in zip(ys, c.itertuples()):
        ax.plot([r.rate_p82, r.pace_p82], [y, y], color="#C9CDD4", lw=3, zorder=1)
    ax.scatter(c.pace_p82, ys, s=60, color=[RED if g > 0 else GRAY for g in c.gap], zorder=3, label="This season's pace")
    ax.scatter(c.rate_p82, ys, s=70, color=BLUE, zorder=4, label="Our rating")
    ax.set_yticks(ys, c.name, fontsize=10)
    ax.set_xlabel("Points per 82 games")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9.5, loc="lower right")
    finish(fig, "Pace vs. history: who's running hot and who's due",
           f"Every Sabres skater with {MIN_GP}+ games. Red dot: pace above his rating; gray: below. Blue: our rating.",
           f"Games through {pd.to_datetime(AS_OF):%b. %-d}. Rating blends every season since 2023-24.")
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
           f"Every NHL skater's rest of 2025-26, projected after 17 games with only what was known then ({t17['skaters']} skaters).",
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
        return (f"Most of it is assists: {x.a} so far. Assists swing a lot over a few weeks, because they depend on "
                "teammates finishing.")
    hot_txt = "\n\n".join(f"**{x.name}** is on pace for {r(x.pace_p82)} points per 82 games; his rating says {r(x.rate_p82)}. {why_hot(x)}"
                          for x in hot3.itertuples())
    cold_txt = "; ".join(f"{x.name}, on pace for {r(x.pace_p82)} with a rating of {r(x.rate_p82)}" for x in cold.itertuples())
    lead = (f"**Owen Power, Jack Quinn and Zach Benson are the Sabres running furthest ahead of their history, and Tage Thompson's {r(tage.pace_p82)}-point pace is "
            f"also ahead of his history, though his rating, {r(tage.rate_p82)} points per 82 games, is still the best on the team. At the other end, "
            f"{names(cold)} are furthest behind. Our rating, built from every season since 2023-24, projected last season's players "
            f"better than going by their pace.**") if list(hot3.name) == ["Owen Power", "Jack Quinn", "Zach Benson"] else None
    assert lead, f"lead names the wrong players: {list(hot3.name)}"
    md = f"""# Sabres: who's running hot, and who's due

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

{n_above} of these {len(c)} Sabres are running ahead of their rating and {n_below} behind.

**Running hot.**

{hot_txt}

**Tage Thompson** is on pace for {r(tage.pace_p82)}; his rating says {r(tage.rate_p82)}. That would still be a big season: about {r(tage.proj_g)} goals and
{r(tage.proj_p)} points if he plays every game.

**Due for more:** {cold_txt}. Their ratings say more is coming.

## Where the rating comes from

**The source:** the NHL's own play-by-play for every game since the start of 2023-24: every goal, assist and shot, and where each shot came
from. **The math:** for each player we add up his points this season, plus his points from past seasons counted at half weight (and the season
before that at a quarter), plus a few games of an average player at his position, and divide by the games. That way a hot month can't take
over, but a player who's been good for years keeps his history. Goals come from the chances a player creates, adjusted slightly for how well
he's finished his chances over the years, because the chances carry over from season to season much better than the finishing does.

## How we checked it

We set the rating up using 2024-25 only. Then we went back to last season, 2025-26, stopped the clock after 17 games, and had the rating project
every NHL skater's rest of the season using only what was known at that point ({t17['skaters']} players). Then we compared with what actually happened.

![The test](sabres-hotcold-test.png)

The rating's projection of a player's rest-of-season points missed by {rp('model'):.1f} on average. Going by his pace missed by {rp('pace'):.1f}; going by his
last season, {rp('last_season'):.1f}. For goals alone, it missed by {rg('model'):.1f}, against {rg('pace'):.1f} for pace. It also beat both at the halfway point of the season,
though by less ({t41['results']['p']['model']['abs_err_rest']:.1f}, against {t41['results']['p']['pace']['abs_err_rest']:.1f} for pace and {t41['results']['p']['last_season']['abs_err_rest']:.1f} for last season), because by then a season's pace means more.

## What it means

- **Expect both groups to drift back toward their ratings.** The players running ahead of their ratings will probably slow down, and the ones behind will probably
  pick up. Not guaranteed: the rating misses by several points a player, and it can't see injuries or a player moving up or down the lineup.
- **Ice time is the missing piece.** We don't have shift data yet, so a player promoted to the top line looks the same to the rating as one
  stuck on the fourth. That's the next thing we're adding.
- **We'll keep score.** These projections are pinned to {pd.to_datetime(AS_OF):%B %-d}. We'll check them against the rest of the season,
  the same way we grade every call on the [Ledger](../ledger.html).

## For the stat-heads

- Rating: `src/metrics/nhl_player_ratings.py`. Per-game rate = (current total + W x past totals + K x position mean) / (current GP + W x past GP + K),
  past seasons weighted W x {bt['method']['decay']}^(age-1). Chances (xG): W={bt['method']['W']['ixg']}, K={bt['method']['K']['ixg']}; assists W={bt['method']['W']['a']}, K={bt['method']['K']['a']}.
  Goals = blended xG/game x (career goals + {bt['method']['fin_shrink']}) / (career xG + {bt['method']['fin_shrink']}). Points = goals + assists. Settings chosen on 2024-25 (history 2023-24).
- Test: checkpoint = date the median team had played 17 (or 41) games; skaters with 5+ games before and 10+ after; errors weighted by games after.
  2025-26 after 17 games, points per game MSE: rating {t17['results']['p']['model']['mse']:.5f}, pace {t17['results']['p']['pace']['mse']:.5f}, last season
  {t17['results']['p']['last_season']['mse']:.5f}, position average {t17['results']['p']['position_avg']['mse']:.5f}; correlation with rest-of-season rate {t17['results']['p']['model']['corr']:.2f} vs.
  {t17['results']['p']['pace']['corr']:.2f} for pace.
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
                      "text": "Projected after 17 games with only what was known then:", "fmt": "pts",
                      "bars": [["Our rating", rp("model")], ["Pace so far", rp("pace")], ["Last season", rp("last_season")]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
