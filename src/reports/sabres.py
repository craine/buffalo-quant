"""Five Sabres stories, 2026-27 start vs. 2023-26. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/sabres-*.md and reports/sabres-*.png. Regular season only; shootouts excluded.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import goalie_season, records, shots, team_season
from src.metrics.nhl_xg import validate
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SRC = "Source: NHL play-by-play (api-web.nhle.com), Buffalo Quant Desk expected-goals model. Regular season."
LBL = {20232024: "2023-24", 20242025: "2024-25", 20252026: "2025-26", 20262027: "2026-27"}
CUR, PREV = 20262027, 20252026
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def ordn(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def bars(ax, labels, vals, fmt, hi_last=True, lg=None):
    cols = [RED if (hi_last and i == len(vals) - 1) else BLUE for i in range(len(vals))]
    ax.bar(labels, vals, color=cols, width=0.6, zorder=2)
    for i, v in enumerate(vals):
        ax.text(i, v * 0.5, fmt.format(v), ha="center", va="center", fontsize=10, color="white", fontweight="bold", zorder=4)
    if lg is not None:
        ax.plot(labels, lg, color=INK, lw=1.2, ls="--", marker="o", ms=5, zorder=3)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)


def main():
    s = shots()
    m_ = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[m_].groupby("season").goal.sum() / s[m_].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    r = records()
    gp = r.groupby(["season", "team"]).agg(gp=("w", "size"), w=("w", "sum"), l=("l", "sum"), otl=("otl", "sum"),
                                           gf_all=("gf", "sum"), ga_all=("ga", "sum")).reset_index()
    gp["pts"] = 2 * gp.w + gp.otl
    gp["ppg"] = gp.pts / gp.gp
    t = team_season(s).merge(gp, on=["season", "team"])
    t5 = team_season(s, "5v5").merge(gp[["season", "team", "gp"]], on=["season", "team"])
    b = t.set_index(["season", "team"]).xs("BUF", level="team")
    b5 = t5.set_index(["season", "team"]).xs("BUF", level="team")
    rec = gp[gp.team == "BUF"].set_index("season")
    cur = rec.loc[CUR]
    v = validate(s[(s.unblocked == 1) & (s.empty_net_against == 0)].copy())
    n_shots = int(((s.unblocked == 1) & (s.empty_net_against == 0) & (s.season < CUR)).sum())
    model_note = (f"Expected goals (xG) come from our own model: gradient-boosted trees on shot distance, angle, type, "
                  f"rebounds, rush chances and manpower, trained on {n_shots:,} unblocked shots from 2023-24 to 2025-26. "
                  f"Tested on a season it never saw (2025-26), it beat a distance-and-angle model "
                  f"(AUC {v['auc_gbm']:.2f} vs {v['auc_dist_angle']:.2f}). Empty-net shots are excluded. "
                  f"Values for 2023-24 to 2025-26 come from a model fit on those seasons; 2026-27 is out of sample. Each season "
                  f"is rescaled so league expected goals equal league goals (the raw model ran "
                  f"{(1 / cal.loc[PREV] - 1):+.1%} hot in 2025-26), so above-expected numbers are relative to that season's league average.")
    sample = f"2026-27 is {int(cur.gp)} games ({int(cur.w)}-{int(cur.l)}-{int(cur.otl)}), a small sample."
    stories = {}

    # ---------- 1. The 50-win mirage
    full = t[t.season < CUR].copy()
    full["xgd_pg"] = (full.xGF - full.xGA) / full.gp
    co = np.polyfit(full.xgd_pg, full.ppg, 1)
    full["exp_pts"] = np.polyval(co, full.xgd_pg) * full.gp
    full["over"] = full.pts - full.exp_pts
    resid_sd = full.over.std()
    f25 = full[full.season == PREV].copy()
    f25["over_rk"] = f25.over.rank(ascending=False, method="min").astype(int)
    bf = f25.set_index("team").loc["BUF"]
    corr = lambda x: np.corrcoef(full.xgd_pg, full.ppg)[0, 1]

    def yoy(col):
        a = full[["season", "team", col]]
        c = a.copy(); c["season"] = c.season.map({20232024: 20242025, 20242025: 20252026})
        m = a.merge(c.dropna(), on=["season", "team"], suffixes=("", "_p"))
        return m[col].corr(m[col + "_p"]), len(m)
    st = {c: yoy(c) for c in ["xGF%", "PDO", "sh%", "sv%"]}
    fin25, sav25 = b.loc[PREV, "G-xG"], b.loc[PREV, "xGA-GA"]

    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=200)
    o = full[full.season == PREV]
    ax.scatter(o.xgd_pg, o.pts, s=36, color=GRAY, zorder=2)
    xs = np.linspace(o.xgd_pg.min(), o.xgd_pg.max(), 50)
    ax.plot(xs, np.polyval(co, xs) * 82, color=INK, lw=1.2, ls="--")
    ax.scatter([bf.xgd_pg], [bf.pts], s=120, color=RED, zorder=3, edgecolor="white", lw=2)
    ax.annotate(f"Sabres: {int(bf.pts)} pts\nexpected {bf.exp_pts:.0f}", (bf.xgd_pg, bf.pts), xytext=(-14, 6), ha="right",
                textcoords="offset points", fontsize=10, color=INK, fontweight="bold")
    ax.set_xlabel("Expected-goal differential per game"); ax.set_ylabel("Points")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Last year's Sabres outran their chances by 18 points" if round(bf.over) == 18 else "Last year's Sabres outran their chances",
           "2025-26 regular season, all 32 teams. Dashed line = points expected from shot quality (2023-26 fit).",
           "Points expected from a linear fit of points on xG differential, 2023-24 to 2025-26.")
    fig.savefig(OUT / "sabres-mirage.png"); plt.close(fig)

    stories["sabres-50-win-mirage"] = (
        "The Sabres' 50-win season was built on goals that weren't supposed to happen",
        "Shot quality said last year's team was a 91-point team. They got 109. Here's what that means now.",
        f"""# The Sabres' 50-win season was built on goals that weren't supposed to happen

**Finding: By the quality of chances they created and allowed, the 2025-26 Sabres played like a {bf.exp_pts:.0f}-point
team. They finished with {int(bf.pts)}: {bf.over:+.0f} points over expectation, the {ordn(bf.over_rk)}-largest gap in the NHL.
The extra came from goaltending and finishing, the two least repeatable of the stats we tested.**

*{sample}*

![Mirage](sabres-mirage.png)

## Where the extra points came from

| | Goals | Expected | Difference |
|---|---|---|---|
| Goals scored | {b.loc[PREV, 'GF']:.0f} | {b.loc[PREV, 'xGF']:.1f} | {fin25:+.1f} (finishing) |
| Goals allowed | {b.loc[PREV, 'GA']:.0f} | {b.loc[PREV, 'xGA']:.1f} | {sav25:+.1f} (goaltending) |

That is {fin25 + sav25:+.0f} goals better than their chances, all situations, empty nets excluded. Their expected-goal share
was {b.loc[PREV, 'xGF%']:.1%} ({ordn(t[t.season == PREV]['xGF%'].rank(ascending=False, method='min')[(t.season == PREV) & (t.team == 'BUF')].iloc[0])} in the NHL):
a league-average team by process.

## Why that was unlikely to repeat

Year-to-year correlation for all 32 teams, 2023-24 to 2025-26 ({st['xGF%'][1]} team pairs):

| Stat | What it measures | Correlation with next season |
|---|---|---|
| Expected-goal share | Chances created vs. allowed | {st['xGF%'][0]:.2f} |
| PDO | Shooting % + save % | {st['PDO'][0]:.2f} |
| Shooting % | Finishing | {st['sh%'][0]:.2f} |
| Save % | Goaltending | {st['sv%'][0]:.2f} |

Shot quality carries over. Shooting and save percentages mostly don't. The Sabres' PDO was
{b.loc[PREV, 'PDO']:.3f} ({ordn(t[t.season == PREV]['PDO'].rank(ascending=False, method='min')[(t.season == PREV) & (t.team == 'BUF')].iloc[0])} in the NHL).
This season it is {b.loc[CUR, 'PDO']:.3f} ({ordn(t[t.season == CUR]['PDO'].rank(ascending=False, method='min')[(t.season == CUR) & (t.team == 'BUF')].iloc[0])}).

## What it says about this season

Through {int(cur.gp)} games their expected-goal share is {b.loc[CUR, 'xGF%']:.1%} ({ordn(t[t.season == CUR]['xGF%'].rank(ascending=False, method='min')[(t.season == CUR) & (t.team == 'BUF')].iloc[0])}) and they are {b.loc[CUR, 'G-xG'] + b.loc[CUR, 'xGA-GA']:+.1f}
goals against their chances. In other words, the 2026-27 record looks a lot like what last year's underlying numbers
suggested, without the luck.

## Method and caveats

- {model_note}
- Expected points: a straight-line fit of points on xG differential per game across all 96 team-seasons, 2023-24 to
  2025-26 (correlation {corr(None):.2f}; typical miss {resid_sd:.1f} points). "Expected" is a model estimate, not a guarantee. Points also
  depend on overtime and shootout results and on empty-net goals, which this fit doesn't model.
- Goaltending here = expected goals against minus goals against on unblocked shots, empty nets excluded.
""")

    # ---------- 2. Goalies
    g = goalie_season(s)
    gb = g[(g.team == "BUF") & (g.shots_faced >= 100)].sort_values(["season", "shots_faced"], ascending=[True, False])
    lg_xsv = {se: 1 - x.xg.sum() / x.on_goal.sum() for se, x in s[(s.unblocked == 1) & (s.empty_net_against == 0)].groupby("season")}
    lg_sv = {se: 1 - x.goal.sum() / x.on_goal.sum() for se, x in s[(s.unblocked == 1) & (s.empty_net_against == 0)].groupby("season")}
    upl = gb[(gb.season == CUR) & gb.name.str.contains("Luukkonen")].iloc[0]
    ell = gb[(gb.season == CUR) & gb.name.str.contains("Ellis")].iloc[0]
    lyon = gb[(gb.season == PREV) & gb.name.str.contains("Lyon")].iloc[0]
    upl25 = gb[(gb.season == PREV) & gb.name.str.contains("Luukkonen")].iloc[0]
    tot25 = gb[gb.season == PREV].GSAx.sum(); tot26 = gb[gb.season == CUR].GSAx.sum()
    g26 = g[(g.season == CUR) & (g.shots_faced >= 100)].copy()
    g26["xsv_rk"] = g26["xsv%"].rank(method="min").astype(int)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    rows = gb[gb.season >= PREV]
    lab = [f"{n.split()[-1]}\n{LBL[se]}" for n, se in zip(rows.name, rows.season)]
    cols = [RED if se == CUR else BLUE for se in rows.season]
    ax.bar(lab, rows.GSAx, color=cols, width=0.6, zorder=2)
    for i, (gs, sf) in enumerate(zip(rows.GSAx, rows.shots_faced)):
        ax.text(i, gs + (0.3 if gs >= 0 else -0.3), f"{gs:+.1f}\n({int(sf)} shots)", ha="center", va="bottom" if gs >= 0 else "top", fontsize=9, color=INK)
    ax.axhline(0, color=INK, lw=1); ax.set_ylabel("Goals saved above expected")
    ax.set_ylim(min(rows.GSAx.min(), 0) - 3, rows.GSAx.max() + 3.5)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Last year's goalies beat expectations. This year they're about average.",
           "Goals saved above expected (GSAx), Sabres goalies with 100+ shots faced. Above zero = better than expected.",
           "Unblocked shots, empty nets excluded. 2026-27 small sample.")
    fig.savefig(OUT / "sabres-goalies.png"); plt.close(fig)
    g_rows = "\n".join(f"| {LBL[r_.season]} | {r_['name']} | {int(r_.shots_faced)} | {r_['sv%']:.3f} | {r_['xsv%']:.3f} | {r_.GSAx:+.1f} |" for _, r_ in gb.iterrows())
    stories["sabres-goalies-not-the-problem"] = (
        "The Sabres' goalies aren't the problem. They're just not the bailout anymore.",
        "Luukkonen's save percentage looks ugly. The shots he's facing explain most of it.",
        f"""# The Sabres' goalies aren't the problem. They're just not the bailout anymore.

**Finding: Ukko-Pekka Luukkonen's .{int(round(upl['sv%'] * 1000)):03d} save percentage looks like a collapse, but his expected save percentage,
based on the shots he's faced, is .{int(round(upl['xsv%'] * 1000)):03d}. He is {upl.GSAx:+.1f} goals against expectation and
Colten Ellis is {ell.GSAx:+.1f}. Last year Sabres goalies were {tot25:+.1f}, and about half of that was Alex Lyon, who hasn't dressed for an NHL game this season.**

*{sample} {int(upl.shots_faced)} shots for Luukkonen, {int(ell.shots_faced)} for Ellis.*

![Goalies](sabres-goalies.png)

| Season | Goalie | Shots faced | Save % | Expected save % | Goals saved above expected |
|---|---|---|---|---|---|
{g_rows}

League save % on these shots: {lg_sv[PREV]:.3f} in 2025-26, {lg_sv[CUR]:.3f} in 2026-27. League expected save %:
{lg_xsv[PREV]:.3f} and {lg_xsv[CUR]:.3f}.

## What changed

- **Lyon hasn't played.** He was {lyon.GSAx:+.1f} on {int(lyon.shots_faced)} shots last season and has not dressed for any NHL team in 2026-27.
- **Luukkonen is facing harder shots.** His expected save % is {upl['xsv%']:.3f}, against {upl25['xsv%']:.3f} last season;
  among {len(g26)} goalies with 100+ shots this season that is {ordn(g26.set_index('name').loc[upl['name'], 'xsv_rk'])}-hardest.
- **Combined**, Sabres goalies are {tot26:+.1f} this season after {tot25:+.1f} last season.

Save percentage is one of the least stable stats in the sport (see the companion piece on last season). A
{int(upl.shots_faced)}-shot sample says very little about Luukkonen either way.

## Method and caveats

- {model_note}
- Goals saved above expected = expected goals on unblocked shots faced minus goals allowed. Blocked shots and
  empty-net situations are excluded; deflections and screens are only partly captured.
""")

    # ---------- 3. Same chances, fewer goals
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0) & (s.team == "BUF")]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name

    def per_game(season):
        x = u[u.season == season]
        return x.goal.sum() / rec.loc[season, "gp"], x.xg.sum() / rec.loc[season, "gp"]
    pg = {se: per_game(se) for se in LBL}
    ind = u[u.season == PREV].groupby("shooter_id").agg(G=("goal", "sum"), ixG=("xg", "sum"))
    ind["fin"] = ind.G - ind.ixG; ind["name"] = ind.index.map(names)
    tuch = ind[ind.name == "Alex Tuch"].iloc[0]
    ro = query("""SELECT r.game_id, r.player_id, g.season AS season, CASE WHEN r.team_id=g.home_id THEN g.home ELSE g.away END AS team
                  FROM raw_nhl_rosters r JOIN raw_nhl_games g ON g.game_id=r.game_id WHERE g.season IN (20252026,20262027)""")
    gone = set(ro[(ro.season == PREV) & (ro.team == "BUF")].player_id) - set(ro[(ro.season == CUR) & (ro.team == "BUF")].player_id)
    stay = set(ro[(ro.season == PREV) & (ro.team == "BUF")].player_id) & set(ro[(ro.season == CUR) & (ro.team == "BUF")].player_id)
    gone_fin = ind[ind.index.isin(gone)]
    ret_prev = ind[ind.index.isin(stay)]
    cur_all = u[u.season == CUR]
    ret_cur = cur_all[cur_all.shooter_id.isin(stay)]
    ret_cur_fin = ret_cur.goal.sum() - ret_cur.xg.sum()
    lg_pg = {se: (s[(s.season == se) & (s.unblocked == 1) & (s.empty_net_against == 0)].xg.sum()
                  / (gp[gp.season == se].gp.sum())) for se in LBL}

    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    xs_ = np.arange(len(LBL)); w = 0.36
    ax.bar(xs_ - w / 2, [pg[se][1] for se in LBL], w, color=GRAY, label="Expected goals per game", zorder=2)
    ax.bar(xs_ + w / 2, [pg[se][0] for se in LBL], w, color=[RED if se == CUR else BLUE for se in LBL], label="Goals per game", zorder=2)
    for i, se in enumerate(LBL):
        ax.text(i - w / 2, pg[se][1], f"{pg[se][1]:.2f}", ha="center", va="bottom", fontsize=9, color=INK)
        ax.text(i + w / 2, pg[se][0], f"{pg[se][0]:.2f}", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xticks(xs_, list(LBL.values())); ax.legend(frameon=False, loc="upper left", fontsize=9)
    ax.set_ylim(0, max(max(v_) for v_ in pg.values()) * 1.25); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "At least as many chances as last year. Fewer go in.",
           "Sabres expected goals vs. actual goals per game, all situations, empty-net goals excluded.",
           "2026-27 small sample.")
    fig.savefig(OUT / "sabres-finishing.png"); plt.close(fig)
    top = ind.sort_values("fin", ascending=False).head(5)
    t_rows = "\n".join(f"| {r_['name']} | {int(r_.G)} | {r_.ixG:.1f} | {r_.fin:+.1f} | {'Yes' if i in gone else ''} |" for i, r_ in top.iterrows())
    cur_ind = u[u.season == CUR].groupby("shooter_id").agg(G=("goal", "sum"), ixG=("xg", "sum"))
    cur_ind["fin"] = cur_ind.G - cur_ind.ixG; cur_ind["name"] = cur_ind.index.map(names)
    c_rows = "\n".join(f"| {r_['name']} | {int(r_.G)} | {r_.ixG:.1f} | {r_.fin:+.1f} |" for _, r_ in cur_ind.sort_values("G", ascending=False).head(5).iterrows())
    stories["sabres-same-chances-fewer-goals"] = (
        "As many chances, fewer goals: too early to call it a slump",
        "Buffalo is creating as much as last year. The finishing hasn't matched last season's, and it isn't about who left.",
        f"""# As many chances, fewer goals: too early to call it a slump

**Finding: The Sabres are generating {pg[CUR][1]:.2f} expected goals per game, at least as many as last season's {pg[PREV][1]:.2f},
but scoring {pg[CUR][0]:.2f} a game, down from {pg[PREV][0]:.2f}. Last season's finishing surplus came from players who are
still here: they scored {ret_prev.fin.sum():+.1f} goals above expected then and are {ret_cur_fin:+.1f} this season. That
dip is within normal game-to-game variation.**

*{sample} League average: {lg_pg[CUR]:.2f} expected goals per team per game this season.*

![Finishing](sabres-finishing.png)

## It isn't Alex Tuch

Tuch was last season's best finisher relative to his chances ({int(tuch.G)} goals on {tuch.ixG:.1f} expected, {tuch.fin:+.1f}),
and he now plays for Washington. But the {len(gone_fin)} skaters not on a Buffalo roster this season who shot for Buffalo last season combined for
{int(gone_fin.G.sum())} goals on {gone_fin.ixG.sum():.1f} expected ({gone_fin.fin.sum():+.1f}). Tuch's surplus was largely cancelled out by others who left.

2025-26 leaders, all situations, empty nets excluded:

| Player | Goals | Expected | Above expected | Gone? |
|---|---|---|---|---|
{t_rows}

## This season's leading scorers

| Player | Goals | Expected | Above expected |
|---|---|---|---|
{c_rows}

The top of the lineup is still finishing (Tage Thompson and Jack Quinn are above expected), so the shortfall is
spread through the rest of the roster.

## How much of this is noise?

Returning players have taken {len(ret_cur)} unblocked shots worth {ret_cur.xg.sum():.1f} expected goals this season. Random
variation alone on that many shots is about {np.sqrt((ret_cur.xg * (1 - ret_cur.xg)).sum()):.1f} goals either way, so
{ret_cur_fin:+.1f} is well within normal. It's the right thing to watch, not yet a slump.

## Why it matters going forward

Finishing above or below expected moves a lot from year to year (team shooting % has a year-to-year correlation
of about 0.3). The chances are still there. If finishing returns to normal, goals would likely follow, though
probably not to last season's level, which was itself above normal.

## Method and caveats

- {model_note}
- Individual expected goals count a player's own unblocked shots. "Not on a Buffalo roster" = dressed for Buffalo in 2025-26 and
  not yet in 2026-27, from game rosters; some may be injured or in the minors rather than gone. Per-game rates use all {int(cur.gp)} games.
""")

    # ---------- 4. Penalty kill
    pp_codes, pk_codes = ["5v4", "5v3", "4v3"], ["4v5", "3v5", "3v4"]
    ne = s[s.empty_net_against == 0]
    pk = ne[ne.strength.isin(pp_codes)].groupby(["season", "opp"]).agg(GA=("goal", "sum"), xGA=("xg", "sum")).rename_axis(["season", "team"])
    pk = pk.join(gp.set_index(["season", "team"]).gp)
    pk["GA_pg"] = pk.GA / pk.gp; pk["xGA_pg"] = pk.xGA / pk.gp
    pk["GA_rk"] = pk.groupby("season").GA_pg.rank(method="min").astype(int)
    pk["xGA_rk"] = pk.groupby("season").xGA_pg.rank(method="min").astype(int)
    pb = pk.xs("BUF", level="team")
    n_pk = int(ne[(ne.season == CUR) & (ne.opp == "BUF") & ne.strength.isin(pp_codes) & (ne.unblocked == 1)].shape[0])
    lg_pk = pk.groupby("season").xGA_pg.mean()
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    bars(ax, list(LBL.values()), [pb.loc[se, "xGA_pg"] for se in LBL], "{:.2f}", lg=[lg_pk[se] for se in LBL])
    ax.set_ylabel("Expected goals allowed per game, shorthanded")
    ax.set_ylim(0, max(pb.xGA_pg.max(), lg_pk.max()) * 1.25)
    finish(fig, "The penalty kill is where this season is leaking",
           "Sabres expected goals allowed per game while shorthanded. Dashed = league average.",
           f"Shorthanded = 4v5, 3v5, 3v4. 2026-27: {n_pk} unblocked shots against.")
    fig.savefig(OUT / "sabres-pk.png"); plt.close(fig)
    pk_rows = "\n".join(f"| {LBL[se]} | {int(pb.loc[se, 'GA'])} | {pb.loc[se, 'xGA']:.1f} | {pb.loc[se, 'GA_pg']:.2f} ({ordn(pb.loc[se, 'GA_rk'])}) | {pb.loc[se, 'xGA_pg']:.2f} ({ordn(pb.loc[se, 'xGA_rk'])}) | {lg_pk[se]:.2f} |" for se in LBL)
    stories["sabres-penalty-kill"] = (
        "The Sabres' penalty kill is where this season is leaking",
        "Last year's 4th-best penalty kill is allowing more, and better, chances.",
        f"""# The Sabres' penalty kill is where this season is leaking

**Finding: Shorthanded, the Sabres are allowing {pb.loc[CUR, 'xGA_pg']:.2f} expected goals per game ({ordn(pb.loc[CUR, 'xGA_rk'])} of 32,
where 1st is best), up from {pb.loc[PREV, 'xGA_pg']:.2f} ({ordn(pb.loc[PREV, 'xGA_rk'])}) last season. They've allowed {int(pb.loc[CUR, 'GA'])} power-play
goals in {int(cur.gp)} games, {ordn(pb.loc[CUR, 'GA_rk'])} in the league. Last season's kill ranked {ordn(pb.loc[PREV, 'GA_rk'])} in goals allowed.**

*{sample}*

![Penalty kill](sabres-pk.png)

| Season | PP goals allowed | Expected | Goals allowed/game (rank) | Expected/game (rank) | League expected/game |
|---|---|---|---|---|---|
{pk_rows}

Ranks: 1 = fewest allowed. The league as a whole is allowing more shorthanded chances this season
({lg_pk[CUR]:.2f} per game, up from {lg_pk[PREV]:.2f}), so not all of the rise is Buffalo's, but the Sabres are
{pb.loc[CUR, 'xGA_pg'] - lg_pk[CUR]:+.2f} per game worse than average. It isn't unprecedented, either: in 2024-25 the kill ranked
{ordn(pb.loc[20242025, 'GA_rk'])} in goals allowed. Part of this season's damage is bad luck ({int(pb.loc[CUR, 'GA'])} goals on {pb.loc[CUR, 'xGA']:.1f} expected),
and part is more chances allowed. Both are early-season numbers ({n_pk} unblocked shots against while
shorthanded); the chances allowed are the part to watch.

## Method and caveats

- {model_note}
- Shorthanded situations are 4-on-5, 3-on-5 and 3-on-4 (excludes the rare 4-on-6 and 3-on-6 with the goalie pulled). Per-game rates do not adjust for how often the team is
  shorthanded; time-on-ice data is not in our dataset yet.
""")

    # ---------- 5. Even strength
    t5r = t5.copy()
    for c_ in ["CF%", "xGF%"]:
        t5r[c_ + "_rk"] = t5r.groupby("season")[c_].rank(ascending=False, method="min").astype(int)
    e5 = t5r[t5r.team == "BUF"].set_index("season")
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.8), dpi=200)
    for ax, col, title in [(axes[0], "CF%", "Share of shot attempts"), (axes[1], "xGF%", "Share of expected goals")]:
        vals = [e5.loc[se, col] for se in LBL]
        ax.bar(list(LBL.values()), vals, color=[RED if se == CUR else BLUE for se in LBL], width=0.6, zorder=2)
        for i, (vv, se) in enumerate(zip(vals, LBL)):
            ax.text(i, max(vv, 0.5) + 0.002, f"{vv:.1%}\n{ordn(e5.loc[se, col + '_rk'])}", ha="center", va="bottom", fontsize=8.6, color=INK)
        ax.axhline(0.5, color=INK, lw=1, ls="--")
        ax.set_ylim(0.44, 0.56); ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
        ax.tick_params(axis="x", labelsize=8.5)
    finish(fig, "At 5-on-5, this is the same team, maybe a bit better",
           "Sabres 5-on-5 share of shot attempts and expected goals. Dashed line = even. Rank among 32 teams.",
           f"2026-27: {int(e5.loc[CUR, 'CF'] + e5.loc[CUR, 'CA']):,} 5-on-5 shot attempts.")
    fig.savefig(OUT / "sabres-5v5.png"); plt.close(fig)
    e_rows = "\n".join(f"| {LBL[se]} | {e5.loc[se, 'CF%']:.1%} ({ordn(e5.loc[se, 'CF%_rk'])}) | {e5.loc[se, 'xGF%']:.1%} ({ordn(e5.loc[se, 'xGF%_rk'])}) | {int(e5.loc[se, 'GF'])}-{int(e5.loc[se, 'GA'])} | {e5.loc[se, 'PDO']:.3f} |" for se in LBL)
    stories["sabres-even-strength"] = (
        "At even strength, these Sabres look like last year's Sabres",
        "Five-on-five, Buffalo is controlling as much of the play as last season. The difference is elsewhere.",
        f"""# At even strength, these Sabres look like last year's Sabres

**Finding: At 5-on-5 the Sabres are taking {e5.loc[CUR, 'CF%']:.1%} of shot attempts ({ordn(e5.loc[CUR, 'CF%_rk'])} in the NHL) and
{e5.loc[CUR, 'xGF%']:.1%} of expected goals, compared with {e5.loc[PREV, 'CF%']:.1%} and {e5.loc[PREV, 'xGF%']:.1%} last season. Last year's edge was the bounces (5-on-5 PDO
{e5.loc[PREV, 'PDO']:.3f}). This year the bounces have evened out and the penalty kill is leaking.**

*{sample}*

![5v5](sabres-5v5.png)

| Season | Shot-attempt share (rank) | Expected-goal share (rank) | 5v5 goals for-against | PDO |
|---|---|---|---|---|
{e_rows}

## How the pieces fit

The 5-on-5 team hasn't changed much, but it's no longer getting last year's bounces (5-on-5 PDO {e5.loc[PREV, 'PDO']:.3f}
then, {e5.loc[CUR, 'PDO']:.3f} now). The goalies have gone from well above expected to about average. The returning
shooters are slightly below expected, within normal variation. And the penalty kill is allowing more; it's the largest
single change. That's how a 109-point team turns into a {int(cur.pts)}-point start in {int(cur.gp)} games.

## Method and caveats

- {model_note}
- 5-on-5 only, empty nets excluded from goals and expected goals. Shot-attempt share counts blocked shots.
""")

    for slug, (title, dek, md) in stories.items():
        (OUT / f"{slug}.md").write_text(md)
    print("\n\n".join(md for _, _, md in stories.values()))
    return stories


if __name__ == "__main__":
    main()
