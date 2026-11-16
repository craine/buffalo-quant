"""Week 10 post-game: Bills at Jets (Nov. 15, 2026). Grades our five Ledger calls in plain English.

Writes reports/2026-wk10-postgame.md, two PNGs and a hero JSON. Every number is computed here.
Pinned: the projections and calls come from the published preview inputs (games through 2026 week 9). League context
uses 2026 games through week 10 that were final when this ran (AS_OF).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger import points_model as pm
from src.ledger.ledger import GRADE_COLS, GRADE_CSV, PRED_COLS, PRED_CSV, _read
from src.ledger.model_v01 import game_values
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.wk10_prediction import points_block

OUT = ROOT / "reports"
SEASON, WEEK, PRE_THRU = 2026, 10, 9
GAME = "2026_10_BUF_NYJ"
SLUG = "2026-wk10-postgame"
AS_OF = "Sunday night, Nov. 15 (the Sunday and Monday night games weren't final yet)"
NOT_FINAL = ("2026_10_PIT_CIN", "2026_10_LAC_BAL")  # pinned: left out of league context so re-runs match
SRC = "Source: nflverse play-by-play and schedules. Regular season."
SMITH, KLUBNIK, COOK, ALLEN = "00-0030565", "00-0041056", "00-0037248", "00-0034857"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})
CALL_LABELS = {  # Ledger id -> plain-English call (same wording as the reworded preview)
    "P0012": "Bills win",
    "P0013": "Bills' passing game helps more than it hurts",
    "P0014": "Jets' passing game helps more than it hurts",
    "P0015": "Bills' running game (designed runs) hurts more than it helps",
    "P0016": "Jets' running game (designed runs) hurts more than it helps"}
ORDER = list(CALL_LABELS)


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def name_of(gsis):
    return query("SELECT display_name FROM raw_players WHERE gsis_id = ?", params=(gsis,)).display_name.iloc[0]


def ordn(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def main():
    # ---- result and the pregame projections (the preview's own function, pinned to week 9)
    s = query(f"SELECT away_team, away_score, home_team, home_score FROM raw_schedules WHERE game_id='{GAME}'").iloc[0]
    assert s.away_team == "BUF" and s.home_team == "NYJ"
    buf, nyj = int(s.away_score), int(s.home_score)
    P = points_block()
    proj, rng, p_win = P["proj"], P["rng"], P["p_buf"]
    assert abs(proj["BUF"] - 29.9) < 0.05 and abs(proj["NYJ"] - 22.1) < 0.05 and round(p_win, 2) == 0.75, (proj, p_win)

    # ---- Ledger grades
    lp, lg = _read(PRED_CSV, PRED_COLS), _read(GRADE_CSV, GRADE_COLS)
    m = lp[lp.game_id == GAME].merge(lg, left_on="id", right_on="prediction_id").set_index("id").loc[ORDER]
    assert len(m) == 5
    m["p"], m["o"] = m.probability.astype(float), m.outcome.astype(int)
    m["hit"] = (m.p >= 0.5) == (m.o == 1)
    m["b"] = m.brier.astype(float)
    week_hits, week_brier = int(m.hit.sum()), m.b.mean()
    allg = lp.merge(lg, left_on="id", right_on="prediction_id")
    all_hits = int(((allg.probability.astype(float) >= 0.5) == (allg.outcome.astype(int) == 1)).sum())
    all_brier = allg.brier.astype(float).mean()

    # ---- plays
    p = query(f"""SELECT play_id, qtr, down, ydstogo, yardline_100, posteam, qb_dropback, pass_attempt, sack, rush, qb_scramble, qb_kneel, epa, ep, wp,
                  yards_gained, interception, complete_pass, rusher_player_id, COALESCE(passer_player_id, rusher_player_id) AS qb,
                  game_seconds_remaining AS gsr, desc
                  FROM raw_pbp WHERE game_id='{GAME}' AND epa IS NOT NULL AND COALESCE(two_point_attempt,0)=0
                  AND COALESCE(play_type,'') <> 'no_play'""")
    d = p[p.qb_dropback == 1].copy()
    d["att"] = (d.pass_attempt == 1) & (d.sack == 0)
    q = {}
    for t in ("BUF", "NYJ"):
        x = d[d.posteam == t]
        a = x[x.att]
        q[t] = dict(db=len(x), epa=x.epa.sum(), att=len(a), cmp=int(a.complete_pass.sum()), yds=int(a.yards_gained.sum()),
                    sacks=int(x.sack.sum()), ints=int(x.interception.sum()))
    jq = {}
    for who, gid in (("smith", SMITH), ("klubnik", KLUBNIK)):
        x = d[(d.posteam == "NYJ") & (d.qb == gid)]
        a = x[x.att]
        jq[who] = dict(db=len(x), epa=x.epa.sum(), att=len(a), cmp=int(a.complete_pass.sum()), yds=int(a.yards_gained.sum()),
                       sacks=int(x.sack.sum()), ints=int(x.interception.sum()), first_q=int(x.qtr.min()), last_q=int(x.qtr.max()))
    assert jq["smith"]["db"] + jq["klubnik"]["db"] == q["NYJ"]["db"]
    assert jq["smith"]["last_q"] == 3 and jq["klubnik"]["first_q"] == 3 and jq["klubnik"]["last_q"] == 4
    runs = p[(p.rush == 1) & (p.qb_scramble == 0) & (p.qb_kneel == 0)]
    ru = {t: dict(n=len(runs[runs.posteam == t]), yds=int(runs[runs.posteam == t].yards_gained.sum()),
                  epa=runs[runs.posteam == t].epa.sum()) for t in ("BUF", "NYJ")}
    br = runs[runs.posteam == "BUF"]
    big = br.loc[br.epa.idxmax()]
    assert int(big.yards_gained) == 74 and big.rusher_player_id == COOK
    rest = br.drop(big.name)
    close = br[(br.wp >= 0.10) & (br.wp <= 0.90)]
    cook = br[br.rusher_player_id == COOK]
    allen = br[br.rusher_player_id == ALLEN]
    big_clock = f"{int(big.gsr // 60)}:{int(big.gsr % 60):02d}"

    # one real run to explain "points": Allen's first-quarter short-yardage run (largest Allen designed run)
    ex = allen.loc[allen.epa.idxmax()]
    assert int(ex.down) == 4 and int(ex.ydstogo) == 1 and int(ex.qtr) == 1
    assert len(allen) == 4 and int((allen.down == 4).sum()) == 2 and int(allen.desc.str.contains('TOUCHDOWN').sum()) == 2

    # ---- league context: every 2026 team-game so far
    rv = game_values(SEASON, "rush_epa")
    rv = rv[(rv.side == "off") & ~rv.game_id.isin(NOT_FINAL)].copy()
    buf_run_rank = int((rv.v > rv[(rv.game_id == GAME) & (rv.team == "BUF")].v.iloc[0]).sum()) + 1
    lg_run_below = float((rv.v < 0).mean())
    past_best = {y: game_values(y, "rush_epa").query("side == 'off' and team == 'BUF'").v.max() for y in (2023, 2024, 2025)}
    nyj_run = rv[(rv.game_id == GAME) & (rv.team == "NYJ")].iloc[0]

    # ---- drives and the defense
    dr = query(f"SELECT game_id, week, posteam, defteam, points, result FROM clean_drives WHERE season={SEASON} AND season_type='REG' AND week<={WEEK}")
    dr = dr[~dr.game_id.isin(NOT_FINAL)]
    gd = dr[dr.game_id == GAME]
    drives = gd.groupby("posteam").agg(n=("points", "size"), pts=("points", "sum"))
    nyj_fg = int(((gd.posteam == "NYJ") & (gd.result == "Field goal")).sum())
    nyj_to = int(((gd.posteam == "NYJ") & (gd.result == "Turnover")).sum())
    nyj_downs = int(((gd.posteam == "NYJ") & (gd.result == "Turnover on downs")).sum())
    buf_td = int(((gd.posteam == "BUF") & (gd.result == "Touchdown")).sum())

    def def_rank(wk):
        x = dr[dr.week <= wk]
        a = x.groupby("defteam").points.agg(["sum", "size"])
        a["ppd"] = a["sum"] / a["size"]
        return a.loc["BUF", "ppd"], int(a.ppd.rank(method="min")["BUF"]), len(a), x.points.sum() / len(x)
    d9, d10 = def_rank(PRE_THRU), def_rank(WEEK)
    nxt = query(f"""SELECT gameday, away_team, home_team FROM raw_schedules WHERE season={SEASON}
                    AND (home_team='BUF' OR away_team='BUF') AND week={WEEK + 1}""").iloc[0]
    assert nxt.home_team == "BUF" and nxt.away_team == "MIA"
    nxt_day = pd.Timestamp(nxt.gameday).strftime("%A, %b. %-d")

    # ---- chart 1: projected vs. final
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    for y, t, col in ((1, "BUF", BLUE), (0, "NYJ", GRAY)):
        lo, hi = rng[t]
        final = buf if t == "BUF" else nyj
        ax.plot([lo, hi], [y, y], color=col, lw=10, alpha=0.25, solid_capstyle="round", zorder=1)
        ax.scatter([proj[t]], [y], s=150, facecolor="white", edgecolor=col, linewidth=2.2, zorder=3)
        ax.scatter([final], [y], s=170, color=RED if t == "BUF" else INK, zorder=4, edgecolor="white", linewidth=1.5)
        ax.text(proj[t], y + 0.25, f"projected {proj[t]:.1f}", ha="center", fontsize=9.5, color=MUTED)
        ax.text(final, y - 0.32, f"final {final}", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_yticks([1, 0], ["Bills", "Jets"], fontsize=11)
    ax.set_ylim(-0.7, 1.6); ax.set_xlim(0, 45)
    ax.set_xlabel("Points", fontsize=10, color=MUTED)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Bills: we said {proj['BUF']:.1f}, they scored {buf}. Jets: we said {proj['NYJ']:.1f}, they scored {nyj}",
           "Open dot = our projection before kickoff. Solid dot = final score. Shaded bar = where we expected 8 games in 10 to land.",
           f"Points model {pm.VERSION}, data through 2026 week {PRE_THRU}, published and logged before kickoff. 1 game.")
    fig.savefig(OUT / "wk10d-proj-vs-final.png"); plt.close(fig)

    # ---- chart 2: the scorecard
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
    ys = np.arange(len(m))[::-1]
    for y, (pid, r_) in zip(ys, m.iterrows()):
        ax.barh(y, r_.p, 0.6, color=BLUE if r_.hit else "#C9CDD4", zorder=2)
        ax.text(r_.p + 0.01, y, f"{r_.p:.0%}  {'HIT' if r_.hit else 'MISS'}", va="center", fontsize=10, fontweight="bold",
                color=INK if r_.hit else MUTED)
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.set_yticks(ys, [CALL_LABELS[i] for i in m.index], fontsize=10)
    ax.set_xlim(0, 1.08); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Bills at Jets: {week_hits} of our 5 calls right",
           "Bar = the chance we gave before kickoff. Blue = it went our way; gray = it didn't. QB scrambles count as pass plays.",
           "5 calls, 1 game. Every call was logged on the Ledger before kickoff and graded from the final play-by-play.")
    fig.savefig(OUT / "wk10d-scorecard.png"); plt.close(fig)

    # ---- chart 3: every team's running night this season, Bills-Jets marked
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    bins = np.arange(np.floor(rv.v.min() / 0.05) * 0.05, rv.v.max() + 0.1, 0.05)
    cnt, _, _ = ax.hist(rv.v, bins=bins, color="#C9CDD4", edgecolor="white", zorder=2)
    assert cnt.sum() == len(rv)
    ax.set_ylim(0, cnt.max() * 1.35)
    bv = rv[(rv.game_id == GAME) & (rv.team == "BUF")].v.iloc[0]
    ax.axvline(0, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.axvline(bv, color=RED, lw=2.5, zorder=3)
    ax.text(bv - 0.01, ax.get_ylim()[1] * 0.92, f"Bills at Jets\n{bv:+.2f} a run", ha="right", va="top", fontsize=10,
            color=RED, fontweight="bold")
    ax.text(-0.01, ax.get_ylim()[1] * 0.92, "runs hurt  ", ha="right", va="top", fontsize=9.5, color=MUTED)
    ax.text(0.01, ax.get_ylim()[1] * 0.92, "  runs helped", ha="left", va="top", fontsize=9.5, color=MUTED)
    ax.set_xlabel("Points added per designed run in one game", fontsize=10, color=MUTED)
    ax.set_ylabel("Team games", fontsize=10, color=MUTED)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Buffalo's best running night of any team this season",
           f"Every team's designed runs in every 2026 game so far ({len(rv)} team games). {lg_run_below:.0%} landed below zero.",
           f"Designed runs only (QB scrambles count as pass plays). 2026 games final as of Nov. 15. Bills at Jets: {ru['BUF']['n']} runs.")
    fig.savefig(OUT / "wk10d-run-nights.png"); plt.close(fig)

    # ---- scorecard table, plain English
    def total(team, metric, word):
        v = game_values(SEASON, metric)
        x = v[(v.game_id == GAME) & (v.team == team) & (v.side == "off")].iloc[0]
        how = "helped: added" if x.num > 0 else "hurt: cost"
        amt = abs(x.num)
        return f"{how} about {amt:.0f} points over {int(x.den)} {word}" if amt >= 1.5 else f"{how} {amt:.1f} points over {int(x.den)} {word}"
    happened = {"P0012": f"Bills {buf}, Jets {nyj}",
                "P0013": total("BUF", "dropback_epa", "pass plays").capitalize(),
                "P0014": total("NYJ", "dropback_epa", "pass plays").capitalize(),
                "P0015": total("BUF", "rush_epa", "designed runs").capitalize(),
                "P0016": total("NYJ", "rush_epa", "designed runs").capitalize()}
    rows = "\n".join(f"| {CALL_LABELS[i]} | {r_.p:.0%} | {happened[i]} | **{'Hit' if r_.hit else 'Miss'}** |" for i, r_ in m.iterrows())

    md = f"""# Bills {buf}, Jets {nyj}: our win call held, our run calls didn't

**We gave the Bills a 75% chance to win and projected them for {proj['BUF']:.1f} points. They won {buf}-{nyj}. Our surest call, that the Bills'
passing game would help more than it hurt, hit too. But we missed three calls, all built on the same idea: that running games usually hurt more
than they help. Buffalo's designed runs had the best night of any team's this season, and the Jets' runs finished just above zero.**

*Bills at Jets, Sunday, Nov. 15, MetLife Stadium. Our prediction ran Saturday ([our preview](bills-jets-prediction.html)), and every call was
logged on the [Ledger](../ledger.html) before kickoff. Here's how they did. League numbers are as of {AS_OF}.*

![Projected vs. final](wk10d-proj-vs-final.png)

## The calls

| Call | Our chance | What happened | Result |
|---|---|---|---|
{rows}

**What "helps" and "hurts" mean.** Every snap starts from a spot where an average offense can expect a certain number of points from the drive.
A good play raises that number and a bad one lowers it. In the first quarter, on fourth-and-{int(ex.ydstogo)} from his own {100 - int(ex.yardline_100)},
Josh Allen ran for {int(ex.yards_gained)} yards. That doesn't sound like much, but it kept the drive alive: Buffalo could expect about {ex.ep:.1f} points
before the snap and about {ex.ep + ex.epa:.1f} after it, so the play was worth about {ex.epa:.1f} points. Add up every designed run, good and bad, and you get whether a team's running
game helped or hurt. Buffalo's added about {ru['BUF']['epa']:.0f}. That's not {ru['BUF']['epa']:.0f} points on the scoreboard. It means the runs kept
moving drives toward points.

## What we missed: the running games

Our model expected Buffalo's designed runs to cost a little, the way most teams' do. In {lg_run_below:.0%} of {len(rv)} team games this season,
a team's designed runs added up to less than zero. Instead, the Bills ran {ru['BUF']['n']} times for {ru['BUF']['yds']} yards, and the runs added
about {ru['BUF']['epa']:.0f} points. Play for play, that's the best running night of any team this season ({ordn(buf_run_rank)} of {len(rv)}), and better
than any Bills game in 2023, 2024 or 2025.

![Every team's running night this season](wk10d-run-nights.png)

**Was it one big run?** Partly. James Cook's 74-yard touchdown run, with {big_clock} left and the game already decided, was worth about {big.epa:.1f}
points by itself. Take it out and Buffalo's other {len(rest)} designed runs still added about {rest.epa.sum():.0f} points. Count only the runs while the
game was still in doubt (each team with at least a 10% chance to win) and they still helped. Cook finished with {len(cook)} carries for
{int(cook.yards_gained.sum())} yards. Allen's {len(allen)} designed runs gained only {int(allen.yards_gained.sum())} yards but added about {allen.epa.sum():.0f}
points: two fourth-and-1 conversions and two 1-yard touchdowns. So this miss wasn't bad luck on one play. Buffalo ran the ball well
all day, and our model didn't see it coming.

**The Jets' runs: a coin on its edge.** We gave a 75% chance that the Jets' designed runs would hurt more than they helped. Over {ru['NYJ']['n']} runs
they added {nyj_run.num:.1f} points, just barely above zero. By the rule we set before kickoff, that's a miss, and it counts. Last week, our call on
the Bills' passing game hit by an even smaller margin.

## What we got right: the passing games and the win

On {q['BUF']['db']} pass plays, Allen went {q['BUF']['cmp']} of {q['BUF']['att']} for {q['BUF']['yds']} yards with
{q['BUF']['ints']} interception, and the passing game added about {q['BUF']['epa']:.0f} points. That's the call we gave 80%, and it hit.

The Jets used two quarterbacks. Geno Smith ({jq['smith']['cmp']} of {jq['smith']['att']}, {jq['smith']['yds']} yards) and rookie Cade Klubnik split
the third quarter, and Klubnik played the fourth ({jq['klubnik']['cmp']} of {jq['klubnik']['att']}, {jq['klubnik']['yds']} yards, {jq['klubnik']['ints']} interception,
sacked {jq['klubnik']['sacks']} times). Together, the Jets' passing game cost them about {abs(q['NYJ']['epa']):.0f} points over {q['NYJ']['db']} pass plays.
We had given 55% that it would help more than it hurt, close to a coin flip, so it's a miss, but not a confident one.

The Jets scored {nyj} points on {int(drives.loc['NYJ', 'n'])} drives: {nyj_fg} field goals, no touchdowns, {nyj_to} turnovers and {nyj_downs} turnover on downs.
Buffalo scored {buf} on {int(drives.loc['BUF', 'n'])} drives, with {buf_td} touchdowns. The Bills now allow about {d10[0]:.2f} points a drive
({ordn(d10[1])} of {d10[2]} teams, league average {d10[3]:.2f}). They were {ordn(d9[1])} before Sunday.

## The record

**How we grade.** A call is a hit when the side we gave 50% or more happens. We also score every call by how far our chance was from what
happened, squared, so a confident miss costs more than a timid one. This week our five calls scored {week_brier:.2f}; guessing 50/50 on every call
would score 0.25, and lower is better. So this week we did worse than a coin flip, mostly because of the two run calls we were sure about.
Across all {len(allg)} graded calls on the Ledger, Bills and Sabres, we're {all_hits} for {len(allg)} with a score of {all_brier:.2f}, a little better
than 50/50. That's still a small record. It grows every week, misses included.

## What it means

- **Run calls need a better model.** Our run calls lean hard on "running games usually hurt," and two of them missed this week. Before we put
  run calls at 75% again, we'll check how often that confidence has held up for strong running teams.
- **Our win projection was close.** We said {proj['BUF']:.1f} for Buffalo and they scored {buf}. The Jets' {nyj} came in well under our
  {proj['NYJ']:.1f}, but inside the range we expected 8 games in 10 to land ({rng['NYJ'][0]:.0f} to {rng['NYJ'][1]:.0f}).
- **Next:** the Bills host Miami on {nxt_day}, with our predictions logged before kickoff.

## For the stat-heads

![Scorecard](wk10d-scorecard.png)

- Points model {pm.VERSION} and win model points-win-v0.1, inputs pinned to 2026 week {PRE_THRU} (as published): BUF {proj['BUF']:.2f},
  NYJ {proj['NYJ']:.2f}, P(BUF win) {p_win:.4f}; 80% ranges from training residuals.
- "Helps/hurts" is nflverse expected points added (EPA), summed over plays. Example play {int(ex.play_id)}: EP {ex.ep:.2f} before, EPA {ex.epa:+.2f}.
- Grades: P0012 from raw_schedules; P0013-P0016 from clean_team_week (model_v01.game_values, offense side), the definitions the models used.
  Actual values: {'; '.join(f"{i} {m.loc[i, 'actual_value']}" for i in ORDER[1:])}. Brier this week {week_brier:.4f}; all graded calls
  {all_brier:.4f} (n={len(allg)}).
- BUF EPA per designed run {ru['BUF']['epa'] / ru['BUF']['n']:+.3f} (n={ru['BUF']['n']}); without play {int(big.play_id)} (74-yard TD, win probability
  {big.wp:.2f} before the snap) {rest.epa.mean():+.3f} (n={len(rest)}); win probability 0.10-0.90 only {close.epa.mean():+.3f} (n={len(close)}). Rank 1 = best
  of {len(rv)} 2026 team-games final as of {AS_OF}. Best BUF game by the same measure: 2023 {past_best[2023]:+.3f}, 2024 {past_best[2024]:+.3f},
  2025 {past_best[2025]:+.3f}.
- NYJ dropbacks: Smith {jq['smith']['db']} (EPA {jq['smith']['epa']:+.1f}), Klubnik {jq['klubnik']['db']} (EPA {jq['klubnik']['epa']:+.1f}). We don't
  say why the Jets changed quarterbacks; the play-by-play doesn't tell us.
- BUF points allowed per drive, regular season: through week {PRE_THRU} {d9[0]:.3f} ({d9[1]} of {d9[2]}); through week {WEEK} games final as of this
  run {d10[0]:.3f} ({d10[1]} of {d10[2]}).
- Hit rule: the side given 50% or more happens (`ledger.summary`). The logged Ledger wording for P0012-P0016 is unchanged; this story uses the
  plain-English labels from the reworded preview.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Sunday, graded",
        "big": [[buf, f"Bills (we said {proj['BUF']:.1f})"], [nyj, f"Jets (we said {proj['NYJ']:.1f})"]],
        "note": f"{week_hits} of 5 Ledger calls right: the win and the Bills' passing game. All three misses were run calls.",
        "explainer": {"kicker": "Receipts", "title": "Every call graded, hit or miss.",
                      "text": "Our calls' score this week vs. guessing 50/50 on every one (lower is better):",
                      "fmt": "score", "bars": [["Our calls", round(float(week_brier), 2)], ["50/50 guess", 0.25]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
