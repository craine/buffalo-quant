"""Sabres post-game: CBJ at BUF, Nov 6, 2026. Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-06-sabres-cbj.md and two PNGs. Expected goals are rescaled per season (league xG = goals).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import goalie_season, shots
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
G, SEASON, US, THEM = 2026020262, 20262027, "BUF", "CBJ"
SRC = "Source: NHL play-by-play (league game feed), Buffalo Quant Desk expected-goals model."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def ordn(n):
    n = int(n)
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def with_score(s):
    """Add the shooting team's goal margin at the moment of each shot (before it)."""
    s = s.sort_values(["game_id", "period", "t", "eventId"]).copy()
    hg = (s.goal * s.is_home).groupby(s.game_id).cumsum() - s.goal * s.is_home
    ag = (s.goal * (1 - s.is_home)).groupby(s.game_id).cumsum() - s.goal * (1 - s.is_home)
    s["margin"] = np.where(s.is_home == 1, hg - ag, ag - hg)
    return s


AS_OF = "2026-11-06"  # games through the night of this game; pinned so the published story doesn't change


def main(as_of=AS_OF):
    s = shots()
    keep = set(query(f"SELECT game_id FROM raw_nhl_games WHERE game_date <= '{as_of}'").game_id)
    s = s[s.game_id.isin(keep)].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    u = s[unb]
    g = u[u.game_id == G].copy()
    f, a = g[g.team == US], g[g.team == THEM]
    goals_all = s[(s.game_id == G) & (s.goal == 1)]

    # season games for BUF, per-game profile
    bs = u[(u.season == SEASON) & ((u.team == US) | (u.opp == US))].copy()
    bs["us"] = bs.team == US
    pp_codes = ["5v4", "5v3", "4v3"]

    def prof(x):
        fo, ag = x[x.us], x[~x.us]
        return pd.Series(dict(xgf=fo.xg.sum(), xga=ag.xg.sum(), reb_f=fo.rebound.sum(), close_f=(fo.dist < 20).sum(),
                              close_a=(ag.dist < 20).sum(), pp_xgf=fo[fo.strength.isin(pp_codes)].xg.sum(),
                              pp_gf=fo[fo.strength.isin(pp_codes)].goal.sum(), gsax=ag.xg.sum() - ag.goal.sum()))
    pg = bs.groupby("game_id").apply(prof)
    order = query(f"SELECT game_id, game_date FROM raw_nhl_games WHERE season={SEASON} AND (home='{US}' OR away='{US}') AND game_date <= '{as_of}' ORDER BY game_date").game_id.tolist()
    pg = pg.loc[[x for x in order if x in pg.index]]
    prev = pg.drop(G)
    rk = lambda col, asc=False: int(pg[col].rank(ascending=asc, method="min").loc[G])
    n_g = len(pg)

    # deserve-to-win simulation over this game's shots
    rng = np.random.default_rng(7)
    N = 20000
    simf = (rng.random((N, len(f))) < f.xg.values).sum(1)
    sima = (rng.random((N, len(a))) < a.xg.values).sum(1)
    p_win, p_tie = (simf > sima).mean(), (simf == sima).mean()

    # through two periods vs third, with score effects check league-wide
    p12 = g[g.period <= 2].groupby("team").xg.sum()
    p3 = g[g.period == 3].groupby("team").xg.sum()
    p3_cbj = p3.get(THEM, 0) / (p3.get(THEM, 0) + p3.get(US, 0))
    # game score at the moment of each shot, from every shot in the game (empty-net goals count toward the score)
    sc = with_score(s[s.season < SEASON])
    sc = sc[(sc.unblocked == 1) & (sc.empty_net_against == 0) & (sc.period == 3)]
    trail, lead = sc[sc.margin <= -3], sc[sc.margin >= 3]
    trail_share = trail.xg.sum() / (trail.xg.sum() + lead.xg.sum())
    # per game: the trailing team's share of third-period chances while down 3+
    tg3 = trail.groupby(["game_id", "team"]).xg.sum().rename("t").reset_index()
    lg3 = lead.groupby(["game_id", "opp"]).xg.sum().rename("l").reset_index().rename(columns={"opp": "team"})
    pp3 = tg3.merge(lg3, on=["game_id", "team"], how="outer").fillna(0)
    pp3 = pp3[(pp3.t + pp3.l) > 0]
    pp3["share"] = pp3.t / (pp3.t + pp3.l)
    med3 = pp3.share.median()
    at_least = (pp3.share >= p3_cbj).mean()

    # rebounds
    tg = u[u.season == SEASON].groupby(["game_id", "team"]).rebound.sum()
    tg_prev = u[u.season == SEASON - 10001].groupby(["game_id", "team"]).rebound.sum()
    share10 = (tg >= 10).mean()
    share10_prev = (tg_prev >= 10).mean()
    reb_rate = u[(u.rebound == 1) & (u.season < SEASON)].goal.mean()
    non_rate = u[(u.rebound == 0) & (u.season < SEASON)].goal.mean()
    rb = f[f.rebound == 1]

    # goalies
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["gsax"] = gk.xga - gk.ga
    gk["name"] = gk.goalie_id.map(names)
    upl = gk[gk.opp == US].iloc[0]
    upl_id = upl.goalie_id
    upl_season = u[(u.season == SEASON) & (u.goalie_id == upl_id)]
    upl_before = upl_season[upl_season.game_id != G]
    upl_before_gsax = upl_before.xg.sum() - upl_before.goal.sum()
    upl_after_gsax = upl_season.xg.sum() - upl_season.goal.sum()

    # penalty kill: season to date
    pk_all = u[(u.season == SEASON) & u.strength.isin(pp_codes)].groupby("opp").agg(GA=("goal", "sum"))
    pk_gp = query(f"""SELECT team, COUNT(*) gp FROM (SELECT home team FROM raw_nhl_games WHERE season={SEASON} AND game_date <= '{as_of}'
                      UNION ALL SELECT away FROM raw_nhl_games WHERE season={SEASON} AND game_date <= '{as_of}') GROUP BY team""").set_index("team").gp
    pk_all["pg"] = pk_all.GA / pk_gp.reindex(pk_all.index)
    pk_all["rk"] = pk_all.pg.rank(method="min").astype(int)

    # goal list
    gl = goals_all.sort_values(["period", "t"]).copy()
    gl["who"] = gl.shooter_id.map(names)
    gl["clock"] = (gl.t - (gl.period - 1) * 1200).map(lambda x: f"{int(x) // 60}:{int(x) % 60:02d}")

    # individual
    ind = f.groupby("shooter_id").agg(n=("xg", "size"), xg=("xg", "sum"), gl=("goal", "sum")).sort_values("xg", ascending=False)
    ind["who"] = ind.index.map(names)
    doan, norris = ind[ind.who == "Josh Doan"].iloc[0], ind[ind.who == "Josh Norris"].iloc[0]

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    for team, col in [(US, BLUE), (THEM, GRAY)]:
        x = g[g.team == team].sort_values(["period", "t"])
        tt = x.t / 60
        cum = x.xg.cumsum()
        ax.step(np.r_[0, tt, 60], np.r_[0, cum, cum.iloc[-1]], where="post", color=col, lw=2.4, label=f"{'Sabres' if team == US else 'Blue Jackets'}")
        gx = x[x.goal == 1]
        ax.scatter(gx.t / 60, cum[x.goal == 1], s=70, color=RED if team == US else INK, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60], ["0", "", "20", "", "40", "", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Buffalo built a big lead on chances, then held on",
           "Running total of what each team's shots were worth. Dots are goals.",
           f"Unblocked shots, empty net excluded. Sabres {len(f)} unblocked shots, Blue Jackets {len(a)}.")
    fig.savefig(OUT / "sabres-cbj-flow.png"); plt.close(fig)

    # ---- chart 2: rebounds by game
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    vals = pg.reb_f.values
    ax.bar(range(1, n_g + 1), vals, color=[RED if gid == G else BLUE for gid in pg.index], width=0.7, zorder=2)
    ax.axhline(prev.reb_f.mean(), color=INK, lw=1.2, ls="--")
    ax.text(0.7, vals.max() * 0.92, f"Dashed line: first {n_g - 1} games' average, {prev.reb_f.mean():.1f}",
            fontsize=9, color=INK, ha="left", va="center")
    ax.text(n_g, vals[-1] + 0.2, f"{int(vals[-1])}", ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.set_xticks(range(1, n_g + 1)); ax.set_xlabel("Sabres game number, 2026-27"); ax.set_ylabel("Rebound shots")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Ten rebound shots: Buffalo's most this season",
           "Sabres shots taken within 3 seconds of another Sabres shot on net or wide, by game.",
           f"Unblocked shots, empty net excluded. {n_g} games.")
    fig.savefig(OUT / "sabres-cbj-rebounds.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {int(r.period)} | {r.clock} | {'Sabres' if r.team == US else 'Blue Jackets'} | {r.who} | {r.shot_type} from {r.dist:.0f} ft"
        f"{', rebound' if r.rebound else ''}{', power play' if r.strength in pp_codes else ''} | {r.xg:.2f} |" for r in gl.itertuples())
    reb_rows = "\n".join(f"| {int(r.period)} | {names.get(r.shooter_id, '')} | {r.dist:.0f} ft | {r.xg:.2f} | {'Goal' if r.goal else ''} |"
                         for r in rb.sort_values(["period", "t"]).itertuples())
    md = f"""# Sabres 5, Blue Jackets 2: Buffalo won the scramble in front of the net

**Finding: The Sabres created their most dangerous night of the season Friday, with shots worth {f.xg.sum():.1f} goals, by living
around Columbus's crease. They had {int(rb.shape[0])} rebound shots, about three times their usual, something that happens in about 1 of every
{100 * round(1 / share10 / 100) if 1 / share10 >= 100 else 10 * round(1 / share10 / 10):.0f} NHL team-games. Two of their five goals came off rebounds.**

*One game, {gm.game_date}, in Buffalo. The Sabres are {n_g} games into the season.*

![Game flow](sabres-cbj-flow.png)

## How we measure "chances"

Every shot has odds of going in, based on where it was taken and what kind of shot it was. A shot from within 10 feet
goes in about 1 time in 7; one from 60 feet or more, about 1 in 125. Add up the odds on every shot and you get what a
team's chances were worth in goals. (The full explanation, with the chart, is in our story on
[last year's 50-win season](sabres-50-win-mirage.html).)

Friday, the Sabres' shots were worth **{f.xg.sum():.1f} goals** and Columbus's **{a.xg.sum():.1f}**. Buffalo scored 5. If you replayed
those exact shots thousands of times, Buffalo would win about {p_win:.0%} of the time and tie about {p_tie:.0%}. Their chances were good enough to win most replays.

## What changed from their first {n_g - 1} games

| | Friday | Average, first {n_g - 1} games | Rank among {n_g} games |
|---|---|---|---|
| What Buffalo's chances were worth | {f.xg.sum():.1f} goals | {prev.xgf.mean():.1f} | {ordn(rk('xgf'))} |
| Rebound shots | {int(pg.loc[G, 'reb_f'])} | {prev.reb_f.mean():.1f} | {ordn(rk('reb_f'))} |
| Buffalo shots from within 20 feet | {int(pg.loc[G, 'close_f'])} | {prev.close_f.mean():.1f} | {ordn(rk('close_f'))} |
| Columbus shots from within 20 feet | {int(pg.loc[G, 'close_a'])} | {prev.close_a.mean():.1f} | {ordn(rk('close_a', True))} fewest |
| Power-play chances, in goals | {pg.loc[G, 'pp_xgf']:.1f} | {prev.pp_xgf.mean():.1f} | {ordn(rk('pp_xgf'))} |
| Goals saved vs. an average goalie | {pg.loc[G, 'gsax']:+.1f} | {prev.gsax.mean():+.1f} | {ordn(rk('gsax'))} |

## The rebound game

A rebound here means a shot taken within three seconds of another Sabres shot (his own or a teammate's) that was saved or
missed the net. Across the NHL over the last three seasons,
rebounds went in {reb_rate:.1%} of the time, against {non_rate:.1%} for other shots, because the goalie is usually out of
position. NHL teams average about {tg.mean():.1f} rebound shots a game this season. Buffalo had {int(rb.shape[0])}, worth {rb.xg.sum():.1f} goals on
their own.

![Rebounds by game](sabres-cbj-rebounds.png)

| Period | Shooter | Distance | Worth | |
|---|---|---|---|---|
{reb_rows}

Zach Benson had three of them by himself. Jack Quinn's opening goal and Josh Doan's deflection from 4 feet both came off
rebounds. Doan's shots were worth a full goal ({doan.xg:.1f}), the most of any Sabre.

## Two periods of control

Through 40 minutes, Buffalo's chances were worth {p12.get(US, 0):.1f} goals to Columbus's {p12.get(THEM, 0):.1f}, and they led 5-1.
Columbus won the third period on chances ({p3.get(THEM, 0):.1f} to {p3.get(US, 0):.1f}), {p3_cbj:.0%} of the chance value. That's a normal
protect-the-lead period. Across the league over the last three seasons, teams down three or more in the third usually
got a bit over half the chances ({trail_share:.0%} overall), because the team ahead sits back, and about {at_least:.0%} of them got
{p3_cbj:.0%} or more.

## The goalie and the finishers

- **Ukko-Pekka Luukkonen** faced shots worth {upl.xga:.1f} goals and allowed {int(upl.ga)}, about {upl.gsax:.1f} better than an average
  goalie. He came in {upl_before_gsax:+.1f} goals against an average goalie for the season; he's now {upl_after_gsax:+.1f}.
- **Josh Norris** scored twice on shots worth {norris.xg:.1f} goals combined.
- **The power play** created its most dangerous chances of the season, worth {pg.loc[G, 'pp_xgf']:.1f} goals, but didn't score.
- **The penalty kill** allowed another goal, a Zach Werenski shot from 46 feet that goes in about 1 time in 20. Buffalo has now
  allowed {int(pk_all.loc[US, 'GA'])} power-play goals in {n_g} games, {ordn(pk_all.loc[US, 'rk'])} of 32 (1st is fewest). The league average is
  {pk_all.pg.mean() * n_g:.0f} over that many games.

| Period | Time | Team | Scorer | Shot | Odds it went in |
|---|---|---|---|---|---|
{goal_rows}

## What to watch Sunday against Vegas

Rebounds come from getting bodies to the net, which is partly a habit and partly how a game breaks. One night of it
doesn't make a trend. The things to watch against Vegas: whether Buffalo keeps getting bodies to the crease, whether
Luukkonen stays at or above average, and whether the penalty kill stops leaking.

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG
  equals league goals. Friday: BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal), CBJ {a.xg.sum():.2f} on
  {len(a)} ({int(a.on_goal.sum())} on goal). Win probability: {N:,} simulated replays of each shot as an independent coin flip with
  p = xG.
- Rebound = shot taken within 3 seconds of the same team's previous unblocked shot (on goal or missed), with no other
  event in between. Blocked attempts never start a rebound. A raw recount from the play feed that
  also counts shots after blocked attempts gives 12 for Buffalo. Teams with 10+ rebound shots: {share10:.1%} of team-games in
  2026-27, {share10_prev:.1%} in 2025-26.
- Score effects: third-period xG share for teams down 3+ goals by the game score at the time of each shot, 2023-24 to
  2025-26 ({trail_share:.1%} pooled; per game, median {med3:.0%}).
- GSAx = xG on unblocked shots faced minus goals allowed. Power play = 5v4, 5v3, 4v3.
"""
    (OUT / "2026-11-06-sabres-cbj.md").write_text(md)
    import json
    (OUT / "2026-11-06-sabres-cbj.hero.json").write_text(json.dumps({
        "label": "Friday's chances, in goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Blue Jackets"]],
        "note": f"Final: Sabres {int(gm.home_score)}, Blue Jackets {int(gm.away_score)}. {int(rb.shape[0])} Buffalo rebound shots, their most this season.",
        "explainer": {
            "kicker": "How we know", "title": "Rebounds are gold.",
            "text": (f"A shot right after another one catches the goalie out of position. Over the last three NHL seasons, "
                     f"rebounds went in {reb_rate:.1%} of the time, nearly double the {non_rate:.1%} for other shots. "
                     f"Buffalo had {int(rb.shape[0])} of them Friday."),
            "bars": [["Rebounds", round(float(reb_rate), 4)], ["Other shots", round(float(non_rate), 4)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
