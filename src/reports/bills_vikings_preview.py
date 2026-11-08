"""Week 9 preview: Bills at Vikings, Monday Night Football, Nov. 9, 2026 (U.S. Bank Stadium, dome).

Writes reports/2026-wk09-bills-at-vikings.md and three PNGs. Every number is computed here.
Headline team numbers are unfiltered (all plays); garbage-time-filtered ranks shown alongside.
Draft predictions are NOT logged; Charlie approves before anything goes on the Ledger.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger.model_v01 import SHRINK, VERSION, game_values, prob_over, qb_relative
from src.metrics.team import season_table
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 8
WENTZ, MURRAY = "00-0032950", "00-0035228"
SRC = "Source: nflverse play-by-play. Regular season."
EP_SEASONS = (2018, 2026)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def ordn(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


DB_WHERE = ("season_type='REG' AND qb_dropback=1 AND epa IS NOT NULL AND COALESCE(two_point_attempt,0)=0")


def qb_seasons():
    q = query(f"""SELECT season, COALESCE(passer_player_id, rusher_player_id) pid, COUNT(DISTINCT game_id) g,
                  COUNT(*) db, AVG(epa) epa, AVG(sack) sk FROM raw_pbp WHERE season IN (2025, 2026) AND {DB_WHERE}
                  GROUP BY 1, 2""")
    lg = query(f"SELECT season, AVG(epa) epa, AVG(sack) sk FROM raw_pbp WHERE season IN (2025, 2026) AND {DB_WHERE} GROUP BY 1").set_index("season")
    q150 = q[q.db >= 150].copy()
    q150["rk"] = q150.groupby("season").epa.rank(ascending=False, method="min").astype(int)
    q150["n_q"] = q150.groupby("season").pid.transform("size")
    return q, lg, q150


def ep_examples():
    a, b = EP_SEASONS
    w = f"season BETWEEN {a} AND {b} AND season_type='REG' AND (pass=1 OR rush=1) AND epa IS NOT NULL"
    ep = query(f"""SELECT yardline_100 y, AVG(ep) ep, COUNT(*) n FROM raw_pbp WHERE {w} AND down=1 AND ydstogo=10
                   GROUP BY 1""").set_index("y")
    third = query(f"""SELECT CASE WHEN sack=1 THEN 'sack' WHEN third_down_converted=1 THEN 'conv' ELSE 'fail' END o,
                      COUNT(*) n, AVG(epa) epa FROM raw_pbp WHERE {w} AND down=3 AND ydstogo=8 AND qb_dropback=1 GROUP BY 1""").set_index("o")
    return ep, third


def main():
    off = season_table("off", [SEASON]).set_index("team")
    de = season_table("def", [SEASON]).set_index("team")
    bo, md, bd, mo = off.loc["BUF"], de.loc["MIN"], de.loc["BUF"], off.loc["MIN"]
    q, lg, q150 = qb_seasons()
    qi = q.set_index(["season", "pid"])
    w26, m26, w25 = qi.loc[(2026, WENTZ)], qi.loc[(2026, MURRAY)], qi.loc[(2025, WENTZ)]
    murray_rk = q150.set_index(["season", "pid"]).loc[(2026, MURRAY)]
    ep, third = ep_examples()
    # second check: does per-play efficiency track scoring? (team offense, 2026)
    r_pts = np.corrcoef(off.epa_play, off.pts_per_drive)[0, 1]
    lg_mean = query(f"SELECT season, AVG(epa) e FROM raw_pbp WHERE season BETWEEN {EP_SEASONS[0]} AND {EP_SEASONS[1]} "
                    "AND season_type='REG' AND (pass=1 OR rush=1) AND epa IS NOT NULL GROUP BY 1").e

    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.game_id == "2026_09_BUF_MIN"] if not lp.empty else lp
    if len(lp):
        ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min()} UTC, before kickoff.** "
                         "These are graded after the game, hit or miss, and stay up either way.")
    else:
        ledger_status = ("**Our model's numbers for this game.** A call only counts once it's logged on the "
                         "[Ledger](../ledger.html) before kickoff, and every logged call is graded after the game.")
    # model calls (draft)
    w_db, n_db = qb_relative(WENTZ, "dropback_epa", [2025, 2026])
    w_sk, n_sk = qb_relative(WENTZ, "sack_rate", [2025, 2026])
    c1b = prob_over("MIN", "BUF", "dropback_epa", 0.0)
    c1 = prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=w_db)
    c2 = prob_over("MIN", "BUF", "rush_epa", 0.0)
    c3b = prob_over("MIN", "BUF", "sack_rate", 0.06)
    c3 = prob_over("MIN", "BUF", "sack_rate", 0.06, off_override=w_sk)

    # ---- chart 1: strength vs strength
    units = [("Bills offense", bo.epa_play - bo.epa_play_lg, int(bo.epa_play_rk), BLUE),
             ("Vikings defense", -(md.epa_play - md.epa_play_lg), int(md.epa_play_rk), RED),
             ("Bills defense", -(bd.epa_play - bd.epa_play_lg), int(bd.epa_play_rk), BLUE),
             ("Vikings offense", mo.epa_play - mo.epa_play_lg, int(mo.epa_play_rk), RED)]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    ys = np.arange(len(units))[::-1]
    for y, (lab, v, rk, c) in zip(ys, units):
        ax.barh(y, v, color=c, height=0.55, zorder=2)
        ax.text(v + (0.006 if v >= 0 else -0.006), y, f"{ordn(rk)} of 32", va="center", ha="left" if v >= 0 else "right",
                fontsize=10, color=INK, fontweight="bold")
    ax.set_yticks(ys, [u[0] for u in units]); ax.axvline(0, color=INK, lw=1)
    lim = max(abs(u[1]) for u in units) * 1.45; ax.set_xlim(-lim, lim)
    ax.set_xlabel("Points per play better (+) or worse (-) than an average NFL unit")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "The best offense meets the best defense",
           f"2026 through week {THRU}, every play. Right = better than average for that unit.",
           f"Bills {int(bo.games)} games ({int(bo.plays)} offensive plays); Vikings {int(mo.games)} games ({int(md.plays)} defensive plays).")
    fig.savefig(OUT / "wk09-matchup.png"); plt.close(fig)

    # ---- chart 2: where the points-per-play number comes from
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.9), dpi=200, gridspec_kw={"width_ratios": [1.5, 1]})
    e = ep[ep.n >= 100]
    a1.plot(100 - e.index, e.ep, color=BLUE, lw=2.2)
    for y in (75, 50, 25, 10):
        a1.scatter(100 - y, ep.loc[y, "ep"], color=RED, s=40, zorder=3)
        a1.annotate(f"{ep.loc[y, 'ep']:.1f}", (100 - y, ep.loc[y, "ep"]), xytext=(-4, 8), textcoords="offset points",
                    fontsize=9.5, color=INK, ha="right")
    a1.set_xticks([25, 50, 75, 90], ["Own 25", "Midfield", "Opp 25", "Opp 10"])
    a1.set_ylabel("Points a drive is worth, on average"); a1.axhline(0, color="#D5D8DE", lw=1)
    a1.set_title("1st-and-10: where you start matters", loc="left", fontsize=10.5, fontweight="bold", color=INK)
    a1.grid(color="#EEF0F3"); a1.set_axisbelow(True)
    labs = [("Converted", "conv", BLUE), ("Stopped", "fail", GRAY), ("Sacked", "sack", RED)]
    vals = [third.loc[k, "epa"] for _, k, _ in labs]
    a2.bar([l for l, _, _ in labs], vals, color=[c for _, _, c in labs], width=0.6, zorder=2)
    for i, v in enumerate(vals):
        a2.text(i, v + (0.08 if v >= 0 else -0.08), f"{v:+.1f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=10, color=INK)
    a2.axhline(0, color=INK, lw=1); a2.set_ylabel("Points gained or lost on the play")
    a2.set_ylim(min(vals) - 0.6, max(vals) + 0.6)
    a2.set_title("3rd-and-8, quarterback drops back", loc="left", fontsize=10.5, fontweight="bold", color=INK)
    a2.grid(axis="y", color="#EEF0F3"); a2.set_axisbelow(True)
    finish(fig, "Every play changes how many points a drive is worth",
           f"Every NFL regular-season play, {EP_SEASONS[0]}-{EP_SEASONS[1]}.",
           f"Left: {int(e.n.sum()):,} first-and-10 plays. Right: {int(third.n.sum()):,} third-and-8 dropbacks.")
    fig.savefig(OUT / "wk09-points-per-play.png"); plt.close(fig)

    # ---- chart 3: Wentz vs Murray
    rows = [("Murray\n2026", m26, BLUE), ("Wentz\n2026", w26, RED), ("Wentz\n2025", w25, GRAY)]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    v3 = [r_.epa for _, r_, _ in rows]
    ax.bar([l for l, _, _ in rows], v3, color=[c for _, _, c in rows], width=0.55, zorder=2)
    lg_at = [lg.loc[2026, "epa"], lg.loc[2026, "epa"], lg.loc[2025, "epa"]]
    for i, (_, r_, _) in enumerate(rows):
        ax.text(i, (max(r_.epa, lg_at[i]) + 0.006) if r_.epa >= 0 else r_.epa - 0.006, f"{r_.epa:+.2f}\n{int(r_.db)} dropbacks",
                ha="center", va="bottom" if r_.epa >= 0 else "top", fontsize=9.5, color=INK)
    ax.plot([-0.4, 1.4], [lg.loc[2026, "epa"]] * 2, color=INK, ls="--", lw=1.2)
    ax.plot([1.6, 2.4], [lg.loc[2025, "epa"]] * 2, color=INK, ls="--", lw=1.2)
    ax.text(2.42, lg.loc[2025, "epa"], "league\naverage", fontsize=8.5, color=MUTED, va="center")
    ax.axhline(0, color="#D5D8DE", lw=1)
    lo = min(min(v3), 0) - 0.05; hi = max(max(v3), lg.epa.max()) + 0.06; ax.set_ylim(lo, hi)
    ax.set_ylabel("Points added per dropback"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Wentz has been about average; Murray was below it this year",
           "Points added per dropback (passes, sacks and scrambles). Dashed = league average that season.",
           f"Wentz 2026 is {int(w26.db)} dropbacks over {int(w26.g)} games: a very small sample. Murray: {int(m26.db)} dropbacks, {int(m26.g)} games.")
    fig.savefig(OUT / "wk09-qbs.png"); plt.close(fig)

    pts = lambda v: f"{v:+.2f}"
    md_text = f"""# Bills at Vikings: the NFL's best offense meets its best defense, and Minnesota's backup QB

**Finding: Through eight weeks, the Bills have the most efficient offense in football and the Vikings have the most
efficient defense (counting every play; with garbage time removed they rank {ordn(bo.epa_play_neutral_rk)} and {ordn(md.epa_play_neutral_rk)}). Something has to give
Monday night. Buffalo's weak spot is its pass defense ({ordn(bd.dropback_epa_rk)} of 32), and with Kyler Murray hurt, Minnesota starts Carson
Wentz, who has been about an average NFL passer over the last two seasons. Murray was below average this year.**

*Bills at Vikings, Monday Night Football, Nov. 9, 8:15 p.m. ET, U.S. Bank Stadium (indoors). Both teams have played
{int(bo.games)} games. Numbers count every play unless noted.*

![Matchup](wk09-matchup.png)

## How we measure "efficiency": points per play

Yards don't tell you much on their own. A 6-yard gain on 3rd-and-5 keeps a drive alive; the same 6 yards on 3rd-and-10
usually means a punt. So we measure every play by **how many points it adds to or takes away from the drive**.

**The source:** the NFL's official play-by-play, cleaned up and published free by the nflverse project. It covers every
snap: down, distance, field position, time left and what happened.

**The reasoning:** start with how many points a drive is usually worth from a given spot. Across every NFL play from
{EP_SEASONS[0]} to {EP_SEASONS[1]}:

![Points per play](wk09-points-per-play.png)

- 1st-and-10 at your own 25 is worth about **{ep.loc[75, 'ep']:.1f} points** on average.
- At midfield, about **{ep.loc[50, 'ep']:.1f}**. At the opponent's 25, about **{ep.loc[25, 'ep']:.1f}**.
- Every play moves that number. On 3rd-and-8, a quarterback who drops back and converts adds about **{third.loc['conv', 'epa']:+.1f} points**.
  If he doesn't convert (an incompletion, a short gain or a turnover), the drive loses about **{abs(third.loc['fail', 'epa']):.1f}**. If he's sacked, about **{abs(third.loc['sack', 'epa']):.1f}**.

**The math:** take the points the drive was worth after the play, subtract what it was worth before, and you have that
play's value. Average it over every play a team runs and you get its **points per play**. The "points a drive is worth"
numbers come from the nflverse project's public expected-points model, built on years of NFL games.

**How we checked it:** across the whole league, plays average out to about zero each season, as they should (we test
this on every data load). And it tracks scoring: this season, teams' points per play and their points per drive move
together very closely (correlation {r_pts:.2f} across all 32 offenses).

So when we say the Bills' offense is **{pts(bo.epa_play)} points per play** and the league average is {pts(bo.epa_play_lg)}, that's
about {(bo.epa_play - bo.epa_play_lg) * bo.plays / bo.games:.0f} extra points per game over the {bo.plays / bo.games:.0f} offensive plays the Bills average. That's the gap shown in the chart above.

## The Bills' offense vs. the Vikings' defense

| | Bills offense | Vikings defense | League average |
|---|---|---|---|
| Points per play | {pts(bo.epa_play)} ({ordn(bo.epa_play_rk)}) | {pts(md.epa_play)} allowed ({ordn(md.epa_play_rk)}) | {pts(bo.epa_play_lg)} |
| Points per pass play | {pts(bo.dropback_epa)} ({ordn(bo.dropback_epa_rk)}) | {pts(md.dropback_epa)} allowed ({ordn(md.dropback_epa_rk)}) | {pts(bo.dropback_epa_lg)} |
| Points per drive | {bo.pts_per_drive:.2f} ({ordn(bo.pts_per_drive_rk)}) | {md.pts_per_drive:.2f} allowed ({ordn(md.pts_per_drive_rk)}) | {bo.pts_per_drive_lg:.2f} |
| Sacks per pass play | {bo.sack_rate:.1%} taken ({ordn(bo.sack_rate_rk)}) | {md.sack_rate:.1%} made ({ordn(md.sack_rate_rk)}) | {bo.sack_rate_lg:.1%} |

Ranks: 1st is best for that unit. Take out blowout garbage time and the Bills' offense ranks {ordn(bo.epa_play_neutral_rk)} and the Vikings'
defense {ordn(md.epa_play_neutral_rk)}, so the strength-on-strength billing holds either way.

The Vikings get to the quarterback more than anyone ({md.sack_rate:.1%} of pass plays). The Bills' offensive line has been
slightly better than average at preventing sacks ({ordn(bo.sack_rate_rk)}).

## The Vikings' offense vs. the Bills' defense

| | Vikings offense | Bills defense | League average |
|---|---|---|---|
| Points per play | {pts(mo.epa_play)} ({ordn(mo.epa_play_rk)}) | {pts(bd.epa_play)} allowed ({ordn(bd.epa_play_rk)}) | {pts(mo.epa_play_lg)} |
| Points per pass play | {pts(mo.dropback_epa)} ({ordn(mo.dropback_epa_rk)}) | {pts(bd.dropback_epa)} allowed ({ordn(bd.dropback_epa_rk)}) | {pts(mo.dropback_epa_lg)} |
| Points per designed run | {pts(mo.rush_epa)} ({ordn(mo.rush_epa_rk)}) | {pts(bd.rush_epa)} allowed ({ordn(bd.rush_epa_rk)}) | {pts(mo.rush_epa_lg)} |
| Sacks per pass play | {mo.sack_rate:.1%} taken ({ordn(mo.sack_rate_rk)}) | {bd.sack_rate:.1%} made ({ordn(bd.sack_rate_rk)}) | {mo.sack_rate_lg:.1%} |

This is the Bills' problem area. Their pass defense has allowed {pts(bd.dropback_epa)} points per pass play, {ordn(bd.dropback_epa_rk)} in the league,
and their pass rush gets home on only {bd.sack_rate:.1%} of pass plays. Minnesota's offense has struggled ({ordn(mo.epa_play_rk)}), but its quarterback
just changed.

## The quarterback change

Kyler Murray is out with a strained hamstring, so Carson Wentz starts. The two have been different kinds of passers:

![Quarterbacks](wk09-qbs.png)

| Quarterback | Season | Games | Dropbacks | Points per dropback | League average | Sacked on |
|---|---|---|---|---|---|---|
| Kyler Murray | 2026 | {int(m26.g)} | {int(m26.db)} | {pts(m26.epa)} | {pts(lg.loc[2026, 'epa'])} | {m26.sk:.1%} |
| Carson Wentz | 2026 | {int(w26.g)} | {int(w26.db)} (small sample) | {pts(w26.epa)} | {pts(lg.loc[2026, 'epa'])} | {w26.sk:.1%} |
| Carson Wentz | 2025 | {int(w25.g)} | {int(w25.db)} | {pts(w25.epa)} | {pts(lg.loc[2025, 'epa'])} | {w25.sk:.1%} |

Among {int(murray_rk.n_q)} quarterbacks with 150+ dropbacks this season, Murray ranks {ordn(murray_rk.rk)}. Wentz's 2026 number looks better, but
{int(w26.db)} dropbacks is far too few to read much into. Over the last two seasons combined ({n_db} dropbacks), Wentz has been about
league average. The catch:
he's been sacked more often than average ({w_sk * 100:.1f} percentage points above the league rate), and Minnesota's offense already
allows sacks at the {ordn(33 - mo.sack_rate_rk)}-highest rate in the league. That's an opening for a Bills pass rush that hasn't found many.

## What we're watching

{ledger_status}

| # | What we expect | Chance |
|---|---|---|
| 1 | Minnesota's pass plays add points overall (more than zero points per dropback; the league average is {pts(mo.dropback_epa_lg)}) | **{c1['p']:.0%}** |
| 2 | Minnesota's designed runs lose points overall (less than zero per run; the league average is {pts(mo.rush_epa_lg)}) | **{1 - c2['p']:.0%}** |
| 3 | The Bills sack the quarterback on more than 6% of his dropbacks | **{c3['p']:.0%}** |

How we get these: we start from each side's season average, pull it halfway back toward the league average (seven games
is a small sample), combine offense and defense, and then look at how much a team's single-game number usually bounces
around its average. For calls 1 and 3 we used Wentz's own passing and sack numbers in place of the Vikings' team numbers,
which were mostly Murray's games. That moved call 1 from {c1b['p']:.0%} to {c1['p']:.0%} and call 3 from {c3b['p']:.0%} to {c3['p']:.0%}.

## For the stat-heads

- Points per play = EPA (expected points added) per play, nflverse/nflfastR expected-points model. Team numbers:
  `src/metrics/team.py` season tables, regular season through week {THRU}, `pass == 1 or rush == 1`, EPA not null,
  no kneels, spikes, two-point tries or no-plays. Points per pass play = EPA per dropback (sacks and scrambles included);
  designed run = rush excluding scrambles. League averages are means of the 32 team values.
- Garbage-time filter (win probability 10-90%): Bills offense {pts(bo.epa_play_neutral)} ({ordn(bo.epa_play_neutral_rk)}),
  Vikings defense {pts(md.epa_play_neutral)} ({ordn(md.epa_play_neutral_rk)}), Bills defense {pts(bd.epa_play_neutral)} ({ordn(bd.epa_play_neutral_rk)}),
  Vikings offense {pts(mo.epa_play_neutral)} ({ordn(mo.epa_play_neutral_rk)}).
- Expected-points examples: mean `ep` on 1st-and-10 by yard line; mean EPA on 3rd-and-8 dropbacks by outcome,
  {EP_SEASONS[0]}-{EP_SEASONS[1]} regular season. League mean EPA/play by season ranges {lg_mean.min():+.3f} to {lg_mean.max():+.3f}.
  Correlation of 2026 team EPA/play with points per drive: {r_pts:.2f} (n = 32).
- QB splits by gsis id (`COALESCE(passer_player_id, rusher_player_id)`), `qb_dropback == 1`, EPA not null, no two-point
  tries. League average in the QB table = all such dropbacks that season (play-weighted); the model calls use the
  mean of team-game values instead, which differs slightly (2026 EPA/dropback {lg.loc[2026, 'epa']:.3f} play-weighted vs {game_values(2026, 'dropback_epa').query("side == 'off'").v.mean():.3f} team-game mean).
- Draft calls: Ledger model {VERSION} (`src/ledger/model_v01.py`), shrink {SHRINK}. Expected game value = league +
  {SHRINK} x (offense vs league + defense vs league); probability from the 2026 within-team game-to-game spread.
  Wentz substitution (`off_override`): dropback-weighted, league-relative, 2025-26 ({n_db} dropbacks): EPA/dropback
  {w_db:+.4f}, sack rate {w_sk:+.4f}. Expected values: call 1 {c1['expected']:+.3f} (team-based {c1b['expected']:+.3f});
  call 2 {c2['expected']:+.3f}; call 3 {c3['expected']:.3f} (team-based {c3b['expected']:.3f}).
- off_override replaces Minnesota's whole 2026 offensive level (line and receivers included) with Wentz's own number;
  196 of his 243 dropbacks came with Minnesota in 2025, so the supporting cast is mostly the same. The team value it
  replaces includes Wentz's 47 dropbacks from weeks 1-2. Baseline for both is the mean of team-game values.
- Small samples throughout: {int(bo.games)} games per team; Wentz 2026 is {int(w26.db)} dropbacks.
- Injury news: Vikings coach Kevin O'Connell announced Nov. 5, 2026 that Wentz starts with Murray out (strained hamstring,
  hurt in the week 8 loss to Detroit). Source: ESPN, Nov. 5, 2026.
"""
    (OUT / "2026-wk09-bills-at-vikings.md").write_text(md_text)
    import json
    (OUT / "2026-wk09-bills-at-vikings.hero.json").write_text(json.dumps({
        "label": f"Through week {THRU}, efficiency per play",
        "big": [[f"#{int(bo.epa_play_rk)}", "Bills offense"], [f"#{int(md.epa_play_rk)}", "Vikings defense"]],
        "note": (f"Counting every play. With garbage time removed: Bills {ordn(bo.epa_play_neutral_rk)}, "
                 f"Vikings {ordn(md.epa_play_neutral_rk)}. Something has to give Monday night."),
        "explainer": {
            "kicker": "How we know", "title": "Every play is worth points.",
            "text": (f"We judge every snap by how many points it adds to or takes away from the drive. "
                     f"On 3rd-and-8, a conversion adds about {third.loc['conv', 'epa']:+.1f} points; a sack costs about "
                     f"{abs(third.loc['sack', 'epa']):.1f}. Here's what 1st-and-10 is worth depending on where you start."),
            "fmt": "pts",
            "bars": [["Own 25", round(float(ep.loc[75, 'ep']), 2)], ["Midfield", round(float(ep.loc[50, 'ep']), 2)],
                     ["Opp. 25", round(float(ep.loc[25, 'ep']), 2)], ["Opp. 10", round(float(ep.loc[10, 'ep']), 2)]]},
    }, indent=1))
    print(md_text)


if __name__ == "__main__":
    main()
