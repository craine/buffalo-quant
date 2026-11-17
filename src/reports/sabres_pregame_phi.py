"""Sabres pregame: Buffalo at Philadelphia, Tue Nov 17, 2026, 7:00 PM ET. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-17-sabres-phi-pregame.md, three PNGs and a hero JSON. Expected goals rescaled per season (league xG = goals).
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
SEASON, US, THEM = 20262027, "BUF", "PHI"
AS_OF = "2026-11-15"  # games through Sunday; Monday's two games (neither BUF nor PHI) weren't final in our feed; pinned
GOLD = "#F74902"  # Flyers orange
GAME_DATE = "2026-11-17"
NICK = {"CHI": "Chicago", "DAL": "Dallas", "PHI": "Philadelphia", "WSH": "Washington", "FLA": "Florida", "TBL": "Tampa Bay"}
RATINGS_BEFORE = "2026-11-16"   # ratings use games before this date (= through AS_OF)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


CH1_TITLE = lambda t, rk: (f"Philadelphia creates the {ordn(33 - rk('xgf_pg', THEM))}-fewest chances. "
                           f"Buffalo allows the {ordn(33 - rk('xga_pg', US, False))}-most")


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
    _ids5 = rec[rec.team == US].sort_values("game_date").game_id.tail(5)
    _x5 = cur[cur.game_id.isin(_ids5)]
    l5x = dict(xgf=_x5[_x5.team == US].xg.sum(), gf=int(_x5[_x5.team == US].goal.sum()),
               xga=_x5[_x5.opp == US].xg.sum(), ga=int(_x5[_x5.opp == US].goal.sum()))
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
    FAV = "Philadelphia" if p_b < 0.5 else "Buffalo"
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
    lp = lp[lp.claim_text.str.contains("Flyers", na=False)] if len(lp) else lp
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
    finish(fig, f"Teams our model gave {calb[bin_i][0]}, like {FAV} tonight, won {calb[bin_i][2]:.0%}",
           f"Every 2025-26 game ({bt[20252026]['n']:,}), predicted using only what was known before each game.",
           f"NHL game model {gmod.VERSION}, fit on 2023-24 and 2024-25.")
    fig.savefig(OUT / "sabres-phi-model-test.png"); plt.close(fig)

    # ---- chart 1: every team's chances created vs allowed
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=200)
    others = t.drop([US, THEM])
    ax.scatter(others.xgf_pg, others.xga_pg, s=42, color="#C9CDD4", zorder=2)
    for tm, col, lab in ((US, BLUE, "Sabres"), (THEM, GOLD, "Flyers")):
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
    finish(fig, CH1_TITLE(t, rk),
           f"All 32 NHL teams, 2026-27 through {pd.to_datetime(last_date):%b. %-d}. Dashed lines are league averages.",
           f"Unblocked shots, empty net excluded, all situations. Sabres {int(b.gp)} games, Flyers {int(v.gp)}.")
    fig.savefig(OUT / "sabres-phi-chances.png"); plt.close(fig)

    # ---- streaks and road trips: next-game results vs what the model said (games through AS_OF)
    lng = pd.concat([gm.assign(team=gm.home, gf=gm.home_score, ga_=gm.away_score, is_home=1),
                     gm.assign(team=gm.away, gf=gm.away_score, ga_=gm.home_score, is_home=0)])[["game_id", "season", "game_date", "team", "gf", "ga_", "is_home"]]
    lng["game_date"] = pd.to_datetime(lng.game_date)
    lng = lng.sort_values(["team", "game_date"])
    lng["won"] = (lng.gf > lng.ga_).astype(int)
    def before(flags):      # length of the run of True values just before each game
        out, n = [], 0
        for f_ in flags:
            out.append(n); n = n + 1 if f_ else 0
        return out
    grp = lng.groupby(["team", "season"])
    lng["skid"] = grp.won.transform(lambda w: pd.Series(before((w == 0).tolist()), index=w.index))
    lng["trip_game"] = grp.is_home.transform(lambda h: pd.Series(before((h == 0).tolist()), index=h.index)) + 1
    mrows = []
    for ss, mxd in ((20252026, None), (SEASON, as_of)):
        mrows.append(gmod.game_rows(gmod.build_frame(tg, [ss], max_date=mxd), coef, p_ot))
    mrows = pd.concat(mrows)
    oos = lng.astype({"game_id": "int64"}).merge(mrows[["game_id", "p_home"]].astype({"game_id": "int64"}), on="game_id")
    oos["p"] = np.where(oos.is_home == 1, oos.p_home, 1 - oos.p_home)
    sk_labs = ["Won last game", "Lost 1", "Lost 2-3 straight", "Lost 4+ straight"]
    oos["sk"] = pd.cut(oos.skid, [-1, 0, 1, 3, 99], labels=sk_labs)
    sk = oos.groupby("sk", observed=True).agg(n=("won", "size"), won=("won", "mean"), said=("p", "mean"))
    rd = oos[oos.is_home == 0].copy()
    tr_labs = ["1st game of trip", "2nd game of trip", "3rd game of trip", "4th or later"]
    rd["tr"] = pd.cut(rd.trip_game, [0, 1, 2, 3, 99], labels=tr_labs)
    tr = rd.groupby("tr", observed=True).agg(n=("won", "size"), won=("won", "mean"), said=("p", "mean"))
    s4 = sk.loc["Lost 4+ straight"]
    s4_se = (s4.won * (1 - s4.won) / s4.n) ** 0.5
    deep = rd[rd.trip_game >= 3]
    deep_n, deep_won, deep_said = len(deep), deep.won.mean(), deep.p.mean()
    buf_l = lng[lng.team == US].sort_values("game_date")
    buf_skid = int(before((buf_l.won == 0).tolist() + [False])[-1])
    _sk_ids = buf_l.game_id.tail(buf_skid)
    skid_ot = int(gm[gm.game_id.isin(_sk_ids)].last_period_type.isin(["OT", "SO"]).sum())
    _xs = cur[cur.game_id.isin(_sk_ids)]
    skx = dict(xgf=_xs[_xs.team == US].xg.sum(), gf=int(_xs[_xs.team == US].goal.sum()),
               xga=_xs[_xs.opp == US].xg.sum(), ga=int(_xs[_xs.opp == US].goal.sum()))
    skx["share"] = skx["xgf"] / (skx["xgf"] + skx["xga"])
    hb = {ss: (bt[ss]["g"].p_home.mean(), bt[ss]["g"].home_won.mean(), len(bt[ss]["g"])) for ss in (20252026, SEASON)}
    home_gap = (hb[20252026][0] - hb[20252026][1]) * 100
    road_all = oos[oos.is_home == 0]
    sch = query(f"SELECT game_date, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') ORDER BY game_date")
    i0 = sch.index[sch.game_date == GAME_DATE][0]
    j = i0
    while j > 0 and sch.loc[j - 1, "away"] == US: j -= 1
    k = i0
    while k + 1 < len(sch) and sch.loc[k + 1, "away"] == US: k += 1
    trip_len, trip_no = k - j + 1, i0 - j + 1
    trip_stops = [NICK.get(x, x) for x in sch.loc[j:k, "home"]]
    next_home = sch.loc[k + 1, "game_date"] if k + 1 < len(sch) else None
    them_l = lng[lng.team == THEM].sort_values("game_date")
    them_rest = (pd.Timestamp(GAME_DATE) - them_l.game_date.iloc[-1]).days
    us_rest = (pd.Timestamp(GAME_DATE) - buf_l.game_date.iloc[-1]).days

    # ---- chart 2: two myths, actual vs model, out of sample
    _src, spg.SRC = spg.SRC, "Source: NHL play-by-play and final scores (league game feed); game model chances from games it never saw (see the story for one caveat)."
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=200, sharey=True)
    for ax, tab_, labs, ttl, hi in ((axes[0], sk, sk_labs, "Losing streaks", "Lost 4+ straight"), (axes[1], tr, tr_labs, "Long road trips", None)):
        xs = np.arange(len(labs)); w = 0.38
        ax.bar(xs - w / 2, [tab_.loc[l, "said"] for l in labs], w, color=GRAY, zorder=2, label="What our model expected")
        ax.bar(xs + w / 2, [tab_.loc[l, "won"] for l in labs], w, color=[BLUE if l == hi or (hi is None and l in ("3rd game of trip", "4th or later")) else "#7F95C6" for l in labs], zorder=2, label="How often they actually won")
        for x_, l in zip(xs, labs):
            ax.text(x_ + w / 2, tab_.loc[l, "won"] + 0.01, f"{tab_.loc[l, 'won']:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK)
            ax.text(x_ - w / 2, tab_.loc[l, "said"] + 0.01, f"{tab_.loc[l, 'said']:.0%}", ha="center", va="bottom", fontsize=8.5, color=MUTED)
        ax.set_xticks(xs, [f"{l}\n({int(tab_.loc[l, 'n']):,} games)" for l in labs], fontsize=9)
        ax.set_title(ttl, loc="left", fontsize=11.5, fontweight="bold", color=INK)
        ax.set_ylim(0, 0.7); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
        ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    axes[0].legend(frameon=False, fontsize=9, loc="upper right")
    finish(fig, "Losing streaks and long road trips don't hurt teams more than our model expects",
           "Win rate vs. what our model expected, every 2025-26 and 2026-27 game it hadn't seen. Left: by losing streak going in. Right: road games, by game of the trip.",
           f"NHL regular season, 2025-26 through {pd.to_datetime(last_date):%b. %-d}, 2026. Any win counts (regulation, overtime, shootout).")
    fig.savefig(OUT / "sabres-phi-myths.png"); plt.close(fig)
    spg.SRC = _src

    if __import__("os").environ.get("DUMP"):
        print("REC", recd(US), recd(THEM), "GP", b.gp, v.gp, "last", last_date)
        print(t.loc[[US, THEM], ["xgf_pg","xga_pg","share","close_f_pg","close_a_pg","reb_f_pg","reb_a_pg"]].round(3).to_string())
        for c,h in [("xgf_pg",1),("xga_pg",0),("share",1),("close_f_pg",1),("close_a_pg",0),("reb_f_pg",1),("reb_a_pg",0)]:
            print(c, "BUF", rk(c,US,bool(h)), "TBL", rk(c,THEM,bool(h)))
        print("GF/GA pg", (gfa.loc[US]/b.gp).round(2).to_dict(), (gfa.loc[THEM]/v.gp).round(2).to_dict())
        print("last5", round(b5,3), l5_rec, round(v5,3)); print("model p_b", round(p_b,3), "mu", round(mu_b,2), round(mu_v,2), "tie", round(p_tie,3))
        print("goalies"); print(pd.concat([bg,vg])[["opp","name","gp","sv","gsax","rk"]].round(3).to_string())
        print(sk.round(3)); print(tr.round(3)); print("skid", buf_skid, "trip", trip_no, "of", trip_len, trip_stops, "next home", next_home, "rest", us_rest, them_rest)
        print("calb", [(c[0], round(c[1],3), round(c[2],3), c[3]) for c in calb]); print("season test", bt[SEASON]["n"], round(bt[SEASON]["right"],3), round(bt[SEASON]["home_obs"],3))
        return
    have = {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies.json").read_text())["cards"]} | \
           {c["name"] for c in json.loads((ROOT / "reports" / "cards" / "goalies_league.json").read_text())["cards"]}
    link = lambda nm: f"[{nm}](../cards/{re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')}.html)" if nm in have else nm
    pgk = vg.set_index("name")
    assert {"Joseph Woll", "Dan Vladar"} <= set(pgk.index)
    gk_rows = "\n".join(f"| {'Sabres' if r.opp == US else 'Flyers'} | {link(r['name'])} | {int(r.gp)} | {r.sv:.1%} | {('0.0, about average,' if abs(r.gsax) < 0.05 else f'{r.gsax:+.1f}')} ({ordn(r.rk)} of {n_gk}) |"
                        for _, r in pd.concat([bg, vg]).iterrows())
    m1 = gm[(gm.season == SEASON) & (((gm.home == US) & (gm.away == THEM)) | ((gm.home == THEM) & (gm.away == US)))]
    assert len(m1) == 1
    m1 = m1.iloc[0]
    m1u = u[u.game_id == m1.game_id]
    m1_us, m1_them = m1u[m1u.team == US].xg.sum(), m1u[m1u.team == THEM].xg.sum()
    m1_sc_us = int(m1.home_score if m1.home == US else m1.away_score)
    m1_sc_them = int(m1.away_score if m1.home == US else m1.home_score)
    assert (m1_sc_us, m1_sc_them, m1.home) == (1, 3, US)
    m1_line = (f"When the teams met in Buffalo on Oct. 21, the Flyers won {m1_sc_them}-{m1_sc_us}. The chances in that game were worth {m1_us:.1f} goals for Buffalo "
               f"and {m1_them:.1f} for Philadelphia. One game is a small sample, and our prediction goes by the full season, blended with last season.")
    assert buf_skid == 4 and trip_no == 3 and trip_len == 6, (buf_skid, trip_no, trip_len)
    buf_a = 33 - rk("xga_pg", US, False)
    phi_f = 33 - rk("xgf_pg", THEM)
    buf_gsax_pg = -bg.gsax.sum() / b.gp
    l5_share_txt = f"{b5:.0%}"
    stops = ", ".join(trip_stops[:-1]) + " and " + trip_stops[-1]
    md = f"""# Sabres at Flyers: four straight losses and a long road trip, and it's still a coin flip

**Our model gives Buffalo a {p_b:.0%} chance to win in Philadelphia Tuesday night (Flyers {1 - p_b:.0%}). The Sabres have lost {buf_skid} straight ({skid_ot} in overtime), and this is game
{trip_no} of a {trip_len}-game road trip. Neither of those changes the number. Since the start of last season, teams on a losing streak of four or more won {s4.won:.0%} of their next
game, exactly what our model expected from their chances ({s4.said:.0%}). And teams deep in a road trip did as well as early in a trip: no sign of wearing down.**

*Buffalo at Philadelphia, Tuesday, Nov. 17, 7 p.m. ET. Buffalo last played Saturday (lost 2-0 at Dallas); Philadelphia played Sunday. Numbers are 2026-27 through
{pd.to_datetime(last_date):%B %-d}: Sabres {recd(US)} in {int(b.gp)} games, Flyers {recd(THEM)} in {int(v.gp)}. Early-season ranks can move a lot.*

![Chances created vs allowed](sabres-phi-chances.png)

## The two teams, side by side

| Per game, 2026-27 | Sabres | Flyers | League average |
|---|---|---|---|
| Chances created (goals they were worth) | {b.xgf_pg:.2f} ({ordn(rk('xgf_pg', US))}) | {v.xgf_pg:.2f} ({ordn(rk('xgf_pg', THEM))}) | {lg.xgf_pg:.2f} |
| Chances allowed | {b.xga_pg:.2f} ({ordn(rk('xga_pg', US, False))}) | {v.xga_pg:.2f} ({ordn(rk('xga_pg', THEM, False))}) | {lg.xgf_pg:.2f} |
| Share of the chances in their games | {b.share:.1%} ({ordn(rk('share', US))}) | {v.share:.1%} ({ordn(rk('share', THEM))}) | 50% |
| Goals scored, actual | {gfa.loc[US].GF / b.gp:.2f} | {gfa.loc[THEM].GF / v.gp:.2f} | |
| Goals allowed, actual | {gfa.loc[US].GA / b.gp:.2f} | {gfa.loc[THEM].GA / v.gp:.2f} | |
| Rebound shots created | {b.reb_f_pg:.1f} ({ordn(rk('reb_f_pg', US))}) | {v.reb_f_pg:.1f} ({ordn(rk('reb_f_pg', THEM))}) | {lg.reb_f_pg:.1f} |
| Share of chances, last {nb5} games | {b5:.1%} | {v5:.1%} | |

Ranks are among 32 teams; 1st is best (most created, fewest allowed). Actual goals come from final scores; chances leave out empty-net shots.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Over the last three seasons ({n_pri:,} shots that weren't
blocked, not counting empty nets), a shot from within 10 feet went in {close10:.1%} of the time; one from 60 feet or more, {far60:.1%}. Add up those chances on
every shot and you get what a team's chances were worth in goals. **The source:** the NHL's own play-by-play feed, which records where every shot came from.
**The math:** each shot's chance comes from our model, built on past seasons and tested on a season it hadn't seen; we nudge each season's totals so the
league's chances add up to the league's real goals. **How we checked it:** the full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## The skid isn't what it looks like

In the {buf_skid} straight losses, Buffalo got {skx['share']:.0%} of the chances, close to an even split. The chances Buffalo created were worth about
{skx['xgf']:.1f} goals, and it scored {skx['gf']}. The chances it allowed were worth about {skx['xga']:.1f}, and it gave up {skx['ga']}, most of that gap in one night, the 8-3 loss
to Tampa Bay. So the skid is more about finishing than goaltending. Over the whole season, Buffalo's goalies are close to average (about {buf_gsax_pg:.2f} goals
a game worse than an average goalie). Philadelphia's problem is different: the Flyers create the {ordn(phi_f)}-fewest chances in the league ({v.xgf_pg:.2f} a game) and allow
more than average.

{m1_line}

## Losing streaks and road trips

![Two myths](sabres-phi-myths.png)

You'll hear that the Sabres are reeling, and that a {trip_len}-game trip ({stops}) wears a team down. We checked both against every game our model hadn't seen
while it was being built (all of last season and this one so far).

- **Losing streaks.** Teams that had lost four or more in a row won **{s4.won:.0%}** of their next game ({int(s4.n)} games). Our model, which never looks at the streak, expected
  {s4.said:.0%}. Teams on a skid do lose more often, mostly because they tend to be weaker teams, which the model already knows from their chances. We found no extra effect from the streak itself, though {int(s4.n)} games can't rule out a small one.
- **Road trips.** On the third game of a trip or later, road teams won **{deep_won:.0%}** ({deep_n} games), when our model expected {deep_said:.0%}. That's the same
  edge over the model they had on the first game of a trip ({tr.loc['1st game of trip', 'won']:.0%} won, {tr.loc['1st game of trip', 'said']:.0%} expected). No sign that a long trip wears teams down.
  The edge itself isn't about trips: road teams in general have beaten our model's number ({road_all.won.mean():.0%} won, {road_all.p.mean():.0%} expected, {len(road_all):,} games), because the model gives home teams a bit too much credit (more below). That fits what we found before the [Chicago game](sabres-blackhawks-pregame-nov-12.html):
  the tiredness that shows up in the results is the second night in a row, not the length of the trip. Buffalo has had two days off, so the back-to-back effect won't apply tonight.

So for Tuesday, the losing streak counts for exactly what the chances in those games were worth, and nothing more.

## In goal

Goals saved compared with an average goalie facing the same shots. Positive is good. Tap a goalie for his card.

| Team | Goalie | Games played in | Saves | Goals saved vs. average |
|---|---|---|---|---|
{gk_rows}

Ranks are among all {n_gk} goalies who have played this season. We hadn't seen confirmed starters when we published. A goalie's numbers over a dozen
games can swing a lot. We tested adding each game's starting goalie to our prediction and it made it no better (details in our [Vegas preview](sabres-vegas-pregame-nov-8.html)): a goalie's goals saved in the first
half of a season is a weak guide to his second half.

## Our prediction: Sabres {p_b:.0%}, Flyers {1 - p_b:.0%}

{ledger_status}

Our model expects about **{mu_b:.1f} goals for Buffalo and {mu_v:.1f} for Philadelphia** ({mu_b:.2f} to {mu_v:.2f} before rounding, so the Flyers are a hair ahead, and ties go to the home team a little more than half the time), and gives about a {p_tie:.0%} chance the game is tied after 60 minutes.

**Where the number comes from.** The chances numbers above. Buffalo creates chances worth {b.xgf_pg:.2f} goals a game; Philadelphia allows {v.xga_pg:.2f}. Early in a season we
blend in last season's numbers and pull everything toward the league average, which makes Buffalo's attack worth {off_r[US]:.2f} a game and Philadelphia's chances allowed {def_r[THEM]:.2f} a game. The other way around,
Philadelphia's attack comes out at {off_r[THEM]:.2f} and Buffalo's chances allowed at {def_r[US]:.2f}. Buffalo creates more, but home ice adds about {coef[2]:.2f} of a goal for the Flyers, and that tips it.
Then we work out the chance of every possible final score; ties after 60 minutes go the way they have for home teams in past overtimes and shootouts ({p_ot:.0%} home wins).

**One caution, and it matters tonight.** Since the start of last season our model has given home teams more than they've actually won: {hb[20252026][0]:.1%} on average
in 2025-26, when home teams won {hb[20252026][1]:.1%} ({hb[20252026][2]:,} games), and {hb[SEASON][0]:.1%} against {hb[SEASON][1]:.1%} this season. Home ice is what tips this game, so Buffalo's real
chance may be a little better than {p_b:.0%}. We're logging the model's number as it is, and we'll look at fixing the home-ice setting after this season's sample grows.

![Model test](sabres-phi-model-test.png)

**How we checked it.** We built the model on the 2023-24 and 2024-25 seasons, then had it call every 2025-26 game using only what was known before each game.
It called the winner {bt[20252026]['right']:.0%} of the time; choosing the home team every time would have been right {bt[20252026]['home_obs']:.0%}. This season so far ({bt[SEASON]['n']} games) it has called
{bt[SEASON]['right']:.0%} right; home teams have won {bt[SEASON]['home_obs']:.0%}. When it gave a team {calb[bin_i][0]} in 2025-26, as it gives {FAV} Tuesday, that team won {calb[bin_i][2]:.0%} of the
time ({calb[bin_i][3]} games). In other words, a true toss-up.

## What to watch

- **Who starts in goal for Philadelphia.** Joseph Woll has saved {pgk.loc['Joseph Woll', 'gsax']:.1f} goals more than an average goalie this season; Dan Vladar has allowed {-pgk.loc['Dan Vladar', 'gsax']:.1f} more.
  Our prediction doesn't change with the starter (see "In goal"), but it's the biggest unknown going in.
- **Philadelphia's recent games.** The Flyers got {v5:.0%} of the chances in their last {nv5} games, better than their season ({v.share:.0%}). Early-season numbers move; watch whether that holds.

## For the stat-heads

- xG: Buffalo Quant Desk model (`src/metrics/nhl_xg.py`), unblocked non-empty-net shots, all strengths, rescaled per season so league xG = league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). The game model works on unrescaled xG, so an average team is {lg_r:.2f} there against {lg.xgf_pg:.2f} in the table. Rebound = within 3 s of a same-team unblocked attempt. Data through {last_date} ({len(g26)} games); Monday Nov. 16's two games
  (neither involves BUF or PHI) were not final in our feed and are left out.
- Streak and trip tests: out of sample (2025-26 and 2026-27 through {as_of}), team-game rows, any win counts. Previous losses in a row:
  {'; '.join(f"{l} won {sk.loc[l, 'won']:.3f} vs model {sk.loc[l, 'said']:.3f} (n {int(sk.loc[l, 'n']):,})" for l in sk_labs)}. Lost 4+ binomial SE {s4_se:.3f}.
  Road games by game number of the road trip: {'; '.join(f"{l} won {tr.loc[l, 'won']:.3f} vs model {tr.loc[l, 'said']:.3f} (n {int(tr.loc[l, 'n']):,})" for l in tr_labs)}.
- Win chance: NHL game model {gmod.VERSION} (`src/ledger/nhl_game_model.py`), ratings from games through {as_of}. Team xGF/xGA per game shrunk with K={gmod.K}
  games toward league + {gmod.PRIOR_KEEP} x last season's edge; goals = {coef[0]:.3f} + {coef[1]:.3f} x expected + {coef[2]:.3f} x home (fit 2023-25), on unrescaled xG;
  independent Poisson; regulation ties to home at {p_ot:.3f}. Brier: 2025-26 {bt[20252026]['brier']:.4f} (home-team rate {bt[20252026]['b_home']:.4f}, record log5
  {bt[20252026]['b_rec']:.4f}, coin 0.25); 2026-27 to date {bt[SEASON]['brier']:.4f}. No goalie, rest, streak or road-trip term.
- GSAx = xG against minus goals against on unblocked shots, empty net excluded. Goalie GSAx per shot, first half vs second half of each season (400+ shots
  each half): r = {', '.join(f'{x:.2f}' for x in rep_g)} for 2023-24 to 2025-26. Adding the starting goalie to the game model did not improve 2024-25 Brier (see the Vegas preview).
- Out-of-sample caveat: the game model never saw 2025-26, but the shot model behind it (`nhl_xg.py`) was trained on 2023-24 to 2025-26 shots, so 2025-26 checks are
  not fully clean; 2026-27 is. Home-team calibration: 2025-26 mean p {hb[20252026][0]:.3f} vs won {hb[20252026][1]:.3f}; 2026-27 {hb[SEASON][0]:.3f} vs {hb[SEASON][1]:.3f}.
"""
    (OUT / "2026-11-17-sabres-phi-pregame.md").write_text(md)
    (OUT / "2026-11-17-sabres-phi-pregame.hero.json").write_text(json.dumps({
        "label": "Sabres at Philadelphia, Tuesday 7 p.m.",
        "big": [[f"{p_b:.0%}", f"Buffalo's chance to win, our model (Flyers {1 - p_b:.0%})"],
                [f"{s4.won:.0%}", f"How often teams on a 4+ game skid won their next game (model expected {s4.said:.0%})"]],
        "note": (f"Four straight losses and game {trip_no} of a {trip_len}-game trip. No sign streaks or long trips matter beyond what the "
                 f"model already counts. Buffalo got {l5_share_txt} of the chances in its last {nb5} games; the finishing hasn't been there, plus one bad night in goal."),
        "explainer": {"kicker": "Losing streaks", "title": "A skid hasn't told us more than the chances already show.",
                      "text": "How often teams that had lost 4+ straight won their next game, 2025-26 to now:",
                      "fmt": "pct", "bars": [["Model expected", round(float(s4.said), 3)], ["Actually won", round(float(s4.won), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
