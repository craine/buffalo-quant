"""Week 9 post-game: Bills 23, Vikings 6 (MNF, Nov. 9, 2026). Grades our seven Ledger calls in plain English.

Writes reports/2026-wk09-postgame.md, two PNGs and a hero JSON. Every number is computed here.
Pinned: games through 2026 week 9 (THRU); the projections come from the published part 3 inputs (week 8).
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

OUT = ROOT / "reports"
SEASON, THRU, PRE_THRU = 2026, 9, 8
GAME = "2026_09_BUF_MIN"
SLUG = "2026-wk09-postgame"
SRC = "Source: nflverse play-by-play and schedules. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})
CALL_LABELS = {  # Ledger id -> plain-English call (same wording as part 3)
    "P0002": "Bills win", "P0003": "Bills score 20 or more", "P0004": "Vikings score 20 or more",
    "P0005": "Bills' pass plays gain points overall", "P0006": "Vikings' pass plays gain points overall, with Wentz",
    "P0007": "Bills' runs lose points overall", "P0008": "Vikings' runs lose points overall"}


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def name_of(pid):
    r = query("SELECT player_display_name FROM raw_player_week WHERE player_id = ? LIMIT 1", params=(pid,))
    return r.player_display_name.iloc[0] if len(r) else None


def main():
    # ---- the result and the pregame projections (same pinned inputs as part 3)
    s = query(f"SELECT away_score, home_score FROM raw_schedules WHERE game_id='{GAME}'").iloc[0]
    buf, mn = int(s.away_score), int(s.home_score)
    coef, res, _, summ = pm.backtest(test={2024: 99, 2025: 99, SEASON: PRE_THRU})
    g = pm._drives()
    r = pm.ratings(g, SEASON, PRE_THRU + 1)
    proj = {"BUF": pm.predict(coef, pm.raw_prediction(*r, "BUF", "MIN")[0], 0),
            "MIN": pm.predict(coef, pm.raw_prediction(*r, "MIN", "BUF")[0], 1)}
    rng = {t: proj[t] + np.quantile(res, [0.1, 0.9]) for t in proj}
    miss_min = mn - proj["MIN"]
    rare_train = float((res <= miss_min).mean())
    te = pm.build_frame([2024, 2025, SEASON], max_week={2024: 99, 2025: 99, SEASON: PRE_THRU})
    te["model"] = pm.predict(coef, te.raw, te.home)
    rare_test = float(((te.score - te.model) <= miss_min).mean())

    # ---- Ledger grades
    lp = _read(PRED_CSV, PRED_COLS)
    lg = _read(GRADE_CSV, GRADE_COLS)
    m = lp[lp.game_id == GAME].merge(lg, left_on="id", right_on="prediction_id")
    assert len(m) == 7, len(m)
    m["p"] = m.probability.astype(float)
    m["o"] = m.outcome.astype(int)
    m["hit"] = (m.p >= 0.5) == (m.o == 1)
    m["b"] = m.brier.astype(float)
    m["label"] = m.id.map(CALL_LABELS)
    week_brier, week_hits = m.b.mean(), int(m.hit.sum())
    allg = lp.merge(lg, left_on="id", right_on="prediction_id")
    all_hits = int(((allg.probability.astype(float) >= 0.5) == (allg.outcome.astype(int) == 1)).sum())
    all_brier = allg.brier.astype(float).mean()

    # ---- the passing games, the drives, the turnovers
    p = query(f"""SELECT p.play_id, p.qtr, p.posteam, p.qb_dropback, p.pass_attempt, p.sack, p.air_yards, p.epa,
                  p.interception, p.interception_player_id, p.fumble_lost, p.yards_gained, p.rush, p.qb_scramble, p.qb_kneel, p.complete_pass
                  FROM raw_pbp p WHERE p.game_id='{GAME}' AND p.epa IS NOT NULL AND COALESCE(p.two_point_attempt,0)=0
                  AND COALESCE(p.play_type,'') <> 'no_play'""")
    d = p[p.qb_dropback == 1].copy()
    d["att"] = (d.pass_attempt == 1) & (d.sack == 0)
    d["short"] = d.att & (d.air_yards < 20)
    q = {}
    for t in ("BUF", "MIN"):
        x = d[d.posteam == t]
        a = x[x.att]
        q[t] = dict(db=len(x), epa=x.epa.sum(), att=len(a), cmp=int(a.complete_pass.sum()), yds=int(a.yards_gained.sum()),
                    sacks=int(x.sack.sum()), ints=int(x.interception.sum()), n_short=int(x.short.sum()), short_epa=x[x.short].epa.sum())
    ru = p[(p.rush == 1) & (p.qb_scramble == 0) & (p.qb_kneel == 0)].groupby("posteam").agg(n=("epa", "size"), yds=("yards_gained", "sum"))
    to_min = int(p[p.posteam == "MIN"].interception.sum() + p[p.posteam == "MIN"].fumble_lost.sum())
    pickers = [name_of(i) for i in p[(p.posteam == "MIN") & (p.interception == 1)].interception_player_id]
    dv = game_values(SEASON, "dropback_epa", max_week=THRU)
    dv = dv[dv.side == "off"].copy()
    dv["rk"] = dv.v.rank(method="min")
    min_rank = int(dv[(dv.game_id == GAME) & (dv.team == "MIN")].rk.iloc[0])
    dr = query(f"SELECT game_id, week, posteam, defteam, points, result FROM clean_drives WHERE season={SEASON} AND season_type='REG' AND week<={THRU}")
    gd = dr[dr.game_id == GAME]
    drives = gd.groupby("posteam").agg(n=("points", "size"), pts=("points", "sum"))
    min_downs = int(((gd.posteam == "MIN") & (gd.result == "Turnover on downs")).sum())

    n_prior = ['zero','one','two','three','four','five','six','seven','eight'][dr[(dr.week <= PRE_THRU) & (dr.defteam == 'BUF')].game_id.nunique()]

    def def_rank(wk):
        x = dr[dr.week <= wk]
        a = x.groupby("defteam").points.agg(["sum", "size"])
        a["ppd"] = a["sum"] / a["size"]
        return a.loc["BUF", "ppd"], int(a.ppd.rank(method="min")["BUF"]), len(a), x.points.sum() / len(x)
    d8, d9 = def_rank(PRE_THRU), def_rank(THRU)
    nxt = query(f"""SELECT week, gameday, away_team, home_team FROM raw_schedules WHERE season={SEASON}
                    AND (home_team='BUF' OR away_team='BUF') AND week={THRU + 1}""").iloc[0]
    team_names = {"NYJ": "the Jets", "MIA": "Miami", "NE": "New England"}
    nxt_opp = nxt.home_team if nxt.away_team == "BUF" else nxt.away_team
    nxt_txt = (f"at {team_names.get(nxt_opp, nxt_opp)}" if nxt.away_team == "BUF" else f"home against {team_names.get(nxt_opp, nxt_opp)}")
    nxt_day = pd.Timestamp(nxt.gameday).strftime("%A, %b. %-d")

    # ---- chart 1: projected vs. final
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    for y, t, lab, col in ((1, "BUF", "Bills", BLUE), (0, "MIN", "Vikings", GRAY)):
        lo, hi = rng[t]
        ax.plot([lo, hi], [y, y], color=col, lw=10, alpha=0.25, solid_capstyle="round", zorder=1)
        ax.scatter([proj[t]], [y], s=150, facecolor="white", edgecolor=col, linewidth=2.2, zorder=3)
        final = buf if t == "BUF" else mn
        ax.scatter([final], [y], s=170, color=RED if t == "BUF" else INK, zorder=4, edgecolor="white", linewidth=1.5)
        ax.text(proj[t], y + 0.25, f"projected {proj[t]:.1f}", ha="center", fontsize=9.5, color=MUTED)
        ax.text(final, y - 0.32, f"final {final}", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_yticks([1, 0], ["Bills", "Vikings"], fontsize=11)
    ax.set_ylim(-0.7, 1.6); ax.set_xlim(0, 40)
    ax.set_xlabel("Points", fontsize=10, color=MUTED)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Bills: we said {proj['BUF']:.0f}, they scored {buf}. Vikings: we said {proj['MIN']:.0f}, they scored {mn}",
           "Open dot = our projection before kickoff. Solid dot = final score. Shaded bar = where we expected 8 games in 10 to land.",
           f"Points model {pm.VERSION}, data through 2026 week {PRE_THRU}, published and logged before kickoff.")
    fig.savefig(OUT / "wk09d-proj-vs-final.png"); plt.close(fig)

    # ---- chart 2: the scorecard
    order = ["P0002", "P0003", "P0004", "P0005", "P0006", "P0007", "P0008"]
    mm = m.set_index("id").loc[order]
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=200)
    ys = np.arange(len(mm))[::-1]
    for y, r_ in zip(ys, mm.itertuples()):
        ax.barh(y, r_.p, 0.6, color=BLUE if r_.hit else "#C9CDD4", zorder=2)
        ax.text(r_.p + 0.01, y, f"{r_.p:.0%}  {'HIT' if r_.hit else 'MISS'}", va="center", fontsize=10, fontweight="bold",
                color=INK if r_.hit else RED)
    ax.axvline(0.5, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.set_yticks(ys, mm.label, fontsize=10)
    ax.set_xlim(0, 1.05); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Our seven calls: {week_hits} right, {7 - week_hits} wrong",
           "Bar = the chance we gave before kickoff. Blue = it went our way; gray = it didn't.",
           "Every call was logged on the Ledger before kickoff and graded from the final play-by-play.")
    fig.savefig(OUT / "wk09d-scorecard.png"); plt.close(fig)

    def plain(team, metric, word):
        v = game_values(SEASON, metric, max_week=THRU)
        x = v[(v.game_id == GAME) & (v.team == team) & (v.side == "off")].iloc[0]
        amt = abs(x.num)
        how = "gained" if x.num > 0 else "lost"
        return f"{how} {amt:.3f} points over {int(x.den)} {word}" if amt < 0.5 else f"{how} about {amt:.0f} points over {int(x.den)} {word}"
    happened = {"P0002": f"Bills {buf}, Vikings {mn}", "P0003": f"Bills {buf}", "P0004": f"Vikings {mn}",
                "P0005": plain("BUF", "dropback_epa", "pass plays"), "P0006": plain("MIN", "dropback_epa", "pass plays"),
                "P0007": plain("BUF", "rush_epa", "runs"), "P0008": plain("MIN", "rush_epa", "runs")}
    rows = "\n".join(f"| {r_.label} | {r_.p:.0%} | {happened[i].capitalize() if i > 'P0004' else happened[i]} | **{'Hit' if r_.hit else 'Miss'}** |"
                     for i, r_ in zip(mm.index, mm.itertuples()))
    p5 = mm.loc["P0005"]
    b_db, m_db = q["BUF"], q["MIN"]
    pick_txt = " and ".join(x for x in pickers if x) if all(pickers) else f"{len(pickers)} interceptions"
    md = f"""# Bills {buf}, Vikings {mn}: we nailed Buffalo's half and missed Minnesota's

**Finding: Our model projected the Bills to score {proj['BUF']:.1f} points. They scored {buf}. It projected the Vikings to score {proj['MIN']:.1f}. They
scored {mn}, a miss that big happened only about {round(rare_test * 100)} times in 100 when we tested the model. On the Ledger, {week_hits} of our 7 calls
were right, including the one that matters most: the Bills win. Both misses came from Minnesota's passing game, which had one of the worst nights
of any team this season.**

*Bills at Vikings, Monday Night Football, Nov. 9. Our prediction ran Monday morning ([part 3](bills-vikings-prediction.html)) and every call
was logged on the [Ledger](../ledger.html) before kickoff. Here's how they did.*

![Projected vs. final](wk09d-proj-vs-final.png)

## The scorecard

| Call | Our chance | What happened | Result |
|---|---|---|---|
{rows}

![Scorecard](wk09d-scorecard.png)

**How we grade.** A call is a hit when the side we gave more than 50% happens. We also score every call by how far our chance was from what
happened, squared, so a confident miss costs more than a timid one. Lower is better. This week's calls scored {week_brier:.2f}; guessing 50/50 on
every one would have scored 0.25. Across all {len(allg)} calls on the Ledger so far, including last week's Sabres call, we're {all_hits} for
{len(allg)} with a score of {all_brier:.2f}. Small numbers, but that's the point of keeping the record: it adds up.

**One hit we're not bragging about.** The Bills' pass plays had to gain points overall for that call to hit. Over {b_db['db']} dropbacks they gained
{b_db['epa']:.3f} points, about as close to zero as it gets. By the rule we set before kickoff, that's a hit, the same way we'd have counted a miss
by that margin. Fairly, it was a coin landing on its edge.

## Buffalo: right on the number

The Bills scored {buf} on {int(drives.loc['BUF', 'n'])} drives, about {drives.loc['BUF', 'pts'] / drives.loc['BUF', 'n']:.1f} points a drive, less than the
{pm.raw_prediction(*r, 'BUF', 'MIN')[1]:.1f} our model expected, but over more drives than the {pm.raw_prediction(*r, 'BUF', 'MIN')[2]:.0f} it planned on. It came out to\nalmost exactly the projection.

Part 3 said this was the best offense in football against the best defense at stopping it, and that the two would mostly cancel out.
That's what happened: Josh Allen went {b_db['cmp']} of {b_db['att']} for {b_db['yds']} yards with {b_db['ints']} interception and was sacked
{b_db['sacks']} times, and Buffalo's pass plays finished almost exactly even. The run game did the steady work: {int(ru.loc['BUF', 'n'])} designed runs
for {int(ru.loc['BUF', 'yds'])} yards.

## Minnesota: what we missed

Carson Wentz went {m_db['cmp']} of {m_db['att']} for {m_db['yds']} yards, threw {m_db['ints']} interceptions ({pick_txt}) and was sacked
{m_db['sacks']} times. Minnesota's pass plays cost it about {abs(m_db['epa']):.0f} points of field position over {m_db['db']} dropbacks, the
{min_rank}{'rd' if min_rank == 3 else 'th'}-worst passing game by any team in {len(dv)} games this season. The Vikings turned it over {to_min} times and
turned it over on downs {min_downs} more, on their way to {mn} points.

**The weak spot that wasn't.** Part 1 said short throws were where the Bills defense was most beatable this season. Monday, Minnesota's
{m_db['n_short']} short throws cost it {abs(m_db['short_epa']):.0f} points. One game doesn't erase {n_prior}, but the Bills' defense closed the gap we
pointed at, and its points allowed per drive went from {d8[1]}{'th' if d8[1] > 3 else ''} in the league to {d9[1]}{'th' if d9[1] > 3 else ''} in one night
({d8[0]:.2f} to {d9[0]:.2f}, with the league at {d9[3]:.2f}).

**Why our Vikings calls missed.** Our model had Minnesota around {proj['MIN']:.0f} points, mostly from Kyler Murray's games and last season, with
a typical range of {rng['MIN'][0]:.0f} to {rng['MIN'][1]:.0f}. {['Zero','Three','Six','Seven'][[0,3,6,7].index(mn)] if mn in (0,3,6,7) else mn} was below that range: in testing, only about {round(rare_test * 100)} in 100 teams fell
that far short of their projection. And the pass call ({mm.loc['P0006'].p:.0%}) was built on the one piece we told you we hadn't tested: swapping in Wentz's own
numbers. One game can't tell us whether that swap is wrong. It does tell us not to use it on the Ledger again until we've tested it, so we won't.

## What it means

- **The Bills' defense might be turning a corner, or might have met a bad night.** Its numbers jumped in one game; one game is a small sample.
  We'll know more after the next two.
- **Next:** the Bills play {nxt_txt} on {nxt_day}. Our prediction and Ledger calls come before kickoff.
- **The record is the point.** {all_hits} of {len(allg)} so far. Every call stays up, hit or miss.

## For the stat-heads

- Points model {pm.VERSION}, inputs pinned to 2026 week {PRE_THRU} (as published). Projections BUF {proj['BUF']:.2f}, MIN {proj['MIN']:.2f};
  80% ranges from training residuals. MIN residual {miss_min:+.1f}; share of residuals at or below it: training {rare_train:.3f}, out of sample
  (2024-26, n={len(te)}) {rare_test:.3f}.
- Grades: P0002-P0004 from raw_schedules; P0005-P0008 from clean_team_week (model_v01.game_values, offense side), the same definitions the
  models used. BUF EPA/dropback {p5.actual_value.split()[-1]} ({b_db['epa']:+.4f} total over {b_db['db']}). Brier this week {week_brier:.4f}; all
  graded calls {all_brier:.4f} (n={len(allg)}).
- MIN EPA per dropback ranks {min_rank} of {len(dv)} 2026 team-games (1 = worst). Short = pass attempts with air yards under 20.
- BUF points allowed per drive, regular season through week {PRE_THRU}: {d8[0]:.3f} ({d8[1]} of {d8[2]}); through week {THRU}: {d9[0]:.3f} ({d9[1]} of {d9[2]}).
- FTN charting (blitz counts) for this game wasn't published yet when we ran this, so part 2's blitz angle isn't graded here.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Monday night, graded",
        "big": [[buf, f"Bills (we said {proj['BUF']:.1f})"], [mn, f"Vikings (we said {proj['MIN']:.1f})"]],
        "note": f"{week_hits} of 7 Ledger calls right, including Bills win. Both misses came from Minnesota's passing game.",
        "explainer": {"kicker": "Receipts", "title": "Every call graded, hit or miss.",
                      "text": "Our calls' score this week, vs. guessing 50/50 on every one (lower is better):",
                      "fmt": "score", "bars": [["Our calls", round(float(week_brier), 2)], ["50/50 guess", 0.25]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
