"""Week 9, part 3: our prediction for Bills at Vikings (MNF, Nov. 9, 2026).

Writes reports/2026-wk09-prediction.md, three PNGs and a homepage hero JSON. Every number is computed here.
Data pinned through 2026 week 8 (THRU), the same inputs as parts 1 and 2, so reruns reproduce the published story.
Only calls whose model passed an out-of-sample test are listed for the Ledger; the logger is src/ledger/log_wk09_part3.py.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT
from src.ledger import points_model as pm
from src.ledger.model_v01 import VERSION as V01, prob_over, qb_relative
from src.ledger.model_v01_backtest import run as v01_run, summary as v01_summary
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 8  # pinned: games through 2026 week 8
GAME = "2026_09_BUF_MIN"
WENTZ = "00-0032950"  # Carson Wentz starts; Kyler Murray out (hamstring)
SLUG = "2026-wk09-prediction"
WIN_VERSION = "points-win-v0.1"
SRC = "Source: nflverse play-by-play and schedules. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def per100(v):
    v = round(v * 100)
    return "0" if v == 0 else f"{v:+d}"


def points_block():
    """Both teams' projections, the win chance, and the tests behind them."""
    coef, res, te, summ = pm.backtest(test={2024: 99, 2025: 99, SEASON: THRU})
    g = pm._drives()
    o_r, d_r, lg, pace, lg_pace = pm.ratings(g, SEASON, THRU + 1)
    raw_b, ppd_b, drv = pm.raw_prediction(o_r, d_r, lg, pace, lg_pace, "BUF", "MIN")
    raw_m, ppd_m, _ = pm.raw_prediction(o_r, d_r, lg, pace, lg_pace, "MIN", "BUF")
    proj = {"BUF": pm.predict(coef, raw_b, 0), "MIN": pm.predict(coef, raw_m, 1)}
    rng = {t: proj[t] + np.quantile(res, [0.1, 0.9]) for t in proj}
    p20 = {t: pm.prob_at_least(proj[t], 20, res) for t in proj}
    cur = g[(g.season == SEASON) & (g.week <= THRU)]
    raw = dict(buf_off=cur[cur.posteam == "BUF"].pts.sum() / cur[cur.posteam == "BUF"].n.sum(),
               buf_off_n=int(cur[cur.posteam == "BUF"].n.sum()),
               min_def=cur[cur.defteam == "MIN"].pts.sum() / cur[cur.defteam == "MIN"].n.sum(),
               min_def_n=int(cur[cur.defteam == "MIN"].n.sum()))
    oo = cur.groupby("posteam").pts.sum() / cur.groupby("posteam").n.sum()
    dd = cur.groupby("defteam").pts.sum() / cur.groupby("defteam").n.sum()
    ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
    rk = dict(off=f"{ordn(int((oo > oo['BUF']).sum()) + 1)} of {len(oo)}", def_=None)
    rk["def"] = f"{ordn(int((dd < dd['MIN']).sum()) + 1)} of {len(dd)} (1st = fewest allowed)"
    _, pairs = pm.paired_misses()
    p_min = pm.win_chance(proj["MIN"], proj["BUF"], pairs)
    # win test on the same blind games
    wg, home_rate = pm.backtest_win(test={2024: 99, 2025: 99, SEASON: THRU})
    brier = lambda p: float(((p - wg.won) ** 2).mean())
    fav = wg.p.where(wg.p >= 0.5, 1 - wg.p)
    fav_won = np.where(wg.p >= 0.5, wg.won, 1 - wg.won)
    cal = pd.DataFrame({"fav": fav, "won": fav_won})
    cal["b"] = pd.cut(cal.fav, [0.5, 0.6, 0.7, 1.0], include_lowest=True)
    cal = cal.groupby("b", observed=True).agg(n=("won", "size"), said=("fav", "mean"), happened=("won", "mean"))
    wt = dict(n=len(wg), brier=brier(wg.p), brier_half=brier(pd.Series(0.5, index=wg.index)),
              brier_home=brier(pd.Series(home_rate, index=wg.index)), home_rate=home_rate,
              right=float(((wg.p > 0.5) & (wg.won == 1) | (wg.p < 0.5) & (wg.won == 0)).mean()),
              home_won=float((wg.won == 1).mean()), cal=cal, n_pairs=len(pairs),
              corr=float(np.corrcoef(pairs.T)[0, 1]))
    tot = summ.n.sum()
    mae = dict(model=(summ.model * summ.n).sum() / tot, league=(summ.league * summ.n).sum() / tot,
               team=(summ.team_ppg * summ.n).sum() / tot, n=int(tot))
    return dict(off_m=o_r["MIN"], def_b=d_r["BUF"], rk=rk, coef=coef, proj=proj, rng=rng, p20=p20, p_buf=1 - p_min, ppd_b=ppd_b, ppd_m=ppd_m, drv=drv, lg=lg,
                off_b=o_r["BUF"], def_m=d_r["MIN"], raw=raw, wt=wt, mae=mae)


def matchup_calls():
    """Model v0.1 calls for both offenses, with the out-of-sample test for each call type."""
    w_db, n_db = qb_relative(WENTZ, "dropback_epa", [2025, SEASON], max_week=THRU)
    w_sk, _ = qb_relative(WENTZ, "sack_rate", [2025, SEASON], max_week=THRU)
    c = dict(min_db=prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=w_db, max_week=THRU),
             min_ru=prob_over("MIN", "BUF", "rush_epa", 0.0, max_week=THRU),
             min_sk=prob_over("MIN", "BUF", "sack_rate", 0.06, off_override=w_sk, max_week=THRU),
             buf_db=prob_over("BUF", "MIN", "dropback_epa", 0.0, max_week=THRU),
             buf_ru=prob_over("BUF", "MIN", "rush_epa", 0.0, max_week=THRU))
    tests = {m: v01_summary(v01_run(m, t)) for m, t in (("dropback_epa", 0.0), ("rush_epa", 0.0), ("sack_rate", 0.06))}
    return c, tests, n_db


def ledger_status():
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[(lp.game_id == GAME) & lp.model_version.isin([pm.VERSION, WIN_VERSION, V01, V01 + "+qb"])] if not lp.empty else lp
    if len(lp):
        return (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.max()} UTC, before kickoff.** All {len(lp)} calls "
                "are graded after the game, hit or miss, and stay up either way.")
    return ("**These are our model's numbers.** They count once they're logged on the [Ledger](../ledger.html) before kickoff; "
            "every logged call is graded after the game, hit or miss.")


def main():
    P = points_block()
    C, T, n_db = matchup_calls()
    pb, pmn = P["proj"]["BUF"], P["proj"]["MIN"]
    wt, mae = P["wt"], P["mae"]
    calls = [  # (plain-English call, our chance, which model, test key)
        ("Bills win (overtime counts; a tie counts as a miss)", P["p_buf"], "Points model, win chance", "win"),
        ("Bills score 20 or more points", P["p20"]["BUF"], "Points model", "pts"),
        ("Vikings score 20 or more points (from part 1)", P["p20"]["MIN"], "Points model", "pts"),
        ("Bills' pass plays gain points overall", C["buf_db"]["p"], "Matchup model", "dropback_epa"),
        ("Vikings' pass plays gain points overall, with Wentz", C["min_db"]["p"], "Matchup model", "dropback_epa"),
        ("Bills' runs lose points overall", 1 - C["buf_ru"]["p"], "Matchup model", "rush_epa"),
        ("Vikings' runs lose points overall", 1 - C["min_ru"]["p"], "Matchup model", "rush_epa"),
    ]
    sk = T["sack_rate"][0]; db = T["dropback_epa"][0]; ru = T["rush_epa"][0]
    ru_cal = T["rush_epa"][1]
    ru_hi = ru_cal.iloc[-2:]  # the two top buckets (55%+ that runs gain points)
    ru_lo = ru_cal.iloc[0]; ru_mid = ru_cal.iloc[1]
    sk_hi = T["sack_rate"][1].iloc[-2:]
    sk_hi_said = (sk_hi.said * sk_hi.n).sum() / sk_hi.n.sum(); sk_hi_hap = (sk_hi.happened * sk_hi.n).sum() / sk_hi.n.sum()

    # ---- chart 1: projected score with 80% ranges
    fig, ax = plt.subplots(figsize=(9.5, 3.9), dpi=200)
    rows = [("Bills", pb, P["rng"]["BUF"], BLUE), ("Vikings", pmn, P["rng"]["MIN"], GRAY)]
    for y, (lab, v, (lo, hi), col) in zip([1, 0], rows):
        ax.plot([lo, hi], [y, y], color=col, lw=10, alpha=0.28, solid_capstyle="round", zorder=1)
        ax.scatter([v], [y], s=170, color=col, zorder=3, edgecolor="white", linewidth=2)
        ax.text(v, y + 0.27, f"{v:.0f}", ha="center", fontsize=13, fontweight="bold", color=INK)
        ax.text(hi + 0.6, y, f"likely {lo:.0f}-{hi:.0f}", va="center", fontsize=9.5, color=MUTED)
    ax.set_yticks([1, 0], ["Bills", "Vikings"], fontsize=11)
    ax.set_ylim(-0.6, 1.7); ax.set_xlim(0, 46)
    ax.set_xlabel("Points", fontsize=10, color=MUTED)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Our projection: Bills {pb:.0f}, Vikings {pmn:.0f}. Bills win {P['p_buf']:.0%} of the time",
           "Dot = projected points. Shaded bar = where the score lands 8 times in 10.",
           f"Points model {pm.VERSION}: 2026 drives through week {THRU}, home field for Minnesota. Tested on {mae['n']:,} team-games from 2024-26 it never saw.")
    fig.savefig(OUT / "wk09c-score.png"); plt.close(fig)

    # ---- chart 2: the calls (homepage hero)
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
    ys = np.arange(len(calls))[::-1]
    for y, (lab, p, _, _) in zip(ys, calls):
        col = BLUE if lab.startswith("Bills") else GRAY
        ax.barh(y, p, 0.6, color=col, zorder=2)
        ax.text(p + 0.01, y, f"{p:.0%}", va="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.text(0.5, len(calls) - 0.35, "50/50", ha="center", fontsize=8.5, color=MUTED)
    ax.set_yticks(ys, [c[0] for c in calls], fontsize=10)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Seven calls for Monday night",
           "Our chance that each one happens. Every one comes from a kind of model we tested on past games before trusting it.",
           f"Points model {pm.VERSION}; matchup model {V01}. Data through 2026 week {THRU}. Logged on the Ledger before kickoff.")
    fig.savefig(OUT / "wk09c-calls.png"); plt.close(fig)

    # ---- chart 3: win-chance test, said vs happened
    cal = wt["cal"]
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    x = np.arange(len(cal)); w = 0.36
    ax.bar(x - w / 2, cal.said, w, color=GRAY, label="Chance we gave the favorite", zorder=2)
    ax.bar(x + w / 2, cal.happened, w, color=BLUE, label="How often the favorite won", zorder=2)
    for i, r in enumerate(cal.itertuples()):
        ax.text(i - w / 2, r.said + 0.015, f"{r.said:.0%}", ha="center", fontsize=9.5, color=MUTED)
        ax.text(i + w / 2, r.happened + 0.015, f"{r.happened:.0%}", ha="center", fontsize=9.5, color=INK)
    labs = ["Close calls\n(50-60%)", "Leans\n(60-70%)", "Clear favorites\n(70%+)"]
    ax.set_xticks(x, [f"{l}\n{int(n)} games" for l, n in zip(labs, cal.n)], fontsize=9.5)
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"When our model says {cal.said.iloc[1]:.0%}, the favorite wins about {cal.happened.iloc[1]:.0%} of the time",
           f"Win chances on {wt['n']} games from 2024-26 the model never saw, grouped by how strongly it leaned.",
           f"Model built on 2019-23 games. 2026 games through week {THRU}. Ties count as half a win.")
    fig.savefig(OUT / "wk09c-win-test.png"); plt.close(fig)

    table = "\n".join(f"| {lab} | **{p:.0%}** | {m} |" for lab, p, m, _ in calls)
    md = f"""# Bills at Vikings: our prediction for Monday night

**Finding: Our model sees a coin flip with a small Buffalo edge. It projects the Bills to score about {pb:.0f} points and the Vikings
about {pmn:.0f}, and gives Buffalo a {P['p_buf']:.0%} chance to win. Strength meets strength on the Bills' side of the ball,
and the model splits the difference: Buffalo's offense has been the best in football, Minnesota's defense the best at
stopping it. On the other side, a below-average Vikings offense ({P['off_m']:.2f} points per drive after our adjustment; league {P['lg']:.2f})
meets a below-average Bills defense ({P['def_b']:.2f} allowed). We're putting seven calls on the [Ledger](../ledger.html), every one from
a kind of model we tested on past games first (one adjustment, swapping in Wentz's numbers, is untested; details below). One call we planned to make, on sacks, failed its test, so it's out.**

*Bills at Vikings, Monday Night Football, Nov. 9, 8:15 p.m. ET, U.S. Bank Stadium (indoors). This is part 3 of our week 9 preview.
[Part 1](wentz-vs-bills-defense.html) covered Carson Wentz against the Bills defense; [part 2](bills-offense-vs-vikings-defense.html)
covered Josh Allen and the Bills offense against Minnesota's defense. Numbers are 2026 through week {THRU}, the same as both parts.*

![Projected score](wk09c-score.png)

## The calls

| Call | Our chance | Where it comes from |
|---|---|---|
{table}

![The calls](wk09c-calls.png)

"Gain points" and "lose points" mean what part 1 and part 2 explained: every play moves a drive closer to points or further
away, and we add it up over the night. A team's runs "lose points" if, all added together, its running plays left it worse off
than when they started. That happens a lot: in the {ru['n']} past team-games we tested on (2023-2025), a team's runs lost points overall {1 - ru['rate']:.0%} of the time.
So {1 - C['buf_ru']['p']:.0%} for the Bills is about the usual rate, a shade better; the Vikings' {1 - C['min_ru']['p']:.0%} is well above it.

{ledger_status()}

## How many points will Buffalo score?

**Our projection: about {pb:.0f} points**, most likely between {P['rng']['BUF'][0]:.0f} and {P['rng']['BUF'][1]:.0f} (8 times in 10), with a
**{P['p20']['BUF']:.0%} chance of 20 or more.** It's the same model, and the same math, that gave Minnesota about {pmn:.0f} in part 1.

**Where the number comes from.** Points come from drives, so we start there. This season the Bills' offense has scored
{P['raw']['buf_off']:.2f} points per drive ({P['raw']['buf_off_n']} drives), {P['rk']['off']} in the league; the league average is {P['lg']:.2f}.
Minnesota's defense has allowed {P['raw']['min_def']:.2f} per drive ({P['raw']['min_def_n']} drives), {P['rk']['def']}. Seven games is a small
sample, so we pull both numbers part of the way back toward last season and the league average: Buffalo's offense counts as
{P['off_b']:.2f} and Minnesota's defense as {P['def_m']:.2f}.

**The math:** start from the league's {P['lg']:.2f} points per drive. Buffalo's offense is {P['off_b'] - P['lg']:.2f} better than average, so add that;
Minnesota's defense is {P['lg'] - P['def_m']:.2f} better than average, so take that off. That leaves about {P['ppd_b']:.2f} points per drive (numbers are rounded).
Multiply by the {P['drv']:.1f} drives a team gets in a typical Bills or Vikings game, and you get {P['ppd_b'] * P['drv']:.0f}. The same final
step as in part 1, fit on past games, turns that into a real score. Buffalo is on the road, so it doesn't get the home-field bump of
about {P['coef'][2]:.1f} points that Minnesota does. That's how we get to {pb:.0f}.

That's why the best-on-best matchup from part 2 nets out close to average: the model treats a great offense against a great defense
as mostly cancelling out. Part 2 found the same thing in past games: when a top-3 offense met a top-3 defense, the result landed
close to simply adding the two strengths together.

## Who wins?

**Our model gives the Bills a {P['p_buf']:.0%} chance and the Vikings {1 - P['p_buf']:.0%}.** With the two teams projected less than a point
apart, that's close to even.

**Where it comes from.** A projection is never exactly right, so we ask how wrong it tends to be. We took the {wt['n_pairs']:,} games
from 2019-2023 the model was built on, and for each one wrote down how far each team's real score landed from its projection.
Then we replay those {wt['n_pairs']:,} pairs of misses on top of Monday's two projections, as if this game were played {wt['n_pairs']:,} times. The
Bills finish ahead in {P['p_buf']:.0%} of them (a game level after regulation counts as half for each side, since overtime is close to a coin flip). On the Ledger, a game that ends
in a tie counts as a miss for this call. Keeping each game's two misses
together keeps any link between them; in practice there's almost none (how far one team misses says almost nothing about the other).

## How we checked it

**The win chance.** Before using it, we had the model give a win chance for every game from week 2 on in 2024, 2025 and 2026 (2026 through week {THRU}),
{wt['n']} games it had never seen, using only what was known before kickoff. The team it favored won {wt['right']:.0%} of the time.
Just taking the home team every time would have been right {wt['home_won']:.0%} of the time. And its percentages mean what they say:

![Win chance test](wk09c-win-test.png)

When it called a game close (50-60%), the favorite won {cal.happened.iloc[0]:.0%} of the time. When it leaned 60-70%, {cal.happened.iloc[1]:.0%}.
Our miss score (explained under "For the stat-heads") was {wt['brier']:.3f}, better than a 50/50 guess on every game ({wt['brier_half']:.3f}) and better than
giving the home team its usual {wt['home_rate']:.0%} ({wt['brier_home']:.3f}). Lower is better.

**The points.** The points model was tested the same way in part 1: an average miss of {mae['model']:.1f} points on {mae['n']:,} team-games
it never saw, better than guessing the league average ({mae['league']:.1f}) or each team's own average ({mae['team']:.1f}).

**The matchup calls.** The pass and run calls come from a separate, simpler model: it takes what each offense has done this season,
what each defense has allowed, and how much a team's games normally swing around its average. We tested every kind of call before using it on
{db['n']} past team-games (2023-2025, week 8 on, using only earlier games), and compared it with just using the league's usual rate:

| Kind of call | Our model's miss score | League rate's | Verdict |
|---|---|---|---|
| Pass plays gain points | {db['brier']:.3f} | {db['brier_base']:.3f} | Better; its percentages held up in the range where Monday's calls sit |
| Runs gain or lose points | {ru['brier']:.3f} | {ru['brier_base']:.3f} | A little better |
| Sacks on more than 6% of dropbacks | {sk['brier']:.3f} | {sk['brier_base']:.3f} | **Worse. Dropped.** |

**Why the sack call is out.** We planned to say there was a {C['min_sk']['p']:.0%} chance the Bills sack Wentz on more than 6% of his dropbacks.
But this kind of call did worse than just using the league's usual rate. When it was confident (above 55%), it said {sk_hi_said:.0%} on average and
it happened {sk_hi_hap:.0%} of the time. Sacks in a single game swing too much for this model to read, so we're not calling them.

**A caution on the run calls.** The run model is honest in the range where Monday's calls sit: when it said runs would gain points
{ru_lo.said:.0%} of the time, they did {ru_lo.happened:.0%} (Minnesota's call), and when it said {ru_mid.said:.0%}, they did {ru_mid.happened:.0%} (Buffalo's).
It gets too confident when it says runs will *gain* points (above 55% it said {(ru_hi.said * ru_hi.n).sum() / ru_hi.n.sum():.0%} and they
happened {(ru_hi.happened * ru_hi.n).sum() / ru_hi.n.sum():.0%}, on only {int(ru_hi.n.sum())} games). Neither of Monday's run calls is in that range.

## What the models don't know

- **Wentz.** The points model doesn't know Minnesota changed quarterbacks; its numbers come mostly from Kyler Murray's games and last season's. The
  Vikings' pass call does swap in Wentz's own numbers (2025 and 2026, {n_db} dropbacks), but that swap wasn't part of the test above.
- **Injuries.** Both Bills starting tackles were on this week's injury report (ClutchPoints, Nov. 5). None of our models know who plays; check the final report
  before kickoff.
- **One game is one game.** A {P['p_buf']:.0%} chance means the Bills lose this one about half the time. That's the point of the Ledger: one call
  doesn't prove anything, but a season of graded calls does.

## For the stat-heads

- Points model {pm.VERSION} (`src/ledger/points_model.py`): ratings = (points + {pm.K} x prior) / (drives + {pm.K}), prior = league + {pm.PRIOR_KEEP} x last
  season's gap; raw = (league + off gap + def gap) x average pace; calibrated score = {P['coef'][0]:.2f} + {P['coef'][1]:.3f} x raw + {P['coef'][2]:.2f} x home,
  fit on 2019-23. Ranges and 20+ chances use the empirical training residuals.
- Win chance ({WIN_VERSION}): {wt['n_pairs']:,} same-game (home miss, away miss) residual pairs from training, added to Monday's two projections;
  ties within half a point split 50/50. Residual correlation {wt['corr']:.3f}. Out of sample (2024-26, n={wt['n']}): Brier {wt['brier']:.4f} vs {wt['brier_half']:.4f}
  (50/50) and {wt['brier_home']:.4f} (training home-win rate {wt['home_rate']:.3f}). "Miss score" in the story is the Brier score: the average squared gap between
  the chance we gave and what happened (1 or 0); tied test games count as 0.5 there and in the chart, and as misses in "the team it favored won".
- Matchup model {V01} (`src/ledger/model_v01.py`): expected = league + 0.5 x (offense gap + defense gap), plus the pooled within-team game-to-game
  spread; P = share of that spread above the threshold. Metrics: EPA per dropback (with scrambles and sacks), EPA per designed rush.
  Bills dropback EPA expected {C['buf_db']['expected']:+.3f} (offense {C['buf_db']['off_mean']:+.3f}, Vikings defense {C['buf_db']['def_mean']:+.3f}, league {C['buf_db']['league']:+.3f});
  Vikings dropback {C['min_db']['expected']:+.3f} with Wentz's relative value; rush: Bills {C['buf_ru']['expected']:+.3f}, Vikings {C['min_ru']['expected']:+.3f}.
- Matchup backtest: `scripts/backtest_model_v01.py`, 2023-25 weeks 8+, n={db['n']} per call type, baseline = league share over the threshold in prior weeks
  of that season. Sack-rate > 6%: Brier {sk['brier']:.4f} vs {sk['brier_base']:.4f}.
- Data pinned through 2026 week {THRU}. No betting lines are used anywhere in these models.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Our projection for Monday night",
        "big": [[round(pb), "Bills, projected points"], [round(pmn), "Vikings, projected points"]],
        "note": f"Bills win {P['p_buf']:.0%} of the time in our model. Seven calls go on the Ledger before kickoff; one planned call failed its test and is out.",
        "explainer": {
            "kicker": "How we checked it", "title": "Tested on games it never saw.",
            "text": (f"Before trusting the win chance, we ran it on {wt['n']} games from 2024-26 the model had never seen. "
                     "How often the team it favored won, vs. always taking the home team:"),
            "bars": [["Our model", round(wt["right"], 3)], ["Home team", round(wt["home_won"], 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
