"""Sabres pregame: Buffalo at Chicago, Thu Nov 12, 2026, 8:00 PM ET (second night of a back-to-back). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-12-sabres-chi-pregame.md, three PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
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
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
SEASON, US, THEM = 20262027, "BUF", "CHI"
AS_OF = "2026-11-11"  # games through Wednesday night; pinned so the published story doesn't change
GOLD = "#8A1C2B"  # Blackhawks red, distinct from Bills red
GAME_DATE = "2026-11-12"
B2B_FROM = "2025-10-01"   # model test on back-to-backs: seasons the model never saw
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
    off_r, def_r, lg_r, ratio = gmod.ratings(tg, SEASON, GAME_DATE)
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
    lp = lp[lp.claim_text.str.contains("Blackhawks", na=False)] if len(lp) else lp
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

    # ---- the back-to-back: rest days for every game, 2023-24 through games before tonight
    ga = query(f"SELECT game_id, season, game_date, home, away, home_score, away_score FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    ga["game_date"] = pd.to_datetime(ga.game_date)
    lg_ = pd.concat([ga.assign(team=ga.home)[["game_id", "season", "game_date", "team"]],
                     ga.assign(team=ga.away)[["game_id", "season", "game_date", "team"]]]).sort_values(["team", "game_date"])
    lg_["rest"] = lg_.groupby(["team", "season"]).game_date.diff().dt.days
    rest = lg_.set_index(["game_id", "team"]).rest
    ga["r_h"] = [rest.get((a, h)) for a, h in zip(ga.game_id, ga.home)]
    ga["r_a"] = [rest.get((a, w)) for a, w in zip(ga.game_id, ga.away)]
    xf = u.groupby(["game_id", "team"]).xg.sum()
    ga["xg_a"] = [xf.get((i, w), 0.0) for i, w in zip(ga.game_id, ga.away)]
    ga["xg_h"] = [xf.get((i, h), 0.0) for i, h in zip(ga.game_id, ga.home)]
    ga["road_won"] = (ga.away_score > ga.home_score).astype(int)
    tired = (ga.r_a == 1) & (ga.r_h >= 2)       # road team played yesterday; home team had at least a day off
    rested = (ga.r_a >= 2) & (ga.r_h >= 2)
    by = pd.DataFrame({lab: ga[m].groupby("season").road_won.mean() for lab, m in (("tired", tired), ("rested", rested))})
    by["n_tired"] = ga[tired].groupby("season").size()
    n_t, n_r = int(tired.sum()), int(rested.sum())
    w_t, w_r = ga[tired].road_won.mean(), ga[rested].road_won.mean()
    sh_t = ga[tired].xg_a.sum() / (ga[tired].xg_a.sum() + ga[tired].xg_h.sum())
    sh_r = ga[rested].xg_a.sum() / (ga[rested].xg_a.sum() + ga[rested].xg_h.sum())
    # what the model said in those games, only seasons it never saw (2025-26 and this season before tonight)
    mr = []
    for ss, mxd in ((20252026, None), (SEASON, as_of)):
        mr.append(gmod.game_rows(gmod.build_frame(tg, [ss], max_date=mxd), coef, p_ot))
    mr = pd.concat(mr).merge(ga[["game_id", "r_h", "r_a"]].astype({"game_id": "int64"}), on="game_id")
    mt_ = mr[(mr.r_a == 1) & (mr.r_h >= 2)]
    mr_ = mr[(mr.r_a >= 2) & (mr.r_h >= 2)]
    m_said_t, m_won_t, m_n_t = (1 - mt_.p_home).mean(), (1 - mt_.home_won).mean(), len(mt_)
    m_said_r, m_won_r, m_n_r = (1 - mr_.p_home).mean(), (1 - mr_.home_won).mean(), len(mr_)
    m_se = (m_won_t * (1 - m_won_t) / m_n_t) ** 0.5
    # goaltending on the second night (complete seasons): who starts, and goals saved vs average
    gsh = u[u.goalie_id.notna()].groupby(["game_id", "opp", "goalie_id"]).agg(sh=("xg", "size"), xga=("xg", "sum"), ga_=("goal", "sum")).reset_index()
    start = gsh.sort_values("sh", ascending=False).drop_duplicates(["game_id", "opp"])
    start = start.merge(ga[["game_id", "season"]], on="game_id")
    no1 = start.groupby(["season", "opp", "goalie_id"]).size().rename("n").reset_index().sort_values("n", ascending=False) \
        .drop_duplicates(["season", "opp"]).set_index(["season", "opp"]).goalie_id
    def goalie_part(m):
        y = ga[m & (ga.season < SEASON)][["game_id", "away"]]
        st_ = y.merge(start, left_on=["game_id", "away"], right_on=["game_id", "opp"])
        tt = y.merge(gsh.groupby(["game_id", "opp"])[["xga", "ga_"]].sum().reset_index(), left_on=["game_id", "away"], right_on=["game_id", "opp"])
        return (pd.Series([no1.get((a, b_)) == c for a, b_, c in zip(st_.season, st_.away, st_.goalie_id)]).mean(), (tt.xga - tt.ga_).mean())
    no1_t, gsv_t = goalie_part(tired)
    no1_r, gsv_r = goalie_part(rested)
    chi_last = ga[(ga.home == THEM) | (ga.away == THEM)].game_date.max()
    chi_rest = (pd.Timestamp(GAME_DATE) - chi_last).days
    buf_prev = ga[((ga.away == US) & (ga.r_a == 1)) & (ga.season == SEASON)]

    most = lambda rank: "most" if rank == 1 else f"{ordn(rank)}-most"
    fewest = lambda rank: "fewest" if rank == 1 else f"{ordn(rank)}-fewest"

    # ---- chart 3: how the model's chances held up on 2025-26
    fav_p = max(p_b, 1 - p_b)
    bin_i = next(k for k, (lo, hi) in enumerate(cal_bins) if lo <= fav_p < hi)
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    xs = np.arange(len(calb)); w = 0.36
    ax.bar(xs - w / 2, [c[1] for c in calb], w, color=GRAY, label="What the model said (favorite's chance)", zorder=2)
    ax.bar(xs + w / 2, [c[2] for c in calb], w, color=BLUE, label="How often the favorite actually won", zorder=2)
    for x_, c in zip(xs, calb):
        ax.text(x_ - w / 2, c[1] + 0.01, f"{c[1]:.0%}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.text(x_ + w / 2, c[2] + 0.01, f"{c[2]:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_xticks(xs, [f"Favorite given {c[0]}\n({c[3]} games)" for c in calb], fontsize=9.5)
    ax.set_ylim(0, 0.9); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Teams given {calb[bin_i][0]}, like Buffalo tonight, won {calb[bin_i][2]:.0%} in 2025-26",
           f"Every 2025-26 game ({bt[20252026]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-chi-model-test.png"); plt.close(fig)

    # ---- chart 1: every team's chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab in ((US, BLUE, "Sabres"), (THEM, GOLD, "Blackhawks")):
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
    finish(fig, f"Chicago creates the {fewest(33 - rk('xgf_pg', THEM))} chances and allows the {most(33 - rk('xga_pg', THEM, False))}",
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Blackhawks {int(v.gp)}.")
    fig.savefig(OUT / "sabres-chi-chances.png"); plt.close(fig)

    # ---- chart 2: the back-to-back, by season
    fig, ax = plt.subplots(figsize=(9.5, 4.9), dpi=200)
    seas = list(by.index); xs = np.arange(len(seas)); w = 0.36
    lab_s = [f"{str(x_)[:4]}-{str(x_)[6:]}" + (" so far" if x_ == SEASON else "") for x_ in seas]
    ax.bar(xs - w / 2, by.rested, w, color="#C9CDD4", label="Road team rested (2+ days off), host rested", zorder=2)
    ax.bar(xs + w / 2, by.tired, w, color=BLUE, label="Road team played the night before, host rested", zorder=2)
    for x_, r in zip(xs, by.itertuples()):
        ax.text(x_ - w / 2, r.rested + 0.01, f"{r.rested:.0%}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.text(x_ + w / 2, r.tired + 0.01, f"{r.tired:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
    ax.set_xticks(xs, [f"{l}\n({int(n)} tired-road games)" for l, n in zip(lab_s, by.n_tired)], fontsize=9.5)
    ax.set_ylim(0, 0.65); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylabel("How often the road team won")
    ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=2); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Tired road teams won {w_t:.0%} of the time; rested ones won {w_r:.0%}",
           "Road teams playing for the second night in a row, against a home team that had at least a day off. Lower in every season.",
           f"Regular-season NHL games, 2023-24 through {pd.to_datetime(last_date):%b. %-d}, 2026: {n_t} tired-road games, {n_r} with both teams rested. Any win counts (regulation, OT, shootout).")
    fig.savefig(OUT / "sabres-chi-b2b.png"); plt.close(fig)

    if __import__("os").environ.get("DUMP"):
        print("REC", recd(US), recd(THEM), "GP", b.gp, v.gp, "last", last_date, "chi rest", chi_rest)
        print(t.loc[[US, THEM], ["xgf_pg","xga_pg","share","close_f_pg","close_a_pg","reb_f_pg","reb_a_pg"]].round(3).to_string())
        for c,h in [("xgf_pg",1),("xga_pg",0),("share",1),("close_f_pg",1),("close_a_pg",0),("reb_f_pg",1),("reb_a_pg",0)]:
            print(c, "BUF", rk(c,US,bool(h)), "CHI", rk(c,THEM,bool(h)))
        print("model p_b", round(p_b,3), "mu", round(mu_b,2), round(mu_v,2), "tie", round(p_tie,3), "bin", calb[bin_i])
        print("b2b", n_t, round(w_t,3), n_r, round(w_r,3), "share", round(sh_t,3), round(sh_r,3))
        print("model on tired", m_n_t, round(m_said_t,3), round(m_won_t,3), "se", round(m_se,3), "rested", m_n_r, round(m_said_r,3), round(m_won_r,3))
        print("goalies no1", round(no1_t,3), round(no1_r,3), "gsv", round(gsv_t,3), round(gsv_r,3)); print(by.round(3))
        print("goalies"); print(pd.concat([bg,vg])[["opp","name","gp","sv","gsax","rk"]].round(3).to_string())
        print(buf_prev[["game_date","away","home","away_score","home_score"]])
        return
    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Blackhawks'} | {link(r['name'])} | {int(r.gp)} | {r.sv:.1%} | {('0.0, about average,' if abs(r.gsax) < 0.05 else f'{r.gsax:+.1f}')} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    chi_f, chi_a = 33 - rk("xgf_pg", THEM), 33 - rk("xga_pg", THEM, False)     # Chicago: rank from the bottom
    buf_a = 33 - rk("xga_pg", US, False)
    gap = m_said_t - m_won_t
    bp = buf_prev.iloc[0] if len(buf_prev) else None
    prev_line = (f" Buffalo's only other second night this season was {pd.to_datetime(bp.game_date):%b. %-d} at {'Montreal' if bp.home == 'MTL' else bp.home}, "
                 f"a {int(bp.home_score)}-{int(bp.away_score)} loss." if bp is not None and bp.home_score > bp.away_score else "")
    md = f"""# Sabres at Blackhawks: the NHL's weakest team by chances, but Buffalo is on tired legs

**Our model leans Buffalo in Chicago: Sabres {p_b:.0%}, Blackhawks {1 - p_b:.0%}. Chicago creates the {fewest(chi_f)} chances in the
league and allows the {most(chi_a)}. But the model doesn't know the Sabres played last night, and that matters: last season and this one, road teams playing a second straight night against a rested home team won {m_won_t:.0%} of the time when our model gave them {m_said_t:.0%}.**

*Buffalo at Chicago, Thursday, Nov. 12, 8 p.m. ET, United Center. The Sabres lost 8-3 to Tampa Bay at home last night; the Blackhawks
haven't played since Nov. 7. Numbers are 2026-27 through {pd.to_datetime(last_date):%B %-d}: Sabres {recd(US)} in {int(b.gp)} games, Blackhawks
{recd(THEM)} in {int(v.gp)}. Eighteen games is early; ranks can move a lot.*

![Chances created vs allowed](sabres-chi-chances.png)

## The two teams, side by side

| Per game, 2026-27 | Sabres | Blackhawks | League average |
|---|---|---|---|
| Chances created (goals they were worth) | {b.xgf_pg:.2f} ({ordn(rk('xgf_pg', US))}) | {v.xgf_pg:.2f} ({ordn(rk('xgf_pg', THEM))}) | {lg.xgf_pg:.2f} |
| Chances allowed | {b.xga_pg:.2f} ({ordn(rk('xga_pg', US, False))}) | {v.xga_pg:.2f} ({ordn(rk('xga_pg', THEM, False))}) | {lg.xgf_pg:.2f} |
| Share of the chances in their games | {b.share:.1%} ({ordn(rk('share', US))}) | {v.share:.1%} ({ordn(rk('share', THEM))}) | 50% |
| Goals scored, actual | {gfa.loc[US].GF / b.gp:.2f} | {gfa.loc[THEM].GF / v.gp:.2f} | |
| Goals allowed, actual | {gfa.loc[US].GA / b.gp:.2f} | {gfa.loc[THEM].GA / v.gp:.2f} | |
| Shots from within 20 feet | {b.close_f_pg:.1f} ({ordn(rk('close_f_pg', US))}) | {v.close_f_pg:.1f} ({ordn(rk('close_f_pg', THEM))}) | {lg.close_f_pg:.1f} |
| Shots allowed from within 20 feet | {b.close_a_pg:.1f} ({ordn(rk('close_a_pg', US, False))}) | {v.close_a_pg:.1f} ({ordn(rk('close_a_pg', THEM, False))}) | {lg.close_f_pg:.1f} |
| Rebound shots created | {b.reb_f_pg:.1f} ({ordn(rk('reb_f_pg', US))}) | {v.reb_f_pg:.1f} ({ordn(rk('reb_f_pg', THEM))}) | {lg.reb_f_pg:.1f} |
| Share of chances, last {nb5} games | {b5:.1%} | {v5:.1%} | |

Ranks are among 32 teams; 1st is best (most created, fewest allowed). Actual goals come from final scores; chances leave
out empty-net shots.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Over the last three seasons
({n_pri:,} shots that reached the net or missed it), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}. Add
up those chances on every shot and you get what a team's chances were worth in goals.

**The source:** the NHL's own play-by-play feed, which records where every shot came from. **The math:** each shot's chance
comes from our model, built on past seasons and tested on a season it hadn't seen; we nudge each season's totals so the
league's chances add up to the league's real goals. **How we checked it:** the full explanation, with the chart, is in our
story on [last year's 50-win season](sabres-50-win-mirage.html).

## The catch: the second night of a back-to-back

![Back-to-backs](sabres-chi-b2b.png)

Since the start of 2023-24 there have been {n_t} games like tonight's: a road team playing for the second night in a row against a
home team that had at least a day off. The tired road team won **{w_t:.0%}** of them. When both teams were rested, road teams won {w_r:.0%}
({n_r:,} games). The gap showed up in every one of the four seasons, which is why we don't think it's luck.

**Our model misses it.** It rates teams by the chances they create and allow, and it doesn't know who played the night before. In the
{m_n_t} games like tonight's from last season and this one (games the model never saw while it was being built), it gave the tired road team
{m_said_t:.0%} on average. Those teams won {m_won_t:.0%}. A gap that size over {m_n_t} games is about {gap / m_se:.1f} times what chance alone would usually
produce. Rested road teams, by comparison, won a little more often than it said ({m_won_r:.0%} against {m_said_r:.0%}).

**Where the drop comes from is less clear.** Tired road teams still got {sh_t:.1%} of the chances in those games, only a little below the {sh_r:.1%} for
rested road teams. Their usual starting goalie was in net {no1_t:.0%} of the time, against {no1_r:.0%} when rested, but the goalies who did play
were only about {abs(gsv_t):.2f} of a goal a game worse than average. Neither explains the whole gap. What we can say is how often it's happened.{prev_line}

Both Sabres goalies played in last night's loss.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good. Tap a Sabres goalie for his card.

| Team | Goalie | Games played in | Saves | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. We hadn't seen confirmed starters when we published. These are small
samples: a goalie's numbers over a dozen games can swing a lot.

## Our prediction: Sabres {p_b:.0%}, Blackhawks {1 - p_b:.0%}

{ledger_status}

Our model expects about **{mu_b:.1f} goals for Buffalo and {mu_v:.1f} for Chicago**, and gives about a {p_tie:.0%} chance the game is tied after 60
minutes. That's the number we've logged, because it's the model we've tested. The back-to-back history above says to read it as
too high: if tonight goes the way games like it have, it's closer to a coin flip.

**Where the number comes from.** The same chances numbers above. Buffalo creates chances worth {b.xgf_pg:.2f} goals a game; Chicago allows
{v.xga_pg:.2f}. Eighteen games is a small sample, so we blend in last season's numbers and pull them toward the league average. That makes
Buffalo's attack worth {off_r[US]:.2f} a game and Chicago's defense {def_r[THEM]:.2f}, against a league average of {lg_r:.2f}. We do the same the other way
for Chicago. Home ice adds about {coef[2]:.2f} of a goal for the Blackhawks. Then we play the game out on paper many times. Ties after 60
minutes go the way they have for home teams in past overtimes and shootouts ({p_ot:.0%} home wins).

![Model test](sabres-chi-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only
what was known before each game. It called the winner {bt[20252026]['right']:.0%} of the time; choosing the home team every time would have been right
{bt[20252026]['home_obs']:.0%}. This season so far ({bt[SEASON]['n']} games) it has called {bt[SEASON]['right']:.0%} right; home teams have won {bt[SEASON]['home_obs']:.0%}. When it gave a team
{calb[bin_i][0]} in 2025-26, as it does Buffalo tonight, that team won {calb[bin_i][2]:.0%} of the time ({calb[bin_i][3]} games).

**What it doesn't count: goalies, or rest.** We tested adding each game's starting goalie and it made the predictions no better: a
goalie's goals saved in the first half of a season tells you little about his second half. Rest is the gap this story found, and it's
on our list to test as part of the model itself, the same way we tested goalies, before we add it.

## What to watch

- **The first period.** Chicago has the {fewest(chi_f)} chances in the league. If Buffalo's legs are there early, the Sabres should be
  the team with the puck.
- **Buffalo's own end.** The Sabres allow the {most(buf_a)} chances in the league, and Tampa Bay had more than twice their chances last night
  while the game was close (see last night's [post-game](sabres-lightning-postgame-nov-11.html)).
- **Results vs. chances.** Buffalo is {l5_rec} in its last {nb5} games with {b5:.0%} of the chances in them. Five games is a small sample,
  but over a full season, results that run ahead of the chances tend to fade (see our [50-win story](sabres-50-win-mirage.html)).

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so
  league xG = league goals (2026-27 factor {cal.loc[SEASON]:.3f}). Share = xGF / (xGF + xGA). Rebound = shot within 3 s of a same-team
  unblocked attempt. Close = within 20 ft. GSAx = xG against minus goals against on unblocked shots, empty net excluded.
- Data through {last_date} ({len(g26)} games). Last-{nb5} shares use each team's five most recent games.
- Back-to-back: rest = days since the team's previous game in the same season; tired road = road rest 1 and home rest 2+; rested = both 2+.
  {n_t} tired-road and {n_r:,} rested games, 2023-24 through {last_date}, regular season. Road win rate by season (tired / rested):
  {'; '.join(f"{str(x_)[:4]}-{str(x_)[6:]} {r.tired:.3f} / {r.rested:.3f}" for x_, r in zip(by.index, by.itertuples()))}. Model check, out of sample
  (2025-26 and 2026-27 to date): tired road mean p {m_said_t:.3f}, won {m_won_t:.3f}, n {m_n_t}, binomial SE {m_se:.3f}; rested road mean p {m_said_r:.3f},
  won {m_won_r:.3f}, n {m_n_r}. Road xG share: tired {sh_t:.3f}, rested {sh_r:.3f}. "Usual starter" = the goalie who faced the most shots in the most games
  for that team that season; starter per game = goalie who faced the most unblocked shots; complete seasons only. GSAx per game for the road team:
  tired {gsv_t:+.3f}, rested {gsv_r:+.3f}.
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`), ratings as of {GAME_DATE}. Team xGF/xGA per game shrunk with
  K={gmod.K} games toward league + {gmod.PRIOR_KEEP} x last season's edge; goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home
  (fit 2023-25); independent Poisson; regulation ties to home at {p_ot:.3f}. Brier: 2025-26 {bt[20252026]['brier']:.4f} (home-team rate
  {bt[20252026]['b_home']:.4f}, record log5 {bt[20252026]['b_rec']:.4f}, coin 0.25); 2026-27 to date {bt[SEASON]['brier']:.4f}. No goalie or rest term.
"""
    (OUT / "2026-11-12-sabres-chi-pregame.md").write_text(md)
    (OUT / "2026-11-12-sabres-chi-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres at Chicago, 8 p.m.: the matchup",
        "big": [[f"{p_b:.0%}", f"Buffalo's chance to win, our model (Chicago {1 - p_b:.0%})"],
                [f"{m_won_t:.0%}", f"How often tired road teams won when our model gave them {m_said_t:.0%}"]],
        "note": (f"Chicago creates the {fewest(chi_f)} chances in the NHL. But Buffalo played last night, and the model doesn't count that: "
                 f"road teams on the second night of a back-to-back have won {w_t:.0%} since 2023-24, against {w_r:.0%} when rested."),
        "explainer": {"kicker": "How we know", "title": "Every shot has a chance of going in.",
                      "text": (f"A shot from within 10 feet went in {close10:.1%} of the time over the last three seasons; from 60 feet or more, "
                               f"{far60:.1%}. Add up those chances on every shot and you get what a team's chances were worth in goals."),
                      "fmt": "pct", "bars": [["Tired road teams", round(float(w_t), 3)], ["Rested road teams", round(float(w_r), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
