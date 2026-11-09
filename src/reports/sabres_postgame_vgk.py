"""Sabres post-game: VGK at BUF, Nov 8, 2026 (Vegas 4, Buffalo 1). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-08-sabres-vgk.md, two PNGs and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF so the published story doesn't change. Grades Ledger P0001 via src/ledger/grade_p0001.py (separate).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
G, SEASON, US, THEM = 2026020278, 20262027, "BUF", "VGK"
AS_OF = "2026-11-08"
PRED_ID, PRED_P = "P0001", 0.46  # pregame call: Sabres win, 46% (ledger/predictions.csv)
VGK_GOLD = "#B4975A"


def main(as_of=AS_OF):
    s = shots()
    keep = set(query(f"SELECT game_id FROM raw_nhl_games WHERE game_date <= '{as_of}'").game_id)
    s = s[s.game_id.isin(keep)].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    u = s[unb & (s.season == SEASON)]
    g = u[u.game_id == G]
    f, a = g[g.team == US], g[g.team == THEM]
    allg = s[s.game_id == G]

    # replays: each shot an independent coin flip with p = its chance of going in
    rng = np.random.default_rng(7)
    N = 20000
    simf = (rng.random((N, len(f))) < f.xg.values).sum(1)
    sima = (rng.random((N, len(a))) < a.xg.values).sum(1)
    p_win, p_tie = (simf > sima).mean(), (simf == sima).mean()
    p_loss = 1 - p_win - p_tie
    p_held1 = (simf <= 1).mean()

    # by period and strength
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    pp_codes = ["5v4", "5v3", "4v3"]
    pp_f = f[f.strength.isin(pp_codes)]
    es_f, es_a = f[f.strength == "5v5"].xg.sum(), a[a.strength == "5v5"].xg.sum()
    st_f, st_a = f.xg.sum() - es_f, a.xg.sum() - es_a
    sh_a = a[a.strength.isin(["4v5", "3v5", "3v4"])].xg.sum()
    late = a[a.t >= 3480]  # final two minutes, after Vegas led 4-1
    late_pp_a = a[(a.t >= 3480) & a.strength.isin(pp_codes)].xg.sum()
    vgk_goals = allg[(allg.goal == 1) & (allg.team == THEM)]
    vgk_es_goals = int((vgk_goals.strength == "5v5").sum())

    # goalies: this game, and the season before/after
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    gk["name"] = gk.goalie_id.map(names)
    hill, ellis = gk[gk.opp == THEM].iloc[0], gk[gk.opp == US].iloc[0]  # opp = the goalie's own team (shots against it)

    def season_line(gid):
        x = u[u.goalie_id == gid]
        b = x[x.game_id != G]
        return x.game_id.nunique(), b.xg.sum() - b.goal.sum(), x.xg.sum() - x.goal.sum()
    cards = json.loads((OUT / "cards" / "goalies.json").read_text())["cards"]
    card = {c["id"]: c["gsax"] for c in cards}
    hill_n, hill_before, hill_after = season_line(hill.goalie_id)
    ellis_n, ellis_before, ellis_after = season_line(ellis.goalie_id)
    gg = u.groupby(["game_id", "goalie_id"]).apply(lambda x: x.xg.sum() - x.goal.sum(), include_groups=False)
    hill_game = gg.loc[(G, hill.goalie_id)]
    n_better = int((gg > hill_game).sum())
    share_atleast = (gg >= hill_game).mean()

    # blocked attempts (the shooting team owns the blocked shot)
    att = s[s.season == SEASON].groupby(["game_id", "team"]).agg(n=("unblocked", "size"), blk=("unblocked", lambda x: (x == 0).sum()))
    blk_g = att.loc[(G, US)]
    blk_avg = att.blk.mean()

    # pregame context: games before this one
    pre = u[u.game_id != G]
    tg = pre.groupby(["game_id", "team"]).xg.sum().rename("xgf").reset_index()
    ta = pre.groupby(["game_id", "opp"]).xg.sum().rename("xga").reset_index().rename(columns={"opp": "team"})
    tm = tg.merge(ta, on=["game_id", "team"]).groupby("team")[["xgf", "xga"]].mean()
    vgk_allow_rk = int(tm.xga.rank(method="min").loc[THEM])
    buf_create = tm.loc[US, "xgf"]
    n_blk_ge = int((att.blk >= blk_g.blk).sum())
    buf_att_avg = att.xs(US, level="team").drop(G).n.mean()
    lg_blk_share = (att.blk.sum() / att.n.sum())

    # goal list
    gl = allg[allg.goal == 1].sort_values(["period", "t"]).copy()
    gl["who"] = gl.shooter_id.map(names)
    gl["clock"] = (gl.t - (gl.period - 1) * 1200).map(lambda x: f"{int(x) // 60}:{int(x) % 60:02d}")
    hertl = a[a.shooter_id.map(names) == "Tomas Hertl"]
    marner_goal = gl[gl.who == "Mitch Marner"].iloc[0]

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, VGK_GOLD, "Golden Knights")]:
        x = g[g.team == team].sort_values(["period", "t"])
        cum = x.xg.cumsum()
        ax.step(np.r_[0, x.t / 60, 60], np.r_[0, cum, cum.iloc[-1]], where="post", color=col, lw=2.4, label=lab)
        gx = x.goal == 1
        ax.scatter(x.t[gx] / 60, cum[gx], s=70, color=RED if team == US else INK, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    for x0, lab in ((10, "1st"), (30, "2nd"), (50, "3rd")):
        ax.text(x0, 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=9, color=MUTED)
    lv = a[a.t >= 3480].xg.sum()
    ax.annotate(f"Vegas up {int(gm.away_score)}-{int(gm.home_score)},\nlast 2 minutes", xy=(59.3, a.xg.sum() - lv / 2), xytext=(50.5, 1.2),
                fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60], ["0", "", "20", "", "40", "", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Buffalo had the better chances. Vegas won {int(gm.away_score)}-{int(gm.home_score)}",
           "Running total of what each team's shots were worth. Red dot = Sabres goal, black dots = Golden Knights goals.",
           f"Unblocked shots, empty net excluded. Sabres {len(f)} unblocked shots, Golden Knights {len(a)}.")
    fig.savefig(OUT / "sabres-vgk-post-flow.png"); plt.close(fig)

    # ---- chart 2: Hill's night against every goalie game this season
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    bins = np.arange(np.floor(gg.min()), np.ceil(gg.max()) + 0.5, 0.5)
    ax.hist(gg, bins=bins, color=GRAY, zorder=2, edgecolor="white")
    ax.axvline(hill_game, color=VGK_GOLD, lw=2.5, zorder=3)
    ax.text(hill_game, ax.get_ylim()[1] * 0.92, f"  Adin Hill, Sunday: {hill_game:+.1f}", color=INK, fontsize=10, fontweight="bold", ha="left")
    ax.axvline(ellis.saved, color=BLUE, lw=2.5, zorder=3)
    ax.text(ellis.saved - 0.15, ax.get_ylim()[1] * 0.97, f"Colten Ellis, Sunday: {ellis.saved:+.1f}", color=INK, fontsize=10, ha="right", va="top",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.set_xlabel("Goals saved vs. an average goalie, one game"); ax.set_ylabel("Goalie games")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Hill's night was better than {1 - share_atleast:.0%} of goalie games this season",
           f"Every NHL goalie appearance in 2026-27 through Nov. 8 ({len(gg)}), by goals saved compared with an average goalie on the same shots.",
           "Unblocked shots, empty net excluded. Positive = saved more than an average goalie would have.")
    fig.savefig(OUT / "sabres-vgk-post-goalies.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {int(r.period)} | {r.clock} | {'Sabres' if r.team == US else 'Golden Knights'} | {r.who} | {r.shot_type} from {r.dist:.0f} ft"
        f"{', rebound' if r.rebound else ''}{', shorthanded' if r.strength in ('4v5', '3v5', '3v4') else ''}"
        f"{', power play' if r.strength in pp_codes else ''} | {r.xg:.0%} |" for r in gl.itertuples())
    brier = (PRED_P - 0) ** 2
    md = f"""# Golden Knights {int(gm.away_score)}, Sabres {int(gm.home_score)}: Buffalo had the better chances. Adin Hill had the better night

**Finding: The Sabres lost {int(gm.away_score)}-{int(gm.home_score)} Sunday, but they had the better chances: their shots were worth {f.xg.sum():.1f} goals to Vegas's {a.xg.sum():.1f},
and {es_f:.1f} to {es_a:.1f} at full strength. The difference was in goal. Adin Hill stopped {int(hill.on - hill.ga)} of {int(hill.on)} shots, about {hill.saved:.1f} goals
better than an average goalie, one of the best goalie nights in the league this season. On shots like Buffalo's, the Sabres score one goal or fewer
only {p_held1:.0%} of the time.**

*One game, {gm.game_date}, in Buffalo. [Our pregame story](sabres-vegas-pregame-nov-8.html).*

![Game flow](sabres-vgk-post-flow.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Add those up and you get what a team's
chances were worth in goals. Sunday's goals show the range: Marner's shot from {marner_goal.dist:.0f} feet had a {marner_goal.xg:.0%} chance of going in;
Hertl's second goal, from {gl.dist.max():.0f} feet, about {gl.loc[gl.dist.idxmax(), 'xg']:.0%}. The shot locations come from the NHL's own play-by-play
for every game. (The full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

Sunday, Buffalo's {len(f)} shots that weren't blocked were worth **{f.xg.sum():.1f} goals**. Vegas's {len(a)} were worth **{a.xg.sum():.1f}**. Buffalo scored once.

To see how unusual that is, we replayed Sunday's game {N:,} times, letting each shot go in or miss at its own chance. Buffalo won {p_win:.0%} of the
replays, Vegas {p_loss:.0%}, and {p_tie:.0%} ended tied. The Sabres scored one goal or fewer in only {p_held1:.0%} of them. (That {p_win:.0%} happens to match our
pregame number. It's a coincidence: the pregame number came from each team's form before the game; this one comes only from Sunday's shots.)

The full-strength edge was clear: **{es_f:.1f} to {es_a:.1f} in chances.** When someone was in the penalty box, on a power play either way, Vegas won {st_a:.1f} to {st_f:.1f}. And a full goal's worth of Vegas's
{a.xg.sum():.1f} ({late.xg.sum():.1f}, on {len(late)} shots) came in the final two minutes, after it led {int(gm.away_score)}-{int(gm.home_score)} and the game was decided.

## A big first period, then a shorthanded goal turned it

| Period | Sabres chances, in goals | Golden Knights chances, in goals | What happened |
|---|---|---|---|
| 1st | {per.loc[1, US]:.1f} | {per.loc[1, THEM]:.1f} | Buffalo's best period. No goals. |
| 2nd | {per.loc[2, US]:.1f} | {per.loc[2, THEM]:.1f} | Vegas scores twice, the first one shorthanded. |
| 3rd | {per.loc[3, US]:.1f} | {per.loc[3, THEM]:.1f} | Beck Malenstyn makes it 2-1; Tomas Hertl answers twice. |

The first period was the Sabres' game to take: their chances were worth {per.loc[1, US]:.1f} goals to {per.loc[1, THEM]:.1f}, and it stayed 0-0. The turn came in the second,
when Mitch Marner scored from {marner_goal.dist:.0f} feet while Vegas was killing a penalty.

That sums up Buffalo's power play Sunday: **Vegas got more out of it than Buffalo did.** Vegas's shorthanded shots were worth {sh_a:.1f} goals; Buffalo's
power-play shots were worth {pp_f.xg.sum():.1f}, and it didn't score with the extra man.

| Period | Time | Team | Scorer | Shot | Chance it went in |
|---|---|---|---|---|---|
{goal_rows}

## The goalie duel went the other way

Coming in, these two were at opposite ends. [Colten Ellis](../cards/colten-ellis.html) had saved {ellis_before:.1f} more goals than an average goalie
would have on the same shots this season ({ellis_n - 1} games). [Adin Hill](../cards/adin-hill.html) had allowed {-hill_before:.1f} more than an average goalie would have
({hill_n - 1} games). Both numbers come from fewer than 10 games, so they swing fast. (Our pregame story said {abs(card[int(hill.goalie_id)]):.1f}; the number shifts a little
as each night's games are added.)

Sunday flipped it. Hill faced Buffalo shots worth {hill.xga:.1f} goals and allowed {int(hill.ga)}: **{hill.saved:.1f} goals better than an average goalie.** Only {n_better} of
the {len(gg)} goalie games in the NHL this season have been better. Ellis faced Vegas shots worth {ellis.xga:.1f} goals and allowed {int(ellis.ga)}: **{-ellis.saved:.1f} worse than
average**, a little below, not a bad night. In one afternoon, Hill went from {-hill_before:.1f} below average for the season to {hill_after:.1f} above ({hill_n} games now);
Ellis went from {ellis_before:.1f} above to {ellis_after:.1f} ({ellis_n} games).

![Goalie nights](sabres-vgk-post-goalies.png)

**Why goalies aren't in our prediction model.** Before Sunday's game we tested it: we split past seasons in half and checked whether a goalie's
first half told us about his second half. It barely did, far less than how many chances a team gives up carries over. And adding the starting goalie
didn't make our game predictions any better. Sunday is an example: the goalie with the worse numbers coming in had one of the best nights in the league.

## Vegas got in the way

Buffalo tried {int(blk_g.n)} shots and Vegas blocked {int(blk_g.blk)} of them. A team has about {blk_avg:.0f} shots blocked in a typical game, and only {n_blk_ge} times in
{len(att)} team games this season has a team had {int(blk_g.blk)} or more blocked. Blocked shots don't count toward Buffalo's {f.xg.sum():.1f}.

## Receipts: our pregame call

Before the game we logged one call on the [Ledger](../ledger.html): **a {PRED_P:.0%} chance the Sabres win.** That meant our model leaned slightly toward Vegas, and
Vegas won, so it counts as a hit. Don't read much into it: our pregame story noted that leans this slight (50-55%) had come in only about half the time in testing.
Hit or miss, it stays up.

We also score every call: take the gap between the chance we gave and what happened, and square it. Lower is better. Our {PRED_P:.0%} on a Buffalo loss
scores {brier:.2f}; a straight 50/50 guess would have scored 0.25. So a bit better than a coin flip, on one game. The point is the season-long record.

We're not taking a victory lap. The model expected a close game with Vegas slightly ahead. It was close, but Buffalo was the one slightly ahead, and
our model doesn't try to predict a goalie's hot night; our tests say it can't be done reliably from a goalie's recent numbers.

## What it means for Buffalo

- **Buffalo won at full strength, {es_f:.1f} to {es_a:.1f} in chances.** And it did that against a defense that had given up the {ordn(vgk_allow_rk)}-fewest chances
  overall coming in. In all, the Sabres created {f.xg.sum():.1f} goals' worth, well above their {buf_create:.1f} average.
- **The power play hurt, but it didn't decide it.** With someone in the penalty box, Vegas had the better chances, {st_a:.1f} to {st_f:.1f}, though
  {late_pp_a:.1f} of that came in the final two minutes with the game decided. Buffalo's power play came up empty, and Marner's shorthanded goal opened
  the scoring. {['None', 'One', 'Two', 'Three', 'Four'][vgk_es_goals]} of Vegas's {['no', 'one', 'two', 'three', 'four', 'five', 'six'][len(vgk_goals)]} goals came at full strength, where Buffalo had the better chances.
- **What carries over is the chances, not the goalie's night.** Two of our tests point the same way. The chances a team gives up carry over from one
  half of a season to the next far better than a goalie's numbers do, and a team's edge in chances carries over from one season to the next far better
  than its finishing or goaltending. One night isn't a trend, but Buffalo's even-strength edge is the kind of thing that tends to last; Hill's afternoon
  is the kind that doesn't.
- **Ellis was a little below average, not bad.** He's still {ellis_after:.1f} above average for the season ({ellis_n} games).

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals.
  BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal); VGK {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal).
- Replays: {N:,} simulations, each shot an independent coin flip with p = xG. BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx = xG on unblocked shots faced minus goals allowed. Hill {hill.saved:+.2f} ({int(hill.on)} shots on goal), Ellis {ellis.saved:+.2f}. Hill's game ranks
  {ordn(n_better + 1)} of {len(gg)} 2026-27 goalie games. Season GSAx before/after: Hill {hill_before:+.2f}/{hill_after:+.2f}, Ellis {ellis_before:+.2f}/{ellis_after:+.2f}
  (this season only; shot values rescaled with games through Nov. 8, so Hill's pregame {card[int(hill.goalie_id)]:+.1f} reads {hill_before:+.1f} here).
- Strength: five on five BUF {es_f:.2f}, VGK {es_a:.2f}; all other situations BUF {st_f:.2f}, VGK {st_a:.2f}. Final two minutes (58:00 on): VGK {late.xg.sum():.2f} on {len(late)} shots.
- Blocked attempts: attributed to the shooting team. Power play = 5v4, 5v3, 4v3 from the shooter's side.
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0, Brier {brier:.4f}; scored a hit because p < 0.5 and the event didn't happen. Model nhl-game-v0.1.
"""
    (OUT / "2026-11-08-sabres-vgk.md").write_text(md)
    hill_sv = (hill.on - hill.ga) / hill.on
    ellis_sv = (ellis.on - ellis.ga) / ellis.on
    (OUT / "2026-11-08-sabres-vgk.hero.json").write_text(json.dumps({
        "label": "Sunday's chances, in goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Golden Knights"]],
        "note": f"Final: Golden Knights {int(gm.away_score)}, Sabres {int(gm.home_score)}. Adin Hill saved {hill.saved:.1f} goals more than an average goalie.",
        "explainer": {
            "kicker": "The difference", "title": "It was in goal.",
            "text": (f"Buffalo's chances were worth more than Vegas's. Adin Hill stopped {int(hill.on - hill.ga)} of {int(hill.on)}; "
                     f"Colten Ellis stopped {int(ellis.on - ellis.ga)} of {int(ellis.on)}. Goals saved compared with an average goalie on the same shots:"),
            "fmt": "goals",
            "bars": [["Hill, Vegas", round(float(hill.saved), 1)], ["Ellis, Buffalo", round(float(ellis.saved), 1)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
