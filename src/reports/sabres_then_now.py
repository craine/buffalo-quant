"""Sabres: same 8-9-4 start as last year's 50-win team. What's different now.

Compares the Sabres' first 21 games of 2026-27 with the first 21 of 2025-26 (and with the 61 games that followed last year).
Every number computed here from raw_nhl_* and the shot/xG table; xG rescaled per season so league xG = league goals.
Pinned to games through AS_OF. Roster moves (Tuch, Byram) are sourced in the story, not computed.
Writes reports/2026-11-18-sabres-then-now.md, two PNGs and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, INK, MUTED
from src.reports.sabres_postgame import finish

OUT = ROOT / "reports"
US, LY, TY = "BUF", 20252026, 20262027
AS_OF = "2026-11-17"
GRAY = "#9AA3B2"
PP = ("5v4", "5v3", "4v3")
TUCH, BENSON, THOMPSON, UPL = 8477949, 8484145, 8479420, 8480045
TEAMS = {"BOS": "Boston", "MTL": "Montreal", "WPG": "Winnipeg", "CBJ": "Columbus"}
W = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def record(gg):
    gf = np.where(gg.home == US, gg.home_score, gg.away_score)
    ga = np.where(gg.home == US, gg.away_score, gg.home_score)
    ot = gg.last_period_type.isin(["OT", "SO"]).to_numpy()
    w, otl, l = int((gf > ga).sum()), int(((gf < ga) & ot).sum()), int(((gf < ga) & ~ot).sum())
    return w, l, otl, 2 * w + otl, int(gf.sum()), int(ga.sum())


def main(as_of=AS_OF):
    s = shots()
    g = query(f"SELECT g.game_id, g.season, g.game_date, g.home, g.away, g.home_score, g.away_score, g.last_period_type "
              f"FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id WHERE c.game_type = 2 AND g.game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(g.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    allg = s[(s.unblocked == 1) & (s.goal == 1)]  # every non-shootout goal, empty nets included
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name

    bg = g[(g.home == US) | (g.away == US)].sort_values("game_date").copy()
    bg["n"] = bg.groupby("season").cumcount() + 1
    ty, ly = bg[bg.season == TY], bg[bg.season == LY]
    N = int(ty.n.max())
    assert N == 21 and len(ly) == 82
    ly_start, ly_rest = ly[ly.n <= N], ly[ly.n > N]
    r_ty, r_lys, r_lyr, r_ly = record(ty), record(ly_start), record(ly_rest), record(ly)
    assert r_ty[:3] == r_lys[:3] == (8, 9, 4) and r_ly[0] == 50

    def part(ids):
        x = u[u.game_id.isin(ids)]
        f, a = x[x.team == US], x[x.opp == US]
        pk = a[a.strength.isin(PP)]
        z = allg[allg.game_id.isin(ids)]
        return dict(n=len(ids), gf_all=int((z.team == US).sum()), ga_all=int((z.opp == US).sum()),
                    en_a=int(((z.opp == US) & (z.empty_net_against == 1)).sum()), xgf=f.xg.sum(), xga=a.xg.sum(), gf=int(f.goal.sum()), ga=int(a.goal.sum()),
                    ev_f=f[f.strength == "5v5"].xg.sum(), ev_a=a[a.strength == "5v5"].xg.sum(),
                    pk_x=pk.xg.sum(), pk_g=int(pk.goal.sum()), pk_n=len(pk),
                    ev_ga=int(a[a.strength == "5v5"].goal.sum()), ev_gf=int(f[f.strength == "5v5"].goal.sum()))
    A, B, R = part(set(ly_start.game_id)), part(set(ty.game_id)), part(set(ly_rest.game_id))
    for P in (A, B, R):
        P["fin"] = P["gf"] - P["xgf"]
        P["save"] = P["xga"] - P["ga"]
        P["share"] = P["xgf"] / (P["xgf"] + P["xga"])

    ratio = A["pk_g"] / A["pk_x"]
    assert 0.4 < ratio < 0.6
    pk_ratio_word = "half"
    # league ranks this season (per game)
    x = u[u.season == TY]
    gp = pd.concat([g[g.season == TY].home, g[g.season == TY].away]).value_counts()
    xga_pg = x.groupby("opp").xg.sum() / gp
    xgf_pg = x.groupby("team").xg.sum() / gp
    pkx_pg = x[x.strength.isin(PP)].groupby("opp").xg.sum() / gp
    pkg = x[x.strength.isin(PP)].groupby("opp").goal.sum()
    rk_xga = int(xga_pg.rank(method="min").loc[US])          # 1 = fewest allowed
    rk_xgf = int(xgf_pg.rank(method="min", ascending=False).loc[US])
    lg_xga = float(xga_pg.mean())
    pkg_pg = pkg / gp
    rk_pkg = int(pkg_pg.rank(method="min", ascending=False).loc[US])   # 1 = most PP goals allowed per game
    tie_pkg = int((pkg_pg == pkg_pg.loc[US]).sum()) > 1
    ev_pg = x[x.strength == "5v5"].groupby("opp").xg.sum() / gp
    rk_ev = int(ev_pg.rank(method="min", ascending=False).loc[US]); lg_ev = float(ev_pg.mean())
    rk_pkx = int(pkx_pg.rank(method="min", ascending=False).loc[US]); lg_pkx = float(pkx_pg.mean())
    pk_extra = float(pkx_pg.loc[US] - lg_pkx)
    pk_share = pk_extra / float(xga_pg.loc[US] - lg_xga)
    assert 0.4 < pk_share < 0.6  # text says "about half"
    pk_rest = pk_extra * (82 - N)
    pk_shots_pg, lg_pk_shots = B["pk_n"] / N, len(x[x.strength.isin(PP)]) / gp.sum()
    ev_share = B["ev_f"] / (B["ev_f"] + B["ev_a"])
    by = x.groupby(["opp", "strength"]).xg.sum().unstack(fill_value=0).div(gp, axis=0)
    gap = by.loc[US] - by.mean()
    gap_ot, gap_ev = float(gap.get("3v3", 0)), float(gap.get("5v5", 0))
    assert pk_extra > 2 * max(gap_ot, gap_ev)  # PK is the biggest single piece
    every_n = 1 / pk_extra
    def per_shot(P): return P["pk_x"] / P["pk_n"]
    shot_up = per_shot(B) / per_shot(A) - 1
    assert 0.2 < shot_up < 0.4  # "about 30%"

    # how rare last year's run was: goals minus chances (both ends), games 22+, every team-season 2023-24..2025-26
    gl = pd.concat([g.assign(team=g.home), g.assign(team=g.away)]).sort_values("game_date")
    gl["n"] = gl.groupby(["season", "team"]).cumcount() + 1
    rows = []
    for (ss, tm), y in gl[gl.season < TY].groupby(["season", "team"]):
        ids = set(y[y.n > N].game_id)
        z = u[u.game_id.isin(ids)]
        f, a = z[z.team == tm], z[z.opp == tm]
        rows.append((ss, tm, (f.goal.sum() - f.xg.sum() + a.xg.sum() - a.goal.sum()) / len(ids)))
    luck = pd.DataFrame(rows, columns=["season", "team", "pg"]).sort_values("pg", ascending=False).reset_index(drop=True)
    buf_rank = int(luck.index[(luck.team == US) & (luck.season == LY)][0]) + 1
    assert buf_rank == 1
    second = luck.iloc[1]

    # goalies: Luukkonen last year (first 21 / rest), this year
    def gk(ids, gid):
        a = u[u.game_id.isin(ids) & (u.opp == US) & (u.goalie_id == gid)]
        return a.game_id.nunique(), a.xg.sum() - a.goal.sum()
    upl_a, upl_r, upl_t = gk(set(ly_start.game_id), UPL), gk(set(ly_rest.game_id), UPL), gk(set(ty.game_id), UPL)
    assert names.get(UPL) == "Ukko-Pekka Luukkonen"

    # players
    def shooter(ids, pid):
        f = u[u.game_id.isin(ids) & (u.team == US) & (u.shooter_id == pid)]
        return int(f.goal.sum()), f.xg.sum(), len(f)
    tuch_ly = shooter(set(ly.game_id), TUCH)
    tuch_ty = shooter(set(ty.game_id), TUCH)
    ben = shooter(set(ty.game_id), BENSON)
    tom = shooter(set(ty.game_id), THOMPSON)
    assert tuch_ty[2] == 0 and names.get(TUCH) == "Alex Tuch" and names.get(BENSON) == "Zach Benson"
    team_ty = u[u.game_id.isin(set(ty.game_id)) & (u.team == US)]
    pl = team_ty.groupby("shooter_id").agg(g_=("goal", "sum"), xg=("xg", "sum"))
    pl["d"] = pl.g_ - pl.xg
    assert pl.d.idxmin() == BENSON
    tuch_ly_rank = int((u[u.game_id.isin(set(ly.game_id)) & (u.team == US)].groupby("shooter_id").apply(
        lambda d: d.goal.sum() - d.xg.sum(), include_groups=False).rank(ascending=False, method="min")).loc[TUCH])

    # GM: shooters 4+ goals behind their chances after 21 team games, 2023-24..2025-26, and what they did after
    rows = []
    for (ss, tm), y in gl[gl.season < TY].groupby(["season", "team"]):
        e_ids, l_ids = set(y[y.n <= N].game_id), set(y[y.n > N].game_id)
        e = u[(u.team == tm) & u.game_id.isin(e_ids)].groupby("shooter_id").agg(g1=("goal", "sum"), x1=("xg", "sum"))
        l = u[(u.team == tm) & u.game_id.isin(l_ids)].groupby("shooter_id").agg(g2=("goal", "sum"), x2=("xg", "sum"))
        rows.append(e.join(l, how="inner"))
    cold = pd.concat(rows); cold = cold[cold.g1 - cold.x1 <= -4]
    cold_n, cold_after = len(cold), cold.g2.sum() / cold.x2.sum()
    assert 0.9 < cold_after < 1.1  # text: "almost exactly what their chances were worth"
    bs = u[(u.shooter_id == BENSON) & (u.season < TY)].groupby("season").agg(g_=("goal", "sum"), x_=("xg", "sum"))
    assert len(bs) == 3 and (bs.g_ == 10).all() and (bs.g_ < bs.x_).all()
    tu = u[u.shooter_id == TUCH].groupby("season").agg(g_=("goal", "sum"), x_=("xg", "sum"), tm=("team", "first"))
    assert tu.loc[TY, "tm"] == "WSH" and (tu.loc[[LY - 10001, LY], "g_"] > tu.loc[[LY - 10001, LY], "x_"]).all()
    pf = u[u.season < TY].groupby(["shooter_id", "season"]).agg(g_=("goal", "sum"), x_=("xg", "sum")).reset_index()
    pf = pf[pf.x_ >= 10].assign(d=lambda d: d.g_ - d.x_).pivot(index="shooter_id", columns="season", values="d").dropna()
    steady = pf[(pf > 0).all(axis=1)]
    luck_n = len(pf) * float((pf > 0).mean().prod())  # if beating your chances were a coin flip each year
    buf_now = set(u[(u.season == TY) & (u.team == US)].shooter_id)
    buf_steady = [names.get(i) for i in steady.index if i in buf_now]
    assert sorted(buf_steady) == ["Rasmus Dahlin", "Tage Thompson"]
    gks = u[u.game_id.isin(set(ty.game_id)) & (u.opp == US)].groupby("goalie_id").apply(lambda d: d.xg.sum() - d.goal.sum(), include_groups=False)
    assert len(gks) == 3 and (gks < 0).all()

    def all_goals(pid, season):
        return int(((allg.shooter_id == pid) & (allg.season == season)).sum())
    assert all_goals(THOMPSON, TY) == tom[0]  # Thompson's goals include no empty-netters
    ben_all_ty, tuch_all_ly, tuch_all_ty = all_goals(BENSON, TY), all_goals(TUCH, LY), all_goals(TUCH, TY)
    ben_all = [all_goals(BENSON, ss) for ss in bs.index]
    assert ben_all_ty == ben[0] + 1  # 'his other goal'
    upl_gsax = float(gks.loc[UPL]); others = gks.drop(UPL)
    assert (others.abs() < 1).all()  # "the other two about average"
    ppx = x[x.strength.isin(PP)]
    pp_pg = ppx.groupby("team").xg.sum() / gp
    ppg_pg = ppx.groupby("team").goal.sum() / gp
    rk_ppx = int(pp_pg.rank(ascending=False, method="min").loc[US]); rk_ppg = int(ppg_pg.rank(ascending=False, method="min").loc[US])
    tie_ppg = int((ppg_pg == ppg_pg.loc[US]).sum()) > 1
    pp_g, pp_x = int(ppx[ppx.team == US].goal.sum()), float(ppx[ppx.team == US].xg.sum())
    assert 12 <= rk_ppx <= 20 and rk_ppg >= 25   # "league-average chances", "near the bottom in goals"
    # published what-ifs from our Nov. 15 playoff story (games through Nov. 14); read from the file so they can't drift
    import re
    po = (OUT / "2026-11-15-sabres-playoff-chances.md").read_text()
    def row(label):
        m = re.search(r"\| " + re.escape(label) + r" \| (\d+)% \|", po); assert m, label; return int(m.group(1))
    assert "0.2 more" in po  # the what-if's offense step is 0.2 goals' worth a game = one every 5 games
    wi = dict(now=row("As things stand"), pk=row("Scoring chances allowed while shorthanded cut to league average"),
              d=row("All scoring chances allowed cut to league average"), o=row("Create 0.2 more goals' worth of scoring chances a game"),
              both=row("Both: average defense and 0.2 more created"))
    assert "we'd have given them 12%" in po and "Of the 23 teams the model gave between 5% and 30%" in po and "3\nmade it" in po
    last = bg[bg.game_date <= as_of].iloc[-1]
    assert last.game_date == "2026-11-17" and "PHI" in (last.home, last.away)

    # next game
    nxt = query(f"SELECT game_date, home, away FROM raw_nhl_schedule WHERE season={TY} AND game_type=2 AND (home='{US}' OR away='{US}') "
                f"AND game_date > '{as_of}' ORDER BY game_date LIMIT 1").iloc[0]
    assert nxt.home == "WSH"

    # ---- chart 1: points by game, both seasons
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    for d, col, lab, ls in ((ly, GRAY, "2025-26 (50 wins)", (0, (4, 1.5))), (ty, BLUE, "2026-27", "-")):
        gf = np.where(d.home == US, d.home_score, d.away_score)
        ga = np.where(d.home == US, d.away_score, d.home_score)
        pts = np.where(gf > ga, 2, np.where(d.last_period_type.isin(["OT", "SO"]), 1, 0)).cumsum()
        ax.plot(np.r_[0, d.n], np.r_[0, pts], color=col, lw=2.6, ls=ls, label=lab)
    ax.axvline(N, color="#D5D8DE", lw=1, ls="--")
    ax.annotate(f"Game {N}: both {r_ty[0]}-{r_ty[1]}-{r_ty[2]}, {r_ty[3]} points", (N, r_ty[3]), xytext=(12, 40), textcoords="offset points",
                fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate(f"Last year's next {len(ly_rest)} games:\n{r_lyr[0]}-{r_lyr[1]}-{r_lyr[2]}", (82, r_ly[3]), xytext=(0, -150), ha='right', textcoords="offset points",
                fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlabel("Game number"); ax.set_ylabel("Points (running total)"); ax.set_xlim(0, 84)
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Same start: the Sabres were {r_ty[0]}-{r_ty[1]}-{r_ty[2]} after {N} games both seasons",
           "Points by game number. Last season's team went on to win 50 games.",
           f"Regular season. 2026-27 through {pd.to_datetime(as_of):%b. %-d}, 2026.")
    fig.texts[-1].set_text(f"Source: NHL game results.\nRegular season. 2026-27 through {pd.to_datetime(as_of):%b. %-d}, 2026.")
    fig.savefig(OUT / "sabres-then-now-points.png"); plt.close(fig)

    # ---- chart 2: first 21 games side by side
    assert B["pk_g"] == 3 * A["pk_g"]  # subtitle says "three times as many"
    labs = ["Chances created\n(worth, in goals)", "Goals scored", "Chances allowed\n(worth, in goals)", "Goals allowed",
            "Power-play goals\nallowed"]
    av = [A["xgf"], A["gf_all"], A["xga"], A["ga_all"], A["pk_g"]]
    bv = [B["xgf"], B["gf_all"], B["xga"], B["ga_all"], B["pk_g"]]
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=200)
    xs = np.arange(len(labs)); w = 0.38
    ax.bar(xs - w / 2, av, w, color=GRAY, label=f"2025-26, first {N} games", zorder=2)
    ax.bar(xs + w / 2, bv, w, color=BLUE, label=f"2026-27, first {N} games", zorder=2)
    for i in range(len(labs)):
        fm = ".1f" if i in (0, 2) else ".0f"
        ax.text(xs[i] - w / 2, av[i] + 0.8, f"{av[i]:{fm}}", ha="center", fontsize=9.5, color=MUTED)
        ax.text(xs[i] + w / 2, bv[i] + 0.8, f"{bv[i]:{fm}}", ha="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_xticks(xs, labs, fontsize=9); ax.set_ylim(0, max(av + bv) * 1.18)
    ax.legend(frameon=False, loc="upper right", fontsize=9); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "This year's Sabres allow more chances and score less",
           f"First {N} games, both seasons. Chances = every shot's chance of going in, added up. Power-play goals allowed tripled.",
           "Chances: shots that weren't blocked, empty nets excluded. Goals: every goal except shootouts.")
    fig.savefig(OUT / "sabres-then-now-compare.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.4), dpi=200)
    cats = ["Five-on-five", "Shorthanded\n(opponent's power play)"]
    bufv, lgv = [ev_pg.loc[US], pkx_pg.loc[US]], [lg_ev, lg_pkx]
    ys = np.arange(2); h = 0.36
    ax.barh(ys + h / 2, lgv, h, color=GRAY, label="League average", zorder=2)
    ax.barh(ys - h / 2, bufv, h, color=BLUE, label="Sabres", zorder=2)
    for i in range(2):
        ax.text(lgv[i] + 0.02, ys[i] + h / 2, f"{lgv[i]:.2f}", va="center", fontsize=9.5, color=MUTED)
        ax.text(bufv[i] + 0.02, ys[i] - h / 2, f"{bufv[i]:.2f}  ({ordn_([rk_ev, rk_pkx][i])}-most of 32)", va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_yticks(ys, cats); ax.invert_yaxis(); ax.set_xlim(0, max(bufv + lgv) * 1.35)
    ax.set_xlabel("Chances allowed per game (worth, in goals)")
    ax.legend(frameon=False, loc="lower right", fontsize=9); ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "The Sabres defend like an average team at full strength. Not a man down.",
           f"Chances allowed per game, 2026-27. At full strength Buffalo is average; a man down it's {ordn_(rk_pkx)}-most.",
           f"Regular season through {pd.to_datetime(as_of):%b. %-d}, 2026. Shots that weren't blocked, empty nets excluded. {N} Sabres games.")
    fig.savefig(OUT / "sabres-then-now-gm.png"); plt.close(fig)

    md = f"""# If I were the Sabres' GM, I wouldn't sell. Here's how I'd fix this 8-9-4 team

**After {N} games last season, the Sabres were {r_lys[0]}-{r_lys[1]}-{r_lys[2]}. After {N} games this season, they're {r_ty[0]}-{r_ty[1]}-{r_ty[2]}: the same record, to the game.
Last year's team then went {r_lyr[0]}-{r_lyr[1]}-{r_lyr[2]} and won 50.**

It did that without better scoring chances: over those {len(ly_rest)} games it got {R['share']:.0%} of the
chances in its games, an even split. What carried it was goaltending and finishing, and by our count no NHL team in the last three seasons beat its chances
by more over that stretch ({TEAMS.get(second.team, second.team)} came close). This year's team is creating a few more chances than last year's did at this point, but it's giving up more, it's scoring less than its chances
are worth, and its penalty kill has allowed {B['pk_g']} goals to last year's {A['pk_g']}. My plan, in short: fix the penalty kill first, keep the five-on-five lineup, be patient with the shooters, and don't sell. If the penalty kill is still leaking
at the 40-game mark, that's when I'd trade, for help a man down. Below: what's different, and why I'd do it that way.

*Numbers are through {pd.to_datetime(as_of):%b. %-d}, 2026: the first {N} games of each season. {N} games is a small sample. The Sabres visit Alex Tuch and
Washington on {pd.Timestamp(nxt.game_date).strftime('%A')}.*

![Points by game](sabres-then-now-points.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. A shot from within 10 feet goes in about 1 time in 7; one from 60 feet
or more, about 1 in 125. Add up those chances on every shot and you get what a team's chances were worth in goals. The shot locations come from the NHL's own
play-by-play, and our model is explained in our story on [last year's 50-win season](sabres-50-win-mirage.html). We count every shot that wasn't blocked, including ones that missed the net, and leave out shots at an empty net, since
there's no goalie to beat. Goal totals in the table count every goal except shootouts; when we compare goals with chances, we leave out empty-net goals the same way.

## Same record, different team

![First {N} games compared](sabres-then-now-compare.png)

| First {N} games | 2025-26 | 2026-27 |
|---|---|---|
| Record | {r_lys[0]}-{r_lys[1]}-{r_lys[2]} | {r_ty[0]}-{r_ty[1]}-{r_ty[2]} |
| Chances created (worth this many goals) | {A['xgf']:.1f} | {B['xgf']:.1f} |
| Goals scored | {A['gf_all']} | {B['gf_all']} |
| Chances allowed (worth this many goals) | {A['xga']:.1f} | {B['xga']:.1f} |
| Goals allowed | {A['ga_all']} | {B['ga_all']} |
| Power-play goals allowed | {A['pk_g']} | {B['pk_g']} |

Three things are different.

**1. They give up more chances, and the penalty kill is the worst of it.** This season's chances against are worth {B['xga'] / N:.2f} goals a game, {B['xga'] / N - A['xga'] / N:.2f} more than
at this point last year, the {ordn_(33 - rk_xga)}-most of 32 teams per game (league average {lg_xga:.2f}). At full strength, five-on-five, Buffalo is right at the league
average ({ev_pg.loc[US]:.2f} a game against {lg_ev:.2f}). A man down, it allows the {ordn_(rk_pkx)}-most; more on that below. The goals-allowed total hasn't moved: {A['ga_all']} last year, {B['ga_all']}
this year. But {A['en_a']} of last year's were into an empty net, against {B['en_a']} this year, so with a goalie in net this year's team has allowed {B['ga'] - A['ga']} more.

**2. The puck stopped going in.** Not counting empty nets, last year's team scored {A['gf']} goals in its first {N} games on chances worth {A['xgf']:.1f}, about {A['fin']:.0f} more
than an average team would have. This year's has scored {B['gf']} on chances worth {B['xgf']:.1f}, about {abs(B['fin']):.0f} fewer. So the Sabres are creating more chances than
last year ({ordn_(rk_xgf)} of 32 teams, right in the middle) and scoring less. The biggest gap is Zach Benson: {ben[2]} shots at a goalie that weren't blocked, worth about {ben[1]:.1f} goals,
and {W[ben[0]]} goal to show for it. (His other goal was into an empty net.) Tage Thompson, with {tom[0]} goals on chances worth {tom[1]:.1f}, is the biggest exception.

**3. Power-play goals against: the jump from {A['pk_g']} to {B['pk_g']} is mostly how many went in.** Opponents have scored {B['pk_g']} power-play goals on Buffalo in {N} games, {'tied for ' if tie_pkg else ''}the {ordn_(rk_pkg)}-most in the league
per game. At this point last year it was {A['pk_g']}. Those power-play chances were worth {B['pk_x']:.1f} goals this year and {A['pk_x']:.1f} last year, on {B['pk_n']} shots this year
and {A['pk_n']} last year (counting shots that missed the net, not blocked ones): fewer shots, but better ones. The average power-play shot against has been about {shot_up:.0%} more dangerous.
Last year's {A['pk_g']} was unusually low, too: about {pk_ratio_word} what those chances were worth.

## Who's gone

Two regulars from last season aren't on the team. Alex Tuch went to Washington in a sign-and-trade in June, and Bowen Byram was traded to Chicago in a deal for the
No. 4 pick in the draft (sources below). Tuch scored {tuch_ly[0]} goals with a goalie in net last season ({tuch_all_ly} in all) on chances worth {tuch_ly[1]:.1f}, about {tuch_ly[0] - tuch_ly[1]:.0f} more than an average
shooter would have, and {'no Sabre beat his chances by more' if tuch_ly_rank == 1 else 'the ' + ordn_(tuch_ly_rank) + '-most on the team'}. That's a lot of finishing to replace, and so far, as a team, they haven't.
We can't yet tie the extra chances allowed to Byram's departure; that would take more games and a player-by-player look.

## What turned last season around

Last year's team barely changed how many chances it created or allowed. Over its last {len(ly_rest)} games its chances were worth {R['xgf'] / len(ly_rest):.2f} goals a game for and {R['xga'] / len(ly_rest):.2f} against,
about even. What changed was everything after the shot:

- **Goaltending.** Ukko-Pekka Luukkonen was {abs(upl_a[1]):.1f} goals worse than an average goalie in his first {upl_a[0]} games, then {upl_r[1]:.1f} goals better over his next {upl_r[0]}.
  As a team, Buffalo's goalies allowed about {R['save']:.0f} fewer goals than the chances against were worth. This season Luukkonen is
  {abs(upl_t[1]):.1f} goals {'worse' if upl_t[1] < 0 else 'better'} than average in {upl_t[0]} games.
- **Finishing.** The team kept scoring: about {R['fin']:.0f} more goals than its chances were worth over the last {len(ly_rest)} games.

Put together, last year's Sabres scored and saved about {R['fin'] + R['save']:.0f} more goals than their chances were worth over those {len(ly_rest)} games, more than one
every other night. Of all {len(luck)} NHL teams over the last three seasons ({len(luck) // 3} a year), that was the most over the same stretch, just ahead of
{'last season' + chr(39) + 's ' + TEAMS.get(second.team, second.team) if int(second.season) == LY else TEAMS.get(second.team, second.team)}.

## If I were GM

*The numbers are Buffalo Quant Desk's. The calls are mine. — Charlie*

Last season's run came with the best goaltending-and-finishing stretch of any team in three years, barely ahead of {TEAMS.get(second.team, second.team)}'s, and as we
found in that [50-win study](sabres-50-win-mirage.html), that kind of luck doesn't carry over well. Chances do: this year's team is a little better on offense and worse
on defense. So here's what I'd do, in order, and how much our numbers can back up each move.

![Chances allowed, five-on-five vs. shorthanded](sabres-then-now-gm.png)

**1. Cut the chances allowed a man down.** The penalty kill is the biggest single source of the extra chances. A man down, Buffalo gives up an extra goal's worth of
chances about every {every_n:.0f} games compared with an average team, about half of its whole gap to a league-average defense. Five-on-five is almost none of it; the next-biggest
piece is overtime. If this pace held, getting the penalty kill to average would take away chances worth about {pk_rest:.0f} goals over the last {82 - N} games. This
year's penalty kill faces fewer shots than last year's, just better ones. So the job is fewer, and less dangerous, shots while a man down. That's as much a coaching
job as a roster one. (Buffalo also faces {pk_shots_pg:.1f} power-play shots a game that aren't blocked, against {lg_pk_shots:.1f} for the average team; we can't
yet tell how much of that is taking more penalties, because we haven't finished checking the NHL's penalty data.)

**2. Don't blow up the five-on-five lineup.** At full strength the Sabres get {ev_share:.0%} of the chances in their games, about even, and allow chances at a league-average
rate. The balance of chances is the part of a team's game that carries over best, and at full strength Buffalo's isn't broken.

**3. Be patient with the shooters.** Over the last three seasons, {cold_n} NHL players (a small group) were 4 or more goals behind their chances after their team's first {N} games. The rest of
those seasons, as a group, they scored almost exactly what their chances were worth. A cold start is a bad reason to trade a shooter. One caution: Benson has scored
10 goals with a goalie in net in each of the last three seasons ({', '.join(map(str, ben_all[:-1]))} and {ben_all[-1]} counting empty nets), on chances worth {bs.x_.min():.0f} to {bs.x_.max():.0f} each year. He creates chances; the goals may not catch up.

**4. Leave Buffalo's own power play alone.** When the Sabres have the extra man, they create chances at a league-average rate ({ordn_(rk_ppx)} of 32 teams per game) but {'they' + chr(39) + 're tied for' if tie_ppg else 'they rank'} {ordn_(rk_ppg)} in goals:
{pp_g} on chances worth {pp_x:.1f}. That's the same cold finishing as above, not a broken power play, and finishing tends to even out. Small sample, too.

**5. When I do shop, look for proven finishers.** Over a few weeks, finishing swings a lot. Over three years, some of it holds. Tuch scored {tu.loc[LY - 10001, 'g_'] - tu.loc[LY - 10001, 'x_']:.0f} and {tu.loc[LY, 'g_'] - tu.loc[LY, 'x_']:.0f} more goals than his chances
were worth the last two seasons (the year before he missed by a fraction of a goal), and has {tu.loc[TY, 'g_']} goals with a goalie in net ({tuch_all_ty} in all) on chances worth {tu.loc[TY, 'x_']:.1f} in Washington. Of {len(pf)} players whose chances were worth 10 or more goals in each
of the last three seasons, {len(steady)} beat their chances in all three, about {len(steady) - luck_n:.0f} more than luck alone would produce. That's about 1 in 4: finishing is real, but it's not common. Buffalo has two, Thompson and Rasmus Dahlin.
That's the profile I'd look for. I don't know who's available or what they'd cost.

**6. Don't plan on the goalies to save it.** Luukkonen is {abs(upl_gsax):.1f} goals worse than an average goalie this season and the other two are about average, a combined
{abs(B['save']):.1f} goals worse than the chances against were worth. Goaltending was the biggest piece of last year's run (about {R['save']:.0f} of the {R['fin'] + R['save']:.0f} goals),
and it's the hardest part to predict. I'd hope for it, but I wouldn't build the plan on it.

### What it adds up to

Our [playoff chances story](sabres-playoff-chances.html) reran the season with one thing changed at a time, using games through Nov. 14, before the Nov. 17 loss to Philadelphia:

| If the Sabres... | Playoff chance |
|---|---|
| Stay as they are | {wi['now']}% |
| Cut the chances they allow a man down to league average | {wi['pk']}% |
| Cut all the chances they allow to league average | {wi['d']}% |
| Create one more goal's worth of chances every {round(1 / 0.2):.0f} games | {wi['o']}% |
| Do both: league-average defense and one more goal's worth of chances every {round(1 / 0.2):.0f} games | {wi['both']}% |

**My call: don't sell.** After 20 games last season our model would have given the Sabres a 12% playoff chance, and they finished with {r_ly[3]} points. Of the 23
teams it gave between 5% and 30% at the same point over the last three seasons, 3 made it. A team at {wi['now']}% isn't done. Cutting the chances allowed a man down to league average, on its own, moves it to {wi['pk']}%. Fix the defense and create a little more, and it's about a coin flip.
I'd start in-house with the penalty kill. If it's still leaking by the 40-game mark, that's when I'd trade, and I'd go for help a man down first, then a proven finisher. Not a goalie.

## Sources for the roster moves

- Tuch: [Daily Faceoff](https://www.dailyfaceoff.com/news/alex-tuch-washington-capitals-buffalo-sabres-sign-trade-contract-free-agency), June 24, 2026 (sign-and-trade to Washington).
- Byram: [Daily Faceoff](https://www.dailyfaceoff.com/news/bowen-byram-trade-chicago-blackhawks-buffalo-sabres-nhl-draft-4th-overall-pick), June 23, 2026 (to Chicago with Jordan Greenway for the No. 4 pick, a second-round pick and Louis Crevier).

## For the stat-heads

- xG: our gradient-boosted model, unblocked non-empty-net shots, rescaled per season so league xG = league goals (2025-26 factor {cal.loc[LY]:.3f}, 2026-27 {cal.loc[TY]:.3f}).
  2025-26 shots are in the model's training data; 2026-27 are out of sample.
- First {N} games, 2025-26 vs 2026-27: xGF {A['xgf']:.2f} vs {B['xgf']:.2f}; GF {A['gf']} vs {B['gf']}; xGA {A['xga']:.2f} vs {B['xga']:.2f}; GA {A['ga']} vs {B['ga']}; xGF% {A['share']:.3f} vs {B['share']:.3f}.
  5v5 xGF {A['ev_f']:.2f} vs {B['ev_f']:.2f}, xGA {A['ev_a']:.2f} vs {B['ev_a']:.2f}; 5v5 GF {A['ev_gf']} vs {B['ev_gf']}, GA {A['ev_ga']} vs {B['ev_ga']}.
  Opponent power play (5v4, 5v3, 4v3): {A['pk_n']} vs {B['pk_n']} unblocked shots, xG {A['pk_x']:.2f} vs {B['pk_x']:.2f}, goals {A['pk_g']} vs {B['pk_g']}. Penalty counts not used.
- 2025-26 games {N + 1}-82: {r_lyr[0]}-{r_lyr[1]}-{r_lyr[2]}; xGF {R['xgf']:.2f}, xGA {R['xga']:.2f} (xGF% {R['share']:.3f}); GF-xGF {R['fin']:+.2f}; xGA-GA {R['save']:+.2f}.
  Rank of (GF-xGF)+(xGA-GA) per game over games {N + 1}+ among {len(luck)} team-seasons 2023-24 to 2025-26: 1st ({luck.iloc[0].pg:.3f}); 2nd {second.team} {int(second.season)} ({second.pg:.3f}).
- Luukkonen GSAx: 2025-26 games 1-{N} {upl_a[1]:+.2f} ({upl_a[0]} GP), games {N + 1}+ {upl_r[1]:+.2f} ({upl_r[0]} GP); 2026-27 {upl_t[1]:+.2f} ({upl_t[0]} GP).
- Tuch 2025-26 (BUF, non-empty-net): {tuch_ly[0]} G on {tuch_ly[1]:.2f} xG ({tuch_ly[2]} unblocked). Benson 2026-27: {ben[0]} G on {ben[1]:.2f} xG ({ben[2]}). Thompson 2026-27: {tom[0]} G on {tom[1]:.2f} xG.
- Standings goal totals for the first {N} games (shootout decider counted as a goal): GF {r_lys[4]} vs {r_ty[4]}, GA {r_lys[5]} vs {r_ty[5]}.
- Ranks are per game among 32 teams through {as_of}.
- BUF power play (5v4, 5v3, 4v3) 2026-27: xGF/GP {pp_pg.loc[US]:.3f} ({ordn_(rk_ppx)}), GF/GP {ppg_pg.loc[US]:.3f} ({'T-' if tie_ppg else ''}{ordn_(rk_ppg)}); {pp_g} G on {pp_x:.2f} xG.
- What-if playoff chances are read from reports/2026-11-15-sabres-playoff-chances.md (ratings through 2026-11-14, 20,000 simulated seasons each); not rerun here. Table and chart goals include empty-net goals (2025-26: {A['en_a']} against; 2026-27: {B['en_a']} against)
  and exclude shootouts; G-xG and xGA-GA exclude empty nets. 5v5 xGA/GP: BUF {ev_pg.loc[US]:.3f}, league {lg_ev:.3f} ({ordn_(rk_ev)}-most). Opp-PP xGA/GP: BUF {pkx_pg.loc[US]:.3f},
  league {lg_pkx:.3f} ({ordn_(rk_pkx)}-most); xGA/GP gap by state: 5v5 {gap_ev:+.3f}, 3v3 {gap_ot:+.3f}; opp-PP xG per unblocked shot {per_shot(A):.3f} vs {per_shot(B):.3f}; share of BUF's total xGA/GP gap to average {pk_share:.2f}; times {82 - N} games = {pk_rest:.1f}.
- GM notes: shooters with G-xG <= -4 through team game {N}, 2023-24 to 2025-26 (same team, still shooting after): n={cold_n}, rest-of-season G/xG {cold_after:.3f}.
  Benson G/xG 2023-24 to 2025-26: {', '.join(f'{int(r.g_)}/{r.x_:.1f}' for r in bs.itertuples())}. Tuch G-xG: {', '.join(f'{int(i)}: {r.g_ - r.x_:+.1f} ({r.tm})' for i, r in tu.iterrows())}.
  Three-season finishers (coin-flip baseline {luck_n:.1f}): {len(steady)} of {len(pf)} shooters with xG >= 10 in each of 2023-24 to 2025-26 had G > xG in all three; current Sabres among them: {', '.join(buf_steady)}.
  2026-27 BUF goalies GSAx: {', '.join(f'{names.get(int(i))} {v:+.2f}' for i, v in gks.items())}.
"""
    (OUT / "2026-11-18-sabres-then-now.md").write_text(md)
    (OUT / "2026-11-18-sabres-then-now.hero.json").write_text(json.dumps({
        "label": f"After {N} games",
        "big": [[f"{r_lys[0]}-{r_lys[1]}-{r_lys[2]}", "Sabres, 2025-26 (went on to win 50)"], [f"{r_ty[0]}-{r_ty[1]}-{r_ty[2]}", "Sabres, 2026-27"]],
        "note": (f"Same record. This year's team creates a few more chances, gives up more, scores less than its chances are worth, "
                 f"and has allowed {B['pk_g']} power-play goals to last year's {A['pk_g']} (last year's was unusually low)."),
        "explainer": {"kicker": f"First {N} games", "title": "Power-play goals allowed",
                      "text": "Goals opponents scored on the power play against Buffalo:", "fmt": "num",
                      "bars": [["2025-26", A["pk_g"]], ["2026-27", B["pk_g"]]]},
    }, indent=1))
    print(md)


def ordn_(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


if __name__ == "__main__":
    main()
