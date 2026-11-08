"""Sabres pregame: Vegas at Buffalo, Sun Nov 8, 2026, 3:30 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-08-sabres-vgk-pregame.md, two PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
No win probability: we don't have a tested hockey game model yet.
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
SEASON, US, THEM = 20262027, "BUF", "VGK"
AS_OF = "2026-11-07"  # games through Saturday night; pinned so the published story doesn't change
GOLD = "#B4975A"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def main(as_of=AS_OF):
    s = shots()
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(gm.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    cur = u[u.season == SEASON]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    g26 = gm[gm.season == SEASON]
    last_date = g26.game_date.max()

    # games played and records
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        rows.append(g26.rename(columns={side: "team", f"{side}_score": "gf", f"{opp}_score": "ga"})[["game_id", "game_date", "team", "gf", "ga", "last_period_type"]])
    rec = pd.concat(rows)
    rec["w"] = rec.gf > rec.ga
    rec["otl"] = (rec.gf < rec.ga) & rec.last_period_type.isin(["OT", "SO"])
    rec["l"] = (rec.gf < rec.ga) & ~rec.last_period_type.isin(["OT", "SO"])
    gp = rec.groupby("team").game_id.nunique()

    # team chances (all situations, unblocked, empty net excluded), per game
    t = pd.DataFrame({"xgf": cur.groupby("team").xg.sum(), "xga": cur.groupby("opp").xg.sum(),
                      "gf_sh": cur.groupby("team").goal.sum(), "ga_sh": cur.groupby("opp").goal.sum(),
                      "close_f": cur[cur.dist < 20].groupby("team").size(), "close_a": cur[cur.dist < 20].groupby("opp").size(),
                      "reb_f": cur[cur.rebound == 1].groupby("team").size(), "reb_a": cur[cur.rebound == 1].groupby("opp").size(),
                      "reb_xgf": cur[cur.rebound == 1].groupby("team").xg.sum(), "reb_xga": cur[cur.rebound == 1].groupby("opp").xg.sum()}).fillna(0)
    t["gp"] = gp.reindex(t.index)
    for c in ["xgf", "xga", "close_f", "close_a", "reb_f", "reb_a", "reb_xgf", "reb_xga", "gf_sh", "ga_sh"]:
        t[c + "_pg"] = t[c] / t.gp
    t["share"] = t.xgf / (t.xgf + t.xga)
    rk = lambda col, team, high_good=True: int(t[col].rank(ascending=not high_good, method="min").loc[team])
    lg = t[["xgf_pg", "close_f_pg", "reb_f_pg"]].mean()
    b, v = t.loc[US], t.loc[THEM]
    recd = lambda tm: f"{int(rec[rec.team == tm].w.sum())}-{int(rec[rec.team == tm].l.sum())}-{int(rec[rec.team == tm].otl.sum())}"
    gfa = rec.groupby("team").agg(GF=("gf", "sum"), GA=("ga", "sum"))

    # last 5 games: share of chances
    def last5(tm):
        ids = rec[rec.team == tm].sort_values("game_date").game_id.tail(5)
        x = cur[cur.game_id.isin(ids)]
        f_, a_ = x[x.team == tm].xg.sum(), x[x.opp == tm].xg.sum()
        return f_ / (f_ + a_), len(ids)
    b5, nb5 = last5(US)
    l5 = rec[rec.team == US].sort_values("game_date").tail(5)
    l5_rec = f"{int(l5.w.sum())}-{int(l5.l.sum())}-{int(l5.otl.sum())}"
    v5, nv5 = last5(THEM)

    # explainer examples (prior seasons, so not circular)
    pri = u[u.season < SEASON]
    close10 = pri[pri.dist < 10].goal.mean()
    far60 = pri[pri.dist >= 60].goal.mean()
    reb_rate, non_rate = pri[pri.rebound == 1].goal.mean(), pri[pri.rebound == 0].goal.mean()
    n_pri = len(pri)

    # goalies: goals saved vs an average goalie this season
    gk = cur[cur.goalie_id.notna()].groupby(["opp", "goalie_id"]).agg(gp=("game_id", "nunique"), sog=("on_goal", "sum"),
                                                                         xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["gsax"] = gk.xga - gk.ga
    gk["name"] = gk.goalie_id.map(names)
    gk["sv"] = 1 - gk.ga / gk.sog
    gk["rk"] = gk.gsax.rank(ascending=False, method="min").astype(int)
    n_gk = len(gk)
    bg = gk[gk.opp == US].sort_values("gp", ascending=False)
    vg = gk[gk.opp == THEM].sort_values("gp", ascending=False)

    # ---- chart 1: every team's chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab in ((US, BLUE, "Sabres"), (THEM, GOLD, "Golden Knights")):
        r = t.loc[tm]
        ax.scatter(r.xgf_pg, r.xga_pg, s=140, color=col, zorder=3, edgecolor="white", lw=1.5)
        ax.annotate(lab, (r.xgf_pg, r.xga_pg), xytext=(8, 6), textcoords="offset points", fontsize=11, fontweight="bold", color=INK)
    mx, my = t.xgf_pg.mean(), t.xga_pg.mean()
    ax.axvline(mx, color="#D5D8DE", lw=1, ls="--"); ax.axhline(my, color="#D5D8DE", lw=1, ls="--")
    ax.invert_yaxis()
    ax.text(t.xgf_pg.max(), t.xga_pg.min(), "Create a lot,\nallow little", ha="right", va="top", fontsize=9, color=MUTED)
    ax.text(t.xgf_pg.min(), t.xga_pg.max(), "Create little,\nallow a lot", ha="left", va="bottom", fontsize=9, color=MUTED)
    ax.set_xlabel("Chances created per game (goals they were worth)")
    ax.set_ylabel("Chances allowed per game (lower is better, so it's flipped)")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Vegas allows the {ordn(rk('xga_pg', THEM, False))}-fewest chances. Buffalo allows the {ordn(33 - rk('xga_pg', US, False))}-most",
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Golden Knights {int(v.gp)}.")
    fig.savefig(OUT / "sabres-vgk-chances.png"); plt.close(fig)

    # ---- chart 2: rebounds — Sabres creating vs Vegas allowing, among 32 teams
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.9), dpi=200)
    for ax, col, tm, title, lab in ((axes[0], "reb_f_pg", US, "Rebound shots created per game", "Sabres"),
                                    (axes[1], "reb_a_pg", THEM, "Rebound shots allowed per game", "Golden Knights")):
        srt = t[col].sort_values(ascending=False)
        cols = [(BLUE if tm == US else GOLD) if i == tm else "#C9CDD4" for i in srt.index]
        ax.bar(range(32), srt.values, color=cols, width=0.8, zorder=2)
        i = list(srt.index).index(tm)
        r_ = rk(col, tm, high_good=(tm == US))
        ax.text(i, srt.loc[tm] + 0.08, f"{lab}\n{srt.loc[tm]:.1f} ({ordn(r_)}{'' if tm == US else ' fewest'})", ha="center", va="bottom", fontsize=9.5, color=INK)
        ax.axhline(srt.mean(), color=INK, lw=1, ls="--")
        ax.set_xticks([]); ax.set_xlabel("32 teams, most to fewest")
        ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        ax.set_ylim(0, srt.max() * 1.3); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Buffalo is {ordn(rk('reb_f_pg', US))} at creating rebound shots; Vegas is {ordn(rk('reb_a_pg', THEM, False))} at preventing them",
           "A rebound shot comes within 3 seconds of another shot by the same team. Dashed line: league average.",
           f"2026-27 through {pd.to_datetime(last_date):%b. %-d}. Unblocked shots, empty net excluded.")
    fig.savefig(OUT / "sabres-vgk-rebounds.png"); plt.close(fig)

    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Golden Knights'} | {r['name']} | {int(r.gp)} | {r.sv:.3f} | {r.gsax:+.1f} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    rb_rk_f, rb_rk_a = rk("reb_f_pg", US), rk("reb_a_pg", THEM, high_good=False)
    md = f"""# Sabres vs. Golden Knights: Buffalo's attack meets one of the NHL's toughest defenses

**Finding: Vegas allows chances worth {v.xga_pg:.2f} goals a game, the {ordn(rk('xga_pg', THEM, False))}-fewest in the NHL, and few shots from close to its net
({ordn(rk('close_a_pg', THEM, False))}-fewest). Buffalo's attack is middle of the pack ({ordn(rk('xgf_pg', US))} in chances created) but {ordn(rb_rk_f)} at creating rebound
shots. The bigger worry is at the other end: the Sabres allow chances worth {b.xga_pg:.2f} goals a game, {ordn(rk('xga_pg', US, False))} of 32.**

*Vegas at Buffalo, Sunday, Nov. 8, 3:30 p.m. ET, KeyBank Center. Numbers are 2026-27 through {pd.to_datetime(last_date):%B %-d}: Sabres
{recd(US)} in {int(b.gp)} games, Golden Knights {recd(THEM)} in {int(v.gp)}. This is a preview, not a prediction: we don't put a win chance on
a hockey game until our game model has been tested on past seasons, and it hasn't been yet.*

![Chances created vs allowed](sabres-vgk-chances.png)

## How we measure "chances"

Every shot has odds of going in, based on where it was taken and what kind of shot it was. Over the last three seasons
({n_pri:,} unblocked shots), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}. Add
up the odds on every shot and you get what a team's chances were worth in goals.

**The source:** the NHL's own play-by-play feed, which records where every shot came from. **The math:** each shot's odds
come from our model, built on past seasons and checked on a season it never saw; we nudge each season's totals so the
league's chances add up to the league's real goals. **How we checked it:** the full explanation, with the chart, is in our
story on [last year's 50-win season](sabres-50-win-mirage.html).

## The two teams, side by side

| Per game, 2026-27 | Sabres | Golden Knights | League average |
|---|---|---|---|
| Chances created (goals they were worth) | {b.xgf_pg:.2f} ({ordn(rk('xgf_pg', US))}) | {v.xgf_pg:.2f} ({ordn(rk('xgf_pg', THEM))}) | {lg.xgf_pg:.2f} |
| Chances allowed | {b.xga_pg:.2f} ({ordn(rk('xga_pg', US, False))}) | {v.xga_pg:.2f} ({ordn(rk('xga_pg', THEM, False))}) | {lg.xgf_pg:.2f} |
| Share of the chances in their games | {b.share:.1%} ({ordn(rk('share', US))}) | {v.share:.1%} ({ordn(rk('share', THEM))}) | 50% |
| Goals scored, actual | {gfa.loc[US].GF / b.gp:.2f} | {gfa.loc[THEM].GF / v.gp:.2f} | |
| Goals allowed, actual | {gfa.loc[US].GA / b.gp:.2f} | {gfa.loc[THEM].GA / v.gp:.2f} | |
| Shots from within 20 feet | {b.close_f_pg:.1f} ({ordn(rk('close_f_pg', US))}) | {v.close_f_pg:.1f} ({ordn(rk('close_f_pg', THEM))}) | {lg.close_f_pg:.1f} |
| Shots allowed from within 20 feet | {b.close_a_pg:.1f} ({ordn(rk('close_a_pg', US, False))}) | {v.close_a_pg:.1f} ({ordn(rk('close_a_pg', THEM, False))}) | {lg.close_f_pg:.1f} |
| Share of chances, last {nb5} games | {b5:.1%} | {v5:.1%} | |

Ranks are among 32 teams; 1st is best (most created, fewest allowed). Actual goals come from final scores; chances leave
out empty-net shots.

## The matchup to watch: rebounds

A rebound shot catches the goalie moving. Over the last three seasons, rebounds went in {reb_rate:.1%} of the time, about
{reb_rate / non_rate:.1f} times the {non_rate:.1%} rate for every other shot.

![Rebounds](sabres-vgk-rebounds.png)

Buffalo gets {b.reb_f_pg:.1f} rebound shots a game ({ordn(rb_rk_f)} of 32; league average {lg.reb_f_pg:.1f}), worth {b.reb_xgf_pg:.2f} goals a game. Friday's
10 against Columbus was its season high. Vegas allows {v.reb_a_pg:.1f} a game, {ordn(rb_rk_a)} of 32 at keeping them down. Vegas's strength
is keeping shots away from the net in the first place. How many second looks Buffalo gets anyway is the part of this
matchup to watch.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good.

| Team | Goalie | Games | Save rate | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. Buffalo has been alternating goalies, which points to
Colten Ellis on Sunday (WGR and Buffalo Hockey Beat both expect him). Vegas hadn't named a starter when we
published; NHL.com projects Adin Hill. These are small samples: a goalie's numbers over a dozen games can swing a lot.

## What to watch

- **Second chances.** Count Buffalo's shots that come right after another shot. The Sabres' season average is {b.reb_f_pg:.1f}.
- **The goalies.** Whichever goalies start, the table above says how they've done against the chances they've faced.
- **Results vs. chances.** Buffalo is {l5_rec} in its last {nb5} games but has had only {b5:.0%} of the chances in them. Winning
  while getting out-chanced usually doesn't last; Sunday is a test of whether the Sabres can win the chances, too.
- **Whether the chances turn into goals.** Over a full season, chances carry over from year to year much better than lucky
  or unlucky finishing, which is why we lead with them.

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so
  league xG = league goals (2026-27 factor {cal.loc[SEASON]:.3f}). Share = xGF / (xGF + xGA). Rebound = shot within 3 s of a same-team
  unblocked attempt. Close = within 20 ft. GSAx = xG against minus goals against on unblocked shots, empty net excluded.
- Data through {last_date} ({len(g26)} games). Last-{nb5} shares use each team's five most recent games.
- No game probability is published: there is no backtested NHL game model in this repo yet.
"""
    (OUT / "2026-11-08-sabres-vgk-pregame.md").write_text(md)
    (OUT / "2026-11-08-sabres-vgk-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres vs. Vegas, 3:30 p.m.: the matchup",
        "big": [[f"{b.reb_f_pg:.1f}", f"Sabres rebound shots a game ({ordn(rb_rk_f)} of 32)"],
                [f"{v.reb_a_pg:.1f}", f"Rebound shots Vegas allows a game ({ordn(rb_rk_a)} fewest)"]],
        "note": f"Rebounds go in {reb_rate:.1%} of the time, about {reb_rate / non_rate:.1f} times the rate of other shots.",
        "explainer": {"kicker": "How we know", "title": "Every shot has odds.",
                      "text": (f"A shot from within 10 feet went in {close10:.1%} of the time over the last three seasons; from 60 feet or more, "
                               f"{far60:.1%}. Add up the odds on every shot and you get what a team's chances were worth in goals."),
                      "fmt": "pct", "bars": [["Rebounds", round(float(reb_rate), 3)], ["Other shots", round(float(non_rate), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
