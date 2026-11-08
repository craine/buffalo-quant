"""Week 9, story B: Josh Allen and the Bills offense vs. the Vikings defense (MNF, Nov. 9, 2026).

Writes reports/2026-wk09-bills-offense-vs-vikings-defense.md, three PNGs and a homepage hero JSON.
Every number is computed here. Data pinned through 2026 week 8 (AS_OF) so reruns reproduce the published story.
Headline team numbers count every play; garbage-time-filtered ranks are shown alongside.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.qb import ALLEN_ID, dropbacks
from src.metrics.team import season_table
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, AS_OF_WEEK = 2026, 8  # pinned: games through 2026 week 8
SLUG = "2026-wk09-bills-offense-vs-vikings-defense"
SRC = "Source: nflverse play-by-play; FTN charting (blitzes, out-of-pocket plays). Regular season."
EP_SEASONS = (2018, 2026)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def ordn(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def pts(v):
    s = f"{v:+.2f}"
    return "0.00" if s in ("+0.00", "-0.00") else s


def h(v):
    """Points per 100 plays, for the story body."""
    v = round(v * 100)
    return "0" if v == 0 else f"{v:+d}"


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def ep_examples():
    a, b = EP_SEASONS
    w = f"season BETWEEN {a} AND {b} AND season_type='REG' AND (pass=1 OR rush=1) AND epa IS NOT NULL"
    w += f" AND NOT (season = {SEASON} AND week > {AS_OF_WEEK})"
    ep = query(f"SELECT yardline_100 y, AVG(ep) ep, COUNT(*) n FROM raw_pbp WHERE {w} AND down=1 AND ydstogo=10 GROUP BY 1").set_index("y")
    third = query(f"""SELECT CASE WHEN sack=1 THEN 'sack' WHEN third_down_converted=1 THEN 'conv' ELSE 'fail' END o,
                      COUNT(*) n, AVG(epa) epa FROM raw_pbp WHERE {w} AND down=3 AND ydstogo=8 AND qb_dropback=1 GROUP BY 1""").set_index("o")
    return ep, third


def opp_adjusted(season, max_week):
    """Same method as src/metrics/adjust.py league_adjusted_rank, pinned to weeks <= max_week:
    each game's EPA/play allowed minus the opponent's EPA/play in its other games, play-weighted. Rank 1 = best."""
    tw = query(f"""SELECT week, game_id, team, side, plays, epa_sum, dropbacks, dropback_epa_sum FROM clean_team_week
                   WHERE season_type='REG' AND season={season} AND week<={max_week}""")
    off, dfn = tw[tw.side == "off"], tw[tw.side == "def"]
    rows = []
    for g in dfn.itertuples():
        o = off[(off.game_id == g.game_id) & (off.team != g.team)].iloc[0]
        other = off[(off.team == o.team) & (off.game_id != g.game_id)]
        rows.append(dict(team=g.team, plays=g.plays, adj=g.epa_sum / g.plays - other.epa_sum.sum() / other.plays.sum(),
                         adj_db=g.dropback_epa_sum / g.dropbacks - other.dropback_epa_sum.sum() / other.dropbacks.sum()))
    r = pd.DataFrame(rows)
    out = r.groupby("team").apply(lambda x: pd.Series({"adj_epa": (x.adj * x.plays).sum() / x.plays.sum(),
                                                       "adj_db_epa": (x.adj_db * x.plays).sum() / x.plays.sum()}), include_groups=False)
    out["adj_epa_rk"] = out.adj_epa.rank(method="min").astype(int)
    out["adj_db_epa_rk"] = out.adj_db_epa.rank(method="min").astype(int)
    return out


def top3_meetings():
    """Every 2018-2025 regular-season game where a top-3 offense (EPA/play entering the week) met a top-3 defense.
    Ranks use games before that week only; both teams need 4+ prior games."""
    tw = query("SELECT season, week, game_id, team, side, plays, epa_sum FROM clean_team_week "
               "WHERE season_type='REG' AND season BETWEEN 2018 AND 2025")
    rows = []
    for se, g in tw.groupby("season"):
        for wk in sorted(g.week.unique()):
            prior = g[g.week < wk]
            o = prior[prior.side == "off"].groupby("team").agg(p=("plays", "sum"), e=("epa_sum", "sum"), n=("game_id", "nunique"))
            d = prior[prior.side == "def"].groupby("team").agg(p=("plays", "sum"), e=("epa_sum", "sum"), n=("game_id", "nunique"))
            if len(o) < 32 or o.n.min() < 4:
                continue
            lgp = o.e.sum() / o.p.sum()  # league EPA/play over the same prior weeks
            o["v"], d["v"] = o.e / o.p, d.e / d.p
            o["rk"], d["rk"] = o.v.rank(ascending=False, method="min"), d.v.rank(method="min")
            for r in g[(g.week == wk) & (g.side == "off")].itertuples():
                opp = g[(g.game_id == r.game_id) & (g.side == "def") & (g.team != r.team)].team.iloc[0]
                rows.append(dict(season=se, week=wk, off=r.team, de=opp, off_rk=o.rk[r.team], def_rk=d.rk[opp],
                                 off_v=o.v[r.team], def_v=d.v[opp], lg=lgp, game=r.epa_sum / r.plays))
    return pd.DataFrame(rows)


def main():
    off = season_table("off", [SEASON], max_week=AS_OF_WEEK).set_index("team")
    de = season_table("def", [SEASON], max_week=AS_OF_WEEK).set_index("team")
    bo, md = off.loc["BUF"], de.loc["MIN"]
    adj = opp_adjusted(SEASON, AS_OF_WEEK)
    adj_2nd = adj.sort_values("adj_epa").iloc[1]
    adj_2nd_team = adj.sort_values("adj_epa").index[1]
    team_names = {"TB": "Tampa Bay", "DET": "Detroit", "HOU": "Houston", "DEN": "Denver", "BAL": "Baltimore",
                  "PHI": "Philadelphia", "SF": "San Francisco", "KC": "Kansas City", "LAC": "the Chargers", "SEA": "Seattle"}

    # schedule: who the Vikings defense has faced
    tw = query(f"SELECT week, game_id, team, side FROM clean_team_week WHERE season={SEASON} AND season_type='REG' AND week<={AS_OF_WEEK}")
    mg = tw[(tw.team == "MIN") & (tw.side == "def")].game_id
    opp = tw[tw.game_id.isin(mg) & (tw.team != "MIN") & (tw.side == "off")][["week", "team"]].sort_values("week")
    prev = season_table("off", [SEASON - 1]).set_index("team")
    opp["rk26"] = opp.team.map(off.epa_play_rk)
    opp["rk25"] = opp.team.map(prev.epa_play_rk)
    n_top10 = int((opp.rk26 <= 10).sum())
    opp_avg_rk, n_17plus = opp.rk26.mean(), int((opp.rk26 >= 17).sum())

    # dropbacks with FTN charting
    d = dropbacks((2022, SEASON))
    d = d[(d.season < SEASON) | (d.week <= AS_OF_WEEK)].copy()
    # FTN changed n_blitzers in 2026 (it now equals n_pass_rushers - 4), so "blitz" = 5+ pass rushers in every season
    d["blitz"] = np.where(d.ftn_rushers.notna(), (d.ftn_rushers >= 5).astype(float), np.nan)
    d["old_blitz"] = np.where(d.n_blitzers.notna(), (d.n_blitzers > 0).astype(float), np.nan)
    d26 = d[d.season == SEASON]
    ch = d[d.blitz.notna()]

    # Vikings blitz rate, three seasons
    bl = {}
    for se in (2024, 2025, 2026):
        x = ch[ch.season == se]
        t = x.groupby("defteam").agg(blitz=("blitz", "mean"), old=("old_blitz", "mean"), n=("epa", "size"))
        bl[se] = dict(min=t.loc["MIN", "blitz"], rk=int(t.blitz.rank(ascending=False, method="min")["MIN"]),
                      lg=x.blitz.mean(), second=t.blitz.drop("MIN").max(), old=t.loc["MIN", "old"], lg_old=x.old_blitz.mean(),
                      n=int(t.loc["MIN", "n"]))
    assert all(bl[y]["rk"] == 1 for y in bl)
    eq26 = ch[(ch.season == SEASON) & ch.n_blitzers.notna()]
    share_eq26 = (eq26.n_blitzers == eq26.ftn_rushers - 4).mean()
    c26 = ch[ch.season == SEASON]
    mn = c26[c26.defteam == "MIN"]
    min_bl_epa, min_nb_epa = mn[mn.blitz == 1].epa.mean(), mn[mn.blitz == 0].epa.mean()
    min_bl_sack, min_nb_sack = mn[mn.blitz == 1].sack.mean(), mn[mn.blitz == 0].sack.mean()
    lg_bl_epa, lg_nb_epa = c26[c26.blitz == 1].epa.mean(), c26[c26.blitz == 0].epa.mean()
    lg_bl_sack = c26[c26.blitz == 1].sack.mean()
    n_min_bl, n_min_nb = int((mn.blitz == 1).sum()), int((mn.blitz == 0).sum())
    # how many rushers on a Vikings blitz
    min_rushers = mn[mn.blitz == 1].ftn_rushers.mean()
    lg_rushers = c26[c26.blitz == 1].ftn_rushers.mean()
    n_better_bl = None

    # Allen vs the blitz
    a = ch[ch.qb_id == ALLEN_ID]
    a26, a_prev = a[a.season == SEASON], a[a.season.between(2023, 2025)]
    lg_prev = ch[ch.season.between(2023, 2025)]
    allen = dict(
        bl26=a26[a26.blitz == 1].epa.mean(), nb26=a26[a26.blitz == 0].epa.mean(), n_bl26=int((a26.blitz == 1).sum()),
        rate26=a26.blitz.mean(), sack_bl26=a26[a26.blitz == 1].sack.mean(),
        blp=a_prev[a_prev.blitz == 1].epa.mean(), nbp=a_prev[a_prev.blitz == 0].epa.mean(), n_blp=int((a_prev.blitz == 1).sum()),
        lg_blp=lg_prev[lg_prev.blitz == 1].epa.mean(), lg_nbp=lg_prev[lg_prev.blitz == 0].epa.mean())
    qb_bl = c26[c26.blitz == 1].groupby("qb_id").epa.agg(["size", "mean"])
    qb_bl = qb_bl[qb_bl["size"] >= 40]
    qb_nb = c26[c26.blitz == 0].groupby("qb_id").epa.mean()
    drop = (qb_nb.reindex(qb_bl.index) - qb_bl["mean"])
    n_better_bl = int((drop < 0).sum())
    allen_drop, lg_drop = drop[ALLEN_ID], lg_nb_epa - lg_bl_epa
    allen_drop_rk = int(drop.rank(method="min")[ALLEN_ID])
    allen_bl_rk, n_qb_bl = int(qb_bl["mean"].rank(ascending=False, method="min")[ALLEN_ID]), len(qb_bl)

    # off script: Allen out of the pocket vs. Vikings defense against out-of-pocket plays
    o26 = d26[d26.is_qb_out_of_pocket.notna()]
    oop_lg_rate, oop_lg_epa = o26.is_qb_out_of_pocket.mean(), o26[o26.is_qb_out_of_pocket == 1].epa.mean()
    ao = o26[o26.qb_id == ALLEN_ID]
    allen_oop_rate, allen_oop_n, allen_oop_epa = ao.is_qb_out_of_pocket.mean(), int(ao.is_qb_out_of_pocket.sum()), ao[ao.is_qb_out_of_pocket == 1].epa.mean()
    od = o26.groupby("defteam").apply(lambda x: pd.Series({"rate": x.is_qb_out_of_pocket.mean(),
                                                          "epa": x[x.is_qb_out_of_pocket == 1].epa.mean(),
                                                          "n": (x.is_qb_out_of_pocket == 1).sum()}), include_groups=False)
    min_oop = od.loc["MIN"]
    on = o26[(o26.neutral == 1) & (o26.is_qb_out_of_pocket == 1)].groupby("defteam").epa.agg(["size", "mean"])
    min_oop_neu, min_oop_neu_n = on.loc["MIN", "mean"], int(on.loc["MIN", "size"])
    min_oop_neu_rk = int(on["mean"].rank(method="min")["MIN"])
    mo_ = o26[(o26.defteam == "MIN") & o26.blitz.notna()]
    min_oop_bl, min_oop_nb = mo_[mo_.blitz == 1].is_qb_out_of_pocket.mean(), mo_[mo_.blitz == 0].is_qb_out_of_pocket.mean()
    min_oop_rk = int(od.epa.rank(method="min")["MIN"])
    min_oop_rate_rk = int(od.rate.rank(ascending=False, method="min")["MIN"])
    # second view of the off-script collision: success rate (no expected points involved)
    min_oop_succ = o26[(o26.defteam == "MIN") & (o26.is_qb_out_of_pocket == 1)].success.mean()
    lg_oop_succ = o26[o26.is_qb_out_of_pocket == 1].success.mean()
    allen_oop_succ = ao[ao.is_qb_out_of_pocket == 1].success.mean()

    # deep passes (20+ air yards, true attempts)
    att = d26[(d26.pass_attempt == 1) & (d26.sack == 0) & d26.air_yards.notna()].copy()
    att["deep"] = (att.air_yards >= 20).astype(int)
    ddf = att.groupby("defteam").apply(lambda x: pd.Series({"epa_deep": x[x.deep == 1].epa.mean(), "n_deep": x.deep.sum(),
                                                           "epa_short": x[x.deep == 0].epa.mean()}), include_groups=False)
    dof = att.groupby("posteam").apply(lambda x: pd.Series({"rate": x.deep.mean(), "epa_deep": x[x.deep == 1].epa.mean(),
                                                           "n_deep": x.deep.sum()}), include_groups=False)
    deep = dict(lg_epa=att[att.deep == 1].epa.mean(), lg_short=att[att.deep == 0].epa.mean(), lg_rate=att.deep.mean(),
                min_epa=ddf.loc["MIN", "epa_deep"], min_n=int(ddf.loc["MIN", "n_deep"]), min_rk=int(ddf.epa_deep.rank(method="min")["MIN"]),
                min_short=ddf.loc["MIN", "epa_short"], min_short_rk=int(ddf.epa_short.rank(method="min")["MIN"]),
                buf_epa=dof.loc["BUF", "epa_deep"], buf_n=int(dof.loc["BUF", "n_deep"]), buf_rate=dof.loc["BUF", "rate"],
                buf_rate_rk=int(dof.rate.rank(ascending=False, method="min")["BUF"]),
                buf_rk=int(dof.epa_deep.rank(ascending=False, method="min")["BUF"]))

    # best vs best, 2018-2025
    hist = top3_meetings()
    t3 = hist[(hist.off_rk <= 3) & (hist.def_rk <= 3)].copy()
    t3["pred"] = t3.off_v + t3.def_v - t3.lg
    o_others = hist[(hist.off_rk <= 3) & (hist.def_rk > 3)]
    buf_t3 = t3[t3.off == "BUF"]
    n1 = hist[(hist.off_rk == 1) & (hist.def_rk == 1)]

    ep, third = ep_examples()

    # ---- chart 1: the blitz
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.9), dpi=200, gridspec_kw={"width_ratios": [1.2, 1]})
    yrs = [2024, 2025, 2026]
    xs = np.arange(3); w = 0.36
    a1.bar(xs - w / 2, [bl[y]["min"] for y in yrs], w, color=RED, label="Vikings", zorder=2)
    a1.bar(xs + w / 2, [bl[y]["lg"] for y in yrs], w, color=GRAY, label="League average", zorder=2)
    for i, y in enumerate(yrs):
        a1.text(i - w / 2, bl[y]["min"] + 0.01, f"{bl[y]['min']:.0%}", ha="center", va="bottom", fontsize=9.5, color=INK, fontweight="bold")
        a1.text(i + w / 2, bl[y]["lg"] + 0.01, f"{bl[y]['lg']:.0%}", ha="center", va="bottom", fontsize=9, color=INK)
    a1.set_xticks(xs, ["2024", "2025", f"2026\n(thru wk {AS_OF_WEEK})"]); a1.set_ylim(0, 0.9)
    a1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    a1.set_title("Share of dropbacks with 5+ pass rushers", loc="left", fontsize=10.5, fontweight="bold", color=INK)
    a1.legend(frameon=False, fontsize=9, loc="upper left"); a1.grid(axis="y", color="#EEF0F3"); a1.set_axisbelow(True)
    labs = ["Allen\n2026", "Allen\n2023-25", "League\n2023-25"]
    vals = [allen["bl26"] * 100, allen["blp"] * 100, allen["lg_blp"] * 100]
    a2.bar(labs, vals, color=[RED, BLUE, GRAY], width=0.58, zorder=2)
    for i, v in enumerate(vals):
        a2.text(i, v + (1 if v >= 0 else -1), h(v / 100), ha="center", va="bottom" if v >= 0 else "top", fontsize=10, color=INK)
    a2.axhline(0, color=INK, lw=1); a2.set_ylim(min(vals + [0]) - 8, max(vals) + 8)
    a2.set_ylabel("Points per 100 dropbacks when blitzed")
    a2.set_title("Allen when blitzed", loc="left", fontsize=10.5, fontweight="bold", color=INK)
    a2.grid(axis="y", color="#EEF0F3"); a2.set_axisbelow(True)
    finish(fig, "Minnesota blitzes more than anyone. Allen handles it.",
           "Blitz = five or more pass rushers (FTN charting).",
           f"Vikings 2026: {bl[2026]['n']} charted dropbacks. Allen blitzed: {allen['n_bl26']} dropbacks in 2026 (small sample), {allen['n_blp']} in 2023-25.")
    fig.savefig(OUT / "wk09-blitz.png"); plt.close(fig)

    # ---- chart 2: off-script collision
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    labs = [f"Allen off script\n({allen_oop_n} plays)", f"League average\noff script", f"Vikings defense vs.\noff-script plays ({int(min_oop.n)})"]
    vals = [allen_oop_epa * 100, oop_lg_epa * 100, min_oop.epa * 100]
    ax.bar(labs, vals, color=[BLUE, GRAY, RED], width=0.55, zorder=2)
    for i, v in enumerate(vals):
        ax.text(i, v + (2 if v >= 0 else -2), h(v / 100), ha="center", va="bottom" if v >= 0 else "top", fontsize=11, color=INK, fontweight="bold")
    ax.axhline(0, color=INK, lw=1); ax.set_ylim(min(vals) - 15, max(vals) + 15)
    ax.set_ylabel("Points per 100 plays"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Allen's best weapon meets the defense that stops it best",
           f"Dropbacks where the quarterback leaves the pocket, 2026 through week {AS_OF_WEEK}. Below zero = the offense lost points.",
           f"Out-of-pocket per FTN charting. Small samples: {allen_oop_n} Allen plays, {int(min_oop.n)} against the Vikings.")
    fig.savefig(OUT / "wk09-offscript.png"); plt.close(fig)

    # ---- chart 3: when the best meet the best
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    labs = ["Top-3 offense's\naverage coming in", "Top-3 defense's\naverage allowed", "Adding the two\npredicts", "What actually\nhappened"]
    vals = [t3.off_v.mean() * 100, t3.def_v.mean() * 100, t3.pred.mean() * 100, t3.game.mean() * 100]
    ax.bar(labs, vals, color=[BLUE, RED, GRAY, INK], width=0.58, zorder=2)
    for i, v in enumerate(vals):
        ax.text(i, v + (1 if v >= 0 else -1), h(v / 100), ha="center", va="bottom" if v >= 0 else "top", fontsize=11, color=INK, fontweight="bold")
    ax.axhline(0, color=INK, lw=1); ax.set_ylim(min(vals) - 8, max(vals) + 8)
    ax.set_ylabel("Offense's points per 100 plays"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "When a top-3 offense meets a top-3 defense, they meet in the middle",
           f"Every such regular-season game, 2018-2025 ({len(t3)} games). Ranks as of kickoff.",
           "Ranks by points per play over each team's prior games that season (4+ games).")
    fig.savefig(OUT / "wk09-best-vs-best.png"); plt.close(fig)

    opp_rows = "\n".join(f"| {int(r.week)} | {r.team} | {ordn(r.rk26)} | {ordn(r.rk25)} |" for r in opp.itertuples())
    buf_rows = "\n".join(f"| {int(r.season)} | Week {int(r.week)} vs. {r.de} | {h(r.off_v)} | {h(r.game)} |"
                         for r in buf_t3.sort_values(["season", "week"]).itertuples())

    md = f"""# Josh Allen and the Bills offense vs. the NFL's best defense

**Finding: Monday night is the best offense in football ({bo.pts_per_drive:.2f} points per drive) against the best defense ({md.pts_per_drive:.2f} allowed), and the Vikings play defense
like no one else: they send five or more pass rushers on {bl[2026]['min']:.0%} of dropbacks, the most in the NFL by a mile (league average {bl[2026]['lg']:.0%}).
Josh Allen has been one of the league's best quarterbacks against the blitz ({ordn(allen_bl_rk)} of {n_qb_bl}). The collision to watch is
Allen's improvising: every 100 of his plays outside the pocket have been worth about {abs(allen_oop_epa) * 100:.0f} points to Buffalo, and no defense has been
better against those plays than Minnesota's, where every 100 have cost offenses about {abs(min_oop.epa) * 100:.0f}. Both are small samples.**

*Bills at Vikings, Monday Night Football, Nov. 9, 8:15 p.m. ET, U.S. Bank Stadium (indoors). Both teams have played
{int(bo.games)} games. Numbers count every play unless noted. Part 1 covered the Vikings' offense with
Carson Wentz; our predictions for the game come in part 3, logged before kickoff.*

![The blitz](wk09-blitz.png)

## How we measure it: what a play is worth

Nobody scores on every play, but every play moves a drive closer to points or further away. Yards alone don't capture
that: 6 yards on 3rd-and-5 keeps a drive alive, 6 yards on 3rd-and-10 usually means a punt. So we measure every play by
**how much it moved the drive toward points or away from them**. (Same method as [part 1](wentz-vs-bills-defense.html).)

**The source:** the NFL's official play-by-play, cleaned and published free by the nflverse project, plus FTN's
play-by-play charting, which records things the official feed doesn't, like how many defenders rushed and whether
the quarterback left the pocket.

**The reasoning:** since {EP_SEASONS[0]}, 1st-and-10 at your own 25 has been worth about **{ep.loc[75, 'ep']:.1f} points**: that's the average of the
next score in the half, with the other team's scores counted as minus points. 1st-and-10 at the opponent's 25 has been worth
about **{ep.loc[25, 'ep']:.1f}**. On 3rd-and-8, a quarterback who converts adds about **{third.loc['conv', 'epa']:+.1f}**; one who gets sacked loses about
**{abs(third.loc['sack', 'epa']):.1f}**.

**The math:** what the drive was worth after the play, minus what it was worth before, is that play's value. Add up 100 plays and you get **points per 100 plays**, a fair way to compare teams that run different numbers of plays.
A positive number is good for the offense; below zero means the plays, on balance, moved drives away from points. The
average run costs a team a little, because short gains on early downs don't move a drive much closer to points.

**How we checked it:** it tracks scoring. Every 100 Bills plays have been worth {h(bo.epa_play)} points (league average {h(bo.epa_play_lg)}), and Buffalo
scores {bo.pts_per_drive:.2f} points per drive, both 1st. Against Minnesota, every 100 plays have cost offenses about {abs(md.epa_play) * 100:.0f} points, and
the Vikings allow {md.pts_per_drive:.2f} points per drive, both 1st.

## Strength on strength

| | Bills offense | Vikings defense | League average |
|---|---|---|---|
| Points per 100 plays | {h(bo.epa_play)} ({ordn(bo.epa_play_rk)}) | {h(md.epa_play)} allowed ({ordn(md.epa_play_rk)}) | {h(bo.epa_play_lg)} |
| Per 100 pass plays | {h(bo.dropback_epa)} ({ordn(bo.dropback_epa_rk)}) | {h(md.dropback_epa)} allowed ({ordn(md.dropback_epa_rk)}) | {h(bo.dropback_epa_lg)} |
| Per 100 designed runs | {h(bo.rush_epa)} ({ordn(bo.rush_epa_rk)}) | {h(md.rush_epa)} allowed ({ordn(md.rush_epa_rk)}) | {h(bo.rush_epa_lg)} |
| Points per drive | {bo.pts_per_drive:.2f} ({ordn(bo.pts_per_drive_rk)}) | {md.pts_per_drive:.2f} allowed ({ordn(md.pts_per_drive_rk)}) | {bo.pts_per_drive_lg:.2f} |
| Big plays (20+ yard passes, 10+ yard runs) | {bo.explosive_rate:.1%} of plays ({ordn(bo.explosive_rate_rk)}) | {md.explosive_rate:.1%} allowed ({ordn(md.explosive_rate_rk)}) | {bo.explosive_rate_lg:.1%} |
| Sacks | {bo.sack_rate:.1%} of pass plays ({ordn(bo.sack_rate_rk)}) | {md.sack_rate:.1%} made ({ordn(md.sack_rate_rk)}) | {bo.sack_rate_lg:.1%} |
| Turnovers | {bo.turnover_rate:.1%} of plays ({ordn(bo.turnover_rate_rk)}) | {md.turnover_rate:.1%} forced ({ordn(md.turnover_rate_rk)}) | {bo.turnover_rate_lg:.1%} |
| Third downs converted | {bo.third_down_rate:.0%} ({ordn(bo.third_down_rate_rk)}) | {md.third_down_rate:.0%} allowed ({ordn(md.third_down_rate_rk)}) | {bo.third_down_rate_lg:.0%} |
| Red-zone trips ending in a touchdown | {bo.rz_td_rate:.0%} ({ordn(bo.rz_td_rate_rk)}) | {md.rz_td_rate:.0%} allowed ({ordn(md.rz_td_rate_rk)}) | {bo.rz_td_rate_lg:.0%} |

Ranks: 1st is best for that unit. For the Vikings, a negative number means offenses lost points against them. Take out blowout garbage time and the Bills' offense ranks {ordn(bo.epa_play_neutral_rk)} and the Vikings'
defense {ordn(md.epa_play_neutral_rk)}.

Two places Buffalo has an edge on paper: **big plays**, where the Bills lead the league and Minnesota is merely
{ordn(md.explosive_rate_rk)}, and **the run game** ({ordn(bo.rush_epa_rk)} vs. a run defense that's {ordn(md.rush_epa_rk)}). The place Minnesota has the edge: **turnovers**.
The Bills give the ball away on {bo.turnover_rate:.1%} of plays ({ordn(bo.turnover_rate_rk)}), and the Vikings take it away at the {ordn(md.turnover_rate_rk)}-best rate.

## Is Minnesota's defense really this good, or is it the schedule?

Mostly real. The Vikings have faced a below-average set of offenses (their opponents' average rank is {opp_avg_rk:.1f};
{n_17plus} of {len(opp)} rank 17th or worse). But when we compare each game to what that opponent does against everyone else,
Minnesota is still narrowly 1st (just ahead of {team_names.get(adj_2nd_team, adj_2nd_team)}): it has held offenses about {abs(adj.loc['MIN', 'adj_epa']) * 100:.0f} points per 100 plays below
their own averages, vs. about {abs(adj_2nd.adj_epa) * 100:.0f} for {team_names.get(adj_2nd_team, adj_2nd_team)}.

| Week | Opponent | Opponent's offense this season | Last season |
|---|---|---|---|
{opp_rows}

{n_top10} of their {len(opp)} opponents have a top-10 offense this season.

## The blitz

We count a blitz as five or more pass rushers. Most defenses do it on about a third of dropbacks. Minnesota does it on
almost three of every four ({bl[2026]['min']:.0%}), and has led the league three years running ({bl[2024]['min']:.0%} in 2024, {bl[2025]['min']:.0%} in 2025; league
{bl[2024]['lg']:.0%} and {bl[2025]['lg']:.0%}). The next-most aggressive defense this season blitzes {bl[2026]['second']:.0%} of the time. A Vikings blitz isn't bigger
than anyone else's ({min_rushers:.2f} rushers on average; league {lg_rushers:.2f}). It just comes far more often.

Both versions work. When Minnesota blitzes, every 100 dropbacks have cost offenses about {abs(min_bl_epa) * 100:.0f} points ({n_min_bl} plays); when it
doesn't, about {abs(min_nb_epa) * 100:.0f} ({n_min_nb} plays, a small sample), so they've been about as good, maybe slightly better, when they sit back.
Around the league, blitzes this season have come out about even ({h(lg_bl_epa)} points per 100 dropbacks) and produced sacks on {lg_bl_sack:.1%} of
them; Minnesota's blitzes get sacks {min_bl_sack:.1%} of the time.

Allen is the kind of quarterback that approach is built to test, and so far he has passed:

| Allen when blitzed | Dropbacks | Points per 100 dropbacks | League average |
|---|---|---|---|
| 2026 | {allen['n_bl26']} (small sample) | {h(allen['bl26'])} ({ordn(allen_bl_rk)} of {n_qb_bl} QBs with 40+) | {h(lg_bl_epa)} |
| 2023-25 | {allen['n_blp']} | {h(allen['blp'])} | {h(allen['lg_blp'])} |

Like most quarterbacks, he's better when he isn't blitzed ({h(allen['nb26'])} per 100 this season; {n_better_bl} of {n_qb_bl} did better when blitzed).
He starts from such a high level that even when blitzed he's {ordn(allen_bl_rk)} of {n_qb_bl}.

## The off-script collision

The biggest change in Allen's 2026, from our [Josh Allen story](josh-allen-2018-to-now.html): he's leaving the pocket on
{allen_oop_rate:.0%} of dropbacks (league {oop_lg_rate:.0%}), and those plays are working: every 100 have been worth {h(allen_oop_epa)} points ({allen_oop_n} plays; league
average {h(oop_lg_epa)}).

Minnesota is the toughest test for that so far this season. When quarterbacks leave the pocket against the Vikings, every 100 of
those plays have cost their offense about {abs(min_oop.epa) * 100:.0f} points, the best mark in the league ({int(min_oop.n)} plays, a small sample). With garbage time removed it's
about {abs(min_oop_neu) * 100:.0f} per 100, {ordn(min_oop_neu_rk)} ({min_oop_neu_n} plays).

![Off script](wk09-offscript.png)

We checked this a second way, with plain success rate (did the play keep the offense on schedule?) instead of points.
It tells the same story: Allen's off-script plays succeed {allen_oop_succ:.0%} of the time, the league's {lg_oop_succ:.0%}, and Minnesota allows
{min_oop_succ:.0%}. The samples are small on both sides, so this is a matchup to watch, not a verdict.

## Deep shots

The Bills throw deep (20+ yards in the air) on {deep['buf_rate']:.0%} of their passes ({ordn(deep['buf_rate_rk'])}; league {deep['lg_rate']:.0%}), and those throws have been
worth {h(deep['buf_epa'])} points per 100 ({ordn(deep['buf_rk'])}; {deep['buf_n']} throws, a small sample; league {h(deep['lg_epa'])}). Minnesota's short-pass defense is the
league's {ordn(deep['min_short_rk'])}-best, but deep throws against it have still been worth {h(deep['min_epa'])} per 100 ({ordn(deep['min_rk'])}-best; {deep['min_n']} throws, a small sample). A defense that sends extra rushers
leaves fewer defenders back, which is where Buffalo's big-play offense lives.

## What usually happens when the best meet the best

Since 2018, a top-3 offense has met a top-3 defense {len(t3)} times in the regular season. Coming in, those offenses
averaged {h(t3.off_v.mean())} points per 100 plays, and those defenses held offenses to about {abs(t3.def_v.mean()) * 100:.0f} below zero. In the game itself, the offense averaged
**{h(t3.game.mean())}**, close to what you get by simply adding the two strengths together ({h(t3.pred.mean())}). The offense fell short of
its own average {(t3.game < t3.off_v).mean():.0%} of the time. Against everyone else, those same top-3 offenses averaged {h(o_others.game.mean())}.

![Best vs best](wk09-best-vs-best.png)

The Bills have been the top-3 offense in {len(buf_t3)} of those games:

| Season | Game | Bills coming in (points per 100 plays) | Bills in the game |
|---|---|---|---|
{buf_rows}

## What we're watching

- **The blitz vs. Allen.** If Minnesota's pressure gets home, Buffalo's offense is in for a long night. If Allen beats it the way he
  has all season, the Bills' deep game is open behind it.
- **Allen on the move.** It's his best weapon this year and Minnesota's best counter. Those plays could decide the night.
- **Turnovers.** The one area where the Bills' offense is below average meets a defense that takes the ball away.
- Our predictions for the game, including how many points each team scores, come in part 3, logged on the
  [Ledger](../ledger.html) before kickoff.

## For the stat-heads

- Points added = EPA (nflverse/nflfastR expected points). Team splits: `src/metrics/team.py`, regular season through
  week {AS_OF_WEEK}, `pass == 1 or rush == 1`, EPA not null, no kneels/spikes/two-point tries/no-plays. Pass play = dropback
  (sacks and scrambles included). Designed run excludes scrambles. Explosive = pass 20+ or rush 10+ yards. League averages are means of team values.
- Garbage-time filter (WP 10-90%): Bills offense {pts(bo.epa_play_neutral)} ({ordn(bo.epa_play_neutral_rk)}), Vikings defense {pts(md.epa_play_neutral)} ({ordn(md.epa_play_neutral_rk)}).
- Opponent quality: average 2026 offensive rank of Minnesota's seven opponents {opp_avg_rk:.1f}.
- Opponent adjustment: same method as `src/metrics/adjust.py` `league_adjusted_rank`, pinned to week {AS_OF_WEEK} (each game's EPA/play allowed minus the opponent's
  EPA/play in its other games, play-weighted). Vikings {adj.loc['MIN', 'adj_epa']:+.3f} ({ordn(adj.loc['MIN', 'adj_epa_rk'])}); pass defense {adj.loc['MIN', 'adj_db_epa']:+.3f} ({ordn(adj.loc['MIN', 'adj_db_epa_rk'])}).
- Blitz = FTN `n_pass_rushers >= 5` on charted dropbacks, every season. FTN changed `n_blitzers` in 2026: it now equals
  `n_pass_rushers - 4` on {share_eq26:.0%} of 2026 charted dropbacks, so `n_blitzers > 0` means different things before and after
  (Vikings under the old flag: {bl[2024]['old']:.0%}, {bl[2025]['old']:.0%}, {bl[2026]['old']:.0%} for 2024-26). The 2025-to-2026 jump ({bl[2025]['min']:.0%} to {bl[2026]['min']:.0%}) rests
  on one source; no second check is possible until 2026 NFL participation data is published.
  Vikings 2026 sack rate: {min_bl_sack:.1%} blitzing, {min_nb_sack:.1%} not.
  Allen 2026 blitz rate faced {allen['rate26']:.0%}; sacked on {allen['sack_bl26']:.1%} of blitzed dropbacks. Drop from not-blitzed to blitzed:
  Allen {allen_drop:.2f}, league {lg_drop:.2f}; {ordn(allen_drop_rk)}-smallest of {n_qb_bl}.
- Off script = FTN `is_qb_out_of_pocket`; Allen by gsis id ({ALLEN_ID}), dropbacks = `COALESCE(passer_player_id, rusher_player_id)`.
  Vikings face out-of-pocket plays on {min_oop.rate:.0%} of dropbacks ({ordn(min_oop_rate_rk)}-highest rate; league {oop_lg_rate:.0%}): {min_oop_bl:.0%} when
  blitzing, {min_oop_nb:.0%} when not. Garbage-time filtered (WP 10-90%): {pts(min_oop_neu)} ({ordn(min_oop_neu_rk)}, {min_oop_neu_n} plays).
- Deep = air yards 20+ on true pass attempts (no sacks). Minnesota's short-pass (under 20 air yards) EPA allowed {pts(deep['min_short'])}; league {pts(deep['lg_short'])}.
- Best vs best: ranks by EPA/play over prior games only; a week counts once every team has played 4+ games. 2018-2025
  regular season, {len(hist):,} team-games eligible; additive prediction = offense avg + defense avg - league average over the
  same prior weeks. #1 offense vs. #1 defense: {len(n1)} games,
  offense averaged {pts(n1.game.mean())}.
- 2026 NFL participation data (pressure, coverage) has not been published, so this story doesn't use pressure for 2026.
- Data pinned through 2026 week {AS_OF_WEEK}.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "How often the Vikings blitz",
        "big": [[round(float(bl[2026]["min"]) * 100), "Vikings, % of dropbacks"], [round(float(bl[2026]["lg"]) * 100), "League average"]],
        "note": (f"Most in the NFL by a mile; next-highest is {bl[2026]['second']:.0%}. Allen is {ordn(allen_bl_rk)} of {n_qb_bl} QBs "
                 f"against the blitz this season."),
        "explainer": {
            "kicker": "How we know", "title": "Nobody scores every play. Every play still counts.",
            "text": (f"Each snap moves a drive closer to points or further away, and we add that up. Deep throws (20+ yards in the air) "
                     f"are among the most valuable plays, and the Bills throw them more than most. Points per 100 deep throws this season:"),
            "fmt": "per100",
            "bars": [["Bills", round(float(deep["buf_epa"]) * 100)], ["League", round(float(deep["lg_epa"]) * 100)],
                     ["vs. Vikings", round(float(deep["min_epa"]) * 100)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
