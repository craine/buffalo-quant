"""Sabres pregame: Buffalo at Tampa Bay, Sun Nov 22, 2026, 5:00 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-22-sabres-tbl-pregame.md, three PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
Win chance from nhl_game_model v0.1 (the same model and inputs src/ledger/log_sabres_tbl_nov22.py logs). Pinned to games through AS_OF.
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
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
SEASON, LY, US, THEM = 20262027, 20252026, "BUF", "TBL"
AS_OF = "2026-11-21"            # games through Saturday (all 14 final)
RATINGS_BEFORE = "2026-11-22"   # ratings use games before this date (= through AS_OF)
GAME_DATE = "2026-11-22"
RED_W = "#002868"               # Lightning blue
PP = ("5v4", "5v3", "4v3")
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def main(as_of=AS_OF):
    s = shots()
    gm = query(f"SELECT g.* FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id WHERE c.game_type = 2 AND g.game_date <= '{as_of}'")
    sched_day = query(f"SELECT game_id FROM raw_nhl_schedule WHERE game_type = 2 AND season = {SEASON} AND game_date <= '{as_of}'")
    assert set(sched_day.game_id) <= set(gm.game_id), "not every scheduled game through AS_OF is in raw_nhl_games; re-run the NHL ingest"
    s = s[s.game_id.isin(set(gm.game_id))].copy()
    missing = set(gm[gm.season == SEASON].game_id) - set(s[s.season == SEASON].game_id)
    assert not missing, f"clean_nhl_shots_xg is missing {len(missing)} games"
    allg = s[(s.unblocked == 1) & (s.goal == 1)]
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    cur = u[u.season == SEASON]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    g26 = gm[gm.season == SEASON]
    last_date = g26.game_date.max()
    assert last_date == as_of

    # records
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        rows.append(g26.rename(columns={side: "team", f"{side}_score": "gf", f"{opp}_score": "ga"})[["game_id", "game_date", "team", "gf", "ga", "last_period_type"]])
    rec = pd.concat(rows)
    ot = rec.last_period_type.isin(["OT", "SO"])
    rec["w"], rec["otl"], rec["l"] = rec.gf > rec.ga, (rec.gf < rec.ga) & ot, (rec.gf < rec.ga) & ~ot
    gp = rec.groupby("team").game_id.nunique()
    recd = lambda tm: f"{int(rec[rec.team == tm].w.sum())}-{int(rec[rec.team == tm].l.sum())}-{int(rec[rec.team == tm].otl.sum())}"
    pts = lambda tm: int(2 * rec[rec.team == tm].w.sum() + rec[rec.team == tm].otl.sum())
    gfa = rec.groupby("team").agg(GF=("gf", "sum"), GA=("ga", "sum"))

    # team chances, per game
    pp = cur[cur.strength.isin(PP)]
    t = pd.DataFrame({"xgf": cur.groupby("team").xg.sum(), "xga": cur.groupby("opp").xg.sum(),
                      "ev_f": cur[cur.strength == "5v5"].groupby("team").xg.sum(), "ev_a": cur[cur.strength == "5v5"].groupby("opp").xg.sum(),
                      "pp_x": pp.groupby("team").xg.sum(), "pp_g": pp.groupby("team").goal.sum(),
                      "pk_x": pp.groupby("opp").xg.sum(), "pk_g": pp.groupby("opp").goal.sum()}).fillna(0)
    t["gp"] = gp.reindex(t.index)
    for c in ["xgf", "xga", "ev_f", "ev_a", "pp_x", "pp_g", "pk_x", "pk_g"]:
        t[c + "_pg"] = t[c] / t.gp
    t["share"] = t.xgf / (t.xgf + t.xga)
    t["ev_share"] = t.ev_f / (t.ev_f + t.ev_a)
    rk = lambda col, team, high=True: int(t[col].rank(ascending=not high, method="min").loc[team])   # high=True: 1 = biggest
    lg = t.mean(numeric_only=True)
    b, v = t.loc[US], t.loc[THEM]

    # recent form, rest, trip
    bl = rec[rec.team == US].sort_values("game_date")
    fl = rec[rec.team == THEM].sort_values("game_date")
    sch = query(f"SELECT game_date, start_utc, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') ORDER BY game_date").reset_index(drop=True)
    i0 = int(sch.index[sch.game_date == GAME_DATE][0])
    assert sch.loc[i0, "home"] == THEM and sch.loc[i0, "start_utc"] == "2026-11-22T22:00:00Z"
    nxt = sch.loc[i0 + 1]
    assert (nxt.game_date, nxt.home) == ("2026-11-25", US)              # then home vs the Rangers
    j = i0
    while j > 0 and sch.loc[j - 1, "away"] == US: j -= 1
    k = i0
    while k + 1 < len(sch) and sch.loc[k + 1, "away"] == US: k += 1
    trip_no, trip_len = i0 - j + 1, k - j + 1
    us_last, them_last = bl.game_date.iloc[-1], fl.game_date.iloc[-1]
    us_off = (pd.Timestamp(GAME_DATE) - pd.Timestamp(us_last)).days - 1
    them_off = (pd.Timestamp(GAME_DATE) - pd.Timestamp(them_last)).days - 1
    assert (trip_no, trip_len, us_off, them_off) == (6, 6, 0, 2), (trip_no, trip_len, us_off, them_off)
    last = bl.iloc[-1]
    assert (int(last.gf), int(last.ga), bool(last.w)) == (3, 4, False)
    f_last = fl.tail(6)
    f6 = (int(f_last.w.sum()), int(f_last.l.sum()), int(f_last.otl.sum()))

    # first meeting, and last season
    m1 = g26[((g26.home == US) & (g26.away == THEM)) | ((g26.home == THEM) & (g26.away == US))]
    assert len(m1) == 1
    m1 = m1.iloc[0]
    m1u = u[u.game_id == m1.game_id]
    m1_sc = {m1.home: int(m1.home_score), m1.away: int(m1.away_score)}
    m1_x = {US: m1u[m1u.team == US].xg.sum(), THEM: m1u[m1u.team == THEM].xg.sum()}
    assert (m1.game_date, m1.home, m1_sc[US], m1_sc[THEM], m1.last_period_type) == ("2026-11-11", US, 3, 8, "REG")
    m1g = allg[allg.game_id == m1.game_id]
    m1_pp = {tm: int(((m1g.team == tm) & m1g.strength.isin(PP)).sum()) for tm in (US, THEM)}
    ly = gm[(gm.season == LY) & (((gm.home == US) & (gm.away == THEM)) | ((gm.home == THEM) & (gm.away == US)))]
    ly_w = int(sum((r.home_score > r.away_score) == (r.home == US) for r in ly.itertuples()))
    assert (ly_w, len(ly)) == (3, 4)

    # scorers
    THOMPSON = 8479420
    gl_ty = allg[allg.season == SEASON].groupby("shooter_id").size()
    g_rank = gl_ty.rank(ascending=False, method="min")
    tied = lambda pid: int((gl_ty == gl_ty[pid]).sum()) > 1
    tom_g, tom_rk = int(gl_ty[THOMPSON]), int(g_rank[THOMPSON])
    fsc = allg[(allg.season == SEASON) & (allg.team == THEM)].groupby("shooter_id").size().sort_values(ascending=False)
    fx = cur[cur.team == THEM].groupby("shooter_id").agg(g=("goal", "sum"), x=("xg", "sum"))
    top2 = sorted(fsc.index[:2], key=lambda i: names[i])
    assert [names[i] for i in top2] == ["Brandon Hagel", "Jake Guentzel"] and int(fsc.iloc[0]) == int(fsc.iloc[1]) == 13
    HAGEL = [i for i in top2 if names[i] == "Brandon Hagel"][0]
    assert fx.x.idxmax() == HAGEL
    hag_x = float(fx.loc[HAGEL].x)
    tb_g = int(fsc.iloc[0])

    # goalies
    gk = cur[cur.goalie_id.notna()].groupby(["opp", "goalie_id"]).agg(gp=("game_id", "nunique"), sog=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["gsax"], gk["name"], gk["sv"] = gk.xga - gk.ga, gk.goalie_id.map(names), 1 - gk.ga / gk.sog
    tot = gk.groupby("goalie_id").gsax.sum()
    gk["rk"] = gk.goalie_id.map(tot.rank(ascending=False, method="min").astype(int))
    n_gk = len(tot)
    bg = gk[gk.opp == US].sort_values("gp", ascending=False)
    vg = gk[gk.opp == THEM].sort_values("gp", ascending=False)

    # explainer
    pri = u[u.season < SEASON]
    close10, far60, n_pri = pri[pri.dist < 10].goal.mean(), pri[pri.dist >= 60].goal.mean(), len(pri)

    # ---- prediction
    tg, coef, p_ot, home_rate = gmod.train()
    off_r, def_r, lg_r, ratio = gmod.ratings(tg, SEASON, RATINGS_BEFORE)
    mu_b = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, US, THEM), 0)
    mu_v = gmod.mu(coef, gmod.raw(off_r, def_r, lg_r, ratio, THEM, US), 1)
    p_v, p_tie = gmod.win_prob(mu_v, mu_b, p_ot)
    p_b = 1 - p_v
    bt = {}
    for ss, mxd in ((LY, None), (SEASON, as_of)):
        fr = gmod.build_frame(tg, [ss], max_date=mxd)
        gr = gmod.baselines(tg, gmod.game_rows(fr, coef, p_ot), home_rate)
        bt[ss] = dict(n=len(gr), brier=gmod.brier(gr.p_home, gr.home_won), b_home=gmod.brier(gr.b_home, gr.home_won),
                      right=((gr.p_home > .5) == gr.home_won).mean(), home_obs=gr.home_won.mean(), p_home=gr.p_home.mean(), g=gr)
    g25 = bt[LY]["g"]
    fav = g25.p_home.where(g25.p_home >= .5, 1 - g25.p_home)
    fav_won = ((g25.p_home >= .5) == g25.home_won)
    cal_bins = [(0.5, 0.55), (0.55, 0.6), (0.6, 0.65), (0.65, 1.0)]
    calb = [(f"{int(lo*100)}-{int(min(hi,0.99)*100)}%" if hi < 1 else f"{int(lo*100)}%+", fav[(fav >= lo) & (fav < hi)].mean(),
             fav_won[(fav >= lo) & (fav < hi)].mean(), int(((fav >= lo) & (fav < hi)).sum())) for lo, hi in cal_bins]
    fav_p = max(p_b, 1 - p_b)
    FAV = "Tampa Bay" if p_b < 0.5 else "Buffalo"
    bin_i = next(i for i, (lo, hi) in enumerate(cal_bins) if lo <= fav_p < hi)
    home_gap = {ss: (bt[ss]["p_home"], bt[ss]["home_obs"], bt[ss]["n"]) for ss in (LY, SEASON)}
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.game_id == "NHL_20262027_2026-11-22_BUF_at_TBL"] if len(lp) else lp
    ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min().replace('T', ' ').rstrip('Z')} UTC, before puck drop.** It gets graded after the game, hit or miss."
                     if len(lp) else "**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before puck drop; "
                     "every logged call is graded after the game, hit or miss.")

    # ---- the three keys: what goes with winning, every regular-season game since 2023-24 through AS_OF
    gl = s[s.goal == 1].sort_values(["game_id", "period", "t"])
    first = gl.groupby("game_id").head(1).set_index("game_id").team
    kr = []
    for side, opp in (("home", "away"), ("away", "home")):
        kr.append(gm.rename(columns={side: "team", f"{side}_score": "gf", f"{opp}_score": "ga"})[["game_id", "season", "team", "gf", "ga"]])
    kr = pd.concat(kr)
    kr = kr[kr.season >= 20232024].copy()
    kr["win"] = kr.gf > kr.ga
    kr["first"] = kr.game_id.map(first) == kr.team
    ppg_a = gl[gl.strength.isin(PP)].groupby(["game_id", "opp"]).size()
    kr["ppga"] = [int(ppg_a.get((gid, tm), 0)) for gid, tm in zip(kr.game_id, kr.team)]
    e5 = u[u.strength == "5v5"]
    e5f, e5a = e5.groupby(["game_id", "team"]).xg.sum(), e5.groupby(["game_id", "opp"]).xg.sum()
    kr["ev_won"] = [e5f.get((gid, tm), 0) > e5a.get((gid, tm), 0) for gid, tm in zip(kr.game_id, kr.team)]
    assert kr.first.notna().all() and abs(kr.win.mean() - 0.5) < 1e-9
    wr = lambda m: (float(kr[m].win.mean()), int(m.sum()))
    K = dict(pp0=wr(kr.ppga == 0), pp1=wr(kr.ppga == 1), pp2=wr(kr.ppga >= 2), f1=wr(kr.first), f0=wr(~kr.first),
             e1=wr(kr.ev_won), e0=wr(~kr.ev_won))
    n_kr, n_seasons = len(kr), kr.season.nunique()
    bk = kr[kr.team == US]; by = bk[bk.season == SEASON]; fy = kr[(kr.team == THEM) & (kr.season == SEASON)]
    BK = dict(pp0=(float(bk[bk.ppga == 0].win.mean()), int((bk.ppga == 0).sum())), pp2=(float(bk[bk.ppga >= 2].win.mean()), int((bk.ppga >= 2).sum())))
    b_first_n, b_first_w = int(by.first.sum()), int(by[by.first].win.sum())
    f_first_n, f_first_w = int(fy.first.sum()), int(fy[fy.first].win.sum())
    b_ev_n, b_ev_w, b_noev_n, b_noev_w = int(by.ev_won.sum()), int(by[by.ev_won].win.sum()), int((~by.ev_won).sum()), int(by[~by.ev_won].win.sum())
    b_pp2_n = int((by.ppga >= 2).sum())
    KEYS_CHECK = (b_first_n, b_first_w, f_first_n, f_first_w, b_ev_n, b_ev_w, b_noev_n, b_noev_w, b_pp2_n)
    otl = set(gm[gm.last_period_type.isin(['OT', 'SO'])].game_id)
    b_first_ot = int(by[by.first & ~by.win].game_id.isin(otl).sum())
    assert b_first_ot == 4
    assert K["pp2"][0] < 0.3 < K["pp1"][0] < K["pp0"][0] and K["f1"][0] > 0.65 and K["e1"][0] > 0.58

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.6), dpi=200, sharey=True)
    panels = [("Power-play goals allowed", [("0", K["pp0"]), ("1", K["pp1"]), ("2+", K["pp2"])]),
              ("First goal", [("Scored it", K["f1"]), ("Allowed it", K["f0"])]),
              ("Five-on-five chances", [("Had more", K["e1"]), ("Had fewer", K["e0"])])]
    for ax, (ttl, bars) in zip(axes, panels):
        xs_ = np.arange(len(bars))
        ax.bar(xs_, [v_[1][0] for v_ in bars], 0.62, color=[BLUE if i == 0 else GRAY for i in range(len(bars))], zorder=2)
        for x_, (lab, (pw, n)) in zip(xs_, bars):
            ax.text(x_, pw + 0.02, f"{pw:.0%}", ha="center", fontsize=11, fontweight="bold", color=INK)
        ax.set_xticks(xs_, [lab for lab, _ in bars], fontsize=10); ax.tick_params(axis="x", length=0)
        ax.set_title(ttl, fontsize=11, color=INK, loc="left")
        ax.axhline(0.5, color="#D5D8DE", lw=1, ls="--", zorder=1)
        ax.set_ylim(0, 0.85); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0)); axes[0].set_ylabel("How often the team won")
    fig.subplots_adjust(top=0.74, bottom=0.17, wspace=0.12)
    finish(fig, "Three things that go with winning an NHL game",
           f"Win rate for every NHL team in every regular-season game, 2023-24 through {pd.Timestamp(as_of):%b. %-d, %Y} ({n_kr:,} team-games). Dashed line = 50%.",
           "Five-on-five chances: whose shots were worth more in goals. Ties count as fewer.")
    fig.savefig(OUT / "sabres-tbl-nov22-keys.png"); plt.close(fig)

    # ---- rest: road teams on the second night of a back-to-back against a rested team, every game since 2023-24
    rr = []
    for side, opp in (("home", "away"), ("away", "home")):
        rr.append(gm.rename(columns={side: "team", opp: "opp_t", f"{side}_score": "gf", f"{opp}_score": "ga"})[["game_id", "season", "game_date", "team", "opp_t", "gf", "ga"]].assign(home=side == "home"))
    rr = pd.concat(rr)
    rr = rr[rr.season >= 20232024].copy()
    rr["d"] = pd.to_datetime(rr.game_date)
    rr = rr.sort_values(["team", "d"])
    rr["rest"] = (rr.d - rr.groupby(["team", "season"]).d.shift()).dt.days - 1
    rr["win"] = rr.gf > rr.ga
    rr = rr.merge(rr[["game_id", "team", "rest"]].rename(columns={"team": "opp_t", "rest": "opp_rest"}), on=["game_id", "opp_t"])
    road = rr[~rr.home]
    tired = road[(road.rest == 0) & (road.opp_rest >= 1)]
    fresh = road[(road.rest >= 1) & (road.opp_rest >= 1)]
    r_tired, n_tired, r_fresh, n_fresh = float(tired.win.mean()), len(tired), float(fresh.win.mean()), len(fresh)
    b2 = rr[(rr.team == US) & (rr.season == SEASON) & (rr.rest == 0)]
    b2_n, b2_w = len(b2), int(b2.win.sum())
    th = rr[(rr.team == THEM) & (rr.season == SEASON) & rr.home]
    th_w, th_n = int(th.win.sum()), len(th)
    m1_date = pd.Timestamp(m1.game_date)
    fig, ax = plt.subplots(figsize=(9.5, 4.2), dpi=200)
    cats = ["Road team, both teams rested", "Road team on the second night\nof a back-to-back, home team rested"]
    vals = [r_fresh, r_tired]; ns = [n_fresh, n_tired]
    ys = np.arange(2)
    ax.barh(ys, vals, 0.55, color=[GRAY, BLUE], zorder=2)
    for i in range(2):
        ax.text(vals[i] + 0.01, ys[i], f"{vals[i]:.0%}  ({ns[i]:,} games)", va="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_yticks(ys, cats); ax.tick_params(axis="y", length=0); ax.invert_yaxis(); ax.set_xlim(0, 0.7)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0)); ax.set_xlabel("How often the road team won")
    ax.axvline(0.5, color="#D5D8DE", lw=1, ls="--", zorder=1); ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "NHL road teams win less on the second night of a back-to-back",
           f"Every regular-season game, 2023-24 through {pd.Timestamp(as_of):%b. %-d, %Y}. Rested = at least one day off.",
           "x")
    fig.texts[-1].set_text("Source: NHL schedule and results.\nBuffalo plays its second game in two nights on Sunday; Tampa Bay has had two days off.")
    fig.savefig(OUT / "sabres-tbl-nov22-rest.png"); plt.close(fig)

    # ---- chart 3: model test
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(len(calb)); w = 0.36
    ax.bar(xs - w / 2, [c[1] for c in calb], w, color=GRAY, label="What the model said (likelier team's chance)", zorder=2)
    ax.bar(xs + w / 2, [c[2] for c in calb], w, color=BLUE, label="How often the likelier team actually won", zorder=2)
    for x_, c in zip(xs, calb):
        ax.text(x_ - w / 2, c[1] + 0.01, f"{c[1]:.0%}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.text(x_ + w / 2, c[2] + 0.01, f"{c[2]:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_xticks(xs, [f"Likelier team given {c[0]}\n({c[3]} games)" for c in calb], fontsize=9.5)
    ax.set_ylim(0, 0.9); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"When our model gave a team {calb[bin_i][0]}, like {FAV} Sunday, it won {calb[bin_i][2]:.0%}",
           f"Every 2025-26 game ({bt[LY]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-tbl-nov22-model-test.png"); plt.close(fig)

    if __import__("os").environ.get("DUMP"):
        print("REC", recd(US), recd(THEM), pts(US), pts(THEM), "GP", b.gp, v.gp, "off", us_off, them_off, "f6", f6)
        print(t.loc[[US, THEM], ["xgf_pg", "xga_pg", "share", "ev_share", "pp_x_pg", "pp_g_pg", "pk_x_pg", "pk_g_pg"]].round(3).to_string())
        for c in ["xgf_pg", "xga_pg", "share", "ev_share", "pp_x_pg", "pp_g_pg", "pk_x_pg", "pk_g_pg"]:
            print(c, "BUF", rk(c, US), "TBL", rk(c, THEM), "lg", round(lg[c], 3))
        print("model", round(p_b, 3), round(mu_b, 2), round(mu_v, 2), round(p_tie, 3), "fav", FAV, calb[bin_i])
        print("m1", m1_sc, {k_: round(v_, 2) for k_, v_ in m1_x.items()}, m1_pp, "ly", ly_w, len(ly))
        print("hagel", round(hag_x, 2), tb_g, "tom", tom_g, tom_rk, tied(THOMPSON), "keys", KEYS_CHECK, "rest", round(r_tired, 3), n_tired, round(r_fresh, 3), n_fresh, "b2", b2_w, b2_n, "th", th_w, th_n)
        print("K", {k_: (round(v_[0], 3), v_[1]) for k_, v_ in K.items()}, "BK", BK)
        print(pd.concat([bg, vg])[["opp", "name", "gp", "sv", "gsax", "rk"]].round(3).to_string())
        print("home", home_gap, "season test", bt[SEASON]["n"], round(bt[SEASON]["right"], 3))
        return

    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]} | \
           {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies_league.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Lightning'} | {link(r['name'])} | {int(r.gp)} | {r.sv:.1%} | {('0.0, about average,' if abs(r.gsax) < 0.05 else f'{r.gsax:+.1f}')} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    b_pkg = int(b.pk_g)
    assert KEYS_CHECK == (13, 5, 13, 12, 13, 6, 10, 3, 5), KEYS_CHECK
    assert (b2_w, b2_n, th_w, th_n) == (0, 2, 10, 11) and r_tired < r_fresh - 0.05
    b2_types = sorted(gm.set_index('game_id').loc[b2.game_id, 'last_period_type'].tolist())
    assert b2_types == ['OT', 'SO'], b2_types
    assert rk("ev_share", THEM) == 3 and rk("pk_x_pg", US) <= 5 and rk("pp_x_pg", THEM) == 15
    assert pts(THEM) == 32 and pts(US) == 22
    assert abs(m1_x[US] - m1_x[THEM]) < 0.1 and (ly_w, len(ly)) == (3, 4)
    md = f"""# Sabres at Lightning: a back-to-back, a 10-1 home team, and the same three keys

**Our model gives Buffalo a {p_b:.0%} chance to win in Tampa on Sunday (Lightning {1 - p_b:.0%}). That number doesn't count rest, and rest matters today: Buffalo played
in Florida last night, and Tampa Bay has had two days off. Since 2023-24, road teams in that spot have won {r_tired:.0%} of the time. Tampa Bay is {th_w}-{th_n - th_w} at home this season.
Here are the same three keys we graded after Florida.**

*Buffalo at Tampa Bay, Sunday, Nov. 22, 5 p.m. ET, the last game of a {trip_len}-game road trip. Sabres {recd(US)} ({pts(US)} points), Lightning {recd(THEM)} ({pts(THEM)} points), through {pd.to_datetime(last_date):%B %-d}.*

![Three things that go with winning](sabres-tbl-nov22-keys.png)

The chart covers every NHL game since 2023-24 ({n_kr:,} team results). These aren't magic: better teams tend to do all three. But they're what to watch on Sunday.
Saturday in Florida, Buffalo hit the first and third and lost 4-3 ([our recap](sabres-panthers-postgame-nov-21.html)).

## Key 1: Tampa Bay gets one power-play goal at most

**The key:** a penalty kill that gives up one goal or none.

NHL teams that allow no power-play goals win {K['pp0'][0]:.0%} of the time; two or more and it drops to {K['pp2'][0]:.0%}. Tampa Bay's power play is about average: {v.pp_x_pg:.2f} goals' worth of chances a game,
{ordn(rk('pp_x_pg', THEM))} of 32. The problem is Buffalo's penalty kill, which allows {b.pk_x_pg:.2f} a game, {ordn(rk('pk_x_pg', US))}-most in the NHL, and has given up {b_pkg} power-play goals in {int(b.gp)} games.
It held Florida's power play, the league's busiest, without a goal on Saturday.

## Key 2: Score first, and keep it

**The key:** the first goal, and no giving it back.

NHL teams that score first win {K['f1'][0]:.0%} of the time. Tampa Bay has scored first {f_first_n} times this season and won {f_first_w}. Buffalo has scored first {b_first_n} times and won {b_first_w}.

## Key 3: More of the chances at five-on-five

**The key:** shots worth more than Tampa Bay's when both teams are at full strength.

Teams that get more of the five-on-five chances win {K['e1'][0]:.0%} of the time. This is Tampa Bay's strength: it gets {v.ev_share:.1%} of the five-on-five chances, {ordn(rk('ev_share', THEM))} in the NHL.
Buffalo gets {b.ev_share:.1%} ({ordn(rk('ev_share', US))}). Buffalo has won {b_ev_w} of the {b_ev_n} games where it got more of them, and {b_noev_w} of the {b_noev_n} where it didn't. Small samples, but the gap is there.

**How we measure "chances."** Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays.
A shot from within 10 feet went in {close10:.1%} of the time over the last three seasons; one from 60 feet or more, {far60:.1%}. Add them up and you get what a team's chances were worth in goals.
More in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## The back-to-back

![Back-to-back win rates](sabres-tbl-nov22-rest.png)

Since 2023-24, road teams playing their second game in two nights against a rested team have won {r_tired:.0%} of the time ({n_tired:,} games). Road teams with both sides rested won {r_fresh:.0%}.
Buffalo has played the second night of a back-to-back { {1: 'once', 2: 'twice', 3: 'three times'}.get(b2_n, f'{b2_n} times') } this season and lost both, once in overtime and once in a shootout. Our model doesn't adjust for rest, so its {p_b:.0%} may be a little high.

## Last time

Tampa Bay won {m1_sc[THEM]}-{m1_sc[US]} in Buffalo on {m1_date:%b. %-d}. The chances that night were even: Buffalo's were worth {m1_x[US]:.1f} goals, Tampa Bay's {m1_x[THEM]:.1f}. Tampa Bay just finished far more of them.
Last season Buffalo won {ly_w} of the {len(ly)} games between them.

## Who to watch

- **Brandon Hagel and Jake Guentzel** have {tb_g} goals each for Tampa Bay. Hagel's chances add up to the most on the team, worth about {hag_x:.0f} goals.
- **Tage Thompson's {tom_g} goals are {'tied for ' if tied(THOMPSON) else ''}{ordn(tom_rk)} in the NHL.** He tied Saturday's game in the third.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good.

| Team | Goalie | Games | Save % | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies this season. Starters weren't confirmed when we published. Alex Lyon played Saturday.

## Our prediction: Sabres {p_b:.0%}, Lightning {1 - p_b:.0%}

{ledger_status}

Our model expects about **{mu_b:.1f} goals for Buffalo and {mu_v:.1f} for Tampa Bay**, and about a {p_tie:.0%} chance the game is tied after 60 minutes. It works from each team's chances this season,
blended with last season's, plus home ice (about {coef[2]:.1f} of a goal for Tampa Bay). If it's tied after 60 minutes, Tampa Bay gets {p_ot:.0%}: how often home teams won in overtime or a shootout in 2023-24 and 2024-25.

**One caution.** Our model has been a little high on home teams. In 2025-26 it gave them {home_gap[LY][0]:.1%} on average, and they won {home_gap[LY][1]:.1%} of
{home_gap[LY][2]:,} games. This season it's {home_gap[SEASON][0]:.1%}, and they've won {home_gap[SEASON][1]:.1%} of {home_gap[SEASON][2]:,}. The back-to-back works against Buffalo, though. We're logging the model's number as it is.

![How often the model's likelier team won, 2025-26](sabres-tbl-nov22-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only what was known before each game.
It called the winner {bt[LY]['right']:.0%} of the time; always going with the home team would have been right {bt[LY]['home_obs']:.0%}. This season ({bt[SEASON]['n']} games) it has called
{bt[SEASON]['right']:.0%} right. When it gave a team {calb[bin_i][0]} in 2025-26, as it gives {FAV} on Sunday, that team won {calb[bin_i][2]:.0%} of the time ({calb[bin_i][3]} games).

## After the game

Our recap will grade the three keys again: did Buffalo hit each one, and did it win?

## For the stat-heads

- Keys: all regular-season team-games, 2023-24 through {last_date}, n = {n_kr:,}. PP goals = goals at 5v4, 5v3, 4v3 by the opponent. First goal includes any goal; games scoreless after overtime count as no first goal for either team.
  5v5 "won" = team 5v5 xG > opponent 5v5 xG (unblocked, non-empty-net). PPGA 0 {K['pp0'][0]:.3f} (n {K['pp0'][1]:,}), 2+ {K['pp2'][0]:.3f} (n {K['pp2'][1]:,}); first goal {K['f1'][0]:.3f}; 5v5 won {K['e1'][0]:.3f}.
- Rest: days since the team's previous game in the same season, minus one. Road on 0 rest vs home 1+: {r_tired:.3f} (n {n_tired:,}); road and home both 1+: {r_fresh:.3f} (n {n_fresh:,}). Descriptive.
- xG: our model, rescaled per season (2026-27 factor {cal.loc[SEASON]:.3f}). Data through {last_date} ({len(g26)} games this season). Nov. 11: xGF BUF {m1_x[US]:.2f}, TBL {m1_x[THEM]:.2f}.
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`), ratings from games through {as_of}. Ratings: BUF off {off_r[US]:.2f}, def {def_r[US]:.2f}; TBL off {off_r[THEM]:.2f}, def {def_r[THEM]:.2f}.
  Goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home; independent Poisson; regulation ties to home at {p_ot:.3f}. Brier: 2025-26 {bt[LY]['brier']:.4f}; 2026-27 to date {bt[SEASON]['brier']:.4f}. No goalie, rest or back-to-back term.
"""
    (OUT / "2026-11-22-sabres-tbl-pregame.md").write_text(md)
    (OUT / "2026-11-22-sabres-tbl-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres at Tampa Bay, Sunday 5 p.m.",
        "big": [[f"{p_b:.0%}", f"Buffalo's chance to win, our model (Lightning {1 - p_b:.0%})"],
                [f"{r_tired:.0%}", "How often NHL road teams win on the second night of a back-to-back against a rested team"]],
        "note": "Three keys for Buffalo: hold Tampa Bay's power play to one goal or fewer, score first and keep it, and get more of the five-on-five chances.",
        "explainer": {"kicker": "The back-to-back", "title": "Road teams' win rate since 2023-24",
                      "text": "How often the road team won:", "fmt": "pct",
                      "bars": [["Both teams rested", round(r_fresh, 3)], ["Road team on a back-to-back", round(r_tired, 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
