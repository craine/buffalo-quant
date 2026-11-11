"""Bills trade for safety Amani Hooker (Nov 10, 2026 deadline). What the data says he brings, in plain English.

Writes reports/2026-11-10-hooker-trade.md, two PNGs and a hero JSON. Every number is computed here, except the trade terms,
which are reported facts cited to the Bills' announcement. Pinned: games through 2026 week THRU.
Coverage numbers (targets, yards allowed, missed tackles) are Pro Football Reference charting via nflverse: human-charted, noisy.
Safeties are identified by matching PFR names to nflverse rosters (same season, team, name) where position is a safety.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 9
HOOKER = "00-0035632"          # gsis id
HOOKER_PFR = "HookAm00"        # PFR id (matched by name+team+season, verified unique)
SAFETY = ("SAF", "FS", "SS", "S")
MIN_TGT, MIN_TGT_SEASON, MIN_TGT_3YR = 25, 15, 60
SLUG = "2026-11-10-hooker-trade"
SRC = "Source: nflverse player stats; Pro Football Reference coverage charting via nflverse. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def ordn(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def safety_seasons():
    pw = query("""SELECT season, week, team, player_id, player_display_name AS name, position, def_interceptions AS i
                  FROM raw_player_week WHERE season_type='REG'""")
    pw = pw[(pw.season < SEASON) | (pw.week <= THRU)]
    pf = query("""SELECT season, week, team, pfr_player_name AS name, pfr_player_id, def_ints, def_targets, def_completions_allowed,
                  def_yards_allowed, def_missed_tackles, def_tackles_combined FROM raw_pfr_def WHERE game_type='REG'""")
    pf = pf[(pf.season < SEASON) | (pf.week <= THRU)]
    saf = pw[pw.position.isin(SAFETY)][["season", "team", "name"]].drop_duplicates()
    x = pf.merge(saf, on=["season", "team", "name"])
    s = x.groupby(["season", "pfr_player_id", "name"]).agg(
        g=("week", "nunique"), ints=("def_ints", "sum"), tgt=("def_targets", "sum"), cmp=("def_completions_allowed", "sum"),
        yds=("def_yards_allowed", "sum"), mt=("def_missed_tackles", "sum"), tk=("def_tackles_combined", "sum")).reset_index()
    s["ypt"] = s.yds / s.tgt
    s["cmp_pct"] = s.cmp / s.tgt
    s["int_rate"] = s.ints / s.tgt
    s["mt_pct"] = s.mt / (s.mt + s.tk)
    return pw, x, s


def carryover(s):
    q = s[(s.tgt >= MIN_TGT) & (s.season < SEASON)]
    a = q.merge(q, on="pfr_player_id", suffixes=("", "_n"))
    a = a[a.season_n == a.season + 1]
    out = {m: float(a[m].corr(a[m + "_n"])) for m in ("int_rate", "ypt", "cmp_pct", "mt_pct")}
    return out, len(a), int(a.season.min()), int(a.season_n.max())


def main():
    pw, x, s = safety_seasons()
    h = pw[pw.player_id == HOOKER]
    hs = h.groupby("season").agg(g=("week", "nunique"), ints=("i", "sum"))
    career_ints = int(hs.ints.sum())
    lead = pw[pw.season == SEASON].groupby(["player_id", "name"]).i.sum()
    top = lead.max()
    co_leaders = [n for (pid, n), v in lead.items() if v == top and pid != HOOKER]
    h_ints = int(hs.loc[SEASON, "ints"])
    h_games = int(hs.loc[SEASON, "g"])
    best_prev = hs.drop(SEASON).ints
    zero_years = [int(y) for y, v in best_prev.items() if v == 0]

    hp = s[s.pfr_player_id == HOOKER_PFR].set_index("season")
    assert hp.name.nunique() == 1
    # 2026 among safeties
    z = s[(s.season == SEASON) & (s.tgt >= MIN_TGT_SEASON)].copy()
    z["rk_ypt"] = z.ypt.rank(method="min")
    z["rk_mt"] = z.mt_pct.rank(method="min")
    hz = z[z.pfr_player_id == HOOKER_PFR].iloc[0]
    lg26 = dict(ypt=z.yds.sum() / z.tgt.sum(), mt=z.mt.sum() / (z.mt.sum() + z.tk.sum()))
    # 2023-2025 pooled
    p3 = s[s.season.between(SEASON - 3, SEASON - 1)].groupby(["pfr_player_id", "name"]).agg(
        tgt=("tgt", "sum"), yds=("yds", "sum"), mt=("mt", "sum"), tk=("tk", "sum"), ints=("ints", "sum")).reset_index()
    p3 = p3[p3.tgt >= MIN_TGT_3YR].copy()
    p3["ypt"] = p3.yds / p3.tgt
    p3["mt_pct"] = p3.mt / (p3.mt + p3.tk)
    p3["rk_ypt"] = p3.ypt.rank(method="min")
    h3 = p3[p3.pfr_player_id == HOOKER_PFR].iloc[0]
    lg3 = dict(ypt=p3.yds.sum() / p3.tgt.sum(), mt=p3.mt.sum() / (p3.mt.sum() + p3.tk.sum()))
    # Bills safeties this season, and every team's safeties
    tm = x[x.season == SEASON].groupby("team").agg(tgt=("def_targets", "sum"), yds=("def_yards_allowed", "sum"),
                                                   mt=("def_missed_tackles", "sum"), tk=("def_tackles_combined", "sum"))
    tm["ypt"] = tm.yds / tm.tgt
    tm["mt_pct"] = tm.mt / (tm.mt + tm.tk)
    tm["rk_ypt"] = tm.ypt.rank(method="min", ascending=False)   # 1 = most yards allowed
    tm["rk_mt"] = tm.mt_pct.rank(method="min", ascending=False)  # 1 = most missed tackles
    bufs = tm.loc["BUF"]
    co, n_pairs, y0, y1 = carryover(s)

    # ---- chart 1: interceptions by season
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    yrs = list(hs.index)
    ax.bar([str(y) for y in yrs], hs.ints, color=[BLUE if y == SEASON else GRAY for y in yrs], width=0.6, zorder=2)
    for i, (y, r) in enumerate(hs.iterrows()):
        ax.text(i, r.ints + 0.1, f"{int(r.ints)}", ha="center", fontsize=11, fontweight="bold", color=INK)
        ax.text(i, -0.55, f"{int(r.g)} games", ha="center", fontsize=8, color=MUTED)
    ax.set_ylim(-0.8, max(hs.ints) + 1.2)
    ax.set_yticks(range(0, int(max(hs.ints)) + 1))
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Amani Hooker's interceptions come in bunches",
           f"Interceptions by season, all with Tennessee. {SEASON} is through week {THRU}.",
           f"{career_ints} career interceptions.")
    fig.savefig(OUT / "hooker-ints.png"); plt.close(fig)

    # ---- chart 2: what carries over
    lab = {"mt_pct": "Missed tackles", "int_rate": "Interceptions", "ypt": "Yards allowed per target",
           "cmp_pct": "Completions allowed"}
    order = sorted(co, key=co.get)
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    ax.barh([lab[k] for k in order], [co[k] for k in order], color=[BLUE if k == "int_rate" else GRAY for k in order], height=0.55, zorder=2)
    for i, k in enumerate(order):
        ax.text(co[k] + 0.01, i, f"{co[k]:.2f}", va="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xlim(0, 1)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlabel("How well one season predicts the next (0 = not at all, 1 = perfectly)", fontsize=9.5)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "For safeties, almost nothing carries over from one season to the next",
           f"Every safety with {MIN_TGT}+ targets in back-to-back seasons, {y0}-{y1} ({n_pairs} pairs).",
           "Interceptions per target, yards and completions allowed per target, missed tackles per tackle attempt.")
    fig.savefig(OUT / "hooker-carryover.png"); plt.close(fig)

    lead_txt = f"tied with {co_leaders[0]} for the NFL lead" if len(co_leaders) == 1 else (
        "the NFL lead" if not co_leaders else f"tied for the NFL lead with {len(co_leaders)} others")
    md = f"""# The Bills paid a second-round pick for Amani Hooker. Here's what they're actually getting

**Finding: Hooker arrives with {h_ints} interceptions, {lead_txt}. Interceptions are a shaky thing to build on: he had
{int(hs.loc[SEASON - 2, 'ints'])} in {SEASON - 2} and {int(hs.loc[SEASON - 1, 'ints'])} in {SEASON - 1}, and for safeties, interceptions barely carry over from one season to the next. What
the Bills are getting is a sure tackler whose coverage has been about average this season and below average before it. Even so, his
numbers beat what Buffalo's safeties have given up this season.**

*The Bills traded a 2027 second-round pick to Tennessee for Hooker and a 2027 fifth-round pick on Tuesday, Nov. 10, deadline day. He's
signed through 2028. (Trade terms as announced by the Bills.) Numbers below are through week {THRU} of the {SEASON} season.*

![Hooker's interceptions by season](hooker-ints.png)

## The interceptions are real, and they come in bunches

Hooker has {career_ints} interceptions in {len(hs)} seasons, all with Tennessee. They don't arrive evenly: he had {int(hs.loc[SEASON - 2, 'ints'])}
in {SEASON - 2}, then {int(hs.loc[SEASON - 1, 'ints'])} in {SEASON - 1} over {int(hs.loc[SEASON - 1, 'g'])} games, then {h_ints} in {h_games} games this season.

That's normal for safeties, and it's the main thing to understand about this trade. We looked at every safety who was thrown at
{MIN_TGT} or more times in back-to-back seasons from {y0} to {y1}, {n_pairs} pairs in all, and asked: how well does one season's number predict
the next? On a scale where 0 means "not at all" and 1 means "perfectly," interceptions scored {co['int_rate']:.2f}. A big interception year
tells you a little about the next one, not a lot.

![What carries over](hooker-carryover.png)

To be fair to Hooker, almost nothing about a safety carries over well. Yards allowed per target scored {co['ypt']:.2f} and completions allowed
{co['cmp_pct']:.2f}. The best of a weak bunch is tackling: how often a safety misses a tackle he attempts scored {co['mt_pct']:.2f}, not much better than
interceptions. Safeties are
hard to measure, and every number here comes with that warning.

## What the Bills are getting

**A sure tackler.** This season Hooker has missed {hz.mt_pct:.1%} of his tackle attempts. The average safety who's been thrown at {MIN_TGT_SEASON}+
times misses {lg26['mt']:.1%}; Hooker ranks {ordn(int(hz.rk_mt))} best of {len(z)}.

**Coverage: about average now, below average before.** Passes thrown at Hooker have gained {hz.ypt:.1f} yards per target this season ({int(hz.tgt)} targets, a small sample), about the same as the average
safety ({lg26['ypt']:.1f}), {ordn(int(hz.rk_ypt))} of {len(z)} (1st = fewest yards allowed). Over {SEASON - 3} to {SEASON - 1} he allowed {h3.ypt:.1f} per target,
more than the average safety's {lg3['ypt']:.1f} ({ordn(int(h3.rk_ypt))} of {len(p3)} safeties thrown at {MIN_TGT_3YR}+ times).

**A fit for what Buffalo needs.** The Bills' safeties have allowed {bufs.ypt:.1f} yards per target this season, the {ordn(int(bufs.rk_ypt))}-most of the
{len(tm)} teams, and have missed {bufs.mt_pct:.1%} of their tackle attempts, the {ordn(int(bufs.rk_mt))}-most. Hooker's numbers beat both: this season ({hz.ypt:.1f} yards per target, {hz.mt_pct:.1%} missed
tackles) and, in coverage, over the three seasons before it ({h3.ypt:.1f}).

## What it means

- **Don't expect {['zero','one','two','three','four','five','six','seven'][h_ints]} more.** If the interceptions keep coming, that's a bonus. The way to think about this trade is "steady starter
  who tackles well," not "takeaway machine."
- **It's a real price.** Per the Bills, it's the most draft capital general manager Brandon Beane has spent on an in-season trade. The
  bet is that a reliable safety for this season and two more is worth a second-round pick.
- **Watch the tackling.** It carries over a little better than the rest of a safety's numbers, and it's where Buffalo's safeties have
  struggled this season. If Hooker's tackling travels to Buffalo, the defense that just held Minnesota to {query("SELECT home_score FROM raw_schedules WHERE game_id='2026_09_BUF_MIN'").home_score.iloc[0]:.0f} points gets sturdier at the back.

## For the stat-heads

- Interceptions: nflverse weekly player stats (gsis {HOOKER}), regular season. {SEASON} through week {THRU}. Co-leader(s): {', '.join(co_leaders) or 'none'}.
- Coverage: Pro Football Reference charting via nflverse (`pfr_advstats` def). Targets, completions, yards allowed, missed tackles,
  combined tackles. Missed-tackle rate = missed / (missed + combined tackles). Charted by humans; treat as noisy.
- Safeties: PFR rows matched to nflverse rosters on season, team and name where the roster position is {', '.join(SAFETY)}.
- Year-to-year: Pearson correlation of each rate between consecutive seasons, safeties with {MIN_TGT}+ targets in both, {y0}-{y1},
  n={n_pairs}: interceptions per target {co['int_rate']:.3f}, yards per target {co['ypt']:.3f}, completion rate {co['cmp_pct']:.3f},
  missed-tackle rate {co['mt_pct']:.3f}.
- Hooker {SEASON}: {int(hz.tgt)} targets, {hz.ypt:.2f} yards/target, missed-tackle rate {hz.mt_pct:.3f}. {SEASON - 3}-{SEASON - 1}: {int(h3.tgt)} targets, {h3.ypt:.2f}.
- Bills safeties {SEASON}: {int(bufs.tgt)} targets, {bufs.ypt:.2f} yards/target, missed-tackle rate {bufs.mt_pct:.3f}.
- Trade terms and "most draft capital under Beane": buffalobills.com, "Bills land impact safety Amani Hooker in trade with Titans," Nov. 10, 2026.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "The Hooker trade",
        "big": [[h_ints, "interceptions this season"], [career_ints, "in his career"]],
        "note": "Interceptions barely carry over for safeties. What the Bills are getting: a sure tackler whose coverage beats what Buffalo's safeties have allowed.",
        "explainer": {"kicker": "What carries over", "title": "How well one season predicts the next.",
                      "text": f"For safeties, {y0}-{y1} (0 = not at all, 1 = perfectly):", "fmt": "score",
                      "bars": [[lab[k], round(co[k], 2)] for k in sorted(co, key=co.get, reverse=True)]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
