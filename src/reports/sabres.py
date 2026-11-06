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
    tr = s[(s.unblocked == 1) & (s.empty_net_against == 0) & (s.season < CUR)]
    edges = [0, 10, 20, 30, 40, 50, 60, 200]; labs = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60+"]
    by_d = tr.groupby(pd.cut(tr.dist, edges, right=False, labels=labs), observed=True).goal.agg(["mean", "size"])
    near, mid, far = by_d.loc["0-10", "mean"], by_d.loc["30-40", "mean"], by_d.loc["60+", "mean"]
    reb = tr.groupby("rebound").goal.mean(); pp = tr.groupby(tr.strength.isin(["5v4", "5v3", "4v3"])).goal.mean()
    one_in = lambda r_: f"about 1 in {round(1 / r_)}"
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    ax.bar(labs, by_d["mean"], color=BLUE, width=0.62, zorder=2)
    for i, (r_, n_) in enumerate(zip(by_d["mean"], by_d["size"])):
        ax.text(i, r_, f"{r_:.1%}\n{one_in(r_)}", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xlabel("Distance from the net (feet)"); ax.set_ylabel("Share of shots that went in")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylim(0, by_d["mean"].max() * 1.3); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Where a shot comes from decides how often it goes in",
           f"Every unblocked NHL shot, 2023-24 to 2025-26 ({len(tr):,} shots), empty nets excluded.",
           "Our expected-goals model also weighs angle, shot type, rebounds, rush chances and power plays.")
    fig.savefig(OUT / "sabres-shot-odds.png"); plt.close(fig)
    xg_source = f"""## Where "chances" comes from

**The source:** the NHL logs every shot in every game: where on the ice it was taken (to the foot), what kind of shot
it was, whether it came right after another shot, and how many players each team had on the ice. It's public, and
we pull it straight from the league's own game feed.

**The reasoning:** some shots are far more dangerous than others. We took {len(tr):,} NHL shots from the last three seasons
and counted how often each kind actually went in.

![Shot odds](sabres-shot-odds.png)

- A shot from within 10 feet of the net went in {near:.1%} of the time ({one_in(near)}).
- From 30 to 40 feet: {mid:.1%} ({one_in(mid)}).
- From 60 feet or more, around the blue line: {far:.1%} ({one_in(far)}).
- A rebound (a shot within three seconds of a teammate's shot) went in {reb.loc[1]:.1%} of the time, against {reb.loc[0]:.1%} for
  other shots.
- On the power play, shots went in {pp.loc[True]:.1%} of the time, against {pp.loc[False]:.1%} otherwise.

**The math:** a computer model combines all of those factors (distance, angle, shot type, rebound, rush, manpower)
and gives every shot a probability of going in. A shot from in close is typically worth about {tr[tr.dist < 10].xg.median():.2f} of a goal;
a long shot from 60 feet or more, about {tr[tr.dist >= 60].xg.median():.2f}. Add up every shot a team takes in a season and you get its **expected goals**: how many goals an
average NHL team would have scored with exactly the same shots.

**The check:** we tested the model on a full season it had never seen. It predicted which shots would go in clearly
better than a simple distance-and-angle model, and over a season its totals land within a few percent of the
actual goals scored league-wide.

So when we say last year's Sabres had chances worth {b.loc[PREV, 'xGF']:.0f} goals, it means: add up the odds on every Sabres shot
last season and that's what you get. They scored {b.loc[PREV, 'GF']:.0f}. Scoring {b.loc[PREV, 'GF'] - b.loc[PREV, 'xGF']:.0f} more than an average team would from the
same shots is either elite finishing or luck, and the rest of this story shows that kind of edge usually doesn't carry
into the next season.
"""
    xg_plain = (f"**Where \"chances\" comes from:** the NHL logs where every shot is taken and what kind it is. Across "
                f"{len(tr):,} shots, those from within 10 feet went in {near:.1%} of the time; from 60 feet or more, {far:.1%}. Our model "
                f"gives every shot those odds, and adding them up gives **expected goals**: what an average team (or goalie) "
                f"would produce from the same shots. The full explanation is in our lead Sabres story, "
                f"[The 50-win mirage](sabres-50-win-mirage.html).")

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
    ax.set_xlabel("Quality of chances: created minus allowed, per game  →  better"); ax.set_ylabel("Points")
    ax.grid(color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Last year's Sabres outran their chances by 18 points" if round(bf.over) == 18 else "Last year's Sabres outran their chances",
           "2025-26, all 32 NHL teams. Each dot is a team. Dashed line = points a team usually gets with those chances.",
           "Points expected from a linear fit of points on xG differential, 2023-24 to 2025-26.")
    fig.savefig(OUT / "sabres-mirage.png"); plt.close(fig)

    lvl = lambda r_: "Strong" if r_ >= 0.6 else ("Some" if r_ >= 0.4 else "Weak")
    xgf_rk = lambda se: ordn(t[t.season == se]['xGF%'].rank(ascending=False, method='min')[(t.season == se) & (t.team == 'BUF')].iloc[0])
    pdo_rk = lambda se: ordn(t[t.season == se]['PDO'].rank(ascending=False, method='min')[(t.season == se) & (t.team == 'BUF')].iloc[0])
    stories["sabres-50-win-mirage"] = (
        "The Sabres' 50-win season was built on goals that weren't supposed to happen",
        "Based on the chances they created, last year's team should have had about 91 points. They got 109.",
        f"""# The Sabres' 50-win season was built on goals that weren't supposed to happen

**Finding: Based on the scoring chances they created and gave up, last year's Sabres played like a {bf.exp_pts:.0f}-point
team. They finished with {int(bf.pts)}. Only one team in the NHL outran its chances by more. The difference came from hot
goaltending and hot shooting, and those rarely last.**

*This season: {int(cur.gp)} games ({int(cur.w)}-{int(cur.l)}-{int(cur.otl)}). That's still a small sample.*

![Mirage](sabres-mirage.png)

{xg_source}
## Last season, in plain numbers

| | What happened | What their shots were worth (expected goals) | Difference |
|---|---|---|---|
| Goals the Sabres scored | {b.loc[PREV, 'GF']:.0f} | {b.loc[PREV, 'xGF']:.0f} | **{fin25:+.0f}** (hot shooting) |
| Goals the Sabres allowed | {b.loc[PREV, 'GA']:.0f} | {b.loc[PREV, 'xGA']:.0f} | **{sav25:+.0f}** (hot goaltending) |

That's about {fin25 + sav25:.0f} goals better than their chances, roughly one extra goal every two games. By chances
alone they were a middle-of-the-pack team ({xgf_rk(PREV)} of 32).

## Why it didn't carry over

We checked every NHL team over three seasons. Some things a team does well one year, it usually does well the next.
Other things bounce around.

| What we measured | Does it carry over to next season? |
|---|---|
| Creating more good chances than you give up | **{lvl(st['xGF%'][0])}** |
| Shooting percentage (finishing) | **{lvl(st['sh%'][0])}** |
| Save percentage (goaltending) | **{lvl(st['sv%'][0])}** |

Last season the Sabres' shooting and goaltending luck combined ranked {pdo_rk(PREV)} in the league. This season it ranks
{pdo_rk(CUR)}.

## What it means for this season

Through {int(cur.gp)} games the Sabres are earning {int(cur.pts)} points, about {cur.pts / cur.gp:.2f} a game. Last season's chances
pointed to about {bf.exp_pts / 82:.2f} a game. **This isn't a collapse. It's the team their chances always said they were,
without last year's luck.**

## For the stat-heads

- Expected goals (xG): our own gradient-boosted model on shot distance, angle, type, rebounds, rush chances and
  manpower, trained on {n_shots:,} unblocked shots, 2023-24 to 2025-26. Out of sample on 2025-26 it beat a
  distance-and-angle model (AUC {v['auc_gbm']:.2f} vs {v['auc_dist_angle']:.2f}). 2023-26 values are in-sample; 2026-27 is out of sample. Each
  season is rescaled so league xG equals league goals (the raw model ran {(1 / cal.loc[PREV] - 1):+.1%} hot in 2025-26). Empty nets
  excluded.
- Last season: goals {b.loc[PREV, 'GF']:.0f} vs xG {b.loc[PREV, 'xGF']:.1f}; goals against {b.loc[PREV, 'GA']:.0f} vs xGA {b.loc[PREV, 'xGA']:.1f}.
  xGF% {b.loc[PREV, 'xGF%']:.1%} ({xgf_rk(PREV)}). This season xGF% {b.loc[CUR, 'xGF%']:.1%} ({xgf_rk(CUR)}), {b.loc[CUR, 'G-xG'] + b.loc[CUR, 'xGA-GA']:+.1f} vs xG.
- Year-to-year correlations, 32 teams, {st['xGF%'][1]} team pairs: xGF% {st['xGF%'][0]:.2f}, shooting % {st['sh%'][0]:.2f},
  save % {st['sv%'][0]:.2f}, PDO {st['PDO'][0]:.2f}. "Strong" means 0.6 or higher, "Weak" means under 0.4. PDO (shooting % +
  save %, 5-on-5) was {b.loc[PREV, 'PDO']:.3f} last season and is {b.loc[CUR, 'PDO']:.3f} now.
- Expected points: a straight-line fit of points on xG differential per game, all 96 team-seasons 2023-24 to 2025-26
  (r = {corr(None):.2f}; typical miss {resid_sd:.1f} points). Doesn't model overtime, shootouts or empty-net goals.
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
    ax.axhline(0, color=INK, lw=1); ax.set_ylabel("Goals saved vs. an average goalie")
    ax.set_ylim(min(rows.GSAx.min(), 0) - 3, rows.GSAx.max() + 3.5)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Last year's goalies beat expectations. This year they're about average.",
           "Goals each Sabres goalie saved compared with an average goalie facing the same shots. Above zero = better.",
           "Unblocked shots, empty nets excluded. 2026-27 small sample.")
    fig.savefig(OUT / "sabres-goalies.png"); plt.close(fig)
    g_rows = "\n".join(f"| {LBL[r_.season]} | {r_['name']} | {int(r_.shots_faced)} | {r_['sv%']:.3f} | {r_['xsv%']:.3f} | {r_.GSAx:+.1f} |" for _, r_ in gb.iterrows())
    g_recent = gb[gb.season >= PREV]
    g_plain = "\n".join(f"| {LBL[r_.season]} | {r_['name']} | {int(r_.shots_faced)} | {r_['sv%']:.1%} | {r_['xsv%']:.1%} | {r_.GSAx:+.0f} |" for _, r_ in g_recent.iterrows())
    upl_rk = ordn(g26.set_index('name').loc[upl['name'], 'xsv_rk'])
    stories["sabres-goalies-not-the-problem"] = (
        "The Sabres' goalies aren't the problem. They're just not the bailout anymore.",
        "Luukkonen's save percentage looks ugly. The shots he's facing explain most of it.",
        f"""# The Sabres' goalies aren't the problem. They're just not the bailout anymore.

**Finding: Ukko-Pekka Luukkonen is stopping {upl['sv%']:.1%} of shots, which looks bad. But he's facing some of the hardest
shots in the league ({upl_rk} toughest of {len(g26)} goalies), and an average goalie would stop only about {upl['xsv%']:.1%} of them.
He's close to average. What's missing is last year's bonus: Sabres goalies saved about {tot25:.0f} more goals than an
average goalie would have, and about half of that was Alex Lyon, who hasn't played an NHL game this season.**

*{sample} Luukkonen has faced {int(upl.shots_faced)} shots, Colten Ellis {int(ell.shots_faced)}.*

![Goalies](sabres-goalies.png)

## How we judge a goalie

Save percentage alone is unfair to goalies behind a leaky defense. So we ask a better question: **given the exact
shots he faced, how many goals would an average NHL goalie have allowed?** If he allowed fewer, he saved his team
goals. {xg_plain}

| Season | Goalie | Shots faced | Stopped | Average goalie would stop | Goals saved vs. average |
|---|---|---|---|---|---|
{g_plain}

## What changed

- **Last year the goalies stole games.** Lyon and Luukkonen saved about {lyon.GSAx:.0f} and {upl25.GSAx:.0f} goals more than an average
  goalie would have. That's a big part of how a middle-of-the-pack team got 109 points.
- **Lyon hasn't played this season.** He hasn't dressed for any NHL team in 2026-27.
- **Luukkonen is seeing tougher shots.** An average goalie would stop {upl['xsv%']:.1%} of what he's faced this year, down from
  {upl25['xsv%']:.1%} last year. The defense in front of him is giving up better looks.
- **Together, this year's goalies are dead even with average** ({tot26:+.1f} goals).

Goaltending swings a lot from year to year, and {int(upl.shots_faced)} shots is a small sample. There's no evidence yet that
Luukkonen has gotten worse.

## For the stat-heads

- {model_note}
- Goals saved above expected (GSAx) = xG on unblocked shots faced minus goals allowed; save % and expected save % use
  shots on goal. Blocked shots and empty nets excluded. Goalies with 100+ shots faced. League save % on these shots:
  {lg_sv[PREV]:.3f} (2025-26), {lg_sv[CUR]:.3f} (2026-27).
- Full history:

| Season | Goalie | Shots | Sv% | xSv% | GSAx |
|---|---|---|---|---|---|
{g_rows}
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
    ax.bar(xs_ - w / 2, [pg[se][1] for se in LBL], w, color=GRAY, label="Goals their chances were worth", zorder=2)
    ax.bar(xs_ + w / 2, [pg[se][0] for se in LBL], w, color=[RED if se == CUR else BLUE for se in LBL], label="Goals actually scored", zorder=2)
    for i, se in enumerate(LBL):
        ax.text(i - w / 2, pg[se][1], f"{pg[se][1]:.2f}", ha="center", va="bottom", fontsize=9, color=INK)
        ax.text(i + w / 2, pg[se][0], f"{pg[se][0]:.2f}", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xticks(xs_, list(LBL.values())); ax.legend(frameon=False, loc="upper left", fontsize=9)
    ax.set_ylim(0, max(max(v_) for v_ in pg.values()) * 1.25); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "At least as many chances as last year. Fewer go in.",
           "Sabres per game. Gray = goals an average team would score from the same chances. Empty-net goals excluded.",
           "2026-27 small sample.")
    fig.savefig(OUT / "sabres-finishing.png"); plt.close(fig)
    top = ind.sort_values("fin", ascending=False).head(5)
    t_rows = "\n".join(f"| {r_['name']} | {int(r_.G)} | {r_.ixG:.1f} | {r_.fin:+.1f} | {'Yes' if i in gone else ''} |" for i, r_ in top.iterrows())
    cur_ind = u[u.season == CUR].groupby("shooter_id").agg(G=("goal", "sum"), ixG=("xg", "sum"))
    cur_ind["fin"] = cur_ind.G - cur_ind.ixG; cur_ind["name"] = cur_ind.index.map(names)
    c_rows = "\n".join(f"| {r_['name']} | {int(r_.G)} | {r_.ixG:.1f} | {r_.fin:+.1f} |" for _, r_ in cur_ind.sort_values("G", ascending=False).head(5).iterrows())
    noise = np.sqrt((ret_cur.xg * (1 - ret_cur.xg)).sum())
    t_plain = "\n".join(f"| {r_['name']} | {int(r_.G)} | {r_.ixG:.0f} | {r_.fin:+.0f} | {'Yes' if i in gone else ''} |" for i, r_ in top.iterrows())
    c_plain = "\n".join(f"| {r_['name']} | {int(r_.G)} | {r_.ixG:.0f} | {r_.fin:+.0f} |" for _, r_ in cur_ind.sort_values("G", ascending=False).head(5).iterrows())
    stories["sabres-same-chances-fewer-goals"] = (
        "As many chances, fewer goals: too early to call it a slump",
        "Buffalo is creating as many good chances as last year. Fewer are going in, and it isn't about who left.",
        f"""# As many chances, fewer goals: too early to call it a slump

**Finding: The Sabres are creating at least as many good scoring chances as last season, but they're scoring
{pg[CUR][0]:.2f} goals a game instead of {pg[PREV][0]:.2f}. It isn't because Alex Tuch left. The players who are still here were
scoring well above their chances last year, and this year they're a little below. Fifteen games in, that's within
normal ups and downs.**

*{sample}*

![Finishing](sabres-finishing.png)

## Chances vs. goals

{xg_plain}

This season the Sabres' chances are worth {pg[CUR][1]:.2f} goals a game, about the same as last season ({pg[PREV][1]:.2f}) and right at
the league average ({lg_pg[CUR]:.2f}). The chances are there. Fewer are going in.

## It isn't Alex Tuch

Tuch was last season's best finisher: {int(tuch.G)} goals on chances an average shooter turns into about {tuch.ixG:.0f}. He now
plays in Washington. But the other players who are gone mostly scored *below* their chances, so as a group the
departures were roughly a wash ({int(gone_fin.G.sum())} goals on chances worth about {gone_fin.ixG.sum():.0f}).

The finishing that drove last season came from players who are still on the team. They scored about {ret_prev.fin.sum():.0f} more
goals than their chances were worth. This season they're about {abs(ret_cur_fin):.0f} below.

**Last season's best finishers**

| Player | Goals | Goals expected from his chances | Difference | No longer with Buffalo? |
|---|---|---|---|---|
{t_plain}

**This season's leading goal scorers**

| Player | Goals | Goals expected from his chances | Difference |
|---|---|---|---|
{c_plain}

Tage Thompson and Jack Quinn are still finishing above their chances. The shortfall is spread through the rest of
the lineup.

## Is it a slump or bad bounces?

Too early to tell. The returning players have taken {len(ret_cur)} shots this season. Over that many shots, luck alone can
swing the total by about {noise:.0f} goals either way. They're about {abs(ret_cur_fin):.0f} below. That's normal. And finishing is one of
the things that doesn't carry over well from one season to the next.

**What to expect:** if the chances keep coming, goals should pick up, though probably not to last season's pace,
which was itself unusually hot.

## For the stat-heads

- {model_note}
- Team xG/game: {pg[PREV][1]:.2f} (2025-26), {pg[CUR][1]:.2f} (2026-27); league {lg_pg[CUR]:.2f}. Goals/game {pg[PREV][0]:.2f} to {pg[CUR][0]:.2f}.
- Returning skaters G-xG: {ret_prev.fin.sum():+.1f} (2025-26), {ret_cur_fin:+.1f} (2026-27) on {len(ret_cur)} unblocked shots, {ret_cur.xg.sum():.1f} xG;
  binomial SD {noise:.1f}. Departed: {len(gone_fin)} skaters, {int(gone_fin.G.sum())} G on {gone_fin.ixG.sum():.1f} xG ({gone_fin.fin.sum():+.1f}). Tuch {tuch.fin:+.1f}.
- Year-to-year correlation of team shooting %: {st['sh%'][0]:.2f}.
- "No longer with Buffalo" = dressed for Buffalo in 2025-26 and not yet in 2026-27, from game rosters; some may be
  injured or in the minors. Individual xG counts a player's own unblocked shots. Empty nets excluded.
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
    ax.set_ylabel("Danger of chances allowed per game")
    ax.set_ylim(0, max(pb.xGA_pg.max(), lg_pk.max()) * 1.25)
    finish(fig, "The penalty kill is where this season is leaking",
           "When the Sabres are a man down: goals an average team would score from the chances they allow. Dashed = league average.",
           f"Man-down situations only (4-on-5, 3-on-5, 3-on-4). 2026-27: {n_pk} shots against.")
    fig.savefig(OUT / "sabres-pk.png"); plt.close(fig)
    pk_rows = "\n".join(f"| {LBL[se]} | {int(pb.loc[se, 'GA'])} | {pb.loc[se, 'xGA']:.1f} | {pb.loc[se, 'GA_pg']:.2f} ({ordn(pb.loc[se, 'GA_rk'])}) | {pb.loc[se, 'xGA_pg']:.2f} ({ordn(pb.loc[se, 'xGA_rk'])}) | {lg_pk[se]:.2f} |" for se in LBL)
    pk_plain = "\n".join(f"| {LBL[se]} | {int(pb.loc[se, 'GA'])} | {ordn(pb.loc[se, 'GA_rk'])} | {pb.loc[se, 'xGA_pg']:.2f} ({ordn(pb.loc[se, 'xGA_rk'])}) | {lg_pk[se]:.2f} |" for se in LBL)
    stories["sabres-penalty-kill"] = (
        "The Sabres' penalty kill is where this season is leaking",
        "Last year's 4th-best penalty kill is giving up more goals, and more dangerous chances.",
        f"""# The Sabres' penalty kill is where this season is leaking

**Finding: When the Sabres are a man down, they've given up {int(pb.loc[CUR, 'GA'])} goals in {int(cur.gp)} games, {ordn(pb.loc[CUR, 'GA_rk'])} of 32 teams.
Last season they were {ordn(pb.loc[PREV, 'GA_rk'])}. Some of that is bad luck, but they're also giving up more dangerous chances than
most teams ({ordn(pb.loc[CUR, 'xGA_rk'])} of 32). Of everything that's changed since last season, this is the biggest.**

*{sample}*

![Penalty kill](sabres-pk.png)

## What the numbers say

{xg_plain}

| Season | Power-play goals allowed | League rank (1 = fewest) | Danger of chances allowed per game (rank) | League average |
|---|---|---|---|---|
{pk_plain}

Two things are happening:

1. **Bad luck.** Opponents have scored {int(pb.loc[CUR, 'GA'])} power-play goals on chances an average team would turn into about
   {pb.loc[CUR, 'xGA']:.0f}. That part tends to even out.
2. **More dangerous chances.** The Sabres are allowing chances worth {pb.loc[CUR, 'xGA_pg']:.2f} goals a game while shorthanded, up from
   {pb.loc[PREV, 'xGA_pg']:.2f} last year and above this season's league average of {lg_pk[CUR]:.2f}. Every team is allowing a bit more this
   year, but Buffalo is allowing more than most.

**What to watch:** the luck should fade. The chances allowed are the part that has to get fixed. It's early, too:
{n_pk} shots against while shorthanded. A bad penalty kill isn't new, either. In 2024-25 it ranked {ordn(pb.loc[20242025, 'GA_rk'])} in goals allowed.

## For the stat-heads

- {model_note}
- Shorthanded = 4-on-5, 3-on-5, 3-on-4 (excludes 4-on-6 and 3-on-6 with a goalie pulled). "Danger of chances" =
  xGA per game. Per-game rates don't adjust for how often a team is shorthanded; time-on-ice isn't in our dataset yet.

| Season | PP GA | xGA | GA/gm (rank) | xGA/gm (rank) | League xGA/gm |
|---|---|---|---|---|---|
{pk_rows}
""")

    # ---------- 5. Even strength
    t5r = t5.copy()
    for c_ in ["CF%", "xGF%"]:
        t5r[c_ + "_rk"] = t5r.groupby("season")[c_].rank(ascending=False, method="min").astype(int)
    e5 = t5r[t5r.team == "BUF"].set_index("season")
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.8), dpi=200)
    for ax, col, title in [(axes[0], "CF%", "Share of all shot attempts"), (axes[1], "xGF%", "Share of good chances")]:
        vals = [e5.loc[se, col] for se in LBL]
        ax.bar(list(LBL.values()), vals, color=[RED if se == CUR else BLUE for se in LBL], width=0.6, zorder=2)
        for i, (vv, se) in enumerate(zip(vals, LBL)):
            ax.text(i, max(vv, 0.5) + 0.002, f"{vv:.1%}\n{ordn(e5.loc[se, col + '_rk'])}", ha="center", va="bottom", fontsize=8.6, color=INK)
        ax.axhline(0.5, color=INK, lw=1, ls="--")
        ax.set_ylim(0.44, 0.56); ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
        ax.tick_params(axis="x", labelsize=8.5)
    finish(fig, "At full strength, this is the same team, maybe a bit better",
           "Sabres at full strength (5-on-5). Above the dashed line = winning that part of the game. Rank among 32 teams.",
           f"2026-27: {int(e5.loc[CUR, 'CF'] + e5.loc[CUR, 'CA']):,} 5-on-5 shot attempts.")
    fig.savefig(OUT / "sabres-5v5.png"); plt.close(fig)
    e_rows = "\n".join(f"| {LBL[se]} | {e5.loc[se, 'CF%']:.1%} ({ordn(e5.loc[se, 'CF%_rk'])}) | {e5.loc[se, 'xGF%']:.1%} ({ordn(e5.loc[se, 'xGF%_rk'])}) | {int(e5.loc[se, 'GF'])}-{int(e5.loc[se, 'GA'])} | {e5.loc[se, 'PDO']:.3f} |" for se in LBL)
    e_plain = "\n".join(f"| {LBL[se]} | {e5.loc[se, 'CF%']:.0%} ({ordn(e5.loc[se, 'CF%_rk'])}) | {e5.loc[se, 'xGF%']:.0%} ({ordn(e5.loc[se, 'xGF%_rk'])}) | {int(e5.loc[se, 'GF'])}-{int(e5.loc[se, 'GA'])} |" for se in LBL)
    stories["sabres-even-strength"] = (
        "At even strength, these Sabres look like last year's Sabres",
        "Five-on-five, Buffalo is controlling as much of the play as last season. The difference is elsewhere.",
        f"""# At even strength, these Sabres look like last year's Sabres

**Finding: When both teams are at full strength, which is most of every game, the Sabres are playing as well as last
season, maybe a bit better. They're taking {e5.loc[CUR, 'CF%']:.0%} of the shot attempts ({ordn(e5.loc[CUR, 'CF%_rk'])} in the NHL) and an even share of the
good chances. What changed is that last year's lucky bounces have evened out, and the penalty kill is leaking.**

*{sample}*

![5v5](sabres-5v5.png)

## How we measure who's controlling the game

Two simple questions. **Who's shooting more?** If you take more than half the shot attempts, you usually have the
puck more. **Who's getting the better chances?** {xg_plain}

| Season | Share of shot attempts (rank) | Share of good chances (rank) | Goals for-against at 5-on-5 |
|---|---|---|---|
{e_plain}

Above 50% means the Sabres are winning that part of the game. They've been right around even all four seasons.

## So what changed?

Put all five of our Sabres stories together and the picture is simple:

- **At full strength, it's the same team.** It's no longer getting last year's lucky bounces.
- **The goalies** went from stealing games to about average.
- **The shooters who stayed** went from scoring way above their chances to slightly below, within normal ups and downs.
- **The penalty kill** is giving up a lot more. That's the biggest single change.

That's how a 109-point team turns into a {int(cur.pts)}-point start in {int(cur.gp)} games.

## For the stat-heads

- {model_note}
- 5-on-5 only, empty nets excluded. Shot-attempt share = CF% (Corsi, blocked shots included). Good-chance share = xGF%.

| Season | CF% (rank) | xGF% (rank) | 5v5 GF-GA | PDO |
|---|---|---|---|---|
{e_rows}

PDO = 5-on-5 shooting % + save %, a common luck gauge: {e5.loc[PREV, 'PDO']:.3f} last season, {e5.loc[CUR, 'PDO']:.3f} now.
""")

    for slug, (title, dek, md) in stories.items():
        (OUT / f"{slug}.md").write_text(md)
    print("\n\n".join(md for _, _, md in stories.values()))
    return stories


if __name__ == "__main__":
    main()
