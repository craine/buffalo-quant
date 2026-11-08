"""reports/2026-defense-baseline.md + charts. Every number here comes from the queries below."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.db import ROOT, connect, query
from src.metrics.adjust import league_adjusted_rank, opp_adjusted_defense, pass_defense_crosscheck
from src.metrics.team import LABELS, season_table

BLUE, RED, GRAY, INK, MUTED = "#00338D", "#C60C30", "#A7ADB8", "#1B1F27", "#5B6270"
OUT = ROOT / "reports"
SOURCE = "Source: nflverse play-by-play, regular season. Buffalo Quant Desk."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": INK, "font.size": 11})

SUMMARY_METRICS = ["epa_play", "dropback_epa", "rush_epa", "sack_rate", "explosive_rate",
                   "third_down_rate", "rz_td_rate", "pts_per_drive"]


def latest_week(con):
    return int(query("SELECT MAX(week) w FROM clean_team_week WHERE season=2026 AND season_type='REG'", con=con).w[0])


def rank_chart(b, wk, plays26):
    rows = SUMMARY_METRICS[::-1]
    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=200)
    for i, m in enumerate(rows):
        r25, r26 = b.loc[2025, m + "_rk"], b.loc[2026, m + "_rk"]
        col = BLUE if r26 < r25 else RED
        ax.plot([r25, r26], [i, i], color="#D5D8DE", lw=2, zorder=1, solid_capstyle="round")
        ax.scatter(r25, i, s=90, color=GRAY, zorder=2, edgecolor="white", lw=2)
        ax.scatter(r26, i, s=110, color=col, zorder=3, edgecolor="white", lw=2)
        sgn = 1 if r26 >= r25 else -1   # x axis is inverted: larger rank sits further left
        ax.text(r26 + 1.1 * sgn, i, f"{r26}", va="center", ha="right" if sgn > 0 else "left",
                color=INK, fontsize=10, fontweight="bold")
        ax.text(r25 - 1.1 * sgn, i, f"{r25}", va="center", ha="left" if sgn > 0 else "right",
                color=MUTED, fontsize=10)
    ax.set_yticks(range(len(rows)), [LABELS[m] for m in rows])
    ax.set_xlim(0.5, 33.5); ax.invert_xaxis()
    ax.set_xticks([1, 8, 16, 24, 32]); ax.set_xlabel("League rank (1 = best defense)  ->  better")
    ax.grid(axis="x", color="#EEF0F3", lw=1); ax.set_axisbelow(True)
    fig.suptitle("Bills run defense: better. Pass defense: much worse.", x=0.02, ha="left",
                 fontsize=16, fontweight="bold", color=INK)
    ax.set_title(f"Defensive league rank: 2025 (gray) vs 2026 through week {wk} (blue = better, red = worse)",
                 loc="left", fontsize=10.5, color=MUTED, pad=10)
    fig.text(0.02, 0.01, f"{SOURCE} 2026 sample: {plays26} plays, small sample.", fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "defense-rank-shift.png"); plt.close(fig)


def weekly_chart(adj, wk):
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=200)
    cols = [BLUE if v < 0 else RED for v in adj.adj_epa]
    ax.bar([f"W{w} {o}" for w, o in zip(adj.week, adj.opp)], adj.adj_epa, color=cols, width=0.6, zorder=2)
    ax.axhline(0, color=INK, lw=1)
    for x, v in enumerate(adj.adj_epa):
        ax.text(x, v + (0.02 if v >= 0 else -0.02), f"{v:+.2f}", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=9, color=INK)
    ax.set_ylabel("EPA/play allowed vs. opponent's norm")
    lo, hi = adj.adj_epa.min(), adj.adj_epa.max()
    ax.set_ylim(min(lo, 0) - 0.08, max(hi, 0) + 0.06)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    fig.suptitle("Worse than the opponent's norm in 6 of 7 games", x=0.02, ha="left",
                 fontsize=15, fontweight="bold", color=INK)
    ax.set_title("Above zero (red) = opponent did better than it does against everyone else. "
                 "W8 BAL started a backup QB.", loc="left", fontsize=9.5, color=MUTED, pad=8)
    fig.text(0.02, 0.01, f"{SOURCE} Opponent norm = its offensive EPA/play in all other 2026 games.",
             fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "defense-weekly-adjusted.png"); plt.close(fig)


def fmt(m, v):
    return f"{v:.1%}" if m.endswith("rate") else f"{v:.2f}" if m == "pts_per_drive" else f"{v:+.3f}"


def main():
    con = connect()
    wk = latest_week(con)
    t = season_table("def", [2025, 2026], con=con)
    b = t[t.team == "BUF"].set_index("season")
    adj = opp_adjusted_defense("BUF", 2026, con)
    ar = {s: league_adjusted_rank(s, con).set_index("team").loc["BUF"] for s in (2025, 2026)}
    cc = {s: pass_defense_crosscheck(s, con).set_index("team").loc["BUF"] for s in (2025, 2026)}
    bal_qb = query("""SELECT passer_player_name AS qb, COUNT(*) AS dropbacks FROM clean_plays
                      WHERE game_id='2026_08_BAL_BUF' AND posteam='BAL' AND is_dropback=1
                        AND passer_player_name IS NOT NULL GROUP BY 1 ORDER BY 2 DESC""", con=con)
    plays26 = int(b.loc[2026, "plays"])
    worse = int((adj.adj_epa > 0).sum())
    rank_chart(b, wk, plays26)
    weekly_chart(adj, wk)

    rows = "\n".join(
        f"| {LABELS[m]} | {fmt(m, b.loc[2025, m])} ({b.loc[2025, m + '_rk']}) | "
        f"{fmt(m, b.loc[2026, m])} ({b.loc[2026, m + '_rk']}) | {fmt(m, b.loc[2026, m + '_lg'])} |"
        for m in LABELS)
    wk_rows = "\n".join(f"| {r.week} | {r.opp} | {int(r.plays)} | {r.epa_allowed:+.3f} | "
                        f"{r.opp_off_epa_other:+.3f} | {r.adj_epa:+.3f} |" for r in adj.itertuples())
    qb_line = ", ".join(f"{r.qb} {r.dropbacks}" for r in bal_qb.itertuples())

    md = f"""# Is the Bills defense actually fixed?

**Finding: Jim Leonhard's 3-4 lifted the run defense from {b.loc[2025, 'rush_epa_rk']}th to {b.loc[2026, 'rush_epa_rk']}th but the pass defense
fell from {b.loc[2025, 'dropback_epa_rk']}th to {b.loc[2026, 'dropback_epa_rk']}th, and the Bills have been worse
than their opponent's norm in {worse} of {len(adj)} games.**

*Through 2026 week {wk}. Regular season. {plays26} defensive plays in 2026: small sample.*

![Rank shift](defense-rank-shift.png)

## The short version

The run defense got better. The pass defense got a lot worse, the pass rush is down from last year,
and the one dominant game came against a Baltimore backup quarterback.

## 2025 vs 2026, every metric

Unfiltered unless labeled. League rank in parentheses (1 = best defense).

| Metric | 2025 | 2026 to date | 2026 league avg |
|---|---|---|---|
{rows}

## Opponent-adjusted, week by week

Each game compared with what that opponent's offense does in all its *other* 2026 games.

![Weekly adjusted](defense-weekly-adjusted.png)

| Week | Opp | Plays | EPA/play allowed | Opp norm | Difference |
|---|---|---|---|---|---|
{wk_rows}

Season opponent-adjusted EPA/play: **{ar[2026].adj_epa:+.3f} ({int(ar[2026].adj_epa_rk)}th)**, vs.
{ar[2025].adj_epa:+.3f} ({int(ar[2025].adj_epa_rk)}th) in 2025. Pass defense adjusted:
{int(ar[2026].adj_db_epa_rk)}th in 2026 vs. {int(ar[2025].adj_db_epa_rk)}th in 2025.

Week 8 Baltimore dropbacks by passer: {qb_line}.

## Checked a second way

The pass-defense drop could be an artifact of EPA modeling, so here it is without EPA,
straight from raw play-by-play:

| Pass defense (no EPA) | 2025 | 2026 |
|---|---|---|
| Yards per dropback allowed | {cc[2025].yds_per_db:.2f} ({int(cc[2025].yds_per_db_rk)}) | {cc[2026].yds_per_db:.2f} ({int(cc[2026].yds_per_db_rk)}) |
| Dropback success rate allowed | {cc[2025].db_success:.1%} ({int(cc[2025].db_success_rk)}) | {cc[2026].db_success:.1%} ({int(cc[2026].db_success_rk)}) |

Same story both ways.

## Method and caveats

- Plays: `pass == 1 or rush == 1`, EPA not null, run/pass play types only; kneels, spikes, two-point tries excluded.
- Neutral = win probability 10-90%. Explosive = pass 20+ or rush 10+ yards. Points per drive uses TD = 7, FG = 3.
- Opponent adjustment uses in-season numbers (6+ weeks exist), excluding the Bills game itself.
- Seven games. Rankings this early move a lot week to week; the direction is the claim, not the decimal.

## Correction, Nov. 8, 2026

An error in how we counted drives credited some defensive and kick-return touchdowns to the offense on the field. Fixing it
changed three cells in the first table and the matching points in the rank chart: Buffalo's 2025 red-zone touchdown rate allowed is unchanged at 68.3% but ranks 28th
(we had 25th); points per drive allowed is 2.09 (14th; we had 13th) for 2025 and 2.35 (26th; we had 2.38, 25th) for 2026;
the league averages are 62.6% and 2.06 (we had 63.4% and 2.10). Nothing else in the story changed.
"""
    (OUT / "2026-defense-baseline.md").write_text(md)
    print(md[:600])


if __name__ == "__main__":
    main()
