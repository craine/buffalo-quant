"""Sabres 5, Rangers 1 (Nov. 25, 2026): 18 goals in four games on chances worth about 10, and what that does to the season.

Chances = expected goals from our shot model (src/metrics/nhl_xg.py), unblocked non-empty-net shots, rescaled so league chances equal
league goals for 2026-27 games through AS_OF. Writes reports/2026-11-25-sabres-nyr-postgame.md, one PNG and a hero JSON.
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
from src.reports.pins import drop_late
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
SLUG = "2026-11-25-sabres-nyr-postgame"
PNG = "sabres-nyr-nov25-postgame.png"
AS_OF = "2026-11-25"
GAME = 2026020387
SEASON = 20262027
SPLIT = "2026-11-19"          # first of the last four games
PRED = "P0023"


def main(as_of=AS_OF):
    keep = drop_late(query(f"SELECT g.game_id, g.season, g.game_date, g.home, g.away, g.home_score, g.away_score, g.last_period_type "
                           f"FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id "
                           f"WHERE c.game_type = 2 AND g.game_date <= '{as_of}' AND g.season = {SEASON}"), as_of)
    s = shots()
    s = s[s.game_id.isin(set(keep.game_id))].merge(keep[["game_id", "game_date"]], on="game_id")
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0)].copy()
    cal = u.goal.sum() / u.xg.sum()
    u["xg"] = u.xg * cal

    # ---- the game
    g = keep[keep.game_id == GAME].iloc[0]
    assert (g.home, g.away, int(g.home_score), int(g.away_score), g.last_period_type) == ("BUF", "NYR", 5, 1, "REG")
    gu = u[u.game_id == GAME]
    x_b, x_n = float(gu[gu.team == "BUF"].xg.sum()), float(gu[gu.team == "NYR"].xg.sum())
    sog = s[s.game_id == GAME].groupby("team").on_goal.sum()
    assert int(s[(s.game_id == GAME) & (s.goal == 1) & (s.empty_net_against == 1)].shape[0]) == 0
    names = query("SELECT DISTINCT player_id, first || ' ' || last AS name FROM raw_nhl_rosters WHERE season = 20262027").drop_duplicates("player_id").set_index("player_id").name
    goals = gu[gu.goal == 1].sort_values(["period", "t"])
    goals = goals.assign(name=goals.shooter_id.map(names))
    nyr_g = int(gu[gu.team == "BUF"].goalie_id.mode().iloc[0])
    buf_g = int(gu[gu.team == "NYR"].goalie_id.mode().iloc[0])
    nyr_goalie, buf_goalie = names[nyr_g], names[buf_g]
    gb = u[(u.goalie_id == nyr_g) & (u.game_date < as_of)]
    k_before, k_games = float(gb.xg.sum() - gb.goal.sum()), int(gb.game_id.nunique())
    # who started each Rangers game since Nov. 7: the goalie facing the first Buffalo-or-other shot of the game
    nyr_sh = s[(s.opp == "NYR") & (s.game_date >= "2026-11-07") & (s.game_date <= as_of) & s.goalie_id.notna()].sort_values(["game_date", "period", "t"])
    starters = nyr_sh.groupby("game_id").first().sort_values("game_date").goalie_id.astype(int).tolist()
    alternate = all(a != b for a, b in zip(starters, starters[1:]))
    other = names[[x for x in starters if x != nyr_g][0]]
    assert alternate and starters[-1] == nyr_g and len(set(starters)) == 2 and len(starters) >= 6, starters
    long_g = goals[goals.team == "NYR"].iloc[0]
    close_b = goals[goals.team == "BUF"].sort_values("dist").iloc[0]
    assert (round(x_b, 1), round(x_n, 1), int(sog["BUF"]), int(sog["NYR"])) == (2.5, 2.3, 30, 30)
    assert nyr_goalie == "Joonas Korpisalo" and buf_goalie == "Ukko-Pekka Luukkonen" and k_games == 3

    # ---- the Sabres' season, game by game
    b = u[(u.team == "BUF") | (u.opp == "BUF")]
    gg = keep[(keep.home == "BUF") | (keep.away == "BUF")].sort_values("game_date").copy()
    gg["gf"] = np.where(gg.home == "BUF", gg.home_score, gg.away_score)
    gg["ga"] = np.where(gg.home == "BUF", gg.away_score, gg.home_score)
    for c, m in (("xgf", b.team == "BUF"), ("xga", b.opp == "BUF")):
        gg[c] = gg.game_id.map(b[m].groupby("game_id").xg.sum()).fillna(0)
    for c, m in (("ngf", b.team == "BUF"), ("nga", b.opp == "BUF")):
        gg[c] = gg.game_id.map(b[m].groupby("game_id").goal.sum()).fillna(0)
    gg["w"] = gg.gf > gg.ga
    early, late = gg[gg.game_date < SPLIT], gg[gg.game_date >= SPLIT]
    e = dict(n=len(early), gf=int(early.ngf.sum()), xgf=float(early.xgf.sum()), ga=int(early.nga.sum()), xga=float(early.xga.sum()))
    l = dict(n=len(late), w=int(late.w.sum()), gf=int(late.ngf.sum()), xgf=float(late.xgf.sum()), ga=int(late.nga.sum()), xga=float(late.xga.sum()),
             gf_all=int(late.gf.sum()))
    gf_ne, ga_ne, xgf_t, xga_t = int(gg.ngf.sum()), int(gg.nga.sum()), float(gg.xgf.sum()), float(gg.xga.sum())
    raw_lg = float(s[(s.unblocked == 1) & (s.empty_net_against == 0)].xg.sum())
    lg_goals = int(u.goal.sum())
    assert (gf_ne, ga_ne) == (75, 82)
    tot_fin = float(gg.ngf.sum() - gg.xgf.sum())
    tot_sv = float(gg.xga.sum() - gg.nga.sum())
    assert (e["n"], l["n"], l["w"], l["gf_all"], e["gf"], round(e["xgf"]), e["ga"]) == (21, 4, 3, 20, 57, 64, 72) and l["gf"] == 18 and round(l["xgf"]) == 10

    # ---- league ranks through the game (chance share, finishing, saves per game)
    c = u
    t = pd.DataFrame({"xgf": c.groupby("team").xg.sum(), "gf": c.groupby("team").goal.sum(), "xga": c.groupby("opp").xg.sum(), "ga": c.groupby("opp").goal.sum()})
    gp = pd.concat([keep.home, keep.away]).value_counts()
    t["gp"] = gp
    t["share"] = t.xgf / (t.xgf + t.xga)
    t["fin"] = (t.gf - t.xgf) / t.gp
    t["sv"] = (t.xga - t.ga) / t.gp
    rk = {k: t[k].rank(ascending=False, method="min").astype(int) for k in ("share", "fin", "sv")}
    B, N = t.loc["BUF"], t.loc["NYR"]
    rec = gg.assign(otl=(gg.gf < gg.ga) & gg.last_period_type.isin(["OT", "SO"]))
    W, L, OTL = int(rec.w.sum()), int(((rec.gf < rec.ga) & ~rec.otl).sum()), int(rec.otl.sum())
    assert (W, L, OTL) == (11, 10, 4) and rk["share"]["BUF"] == 22 and rk["fin"]["NYR"] == 30

    # ---- the Ledger
    p = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    pr = p[p.id == PRED].iloc[0]
    me = gr[gr.prediction_id == PRED].iloc[0]
    m = p.merge(gr, left_on="id", right_on="prediction_id")
    m = m[m.id <= PRED]
    right = int((((m.probability > 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))).sum())
    assert (float(pr.probability), int(me.outcome), round(float(me.brier), 2), right, len(m)) == (0.49, 1, 0.26, 13, 22)

    # ---- chart: cumulative scoring and goaltending vs. chances, game by game
    gg["fin_c"] = (gg.ngf - gg.xgf).cumsum()
    gg["sv_c"] = (gg.xga - gg.nga).cumsum()
    xs = np.arange(1, len(gg) + 1)
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=200)
    ax.axhline(0, color="#D5D8DE", lw=1)
    ax.axvspan(len(early) + 0.5, len(gg) + 0.5, color="#EEF2F9", zorder=0)
    ax.plot(xs, gg.fin_c, color=BLUE, lw=2.2, marker="o", ms=4, label="Scoring: goals minus what their chances were worth")
    ax.plot(xs, gg.sv_c, color=RED, lw=2.2, marker="o", ms=4, label="Goaltending: chances against minus goals allowed")
    for col, colr in (("fin_c", BLUE), ("sv_c", RED)):
        lo = gg[col].idxmin()
        ax.annotate(f"{gg.loc[lo, col]:+.1f}", (xs[gg.index.get_loc(lo)], gg.loc[lo, col]), xytext=(0, -14), textcoords="offset points",
                    ha="center", fontsize=9, color=colr, fontweight="bold")
        ax.annotate(f"{gg[col].iloc[-1]:+.1f}", (xs[-1], gg[col].iloc[-1]), xytext=(8, 0), textcoords="offset points", va="center",
                    fontsize=9.5, color=colr, fontweight="bold")
    ax.text(len(early) + 0.8, max(gg.fin_c.max(), gg.sv_c.max()) + 0.6, f"Last {l['n']} games:\n{l['gf']} goals on chances\nworth {l['xgf']:.1f}", fontsize=9, color=INK, va="top")
    ax.set_xlim(0.5, len(gg) + 2)
    ax.set_ylim(min(gg.fin_c.min(), gg.sv_c.min()) - 1.2, max(gg.fin_c.max(), gg.sv_c.max()) + 0.8)
    ax.set_xlabel("Sabres game, 2026-27")
    ax.set_ylabel("Goals above (+) or below (-) the chances, season so far")
    ax.legend(loc="lower left", fontsize=9, frameon=False)
    ax.grid(axis="y", color="#EEF0F3")
    fig.subplots_adjust(left=0.08, right=0.95, bottom=0.14, top=0.8)
    finish(fig, "The Sabres' early bad luck has evened out",
           f"Running total through {len(gg)} games. Zero means the Sabres scored, or allowed, exactly what their chances were worth.", "x")
    fig.texts[-1].set_text(f"Source: NHL play-by-play; Buffalo Quant Desk chance model. Empty-net goals left out. Games through {as_of}.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    bl = [r.name for r in goals[goals.team == "BUF"].itertuples()]
    gl = ", ".join(bl[:-1]) + " and " + bl[-1]
    md = f"""# Sabres 5, Rangers 1: a hot week cancels out a cold start

**Through {e['n']} games the Sabres had scored {e['gf']} goals on chances worth {e['xgf']:.0f}, and allowed {e['ga']} on chances worth {e['xga']:.0f}. Four games later,
both running totals are back near zero. Wednesday was the latest: even chances, {x_b:.1f} to {x_n:.1f}, and a {int(g.home_score)}-{int(g.away_score)} win. A hot four games has
cancelled out the cold start, and the hot streak is no more likely to last than the cold start was. Underneath, the Sabres get {B.share:.0%} of the chances
in their games, {ordn(rk['share']['BUF'])} in the NHL.**

![The Sabres' early bad luck has evened out]({PNG})

## The game

Both teams had {int(sog['BUF'])} shots on goal. Buffalo's goals came from {gl}. New York's lone goal was {long_g['name']}'s shot from {long_g.dist:.0f} feet,
a chance worth about {long_g.xg:.0%} of a goal. {buf_goalie} stopped everything else, about {x_n - 1:.1f} goals better than the chances he faced.

At the other end, the Rangers started {nyr_goalie}, who has been taking turns with {other} since early November. {nyr_goalie.split()[-1]} had saved about
{k_before:.1f} more goals than an average goalie would have in his first {k_games} games.
On Wednesday he allowed {int(g.home_score)} on chances worth {x_b:.1f}.

## How we count chances

Every shot that isn't blocked gets a value: the share of similar shots that go in, based on distance, angle, shot type and whether it's a rebound or rush.
Buffalo's closest goal came from {close_b.dist:.0f} feet, a chance worth about {close_b.xg:.0%}. Add up a team's shots and you get what its chances
were worth in goals. Score more than that and you finished well; allow fewer and your goalie saved some.

**How we checked it.** The model's values are set so that, across the league, chances add up to goals: this season its raw values came to
{raw_lg:.0f} goals and teams scored {lg_goals} on those shots, so we scaled them by {cal:.3f}. And in the [Tampa recap](sabres-lightning-postgame-nov-22.html)
we checked what carries over: a team's share of chances in the first half of a season predicts the second half far better than its finishing or goaltending.

## The season, evened out

| | Games | Goals | Chances worth | Goals allowed | Chances against worth |
|---|---|---|---|---|---|
| First {e['n']} games | {e['n']} | {e['gf']} | {e['xgf']:.1f} | {e['ga']} | {e['xga']:.1f} |
| Last {l['n']} games | {l['n']} | {l['gf']} | {l['xgf']:.1f} | {l['ga']} | {l['xga']:.1f} |

*Goals in the table leave out empty-net and shootout goals.*

Over the whole season, the Sabres have now scored {abs(tot_fin):.1f} {"more" if tot_fin > 0 else "fewer"} goals than their chances were worth, and their goalies
have allowed {abs(tot_sv):.1f} {"more" if tot_sv < 0 else "fewer"} than expected. Both are close to zero.
Not counting empty nets, they've been outscored {gf_ne}-{ga_ne}, almost exactly what their chances say ({xgf_t:.1f} to {xga_t:.1f}).

## What to expect

Finishing and goaltending streaks come and go; a team's chances carry over far better than either. The Sabres get {B.share:.0%} of the chances,
{ordn(rk['share']['BUF'])} in the league. Expect them to look like that team, a little below average, rather than the one that
scored {l['gf_all']} in four games.

## Receipts

- **Our preview** said the Rangers' poor finishing ({ordn(rk['fin']['NYR'])} in the NHL) probably wouldn't last and their goaltending would probably cool off.
  It also said one game wouldn't settle either. On Wednesday New York scored {int(g.away_score)} goal on chances worth {x_n:.1f}, and {nyr_goalie.split()[-1]} allowed
  {int(g.home_score)} on chances worth {x_b:.1f}. Both are season-long calls, and we'll keep tracking them.
- **The Ledger** gave the Sabres {pr.probability:.0%}. They won, so the call leaned the wrong way and counts as a miss, though the chances themselves came out
  close to even. On our scorecard, where 0 is perfect and a coin flip scores 0.25, it scored {me.brier:.2f}. Our record is {right} of {len(m)}.

## For the stat-heads

- Rangers starters since Nov. 7 (first goalie faced each game): {", ".join(names[x].split()[-1] for x in starters)}.
- xG model: unblocked non-empty-net shots, rescaled so 2026-27 league xG equals league goals through {as_of} (factor {cal:.3f}).
- Game: xGF {x_b:.2f}, xGA {x_n:.2f}; all situations. Korpisalo GSAx {x_b - int(g.home_score):+.2f} on the night, {k_before:+.2f} in {k_games} games before it.
- Season ({len(gg)} games): xGF% {B.share:.3f} ({ordn(rk['share']['BUF'])}); finishing (G - xG) {B.fin:+.2f} per game ({ordn(rk['fin']['BUF'])}); GSAx {B.sv:+.2f} per game ({ordn(rk['sv']['BUF'])}).
- Ledger {PRED}: p = {pr.probability:.2f}, outcome {int(me.outcome)}, Brier {me.brier:.4f}. "Right" = the side above 50% won.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Sabres 5, Rangers 1",
        "big": [[l["gf"], f"Sabres goals in the last {l['n']} games, not counting empty-net goals"], [round(l["xgf"], 1), "what those chances were worth"]],
        "note": f"Early bad luck has evened out. The Sabres get {B.share:.0%} of the chances, {ordn(rk['share']['BUF'])} in the NHL: that's the part that lasts.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
