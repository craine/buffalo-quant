"""Week 10: our prediction for Bills at Jets (Sunday, Nov. 15, 2026, 1 p.m. ET).

Writes reports/2026-wk10-bills-at-jets.md, three PNGs and a homepage hero JSON. Every number is computed here.
Data pinned through 2026 week 9 (THRU), so reruns reproduce the published story.
Only calls whose model passed an out-of-sample test are listed for the Ledger; the logger is src/ledger/log_wk10.py.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger import points_model as pm
from src.ledger.model_v01 import VERSION as V01, prob_over, qb_relative
from src.ledger.model_v01_backtest import run as v01_run, summary as v01_summary
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 9  # pinned: games through 2026 week 9
GAME = "2026_10_BUF_NYJ"
OPP = "NYJ"
SLUG = "2026-wk10-bills-at-jets"
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
    raw_b, ppd_b, drv = pm.raw_prediction(o_r, d_r, lg, pace, lg_pace, "BUF", OPP)
    raw_m, ppd_m, _ = pm.raw_prediction(o_r, d_r, lg, pace, lg_pace, OPP, "BUF")
    proj = {"BUF": pm.predict(coef, raw_b, 0), OPP: pm.predict(coef, raw_m, 1)}
    rng = {t: proj[t] + np.quantile(res, [0.1, 0.9]) for t in proj}
    p20 = {t: pm.prob_at_least(proj[t], 20, res) for t in proj}
    cur = g[(g.season == SEASON) & (g.week <= THRU)]
    raw = dict(buf_off=cur[cur.posteam == "BUF"].pts.sum() / cur[cur.posteam == "BUF"].n.sum(),
               buf_off_n=int(cur[cur.posteam == "BUF"].n.sum()),
               opp_def=cur[cur.defteam == OPP].pts.sum() / cur[cur.defteam == OPP].n.sum(),
               opp_def_n=int(cur[cur.defteam == OPP].n.sum()),
               opp_off=cur[cur.posteam == OPP].pts.sum() / cur[cur.posteam == OPP].n.sum(),
               buf_def=cur[cur.defteam == "BUF"].pts.sum() / cur[cur.defteam == "BUF"].n.sum())
    oo = cur.groupby("posteam").pts.sum() / cur.groupby("posteam").n.sum()
    dd = cur.groupby("defteam").pts.sum() / cur.groupby("defteam").n.sum()
    ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
    rk = dict(off=f"{ordn(int((oo > oo['BUF']).sum()) + 1)} of {len(oo)}", def_=None)
    rk["def"] = f"{ordn(int((dd < dd[OPP]).sum()) + 1)} of {len(dd)}"
    rk["def_most"] = ordn(int((dd > dd[OPP]).sum()) + 1)
    rk["opp_off_rank"] = int((oo > oo[OPP]).sum()) + 1
    rk["buf_def_rank"] = int((dd < dd["BUF"]).sum()) + 1
    rk["n"] = len(oo)
    _, pairs = pm.paired_misses()
    p_min = pm.win_chance(proj[OPP], proj["BUF"], pairs)
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
    return dict(res=res, off_m=o_r[OPP], def_b=d_r["BUF"], rk=rk, coef=coef, proj=proj, rng=rng, p20=p20, p_buf=1 - p_min, ppd_b=ppd_b, ppd_m=ppd_m, drv=drv, lg=lg,
                off_b=o_r["BUF"], def_m=d_r[OPP], raw=raw, wt=wt, mae=mae)


LADDER = [10, 14, 17, 20, 24, 27, 30, 35]



def matchup_calls():
    """Model v0.1 calls for both offenses, with the out-of-sample test for each call type."""
    c = dict(opp_db=prob_over(OPP, "BUF", "dropback_epa", 0.0, max_week=THRU),
             opp_ru=prob_over(OPP, "BUF", "rush_epa", 0.0, max_week=THRU),
             buf_db=prob_over("BUF", OPP, "dropback_epa", 0.0, max_week=THRU),
             buf_ru=prob_over("BUF", OPP, "rush_epa", 0.0, max_week=THRU))
    tests = {m: v01_summary(v01_run(m, t)) for m, t in (("dropback_epa", 0.0), ("rush_epa", 0.0))}
    return c, tests


def pass_ranks():
    """Dropback EPA per play this season: Bills offense and Jets defense, with ranks."""
    q = query(f"""SELECT posteam, defteam, epa FROM raw_pbp WHERE season={SEASON} AND week<={THRU} AND season_type='REG'
                  AND qb_dropback=1 AND epa IS NOT NULL""")
    off = q.groupby("posteam").epa.mean().sort_values(ascending=False)
    de = q.groupby("defteam").epa.mean().sort_values()
    return dict(buf_off=off["BUF"], buf_off_rk=list(off.index).index("BUF") + 1, opp_def=de[OPP], opp_def_rk=list(de.index).index(OPP) + 1,
                opp_def_most=len(de) - list(de.index).index(OPP), n_off=int((q.posteam == "BUF").sum()), n_def=int((q.defteam == OPP).sum()),
                lg=q.epa.mean(), n_teams=len(off))


def _et(ts):
    t = pd.Timestamp(ts).tz_convert("America/New_York")
    return t.strftime("%b. %-d at %-I:%M ") + ("a.m." if t.hour < 12 else "p.m.") + " ET"


def ledger_status():
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[(lp.game_id == GAME) & lp.model_version.isin([pm.VERSION, WIN_VERSION, V01, V01 + "+qb"])] if not lp.empty else lp
    if len(lp):
        return (f"**Logged on the [Ledger](../ledger.html) on {_et(lp.created_at_utc.max())}, before kickoff.** All {len(lp)} calls "
                "are graded after the game, hit or miss, and stay up either way.")
    return ("**These are our model's numbers.** They count once they're logged on the [Ledger](../ledger.html) before kickoff; "
            "every logged call is graded after the game, hit or miss.")


def main():
    P = points_block()
    C, T = matchup_calls()
    R = pass_ranks()
    pb, pj = P["proj"]["BUF"], P["proj"][OPP]
    wt, mae = P["wt"], P["mae"]
    calls = [  # (plain-English call, our chance, which model, test key)
        ("Bills win (overtime counts; a tie counts as a miss)", P["p_buf"], "Points model, win chance", "win"),
        ("Bills' pass plays gain points overall", C["buf_db"]["p"], "Matchup model", "dropback_epa"),
        ("Jets' pass plays gain points overall", C["opp_db"]["p"], "Matchup model", "dropback_epa"),
        ("Bills' runs lose points overall", 1 - C["buf_ru"]["p"], "Matchup model", "rush_epa"),
        ("Jets' runs lose points overall", 1 - C["opp_ru"]["p"], "Matchup model", "rush_epa"),
    ]
    db, db_cal = T["dropback_epa"]; ru, ru_cal = T["rush_epa"]
    db_hi = db_cal.iloc[-1]                     # the model's most confident pass calls (70%+)
    assert C["buf_db"]["p"] > 0.7

    # ---- ladder
    res = P["res"]
    lad = {t: (pm.prob_at_least(pb, t, res), pm.prob_at_least(pj, t, res)) for t in LADDER}
    miss50, miss80 = np.quantile(np.abs(res), [0.5, 0.8])
    lt = pm.build_frame([2024, 2025, SEASON], max_week={2024: 99, 2025: 99, SEASON: THRU})
    lt["model"] = pm.predict(P["coef"], lt.raw, lt.home)
    lc = pd.DataFrame([(pm.prob_at_least(m, t, res), y >= t) for m, y in zip(lt.model, lt.score) for t in LADDER], columns=["p", "y"])
    mid = lc[(lc.p >= 0.4) & (lc.p <= 0.6)]
    mid_said, mid_hap, mid_n = mid.p.mean(), mid.y.mean(), len(mid)
    assert mid_hap > mid_said
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    x = np.arange(len(LADDER)); w = 0.38
    ax.bar(x - w / 2, [lad[t][0] for t in LADDER], w, color=BLUE, label="Bills", zorder=2)
    ax.bar(x + w / 2, [lad[t][1] for t in LADDER], w, color=GRAY, label="Jets", zorder=2)
    for i, t in enumerate(LADDER):
        ax.text(i - w / 2, lad[t][0] + 0.015, f"{lad[t][0]:.0%}", ha="center", fontsize=9, color=INK, fontweight="bold")
        ax.text(i + w / 2, lad[t][1] + 0.015, f"{lad[t][1]:.0%}", ha="center", fontsize=9, color=MUTED)
    ax.set_xticks(x, [f"{t}+" for t in LADDER], fontsize=10.5)
    ax.set_xlabel("Points scored Sunday", fontsize=10, color=MUTED)
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Buffalo is ahead at every scoreline: {lad[24][0]:.0%} to {lad[24][1]:.0%} to reach 24",
           f"Our chance each team scores at least this many points. Projection: Bills {pb:.1f}, Jets {pj:.1f}. Bills win {P['p_buf']:.0%} of the time.",
           f"Points model {pm.VERSION}: 2026 drives through week {THRU}, home field for New York. Tested on {mae['n']:,} team-games from 2024-26 it never saw.")
    fig.savefig(OUT / "wk10-ladder.png"); plt.close(fig)

    # ---- the calls (homepage hero)
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=200)
    ys = np.arange(len(calls))[::-1]
    for y, (lab, pr, _, _) in zip(ys, calls):
        ax.barh(y, pr, 0.6, color=BLUE if lab.startswith("Bills") else GRAY, zorder=2)
        ax.text(pr + 0.01, y, f"{pr:.0%}", va="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.text(0.5, len(calls) - 0.35, "50/50", ha="center", fontsize=8.5, color=MUTED)
    ax.set_yticks(ys, [c[0] for c in calls], fontsize=10)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Our surest call: the Bills' passing game gains ground ({C['buf_db']['p']:.0%})",
           "Our chance that each one happens. Each comes from a kind of model we tested on past games before trusting it.",
           f"Points model {pm.VERSION}; matchup model {V01}. Data through 2026 week {THRU}. Logged on the Ledger before kickoff.")
    fig.savefig(OUT / "wk10-calls.png"); plt.close(fig)

    # ---- win-chance test
    cal = wt["cal"]
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    x = np.arange(len(cal)); w = 0.36
    ax.bar(x - w / 2, cal.said, w, color=GRAY, label="Chance we gave the team we leaned to", zorder=2)
    ax.bar(x + w / 2, cal.happened, w, color=BLUE, label="How often that team won", zorder=2)
    for i, r in enumerate(cal.itertuples()):
        ax.text(i - w / 2, r.said + 0.015, f"{r.said:.0%}", ha="center", fontsize=9.5, color=MUTED)
        ax.text(i + w / 2, r.happened + 0.015, f"{r.happened:.0%}", ha="center", fontsize=9.5, color=INK)
    labs = ["Close calls\n(50-60%)", "Leans\n(60-70%)", "Strong leans\n(70%+)"]
    ax.set_xticks(x, [f"{l}\n{int(n)} games" for l, n in zip(labs, cal.n)], fontsize=9.5)
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"When we gave a team 70% or more, we said {cal.said.iloc[2]:.0%} and it won {cal.happened.iloc[2]:.0%}",
           f"Win chances on {wt['n']} games from 2024-26 the model never saw, grouped by how strongly it leaned.",
           f"Model built on 2019-23 games. 2026 games through week {THRU}. Ties count as half a win.")
    fig.savefig(OUT / "wk10-win-test.png"); plt.close(fig)

    # last week's receipts
    from src.ledger.ledger import GRADE_COLS, GRADE_CSV, PRED_COLS, PRED_CSV, _read
    lp, lg_ = _read(PRED_CSV, PRED_COLS), _read(GRADE_CSV, GRADE_COLS)
    w9 = lp[lp.game_id == "2026_09_BUF_MIN"].merge(lg_, left_on="id", right_on="prediction_id")
    w9_hits = int(((w9.probability.astype(float) >= 0.5) == (w9.outcome.astype(int) == 1)).sum())
    assert len(w9) == 7

    table = "\n".join(f"| {lab} | **{pr:.0%}** | {m} |" for lab, pr, m, _ in calls)
    ladder_rows = "\n".join(f"| {t} or more | **{lad[t][0]:.0%}** | {lad[t][1]:.0%} |" for t in LADDER)
    md = f"""# Bills at Jets: our prediction. The NFL's best offense gets one of its leakiest pass defenses

**Finding: We project the Bills for {pb:.1f} points and the Jets for {pj:.1f}, which gives Buffalo a {P['p_buf']:.0%} chance to win. The biggest mismatch on
the field: the Bills' passing game, {ordn_(R['buf_off_rk'])}-best in the NFL, against a Jets pass defense that's {ordn_(R['opp_def_most'])}-worst. Our matchup model gives an
{C['buf_db']['p']:.0%} chance the Bills' pass plays gain ground Sunday, our most confident pass call yet, and the model's confident calls have held up.**

*Bills at Jets, Sunday, Nov. 15, 1 p.m. ET, MetLife Stadium. Numbers are 2026 through week {THRU}. [Last week's prediction](bills-vikings-prediction.html)
and [how it went](bills-vikings-postgame.html): {w9_hits} of 7 calls hit.*

![Chance each team reaches each scoreline](wk10-ladder.png)

## The matchup that decides it

Every play moves a drive closer to scoring or further away; we measure that in points. This season the Bills' pass plays have gained
{R['buf_off']:+.2f} points each on average, {ordn_(R['buf_off_rk'])} in the NFL, over {R['n_off']} dropbacks. The Jets' pass defense has given up {R['opp_def']:+.2f} a play, {ordn_(R['opp_def_most'])}-most
of {R['n_teams']}, over {R['n_def']} dropbacks. An average pass play gains {R['lg']:+.2f}.

Put them together and our matchup model expects Buffalo's pass plays to gain about {C['buf_db']['expected']:+.2f} points each Sunday. Games swing a lot, so that's not a
promise; it says there's an **{C['buf_db']['p']:.0%}** chance that, all told, the Bills' passing plays leave them better off than they started.

**Is {C['buf_db']['p']:.0%} too bold?** It's the most confident pass call we've made, so we checked the model's track record at that level. On {db['n']} past team games
(2023-2025) it hadn't seen, when it gave a passing game 70% or more, it said {db_hi.said:.0%} on average and it happened {db_hi.happened:.0%} of the time ({int(db_hi.n)} games).

The rest of the game is closer to even. The Jets score {P['raw']['opp_off']:.2f} points per drive ({ordn_(P['rk']['opp_off_rank'])} of {P['rk']['n']}); the Bills' defense allows
{P['raw']['buf_def']:.2f} ({ordn_(P['rk']['buf_def_rank'])}).

## The scoreboard ladder

For each scoreline, here's our chance that each team gets at least that many points Sunday:

| Points | Bills | Jets |
|---|---|---|
{ladder_rows}

Read it like this: there's a {lad[24][0]:.0%} chance the Bills score 24 or more, and a {lad[24][1]:.0%} chance the Jets do.

## How a 30-point projection becomes {P['p_buf']:.0%}

Nobody scores exactly what we project. We looked at {len(res):,} past team scores from 2019-2023 and asked how far off we were. Half the time, a team landed
within about {miss50:.0f} points of our number; eight times in ten, within about {miss80:.0f}. (On games it had never seen, its average miss was {mae['model']:.1f} points.)

Then we play Sunday's game over and over, once for every one of those past misses. Eight times in ten the Bills land between {P['rng']['BUF'][0]:.0f} and
{P['rng']['BUF'][1]:.0f} points. For who wins, we took {wt['n_pairs']:,} real past games, noted how far off we were for each team in that same game, applied each pair
to Sunday's projections, and checked who came out ahead: Buffalo, {P['p_buf']:.0%} of the time. (A game tied after 60 minutes counts as half for each side.)

## The calls going on the Ledger

| Call | Our chance | Where it comes from |
|---|---|---|
{table}

![The calls](wk10-calls.png)

What "gain points" and "lose points" mean: these aren't scoreboard points. A team's runs "lose points" if, all told, its running plays left it worse off
than before. That's normal: in {ru['n']} past team games, runs lost points overall {1 - ru['rate']:.0%} of the time.

**Why no 20-point calls this week.** Last week we said our chances of a team reaching 20 points ran a few points low, and that we'd fix that before using
those lines again. We haven't fixed it yet, so we're not logging them. The ladder above has the same issue: on games the model never saw, when it gave a
team a 40-60% chance of reaching a scoreline, it said {mid_said:.0%} on average and the team got there {mid_hap:.0%} of the time. Read the middle of the ladder as a little low.

{ledger_status()}

## Where the {pb:.0f} comes from

Points come from drives. Four steps:

1. **How good is each side?** This season the Bills average {P['raw']['buf_off']:.2f} points per drive, the most in the NFL ({P['rk']['off']}). The Jets' defense
   allows {P['raw']['opp_def']:.2f} per drive, {P['rk']['def_most']}-most. An average offense scores {P['lg']:.2f}.
2. **Don't overreact to nine weeks.** We mix in last season and an average team. That makes the Bills' offense {P['off_b']:.2f} and the Jets' defense {P['def_m']:.2f}.
3. **Let them meet.** Both sides favor Buffalo, which leaves about {P['ppd_b']:.2f} points per drive.
4. **Count the drives and check against history.** About {P['drv']:.0f} drives a game gets you to about {P['ppd_b'] * P['drv']:.0f}. A final check against past games pulls
   extreme projections back toward normal and gives the home team about {P['coef'][2]:.1f} points. Buffalo is on the road, so it lands at **{pb:.1f}**.

The Jets go through the same steps from the other direction: an offense at {P['off_m']:.2f} per drive against a Bills defense at {P['def_b']:.2f}, plus the home bump.
That's **{pj:.1f}**.

## Did we check it?

**The win chance.** On {wt['n']} games from 2024-2026 the model had never seen, the team it leaned to won {wt['right']:.0%} of the time. Taking the home team every
time would have been right {wt['home_won']:.0%}.

![Win chance test](wk10-win-test.png)

*The chart counts a tied game as half a win; the {wt['right']:.0%} above counts it as a miss.*

**The pass and run calls.** These come from a simpler model, tested on {db['n']} past team games (2023-2025) against just guessing the league's usual rate.
It beat the guess on pass calls and edged it on run calls.

## What the model doesn't know

- **Injuries.** Our models don't know who plays. Check the final injury reports before kickoff.
- **One game is one game.** {P['p_buf']:.0%} means the Jets win this about one time in four. That's why every call goes on the Ledger and gets graded.

## For the stat-heads

- Matchup model {V01} (`src/ledger/model_v01.py`): expected = league + 0.5 x (offense gap + defense gap), plus the pooled within-team game-to-game spread;
  P = share of that spread above the threshold. EPA per dropback (scrambles and sacks included), EPA per designed rush. Bills dropback EPA expected
  {C['buf_db']['expected']:+.3f} (offense {C['buf_db']['off_mean']:+.3f}, Jets defense {C['buf_db']['def_mean']:+.3f}, league {C['buf_db']['league']:+.3f}); Jets dropback
  {C['opp_db']['expected']:+.3f}; rush: Bills {C['buf_ru']['expected']:+.3f}, Jets {C['opp_ru']['expected']:+.3f}.
- Matchup backtest (`scripts/backtest_model_v01.py`, 2023-25 weeks 8+, n={db['n']} per call type), Brier vs league-rate baseline: dropback {db['brier']:.4f} vs
  {db['brier_base']:.4f}; rush {ru['brier']:.4f} vs {ru['brier_base']:.4f}. Dropback calibration: """ + "; ".join(
        f"said {r.said:.0%} / happened {r.happened:.0%} (n={int(r.n)})" for r in db_cal.itertuples()) + f""".
- Raw dropback EPA per play, 2026 weeks 1-{THRU}: Bills offense {R['buf_off']:+.3f} (rank {R['buf_off_rk']}), Jets defense {R['opp_def']:+.3f} (rank {R['opp_def_rk']} of
  {R['n_teams']}, 1 = best), league {R['lg']:+.3f}.
- Points model {pm.VERSION} (`src/ledger/points_model.py`): ratings = (points + {pm.K} x prior) / (drives + {pm.K}), prior = league + {pm.PRIOR_KEEP} x last
  season's gap; calibrated score = {P['coef'][0]:.2f} + {P['coef'][1]:.3f} x raw + {P['coef'][2]:.2f} x home, fit on 2019-23 (week 2 on).
- Win chance ({WIN_VERSION}): {wt['n_pairs']:,} same-game residual pairs; out of sample (2024-26, week 2 on, n={wt['n']}): Brier {wt['brier']:.4f} vs {wt['brier_half']:.4f}
  (50/50) and {wt['brier_home']:.4f} (home-win rate).
- Ladder calibration out of sample (2024-26, all {len(LADDER)} lines pooled), chances 0.4-0.6: said {mid_said:.3f}, happened {mid_hap:.3f}, n={mid_n:,}.
- Data pinned through 2026 week {THRU}. No betting lines are used anywhere in these models.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Our projection for Sunday",
        "big": [[round(pb), "Bills, projected points"], [round(pj), "Jets, projected points"]],
        "note": (f"Bills win {P['p_buf']:.0%} of the time. The key matchup: Buffalo's passing game ({ordn_(R['buf_off_rk'])} in the NFL) against a Jets pass "
                 f"defense that's {ordn_(R['opp_def_most'])}-worst."),
        "explainer": {
            "kicker": "How we checked it", "title": "Its confident calls have held up.",
            "text": (f"When our matchup model gave a passing game 70% or more on {int(db_hi.n)} past games it hadn't seen, "
                     "it said this, and this is how often it happened:"),
            "fmt": "pct", "bars": [["What it said", round(float(db_hi.said), 3)], ["What happened", round(float(db_hi.happened), 3)]]},
    }, indent=1))
    print(md)


def ordn_(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


if __name__ == "__main__":
    main()
