"""Sabres pregame: Buffalo at Dallas, Sat Nov 14, 2026, 8:00 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-14-sabres-dal-pregame.md, three PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
Win chance from nhl_game_model v0.1, tested on 2025-26 and 2026-27 games it never saw.
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.ledger import nhl_game_model as gmod
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
import src.reports.sabres_postgame as spg
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
SEASON, US, THEM = 20262027, "BUF", "DAL"
AS_OF = "2026-11-12"  # games through Thursday night; neither team plays Friday; pinned so the published story doesn't change
GOLD = "#006847"  # Stars green
GAME_DATE = "2026-11-14"
RATINGS_BEFORE = "2026-11-13"   # ratings use games before this date (= through AS_OF); Friday games excluded
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def main(as_of=AS_OF):
    s = shots()
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(gm.game_id))].copy()
    missing = set(gm[gm.season == SEASON].game_id) - set(s[s.season == SEASON].game_id)
    assert not missing, f"clean_nhl_shots_xg is missing {len(missing)} games; run src.clean.nhl and src.metrics.nhl_xg first"
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
    tot = gk.groupby("goalie_id").gsax.sum()          # rank each goalie once, even if he played for two teams
    gk["rk"] = gk.goalie_id.map(tot.rank(ascending=False, method="min").astype(int))
    n_gk = len(tot)
    bg = gk[gk.opp == US].sort_values("gp", ascending=False)
    vg = gk[gk.opp == THEM].sort_values("gp", ascending=False)

    # ---- game prediction (NHL game model v0.1), pinned to games before Nov 8
    tg, coef, p_ot, home_rate = gmod.train()
    off_r, def_r, lg_r, ratio = gmod.ratings(tg, SEASON, RATINGS_BEFORE)   # games through AS_OF only, so re-runs reproduce the story
    mu_b = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, US, THEM), 0)
    mu_v = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, THEM, US), 1)
    p_v, p_tie = gmod.win_prob(mu_v, mu_b, p_ot)
    p_b = 1 - p_v
    bt = {}
    for ss, mxd in ((20252026, None), (SEASON, as_of)):
        fr = gmod.build_frame(tg, [ss], max_date=mxd)
        gr = gmod.baselines(tg, gmod.game_rows(fr, coef, p_ot), home_rate)
        bt[ss] = dict(n=len(gr), brier=gmod.brier(gr.p_home, gr.home_won), b_home=gmod.brier(gr.b_home, gr.home_won),
                      b_rec=gmod.brier(gr.b_record, gr.home_won), right=((gr.p_home > .5) == gr.home_won).mean(),
                      home_obs=gr.home_won.mean(), g=gr)
    g25 = bt[20252026]["g"]
    fav = g25.p_home.where(g25.p_home >= .5, 1 - g25.p_home)
    fav_won = ((g25.p_home >= .5) == g25.home_won)
    cal_bins = [(0.5, 0.55), (0.55, 0.6), (0.6, 0.65), (0.65, 1.0)]
    calb = [(f"{int(lo*100)}-{int(min(hi,0.99)*100)}%" if hi < 1 else f"{int(lo*100)}%+", fav[(fav >= lo) & (fav < hi)].mean(),
            fav_won[(fav >= lo) & (fav < hi)].mean(), int(((fav >= lo) & (fav < hi)).sum())) for lo, hi in cal_bins]
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.model_version == gmod.VERSION] if not lp.empty else lp
    lp = lp[lp.claim_text.str.contains("Stars", na=False)] if len(lp) else lp
    ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min().replace("T", " ").rstrip("Z")} UTC, before puck drop.** It gets graded after the game, hit or miss."
                     if len(lp) else "**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before puck drop; "
                     "every logged call is graded after the game, hit or miss.")

    # ---- why goalies aren't in the model: half-season repeatability, goalies vs team chances allowed (complete seasons only)
    gg = gmod.goalie_games()
    rep_g, rep_t = [], []
    for ss in (20232024, 20242025, 20252026):
        x = gg[gg.season == ss]; mid = x.game_date.sort_values().iloc[len(x) // 2]
        h1 = x[x.game_date < mid].groupby("goalie_id").agg(sh=("shots", "sum"), xga=("xga", "sum"), ga=("ga", "sum"))
        h2 = x[x.game_date >= mid].groupby("goalie_id").agg(sh=("shots", "sum"), xga=("xga", "sum"), ga=("ga", "sum"))
        jj = h1.join(h2, lsuffix="1", rsuffix="2"); jj = jj[(jj.sh1 >= 400) & (jj.sh2 >= 400)]
        rep_g.append(np.corrcoef((jj.xga1 - jj.ga1) / jj.sh1, (jj.xga2 - jj.ga2) / jj.sh2)[0, 1])
        y = tg[tg.season == ss]; mid = y.game_date.sort_values().iloc[len(y) // 2]
        a1 = y[y.game_date < mid].groupby("team").xga.mean(); a2 = y[y.game_date >= mid].groupby("team").xga.mean()
        rep_t.append(np.corrcoef(a1, a2.reindex(a1.index))[0, 1])
    g_lo, g_hi, t_lo, t_hi = min(rep_g), max(rep_g), min(rep_t), max(rep_t)

    # ---- chart 3: how the model's chances held up on 2025-26
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(len(calb)); w = 0.36
    fav_p = max(p_b, 1 - p_b)
    bin_i = next(k for k, (lo, hi) in enumerate(cal_bins) if lo <= fav_p < hi)
    ax.bar(xs - w / 2, [c[1] for c in calb], w, color=GRAY, label="What the model said (likelier team's chance)", zorder=2)
    ax.bar(xs + w / 2, [c[2] for c in calb], w, color=BLUE, label="How often the likelier team actually won", zorder=2)
    for x_, c in zip(xs, calb):
        ax.text(x_ - w / 2, c[1] + 0.01, f"{c[1]:.0%}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.text(x_ + w / 2, c[2] + 0.01, f"{c[2]:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_xticks(xs, [f"Likelier team given {c[0]}\n({c[3]} games)" for c in calb], fontsize=9.5)
    ax.set_ylim(0, 0.9); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Teams given {calb[bin_i][0]}, like Dallas on Saturday, won {calb[bin_i][2]:.0%} in 2025-26",
           f"Every 2025-26 game ({bt[20252026]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-dal-model-test.png"); plt.close(fig)

    # ---- chart 1: every team's chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab in ((US, BLUE, "Sabres"), (THEM, GOLD, "Stars")):
        r = t.loc[tm]
        ax.scatter(r.xgf_pg, r.xga_pg, s=140, color=col, zorder=3, edgecolor="white", lw=1.5)
        ax.annotate(lab, (r.xgf_pg, r.xga_pg), xytext=(8, 6), textcoords="offset points", fontsize=11, fontweight="bold", color=INK)
    mx, my = t.xgf_pg.mean(), t.xga_pg.mean()
    ax.axvline(mx, color="#D5D8DE", lw=1, ls="--"); ax.axhline(my, color="#D5D8DE", lw=1, ls="--")
    ax.invert_yaxis()
    ax.text(t.xgf_pg.max(), t.xga_pg.min(), "Create a lot,\nallow little", ha="right", va="top", fontsize=9, color=MUTED)
    ax.text(t.xgf_pg.min(), t.xga_pg.max(), "Create little,\nallow a lot", ha="left", va="bottom", fontsize=9, color=MUTED)
    ax.set_xlabel("Chances created per game (goals they were worth)")
    ax.set_ylabel("Chances allowed per game (better defense is higher)")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Dallas allows the {ordn(rk('xga_pg', THEM, False))}-fewest chances. Buffalo allows the {ordn(33 - rk('xga_pg', US, False))}-most",
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Stars {int(v.gp)}.")
    fig.savefig(OUT / "sabres-dal-chances.png"); plt.close(fig)

    # ---- the "bounce-back game": next-game results by the margin of the previous game (games through AS_OF)
    lng = pd.concat([gm.assign(team=gm.home, gf=gm.home_score, ga_=gm.away_score, is_home=1),
                     gm.assign(team=gm.away, gf=gm.away_score, ga_=gm.home_score, is_home=0)])[["game_id", "season", "game_date", "team", "gf", "ga_", "is_home"]]
    lng["game_date"] = pd.to_datetime(lng.game_date)
    lng = lng.sort_values(["team", "game_date"])
    lng["margin"] = lng.gf - lng.ga_
    lng["prev"] = lng.groupby(["team", "season"]).margin.shift()
    lng["won"] = (lng.margin > 0).astype(int)
    lng = lng[lng.prev.notna()]
    labs = ["Lost by 4+", "Lost by 1-3", "Won by 1-3", "Won by 4+"]
    lng["bucket"] = pd.cut(lng.prev, [-99, -4, -1, 3, 99], labels=labs)
    raw = lng.groupby("bucket", observed=True).won.agg(["size", "mean"])
    n_blow, w_blow = int(raw.loc["Lost by 4+", "size"]), raw.loc["Lost by 4+", "mean"]
    w_other = lng[lng.bucket != "Lost by 4+"].won.mean()
    mrows = []
    for ss, mxd in ((20252026, None), (SEASON, as_of)):
        mrows.append(gmod.game_rows(gmod.build_frame(tg, [ss], max_date=mxd), coef, p_ot))
    mrows = pd.concat(mrows)
    oos = lng.astype({"game_id": "int64"}).merge(mrows[["game_id", "p_home"]].astype({"game_id": "int64"}), on="game_id")
    oos["p"] = np.where(oos.is_home == 1, oos.p_home, 1 - oos.p_home)
    ob = oos[oos.bucket == "Lost by 4+"]
    ob_n, ob_said, ob_won = len(ob), ob.p.mean(), ob.won.mean()
    ob_se = (ob_won * (1 - ob_won) / ob_n) ** 0.5
    oth_said = oos[oos.bucket != "Lost by 4+"].p.mean()
    dal_last = lng[(lng.team == THEM)].sort_values("game_date").iloc[-1]
    buf_last2 = lng[(lng.team == US)].sort_values("game_date").iloc[-2:]
    assert dal_last.margin == -5 and pd.Timestamp(dal_last.game_date) == pd.Timestamp(last_date)
    _src, spg.SRC = spg.SRC, "Source: NHL final scores and schedule (league game feed)."   # win rates only, no chances model
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(4)
    cols = [BLUE if l == "Lost by 4+" else "#C9CDD4" for l in labs]
    ax.bar(xs, [raw.loc[l, "mean"] for l in labs], 0.6, color=cols, zorder=2)
    for x_, l in zip(xs, labs):
        ax.text(x_, raw.loc[l, "mean"] + 0.01, f"{raw.loc[l, 'mean']:.0%}", ha="center", va="bottom", fontsize=10.5, color=INK)
    ax.axhline(0.5, color="#D5D8DE", lw=1, ls="--")
    ax.set_xticks(xs, [f"{l}\n({int(raw.loc[l, 'size']):,} games)" for l in labs], fontsize=10)
    ax.set_xlabel("How the team's previous game went"); ax.set_ylabel("How often it won the next game")
    ax.set_ylim(0, 0.7); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"No bounce-back: after a blowout loss, teams won {w_blow:.0%} of their next game",
           "Next-game win rate, by the score of the team's previous game. Any win counts (regulation, overtime, shootout).",
           f"Regular-season NHL games, 2023-24 through {pd.to_datetime(last_date):%b. %-d}, 2026; a team's first game of each season left out.")
    fig.savefig(OUT / "sabres-dal-bounce.png"); plt.close(fig)
    spg.SRC = _src

    if __import__("os").environ.get("DUMP"):
        print("REC", recd(US), recd(THEM), "GP", b.gp, v.gp, "last", last_date)
        print(t.loc[[US, THEM], ["xgf_pg","xga_pg","share","close_f_pg","close_a_pg","reb_f_pg","reb_a_pg"]].round(3).to_string())
        for c,h in [("xgf_pg",1),("xga_pg",0),("share",1),("close_f_pg",1),("close_a_pg",0),("reb_f_pg",1),("reb_a_pg",0)]:
            print(c, "BUF", rk(c,US,bool(h)), "TBL", rk(c,THEM,bool(h)))
        print("GF/GA pg", (gfa.loc[US]/b.gp).round(2).to_dict(), (gfa.loc[THEM]/v.gp).round(2).to_dict())
        print("last5", round(b5,3), l5_rec, round(v5,3)); print("model p_b", round(p_b,3), "mu", round(mu_b,2), round(mu_v,2), "tie", round(p_tie,3))
        print("goalies"); print(pd.concat([bg,vg])[["opp","name","gp","sv","gsax","rk"]].round(3).to_string())
        print("calb", [(c[0], round(c[1],3), round(c[2],3), c[3]) for c in calb]); print("season test", bt[SEASON]["n"], round(bt[SEASON]["right"],3), round(bt[SEASON]["home_obs"],3))
        return
    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]} | \
           {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies_league.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Stars'} | {link(r['name'])} | {int(r.gp)} | {r.sv:.1%} | {('0.0, about average,' if abs(r.gsax) < 0.05 else f'{r.gsax:+.1f}')} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    # the first meeting, Oct. 8 in Buffalo
    m1 = gm[(gm.season == SEASON) & (((gm.home == US) & (gm.away == THEM)) | ((gm.home == THEM) & (gm.away == US)))]
    assert len(m1) == 1
    m1 = m1.iloc[0]
    m1u = u[u.game_id == m1.game_id]
    m1_us, m1_them = m1u[m1u.team == US].xg.sum(), m1u[m1u.team == THEM].xg.sum()
    m1_sc_us = int(m1.home_score if m1.home == US else m1.away_score)
    m1_sc_them = int(m1.away_score if m1.home == US else m1.home_score)
    assert (m1_sc_us, m1_sc_them) == (0, 4)
    dal_a = rk("xga_pg", THEM, False)
    buf_gsax_pg = -bg.gsax.sum() / b.gp           # goals a game Buffalo's goalies have allowed beyond an average goalie
    fewest = lambda r_: "fewest" if r_ == 1 else f"{ordn(r_)}-fewest"
    buf_a = 33 - rk("xga_pg", US, False)
    md = f"""# Sabres at Stars: forget the bounce-back game. Dallas is the better team anyway

**Our model gives Dallas a {1 - p_b:.0%} chance to win at home Saturday (Sabres {p_b:.0%}). The Stars allow the {ordn(dal_a)}-fewest chances in the NHL;
the Sabres allow the {ordn(buf_a)}-most. Dallas got blown out 8-3 at home Thursday, so you'll hear about a bounce-back game. The numbers say there's no such
thing: since 2023-24, teams coming off a loss by four or more won {w_blow:.0%} of their next game, a little less often than everyone else ({w_other:.0%}).**

*Buffalo at Dallas, Saturday, Nov. 14, 8 p.m. ET. Neither team has played since Thursday: Buffalo lost 3-2 in overtime at Chicago, Dallas lost 8-3 at home to
Winnipeg. Numbers are 2026-27 through {pd.to_datetime(last_date):%B %-d}: Sabres {recd(US)} in {int(b.gp)} games, Stars {recd(THEM)} in {int(v.gp)}. Early-season ranks can move a lot.*

![Chances created vs allowed](sabres-dal-chances.png)

## The two teams, side by side

| Per game, 2026-27 | Sabres | Stars | League average |
|---|---|---|---|
| Chances created (goals they were worth) | {b.xgf_pg:.2f} ({ordn(rk('xgf_pg', US))}) | {v.xgf_pg:.2f} ({ordn(rk('xgf_pg', THEM))}) | {lg.xgf_pg:.2f} |
| Chances allowed | {b.xga_pg:.2f} ({ordn(rk('xga_pg', US, False))}) | {v.xga_pg:.2f} ({ordn(rk('xga_pg', THEM, False))}) | {lg.xgf_pg:.2f} |
| Share of the chances in their games | {b.share:.1%} ({ordn(rk('share', US))}) | {v.share:.1%} ({ordn(rk('share', THEM))}) | 50% |
| Goals scored, actual | {gfa.loc[US].GF / b.gp:.2f} | {gfa.loc[THEM].GF / v.gp:.2f} | |
| Goals allowed, actual | {gfa.loc[US].GA / b.gp:.2f} | {gfa.loc[THEM].GA / v.gp:.2f} | |
| Shots allowed from within 20 feet | {b.close_a_pg:.1f} ({ordn(rk('close_a_pg', US, False))}) | {v.close_a_pg:.1f} ({ordn(rk('close_a_pg', THEM, False))}) | {lg.close_f_pg:.1f} |
| Rebound shots allowed | {b.reb_a_pg:.1f} ({ordn(rk('reb_a_pg', US, False))}) | {v.reb_a_pg:.1f} ({ordn(rk('reb_a_pg', THEM, False))}) | {lg.reb_f_pg:.1f} |
| Share of chances, last {nb5} games | {b5:.1%} | {v5:.1%} | |

Ranks are among 32 teams; 1st is best (most created, fewest allowed). Actual goals come from final scores; chances leave out empty-net shots.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Over the last three seasons ({n_pri:,} shots that weren't
blocked, not counting empty nets), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}. Add up those chances on
every shot and you get what a team's chances were worth in goals. **The source:** the NHL's own play-by-play feed, which records where every shot came from.
**The math:** each shot's chance comes from our model, built on past seasons and tested on a season it hadn't seen; we nudge each season's totals so the
league's chances add up to the league's real goals. **How we checked it:** the full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).

Here's what that looks like for Buffalo: the chances the Sabres have allowed were worth {b.xga_pg:.2f} goals a game, and they've actually allowed {gfa.loc[US].GA / b.gp:.2f}.
Much of that gap is in goal: Buffalo's goalies have allowed about {buf_gsax_pg:.2f} goals a game more than an average goalie would have on the same shots.

## What makes Dallas hard to play

The Stars don't let teams near the net. They allow {v.close_a_pg:.1f} shots a game from within 20 feet ({fewest(rk('close_a_pg', THEM, False))}) and {v.reb_a_pg:.1f} rebound shots
({fewest(rk('reb_a_pg', THEM, False))}), the two kinds of shots most likely to go in. Buffalo is in the middle of the league at creating chances ({ordn(rk('xgf_pg', US))}) and near
the bottom at preventing them. One caution: when the teams met in Buffalo on Oct. 8, the Sabres actually got the better chances (worth {m1_us:.1f} goals to Dallas's {m1_them:.1f}) and
still lost {m1_sc_them}-{m1_sc_us}. One game is a small sample, and our prediction goes by the full season.

## The bounce-back game

![Bounce-back](sabres-dal-bounce.png)

Dallas lost 8-3 at home Thursday. Buffalo lost 8-3 at home to Tampa Bay on Wednesday. It's natural to think a team comes out angry after a game like that.
We checked every NHL game since 2023-24. Teams coming off a loss by four goals or more won **{w_blow:.0%}** of their next game ({n_blow} games). After any
other result, teams won {w_other:.0%}. A blowout doesn't make a team play better next time; if anything, they win a little less. Part of the reason is simple: teams that get
blown out tend to be a little weaker to begin with.

**Does our model miss it?** Our model never looks at the last score, only at the chances teams create and allow. On games it never saw while it was
being built (last season and this one), it gave teams coming off a blowout loss {ob_said:.0%} on average, against {oth_said:.0%} for everyone else, because those teams
were a little weaker. They won {ob_won:.0%} ({ob_n} games). That gap is small enough to be chance.

That's the opposite of what we found Thursday. Before the [Chicago game](sabres-blackhawks-pregame-nov-12.html), we showed that road teams playing a second night
in a row lose more often than our model says. Being tired is something the model misses; a bad last game isn't. So for Saturday, Dallas's 8-3 loss counts for exactly what its chances were worth, and nothing more.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good. Tap a goalie for his card.

| Team | Goalie | Games played in | Saves | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. We hadn't seen confirmed starters when we published. A goalie's numbers over a dozen
games can swing a lot. We tested adding each game's starting goalie to our prediction and it made it no better: a goalie's goals saved in the first
half of a season tells you little about his second half.

## Our prediction: Stars {1 - p_b:.0%}, Sabres {p_b:.0%}

{ledger_status}

Our model expects about **{mu_v:.1f} goals for Dallas and {mu_b:.1f} for Buffalo**, and gives about a {p_tie:.0%} chance the game is tied after 60 minutes.

**Where the number comes from.** The chances numbers above. Buffalo creates chances worth {b.xgf_pg:.2f} goals a game; Dallas allows {v.xga_pg:.2f}. Early in a season we
blend in last season's numbers and pull everything toward the league average, which makes Buffalo's attack worth {off_r[US]:.2f} a game and Dallas's defense
{def_r[THEM]:.2f}. (The model works with the chances before our small season adjustment, so an average team is {lg_r:.2f} there, against {lg.xgf_pg:.2f} in the table.) We do the same the other way for Dallas. Home ice adds about {coef[2]:.2f} of a goal for the Stars.
Then we play the game out on paper many times; ties after 60 minutes go the way they have for home teams in past overtimes and shootouts ({p_ot:.0%} home wins).

![Model test](sabres-dal-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only what was known before each game.
It called the winner {bt[20252026]['right']:.0%} of the time; choosing the home team every time would have been right {bt[20252026]['home_obs']:.0%}. This season so far ({bt[SEASON]['n']} games) it has called
{bt[SEASON]['right']:.0%} right; home teams have won {bt[SEASON]['home_obs']:.0%}. When it gave a team {calb[bin_i][0]} in 2025-26, as it gives Dallas Saturday, that team won {calb[bin_i][2]:.0%} of the
time ({calb[bin_i][3]} games).

## What to watch

- **Second chances.** Dallas allows the {fewest(rk('reb_a_pg', THEM, False))} rebound shots in the NHL and the {fewest(rk('close_a_pg', THEM, False))} from close in. If Buffalo's
  chances come from the point and the outside, expect a low-scoring night for the Sabres.
- **Buffalo's own end.** The Sabres allow chances worth {b.xga_pg:.2f} goals a game, {ordn(buf_a)}-most in the league. That's the bigger reason our model has Dallas ahead.

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so league xG = league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). Close = within 20 ft; rebound = within 3 s of a same-team unblocked attempt. Data through {last_date} ({len(g26)} games).
- Bounce-back: next-game win rate by previous-game goal margin, same team and season, 2023-24 to {last_date}, regular season, any result counts.
  {'; '.join(f"{l} {raw.loc[l, 'mean']:.3f} (n {int(raw.loc[l, 'size']):,})" for l in labs)}. Model check out of sample (2025-26 and 2026-27 to date), previous loss
  by 4+: mean p {ob_said:.3f}, won {ob_won:.3f}, n {ob_n}, binomial SE {ob_se:.3f}.
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`), ratings from games through {as_of}. Team xGF/xGA per game shrunk with K={gmod.K}
  games toward league + {gmod.PRIOR_KEEP} x last season's edge; goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home (fit 2023-25), on unrescaled xG;
  independent Poisson; regulation ties to home at {p_ot:.3f}. Brier: 2025-26 {bt[20252026]['brier']:.4f} (home-team rate {bt[20252026]['b_home']:.4f}, record log5
  {bt[20252026]['b_rec']:.4f}, coin 0.25); 2026-27 to date {bt[SEASON]['brier']:.4f}. No goalie, rest or last-game term.
- GSAx = xG against minus goals against on unblocked shots, empty net excluded.
"""
    (OUT / "2026-11-14-sabres-dal-pregame.md").write_text(md)
    (OUT / "2026-11-14-sabres-dal-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres at Dallas, Saturday 8 p.m.",
        "big": [[f"{1 - p_b:.0%}", f"Dallas's chance to win, our model (Sabres {p_b:.0%})"],
                [f"{w_blow:.0%}", "How often teams won right after losing by 4+"]],
        "note": (f"Dallas allows the {ordn(dal_a)}-fewest chances in the NHL; Buffalo allows the {ordn(buf_a)}-most. "
                 "And no, Dallas's 8-3 loss Thursday doesn't make a bounce-back more likely."),
        "explainer": {"kicker": "Bounce-back games", "title": "A blowout loss doesn't fire a team up.",
                      "text": "How often teams won their next game since 2023-24, by how the last one went:",
                      "fmt": "pct", "bars": [["After losing by 4+", round(float(w_blow), 3)], ["After any other result", round(float(w_other), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
