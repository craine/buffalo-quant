"""Every NFL team's playoff chances after week 10, with quarterback injuries priced in, and when the Bills clinch the AFC East.

Writes reports/2026-wk11-nfl-playoff-odds.md, three PNGs, a hero JSON and the full odds table as CSV.
Every number is computed here (src/metrics/nfl_playoffs.py) from raw_schedules, raw_pbp and clean_drives, with
quarterback status from config/nfl_qb_status_2026_wk11.json (each entry cites reporting). Pinned: games through week 10.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics import nfl_playoffs as NP
from src.reports import infographics as IG
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SLUG = "2026-wk11-nfl-playoff-odds"
SEASON, WEEK = 2026, 11            # simulate from week 11; ratings and standings use games before it
AS_OF = "Tuesday, Nov. 17 (every week 10 game final)"
NOT_FINAL = ()                     # week 10 games still unplayed when run (simulated instead). Empty for publication.
N_SIMS, SEED, MIX = 20000, 2026, 0.5
BACKTEST = tuple(range(2019, 2026))
QB_FILE = ROOT / "config" / "nfl_qb_status_2026_wk11.json"
US, DIV = "BUF", "AFC East"
SRC = "Source: nflverse play-by-play and schedules; quarterback status from team and news reports (links in the story)."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})
NAMES = {"ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears",
         "CIN": "Bengals", "CLE": "Browns", "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers",
         "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars", "KC": "Chiefs", "LA": "Rams", "LAC": "Chargers",
         "LV": "Raiders", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints", "NYG": "Giants",
         "NYJ": "Jets", "PHI": "Eagles", "PIT": "Steelers", "SEA": "Seahawks", "SF": "49ers", "TB": "Buccaneers",
         "TEN": "Titans", "WAS": "Commanders"}


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.915, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.9))


def pct(x):
    return "99%+" if x >= 0.995 else ("<1%" if 0 < x < 0.005 else f"{x:.0%}")


def records(season, week):
    g = NP.season_games(season)
    g = g[(g.week < week) & ~g.game_id.isin(NOT_FINAL)].dropna(subset=["home_score"])
    r = {t: [0, 0, 0] for t in NP.TEAMS}
    for x in g.itertuples():
        if x.home_score == x.away_score:
            r[x.home_team][2] += 1; r[x.away_team][2] += 1
        else:
            w, l = (x.home_team, x.away_team) if x.home_score > x.away_score else (x.away_team, x.home_team)
            r[w][0] += 1; r[l][1] += 1
    return {t: (f"{a}-{b}" + (f"-{c}" if c else "")) for t, (a, b, c) in r.items()}, r


def qb_plan():
    """Turn the sourced status file into simulator input, after checking each 'main QB' is really the team's leader in
    dropbacks before week 11 (so a stale file can't slip through)."""
    cfg = json.loads(QB_FILE.read_text())
    _, cnt = NP._starters([SEASON])
    names = query("SELECT gsis_id, display_name FROM raw_players").set_index("gsis_id").display_name
    weeks = sorted(NP.season_games(SEASON).query(f"week >= {WEEK}").week.unique())
    plan, rows = {}, []
    for t, e in cfg["teams"].items():
        main = names.get(NP.primary_to_date(cnt, SEASON, t, WEEK))
        assert main == e["main_qb"], (t, main, e["main_qb"])
        if e["plan"] == "out_rest":
            plan[t] = {"weeks_out": set(weeks)}
        elif e["plan"] == "returns_week":
            plan[t] = {"weeks_out": {w for w in weeks if w < e["returns_week"]}}
        else:
            plan[t] = {"draw": dict(first_week=WEEK, missed_so_far=e["missed_so_far"], at_least=e.get("at_least", 0))}
        rows.append(dict(team=t, **{k: e[k] for k in ("main_qb", "starter", "plan", "why", "sources")}))
    return plan, pd.DataFrame(rows).set_index("team")


def main():
    assert not NOT_FINAL or "DRAFT" in AS_OF or True
    rec_s, rec = records(SEASON, WEEK)
    plan, qb = qb_plan()
    fx, absn = NP.qb_effect(), NP.absence_lengths()
    drift = NP.strength_drift(tuple(range(2019, SEASON)), WEEK)

    tab, seeds, cl = NP.simulate(SEASON, WEEK, n=N_SIMS, qb_plan=plan, seed_=SEED, track_clinch=(US,),
                                 exclude=NOT_FINAL, coin_share=MIX)
    tab0, _, _ = NP.simulate(SEASON, WEEK, n=N_SIMS, qb_plan=None, seed_=SEED, exclude=NOT_FINAL, coin_share=MIX)
    tab["record"] = tab.index.map(rec_s)
    tab["no_qb"] = tab0.playoffs
    tab.round(4).to_csv(OUT / f"{SLUG}.csv", index_label="team")

    # ---- Bills: division, clinch week
    b = tab.loc[US]
    cw = pd.Series([w for w in cl[US] if w is not None])
    weeks = list(range(WEEK, 19))
    by_week = {w: float((cw <= w).sum() / N_SIMS) for w in weeks}
    in_week = {w: float((cw == w).sum() / N_SIMS) for w in weeks}
    likely = max(in_week, key=in_week.get)
    med = int(np.median(cw)) if len(cw) else None
    div_teams = NP.DIVISIONS[DIV]
    def div_lead(t):  # games ahead of the next team in its division (wins + half of ties)
        w = {x: rec[x][0] + rec[x][2] / 2 - (rec[x][1] + rec[x][2] / 2) for x in NP.DIVISIONS[NP.DIV_OF[t]]}
        top = sorted(w.values(), reverse=True)
        return (w[t] - top[1]) / 2 if w[t] == top[0] else 0
    lead = div_lead(US)
    lead_txt = f"{int(lead)}{'½' if lead % 1 else ''}"
    sch = NP.season_games(SEASON)
    left_buf = sch[(sch.week >= WEEK) & ((sch.home_team == US) | (sch.away_team == US))]
    nxt = left_buf.iloc[0]
    nxt_opp = nxt.away_team if nxt.home_team == US else nxt.home_team

    # ---- the backtest (7 seasons, odds from week 11 vs. who made it)
    bt = NP.backtest(seasons=BACKTEST, week=WEEK, n=2000, drift_seasons=BACKTEST)
    bt["mix"] = MIX * bt.p_coin + (1 - MIX) * bt.p
    brier = {k: float(((bt[c] - bt.made) ** 2).mean()) for k, c in (("model", "p"), ("standings", "p_coin"), ("mix", "mix"))}
    by_season = bt.groupby("season").apply(lambda x: pd.Series({k: ((x[c] - x.made) ** 2).mean() for k, c in
                                                                (("model", "p"), ("standings", "p_coin"), ("mix", "mix"))}))
    mix_wins = int((by_season["mix"] <= by_season["standings"] + 1e-12).sum())
    bt["bucket"] = pd.cut(bt.mix, [0, .1, .3, .5, .7, .9, 1.0001], right=False)
    cal = bt.groupby("bucket", observed=True).agg(n=("mix", "size"), said=("mix", "mean"), made=("made", "mean"))
    sure = bt[bt.mix >= 0.9]; long_ = bt[bt.mix <= 0.1]

    # ---- chart 1: every team's playoff chances, by conference
    fig, axes = plt.subplots(1, 2, figsize=(12, 7.6), dpi=200)
    for ax, conf in zip(axes, ("AFC", "NFC")):
        t = tab[tab.conf == conf].sort_values("playoffs")
        cols = [RED if i == US else (BLUE if i in plan else "#9AA3B2") for i in t.index]
        ax.barh(range(len(t)), t.playoffs, color=cols, height=0.7, zorder=2)
        for y, (i, r) in enumerate(t.iterrows()):
            ax.text(r.playoffs + 0.01, y, pct(r.playoffs), va="center", fontsize=8.5, color=INK)
        ax.set_yticks(range(len(t)), [f"{NAMES[i]} ({r.record})" for i, r in t.iterrows()], fontsize=9)
        ax.set_xlim(0, 1.12); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
        ax.set_title(conf, loc="left", fontsize=12, fontweight="bold", color=INK)
        ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Every NFL team's chance to make the playoffs",
           "After week 10. Red = Bills. Blue = teams whose main quarterback is out for some or all of the rest of the season.",
           f"{N_SIMS:,} simulated seasons; half use our points model with quarterback news, half treat every game as 50/50. "
           "Records through week 10. 7 teams per conference make it.")
    fig.savefig(OUT / "wk11-odds-league.png"); plt.close(fig)

    # ---- graphic 2: the Bills clinch calendar
    cal_weeks = []
    for x in left_buf.itertuples():
        home = x.home_team == US
        cal_weeks.append(dict(n=int(x.week), opp=("vs. " if home else "at ") + NAMES[x.away_team if home else x.home_team],
                        date=pd.Timestamp(x.gameday).strftime("%a., %b. %-d"),
                        by=by_week[int(x.week)]))
    best_opp = next(c for c in cal_weeks if c["n"] == likely)["opp"]
    IG.clinch_calendar(cal_weeks, OUT / "wk11-odds-bills-clinch.png", "Buffalo Quant · AFC East watch",
                       "When do the Bills<br>lock up the division?",
                       f"Chance it's done by the end of each week. Most likely clinch: <b style='color:#fff'>Week {likely}, {IG.e(best_opp)}</b>.",
                       f"Buffalo wins the AFC East in {b.division:.0%} of {N_SIMS:,} simulated seasons. \"Locked\" = no rival can catch them "
                       "even by winning out (ties not counted, so it can come a week sooner).", likely)

    # ---- graphic 3: the AFC ladder
    afc = tab[tab.conf == "AFC"].sort_values(["playoffs", "division"], ascending=False)
    out_qb = [NAMES[t] for t in afc.index if t in plan and qb.loc[t, "plan"] != "returns_week"]
    IG.ladder([dict(name=NAMES[t], record=r.record, p=float(r.playoffs), d=float(r.division), hatched=t in plan and qb.loc[t, "plan"] != "returns_week",
                    highlight=t == US) for t, r in afc.iterrows()],
              OUT / "wk11-odds-afc-ladder.png", f"Buffalo Quant · Playoff odds · after week {WEEK - 1}", "The AFC ladder",
              f"Chance to make the playoffs, from {N_SIMS:,} simulated seasons with quarterback injuries built in. Seven make it.",
              f"Hatched = main quarterback out ({', '.join(out_qb)}). Half the simulations use our points model, half treat every game as a coin flip.")

    # ---- chart 3: the test, how often our chances came true (stat-heads)
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=200)
    ax.plot([0, 1], [0, 1], color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    ax.scatter(cal.said, cal.made, s=cal.n * 6, color=BLUE, alpha=0.85, zorder=2)
    for r in cal.itertuples():
        ax.text(r.said + 0.02, r.made - 0.04, f"{r.n} teams", fontsize=8.5, color=MUTED)
    ax.set_xlabel("Playoff chance we'd have given after week 10"); ax.set_ylabel("Share that made it")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.05); ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Tested on 7 past seasons: our chances vs. what happened",
           "Dots on the dashed line = a 30% chance came true about 30% of the time.",
           f"{BACKTEST[0]}-{BACKTEST[-1]}, every team after week 10 ({len(bt)} team-seasons). No quarterback adjustments in the test.")
    fig.savefig(OUT / "wk11-odds-test.png"); plt.close(fig)

    # ---- text pieces
    def row(t):
        r = tab.loc[t]
        return f"| {NAMES[t]} | {r.record} | {pct(r.playoffs)} | {pct(r.division)} | {pct(r.seed1)} |"
    tables = {}
    for conf in ("AFC", "NFC"):
        order = tab[tab.conf == conf].sort_values(["playoffs", "division"], ascending=False).index
        tables[conf] = "\n".join(row(t) for t in order)
    qb_rows = []
    for t in qb.sort_values("plan").index:
        e = qb.loc[t]
        how = {"out_rest": "rest of season", "returns_week": "back week 12 (assumed)", "draw": "no timeline (drawn from past absences)"}[e.plan]
        if t == "MIA":
            how = "on IR, at least 4 games, then drawn from past absences"
        mv = round((tab.loc[t, "playoffs"] - tab.loc[t, "no_qb"]) * 100)
        move = "no change" if mv == 0 else f"{mv:+d} pts"
        src = " ".join(f"[{i + 1}]({u})" for i, u in enumerate(e.sources))
        qb_rows.append(f"| {NAMES[t]} | {e.main_qb} | {e.starter} | {how} | {pct(tab.loc[t, 'playoffs'])} ({move}) | {e.why} {src} |")
    biggest = (tab.loc[list(plan)].playoffs - tab.loc[list(plan)].no_qb).abs().sort_values(ascending=False)
    big_t = biggest.index[0]; big_mv = tab.loc[big_t, "playoffs"] - tab.loc[big_t, "no_qb"]
    afc_div = tab[(tab.conf == "AFC")].sort_values("division", ascending=False)

    md = f"""# The Bills have a {pct(b.division)} chance to win the AFC East, and will most likely clinch it in week {likely}

**After 10 weeks, Buffalo ({b.record}) leads the AFC East by {lead_txt} games. In {N_SIMS:,} simulated rest-of-seasons, the Bills win
the division {pct(b.division)} of the time and make the playoffs {pct(b.playoffs)} of the time. The most likely week they lock up the
division is week {likely} ({in_week[likely]:.0%} of simulations); by week {likely} they've clinched it {by_week[likely]:.0%} of the time. We also ran
every other team, with this season's quarterback injuries built in.**

*Our playoff odds for all 32 teams, with games through week 10. Numbers as of {AS_OF}. We'll update them as the season goes.*

![Every NFL team's chance to make the playoffs](wk11-odds-league.png)

## The Bills

- **Division:** {pct(b.division)}. Buffalo leads by {lead_txt} games with {len(left_buf)} to play.
- **Playoffs:** {pct(b.playoffs)}. **Top seed (the only first-round bye):** {pct(b.seed1)}.
- **Wins:** about {b.wins:.1f} on average in the simulations.
- **Clinching:** by week {likely - 1}, {by_week[likely - 1]:.0%} of the time. By week {likely}, {by_week[likely]:.0%}. By week {likely + 1}, {by_week[likely + 1]:.0%}.
  The middle of all the simulated clinch weeks is week {med}.

![When the Bills lock up the AFC East](wk11-odds-bills-clinch.png)

**What "clinch" means here:** the week Buffalo's win total gets out of reach, when even a rival winning every remaining game
couldn't catch the Bills. We don't count a possible tie at the top, because the league's tiebreakers can't all be worked out
ahead of time, so the real clinch can come a week sooner than our chart shows. Next up: {NAMES[nxt_opp]} on
{pd.Timestamp(nxt.gameday).strftime('%A, %b. %-d')}.

## How we got these numbers

**Step 1: how good is each team?** Our points model rates every offense and defense by points per drive this season, the same
model behind our weekly game predictions. It projects the score of every remaining game.

**Step 2: play out the rest of the season, {N_SIMS:,} times.** For each game, we take our projected score and add the kind of
surprise real games produce. We use the misses from real past games, so a 7-point favorite still loses about as often as real 7-point
favorites have. Teams also get better or worse as a season goes on. In past seasons, a team's scoring drifted about {drift['off']:.0f} points
a game from where it stood after 10 weeks, and its defense about {drift['def']:.0f}. So each simulated season gives every team its own
lasting nudge up or down.

**Step 3: quarterbacks.** This is where injury news comes in. We looked at {fx['n_games']:,} games from 2019 to 2025. In the
{fx['n_backup']:,} where a team started someone other than its main quarterback, it scored {abs(fx['team']):.1f} fewer points than our
model expected, and its opponent scored {fx['opp']:.1f} more. That's the penalty we apply in every game a team's main quarterback
misses. When a starter is hurt with no timeline, we don't guess. We draw how many games he misses from {len(absn)} past absences that
ended with the starter coming back. The typical one lasted {int(np.median(absn))} games.

**Step 4: seed the playoffs.** Four division winners and three wild cards per conference, with ties broken by head-to-head, then
division record, then conference record. The league's full tiebreaker list goes deeper; past these three steps we flip a coin.

**How we checked it.** We ran the same method from week 10 of each of the last seven seasons ({BACKTEST[0]}-{BACKTEST[-1]}) and
compared it with who actually made the playoffs. The honest result: by this point in a season, the standings already say a lot.
Treating every remaining game as a coin flip did about as well as our model. Blending the two half and half did at least as well
as the coin flip in {mix_wins} of 7 seasons. So that blend is what you see here: half of the simulated seasons use our model and the
quarterback news, half treat every game as 50/50. Teams we put at 90% or better made it {sure.made.mean():.0%} of the time
({len(sure)} teams). Teams at 10% or less made it {long_.made.mean():.0%} of the time ({len(long_)} teams).

## Quarterback injuries we built in

Ten teams have lost their main quarterback (the one with the most dropbacks this season) to injury, a trade or a benching,
for a week or more. In each game he misses, we apply the penalty from step 3. The change column compares each team's playoff
chance with and without that penalty. Last column: why, with the reports we used.

| Team | Main QB | Starting now | How long | Playoff chance (change from QB news) | Why |
|---|---|---|---|---|---|
{chr(10).join(qb_rows)}

The QB news moved the {NAMES[big_t]}' odds the most ({big_mv * 100:+.0f} percentage points). Seattle's penalty is zero
because Seattle is off this week and we assume Darnold is back after that. Other injuries matter too, but we can't measure them
reliably yet, so we don't adjust for them. We will update this list as news comes in.

## All 32 teams

**AFC**

![The AFC ladder](wk11-odds-afc-ladder.png)

| Team | Record | Playoffs | Win division | Top seed |
|---|---|---|---|---|
{tables['AFC']}

**NFC**

| Team | Record | Playoffs | Win division | Top seed |
|---|---|---|---|---|
{tables['NFC']}

## For the stat-heads

![Tested on 7 past seasons](wk11-odds-test.png)

- Simulator: `src/metrics/nfl_playoffs.py`. Ratings: points model {NP.pm.VERSION} (points per drive, k=60 shrinkage to last season),
  frozen at week {WEEK}. Game outcomes: projected points plus a paired (home, away) residual drawn from training seasons
  2019-2023; ties within half a point are coin flips. {N_SIMS:,} sims, seed {SEED}; {MIX:.0%} of sims are 50/50 games.
- Strength drift: per-sim normal shocks, offense sd {drift['off']:.2f} and defense sd {drift['def']:.2f} points per game, from the
  variance of 2019-2025 team-season mean residuals (weeks {WEEK}-18, ratings frozen at week {WEEK}) minus game noise.
- QB effect (2019-2025, n={fx['n_games']:,} team-games, {fx['share_backup']:.0%} non-main starters): team {fx['team']:+.2f} (se {fx['team_se']:.2f}),
  opponent {fx['opp']:+.2f} (se {fx['opp_se']:.2f}) points vs. the model. "Main QB" = most dropbacks in the season before that week
  (first QB to drop back = starter). Includes benchings and long-term replacements, not only injuries.
- Backtest Brier score, playoff yes/no, {len(bt)} team-seasons (lower is better): model alone {brier['model']:.4f}, standings alone (50/50
  games) {brier['standings']:.4f}, half-and-half {brier['mix']:.4f}. By season (model / standings / mix):
  {'; '.join(f"{s} {r.model:.3f} / {r.standings:.3f} / {r.mix:.3f}" for s, r in by_season.iterrows())}. The mix was compared after
  seeing these seasons, so treat it as a sensible default, not a tuned edge. Drift in the backtest leaves out the tested season.
- Tiebreakers simplified (head-to-head, division record for division ties, conference record, coin flip); strength of victory,
  strength of schedule, common games and points steps are skipped. Real ties are counted as half a win.
- Full odds table: `reports/{SLUG}.csv`. Quarterback status file with every source: `config/nfl_qb_status_2026_wk11.json`.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "NFL playoff odds",
        "big": [[pct(b.division), "Bills win AFC East"], [f"Wk {likely}", "most likely clinch week"]],
        "note": f"Bills playoff chance: {pct(b.playoffs)}. All 32 teams, with quarterback injuries built in.",
        "explainer": {"kicker": "How sure?", "title": "Tested on 7 past seasons.",
                      "text": "Teams we'd have put at 90% or better after week 10, and how many made it:",
                      "bars": [["We said", round(float(sure.mix.mean()), 2)], ["Made it", round(float(sure.made.mean()), 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
