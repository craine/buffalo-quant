"""Week 9 matchup story A: Carson Wentz and the Vikings offense vs. the Bills defense (MNF, Nov. 9, 2026).

Writes reports/2026-wk09-wentz-vs-bills-defense.md, two PNGs and a homepage hero JSON. Every number is computed here.
Pinned: 2025 full regular season and 2026 through week 8 (AS_OF), so reruns reproduce the published story.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger.model_v01 import SHRINK, VERSION, prob_over, qb_relative
from src.ledger import points_model as pm
from src.metrics.team import season_table
from src.reports.bills_vikings_preview import ordn, finish
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 8  # AS_OF: 2026 regular season through week 8
WENTZ, MURRAY = "00-0032950", "00-0035228"
MIN_DB = 150
GAME = "2026_09_BUF_MIN"
EP_SEASONS = (2018, 2026)
WHERE = (f"p.season_type='REG' AND p.qb_dropback=1 AND p.epa IS NOT NULL AND COALESCE(p.two_point_attempt,0)=0 "
         f"AND (p.season=2025 OR (p.season={SEASON} AND p.week<={THRU}))")


def dropbacks():
    p = query(f"""SELECT p.season, p.week, p.game_id, p.play_id, p.posteam, p.defteam,
                  COALESCE(p.passer_player_id, p.rusher_player_id) AS pid, p.epa, p.sack, p.pass_attempt, p.complete_pass,
                  p.air_yards, p.cpoe, p.interception, p.fumble_lost, p.yards_gained, p.wp,
                  f.n_blitzers, f.is_interception_worthy
                  FROM raw_pbp p LEFT JOIN raw_ftn f ON f.nflverse_game_id = p.game_id AND f.nflverse_play_id = p.play_id
                  WHERE {WHERE}""")
    p["att"] = (p.pass_attempt == 1) & (p.sack == 0)
    p["deep"] = p.att & (p.air_yards >= 20)
    p["short"] = p.att & (p.air_yards < 20)
    p["to"] = (p.interception.fillna(0) + p.fumble_lost.fillna(0)) > 0
    p["blitz"] = p.n_blitzers > 0
    p["expl"] = (p.yards_gained >= 20) & (p.sack == 0)
    p["close"] = (p.wp >= 0.10) & (p.wp <= 0.90)
    return p


def qb_line(x):
    a = x[x.att]
    c = x[x.close]
    return pd.Series(dict(db=len(x), g=x.game_id.nunique(), epa=x.epa.mean(), epa_close=c.epa.mean(), n_close=len(c),
                          sk=x.sack.mean(), deep_share=a.deep.mean(), n_att=len(a), n_deep=int(x.deep.sum()),
                          short_epa=x[x.short].epa.mean(), cpoe=a.cpoe.mean(), to=x.to.mean(),
                          intw=a.is_interception_worthy.mean(), n_intw=int(a.is_interception_worthy.sum()),
                          blitz_faced=x.blitz.mean(), epa_blitz=x[x.blitz == True].epa.mean(), n_blitz=int((x.blitz == True).sum())))


def def_line(x):
    a = x[x.att]
    c = x[x.close]
    return pd.Series(dict(db=len(x), short_epa=x[x.short].epa.mean(), short_epa_close=c[c.short].epa.mean(),
                          n_short=int(x.short.sum()), deep_epa=x[x.deep].epa.mean(), deep_epa_close=c[c.deep].epa.mean(),
                          n_deep=int(x.deep.sum()), deep_share=a.deep.mean(), short_ypa=x[x.short].yards_gained.mean(),
                          blitz=x.blitz.mean(), n_blitz=int((x.blitz == True).sum()), sk_blitz=x[x.blitz == True].sack.mean(),
                          sk_noblitz=x[x.blitz == False].sack.mean(), expl=x.expl.mean(), to=x.to.mean()))


def rank(s, team, low_is_good):
    return int(s.rank(ascending=low_is_good, method="min").loc[team])


def ep_examples():
    a, b = EP_SEASONS
    w = (f"season BETWEEN {a} AND {b} AND NOT (season = {SEASON} AND week > {THRU}) AND season_type='REG' "
         "AND (pass=1 OR rush=1) AND epa IS NOT NULL")
    ep = query(f"SELECT yardline_100 y, AVG(ep) ep, COUNT(*) n FROM raw_pbp WHERE {w} AND down=1 AND ydstogo=10 GROUP BY 1").set_index("y")
    third = query(f"""SELECT CASE WHEN sack=1 THEN 'sack' WHEN third_down_converted=1 THEN 'conv' ELSE 'fail' END o,
                      COUNT(*) n, AVG(epa) epa FROM raw_pbp WHERE {w} AND down=3 AND ydstogo=8 AND qb_dropback=1 GROUP BY 1""").set_index("o")
    return ep, third


def main():
    p = dropbacks()
    q = p.groupby(["season", "pid"]).apply(qb_line)
    lgq = {se: qb_line(p[p.season == se]) for se in (2025, SEASON)}
    pool = {se: q.loc[se][q.loc[se].db >= MIN_DB] for se in (2025, SEASON)}
    n_pool = {se: len(pool[se]) for se in pool}
    w25, w26, m26 = q.loc[(2025, WENTZ)], q.loc[(SEASON, WENTZ)], q.loc[(SEASON, MURRAY)]
    r25 = lambda col, low: rank(pool[2025][col], WENTZ, low)
    w_rk = dict(epa=r25("epa", False), epa_close=r25("epa_close", False), sk=r25("sk", True), intw=r25("intw", True),
                to=r25("to", True), short_epa=r25("short_epa", False), deep_share=r25("deep_share", False))
    sk_most = n_pool[2025] - w_rk["sk"] + 1        # 1 = sacked most often
    intw_most = n_pool[2025] - w_rk["intw"] + 1    # 1 = most interception-worthy throws
    m_rk = rank(pool[SEASON]["epa"], MURRAY, False)
    m_rk_close = rank(pool[SEASON]["epa_close"], MURRAY, False)

    d = p[p.season == SEASON]
    D = d.groupby("defteam").apply(def_line)
    lgd = def_line(d)
    bd = D.loc["BUF"]
    b_rk = dict(short=rank(D.short_epa, "BUF", True), short_close=rank(D.short_epa_close, "BUF", True),
                deep=rank(D.deep_epa, "BUF", True), deep_close=rank(D.deep_epa_close, "BUF", True),
                short_ypa=rank(D.short_ypa, "BUF", True), deep_share=rank(D.deep_share, "BUF", True),
                blitz=rank(D.blitz, "BUF", False), expl=rank(D.expl, "BUF", True), to=rank(D.to, "BUF", False))

    off = season_table("off", [SEASON], max_week=THRU).set_index("team")
    de = season_table("def", [SEASON], max_week=THRU).set_index("team")
    mo, bdt = off.loc["MIN"], de.loc["BUF"]
    t3 = query(f"""SELECT defteam, SUM(third_down_converted) c, SUM(third_down_converted) + SUM(third_down_failed) n FROM raw_pbp
                   WHERE season={SEASON} AND week<={THRU} AND season_type='REG' AND down=3 AND (pass=1 OR rush=1)
                   GROUP BY 1""").set_index("defteam")
    t3["r"] = t3.c / t3.n
    t3_rk = rank(t3.r, "BUF", True)
    ep, third = ep_examples()

    # Ledger calls (same model and inputs as the week 9 card), pinned to week 8
    w_db, n_db = qb_relative(WENTZ, "dropback_epa", [2025, SEASON], max_week=THRU)
    w_sk, n_sk = qb_relative(WENTZ, "sack_rate", [2025, SEASON], max_week=THRU)
    c1 = prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=w_db, max_week=THRU)
    c2 = prob_over("MIN", "BUF", "rush_epa", 0.0, max_week=THRU)
    c3 = prob_over("MIN", "BUF", "sack_rate", 0.06, off_override=w_sk, max_week=THRU)
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.game_id == GAME] if not lp.empty else lp
    if len(lp):
        ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min()} UTC, before kickoff.** "
                         "These are graded after the game, hit or miss, and stay up either way.")
    else:
        ledger_status = ("**This is our model's number.** It counts once it's logged on the [Ledger](../ledger.html) before "
                         "kickoff; every logged call is graded after the game, hit or miss.")

    pts = lambda v: "0.00" if abs(v) < 0.005 else f"{v:+.2f}"
    h = lambda v: "0" if abs(v) < 0.005 else f"{v * 100:+.0f}"  # points per 100 plays, for the story body
    n_games = d[d.defteam == "BUF"].game_id.nunique()
    extra_short = (bd.short_epa - lgd.short_epa) * bd.n_short
    # Opponent adjustment (6+ weeks played): what each offense did on short passes in its other games
    sh = d[d.short]
    bsh = sh[sh.defteam == "BUF"]
    exp_adj = 0.0
    for (gid, off_tm), grp in bsh.groupby(["game_id", "posteam"]):
        other = sh[(sh.posteam == off_tm) & (sh.game_id != gid)]
        exp_adj += len(grp) * other.epa.mean()
    extra_adj = bsh.epa.sum() - exp_adj
    gain = ep.loc[25, 'ep'] - ep.loc[75, 'ep']
    close25 = p[(p.season == 2025) & p.close & p.short]
    sc = close25.groupby("pid").epa.mean()
    sc = sc[sc.index.isin(pool[2025].index)]
    w_short_close_rk = rank(sc, WENTZ, False)
    n_short_close_pool = len(sc)
    n_deep_close = int(d[(d.defteam == "BUF") & d.close & d.deep].shape[0])
    # ---- Minnesota points projection (points model, tested on 2024-26 games it never saw)
    coef, res, te, summ = pm.backtest()
    g_dr = pm._drives()
    o_r, d_r, lg_ppd, pace, lg_pace = pm.ratings(g_dr, SEASON, THRU + 1)
    raw_pts, ppd_min, drv_min = pm.raw_prediction(o_r, d_r, lg_ppd, pace, lg_pace, "MIN", "BUF")
    proj = pm.predict(coef, raw_pts, 1)
    lo, hi80 = proj + np.quantile(res, [0.1, 0.9])
    ths = [10, 14, 17, 20, 24, 27, 30]
    chance = {t: pm.prob_at_least(proj, t, res) for t in ths}
    cur = g_dr[(g_dr.season == SEASON) & (g_dr.week <= THRU)]
    min_off_raw = cur[cur.posteam == "MIN"].pts.sum() / cur[cur.posteam == "MIN"].n.sum()
    min_off_n = int(cur[cur.posteam == "MIN"].n.sum())
    buf_def_raw = cur[cur.defteam == "BUF"].pts.sum() / cur[cur.defteam == "BUF"].n.sum()
    buf_def_n = int(cur[cur.defteam == "BUF"].n.sum())
    # calibration on the test games: chances between 60% and 80%
    cal = [(pm.prob_at_least(p_, t, res), y >= t) for p_, y in zip(te.model, te.score) for t in ths]
    cal = pd.DataFrame(cal, columns=["p", "y"]); c68 = cal[(cal.p >= 0.6) & (cal.p < 0.8)]
    tot = summ.n.sum()
    mae_m = (summ.model * summ.n).sum() / tot; mae_l = (summ.league * summ.n).sum() / tot
    mae_t = (summ.team_ppg * summ.n).sum() / tot; w7 = (summ.within7 * summ.n).sum() / tot
    PTS_THR = 20

    # ---- chart 3: chance Minnesota scores at least X
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    xs = np.arange(len(ths))
    cols = [RED if t == PTS_THR else GRAY for t in ths]
    ax.bar(xs, [chance[t] for t in ths], 0.62, color=cols, zorder=2)
    for x_, t in zip(xs, ths):
        ax.text(x_, chance[t] + 0.02, f"{chance[t]:.0%}", ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_xticks(xs, [f"{t}+" for t in ths], fontsize=10)
    ax.set_xlabel("Minnesota points", fontsize=10, color=MUTED)
    ax.set_ylim(0, 1.08); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Our projection: Minnesota scores about {proj:.0f}",
           f"Chance the Vikings score at least this many points Monday. Most likely range: {lo:.0f} to {hi80:.0f} (8 times in 10).",
           f"Points model {pm.VERSION}: 2026 drives through week {THRU}, home field, tested on {int(tot)} team-games from 2024-26 it never saw.")
    fig.savefig(OUT / "wk09a-min-points.png"); plt.close(fig)

    # ---- chart 1: Bills pass defense, short vs deep, all plays and close games
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), dpi=200, sharey=True)
    panels = [("All plays", "short_epa", "deep_epa", b_rk["short"], b_rk["deep"]),
              ("Close games only (win chance 10-90%)", "short_epa_close", "deep_epa_close", b_rk["short_close"], b_rk["deep_close"])]
    for ax, (title, s_col, dc, rs, rd) in zip(axes, panels):
        x = np.arange(2); w = 0.36
        buf = [bd[s_col] * 100, bd[dc] * 100]; lg = [lgd[s_col] * 100, lgd[dc] * 100]
        ax.bar(x - w / 2, buf, w, color=BLUE, label="Bills defense", zorder=2)
        ax.bar(x + w / 2, lg, w, color=GRAY, label="League average", zorder=2)
        for i, (v, r_) in enumerate(zip(buf, (rs, rd))):
            ax.text(i - w / 2, max(v, 0) + 1, f"{h(v / 100)}\n{ordn(r_)} of 32", ha="center", va="bottom", fontsize=9, color=INK)
        for i, v in enumerate(lg):
            ax.text(i + w / 2, v + 1, f"{h(v / 100)}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.set_xticks(x, ["Short throws\n(under 20 yards in the air)", "Deep throws\n(20+ yards)"], fontsize=9.5)
        ax.axhline(0, color=INK, lw=1); ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    axes[0].set_ylabel("Points per 100 throws (lower = better defense)")
    axes[0].legend(frameon=False, fontsize=9, loc="upper left")
    hi = max(D[["short_epa", "deep_epa", "short_epa_close", "deep_epa_close"]].loc["BUF"].max(), lgd.deep_epa, lgd.deep_epa_close)
    axes[0].set_ylim((min(0, bd.deep_epa_close) - 0.08) * 100, (hi + 0.18) * 100)
    finish(fig, "The Bills bend most on short throws",
           f"What every 100 throws were worth to the offense, against the Bills vs. an average defense. 2026 through week {THRU}. 1st = best defense.",
           f"Bills: {int(bd.n_short)} short and {int(bd.n_deep)} deep attempts faced. Both deep samples are small ({int(bd.n_deep)} all plays, {n_deep_close} in close games).")
    fig.savefig(OUT / "wk09a-bills-short-deep.png"); plt.close(fig)

    # ---- chart 2: Wentz's risk profile, 2025
    items = [("Sacked, share of dropbacks", w25.sk, lgq[2025].sk, f"{ordn(sk_most)}-highest rate of {n_pool[2025]}"),
             ("Throws that should have been intercepted", w25.intw, lgq[2025].intw, f"{ordn(intw_most)}-highest rate of {n_pool[2025]}"),
             ("Turnovers, share of dropbacks", w25.to, lgq[2025].to, f"{ordn(w_rk['to'])} of {n_pool[2025]}, 1st = fewest")]
    fig, ax = plt.subplots(figsize=(9.5, 4.9), dpi=200)
    ys = np.arange(len(items))[::-1]
    for y, (lab, v, lg, note) in zip(ys, items):
        ax.barh(y + 0.18, v, 0.34, color=RED, zorder=2)
        ax.barh(y - 0.18, lg, 0.34, color=GRAY, zorder=2)
        ax.text(v + 0.002, y + 0.18, f"Wentz {v:.1%}  ({note})", va="center", fontsize=9, color=INK)
        ax.text(lg + 0.002, y - 0.18, f"League {lg:.1%}", va="center", fontsize=9, color=MUTED)
    ax.set_yticks(ys, [i[0] for i in items], fontsize=10)
    ax.set_xlim(0, max(max(i[1], i[2]) for i in items) * 1.9)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.02))
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Wentz's 2025: lots of sacks and risky throws, average turnovers",
           f"Carson Wentz, 2025 regular season, vs. the league. Ranks among {n_pool[2025]} QBs with {MIN_DB}+ dropbacks.",
           f"Wentz: {int(w25.db)} dropbacks, {int(w25.n_att)} pass attempts. Risky throws charted by FTN Data.")
    fig.savefig(OUT / "wk09a-wentz-risk.png"); plt.close(fig)

    md = f"""# Carson Wentz vs. the Bills defense: short passes, sacks and risky throws

**Finding: Compared with the rest of the league, the Bills' defense is weakest on short passes, the ones thrown less than 20 yards downfield. They rank
{ordn(b_rk['short'])} of 32 there, and {ordn(b_rk['short_close'])} with garbage time removed. Even accounting for the offenses they've faced, short passes have been worth about
{extra_adj:.0f} more points to opponents than you'd expect against an average defense, roughly {extra_adj / n_games:.0f} a game. That's where most of Minnesota's passing will go: like most quarterbacks, Carson Wentz threw short
on {1 - w25.deep_share:.0%} of his attempts last season. But Wentz brings two weak spots of his own. He was sacked on {w25.sk:.1%} of his dropbacks, the
{ordn(sk_most)}-highest rate among {n_pool[2025]} quarterbacks, and his share of throws that should have been intercepted was the {ordn(intw_most)}-highest. Our model projects about {proj:.0f} points for Minnesota.**

*Bills at Vikings, Monday Night Football, Nov. 9, 8:15 p.m. ET, U.S. Bank Stadium (indoors). Kyler Murray is out with a
strained hamstring, so Wentz starts. Numbers are 2026 through week {THRU} unless noted, and Wentz's are mostly from 2025,
since he has dropped back only {int(w26.db)} times this year.*

![Bills short vs deep](wk09a-bills-short-deep.png)

## How we measure it: what a play is worth

Nobody scores on every play, so how can a short pass be "worth" points? Because every play moves a drive closer to
points or further away. Since 2018, 1st-and-10 at your own 25 has been worth about **{ep.loc[75, 'ep']:.1f} points**: that's the
average of the next score in the half, with the other team's scores counted as minus points (so a punt that hands them good
field position counts against you). 1st-and-10 at the opponent's 25 has been worth about **{ep.loc[25, 'ep']:.1f}**. So a pass that moves
the ball from one spot to the other is worth about **{gain:.0f} points**, even though nobody has scored yet. On 3rd-and-8, a
conversion is worth about **{third.loc['conv', 'epa']:+.1f} points**, and a sack costs about **{abs(third.loc['sack', 'epa']):.1f}**.

![Points per play](wk09-points-per-play.png)

**The source:** the NFL's official play-by-play, published free by the nflverse project, covering every snap. For
blitzes and risky throws we add charting from FTN Data, whose analysts watch every play and mark things the official
feed doesn't, like how many defenders rushed and whether a throw should have been picked off.

**The math:** take what the drive was worth after the play, subtract what it was worth before, and that's the play's
value. Add up 100 plays and you get **points per 100 plays**, a fair way to compare teams that run different numbers
of plays. A good defense keeps that number low. It adds up fast: the Bills give up about {(bd.short_epa - lgd.short_epa) * 100:.0f} more points per 100 short
passes than average and face about {bd.n_short / n_games:.0f} a game, which works out to about {extra_short / n_games:.0f} points a game. Part of that is the schedule:
the offenses Buffalo has played have also been good on short passes in their other games. Measured against what those same
offenses did elsewhere, the gap is about {extra_adj:.0f} points, or {extra_adj / n_games:.0f} a game. That's the number we lead with.

**How we checked it:** we ran the efficiency numbers two ways, on all plays and on close-game plays only (when either team
had between a 10% and 90% chance to win), so a few blowout drives can't drive the story. Where the two disagree, we say so.

## Where the Bills bend: short throws

Every 100 short passes against an average defense are worth about **{h(lgd.short_epa)} points** to the offense. Against the Bills,
**{h(bd.short_epa)}**, {ordn(b_rk['short'])} of 32. Over the {int(bd.n_short)} short passes they've faced in {n_games} games, that's about {extra_short:.0f} points of value more than an
average defense would have given up ({extra_adj:.0f} after adjusting for the offenses they've faced). The second check agrees: in close games it's {h(bd.short_epa_close)} per 100 ({ordn(b_rk['short_close'])}), and they give up {bd.short_ypa:.1f} yards per short attempt
({ordn(b_rk['short_ypa'])}; league {lgd.short_ypa:.1f}).

Deep throws are a different story. Opponents have tried them on only {bd.deep_share:.1%} of attempts against Buffalo
({ordn(b_rk['deep_share'])}-fewest), and in close games those deep throws have been worth {h(bd.deep_epa_close)} points per 100 against the Bills, {ordn(b_rk['deep_close'])} in the league
(league average {h(lgd.deep_epa_close)}; only {n_deep_close} attempts, a small sample). Counting blowouts they're {ordn(b_rk['deep'])}, but that's only {int(bd.n_deep)} deep attempts.

Overall the Bills rank {ordn(bdt.dropback_epa_rk)} against the pass ({h(bdt.dropback_epa)} points per 100 dropbacks; league {h(bdt.dropback_epa_lg)}), give up 20-yard plays on {bd.expl:.1%} of dropbacks ({ordn(b_rk['expl'])}; league {lgd.expl:.1%}),
and allow third-down conversions {t3.loc['BUF', 'r']:.0%} of the time ({ordn(t3_rk)}; league {t3.c.sum() / t3.n.sum():.0%}).

## What Wentz brings

| | Wentz 2025 | Wentz 2026 | Murray 2026 | League 2026 |
|---|---|---|---|---|
| Dropbacks | {int(w25.db)} | {int(w26.db)} (small sample) | {int(m26.db)} | |
| Points per 100 dropbacks, all plays | {h(w25.epa)} | {h(w26.epa)} | {h(m26.epa)} ({ordn(m_rk)} of {n_pool[SEASON]}) | {h(lgq[SEASON].epa)} |
| Points per 100 dropbacks, close games | {h(w25.epa_close)} | {h(w26.epa_close)} | {h(m26.epa_close)} ({ordn(m_rk_close)}) | {h(lgq[SEASON].epa_close)} |
| Sacked | {w25.sk:.1%} | {w26.sk:.1%} | {m26.sk:.1%} | {lgq[SEASON].sk:.1%} |
| Share of throws 20+ yards downfield | {w25.deep_share:.1%} | {w26.deep_share:.1%} | {m26.deep_share:.1%} | {lgq[SEASON].deep_share:.1%} |
| Throws that should have been intercepted | {w25.intw:.1%} | {w26.intw:.1%} | {m26.intw:.1%} | {lgq[SEASON].intw:.1%} |

League averages for 2025: {h(lgq[2025].epa)} points per 100 dropbacks, {h(lgq[2025].epa_close)} in close games, sacked {lgq[2025].sk:.1%}, deep share {lgq[2025].deep_share:.1%},
should-have-been-intercepted {lgq[2025].intw:.1%}.

Two things stand out.

**Wentz looks better overall than in close games.** Counting every play, he was about league average last season
({h(w25.epa)} points per 100 dropbacks; league {h(lgq[2025].epa)}). With garbage time removed he drops to {h(w25.epa_close)}, {ordn(w_rk['epa_close'])} of {n_pool[2025]}, meaning that when games were close his
dropbacks moved his team further from points, not closer.
Some of his best numbers came when games were already decided ({int(w25.db - w25.n_close)} dropbacks outside close games, a small sample). Murray this year was {ordn(m_rk)} of {n_pool[SEASON]} overall and {ordn(m_rk_close)} in close
games. By these numbers, neither has been an above-average passer when the game is still in doubt.

**Risk.** Wentz was sacked on {w25.sk:.1%} of dropbacks ({ordn(sk_most)}-highest rate of {n_pool[2025]}) and threw {int(w25.n_intw)} passes that FTN's charters
marked as should-have-been-intercepted, {w25.intw:.1%} of his attempts ({ordn(intw_most)}-highest rate; league {lgq[2025].intw:.1%}). He got away with most of
them: his actual turnover rate was {w25.to:.1%}, about league average ({lgq[2025].to:.1%}).

![Wentz risk profile](wk09a-wentz-risk.png)

## Where it meets

- **Short passes are the matchup.** Most of Wentz's throws are short ({1 - w25.deep_share:.0%}, about the league norm) and the Bills are at
  their weakest there. His own short-throw numbers were good overall ({ordn(w_rk['short_epa'])} of {n_pool[2025]}) but {ordn(w_short_close_rk)} in close games.
  That's where we'd expect the Vikings to attack.
- **The Bills blitz a lot without getting home.** Buffalo sends extra rushers on {bd.blitz:.0%} of dropbacks ({ordn(b_rk['blitz'])}-most), but
  gets sacks on only {bd.sk_blitz:.1%} of those plays (league {lgd.sk_blitz:.1%}) and {bd.sk_noblitz:.1%} without a blitz (league {lgd.sk_noblitz:.1%}).
  Wentz's sack habit is the best chance for that to change. Against the blitz last season, his dropbacks ranked
  {ordn(rank(pool[2025]['epa_blitz'], WENTZ, False))} of {n_pool[2025]} for value, on only {int(w25.n_blitz)} plays.
- **The ground game shouldn't scare anyone.** The average run costs a team a little, because short gains on early downs don't move a drive
  much closer to points. Minnesota's designed runs rank {ordn(mo.rush_epa_rk)}: every 100 have cost the Vikings about {abs(mo.rush_epa) * 100:.0f} points (league average: about {abs(mo.rush_epa_lg) * 100:.0f}).
  The Bills' run defense ranks {ordn(bdt.rush_epa_rk)}, right around average (runs against Buffalo have lost the offense about {abs(bdt.rush_epa) * 100:.0f} points per 100, the league norm).
- **Turnovers.** Buffalo forces turnovers on {bd.to:.1%} of dropbacks ({ordn(b_rk['to'])}; league {lgd.to:.1%}). That's about average. If Wentz keeps
  putting the ball in harm's way, Monday is a chance for that number to go up.

## How many points will Minnesota score?

**Our projection: about {proj:.0f} points**, most likely somewhere between {lo:.0f} and {hi80:.0f}. We give Minnesota a **{chance[PTS_THR]:.0%} chance of
scoring {PTS_THR} or more.**

![Minnesota points](wk09a-min-points.png)

**Where the number comes from.** We start with drives, because points come from drives. This season Minnesota's offense has
scored {min_off_raw:.2f} points per drive ({min_off_n} drives), below the league's {lg_ppd:.2f}. The Bills' defense has allowed {buf_def_raw:.2f} per drive
({buf_def_n} drives), worse than average. Seven games is a small sample, so we pull both numbers part of the way back toward
last season and the league average: Minnesota's offense counts as {o_r["MIN"]:.2f} and Buffalo's defense as {d_r["BUF"]:.2f}.

**The math:** start from the league's {lg_ppd:.2f} points per drive. Minnesota's offense is {lg_ppd - o_r["MIN"]:.2f} worse than average, so take that off;
Buffalo's defense is {d_r["BUF"] - lg_ppd:.2f} worse than average, so add that back. That leaves {ppd_min:.2f} points per drive. Multiply by the {drv_min:.1f} drives a team usually gets in games like this, and you get {raw_pts:.0f}. A final step,
fit on past games, turns that into a real score. It adds back what drives don't count (defensive touchdowns, safeties,
missed extra points), pulls very high and very low projections toward the middle because past games show they overshoot,
and adds about {coef[2]:.1f} points for playing at home. That's how we get to {proj:.0f}.

**How we checked it.** We built the model on 2019-2023 games, then had it predict every 2024, 2025 and 2026 game it had never
seen, using only what was known before kickoff. Its average miss was {mae_m:.1f} points. That beat simply guessing the league
average ({mae_l:.1f}) and guessing each team's own scoring average ({mae_t:.1f}), but not by a lot: football scores bounce around.
It lands within 7 points {w7:.0%} of the time. When it gave something a 60-80% chance, that thing happened {c68.y.mean():.0%} of the
time (it said {c68.p.mean():.0%} on average), so its percentages can be taken at face value.

**What it doesn't know: Wentz.** Minnesota's numbers come mostly from Kyler Murray's games, and the model doesn't know the
quarterback changed. We didn't adjust for it, because we haven't tested an adjustment. By the numbers above, Wentz hasn't
been worse than Murray this year, so the switch shouldn't push the projection down.

{ledger_status}

Our other predictions for Monday come in part 3, after part 2 looks at the Bills offense against Minnesota's defense.

## For the stat-heads

- Points per 100 plays = mean EPA (nflverse expected points added) x 100. Opponent-adjusted short-pass gap: Buffalo's short-pass EPA
  allowed minus, game by game, the opponent's short-pass EPA per attempt in its other 2026 games times its short attempts vs. Buffalo
  (raw gap vs. league average: {extra_short:.1f}; adjusted: {extra_adj:.1f}). Dropbacks: `qb_dropback == 1`, EPA not null, no two-point tries, QB by
  gsis id via `COALESCE(passer_player_id, rusher_player_id)` (scrambles included). Short/deep: pass attempts excluding
  sacks, `air_yards` < 20 vs >= 20. Close games: `wp` between 0.10 and 0.90. Regular season; 2026 through week {THRU}.
- QB ranks among quarterbacks with {MIN_DB}+ dropbacks ({n_pool[2025]} in 2025, {n_pool[SEASON]} in 2026). League values in the QB table are
  play-weighted over all dropbacks. Wentz 2025 close-game sample: {int(w25.n_close)} dropbacks; 2026: {int(w26.n_close)}. Wentz 2025 short throws, close games: {ordn(w_short_close_rk)} of {n_short_close_pool}.
- FTN charting (`raw_ftn`, joined on game and play id): blitz = `n_blitzers` > 0; should-have-been-intercepted =
  `is_interception_worthy` on pass attempts. Wentz 2025: {int(w25.n_intw)} of {int(w25.n_att)} attempts; {int(w25.n_blitz)} dropbacks vs. the blitz.
- Bills defense: {int(bd.db)} dropbacks faced, {int(bd.n_short)} short and {int(bd.n_deep)} deep attempts, {int(bd.n_blitz)} blitzes. Team ranks are among 32
  defenses (1st = best, except blitz rate where 1st = most). Team tables from `src/metrics/team.py` (`max_week={THRU}`).
- Points model {pm.VERSION} (`src/ledger/points_model.py`): ratings = (points + {pm.K} x prior) / (drives + {pm.K}), prior = league + {pm.PRIOR_KEEP} x last
  season's edge; expected drives = average of both teams' drives per game (shrunk 3 games toward league); score = {coef[0]:.2f} + {coef[1]:.3f} x
  drive points + {coef[2]:.2f} x home, fit on 2019-23. Chances from the empirical distribution of training misses (SD {res.std():.1f}).
  Test MAE by season: {', '.join(f'{int(k)} {v.model:.2f} (league {v.league:.2f}, team ppg {v.team_ppg:.2f})' for k, v in summ.iterrows())}.
- Injury news: Kevin O'Connell announced Nov. 5, 2026 that Wentz starts with Murray out (strained hamstring). Source: ESPN.
"""
    (OUT / "2026-wk09-wentz-vs-bills-defense.md").write_text(md)
    (OUT / "2026-wk09-wentz-vs-bills-defense.hero.json").write_text(json.dumps({
        "label": "Monday night: where the matchup is",
        "big": [[ordn(b_rk["short"]), "Bills defense vs. short throws (of 32)"],
                [f"{proj:.0f}", "Vikings points, our projection"]],
        "note": (f"With garbage time removed the Bills are still {ordn(b_rk['short_close'])}. Wentz was sacked on {w25.sk:.1%} of dropbacks last "
                 f"season, the {ordn(sk_most)}-highest rate among {n_pool[2025]} QBs."),
        "explainer": {
            "kicker": "How we know", "title": "Nobody scores every play. Every play still counts.",
            "text": (f"Each snap moves a drive closer to points or further away. 1st-and-10 at your own 25 is worth about "
                     f"{ep.loc[75, 'ep']:.1f} points on average; at the opponent's 25, about {ep.loc[25, 'ep']:.1f}. A pass that gets "
                     f"you from one to the other is worth the difference. Here's what 1st-and-10 is worth by field position."),
            "fmt": "pts",
            "bars": [["Own 25", round(float(ep.loc[75, 'ep']), 2)], ["Midfield", round(float(ep.loc[50, 'ep']), 2)],
                     ["Opp. 25", round(float(ep.loc[25, 'ep']), 2)], ["Opp. 10", round(float(ep.loc[10, 'ep']), 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
