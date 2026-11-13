"""Sabres post-game: BUF at CHI, Nov 12, 2026 (Chicago 3, Buffalo 2, OT). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-13-sabres-chi.md, two PNGs and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF so the published story doesn't change. Ledger P0010 graded by src/ledger/grade_p0010.py (separate).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
G, SEASON, US, THEM = 2026020305, 20262027, "BUF", "CHI"
AS_OF = "2026-11-12"
PRED_ID, PRED_P = "P0010", 0.57
PRE_XG_US, PRE_XG_THEM = 3.45, 2.97   # pregame expected goals, from P0010's notes in ledger/predictions.csv
CHI_RED = "#8A1C2B"
LYON = 8479312


def clock(t):
    t = int(t) % 1200
    return f"{t // 60}:{t % 60:02d}"


def main(as_of=AS_OF):
    s = shots()
    keep = query(f"SELECT game_id, season, game_date, home, away FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(keep.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    assert gm.home == THEM and gm.away == US and gm.game_state in ("OFF", "FINAL") and gm.last_period_type == "OT"
    us_sc, them_sc = int(gm.away_score), int(gm.home_score)

    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    allg["us_g"] = ((allg.team == US) & (allg.goal == 1)).cumsum().shift(fill_value=0)
    allg["them_g"] = ((allg.team == THEM) & (allg.goal == 1)).cumsum().shift(fill_value=0)
    assert int((allg[allg.team == US].goal == 1).sum()) == us_sc and int((allg[allg.team == THEM].goal == 1).sum()) == them_sc
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    f, a = g[g.team == US], g[g.team == THEM]
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    nper = g.groupby(["period", "team"]).size().unstack().fillna(0).astype(int)
    two_f, two_a = per.loc[[1, 2], US].sum(), per.loc[[1, 2], THEM].sum()

    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    lead_goal, tie_goal, ot_goal = gl.iloc[2], gl.iloc[3], gl.iloc[4]
    assert lead_goal.team == US and tie_goal.team == THEM and tie_goal.period == 3 and ot_goal.period == 4
    p3 = g[g.period == 3]
    up1 = p3[(p3.us_g - p3.them_g) == 1]
    tied3 = p3[p3.us_g == p3.them_g]
    u1f, u1a = up1[up1.team == US].xg.sum(), up1[up1.team == THEM].xg.sum()
    n_u1f, n_u1a = int((up1.team == US).sum()), int((up1.team == THEM).sum())
    t3f, t3a = tied3[tied3.team == US].xg.sum(), tied3[tied3.team == THEM].xg.sum()

    # league, all seasons through AS_OF (this game left out): share of third-period chances for a team up by one
    lg = s.sort_values(["game_id", "period", "t", "eventId"]).copy()
    lg["gf"] = (lg.goal == 1).astype(int)
    lg["tg"] = lg.groupby(["game_id", "team"]).gf.cumsum() - lg.gf
    lg["og"] = lg.groupby("game_id").gf.cumsum() - lg.gf - lg.tg
    x3 = lg[(lg.unblocked == 1) & (lg.empty_net_against == 0) & (lg.period == 3) & (lg.game_id != G)]
    d = x3.tg - x3.og
    lead1_share = x3[d == 1].xg.sum() / (x3[d == 1].xg.sum() + x3[d == -1].xg.sum())
    n_lead1 = x3[d.abs() == 1].game_id.nunique()

    # back-to-backs: road team's share of chances by period, tired vs rested (this game left out)
    ga = keep.copy()
    ga["game_date"] = pd.to_datetime(ga.game_date)
    lgr = pd.concat([ga.assign(team=ga.home)[["game_id", "season", "game_date", "team"]],
                     ga.assign(team=ga.away)[["game_id", "season", "game_date", "team"]]]).sort_values(["team", "game_date"])
    lgr["rest"] = lgr.groupby(["team", "season"]).game_date.diff().dt.days
    rest = lgr.set_index(["game_id", "team"]).rest
    ga["r_h"] = [rest.get((i, h)) for i, h in zip(ga.game_id, ga.home)]
    ga["r_a"] = [rest.get((i, w)) for i, w in zip(ga.game_id, ga.away)]
    assert ga.set_index("game_id").loc[G, "r_a"] == 1
    ga = ga[ga.game_id != G]
    ub = s[unb & (s.period <= 3)].merge(ga[["game_id", "away", "r_h", "r_a"]], on="game_id")
    ub["road"] = ub.team == ub.away
    shares, ngames = {}, {}
    for lab, m in (("tired", (ub.r_a == 1) & (ub.r_h >= 2)), ("rested", (ub.r_a >= 2) & (ub.r_h >= 2))):
        t = ub[m].pivot_table(index="period", columns="road", values="xg", aggfunc="sum")
        shares[lab] = t[True] / (t[True] + t[False])
        ngames[lab] = ub[m].game_id.nunique()
    buf_share = per[US] / (per[US] + per[THEM])

    # replays: each shot goes in or misses at its own chance, exactly (Poisson-binomial)
    def pmf(ps):
        out = np.array([1.0])
        for q in ps:
            out = np.convolve(out, [1 - q, q])
        return out
    joint = np.outer(pmf(f[f.period <= 3].xg.values), pmf(a[a.period <= 3].xg.values))
    p_win, p_tie = np.tril(joint, -1).sum(), np.trace(joint)
    p_loss = 1 - p_win - p_tie

    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    assert len(gk) == 2 and set(gk.opp) == {US, THEM}
    ours, theirs = gk[gk.opp == US].iloc[0], gk[gk.opp == THEM].iloc[0]
    assert int(ours.goalie_id) == LYON
    lyon_games = s[(s.goalie_id == LYON) & (s.season == SEASON)].game_id.nunique()
    assert lyon_games == 1

    # ledger record to date
    pr = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    m = pr.merge(gr, left_on="id", right_on="prediction_id")
    m = m[pd.to_datetime(m.graded_at_utc) <= pd.Timestamp(as_of, tz="UTC") + pd.Timedelta(days=2)]
    hits = int((((m.probability >= 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))).sum())
    row = m[m.id == PRED_ID].iloc[0]
    assert row.outcome == 0
    brier = float(row.brier)

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    end = g.t.max() / 60 + 0.5
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, CHI_RED, "Blackhawks")]:
        x = g[g.team == team]
        cum = x.xg.cumsum()
        ax.step(np.r_[0, x.t / 60, end], np.r_[0, cum, cum.iloc[-1]], where="post", color=col, lw=2.4, label=lab,
                ls="-" if team == US else (0, (4, 1.5)))
        gx = x.goal == 1
        ax.scatter(x.t[gx] / 60, cum[gx], s=70, color=RED if team == US else INK, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40, 60):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    ax.axvspan(40, tie_goal.t / 60, color="#F3F4F6", zorder=0)
    ax.text((40 + tie_goal.t / 60) / 2, 0.15, "3rd, Sabres\nup 2-1", fontsize=8.5, color=MUTED, ha="center")
    for x0, lab in ((10, "1st"), (30, "2nd"), (50, "3rd"), (61.6, "OT")):
        ax.text(x0, 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=9, color=MUTED)
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Buffalo led the chances for two periods; Chicago took the third",
           f"Running total of each team's chances. Final chances {f.xg.sum():.1f} to {a.xg.sum():.1f}, score {them_sc}-{us_sc} Chicago (OT). Red dots = Sabres goals, black = Chicago's.",
           f"Unblocked shots, empty net excluded. Sabres {len(f)} unblocked shots, Blackhawks {len(a)}. Nov. 12, 2026, in Chicago.")
    fig.savefig(OUT / "sabres-chi-post-flow.png"); plt.close(fig)

    # ---- chart 2: tired vs rested road teams, share of chances by period
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(3); w = 0.27
    ax.bar(xs - w, [shares["rested"][p] for p in (1, 2, 3)], w, color="#C9CDD4", label=f"Rested road teams ({ngames['rested']:,} games)", zorder=2)
    ax.bar(xs, [shares["tired"][p] for p in (1, 2, 3)], w, color=BLUE, label=f"Tired road teams ({ngames['tired']} games)", zorder=2)
    ax.bar(xs + w, [buf_share[p] for p in (1, 2, 3)], w, color=RED, label="Sabres, Thursday", zorder=2)
    for i, p in enumerate((1, 2, 3)):
        for dx, v, c in ((-w, shares["rested"][p], MUTED), (0, shares["tired"][p], INK), (w, buf_share[p], INK)):
            ax.text(i + dx, v + 0.01, f"{v:.0%}", ha="center", va="bottom", fontsize=9, color=c)
    ax.axhline(0.5, color="#D5D8DE", lw=1, ls="--")
    ax.set_xticks(xs, ["1st period", "2nd period", "3rd period"])
    ax.set_ylim(0, 0.8); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylabel("Road team's share of the chances")
    ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=3); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Tired road teams trail most early, not late. Buffalo did the opposite",
           "Road team's share of the chances in each period. Tired = played the night before; the home team had at least a day off.",
           f"Regular-season NHL games, 2023-24 through {pd.Timestamp(as_of):%b. %-d}, 2026, Thursday's game left out. Overtime not shown.")
    fig.savefig(OUT / "sabres-chi-post-periods.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {'OT' if r.period == 4 else int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Blackhawks'} | {r.who} | {r.shot_type} from {r.dist:.0f} ft"
        f"{', rebound' if r.rebound else ''}{', power play' if r.strength in ('5v4', '5v3', '4v3') else ''}{', 3-on-3' if r.strength == '3v3' else ''} | {r.xg:.0%} | "
        f"{int(r.us_g + (r.team == US))}-{int(r.them_g + (r.team == THEM))} |" for r in gl.itertuples())
    tie_left = 1200 - int(tie_goal.t) % 1200
    md = f"""# Blackhawks {them_sc}, Sabres {us_sc} (OT): Buffalo carried two periods, then sat on a lead it couldn't keep

**Finding: The Sabres had the better of Chicago for 40 minutes: their chances were worth {two_f:.1f} goals to Chicago's {two_a:.1f}, and they led 2-1
going into the third. Then Chicago took over. With the lead in the third, Buffalo got {u1f / (u1f + u1a):.0%} of the chances; teams up a goal in the third
usually get {lead1_share:.0%}. Chicago tied it with {clock(tie_left)} left and won it {clock(ot_goal.t)} into overtime. The Sabres get a point; our {PRED_P:.0%} call
for a Buffalo win goes down as a miss.**

*One game, Nov. 12, in Chicago, the second night of a back-to-back for Buffalo. [Our pregame story](sabres-blackhawks-pregame-nov-12.html).*

![Game flow](sabres-chi-post-flow.png)

## How it went

| Period | Sabres chances, in goals | Blackhawks chances, in goals |
|---|---|---|
| 1st | {per.loc[1, US]:.2f} ({nper.loc[1, US]} shots) | {per.loc[1, THEM]:.2f} ({nper.loc[1, THEM]} shots) |
| 2nd | {per.loc[2, US]:.2f} ({nper.loc[2, US]} shots) | {per.loc[2, THEM]:.2f} ({nper.loc[2, THEM]} shots) |
| 3rd | {per.loc[3, US]:.2f} ({nper.loc[3, US]} shots) | {per.loc[3, THEM]:.2f} ({nper.loc[3, THEM]} shots) |
| Overtime | {per.loc[4, US] if US in per.columns and 4 in per.index else 0:.2f} ({nper.loc[4, US] if 4 in nper.index else 0} shots) | {per.loc[4, THEM]:.2f} ({nper.loc[4, THEM]} shots) |
| **Game** | **{f.xg.sum():.2f}** ({len(f)} shots) | **{a.xg.sum():.2f}** ({len(a)} shots) |

Shots counted here are the ones that weren't blocked, not counting empty nets.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

Over the whole game it was close to even: Buffalo's chances were worth {f.xg.sum():.1f} goals, Chicago's {a.xg.sum():.1f}. Replay the 60 minutes over and over, with each
shot going in or missing at its own chance, Buffalo wins {p_win:.0%} of the time and Chicago {p_loss:.0%}; the other {p_tie:.0%}, it's tied after 60 minutes. That's how close this one was.

## The third period

Buffalo led 2-1 from {clock(lead_goal.t)} of the first until Frank Nazar's tip-in {clock(tie_goal.t)} into the third. In those first {clock(tie_goal.t)} of the third, with the
lead, the Sabres had {n_u1f} shots that weren't blocked, worth {u1f:.2f} goals. Chicago had {n_u1a}, worth {u1a:.2f}. That's **{u1f / (u1f + u1a):.0%} of the chances for Buffalo.**

Some of that is normal. A team protecting a one-goal lead in the third tends to sit back, and the trailing team pushes: across the NHL since 2023-24
({n_lead1:,} games), the team up a goal in the third got {lead1_share:.0%} of the chances. Buffalo sat back further than that. It's {n_u1f + n_u1a} shots in about eight minutes, so
it's one stretch of one game, not a trend. After the tie, the chances were even ({t3f:.2f} to {t3a:.2f}) until overtime, where Chicago had all {nper.loc[4, THEM]} shots.

## Was it tired legs?

The easy story is that Buffalo ran out of gas on the second night of a back-to-back. The numbers don't back that up.

![Periods](sabres-chi-post-periods.png)

Our pregame story found that tired road teams win less often. Split their chances by period ({ngames['tired']} games since 2023-24, not counting
Thursday's) and they don't fade late. They're furthest behind in the **first** period, with {shares['tired'][1]:.0%} of the chances against {shares['rested'][1]:.0%} for rested road
teams, and by the third they've nearly caught up ({shares['tired'][3]:.0%} against {shares['rested'][3]:.0%}). Buffalo did the opposite: {buf_share[1]:.0%} of the chances in the
first, {buf_share[3]:.0%} in the third. The score explains Thursday's third period better than the schedule does.

## In goal

Alex Lyon started for Buffalo after both of the Sabres' regular goalies played in Wednesday's 8-3 loss to Tampa Bay. It was his first NHL game this season.
He faced Chicago shots worth {ours.xga:.1f} goals and allowed {int(ours.ga)}, {abs(ours.saved):.1f} {'more' if ours.saved < 0 else 'fewer'} than an average goalie would have.
At the other end, [Spencer Knight](../cards/spencer-knight.html) stopped {int(theirs.on - theirs.ga)} of {int(theirs.on)}, {abs(theirs.saved):.1f} goals {'better' if theirs.saved >= 0 else 'worse'} than average.
Neither goalie's night was far from average.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). They lost in overtime, so it's a miss. Scored the usual way (the gap between
our chance and what happened, squared; lower is better), it comes to {brier:.2f}, worse than a 50/50 guess's 0.25. Our record on graded calls is now {hits} of {len(m)}.

Our pregame story said to read the {PRED_P:.0%} as too high, because the model doesn't know about back-to-backs. Chicago won, the way that warning
pointed, but one game can't confirm it, and the {PRED_P:.0%} is what we logged and what gets graded. The model expected chances worth {PRE_XG_US:.2f} goals for Buffalo and {PRE_XG_THEM:.2f} for Chicago; the game came in well below both,
at {f.xg.sum():.1f} and {a.xg.sum():.1f}.

## What it means for Buffalo

- **The Sabres can carry play against a weak team.** For two periods they did what the numbers said they should against the league's weakest team at
  creating chances.
- **Holding a lead is the thing to watch.** One stretch isn't a pattern, but if Buffalo keeps getting this far out-chanced with a lead in the third, it'll show up
  in the standings. Next up: Saturday at Dallas.

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal); CHI {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal).
- Third period with BUF +1 (40:00 to {int(tie_goal.t) // 60}:{int(tie_goal.t) % 60:02d}): BUF {u1f:.2f} xG ({n_u1f}), CHI {u1a:.2f} ({n_u1a}). League third-period xG share for a team
  up one, 2023-24 to date: {lead1_share:.3f} ({n_lead1:,} games).
- Back-to-back split: road xG share by period, tired (road rest 1, home rest 2+) {', '.join(f'P{p} {shares["tired"][p]:.3f}' for p in (1, 2, 3))};
  rested (both 2+) {', '.join(f'P{p} {shares["rested"][p]:.3f}' for p in (1, 2, 3))}. Games: {ngames['tired']} / {ngames['rested']:,}. Regulation only.
- Replays: exact Poisson-binomial over regulation shots (each an independent Bernoulli with p = xG). BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx = xG on unblocked shots faced minus goals allowed. Lyon {ours.saved:+.2f} ({int(ours.on)} SOG), Knight {theirs.saved:+.2f} ({int(theirs.on)} SOG).
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0 (CHI won in OT; any result counts), Brier {brier:.4f}. Model nhl-game-v0.1.
"""
    (OUT / "2026-11-13-sabres-chi.md").write_text(md)
    (OUT / "2026-11-13-sabres-chi.hero.json").write_text(json.dumps({
        "label": "Chances through two periods, in goals",
        "big": [[round(float(two_f), 1), "Sabres"], [round(float(two_a), 1), "Blackhawks"]],
        "note": f"Final: Blackhawks {them_sc}, Sabres {us_sc} in overtime. With a 2-1 lead in the third, Buffalo got {u1f / (u1f + u1a):.0%} of the chances.",
        "explainer": {
            "kicker": "Not the legs", "title": "Tired road teams trail most early, not late.",
            "text": "Road team's share of the chances in the first period, since 2023-24:",
            "fmt": "pct",
            "bars": [["Tired road teams", round(float(shares["tired"][1]), 3)], ["Rested road teams", round(float(shares["rested"][1]), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
