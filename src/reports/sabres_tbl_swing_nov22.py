"""Sabres post-game, Nov 22, 2026 (Buffalo 6, Tampa Bay 2): the two Tampa games, 11 days apart, and what carries over.

Writes reports/2026-11-22-sabres-tbl-swing.md, one PNG (sabres-tbl-nov22-swing.png) and a hero JSON. Replaces the
unpublished template recap. Expected goals rescaled per season (league xG = goals); chances and the goal split use
unblocked non-empty-net shots. Pinned to games through AS_OF (VAN-CHI pinned in src/reports/pins.py). Ledger P0022 graded
by src/ledger/grade_p0022.py. Keys as in src/reports/sabres_pregame_tbl_nov22.py.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED
from src.reports.pins import drop_late
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
G, NOV11, SEASON, US, THEM = 2026020374, 2026020293, 20262027, "BUF", "TBL"
AS_OF = "2026-11-22"
PRED_ID, PRED_P = "P0022", 0.35
TB_GRAY = "#6E7B8B"
UPL, HILDEBY, TTHOMPSON = 8480045, 8483710, 8479420
PAST = (20232024, 20242025, 20252026)
TEAM = {"MIN": "Minnesota", "CHI": "Chicago", "CBJ": "Columbus", "SJS": "San Jose", "TOR": "Toronto", "VGK": "Vegas", "FLA": "Florida",
        "ANA": "Anaheim", "DAL": "Dallas", "UTA": "Utah", "PHI": "Philadelphia", "WSH": "Washington", "MTL": "Montreal", "LAK": "Los Angeles",
        "OTT": "Ottawa", "TBL": "Tampa Bay"}
PP = ("5v4", "5v3", "4v3")


def team_games(keep, u):
    xf = u.groupby(["game_id", "team"]).xg.sum()
    gf = u.groupby(["game_id", "team"]).goal.sum()
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        rows.append(keep.rename(columns={side: "team", opp: "opp", f"{side}_score": "gf", f"{opp}_score": "ga"})
                    [["game_id", "season", "game_date", "team", "opp", "gf", "ga", "last_period_type"]])
    t = pd.concat(rows, ignore_index=True)
    t["xgf"] = [float(xf.get((g, a), 0)) for g, a in zip(t.game_id, t.team)]
    t["xga"] = [float(xf.get((g, b), 0)) for g, b in zip(t.game_id, t.opp)]
    t["ngf"] = [int(gf.get((g, a), 0)) for g, a in zip(t.game_id, t.team)]   # goals on non-empty-net shots
    t["nga"] = [int(gf.get((g, b), 0)) for g, b in zip(t.game_id, t.opp)]
    t["win"] = t.gf > t.ga
    t["more"] = t.xgf > t.xga
    t["luck"] = (t.ngf - t.xgf) + (t.xga - t.nga)                             # finishing + saves, in goals
    return t


def main(as_of=AS_OF):
    s = shots()
    keep = drop_late(query(f"SELECT g.game_id, g.season, g.game_date, g.home, g.away, g.home_score, g.away_score, g.last_period_type "
                           f"FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id "
                           f"WHERE c.game_type = 2 AND g.game_date <= '{as_of}'"), as_of)
    s = s[s.game_id.isin(set(keep.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    t = team_games(keep, u)
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name

    # ---- the two games
    tw = t[(t.team == US) & t.game_id.isin([NOV11, G])].set_index("game_id")
    a, b = tw.loc[NOV11], tw.loc[G]
    assert (a.gf, a.ga, b.gf, b.ga) == (3, 8, 6, 2) and b.last_period_type == "REG"
    swing = (b.gf - b.ga) - (a.gf - a.ga)
    assert swing == 9
    gk = u[u.game_id.isin([NOV11, G])].groupby(["game_id", "opp", "goalie_id"]).agg(xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    gk["name"] = gk.goalie_id.map(names)
    side = gk.groupby(["game_id", "opp"]).agg(saved=("saved", "sum"), xga=("xga", "sum"), ga=("ga", "sum"),
                                              name=("name", lambda x: ", then ".join(x))).reset_index()
    us_g = side[side.opp == US].set_index("game_id")
    th_g = side[side.opp == THEM].set_index("game_id")
    starts = gk[gk.opp == US].sort_values("xga", ascending=False).groupby("game_id").goalie_id.apply(list)
    assert list(starts.loc[G]) == [UPL] and UPL in starts.loc[NOV11] and len(starts.loc[NOV11]) == 2
    assert list(gk[(gk.opp == THEM) & (gk.game_id == G)].goalie_id) == [HILDEBY]
    n11_us, n11_th = us_g.loc[NOV11], th_g.loc[NOV11]
    n11_upl = gk[(gk.game_id == NOV11) & (gk.goalie_id == UPL)].iloc[0]
    n11_oth = gk[(gk.game_id == NOV11) & (gk.opp == US) & (gk.goalie_id != UPL)].iloc[0]
    en = s[(s.game_id == G) & (s.goal == 1) & (s.empty_net_against == 1)]
    assert len(en) == 1 and en.iloc[0].team == US

    # ---- what carries over: first half vs second half of each team-season, 2023-24 to 2025-26
    t["fin"] = t.ngf - t.xgf                                                  # goals above what the chances were worth
    t["sv"] = t.xga - t.nga                                                   # goals saved vs. the other team's chances
    r = []
    for (se, tm), d in t[t.season.isin(PAST)].sort_values(["game_date", "game_id"]).groupby(["season", "team"]):
        d = d.reset_index(drop=True)
        h = len(d) // 2
        o, e = d.iloc[:h], d.iloc[h:]
        r.append(dict(season=se, team=tm, sh_o=o.xgf.sum() / (o.xgf.sum() + o.xga.sum()), sh_e=e.xgf.sum() / (e.xgf.sum() + e.xga.sum()),
                      fin_o=o.fin.sum(), fin_e=e.fin.sum(), sv_o=o.sv.sum(), sv_e=e.sv.sum(), n=len(d)))
    r = pd.DataFrame(r)
    n_ts = len(r)
    assert n_ts == 96 and (r.n == 82).all()
    rr = {k: float(r[f"{k}_o"].corr(r[f"{k}_e"])) for k in ("sh", "fin", "sv")}
    ex = {}
    for k in ("sh", "fin", "sv"):
        top = r[r[f"{k}_o"] >= r[f"{k}_o"].quantile(0.75)]
        bot = r[r[f"{k}_o"] <= r[f"{k}_o"].quantile(0.25)]
        ex[k] = dict(top_o=float(top[f"{k}_o"].mean()), top_e=float(top[f"{k}_e"].mean()),
                     bot_o=float(bot[f"{k}_o"].mean()), bot_e=float(bot[f"{k}_e"].mean()), n=len(top))
    assert round(ex["sh"]["top_o"], 2) == 0.54 and round(ex["sh"]["top_e"], 2) == 0.53
    assert round(ex["fin"]["top_o"]) == 14 and abs(ex["fin"]["top_e"]) < 1
    assert round(ex["sv"]["top_o"]) == 13 and round(ex["sv"]["top_e"]) == 5
    sv_kept = ex["sv"]["top_e"] / ex["sv"]["top_o"]
    assert 0.3 < sv_kept < 0.4

    # ---- league: does the team with more of the chances win?
    lg = t[t.season.isin(PAST)]
    lg_more_w, lg_more_n = float(lg[lg.more].win.mean()), int(lg.more.sum())
    ty = t[t.season == SEASON]
    ty_agree = float((ty.more == ty.win).mean())

    # ---- Buffalo's season
    bu = t[(t.team == US) & (t.season == SEASON)].sort_values("game_date")
    ngp = len(bu)
    n_more, w_more, w_fewer = int(bu.more.sum()), int(bu[bu.more].win.sum()), int(bu[~bu.more].win.sum())
    agree = int((bu.more == bu.win).sum())
    assert (ngp, n_more, w_more, w_fewer, agree) == (24, 9, 5, 5, 15)
    sh = float(bu.xgf.sum() / (bu.xgf.sum() + bu.xga.sum()))
    ts = ty.groupby("team").agg(xgf=("xgf", "sum"), xga=("xga", "sum"), more=("more", "sum"), gp=("game_id", "size"))
    ts["sh"] = ts.xgf / (ts.xgf + ts.xga)
    sh_rank = int(ts.sh.rank(ascending=False, method="min")[US])
    more_rank_low = int(ts.more.rank(method="min")[US])                      # 1 = fewest games with more chances
    more_tied = int((ts.more == ts.loc[US, "more"]).sum()) > 1
    b_luck = float(bu.luck.sum())
    ts["more_rate"] = ts.more / ts.gp
    n_less = int((ts.more_rate < ts.loc[US, "more_rate"]).sum())
    assert n_less == 8
    bu["xmarg"] = bu.xgf - bu.xga
    best = bu.sort_values("xmarg", ascending=False).head(2)
    best_txt = " and ".join(f"{pd.Timestamp(r.game_date).strftime('%b. %-d').replace('Oct.', 'Oct.').replace('Nov.', 'Nov.')} against {TEAM.get(r.opp, r.opp)}"
                            for r in best.itertuples())
    chance_move = (a.xgf - a.xga) - (b.xgf - b.xga)                           # how far the chances moved toward Tampa Bay
    luck_move = float(b.luck - a.luck)                                        # finishing + saves, Nov. 22 minus Nov. 11
    assert round(luck_move, 1) == 8.5 and abs(luck_move - chance_move + 1 - swing) < 1e-9
    best_marg = [float(x) for x in best.xmarg]
    assert all(round(x) == 2 for x in best_marg)
    b_ngd = int(bu.ngf.sum() - bu.nga.sum())
    assert b_ngd == -11
    b_gd = int(bu.gf.sum() - bu.ga.sum())
    b_xd = float(bu.xgf.sum() - bu.xga.sum())
    rec_w = int(bu.win.sum())
    ot = bu.last_period_type.isin(["OT", "SO"])
    rec = f"{rec_w}-{int((~bu.win & ~ot).sum())}-{int((~bu.win & ot).sum())}"
    pts = int(2 * rec_w + (~bu.win & ot).sum())
    assert rec == "10-10-4" and pts == 24

    # ---- keys (one line) and context
    sa = s.sort_values(["game_id", "period", "t", "eventId"])
    gall = sa[sa.goal == 1]
    gl = gall[gall.game_id == G]
    tb_ppg = int(((gl.team == THEM) & gl.strength.isin(PP)).sum())
    first_team = gl.iloc[0].team
    run_us, run_th = (gl.team == US).cumsum(), (gl.team == THEM).cumsum()
    tied_after = bool(((run_th >= run_us) & (gl.team == THEM)).any())
    g5 = u[(u.game_id == G) & (u.strength == "5v5")]
    e5f, e5a = float(g5[g5.team == US].xg.sum()), float(g5[g5.team == THEM].xg.sum())
    assert tb_ppg == 1 and first_team == US and tied_after and e5f < e5a
    th = ty[(ty.team == THEM) & (ty.game_id != G) & (ty.game_id.isin(keep[keep.home == THEM].game_id))]
    assert (int(th.win.sum()), int((~th.win).sum())) == (10, 1)
    tt = gl[gl.shooter_id == TTHOMPSON]
    goals_all = s[(s.goal == 1) & (s.season == SEASON)].groupby("shooter_id").size()
    tt_g, tt_rank = int(goals_all[TTHOMPSON]), int(goals_all.rank(ascending=False, method="min")[TTHOMPSON])
    assert len(tt) == 2 and (tt_g, tt_rank) == (17, 5)
    sch = query(f"SELECT game_date, start_utc, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') "
                f"AND game_date > '{as_of}' ORDER BY game_date LIMIT 1").iloc[0]
    assert (sch.home, sch.away) == (US, "NYR")
    nxt_day = pd.Timestamp(sch.game_date).strftime("%A")
    nyr = ts.loc["NYR"]
    nyr_rank = int(ts.sh.rank(ascending=False, method="min")["NYR"])

    # ledger
    pr = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    m = pr.merge(gr, left_on="id", right_on="prediction_id")
    m = m[pd.to_datetime(m.graded_at_utc) <= pd.Timestamp(as_of, tz="UTC") + pd.Timedelta(days=2)]
    hit = ((m.probability >= 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))
    nhl = m.sport == "NHL"
    row = m[m.id == PRED_ID].iloc[0]
    assert row.outcome == 1
    brier = float(row.brier)

    # ---- chart: three panels
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.9), dpi=200, gridspec_kw={"width_ratios": [1.15, 1, 1]})
    ax = axes[0]
    xs = np.arange(2)
    for i, (gid, lab) in enumerate(((NOV11, "Nov. 11\nin Buffalo"), (G, "Nov. 22\nin Tampa"))):
        r0 = tw.loc[gid]
        ax.bar(i - 0.2, r0.xgf, 0.36, color=BLUE, alpha=0.35, zorder=2)
        ax.bar(i + 0.2, r0.xga, 0.36, color=TB_GRAY, alpha=0.35, zorder=2)
        ax.scatter([i - 0.2], [r0.gf], s=110, color=BLUE, zorder=4, edgecolor="white", lw=1.5)
        ax.scatter([i + 0.2], [r0.ga], s=110, color=TB_GRAY, zorder=4, edgecolor="white", lw=1.5)
        ax.text(i - 0.2, r0.gf + 0.35, f"{int(r0.gf)}", ha="center", fontsize=10, fontweight="bold", color=BLUE)
        ax.text(i + 0.2, r0.ga + 0.35, f"{int(r0.ga)}", ha="center", fontsize=10, fontweight="bold", color=TB_GRAY)
    ax.set_xticks(xs, ["Nov. 11 in Buffalo", "Nov. 22 in Tampa"], fontsize=9)
    ax.set_ylim(0, 9.5)
    ax.set_title("Bars = what the chances were worth\nDots = goals scored", fontsize=10, color=INK, loc="left")
    ax.text(0.02, 0.97, "Sabres", color=BLUE, fontsize=9, fontweight="bold", transform=ax.transAxes, va="top")
    ax.text(0.02, 0.90, "Lightning", color=TB_GRAY, fontsize=9, fontweight="bold", transform=ax.transAxes, va="top")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True); ax.tick_params(axis="x", length=0)
    ax = axes[1]
    ax.scatter(r.sh_o, r.sh_e, s=16, color=BLUE, alpha=0.55, lw=0)
    lo, hi = min(r.sh_o.min(), r.sh_e.min()), max(r.sh_o.max(), r.sh_e.max())
    ax.plot([lo, hi], [lo, hi], color="#D5D8DE", lw=1, zorder=0)
    ax.set_title("Share of the chances: it lasts", fontsize=10, color=INK, loc="left")
    ax.set_xlabel("First half of the season"); ax.set_ylabel("Second half")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    ax = axes[2]
    pos = [0, 1, 3, 4]
    vals = [ex["fin"]["top_o"], ex["fin"]["top_e"], ex["sv"]["top_o"], ex["sv"]["top_e"]]
    cols = [BLUE, GRAY, BLUE, GRAY]
    ax.bar(pos, vals, 0.8, color=cols, zorder=2)
    for x0, v in zip(pos, vals):
        ax.text(x0, v + (0.5 if v >= 0 else -1.6), "0" if abs(v) < 1 else f"{v:+.0f}", ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xticks([0.5, 3.5], ["Finishing", "Saves"], fontsize=10)
    ax.set_ylim(-3, 17)
    ax.set_title("Best quarter in the first half, then the second", fontsize=10, color=INK, loc="left")
    ax.text(0.5, 0.97, "First half", color=BLUE, fontsize=9, fontweight="bold", transform=ax.transAxes, ha="center", va="top")
    ax.text(0.5, 0.90, "Second half", color=GRAY, fontsize=9, fontweight="bold", transform=ax.transAxes, ha="center", va="top")
    ax.set_yticks([0, 5, 10, 15])
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True); ax.tick_params(axis="x", length=0)
    finish(fig, "Chances last. Finishing doesn't. Goaltending only partly",
           "Left: the two Sabres-Lightning games. Middle and right: every NHL team-season, 2023-24 to 2025-26, first 41 games vs. last 41. Middle: each dot is one team-season.",
           f"Chances exclude empty-net shots; the Nov. 22 dot for Buffalo includes Zach Benson's empty-net goal. Middle and right: {n_ts} team-seasons; top quarter = {ex['fin']['n']} each.")
    fig.savefig(OUT / "sabres-tbl-nov22-swing.png"); plt.close(fig)

    md = f"""# Sabres 6, Lightning 2: a {swing}-goal swing from the 8-3 loss, and the chances didn't cause it

**Eleven days ago, Buffalo and Tampa Bay had even chances and Tampa Bay won 8-3. On Sunday, Tampa Bay had more of the chances and Buffalo won 6-2.
That's a {swing}-goal swing. Tampa Bay's edge in chances actually grew, by {"half a goal" if round(chance_move, 1) == 0.5 else f"{chance_move:.1f} of a goal"}. Finishing and saves made up {luck_move:.1f} goals of the swing, and an empty-netter one more.
Over the last three seasons, finishing hasn't carried over from one half of a season to the next, and goaltending only partly. Chances have.
And on chances, Buffalo has come out ahead in only {n_more} of its {ngp} games.**

*Buffalo at Tampa Bay, Nov. 22. Sabres {rec} ({pts} points). [Our preview](sabres-lightning-pregame-nov-22.html).*

![Chances last, finishing doesn't, goaltending only partly](sabres-tbl-nov22-swing.png)

## Two games, one matchup

| | Nov. 11 in Buffalo | Nov. 22 in Tampa |
|---|---|---|
| Sabres' chances, worth | {a.xgf:.1f} goals | {b.xgf:.1f} goals |
| Lightning's chances, worth | {a.xga:.1f} goals | {b.xga:.1f} goals |
| Final | Lightning {int(a.ga)}, Sabres {int(a.gf)} | Sabres {int(b.gf)}, Lightning {int(b.ga)} |
| Ukko-Pekka Luukkonen | {abs(n11_upl.saved):.1f} goals worse than average (pulled) | {us_g.loc[G, 'saved']:.1f} goals better than average |
| {n11_oth['name']} | {abs(n11_oth.saved):.1f} goals worse than average (in relief) | Didn't play |
| Lightning goalie | {n11_th['name']}: {n11_th.saved:.1f} goals better than average | {th_g.loc[G, 'name']}: {abs(th_g.loc[G, 'saved']):.1f} goals worse than average |

On Sunday Buffalo scored {int(b.ngf)} on Dennis Hildeby, plus an empty-netter, and Tage Thompson scored twice. He has {tt_g}, {ordn(tt_rank)} in the NHL.
Luukkonen started both games. On Nov. 11 he allowed {int(n11_upl.ga)} on chances worth {n11_upl.xga:.1f} and was pulled. On Sunday he allowed {int(us_g.loc[G, 'ga'])} on chances worth {us_g.loc[G, 'xga']:.1f}.

## What lasts, and what doesn't

We split every NHL team's season into its first 41 games and its last 41, for the three seasons before this one ({n_ts} team-seasons). Then we asked:
does how a team did in the first half tell you how it would do in the second?

**Chances: yes.** The quarter of teams that got the most of the chances in the first half got {ex['sh']['top_o']:.0%} of them. In the second half they got {ex['sh']['top_e']:.0%}.
The quarter that got the least got {ex['sh']['bot_o']:.0%}, then {ex['sh']['bot_e']:.0%}.

**Finishing: no.** Take how many more goals a team scored than its chances were worth. The quarter of teams that did best in the first half were {ex['fin']['top_o']:.0f} goals better
than average. In the second half they were {"about average" if abs(ex['fin']['top_e']) < 1 else f"{abs(ex['fin']['top_e']):.0f} {'worse' if ex['fin']['top_e'] < 0 else 'better'}"}. Hot shooting didn't last.

**Saves: a little.** Take how many fewer goals a team's goalies allowed than the other team's chances were worth. The best quarter went from {ex['sv']['top_o']:.0f} goals better than average
to {ex['sv']['top_e']:.0f}. About a third of it stuck. Teams with good goaltending stayed above average, just not by as much.

**How we measure "chances."** Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays.
Add them up and you get what a team's chances were worth in goals. Across the last three seasons, the team with more of the chances won {lg_more_w:.0%} of {lg_more_n:,} games.
More in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## Where that leaves Buffalo

The Sabres have had more of the chances in {n_more} of their {ngp} games. Only {n_less} NHL teams have done it in a smaller share of their games. They won {w_more} of those {n_more} and {w_fewer} of the other {ngp - n_more}.
For the season they get {sh:.1%} of the chances, {ordn(sh_rank)} of 32. Their chances say they should be about {abs(b_xd):.0f} goals behind their opponents. Not counting empty nets, they're {abs(b_ngd)} behind,
so finishing and goaltending haven't been carrying them. They've cost a few goals.

That's the honest read: Sunday's win was real, but the way they won it isn't something to count on. What would change the outlook is more games like {best_txt},
when Buffalo's chances were worth about two goals more than the other team's.

## The keys, and our call

Of the three keys from our preview: Tampa Bay got one power-play goal (hit), Buffalo scored first but Tampa Bay tied it (missed), and Tampa Bay had more of the five-on-five chances (missed).
One of three, and a four-goal win.

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). Buffalo won, so the call goes down as a miss. It scores {brier:.2f} on our scorecard,
where 0 is perfect and a coin flip scores 0.25. We're {int(hit.sum())} of {len(m)} on graded calls, {int(hit[nhl].sum())} of {int(nhl.sum())} on Sabres games. Our model works from chances,
so a night like this one is exactly the kind it gets wrong.

## What's next

The Rangers are in Buffalo on {nxt_day}. They get {nyr.sh:.1%} of the chances this season ({ordn(nyr_rank)} of 32). Watch whether Buffalo wins that part of the game, not just the score.

## For the stat-heads

- xG: our model, unblocked non-empty-net shots, rescaled per season (2026-27 factor {cal.loc[SEASON]:.3f}). Nov. 11 xGF BUF {a.xgf:.2f}, TBL {a.xga:.2f}; Nov. 22 BUF {b.xgf:.2f}, TBL {b.xga:.2f}.
- GSAx: Nov. 11 Luukkonen {n11_upl.saved:+.2f}, {n11_oth['name']} {n11_oth.saved:+.2f}, {n11_th['name']} {n11_th.saved:+.2f}; Nov. 22 Luukkonen {us_g.loc[G, 'saved']:+.2f}, Hildeby {th_g.loc[G, 'saved']:+.2f}.
- First-half vs second-half repeatability (games 1-41 vs 42-82 by date), {n_ts} team-seasons 2023-24 to 2025-26: xG share r = {rr['sh']:.2f}; finishing (G - xG) r = {rr['fin']:.2f};
  saves (xGA - GA) r = {rr['sv']:.2f}; all non-empty-net. Quartile examples: top/bottom 25% by first-half value (n = {ex['sh']['n']}). An odd/even split gives lower values for finishing plus saves; first/second half is the more conservative read.
- More-xG team won {lg_more_w:.3f} of {lg_more_n:,} team-games, 2023-24 to 2025-26 (any result; equal xG excluded from "more"). This season xG side agreed with the result in {ty_agree:.1%}.
- BUF 2026-27: xG share {sh:.3f} ({ordn(sh_rank)}); games with more xG {n_more} of {ngp} ({n_less} teams lower by rate); GD {b_gd:+d} (incl. empty-net), non-empty-net GD {b_ngd:+d}, xGD {b_xd:+.1f}, finishing + saves {b_luck:+.1f}.
- Swing: BUF goal margin {int(a.gf - a.ga):+d} then {int(b.gf - b.ga):+d}; xG margin {a.xgf - a.xga:+.2f} then {b.xgf - b.xga:+.2f}; finishing + saves {float(a.luck):+.2f} then {float(b.luck):+.2f}; empty-net goal +1.
- Keys as in the preview; key 2 graded missed (the preview's wording: no giving it back). Tampa Bay 10-1 at home before the game.
- Data through {as_of}; VAN-CHI, not final at publish, excluded (src/reports/pins.py). Ledger {PRED_ID}: p = {PRED_P}, outcome 1, Brier {brier:.4f}.
"""
    (OUT / "2026-11-22-sabres-tbl-swing.md").write_text(md)
    (OUT / "2026-11-22-sabres-tbl-swing.hero.json").write_text(json.dumps({
        "label": "Same matchup, 11 days apart",
        "big": [[int(swing), "goal swing between the two games"], [round(luck_move, 1), "goals of it from finishing and saves"]],
        "note": f"Finishing and saves swung it. Finishing rarely lasts, and goaltending only partly. Chances do, and Buffalo has had more of them in only {n_more} of {ngp} games.",
        "explainer": {"kicker": "What lasts", "title": "The best finishing teams in the first half were average in the second",
                      "text": "Top quarter of teams by finishing, goals above average:", "fmt": "num",
                      "bars": [["First half", round(ex['fin']['top_o'])], ["Second half", 0 if abs(ex['fin']['top_e']) < 1 else round(ex['fin']['top_e'])]]},
    }, indent=1))
    print(md)
    print(n_less, best_txt, chance_move)


if __name__ == "__main__":
    main()
