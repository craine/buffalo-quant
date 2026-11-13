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
    win = int(tie_goal.t) % 1200                       # Buffalo's stretch: the first 8:22 of the third
    pulled = ["6v5", "5v6", "6v4", "4v6", "6v3", "3v6"]
    x3 = lg[(lg.unblocked == 1) & (lg.empty_net_against == 0) & (lg.period == 3) & (lg.game_id != G)
            & (lg.t % 1200 < win) & ~lg.strength.isin(pulled)].copy()
    x3["d"] = x3.tg - x3.og
    x3 = x3[x3.d.abs() == 1]
    lead1_share = x3[x3.d == 1].xg.sum() / x3.xg.sum()
    x3["leader"] = np.where(x3.d == 1, x3.team, x3.opp)
    pgl = x3.groupby(["game_id", "leader", x3.d == 1]).xg.sum().unstack(fill_value=0)
    pgl_share = pgl[True] / (pgl[True] + pgl[False])
    n_lead1, low_frac = len(pgl_share), float((pgl_share <= u1f / (u1f + u1a)).mean())
    pp_codes = ["5v4", "5v3", "4v3", "4v5", "3v5", "3v4"]
    them_st = up1[up1.team == THEM]
    st_xg = them_st[them_st.strength != "5v5"].xg.sum()     # Chicago's chances in the stretch on a power play or 4-on-4
    assert set(them_st.strength) <= {"5v5", "5v4", "4v4"} and set(up1[up1.team == US].strength) == {"5v5"}
    reg_f, reg_a = f[f.period <= 3].xg.sum(), a[a.period <= 3].xg.sum()

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
    # the pregame story's win rates (games before Nov 12), recomputed so this story's hero is traceable
    pw = ga[ga.game_date < pd.Timestamp("2026-11-12")].merge(query("SELECT game_id, home_score, away_score FROM raw_nhl_games"), on="game_id")
    pw["road_won"] = (pw.away_score > pw.home_score).astype(int)
    w_tired = pw[(pw.r_a == 1) & (pw.r_h >= 2)].road_won.mean()
    w_rested = pw[(pw.r_a >= 2) & (pw.r_h >= 2)].road_won.mean()
    assert round(w_tired, 2) == 0.38 and round(w_rested, 2) == 0.47, (w_tired, w_rested)
    ga = ga[ga.game_id != G]
    ub = s[unb & (s.period <= 3)].merge(ga[["game_id", "away", "r_h", "r_a"]], on="game_id")
    ub["road"] = ub.team == ub.away
    shares, ngames = {}, {}
    for lab, m in (("tired", (ub.r_a == 1) & (ub.r_h >= 2)), ("rested", (ub.r_a >= 2) & (ub.r_h >= 2))):
        t = ub[m].pivot_table(index="period", columns="road", values="xg", aggfunc="sum")
        shares[lab] = t[True] / (t[True] + t[False])
        ngames[lab] = ub[m].game_id.nunique()
    buf_share = per[US] / (per[US] + per[THEM])
    tired_ids = set(ub[(ub.r_a == 1) & (ub.r_h >= 2)].game_id)
    rested_ids = set(ub[(ub.r_a >= 2) & (ub.r_h >= 2)].game_id)
    pg = ub.groupby(["game_id", "period", "road"]).xg.sum().unstack(fill_value=0)
    rng = np.random.default_rng(12)
    def share(ids, per_):
        z = pg.xs(per_, level=1).reindex(ids).fillna(0)
        return z[True].sum() / (z[True].sum() + z[False].sum())
    gaps = {}
    ti, ri = np.array(sorted(tired_ids)), np.array(sorted(rested_ids))
    for per_ in (1, 2, 3):
        bs = [share(rng.choice(ti, len(ti)), per_) - share(rng.choice(ri, len(ri)), per_) for _ in range(400)]
        gaps[per_] = (shares["tired"][per_] - shares["rested"][per_], np.percentile(bs, 2.5), np.percentile(bs, 97.5))

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
        ax.scatter(x.t[gx] / 60, cum[gx], s=70, color=BLUE if team == US else INK, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40, 60):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    ax.axvspan(40, tie_goal.t / 60, color="#F3F4F6", zorder=0)
    ax.text((40 + tie_goal.t / 60) / 2, 0.15, "3rd, Sabres\nup 2-1", fontsize=8.5, color=MUTED, ha="center")
    for x0, lab in ((10, "1st"), (30, "2nd"), (50, "3rd"), (61.6, "OT")):
        ax.text(x0, 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=9, color=MUTED)
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Buffalo led the chances for 60 minutes; Chicago had all of overtime",
           f"Chances {reg_f:.1f} to {reg_a:.1f} Buffalo after 60 minutes; {f.xg.sum():.1f} to {a.xg.sum():.1f} with overtime. Chicago won {them_sc}-{us_sc} in OT. Blue dots = Sabres goals, black = Chicago's.",
           f"Unblocked shots, empty net excluded. Sabres {len(f)} unblocked shots, Blackhawks {len(a)}. Nov. 12, 2026, in Chicago.")
    fig.savefig(OUT / "sabres-chi-post-flow.png"); plt.close(fig)

    # ---- chart 2: tired vs rested road teams, share of chances by period
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(3); w = 0.27
    ax.bar(xs - w, [shares["rested"][p] for p in (1, 2, 3)], w, color="#C9CDD4", label=f"Rested road teams ({ngames['rested']:,} games)", zorder=2)
    ax.bar(xs, [shares["tired"][p] for p in (1, 2, 3)], w, color="#7A8699", label=f"Tired road teams ({ngames['tired']} games)", zorder=2)
    ax.bar(xs + w, [buf_share[p] for p in (1, 2, 3)], w, color=BLUE, label="Sabres, Thursday", zorder=2)
    for i, p in enumerate((1, 2, 3)):
        for dx, v, c in ((-w, shares["rested"][p], MUTED), (0, shares["tired"][p], INK), (w, buf_share[p], INK)):
            ax.text(i + dx, v + 0.01, f"{v:.0%}", ha="center", va="bottom", fontsize=9, color=c)
    ax.axhline(0.5, color="#D5D8DE", lw=1, ls="--")
    ax.set_xticks(xs, ["1st period", "2nd period", "3rd period"])
    ax.set_ylim(0, 0.8); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylabel("Road team's share of the chances")
    ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=3); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Tired road teams are a little behind all game. They don't fade late",
           "Road team's share of the chances in each period. Tired = played the night before; the home team had at least a day off.",
           f"Regular-season NHL games, 2023-24 through {pd.Timestamp(as_of):%b. %-d}, 2026, Thursday's game left out. Overtime not shown.")
    fig.savefig(OUT / "sabres-chi-post-periods.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {'OT' if r.period == 4 else int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Blackhawks'} | {r.who} | {r.shot_type} from {r.dist:.0f} ft"
        f"{', rebound' if r.rebound else ''}{', power play' if r.strength in ('5v4', '5v3', '4v3') else ''}{', 3-on-3' if r.strength == '3v3' else ''} | {r.xg:.0%} | "
        f"{int(r.us_g + (r.team == US))}-{int(r.them_g + (r.team == THEM))} |" for r in gl.itertuples())
    tie_left = 1200 - int(tie_goal.t) % 1200
    md = f"""# Blackhawks {them_sc}, Sabres {us_sc} (OT): Buffalo had more of the chances for 60 minutes and still lost

**Finding: Over 60 minutes, the Sabres' chances were worth {reg_f:.1f} goals to Chicago's {reg_a:.1f}, and they led 2-1 into the third. Chicago tied it with
{clock(tie_left)} left and won {clock(ot_goal.t)} into overtime. That fits the pattern from our pregame story: road teams on the second night of a back-to-back lose more
often than their chances say. One game can't prove it. Our {PRED_P:.0%} call for a Buffalo win is a miss.**

*One game, Nov. 12, in Chicago, the second night of a back-to-back for Buffalo. [Our pregame story](sabres-blackhawks-pregame-nov-12.html).*

![Game flow](sabres-chi-post-flow.png)

## How it went

| Period | Sabres chances, in goals | Blackhawks chances, in goals |
|---|---|---|
| 1st | {per.loc[1, US]:.1f} ({nper.loc[1, US]} shots) | {per.loc[1, THEM]:.1f} ({nper.loc[1, THEM]} shots) |
| 2nd | {per.loc[2, US]:.1f} ({nper.loc[2, US]} shots) | {per.loc[2, THEM]:.1f} ({nper.loc[2, THEM]} shots) |
| 3rd | {per.loc[3, US]:.1f} ({nper.loc[3, US]} shots) | {per.loc[3, THEM]:.1f} ({nper.loc[3, THEM]} shots) |
| Overtime | 0.0 (0 shots) | {per.loc[4, THEM]:.1f} ({nper.loc[4, THEM]} shots) |

Shots counted here are the ones that weren't blocked, not counting empty nets.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

Our pregame story said to watch the first period, because tired road teams usually start a little behind. Buffalo didn't: it had {buf_share[1]:.0%} of the chances in
the first and {buf_share[2]:.0%} in the second. In regulation the chances came out {reg_f:.1f} to {reg_a:.1f} Buffalo. Replay those 60 minutes over and over, with each shot going
in or missing at its own chance, and Buffalo wins {p_win:.0%} of the time and Chicago {p_loss:.0%}; the other {p_tie:.0%}, it's tied after 60. That's what happened: 2-2 after 60, and overtime
belonged to Chicago: {nper.loc[4, THEM]} shots to none.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Frank Nazar's first goal, from {gl.iloc[1].dist:.0f} feet, had a
{gl.iloc[1].xg:.0%} chance; Tage Thompson's power-play goal from {gl.iloc[2].dist:.0f} feet, about {gl.iloc[2].xg:.0%}. Add those chances up over a game and you get what a team's chances
were worth in goals: all {len(a)} of Chicago's shots, overtime included, were worth {a.xg.sum():.1f}, and Chicago scored {them_sc}. In regulation alone it was {reg_f:.1f} for Buffalo,
{reg_a:.1f} for Chicago; Chicago's last {per.loc[4, THEM]:.1f} came in overtime. The shot locations come from the NHL's own play-by-play. (The full
explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

## The third period

Buffalo led 2-1 from {clock(lead_goal.t)} of the first until Nazar's tip-in {clock(tie_goal.t)} into the third. In those first {clock(tie_goal.t)} of the third, the Sabres had {n_u1f} shots
that weren't blocked, worth {u1f:.1f} goals, and Chicago had {n_u1a}, worth {u1a:.1f}: **{u1f / (u1f + u1a):.0%} of the chances for Buffalo.** A team up a goal at that point of the third
usually gets about {lead1_share:.0%}, since the trailing team pushes. About {st_xg / u1a:.0%} of Chicago's chances in that stretch came on a power play or at 4-on-4.

It's {n_u1f + n_u1a} shots in about eight minutes, and stretches like that swing a lot: across the NHL since 2023-24, about {low_frac:.0%} of teams up a goal in the same
part of the third got {u1f / (u1f + u1a):.0%} of the chances or less ({n_lead1:,} teams in that spot). After the tie, the chances were even until overtime.

## The back-to-back

Our pregame story found that road teams playing the second night in a row, against a rested home team, win less often, without falling far behind in the chances.
Thursday fit that: Buffalo had more of the chances in regulation and still lost. One game doesn't confirm it, and we still don't know why it happens.

It's not that tired teams fade late. Split their chances by period ({ngames['tired']} games since 2023-24, not counting Thursday's), and they're a little behind all game,
not more in the third:

![Periods](sabres-chi-post-periods.png)

One thing did follow the usual pattern: in the pregame we found that a tired road team's usual starter was in net only 37% of the time, and Thursday Buffalo
started its third goalie. But in those past games, the goalies who played were only about 0.06 of a goal a game worse than average, so that isn't the whole answer either.

## In goal

Alex Lyon started for Buffalo after both of the Sabres' regular goalies played in Wednesday's 8-3 loss to Tampa Bay. It was his first NHL game this season.
He faced Chicago shots worth {ours.xga:.1f} goals and allowed {int(ours.ga)}, {abs(ours.saved):.1f} {'more' if ours.saved < 0 else 'fewer'} than an average goalie would have.
At the other end, [Spencer Knight](../cards/spencer-knight.html) stopped {int(theirs.on - theirs.ga)} of {int(theirs.on)}, {abs(theirs.saved):.1f} goals {'better' if theirs.saved >= 0 else 'worse'} than average.
Neither night was far from average.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). They lost in overtime, so it's a miss. Scored the usual way (the gap between
our chance and what happened, squared; lower is better), it comes to {brier:.2f}, worse than a 50/50 guess's 0.25. Our record on graded calls is now {hits} of {len(m)}.

Our pregame story said to read the {PRED_P:.0%} as too high, because the model doesn't know about back-to-backs. Chicago won, the way that warning pointed, but one game
can't confirm it, and the {PRED_P:.0%} is what we logged and what gets graded. The model expected about {PRE_XG_US:.1f} goals for Buffalo and {PRE_XG_THEM:.1f} for Chicago; after 60
minutes it was 2-2, on chances worth {reg_f:.1f} and {reg_a:.1f}. Both teams created less than the model thought; the edge went the way it expected.

## What it means for Buffalo

- **The Sabres had the better of the team that creates the fewest chances**, as expected, though both teams created less than our model thought. In the
  standings it's one point from a game they had the better of.
- **The third-period stretch is one to watch, not a trend yet.** If Buffalo keeps getting this far out-chanced with a lead, it'll show up in more than one game.

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal); CHI {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal).
  Regulation: BUF {reg_f:.2f}, CHI {reg_a:.2f}. Through two periods: BUF {two_f:.2f}, CHI {two_a:.2f}.
- Third period with BUF +1 (40:00 to {int(tie_goal.t) // 60}:{int(tie_goal.t) % 60:02d}): BUF {u1f:.2f} xG ({n_u1f}, all 5v5), CHI {u1a:.2f} ({n_u1a}; {st_xg:.2f} at 5v4 or 4v4). BUF 5v5 share
  {u1f / (u1f + them_st[them_st.strength == '5v5'].xg.sum()):.2f}. League comparison: shots in the first {clock(win)} of the third with a one-goal margin, pulled-goalie strengths excluded,
  2023-24 to date: leader's xG share {lead1_share:.3f}; per game, {low_frac:.3f} of leaders got {u1f / (u1f + u1a):.2f} or less ({n_lead1:,} game-leaders).
- Back-to-back split: road xG share by period, tired (road rest 1, home rest 2+) {', '.join(f'P{p} {shares["tired"][p]:.3f}' for p in (1, 2, 3))};
  rested (both 2+) {', '.join(f'P{p} {shares["rested"][p]:.3f}' for p in (1, 2, 3))}. Tired minus rested, with 95% game-resampling ranges:
  {'; '.join(f'P{p} {gaps[p][0] * 100:+.1f} pts ({gaps[p][1] * 100:+.1f} to {gaps[p][2] * 100:+.1f})' for p in (1, 2, 3))}. Games: {ngames['tired']} / {ngames['rested']:,}. Regulation only;
  by-period shares are not score-adjusted (tired road teams trail more often late, which lifts their third-period share).
- Replays: exact Poisson-binomial over regulation shots (each an independent Bernoulli with p = xG). BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx = xG on unblocked shots faced minus goals allowed. Lyon {ours.saved:+.2f} ({int(ours.on)} SOG), Knight {theirs.saved:+.2f} ({int(theirs.on)} SOG).
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0 (CHI won in OT; any result counts), Brier {brier:.4f}. Model nhl-game-v0.1; its 3.45 / 2.97 are expected goals for 60 minutes.
"""
    (OUT / "2026-11-13-sabres-chi.md").write_text(md)
    (OUT / "2026-11-13-sabres-chi.hero.json").write_text(json.dumps({
        "label": "Chances in regulation, in goals",
        "big": [[round(float(reg_f), 1), "Sabres"], [round(float(reg_a), 1), "Blackhawks"]],
        "note": f"Final: Blackhawks {them_sc}, Sabres {us_sc} in overtime. Buffalo had more of the chances over 60 minutes and still lost.",
        "explainer": {
            "kicker": "The back-to-back", "title": "Tired road teams lose more often than their chances say.",
            "text": "How often road teams won since 2023-24, from our pregame story:",
            "fmt": "pct",
            "bars": [["Played the night before", round(float(w_tired), 3)], ["Rested", round(float(w_rested), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
