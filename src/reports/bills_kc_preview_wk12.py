"""Bills vs. Chiefs preview (Thursday, Nov. 26, 2026, 8:20 p.m. ET): the two Ledger calls logged Nov. 25 and where they come from.

- Win chance: points model (points-win-v0.1), the same functions src/ledger/log_bills_kc_wk12.py used to log P0024.
- Allen 4+ runs: his 2026 games (15+ plays), designed runs plus scrambles, no kneel-downs (P0025).
- Weather: National Weather Service forecast captured Thursday (reports/weather/2026-11-26-orchard-park-nws-2026-11-26T1457Z.json),
  and part 4's rain finding, imported from its generator's saved story (not recomputed here).

Writes reports/2026-wk12-kc-preview.md, one PNG (bills-kc-wk12-preview.png) and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger import points_model as pm
from src.ledger.log_bills_kc_wk12 import ALLEN_PFR, GAME, THRU, allen_call, win_call
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.wk11_postgame import finish, ordn

OUT = ROOT / "reports"
SLUG = "2026-wk12-kc-preview"
PNG = "bills-kc-wk12-preview.png"
FORECAST = OUT / "weather" / "2026-11-26-orchard-park-nws-2026-11-26T1457Z.json"
CALLS = ("P0024", "P0025")
PBP26_FINGERPRINT = (28141, -186.8888)       # 2026 weeks 1-11, after the Nov. 25 nflverse re-post


def main():
    fp = query(f"SELECT COUNT(*) n, ROUND(SUM(epa), 4) s FROM raw_pbp WHERE season = 2026 AND season_type = 'REG' AND week <= {THRU} AND epa IS NOT NULL").iloc[0]
    assert (int(fp.n), float(fp.s)) == PBP26_FINGERPRINT, f"2026 play-by-play changed: {tuple(fp)}"

    # ---- the logged calls (read from the Ledger, then recomputed and matched)
    led = pd.read_csv(ROOT / "ledger" / "predictions.csv").set_index("id")
    p_log, r_log = float(led.loc["P0024", "probability"]), float(led.loc["P0025", "probability"])
    logged_at = led.loc["P0024", "created_at_utc"]
    lt = pd.Timestamp(logged_at).tz_convert("America/New_York")
    logged_et = f"{lt.strftime('%A')} at {lt.strftime('%-I:%M %p').replace('AM', 'a.m.').replace('PM', 'p.m.')} Eastern"
    assert logged_et == "Wednesday at 9:44 a.m. Eastern"
    p_win, pb, pk = win_call()
    p_run, n_g, k_g = allen_call()
    assert round(p_win, 2) == p_log == 0.55 and round(p_run, 2) == r_log == 0.80 and (round(pb, 1), round(pk, 1)) == (25.6, 23.9)

    # how good is the scoring model: average miss per team per game in seasons it never trained on
    _, _, te, summ = pm.backtest(test={2024: 99, 2025: 99, 2026: THRU})
    miss_model, miss_lg = float(summ.model.mean()), float(summ.league.mean())
    within7 = float((summ.within7 * summ.n).sum() / summ.n.sum())
    g, home_rate = pm.backtest_win(test={2024: 99, 2025: 99, 2026: THRU})
    brier = float(((g.p - g.won) ** 2).mean())
    fav_right = float(((g.p > 0.5) == (g.won == 1)).loc[g.won != 0.5].mean())
    n_games = int((g.won != 0.5).sum())
    assert miss_model < miss_lg and brier < 0.25 and (len(g), n_games) == (659, 657)

    # ---- Allen's runs, game by game
    allen = query(f"SELECT DISTINCT gsis_id FROM raw_rosters_weekly WHERE pfr_id = '{ALLEN_PFR}'").gsis_id.iloc[0]
    r = query(f"""SELECT p.week, p.defteam opp,
                  SUM(CASE WHEN p.rush = 1 AND p.rusher_player_id = '{allen}' THEN 1 ELSE 0 END)
                  + SUM(CASE WHEN p.qb_scramble = 1 AND COALESCE(p.rusher_player_id, p.passer_player_id) = '{allen}' THEN 1 ELSE 0 END) runs,
                  SUM(CASE WHEN p.qb_scramble = 1 AND COALESCE(p.rusher_player_id, p.passer_player_id) = '{allen}' THEN 1 ELSE 0 END) scr,
                  SUM(CASE WHEN COALESCE(p.passer_player_id, p.rusher_player_id) = '{allen}' THEN 1 ELSE 0 END) plays
                  FROM raw_pbp p WHERE p.season = 2026 AND p.week <= {THRU} AND p.season_type = 'REG' AND p.posteam = 'BUF'
                  AND p.play_type <> 'no_play' AND COALESCE(p.qb_kneel, 0) = 0 AND COALESCE(p.two_point_attempt, 0) = 0
                  GROUP BY 1, 2 HAVING plays >= 15 ORDER BY 1""")
    assert len(r) == n_g and int((r.runs >= 4).sum()) == k_g
    low = r[r.runs < 4]
    med_runs = float(r.runs.median())

    # ---- weather: Thursday's forecast and part 4's numbers (from the published story's hero)
    fc = json.loads(FORECAST.read_text())
    t = [h[1] for h in fc["hourly_et"]]
    w = [int(h[2].split()[0]) for h in fc["hourly_et"]]
    pop = [h[4] for h in fc["hourly_et"]]
    dirs = {"NE": "northeast", "E": "east", "N": "north", "SE": "southeast"}
    dset = list(dict.fromkeys(h[3] for h in fc["hourly_et"]))
    dtxt = " to ".join(dirs[d] for d in dset)
    assert dset == ["NE", "E"]
    gusts = [x[1] for x in fc["gust_mph_utc"] if x[0] >= "2026-11-27T01"]       # 8 p.m. ET onward
    rain = fc["rain_in_7pm_to_1am_et"]
    assert (min(t), max(t), min(w), max(w), min(pop), min(gusts), max(gusts), rain) == (37, 38, 10, 13, 88, 29, 35, 0.66)
    p4 = json.loads((OUT / "2026-wk12-kc-weather.hero.json").read_text())
    p4_rain_pts, p4_usual = p4["big"][0][0], p4["big"][1][0]
    assert (p4_rain_pts, p4_usual) == (18.3, 22.9)

    # ---- chart: Allen's runs by game, with the 4-run line
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=200)
    cols = [BLUE if x >= 4 else GRAY for x in r.runs]
    ax.bar(range(len(r)), r.runs, 0.62, color=cols, zorder=2)
    ax.bar(range(len(r)), r.scr, 0.62, color="white", alpha=0.35, hatch="///", edgecolor="white", zorder=3)
    ax.axhline(4, color=RED, lw=1.5, ls="--", zorder=4)
    ax.text(len(r) - 0.4, 4.15, "4 runs", color=RED, fontsize=9.5, ha="right", fontweight="bold")
    for i, v in enumerate(r.runs):
        ax.text(i, v + 0.15, str(int(v)), ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.set_xticks(range(len(r)), [f"Wk {wk}\n{o}" for wk, o in zip(r.week, r.opp)], fontsize=8.5)
    ax.set_ylabel("Allen runs (designed runs + scrambles)")
    ax.set_ylim(0, max(r.runs) + 1.5)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.8)
    finish(fig, f"Josh Allen has run 4+ times in {k_g} of {n_g} games this season",
           "Each bar is one 2026 game. Striped part: scrambles. Kneel-downs not counted.", "x")
    fig.texts[-1].set_text(f"Source: nflverse play-by-play, 2026 weeks 1-{THRU}. Games where Allen had 15+ plays.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    lowtxt = " and ".join(f"Week {int(x.week)} against {x.opp} ({int(x.runs)})" for x in low.itertuples())
    md = f"""# Bills vs. Chiefs: we give Buffalo {p_win:.0%}, and Josh Allen {p_run:.0%} to run at least 4 times

**Two calls on the Ledger for Thursday night, logged Wednesday morning: the Bills beat the Chiefs ({p_win:.0%}), and Josh Allen runs the ball 4 or more
times ({p_run:.0%}). Our scoring model has Buffalo by about {pb - pk:.0f} point{"s" if round(pb - pk) != 1 else ""} at home, {pb:.1f} to {pk:.1f}. Allen has run at least 4 times in {k_g} of his
{n_g} games. And the forecast has gotten wetter: rain all game, with gusts up to {max(gusts)} mph.**

![Josh Allen has run 4+ times in {k_g} of {n_g} games this season]({PNG})

## Call 1: Bills win, {p_win:.0%}

The model projects each team's points from how many points its offense scores per drive this season and how many the other team's defense gives up,
blended with last season's numbers, plus home field. Buffalo projects to {pb:.1f} and Kansas City to {pk:.1f}. To turn that into a win chance, we replay how far real games have landed from the
model's projections. A gap of under two points leaves plenty of room for either team, which is why it's {p_win:.0%}.

**How good is it?** In seasons it never saw (2024, 2025 and 2026 so far), its projections missed a team's actual score by {miss_model:.1f} points on
average, against {miss_lg:.1f} for just guessing the league average. It landed within 7 points {within7:.0%} of the time. The team it gave the better chance won
{fav_right:.0%} of the {n_games} games that didn't end in a tie.

## Call 2: Allen runs 4+ times, {p_run:.0%}

This one is simple: the share of Allen's games this season with 4 or more runs, counting designed runs and scrambles but not kneel-downs. He did it
in {k_g} of {n_g}. Ten games is a small sample. The two times he didn't: {lowtxt}. His typical game this season has {med_runs:.0f} runs. It's a plain season rate, not a model, and
the Ledger says so.

Will the rain change it? [Part 4](bills-chiefs-rain-and-wind.html) found NFL teams run more in the rain, but that counted designed runs by everyone,
mostly running backs, and no scrambles. It doesn't tell us about quarterbacks, so the {p_run:.0%} leaves the weather out.

## The weather, updated

Thursday morning's National Weather Service forecast for Orchard Park, from 8 to 11 p.m.: rain ({min(pop)}-{max(pop)}% chance each hour), {min(t)}-{max(t)} degrees,
a {dtxt} wind of {min(w)}-{max(w)} mph with gusts of {min(gusts)}-{max(gusts)} mph, and about {rain:.2f} of an inch of rain from 7 p.m. to 1 a.m. That's wetter
than Wednesday's forecast in part 4. In games with rain and a 10+ mph wind since 2018, each team scored {p4_rain_pts} points on average, against the {p4_usual} we'd expect from the same offenses
and defenses in dry games.
The model above doesn't know about the weather; it projects a normal game.

## Catch up on Chiefs week

- [Part 1: Greg Rousseau leads the NFL in pressures, but the sacks lag](bills-chiefs-leonhard-file.html)
- [Part 2: who's left from the last playoff meeting](bills-chiefs-whos-left.html)
- [Part 3: how to slow down Patrick Mahomes](bills-chiefs-slowing-mahomes.html)
- [Part 4: rain, wind and the run game](bills-chiefs-rain-and-wind.html)

## Receipts

Both calls were logged {logged_et}, before kickoff, and we'll grade them Friday. Win or lose, they stay on the [Ledger](../ledger.html).

## For the stat-heads

- Win: points-win-v0.1 (src/ledger/points_model.py), drive-level ratings through 2026 Week {THRU}, home = BUF. Projections {pb:.2f} / {pk:.2f}. Win chance = share
  of paired training misses (home, away) replayed on the projections in which BUF finishes ahead; ties after regulation split 50/50.
- Out-of-sample: mean absolute error {miss_model:.2f} vs {miss_lg:.2f} (league-average guess); within 7 points {within7:.1%}; win Brier {brier:.3f} on {len(g)} games, ties scored as half
  (50/50 guess = 0.250); the side given more than 50% won {fav_right:.1%} of the {n_games} games without a tie.
- Allen runs: play-by-play `rush` with Allen as rusher plus `qb_scramble`; excludes kneels, two-point tries and no-plays; games with 15+ Allen plays. Per game: {", ".join(str(int(x)) for x in r.runs)}.
- Ledger timestamps: P0024 and P0025 logged {logged_at} UTC.
- 2026 play-by-play fingerprint {PBP26_FINGERPRINT}. Weather: NWS gridpoint BUF/39,42, updated {fc["updateTime"]}; saved in reports/weather/.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Bills vs. Chiefs, Thursday",
        "big": [[f"{p_win:.0%}", "Bills win (logged on the Ledger)"], [f"{p_run:.0%}", "Josh Allen runs 4+ times"]],
        "note": f"Model: Buffalo {pb:.1f}, Kansas City {pk:.1f}. Forecast: rain all game, gusts to {max(gusts)} mph.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
