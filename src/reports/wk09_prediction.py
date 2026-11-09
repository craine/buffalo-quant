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
    return dict(res=res, off_m=o_r["MIN"], def_b=d_r["BUF"], rk=rk, coef=coef, proj=proj, rng=rng, p20=p20, p_buf=1 - p_min, ppd_b=ppd_b, ppd_m=ppd_m, drv=drv, lg=lg,
                off_b=o_r["BUF"], def_m=d_r["MIN"], raw=raw, wt=wt, mae=mae)


LADDER = [10, 14, 17, 20, 24, 27, 30, 35]



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

    # ---- ladder: chance each team reaches each scoreline, plus the test behind it
    res = P["res"]
    lad = {t: (pm.prob_at_least(pb, t, res), pm.prob_at_least(pmn, t, res)) for t in LADDER}
    n_ahead = sum(round(b * 100) > round(m * 100) for b, m in lad.values())
    n_level = sum(round(b * 100) == round(m * 100) for b, m in lad.values())
    miss50, miss80 = np.quantile(np.abs(res), [0.5, 0.8])
    lt = pm.build_frame([2024, 2025, SEASON], max_week={2024: 99, 2025: 99, SEASON: THRU})
    lt["model"] = pm.predict(P["coef"], lt.raw, lt.home)
    lc = pd.DataFrame([(pm.prob_at_least(m, t, res), y >= t) for m, y in zip(lt.model, lt.score) for t in LADDER], columns=["p", "y"])
    lc["t"] = [t for _ in range(len(lt)) for t in LADDER]
    l20 = lc[lc.t == 20]
    lc["b"] = pd.cut(lc.p, [0, .2, .4, .6, .8, 1], include_lowest=True)
    lc = lc.groupby("b", observed=True).agg(n=("y", "size"), said=("p", "mean"), happened=("y", "mean"))
    g26 = pm._drives(); c26 = g26[(g26.season == SEASON) & (g26.week <= THRU)]
    oo26 = c26.groupby("posteam").pts.sum() / c26.groupby("posteam").n.sum()
    k = int((oo26 > P["ppd_b"]).sum()) + 1
    ppd_rank = f"about {k}{'th' if 10 <= k % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')} of {len(oo26)}"
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    x = np.arange(len(LADDER)); w = 0.38
    ax.bar(x - w / 2, [lad[t][0] for t in LADDER], w, color=BLUE, label="Bills", zorder=2)
    ax.bar(x + w / 2, [lad[t][1] for t in LADDER], w, color=GRAY, label="Vikings", zorder=2)
    for i, t in enumerate(LADDER):
        ax.text(i - w / 2, lad[t][0] + 0.015, f"{lad[t][0]:.0%}", ha="center", fontsize=9, color=INK, fontweight="bold")
        ax.text(i + w / 2, lad[t][1] + 0.015, f"{lad[t][1]:.0%}", ha="center", fontsize=9, color=MUTED)
    ax.set_xticks(x, [f"{t}+" for t in LADDER], fontsize=10.5)
    ax.set_xlabel("Points scored Monday", fontsize=10, color=MUTED)
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    xi = LADDER.index(20) + (pb - 20) / (24 - 20)  # projection placed between the 20+ and 24+ groups
    ax.plot([xi, xi], [lad[24][0] + 0.06, 1.0], color=INK, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(xi + 0.06, 0.97, f"Our projection:\nBills {pb:.1f}, Vikings {pmn:.1f}", fontsize=8.5, color=INK, va="top")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "At nearly every scoreline, the Bills are a step ahead",
           f"Our chance each team scores at least this many points. Bills win {P['p_buf']:.0%} of the time.",
           f"Points model {pm.VERSION}: 2026 drives through week {THRU}, home field for Minnesota. Tested on {mae['n']:,} team-games from 2024-26 it never saw.")
    fig.savefig(OUT / "wk09c-ladder.png"); plt.close(fig)

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
    closest = min(calls, key=lambda c: abs(c[1] - 0.5)); surest = max(calls, key=lambda c: abs(c[1] - 0.5))
    finish(fig, f"Closest: who wins ({closest[1]:.0%}). Surest: Vikings' runs lose points ({surest[1]:.0%})",
           "Our chance that each one happens. Every one comes from a kind of model we tested on past games before trusting it.",
           f"Points model {pm.VERSION}; matchup model {V01}. Data through 2026 week {THRU}. Logged on the Ledger before kickoff.")
    fig.savefig(OUT / "wk09c-calls.png"); plt.close(fig)

    # ---- chart 3: win-chance test, said vs happened
    cal = wt["cal"]
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    x = np.arange(len(cal)); w = 0.36
    ax.bar(x - w / 2, cal.said, w, color=GRAY, label="Chance we gave the team we leaned to", zorder=2)
    ax.bar(x + w / 2, cal.happened, w, color=BLUE, label="How often that team won", zorder=2)
    for i, r in enumerate(cal.itertuples()):
        ax.text(i - w / 2, r.said + 0.015, f"{r.said:.0%}", ha="center", fontsize=9.5, color=MUTED)
        ax.text(i + w / 2, r.happened + 0.015, f"{r.happened:.0%}", ha="center", fontsize=9.5, color=INK)
    labs = ["Close calls\n(50-60%)", "Leans\n(60-70%)", "Clear favorites\n(70%+)"]
    ax.set_xticks(x, [f"{l}\n{int(n)} games" for l, n in zip(labs, cal.n)], fontsize=9.5)
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"In close calls like Monday's, we said {cal.said.iloc[0]:.0%} and the team we leaned to won {cal.happened.iloc[0]:.0%}",
           f"Win chances on {wt['n']} games from 2024-26 the model never saw, grouped by how strongly it leaned.",
           f"Model built on 2019-23 games. 2026 games through week {THRU}. Ties count as half a win.")
    fig.savefig(OUT / "wk09c-win-test.png"); plt.close(fig)

    table = "\n".join(f"| {lab} | **{p:.0%}** | {m} |" for lab, p, m, _ in calls)
    gaps = [100 * (lad[t][0] - lad[t][1]) for t in LADDER if round(lad[t][0] * 100) > round(lad[t][1] * 100)]
    level_rungs = [t for t in LADDER if round(lad[t][0] * 100) == round(lad[t][1] * 100)]
    level_txt = (f"every rung except {level_rungs[0]} points, where the edge is under one point ({lad[level_rungs[0]][0]:.0%} each, rounded)" if len(level_rungs) == 1
                 else "every rung" if not level_rungs else f"{n_ahead} of the {len(LADDER)} rungs")
    ladder_rows = "\n".join(f"| {t} or more | **{lad[t][0]:.0%}** | {lad[t][1]:.0%} |" for t in LADDER)
    md = f"""# Bills at Vikings: our prediction for Monday night

**Finding: Pick almost any score, and the Bills are a little more likely than the Vikings to get there: {lad[17][0]:.0%} to {lad[17][1]:.0%} to reach
17 points, {lad[24][0]:.0%} to {lad[24][1]:.0%} to reach 24. It's never a big edge, but it's there nearly everywhere, and the same edge gives the Bills a {P['p_buf']:.0%} chance
to win. It all traces to one small gap: we project Buffalo {pb:.1f} points, Minnesota {pmn:.1f}.**

*Bills at Vikings, Monday Night Football, Nov. 9, 8:15 p.m. ET, U.S. Bank Stadium (indoors). Part 3 of our week 9 preview.
[Part 1](wentz-vs-bills-defense.html) covered Carson Wentz against the Bills defense; [part 2](bills-offense-vs-vikings-defense.html)
covered Josh Allen against Minnesota's defense. Numbers are 2026 through week {THRU}.*

![Chance each team reaches each scoreline](wk09c-ladder.png)

## The scoreboard ladder

Picture a ladder of scorelines: 10 points, 14, 17, 20 and up. For each rung, here's our chance that each team climbs at least that high Monday:

| Points | Bills | Vikings |
|---|---|---|
{ladder_rows}

Read it like this: there's a {lad[17][0]:.0%} chance the Bills score 17 or more, and a {lad[17][1]:.0%} chance the Vikings do. The Bills are ahead by
{min(gaps):.0f} to {max(gaps):.0f} percentage points on {level_txt}. That's this game in one table: no big edge anywhere, a small one almost everywhere.

## How a 23-point game becomes 53%

Nobody scores exactly what we project. So we looked at {len(res):,} past team scores from 2019-2023 and asked how far off we were. Half the time, a team
landed within about {miss50:.0f} points of our number. Eight times in ten, within about {miss80:.0f}. (Those are the games the model was built on; on games it
had never seen, its average miss was {mae['model']:.1f} points.)

Then we play Monday's game over and over, once for every one of those past misses, on top of today's projections. In some replays the Bills
score a lot; in others they're held down. Eight times in ten they land between {P['rng']['BUF'][0]:.0f} and {P['rng']['BUF'][1]:.0f}. Count how often the Bills reach 20
or more in all those replays and you get {lad[20][0]:.0%}. Count 24 or more and it's {lad[24][0]:.0%}, just under half, because {pb:.1f} is right in the middle.
That's what our {pb:.1f} really is: the middle of a wide range, not a guess at the final score. And it's why a {pb - pmn:.1f}-point edge only gets the Bills
to {P['p_buf']:.0%}. When a typical miss is {miss50:.0f} points either way, {pb - pmn:.1f} is a nudge, not a shove.

**Who wins?** Same idea, both teams at once. We took {wt['n_pairs']:,} real past games and noted how far off we were for each team in that same game.
Then we applied each pair of misses to Monday's projections and checked who came out ahead. Buffalo did in {P['p_buf']:.0%} of them. (A game tied after
60 minutes counts as half for each side, since overtime is close to a coin flip.)

So why not call it a tie? Because the model doesn't: {pb:.1f} beats {pmn:.1f}, and that's what tips it to {P['p_buf']:.0%}. Both projections are written into
our Ledger entries before kickoff.

## The calls going on the Ledger

| Call | Our chance | Where it comes from |
|---|---|---|
{table}

![The calls](wk09c-calls.png)

What "gain points" and "lose points" mean: these aren't scoreboard points. Every play moves a drive closer to scoring or further away, and we add
that up over the night. A team's runs "lose points" if, all told, its running plays left it worse off than before. That's normal: in the {ru['n']} past
team games we tested on (2023-2025), a team's runs lost points overall {1 - ru['rate']:.0%} of the time. So {1 - C['buf_ru']['p']:.0%} for the Bills is about the usual
rate, a shade better; the Vikings' {1 - C['min_ru']['p']:.0%} is well above it.

{ledger_status()}

## Where the 23 comes from: the NFL's best offense meets its best defense, and they cancel out

The most interesting matchup of the night, the best offense against the best defense, mostly cancels itself out. Part 2 found that's
usually what happens: when a top-3 offense meets a top-3 defense, the result lands close to adding the two together.

Points come from drives, so that's where we start. Four steps:

1. **How good is each side?** This season the Bills average {P['raw']['buf_off']:.2f} points per drive, the most in the NFL
   ({P['rk']['off']}). Minnesota's defense gives up just {P['raw']['min_def']:.2f} per drive, the fewest. An average offense scores {P['lg']:.2f} per drive.
2. **Don't overreact to seven games.** A hot start isn't a guarantee, so we mix in last season and an average team.
   That makes the Bills' offense {P['off_b']:.2f} and the Vikings' defense {P['def_m']:.2f}: still far better than average, just less extreme.
3. **Let them meet.** The Bills' offense is {P['off_b'] - P['lg']:.2f} points per drive better than average. Minnesota's defense is
   {P['lg'] - P['def_m']:.2f} better than average. Those almost cancel out, leaving about {P['ppd_b']:.2f} points per drive: a bit better than an average
   offense, which would rank {ppd_rank} this season.
4. **Count the drives and check against history.** About {P['drv']:.0f} drives a game gets you to about {P['ppd_b'] * P['drv']:.0f}. A final check against past games
   pulls extreme projections back toward normal and gives the home team about {P['coef'][2]:.1f} points. Buffalo is on the road, so it lands at **{pb:.1f}**.

Minnesota goes through the same four steps from the other direction: a below-average offense ({P['off_m']:.2f} per drive) against a below-average
Bills defense ({P['def_b']:.2f} allowed), plus the home bump. That's **{pmn:.1f}**.

## Did we check it? Yes, before trusting it

**The scoreline chances.** We ran the model on {mae['n']:,} team games from 2024-2026 that it had never seen. At the extremes it was right on: when
it gave a team a 20% chance or less, it said {lc.said.iloc[0]:.0%} on average and it happened {lc.happened.iloc[0]:.0%}; at 80% or more, it said {lc.said.iloc[4]:.0%} and it
happened {lc.happened.iloc[4]:.0%}. In the middle it ran a few points low, including right at the 20-point line (it said {l20.p.mean():.0%}, teams got there
{l20.y.mean():.0%}). Real scores bunch up on 17, 20 and 24, and our model smooths that out. So both teams' 20-or-more chances are probably a few points
low. We're logging them as they are and will fix this before using these lines again.

**The win chance.** On {wt['n']} unseen games (week 2 on, 2024-2026), the team our model leaned to won {wt['right']:.0%} of the time. Taking the
home team every time would have been right {wt['home_won']:.0%} of the time.

![Win chance test](wk09c-win-test.png)

*The chart counts a tied game as half a win; the {wt['right']:.0%} above counts it as a miss.*

**The pass and run calls.** These come from a simpler model, tested on {db['n']} past team games (2023-2025) against just guessing the league's usual
rate. It beat the guess on pass calls and edged it on run calls. On one kind of call it lost, so we threw that call out.

**The call we threw out.** We were going to say there was a {C['min_sk']['p']:.0%} chance the Bills sack Wentz on more than 6% of his dropbacks.
But when this kind of call was confident, it said {sk_hi_said:.0%} and was right {sk_hi_hap:.0%} of the time: worse than just guessing the usual rate.
Sacks in one game swing too much to call, so we're not.

## What the model doesn't know

- **Wentz.** The points model doesn't know Minnesota switched quarterbacks; its numbers come mostly from Kyler Murray's games and last season's.
  The Vikings' pass call does use Wentz's own numbers ({n_db} dropbacks over 2025 and 2026), but that swap is the one piece we haven't tested.
- **Injuries.** Both Bills starting tackles were on this week's injury report (ClutchPoints, Nov. 5). Our models don't know who plays.
- **One game is one game.** {P['p_buf']:.0%} means the Bills lose this about half the time. One call proves nothing; a season of graded calls does.
  That's why everything goes on the Ledger.

## For the stat-heads

- Matchup-call backtest grades (Brier score, lower is better), {db['n']} team games per call type: pass plays gain points {db['brier']:.3f} vs {db['brier_base']:.3f}
  for the league rate (calibrated in the range of Monday's calls); runs {ru['brier']:.3f} vs {ru['brier_base']:.3f}; sacks on 6%+ of dropbacks {sk['brier']:.3f} vs
  {sk['brier_base']:.3f} (dropped).
- Run-model caution: above 55% that runs gain points it said {(ru_hi.said * ru_hi.n).sum() / ru_hi.n.sum():.0%} and it happened {(ru_hi.happened * ru_hi.n).sum() / ru_hi.n.sum():.0%}
  (n={int(ru_hi.n.sum())}). Monday's run calls sit in buckets where it said {ru_lo.said:.0%} / {ru_mid.said:.0%} and it happened {ru_lo.happened:.0%} / {ru_mid.happened:.0%}.
- Points model {pm.VERSION} (`src/ledger/points_model.py`): ratings = (points + {pm.K} x prior) / (drives + {pm.K}), prior = league + {pm.PRIOR_KEEP} x last
  season's gap; raw = (league + off gap + def gap) x average pace; calibrated score = {P['coef'][0]:.2f} + {P['coef'][1]:.3f} x raw + {P['coef'][2]:.2f} x home,
  fit on 2019-23 (week 2 on). Ladder chances = share of the {len(res):,} empirical training residuals that put the projection at or above each line.
  Ladder calibration out of sample, all {len(LADDER)} lines pooled: """ + "; ".join(
        f"said {r.said:.0%} / happened {r.happened:.0%} (n={int(r.n):,})" for r in lc.itertuples()) + f""".
- Win chance ({WIN_VERSION}): {wt['n_pairs']:,} same-game (home miss, away miss) residual pairs from training, added to Monday's two projections;
  margins within half a point split 50/50. Residual correlation {wt['corr']:.3f}. Out of sample (2024-26, week 2 on, n={wt['n']}): Brier {wt['brier']:.4f} vs {wt['brier_half']:.4f}
  (50/50) and {wt['brier_home']:.4f} (training home-win rate {wt['home_rate']:.3f}). The "grade" in the story is the Brier score: the average squared gap between
  the chance we gave and what happened (1 or 0); tied test games count as 0.5 there and in the chart, and as misses in "the team it favored won".
- Matchup model {V01} (`src/ledger/model_v01.py`): expected = league + 0.5 x (offense gap + defense gap), plus the pooled within-team game-to-game
  spread; P = share of that spread above the threshold. EPA per dropback (with scrambles and sacks), EPA per designed rush.
  Bills dropback EPA expected {C['buf_db']['expected']:+.3f} (offense {C['buf_db']['off_mean']:+.3f}, Vikings defense {C['buf_db']['def_mean']:+.3f}, league {C['buf_db']['league']:+.3f});
  Vikings dropback {C['min_db']['expected']:+.3f} with Wentz's relative value; rush: Bills {C['buf_ru']['expected']:+.3f}, Vikings {C['min_ru']['expected']:+.3f}.
- Matchup backtest: `scripts/backtest_model_v01.py`, 2023-25 weeks 8+, n={db['n']} per call type, baseline = league share over the threshold in prior weeks
  of that season. Sack rate > 6%: Brier {sk['brier']:.4f} vs {sk['brier_base']:.4f}.
- Data pinned through 2026 week {THRU}. No betting lines are used anywhere in these models.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Our projection for Monday night",
        "big": [[round(pb), "Bills, projected points"], [round(pmn), "Vikings, projected points"]],
        "note": f"At nearly every scoreline Buffalo is a step ahead: {lad[20][0]:.0%} vs {lad[20][1]:.0%} to reach 20. Bills win {P['p_buf']:.0%} of the time. Projection: Bills {pb:.1f}, Vikings {pmn:.1f}.",
        "explainer": {
            "kicker": "How we checked it", "title": "Tested on games it never saw.",
            "text": (f"Before trusting the win chance, we ran it on {wt['n']} games from 2024-26 the model had never seen. "
                     "How often the team it leaned to won, vs. always taking the home team:"),
            "bars": [["Our model", round(wt["right"], 3)], ["Home team", round(wt["home_won"], 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
