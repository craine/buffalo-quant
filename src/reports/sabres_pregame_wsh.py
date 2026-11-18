"""Sabres pregame: Buffalo at Washington, Thu Nov 19, 2026, 7:00 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-19-sabres-wsh-pregame.md, three PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
Win chance from nhl_game_model v0.1 (the same model and inputs src/ledger/log_sabres_wsh.py logs). Pinned to games through AS_OF.
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
SEASON, LY, US, THEM = 20262027, 20252026, "BUF", "WSH"
AS_OF = "2026-11-17"            # games through Tuesday; Wednesday's three games involve neither team
RATINGS_BEFORE = "2026-11-18"   # ratings use games before this date (= through AS_OF)
GAME_DATE = "2026-11-19"
RED_W = "#C8102E"               # Capitals red
PP = ("5v4", "5v3", "4v3")
TUCH = 8477949
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

    # skid and trip
    bl = rec[rec.team == US].sort_values("game_date")
    skid = 0
    for w_ in bl.w.tolist()[::-1]:
        if w_: break
        skid += 1
    skid_ids = bl.game_id.tail(skid)
    skid_ot = int(gm[gm.game_id.isin(skid_ids)].last_period_type.isin(["OT", "SO"]).sum())
    xs_ = cur[cur.game_id.isin(skid_ids)]
    skx = dict(xgf=xs_[xs_.team == US].xg.sum(), xga=xs_[xs_.opp == US].xg.sum(), gf=int(xs_[xs_.team == US].goal.sum()), ga=int(xs_[xs_.opp == US].goal.sum()))
    skx["share"] = skx["xgf"] / (skx["xgf"] + skx["xga"])
    sch = query(f"SELECT game_date, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') ORDER BY game_date").reset_index(drop=True)
    i0 = int(sch.index[sch.game_date == GAME_DATE][0]); j = i0
    while j > 0 and sch.loc[j - 1, "away"] == US: j -= 1
    k = i0
    while k + 1 < len(sch) and sch.loc[k + 1, "away"] == US: k += 1
    trip_no, trip_len = i0 - j + 1, k - j + 1
    assert sch.loc[i0, "home"] == THEM and skid == 5 and (trip_no, trip_len) == (4, 6), (skid, trip_no, trip_len)
    wl = rec[rec.team == THEM].sort_values("game_date")
    them_rest = (pd.Timestamp(GAME_DATE) - pd.Timestamp(wl.game_date.iloc[-1])).days
    us_rest = (pd.Timestamp(GAME_DATE) - pd.Timestamp(bl.game_date.iloc[-1])).days

    # first meeting
    m1 = g26[((g26.home == US) & (g26.away == THEM)) | ((g26.home == THEM) & (g26.away == US))]
    assert len(m1) == 1
    m1 = m1.iloc[0]
    m1u = u[u.game_id == m1.game_id]
    m1_sc = {m1.home: int(m1.home_score), m1.away: int(m1.away_score)}
    m1_x = {US: m1u[m1u.team == US].xg.sum(), THEM: m1u[m1u.team == THEM].xg.sum()}
    m1_ot = m1.last_period_type in ("OT", "SO")
    assert (m1.game_date, m1.home, m1_sc[THEM], m1_sc[US]) == ("2026-10-24", THEM, 4, 3)
    tuch_m1 = int(((allg.game_id == m1.game_id) & (allg.shooter_id == TUCH)).sum())

    # Tuch
    tu = u[u.shooter_id == TUCH]
    tu_ty = tu[tu.season == SEASON]
    assert set(tu_ty.team) == {THEM}
    tuch = dict(g=int(tu_ty.goal.sum()), x=tu_ty.xg.sum(), g_all=int(((allg.shooter_id == TUCH) & (allg.season == SEASON)).sum()),
                gp=tu_ty.game_id.nunique(), ly_g=int(tu[tu.season == LY].goal.sum()), ly_x=tu[tu.season == LY].xg.sum())
    wt = cur[cur.team == THEM].groupby("shooter_id").agg(g=("goal", "sum"))
    tuch_rank = int(wt.g.rank(ascending=False, method="min").loc[TUCH])
    tu_d = tu.groupby('season').apply(lambda d: d.goal.sum() - d.xg.sum(), include_groups=False)
    assert tu_d[LY] > 0 and tu_d[LY - 10001] > 0 and tu_d[SEASON] > 0
    tuch_pp = int(pp[(pp.shooter_id == TUCH)].goal.sum())

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
    FAV = "Washington" if p_b < 0.5 else "Buffalo"
    bin_i = next(i for i, (lo, hi) in enumerate(cal_bins) if lo <= fav_p < hi)
    home_gap = {ss: (bt[ss]["p_home"], bt[ss]["home_obs"], bt[ss]["n"]) for ss in (LY, SEASON)}
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[(lp.model_version == gmod.VERSION) & lp.claim_text.str.contains("Capitals", na=False)] if len(lp) else lp
    ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min().replace('T', ' ').rstrip('Z')} UTC, before puck drop.** It gets graded after the game, hit or miss."
                     if len(lp) else "**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before puck drop; "
                     "every logged call is graded after the game, hit or miss.")

    # ---- chart 1: chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab in ((US, BLUE, "Sabres"), (THEM, RED_W, "Capitals")):
        r = t.loc[tm]
        ax.scatter(r.xgf_pg, r.xga_pg, s=140, color=col, zorder=3, edgecolor="white", lw=1.5)
        ax.annotate(lab, (r.xgf_pg, r.xga_pg), xytext=(8, 6), textcoords="offset points", fontsize=11, fontweight="bold", color=INK)
    ax.axvline(t.xgf_pg.mean(), color="#D5D8DE", lw=1, ls="--"); ax.axhline(t.xga_pg.mean(), color="#D5D8DE", lw=1, ls="--")
    ax.invert_yaxis()
    ax.text(t.xgf_pg.max(), t.xga_pg.min(), "Create a lot,\nallow little", ha="right", va="top", fontsize=9, color=MUTED)
    ax.text(t.xgf_pg.min(), t.xga_pg.max(), "Create little,\nallow a lot", ha="left", va="bottom", fontsize=9, color=MUTED)
    ax.set_xlabel("Chances created per game (goals they were worth)")
    ax.set_ylabel("Chances allowed per game (better defense is higher)")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Washington creates the {ordn(rk('xgf_pg', THEM))}-most chances; Buffalo allows the {ordn(rk('xga_pg', US))}-most",
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Capitals {int(v.gp)}.")
    fig.savefig(OUT / "sabres-wsh-chances.png"); plt.close(fig)

    # ---- chart 2: Buffalo's penalty kill vs Washington's power play
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    cats = ["Washington's power play:\nchances created a game", "Buffalo's penalty kill:\nchances allowed a game"]
    vals, lgv = [v.pp_x_pg, b.pk_x_pg], [lg.pp_x_pg, lg.pk_x_pg]
    ys = np.arange(2); h = 0.36
    ax.barh(ys + h / 2, lgv, h, color=GRAY, label="League average", zorder=2)
    ax.barh(ys - h / 2, vals, h, color=[RED_W, BLUE], zorder=2)
    rks = [rk("pp_x_pg", THEM), rk("pk_x_pg", US)]
    for i in range(2):
        ax.text(lgv[i] + 0.01, ys[i] + h / 2, f"{lgv[i]:.2f}", va="center", fontsize=9.5, color=MUTED)
        lab = f"{ordn(rks[i])}-most of 32" if rks[i] <= 16 else f"{ordn(33 - rks[i])}-fewest of 32"
        ax.text(vals[i] + 0.01, ys[i] - h / 2, f"{vals[i]:.2f}  ({lab})", va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_yticks(ys, cats); ax.invert_yaxis(); ax.set_xlim(0, max(vals + lgv) * 1.45)
    ax.set_xlabel("Chances per game on the power play (worth this many goals)")
    ax.legend(frameon=False, loc="lower right", fontsize=9); ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Buffalo's leaky penalty kill meets a quiet Washington power play",
           "Chances on the power play per game, 2026-27. Grey bars are the league average.",
           f"Through {pd.to_datetime(last_date):%b. %-d}, 2026: Sabres {int(b.gp)} games, Capitals {int(v.gp)}. Power play = 5-on-4, 5-on-3, 4-on-3. Depends on penalties drawn or taken.")
    fig.savefig(OUT / "sabres-wsh-special.png"); plt.close(fig)

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
    finish(fig, f"Teams given a {calb[bin_i][0]} chance to win, like {FAV} Thursday, won {calb[bin_i][2]:.0%}",
           f"Every 2025-26 game ({bt[LY]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-wsh-model-test.png"); plt.close(fig)

    if __import__("os").environ.get("DUMP"):
        print("REC", recd(US), recd(THEM), pts(US), pts(THEM), "GP", b.gp, v.gp, "rest", us_rest, them_rest)
        print(t.loc[[US, THEM], ["xgf_pg", "xga_pg", "share", "ev_share", "pp_x_pg", "pp_g_pg", "pk_x_pg", "pk_g_pg"]].round(3).to_string())
        for c in ["xgf_pg", "xga_pg", "share", "ev_share", "pp_x_pg", "pp_g_pg", "pk_x_pg", "pk_g_pg"]:
            print(c, "BUF", rk(c, US), "WSH", rk(c, THEM), "lg", round(lg[c], 3))
        print("model", round(p_b, 3), round(mu_b, 2), round(mu_v, 2), round(p_tie, 3), "fav", FAV, calb[bin_i])
        print("skid", skid, skid_ot, {k_: round(v_, 2) for k_, v_ in skx.items()}, "m1", m1_sc, {k_: round(v_, 2) for k_, v_ in m1_x.items()}, m1_ot, "tuch m1", tuch_m1)
        print("tuch", tuch, "rank on WSH", tuch_rank, "pp goals", tuch_pp)
        print(pd.concat([bg, vg])[["opp", "name", "gp", "sv", "gsax", "rk"]].round(3).to_string())
        print("home", home_gap, "season test", bt[SEASON]["n"], round(bt[SEASON]["right"], 3))
        return

    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]} | \
           {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies_league.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Capitals'} | {link(r['name'])} | {int(r.gp)} | {r.sv:.1%} | {('0.0, about average,' if abs(r.gsax) < 0.05 else f'{r.gsax:+.1f}')} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    assert tuch_pp == 0 and us_rest == them_rest == 2   # both played Tuesday: one day off
    assert rk("pp_x_pg", THEM) >= 24 and rk("pk_x_pg", US) <= 5 and tuch_rank == 1 and tuch_m1 == 2 and m1_ot
    pp_few = 33 - rk("pp_x_pg", THEM)
    b_pkg, w_ppg = int(b.pk_g), int(v.pp_g)
    w_pk_rank = 33 - rk("pk_x_pg", THEM)
    assert w_pk_rank >= 25 and 12 <= rk("pp_x_pg", US) <= 20    # "almost as much as Buffalo's", "league-average rate"
    assert v.xga_pg > lg.xga_pg and b.xga_pg > lg.xga_pg        # "both defenses give up more than average"
    sk_fin, sk_save = skx["gf"] - skx["xgf"], skx["xga"] - skx["ga"]
    assert sk_fin < -3 and sk_save < -3   # "both ends"
    md = f"""# Sabres at Capitals: Alex Tuch, a five-game skid, and a {p_b:.0%} chance

**Our model gives Buffalo a {p_b:.0%} chance to win in Washington Thursday night (Capitals {1 - p_b:.0%}). The Sabres have lost {skid} straight. Alex Tuch, who left Buffalo
in a June sign-and-trade, leads the Capitals with {tuch['g_all']} goals and scored twice when they beat the Sabres {m1_sc[THEM]}-{m1_sc[US]} in overtime on Oct. 24. The matchup
to watch is the one Charlie said to fix first in his [GM story](sabres-if-i-were-gm.html): Buffalo's penalty kill allows the {ordn(rk('pk_x_pg', US))}-most chances in the league, but Washington's power play creates the {ordn(pp_few)}-fewest.**

*Buffalo at Washington, Thursday, Nov. 19, 7 p.m. ET, game {trip_no} of a {trip_len}-game road trip. Both teams played Tuesday and have had a day off. Numbers are 2026-27 through {pd.to_datetime(last_date):%B %-d}:
Sabres {recd(US)} ({pts(US)} points) in {int(b.gp)} games, Capitals {recd(THEM)} ({pts(THEM)} points) in {int(v.gp)}. Early-season ranks can move a lot. These include every game played around the league Tuesday, so a few numbers differ slightly from the GM story.*

![Chances created vs allowed](sabres-wsh-chances.png)

## The two teams, side by side

| Per game, 2026-27 | Sabres | Capitals | League average |
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

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Over the last three seasons ({n_pri:,} shots that weren't
blocked, not counting empty nets), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}. Add up those chances on
every shot and you get what a team's chances were worth in goals. The shot locations come from the NHL's own play-by-play. The full explanation and how we
checked it are in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## Tuch against his old team

Tuch has {tuch['g_all']} goals in {tuch['gp']} games for Washington ({tuch['g']} with a goalie in net, on chances worth about {tuch['x']:.0f}, so he's beating his chances again), the most on the team. None has come on the power play.
In his last two seasons in Buffalo he scored about {tu_d[LY - 10001]:.0f} and {tu_d[LY]:.0f} more goals than his chances were worth, which is why
[If I were the Sabres' GM](sabres-if-i-were-gm.html) called him a lot of finishing to replace, and why a proven finisher is on Charlie's shopping list, after help a man down.
Tuch is the kind of finisher he means.

That Oct. 24 game, when he scored twice, wasn't close on chances: Washington's were worth {m1_x[THEM]:.1f} goals to Buffalo's {m1_x[US]:.1f}, and the Sabres still got a point by reaching overtime.
One game is a small sample, and our prediction goes by the full season, blended with last season.

## A man down

![Penalty kill vs power play](sabres-wsh-special.png)

Buffalo's penalty kill is the biggest single reason it gives up more chances than an average team (see the [GM story](sabres-if-i-were-gm.html)). It allows
{b.pk_x_pg:.2f} goals' worth of chances a game while shorthanded (league average {lg.pk_x_pg:.2f}), {ordn(rk('pk_x_pg', US))}-most of 32, and has allowed {b_pkg} power-play goals in {int(b.gp)} games.
Washington's power play is one of the quieter ones: {v.pp_x_pg:.2f} goals' worth of chances a game, {ordn(pp_few)}-fewest, and {w_ppg} goals in {int(v.gp)} games. Both numbers also depend on how many penalties
get called, which we can't yet split out. If Buffalo's penalty kill is going to look better anywhere on this trip, this is a good place for it.

It cuts the other way too: Washington's penalty kill allows almost as much as Buffalo's ({ordn(w_pk_rank)} of 32), and Buffalo's power play creates chances at a
league-average rate. It just hasn't finished them, as we wrote in the [GM story](sabres-if-i-were-gm.html).

## The skid

In the {skid} straight losses ({skid_ot} in overtime), Buffalo got {skx['share']:.0%} of the chances, close to even. It scored {skx['gf']} goals on chances worth about {skx['xgf']:.1f}, and
allowed {skx['ga']} on chances worth about {skx['xga']:.1f}. So the skid is both ends: the puck isn't going in, and the saves haven't been there. Neither tends to carry over from one part of a season to the next (see our
[playoff chances story](sabres-playoff-chances.html)), and the skid itself doesn't tell you much: in our [Flyers preview](sabres-flyers-pregame-nov-17.html) teams on a skid of four or more
won their next game about as often as our model expected from their chances.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good.

| Team | Goalie | Games | Save % | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. We hadn't seen confirmed starters when we published, and our prediction doesn't change with the
starter: a goalie's first half of a season is a weak guide to his second half (details in our [Vegas preview](sabres-vegas-pregame-nov-8.html)).

## Our prediction: Sabres {p_b:.0%}, Capitals {1 - p_b:.0%}

{ledger_status}

Our model expects about **{mu_b:.1f} goals for Buffalo and {mu_v:.1f} for Washington**, and gives about a {p_tie:.0%} chance the game is tied after 60 minutes. That's a lot of goals for both sides: both defenses give up more than average.

**Where the number comes from.** The chances numbers above. Early in a season we blend in last season's numbers and pull everything toward the league
average, which makes Buffalo's attack worth {off_r[US]:.1f} goals a game and Washington's chances allowed {def_r[THEM]:.1f}; the other way, Washington's attack comes out at
{off_r[THEM]:.1f} and Buffalo's chances allowed at {def_r[US]:.1f}. Home ice adds about {coef[2]:.1f} of a goal for the Capitals. Then we work out the chance of every possible
final score; ties after 60 minutes go the way they have for home teams in past overtimes and shootouts ({p_ot:.0%} home wins).

**One caution.** Our model has given home teams a little more than they've won: {home_gap[LY][0]:.1%} on average in 2025-26, when home teams won {home_gap[LY][1]:.1%}
({home_gap[LY][2]:,} games), and {home_gap[SEASON][0]:.1%} against {home_gap[SEASON][1]:.1%} this season. So Buffalo's real chance on the road may be a little better than {p_b:.0%}.
We're logging the model's number as it is.

![How often the model's likelier team won, 2025-26](sabres-wsh-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only what was known before each game.
It called the winner {bt[LY]['right']:.0%} of the time; always going with the home team would have been right {bt[LY]['home_obs']:.0%}. This season ({bt[SEASON]['n']} games) it has called
{bt[SEASON]['right']:.0%} right. When it gave a team {calb[bin_i][0]} in 2025-26, as it gives {FAV} Thursday, that team won {calb[bin_i][2]:.0%} of the time ({calb[bin_i][3]} games).

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so league xG = league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). Data through {last_date} ({len(g26)} games, every scheduled game through that date).
- Power play = 5v4, 5v3, 4v3 shots; per game over all games played, so it mixes how often a team is on the power play with what it does there. Penalty counts not used.
- Tuch 2026-27 (WSH): {tuch['g']} G on {tuch['x']:.2f} xG, non-empty-net; {tuch['g_all']} G including empty net. 2025-26 (BUF): {tuch['ly_g']} G on {tuch['ly_x']:.2f} xG.
- Skid ({skid} games): xGF {skx['xgf']:.2f}, GF {skx['gf']}; xGA {skx['xga']:.2f}, GA {skx['ga']} (non-empty-net). Oct. 24: xGF BUF {m1_x[US]:.2f}, WSH {m1_x[THEM]:.2f}.
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`), ratings from games through {as_of}. Team xGF/xGA per game shrunk with K={gmod.K}
  games toward league + {gmod.PRIOR_KEEP} x last season's edge; goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home (fit 2023-25), on unrescaled xG;
  independent Poisson; regulation ties to home at {p_ot:.3f}. Brier: 2025-26 {bt[LY]['brier']:.4f} (home-team rate {bt[LY]['b_home']:.4f}, coin 0.25); 2026-27 to date {bt[SEASON]['brier']:.4f}.
  No goalie, rest, streak or road-trip term. The shot model was trained on 2023-24 to 2025-26 shots, so 2025-26 checks are not fully clean; 2026-27 is.
"""
    (OUT / "2026-11-19-sabres-wsh-pregame.md").write_text(md)
    (OUT / "2026-11-19-sabres-wsh-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres at Washington, Thursday 7 p.m.",
        "big": [[f"{p_b:.0%}", f"Buffalo's chance to win, our model (Capitals {1 - p_b:.0%})"],
                [f"{ordn(rk('pk_x_pg', US))}-most", "Chances Buffalo's penalty kill allows, of 32 teams"]],
        "note": f"Alex Tuch leads Washington with {tuch['g_all']} goals and scored twice against Buffalo on Oct. 24. Buffalo's leaky penalty kill meets one of the league's quieter power plays.",
        "explainer": {"kicker": "A man down", "title": "Buffalo's penalty kill vs. the league",
                      "text": "Scoring chances allowed while a man down, counted in the goals they're worth, per game:", "fmt": "num",
                      "bars": [["League average", round(float(lg.pk_x_pg), 2)], ["Sabres", round(float(b.pk_x_pg), 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
