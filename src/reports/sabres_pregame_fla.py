"""Sabres pregame: Buffalo at Florida, Sat Nov 21, 2026, 6:00 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-21-sabres-fla-pregame.md, three PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
Win chance from nhl_game_model v0.1 (the same model and inputs src/ledger/log_sabres_fla.py logs). Pinned to games through AS_OF.
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
SEASON, LY, US, THEM = 20262027, 20252026, "BUF", "FLA"
AS_OF = "2026-11-19"            # games through Thursday; no NHL games Friday Nov 20
RATINGS_BEFORE = "2026-11-20"   # ratings use games before this date (= through AS_OF)
GAME_DATE = "2026-11-21"
RED_W = "#C8102E"               # Panthers red
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
    assert sch.loc[i0, "home"] == THEM and sch.loc[i0, "start_utc"] == "2026-11-21T23:00:00Z"
    nxt = sch.loc[i0 + 1]
    assert (nxt.game_date, nxt.home) == ("2026-11-22", "TBL")          # back-to-back: at Tampa Sunday
    j = i0
    while j > 0 and sch.loc[j - 1, "away"] == US: j -= 1
    k = i0
    while k + 1 < len(sch) and sch.loc[k + 1, "away"] == US: k += 1
    trip_no, trip_len = i0 - j + 1, k - j + 1
    us_last, them_last = bl.game_date.iloc[-1], fl.game_date.iloc[-1]
    us_off = (pd.Timestamp(GAME_DATE) - pd.Timestamp(us_last)).days - 1
    them_off = (pd.Timestamp(GAME_DATE) - pd.Timestamp(them_last)).days - 1
    assert (trip_no, trip_len, us_off, them_off) == (5, 6, 1, 3), (trip_no, trip_len, us_off, them_off)
    last = bl.iloc[-1]
    assert (int(last.gf), int(last.ga), bool(last.w)) == (6, 3, True)
    f_last = fl.tail(6)
    f6 = (int(f_last.w.sum()), int(f_last.l.sum()), int(f_last.otl.sum()))

    # first meeting, and last season
    m1 = g26[((g26.home == US) & (g26.away == THEM)) | ((g26.home == THEM) & (g26.away == US))]
    assert len(m1) == 1
    m1 = m1.iloc[0]
    m1u = u[u.game_id == m1.game_id]
    m1_sc = {m1.home: int(m1.home_score), m1.away: int(m1.away_score)}
    m1_x = {US: m1u[m1u.team == US].xg.sum(), THEM: m1u[m1u.team == THEM].xg.sum()}
    assert (m1.game_date, m1.home, m1_sc[US], m1_sc[THEM], m1.last_period_type) == ("2026-10-12", US, 5, 3, "REG")
    m1g = allg[allg.game_id == m1.game_id]
    m1_pp = {tm: int(((m1g.team == tm) & m1g.strength.isin(PP)).sum()) for tm in (US, THEM)}
    ly = gm[(gm.season == LY) & (((gm.home == US) & (gm.away == THEM)) | ((gm.home == THEM) & (gm.away == US)))]
    ly_w = int(sum((r.home_score > r.away_score) == (r.home == US) for r in ly.itertuples()))
    assert (ly_w, len(ly)) == (3, 4)

    thu = allg[(allg.game_id == 2026020351) & (allg.team == US)]
    thu_ppg = int(thu.strength.isin(PP).sum())
    W2 = {1: 'once', 2: 'twice', 3: 'three times'}
    assert thu_ppg == 2
    sk = 0
    for w_ in bl.w.tolist()[-2::-1]:
        if w_: break
        sk += 1
    assert sk == 5   # the skid Thursday's win ended
    # scorers
    THOMPSON = 8479420
    gl_ty = allg[allg.season == SEASON].groupby("shooter_id").size()
    g_rank = gl_ty.rank(ascending=False, method="min")
    tied = lambda pid: int((gl_ty == gl_ty[pid]).sum()) > 1
    tom_g, tom_rk = int(gl_ty[THOMPSON]), int(g_rank[THOMPSON])
    fsc = allg[(allg.season == SEASON) & (allg.team == THEM)].groupby("shooter_id").size().sort_values(ascending=False)
    REINHART, BTKACHUK = fsc.index[0], fsc.index[1]
    assert names[REINHART] == "Sam Reinhart" and names[BTKACHUK] == "Brady Tkachuk" and int(fsc.iloc[0]) == 12 and int(fsc.iloc[1]) == 11
    fx = cur[cur.team == THEM].groupby("shooter_id").agg(g=("goal", "sum"), x=("xg", "sum"))
    assert fx.x.idxmax() == REINHART
    rein_x, rein_g = float(fx.loc[REINHART].x), int(fx.loc[REINHART].g)
    bt_team = query("SELECT r.season, MIN(r.team_id) AS team_id, COUNT(*) AS n FROM raw_nhl_rosters r WHERE r.first = 'Brady' AND r.last = 'Tkachuk' GROUP BY r.season ORDER BY r.season")
    fla_id = int(gm[gm.home == THEM].home_id.iloc[0]); ott_id = int(gm[gm.home == "OTT"].home_id.iloc[0])
    assert list(bt_team.team_id) == [ott_id, ott_id, ott_id, fla_id]   # Ottawa 2023-24 to 2025-26, Florida now

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
    FAV = "Florida" if p_b < 0.5 else "Buffalo"
    bin_i = next(i for i, (lo, hi) in enumerate(cal_bins) if lo <= fav_p < hi)
    home_gap = {ss: (bt[ss]["p_home"], bt[ss]["home_obs"], bt[ss]["n"]) for ss in (LY, SEASON)}
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[(lp.model_version == gmod.VERSION) & lp.claim_text.str.contains("Panthers", na=False)] if len(lp) else lp
    ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min().replace('T', ' ').rstrip('Z')} UTC, before puck drop.** It gets graded after the game, hit or miss."
                     if len(lp) else "**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before puck drop; "
                     "every logged call is graded after the game, hit or miss.")

    # ---- chart 1: chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab, off, ha in ((US, BLUE, "Sabres", (8, 6), "left"), (THEM, RED_W, "Panthers", (10, -18), "left")):
        r = t.loc[tm]
        ax.scatter(r.xgf_pg, r.xga_pg, s=140, color=col, zorder=3, edgecolor="white", lw=1.5)
        ax.annotate(lab, (r.xgf_pg, r.xga_pg), xytext=off, textcoords="offset points", fontsize=11, fontweight="bold", color=INK, ha=ha)
    ax.axvline(t.xgf_pg.mean(), color="#D5D8DE", lw=1, ls="--"); ax.axhline(t.xga_pg.mean(), color="#D5D8DE", lw=1, ls="--")
    ax.invert_yaxis()
    ax.margins(x=0.12, y=0.12)
    ax.text(0.99, 0.99, "Create a lot,\nallow little", transform=ax.transAxes, ha="right", va="top", fontsize=9, color=MUTED)
    ax.text(0.01, 0.01, "Create little,\nallow a lot", transform=ax.transAxes, ha="left", va="bottom", fontsize=9, color=MUTED)
    ax.set_xlabel("Chances created per game (goals they were worth)")
    ax.set_ylabel("Chances allowed per game (better defense is higher)")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Florida allows the {ordn(33 - rk('xga_pg', THEM))}-fewest chances; Buffalo allows the {ordn(rk('xga_pg', US))}-most",
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Panthers {int(v.gp)}.")
    fig.savefig(OUT / "sabres-fla-chances.png"); plt.close(fig)

    # ---- chart 2: Florida's power play vs Buffalo's penalty kill
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    cats = ["Florida's power play:\nchances created a game", "Buffalo's penalty kill:\nchances allowed a game"]
    vals, lgv = [v.pp_x_pg, b.pk_x_pg], [lg.pp_x_pg, lg.pk_x_pg]
    ys = np.arange(2); h = 0.36
    ax.barh(ys + h / 2, lgv, h, color=GRAY, label="League average", zorder=2)
    ax.barh(ys - h / 2, vals, h, color=[RED_W, BLUE], zorder=2)
    rks = [rk("pp_x_pg", THEM), rk("pk_x_pg", US)]
    for i in range(2):
        ax.text(lgv[i] + 0.01, ys[i] + h / 2, f"{lgv[i]:.2f}", va="center", fontsize=9.5, color=MUTED)
        lab = "most of 32" if rks[i] == 1 else f"{ordn(rks[i])}-most of 32"
        ax.text(vals[i] + 0.01, ys[i] - h / 2, f"{vals[i]:.2f}  ({lab})", va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_yticks(ys, cats); ax.tick_params(axis='y', length=0); ax.invert_yaxis(); ax.set_xlim(0, max(vals + lgv) * 1.45)
    ax.set_xlabel("Chances per game on the power play (worth this many goals)")
    ax.legend(frameon=False, loc="lower right", fontsize=9); ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "The NHL's busiest power play meets Buffalo's leaky penalty kill",
           "Chances on the power play per game, 2026-27. Grey bars are the league average.",
           f"Through {pd.to_datetime(last_date):%b. %-d}, 2026: Sabres {int(b.gp)} games, Panthers {int(v.gp)}. Power play = 5-on-4, 5-on-3, 4-on-3. Depends on penalties drawn or taken.")
    fig.savefig(OUT / "sabres-fla-special.png"); plt.close(fig)

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
    finish(fig, f"When our model gave a team {calb[bin_i][0]}, like {FAV} Saturday, it won {calb[bin_i][2]:.0%}",
           f"Every 2025-26 game ({bt[LY]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-fla-model-test.png"); plt.close(fig)

    if __import__("os").environ.get("DUMP"):
        print("REC", recd(US), recd(THEM), pts(US), pts(THEM), "GP", b.gp, v.gp, "off", us_off, them_off, "f6", f6)
        print(t.loc[[US, THEM], ["xgf_pg", "xga_pg", "share", "ev_share", "pp_x_pg", "pp_g_pg", "pk_x_pg", "pk_g_pg"]].round(3).to_string())
        for c in ["xgf_pg", "xga_pg", "share", "ev_share", "pp_x_pg", "pp_g_pg", "pk_x_pg", "pk_g_pg"]:
            print(c, "BUF", rk(c, US), "FLA", rk(c, THEM), "lg", round(lg[c], 3))
        print("model", round(p_b, 3), round(mu_b, 2), round(mu_v, 2), round(p_tie, 3), "fav", FAV, calb[bin_i])
        print("m1", m1_sc, {k_: round(v_, 2) for k_, v_ in m1_x.items()}, m1_pp, "ly", ly_w, len(ly))
        print("rein", rein_g, round(rein_x, 2), "goals", int(fsc.iloc[0]), int(fsc.iloc[1]), "tom", tom_g, tom_rk)
        print(pd.concat([bg, vg])[["opp", "name", "gp", "sv", "gsax", "rk"]].round(3).to_string())
        print("home", home_gap, "season test", bt[SEASON]["n"], round(bt[SEASON]["right"], 3))
        return

    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]} | \
           {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies_league.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Panthers'} | {link(r['name'])} | {int(r.gp)} | {r.sv:.1%} | {('0.0, about average,' if abs(r.gsax) < 0.05 else f'{r.gsax:+.1f}')} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    assert rk("pp_x_pg", THEM) == 1 and rk("pk_x_pg", US) <= 5 and rk("pk_x_pg", THEM) <= 5
    assert 33 - rk("xga_pg", THEM) <= 12 and rk("xga_pg", US) <= 8
    b_pkg, f_ppg = int(b.pk_g), int(v.pp_g)
    assert pts(THEM) == 27 and pts(US) == 22 and f6 == (3, 2, 1)
    md = f"""# Sabres at Panthers: the NHL's busiest power play meets Buffalo's leaky penalty kill

**Our model gives Buffalo a {p_b:.0%} chance to win in Florida on Saturday (Panthers {1 - p_b:.0%}). The Sabres just ended a five-game skid with a 6-3 win in Washington.
The matchup to watch: Florida's power play creates more chances than any team's in the NHL, and Buffalo's penalty kill allows the {ordn(rk('pk_x_pg', US))}-most.
That's the problem the [GM story](sabres-if-i-were-gm.html) said to fix first.**

*Buffalo at Florida, Saturday, Nov. 21, 6 p.m. ET, game {trip_no} of a {trip_len}-game road trip. Buffalo played Thursday and plays again Sunday in Tampa; Florida last played Tuesday.
Numbers are 2026-27 through {pd.to_datetime(last_date):%B %-d}: Sabres {recd(US)} ({pts(US)} points) in {int(b.gp)} games, Panthers {recd(THEM)} ({pts(THEM)} points) in {int(v.gp)}.
Early-season ranks can move a lot.*

![Chances created vs allowed](sabres-fla-chances.png)

## The two teams, side by side

| Per game, 2026-27 | Sabres | Panthers | League average |
|---|---|---|---|
| Chances created (worth this many goals) | {b.xgf_pg:.2f} ({ordn(rk('xgf_pg', US))}) | {v.xgf_pg:.2f} ({ordn(rk('xgf_pg', THEM))}) | {lg.xgf_pg:.2f} |
| Chances allowed | {b.xga_pg:.2f} ({ordn(33 - rk('xga_pg', US))}) | {v.xga_pg:.2f} ({ordn(33 - rk('xga_pg', THEM))}) | {lg.xga_pg:.2f} |
| Share of the chances at five-on-five | {b.ev_share:.1%} ({ordn(rk('ev_share', US))}) | {v.ev_share:.1%} ({ordn(rk('ev_share', THEM))}) | 50% |
| Goals scored, actual | {gfa.loc[US].GF / b.gp:.2f} | {gfa.loc[THEM].GF / v.gp:.2f} | |
| Goals allowed, actual | {gfa.loc[US].GA / b.gp:.2f} | {gfa.loc[THEM].GA / v.gp:.2f} | |
| Power-play chances created | {b.pp_x_pg:.2f} ({ordn(rk('pp_x_pg', US))}) | {v.pp_x_pg:.2f} ({ordn(rk('pp_x_pg', THEM))}) | {lg.pp_x_pg:.2f} |
| Chances allowed a man down | {b.pk_x_pg:.2f} ({ordn(33 - rk('pk_x_pg', US))}) | {v.pk_x_pg:.2f} ({ordn(33 - rk('pk_x_pg', THEM))}) | {lg.pk_x_pg:.2f} |

Ranks are among 32 teams; 1st is best (most created, fewest allowed). Actual goals come from final scores; chances leave out empty-net shots.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays. Over the last three seasons
({n_pri:,} shots that weren't blocked, not counting empty nets), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}.
Add up those chances on every shot and you get what a team's chances were worth in goals. The shot locations come from the NHL's own play-by-play. The full explanation
and how we checked it are in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## A man down

![Power play vs penalty kill](sabres-fla-special.png)

Florida's power play creates {v.pp_x_pg:.2f} goals' worth of chances a game, the most in the NHL (league average {lg.pp_x_pg:.2f}), and has scored {f_ppg} power-play goals in {int(v.gp)} games.
Buffalo's penalty kill allows {b.pk_x_pg:.2f} a game, {ordn(rk('pk_x_pg', US))}-most of 32, and has allowed {b_pkg} power-play goals in {int(b.gp)} games. Both numbers also depend on how many
penalties get called. Staying out of the penalty box matters on Saturday.

Buffalo's own power play scored {W2[thu_ppg]} in Washington on Thursday.

## The first meeting

Buffalo beat Florida {m1_sc[US]}-{m1_sc[THEM]} at home on Oct. 12. The chances were even: Buffalo's were worth {m1_x[US]:.1f} goals, Florida's {m1_x[THEM]:.1f}. Each team scored {m1_pp[US]} power-play goals.
Last season Buffalo won {ly_w} of the {len(ly)} games between them. One game is a small sample, and our prediction goes by the full season, blended with last season.

## Notes for Saturday

- **Florida's top two.** Sam Reinhart leads the Panthers with {int(fsc.iloc[0])} goals, and his chances add up to the most on the team, worth about {rein_x:.0f} goals.
  Brady Tkachuk, who played for Ottawa through last season, has {int(fsc.iloc[1])}.
- **Tage Thompson's {tom_g} goals are {'tied for ' if tied(THOMPSON) else ''}{ordn(tom_rk)} in the NHL.**
- **Rest.** Florida has had three days off. Buffalo has had one, and plays again Sunday in Tampa. Our model doesn't count rest.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good.

| Team | Goalie | Games | Save % | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. We hadn't seen confirmed starters when we published, and our prediction doesn't change with the
starter: a goalie's first half of a season is a weak guide to his second half (details in our [Vegas preview](sabres-vegas-pregame-nov-8.html)).

## Our prediction: Sabres {p_b:.0%}, Panthers {1 - p_b:.0%}

{ledger_status}

Our model expects about **{mu_b:.1f} goals for Buffalo and {mu_v:.1f} for Florida**, and gives about a {p_tie:.0%} chance the game is tied after 60 minutes.

**Where the number comes from.** The chances numbers above. Early in a season we blend in last season's numbers and pull everything toward the league
average, which makes Buffalo's attack worth {off_r[US]:.1f} goals a game and Florida's chances allowed {def_r[THEM]:.1f}. Florida's attack comes out at
{off_r[THEM]:.1f}, and Buffalo's chances allowed at {def_r[US]:.1f}. Home ice adds about {coef[2]:.1f} of a goal for the Panthers. Then we work out the chance of every possible
final score. If it's tied after 60 minutes, Florida gets {p_ot:.0%}: how often home teams won in overtime or a shootout in 2023-24 and 2024-25.

**One caution.** Our model has been a little high on home teams. In 2025-26 it gave them {home_gap[LY][0]:.1%} on average, and they won {home_gap[LY][1]:.1%} of
{home_gap[LY][2]:,} games. This season it's {home_gap[SEASON][0]:.1%}, and they've won {home_gap[SEASON][1]:.1%} of {home_gap[SEASON][2]:,}. So Buffalo's real chance on the road may be a little better than {p_b:.0%}.
We're logging the model's number as it is.

![How often the model's likelier team won, 2025-26](sabres-fla-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only what was known before each game.
It called the winner {bt[LY]['right']:.0%} of the time; always going with the home team would have been right {bt[LY]['home_obs']:.0%}. This season ({bt[SEASON]['n']} games) it has called
{bt[SEASON]['right']:.0%} right. When it gave a team {calb[bin_i][0]} in 2025-26, as it gives {FAV} on Saturday, that team won {calb[bin_i][2]:.0%} of the time ({calb[bin_i][3]} games).

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so league xG = league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). Data through {last_date} ({len(g26)} games, every scheduled game through that date).
- Power play = 5v4, 5v3, 4v3 shots; per game over all games played, so it mixes how often a team is on the power play with what it does there. Penalty counts not used.
- Oct. 12: xGF BUF {m1_x[US]:.2f}, FLA {m1_x[THEM]:.2f}. Reinhart 2026-27: {rein_g} G on {rein_x:.2f} xG, non-empty-net.
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`), ratings from games through {as_of}. Team xGF/xGA per game shrunk with K={gmod.K}
  games toward league + {gmod.PRIOR_KEEP} x last season's edge; goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home (fit 2023-25), on unrescaled xG;
  independent Poisson; regulation ties to home at {p_ot:.3f}. Brier: 2025-26 {bt[LY]['brier']:.4f} (home-team rate {bt[LY]['b_home']:.4f}, coin 0.25); 2026-27 to date {bt[SEASON]['brier']:.4f}.
  No goalie, rest, back-to-back or road-trip term. The shot model was trained on 2023-24 to 2025-26 shots, so 2025-26 checks are not fully clean; 2026-27 is.
"""
    (OUT / "2026-11-21-sabres-fla-pregame.md").write_text(md)
    (OUT / "2026-11-21-sabres-fla-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres at Florida, Saturday 6 p.m.",
        "big": [[f"{p_b:.0%}", f"Buffalo's chance to win, our model (Panthers {1 - p_b:.0%})"],
                ["1st", "Florida's power play in chances created, of 32 NHL teams"]],
        "note": f"Florida's power play creates more chances than any in the NHL. Buffalo's penalty kill allows the {ordn(rk('pk_x_pg', US))}-most.",
        "explainer": {"kicker": "A man down", "title": "Florida's power play vs. the league",
                      "text": "Scoring chances created on the power play, counted in the goals they're worth, per game:", "fmt": "num",
                      "bars": [["League average", round(float(lg.pp_x_pg), 2)], ["Panthers", round(float(v.pp_x_pg), 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
