"""Sabres post-game: TBL at BUF, Nov 11, 2026 (Tampa Bay 8, Buffalo 3). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-12-sabres-tbl.md, two PNGs and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF so the published story doesn't change. Ledger P0009 graded by src/ledger/grade_p0009.py (separate).
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
G, SEASON, US, THEM = 2026020293, 20262027, "BUF", "TBL"
AS_OF = "2026-11-11"
PRED_ID, PRED_P = "P0009", 0.47
PRE_XG_US, PRE_XG_THEM = 3.20, 3.44   # pregame expected chances, from P0009's notes in ledger/predictions.csv
TBL_BLUE = "#7A8699"   # gray-blue, so Tampa's line reads apart from the Sabres' blue
UPL, ELLIS = 8480045, 8481551


def clock(t):
    t = int(t) % 1200
    return f"{t // 60}:{t % 60:02d}"


def main(as_of=AS_OF):
    s = shots()
    keep = set(query(f"SELECT game_id FROM raw_nhl_games WHERE game_date <= '{as_of}'").game_id)
    s = s[s.game_id.isin(keep)].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg_raw"] = s.xg
    s["xg"] = s.xg * s.season.map(cal)
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    assert gm.home == US and gm.away == THEM and gm.game_state in ("OFF", "FINAL")
    us_sc, them_sc = int(gm.home_score), int(gm.away_score)

    # score at the moment of every shot (goals before this event)
    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    allg["us_g"] = ((allg.team == US) & (allg.goal == 1)).cumsum().shift(fill_value=0)
    allg["them_g"] = ((allg.team == THEM) & (allg.goal == 1)).cumsum().shift(fill_value=0)
    allg["diff"] = allg.us_g - allg.them_g
    assert int(allg.us_g.iloc[-1] + (allg.team.iloc[-1] == US) * allg.goal.iloc[-1]) == us_sc
    assert int((allg[(allg.team == THEM)].goal == 1).sum()) == them_sc and int((allg[(allg.team == US)].goal == 1).sum()) == us_sc
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    f, a = g[g.team == US], g[g.team == THEM]
    close = g[g["diff"] >= -1]
    behind = g[g["diff"] <= -2]
    cf, ca = close[close.team == US].xg.sum(), close[close.team == THEM].xg.sum()
    bf, ba = behind[behind.team == US].xg.sum(), behind[behind.team == THEM].xg.sum()
    n_cf, n_ca = int((close.team == US).sum()), int((close.team == THEM).sum())
    n_bf, n_ba = int((behind.team == US).sum()), int((behind.team == THEM).sum())
    assert (g["diff"] <= 0).all(), "Buffalo never led; table labels assume it"
    big = close[close.team == THEM].sort_values("xg").iloc[-1]
    assert big.xg > cf / 2 and big.rebound == 1

    # league-wide: share of chances taken by a team that trails by 2+ (this season, all games through AS_OF)
    lg = s[s.season == SEASON].sort_values(["game_id", "period", "t", "eventId"]).copy()
    lg["gf"] = (lg.goal == 1).astype(int)
    lg["tg"] = lg.groupby(["game_id", "team"]).gf.cumsum() - lg.gf           # shooter's team goals before this shot
    tot = lg.groupby("game_id").gf.cumsum() - lg.gf
    lg["og"] = tot - lg.tg                                                   # opponent goals before this shot
    lu = lg[(lg.unblocked == 1) & (lg.empty_net_against == 0)]
    lead_xg = lu.assign(d=lu.tg - lu.og)
    down2 = lead_xg[lead_xg.d <= -2].xg.sum()
    up2 = lead_xg[lead_xg.d >= 2].xg.sum()
    trail_share = down2 / (down2 + up2)
    even_share = 0.5

    # exact replay math: each shot goes in or misses at its own chance (Poisson-binomial, by convolution)
    def pmf(ps):
        d = np.array([1.0])
        for q in ps:
            d = np.convolve(d, [1 - q, q])
        return d
    pf, pa = pmf(f.xg.values), pmf(a.xg.values)
    joint = np.outer(pf, pa)                      # [buffalo goals, tampa goals]
    p_win, p_tie = np.tril(joint, -1).sum(), np.trace(joint)
    p_loss = 1 - p_win - p_tie
    p_8 = pa[them_sc:].sum()

    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    pp_codes = ["5v4", "5v3", "4v3"]
    es_f, es_a = f[f.strength == "5v5"].xg.sum(), a[a.strength == "5v5"].xg.sum()
    pp_f, pp_a = f[f.strength.isin(pp_codes)].xg.sum(), a[a.strength.isin(pp_codes)].xg.sum()

    # goalies: this game, the season before/after, and where the night ranks
    u = s[unb & (s.season == SEASON)]
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    gk = gk.set_index("goalie_id")
    upl, ellis, vasy = gk.loc[UPL], gk.loc[ELLIS], gk[gk.opp == THEM].iloc[0]   # opp = the goalie's own team
    assert len(gk[gk.opp == THEM]) == 1 and gk.loc[UPL].opp == US and gk.loc[ELLIS].opp == US
    switch = allg[(allg.team == THEM) & (allg.goalie_id == ELLIS)].t.min()        # first Tampa shot Ellis faced
    pulled_after = allg[(allg.team == THEM) & (allg.goal == 1) & (allg.t < switch)]
    assert len(pulled_after) == int(upl.ga)

    sw = allg[allg.t >= switch].iloc[0]
    sw_us, sw_them = int(sw.us_g), int(sw.them_g)

    def season_line(gid):
        x = u[u.goalie_id == gid]
        b = x[x.game_id != G]
        return x.game_id.nunique(), b.xg.sum() - b.goal.sum(), x.xg.sum() - x.goal.sum()
    upl_n, upl_before, upl_after = season_line(UPL)
    ell_n, ell_before, ell_after = season_line(ELLIS)
    tg = u.groupby(["game_id", "opp"]).apply(lambda x: x.xg.sum() - x.goal.sum(), include_groups=False)   # team goaltending, per game
    team_night = tg.loc[(G, US)]
    n_worse = int((tg < team_night).sum())
    sv_us = 1 - (upl.ga + ellis.ga) / (upl.on + ellis.on)
    lg_sv = 1 - u[u.on_goal == 1].goal.sum() / u.on_goal.sum()

    # context: season averages before this game
    # "coming in" = games before this game's date, with shot values scaled on those games only (matches the pregame story)
    before = set(query(f"SELECT game_id FROM raw_nhl_games WHERE game_date < '{gm.game_date}'").game_id)
    sb = s[s.game_id.isin(before)].copy()
    sb["xg"] = sb.xg_raw
    ub = (sb.unblocked == 1) & (sb.empty_net_against == 0)
    cal_b = sb[ub].groupby("season").goal.sum() / sb[ub].groupby("season").xg.sum()
    sb["xg"] = sb.xg * sb.season.map(cal_b)
    pre = sb[ub & (sb.season == SEASON)]
    tf = pre.groupby(["game_id", "team"]).xg.sum()
    ta = pre.groupby(["game_id", "opp"]).xg.sum()
    buf_for, buf_ag = tf.xs(US, level=1).mean(), ta.xs(US, level=1).mean()
    tf_m, ta_m = tf.groupby(level=1).mean(), ta.groupby(level=1).mean()
    rk_for, rk_ag = int(tf_m.rank(ascending=False, method="min")[US]), int(ta_m.rank(method="min")[US])
    lg_pg = tf_m.mean()

    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    kuch = gl[(gl.team == THEM) & (gl.who == "Nikita Kucherov")]
    first_goal_t = gl.t.min()
    early = g[g.t < first_goal_t]
    e_f, e_a = early[early.team == US].xg.sum(), early[early.team == THEM].xg.sum()

    # ledger record to date (graded calls only)
    pr = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    m = pr.merge(gr, left_on="id", right_on="prediction_id")
    m = m[pd.to_datetime(m.graded_at_utc) <= pd.Timestamp(as_of, tz="UTC") + pd.Timedelta(days=2)]
    hits = int((((m.probability >= 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))).sum())
    brier = (PRED_P - 0) ** 2
    assert PRED_ID in set(m.id)

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, TBL_BLUE, "Lightning")]:
        x = g[g.team == team]
        cum = x.xg.cumsum()
        ax.step(np.r_[0, x.t / 60, 60], np.r_[0, cum, cum.iloc[-1]], where="post", color=col, lw=2.4, label=lab,
                ls="-" if team == US else (0, (4, 1.5)))
        gx = x.goal == 1
        ax.scatter(x.t[gx] / 60, cum[gx], s=70, color=RED if team == US else INK, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    for x0, lab in ((10, "1st"), (30, "2nd"), (50, "3rd")):
        ax.text(x0, 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=9, color=MUTED)
    ax.axvspan(0, first_goal_t / 60, color="#F3F4F6", zorder=0)
    ax.axvline(switch / 60, color=MUTED, lw=1, ls=":")
    ax.text(switch / 60 + 0.4, 0.4, "Ellis's first\nshot faced", fontsize=8.5, color=INK)
    ax.text(first_goal_t / 120, 3.3, "Before the\nfirst goal", fontsize=8.5, color=MUTED, ha="center")
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60], ["0", "", "20", "", "40", "", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="lower right"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Tampa had the chances while it was close; Buffalo's came once it was down",
           f"Running total of each team's chances. Final: chances {f.xg.sum():.1f} to {a.xg.sum():.1f}, score {them_sc}-{us_sc} Tampa. Red dots = Sabres goals, black = Lightning.",
           f"Unblocked shots, empty net excluded. Sabres {len(f)} unblocked shots, Lightning {len(a)}. Nov. 11, 2026, in Buffalo.")
    fig.savefig(OUT / "sabres-tbl-post-flow.png"); plt.close(fig)

    # ---- chart 2: Buffalo's goaltending night against every team-game this season
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    bins = np.arange(np.floor(tg.min()), np.ceil(tg.max()) + 0.5, 0.5)
    ax.hist(tg.drop((G, US)), bins=bins, color=GRAY, zorder=2, edgecolor="white")
    ax.axvline(team_night, color=RED, lw=2.5, zorder=3)
    ax.text(team_night + 0.15, ax.get_ylim()[1] * 0.92, f"Sabres, Wednesday: {team_night:+.1f}", color=INK, fontsize=10, fontweight="bold")
    ax.set_xlabel("Goals saved vs. an average goalie, one team, one game"); ax.set_ylabel("Team games")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Only {n_worse} games this season have been worse in goal for any NHL team",
           f"Every other NHL team game in 2026-27 through Nov. 11 ({len(tg) - 1}), by goals saved compared with an average goalie on the same shots.",
           "Unblocked shots, empty net excluded. Both Sabres goalies combined. Positive = saved more than an average goalie would have.")
    fig.savefig(OUT / "sabres-tbl-post-goalies.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Lightning'} | {r.who} | {r.shot_type} from {r.dist:.0f} ft"
        f"{', rebound' if r.rebound else ''}{', power play' if r.strength in pp_codes else ''} | {r.xg:.0%} | "
        f"{int(r.us_g + (r.team == US))}-{int(r.them_g + (r.team == THEM))} |" for r in gl.itertuples())
    n_kuch = len(kuch)
    kuch_pp = ", one of them the third of Kucherov's hat trick" if n_kuch >= 3 and kuch.strength.isin(pp_codes).any() else ""
    them_pp = int(((gl.team == THEM) & gl.strength.isin(pp_codes)).sum())
    us_goals_t = gl[gl.team == US].t
    burst = us_goals_t.max() - us_goals_t.min()
    comeback_gap = int(gl[(gl.team == THEM) & (gl.t > us_goals_t.max())].t.min() - us_goals_t.max())
    plural_s = lambda n: f"{n} seconds" if n < 60 else f"{n // 60} minute{'s' if n >= 120 else ''} {n % 60} seconds"
    assert ca > 2 * cf and burst < 300
    fg_min, fg_sec = divmod(int(first_goal_t), 60)
    gs = lambda v: f"{abs(v):.1f} {'better' if v >= 0 else 'worse'}"
    gw = lambda v: f"{abs(v):.1f} goals {'better' if v >= 0 else 'worse'} than an average goalie"
    md = f"""# Lightning {them_sc}, Sabres {us_sc}: outplayed early, then sunk in goal

**Finding: The Sabres were badly outplayed while this game was still close: Tampa's chances were worth {ca:.1f} goals to Buffalo's {cf:.1f}.
Then the goaltending turned it into a blowout. Ukko-Pekka Luukkonen and Colten Ellis allowed {them_sc} goals on shots worth {a.xg.sum():.1f}, the
{ordn(n_worse + 1)}-worst night in goal for any NHL team this season, out of {len(tg)}.**

*One game, {gm.game_date}, in Buffalo. [Our pregame story](sabres-lightning-pregame-nov-11.html).*

![Game flow](sabres-tbl-post-flow.png)

## Even chances, but only on paper

Over the whole game, the chances came out even: Buffalo's {len(f)} shots that weren't blocked were worth **{f.xg.sum():.1f} goals**, Tampa's {len(a)} were worth
**{a.xg.sum():.1f}**. That number hides how the game went, so we split it by the score.

| Score when the shot was taken | Sabres chances, in goals | Lightning chances, in goals |
|---|---|---|
| Tied, or Sabres down one | {cf:.1f} ({n_cf} shots) | {ca:.1f} ({n_ca} shots) |
| Sabres down two or more | {bf:.1f} ({n_bf} shots) | {ba:.1f} ({n_ba} shots) |

In the first {fg_min}:{fg_sec:02d}, before anyone scored, Tampa's chances were worth {e_a:.1f} goals to Buffalo's {e_f:.1f}, and the first period as a whole
went {per.loc[1, THEM]:.1f} to {per.loc[1, US]:.1f} Tampa. While the game was within reach, **Tampa had better than twice Buffalo's chances.** That's a small sample,
{n_cf + n_ca} shots, nearly all of them in the first period.

Buffalo's push came from behind, and it was real: down two or more, the Sabres got {bf / (bf + ba):.0%} of the chances. Across the NHL this season, a team
that far behind gets {trail_share:.0%}, so this looks like more than the usual effect of Tampa sitting on a lead, though it's only {n_bf + n_ba} shots. Down 4-0 in the second, the Sabres scored three times in
{burst // 60} minutes {burst % 60} seconds, the last {clock(gl[gl.team == US].t.max())} into the third, to make it 4-3. Just {plural_s(comeback_gap)} later, Nikita Kucherov
made it 5-3, and that was the turn.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Add those up and you get what a team's chances were
worth in goals. Wednesday shows the range: Josh Doan's tip-in from {gl[gl.who == 'Josh Doan'].dist.iloc[0]:.0f} feet had a {gl[gl.who == 'Josh Doan'].xg.iloc[0]:.0%} chance of going in;
Tage Thompson's slap shot from {gl[gl.who == 'Tage Thompson'].dist.iloc[0]:.0f} feet about {gl[gl.who == 'Tage Thompson'].xg.iloc[0]:.0%}. While it was close, one Tampa rebound, {names[big.shooter_id]}'s from {big.dist:.0f} feet, was a {big.xg:.0%} chance by itself,
more than half of Buffalo's {cf:.1f} total in that stretch. Add up all {len(a)} of Tampa's shots that
weren't blocked and they were worth {a.xg.sum():.1f} goals. Tampa scored {them_sc}. The shot locations come from the NHL's own
play-by-play. (The full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

To see how unusual {them_sc} goals on those chances is, imagine replaying the game over and over, with each shot going in or missing at its own
chance. Tampa would score {them_sc} or more **{p_8:.1%} of the time**, about once in {round(1 / p_8)} games. Over the whole game those replays come out about even:
Buffalo wins {p_win:.0%}, Tampa {p_loss:.0%}, tied after 60 minutes {p_tie:.0%}. The catch: {bf / f.xg.sum():.0%} of Buffalo's chances came after it was already down two or more.

## The goaltending

[Luukkonen](../cards/ukko-pekka-luukkonen.html) faced Tampa shots worth {upl.xga:.1f} goals and allowed {int(upl.ga)} before he was pulled with the Sabres down {sw_them}-{sw_us}
early in the third: **{-upl.saved:.1f} more than an average goalie would have allowed.** [Ellis](../cards/colten-ellis.html) faced {int((g.goalie_id == ELLIS).sum())} shots
worth {ellis.xga:.1f} and allowed {int(ellis.ga)}: **{-ellis.saved:.1f} more than average.** Together, the Sabres stopped {sv_us:.0%} of the shots on goal; the league
stops {lg_sv:.0%}. At the other end, [Andrei Vasilevskiy](../cards/andrei-vasilevskiy.html) stopped {int(vasy.on - vasy.ga)} of {int(vasy.on)}, {vasy.saved:.1f} goals better than an average goalie.

Add the two Sabres goalies together and it's **{-team_night:.1f} goals worse than average** in one night. Only {n_worse} team games this season have been worse.

![Goalie nights](sabres-tbl-post-goalies.png)

Luukkonen's season goes from {gw(upl_before)} to {gs(upl_after)} ({upl_n} games). Ellis's season goes from
{gs(ell_before)} to {gs(ell_after)} ({ell_n} games). One night moved Ellis from above average to below. Both seasons are short enough that one game swings them hard,
which is also why our game model doesn't lean on goalies: in [our tests](sabres-vegas-pregame-nov-8.html), a goalie's first half of a season told us little about his second half.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). Tampa won, so it counts as a hit, but a soft one: a
{PRED_P:.0%} call is close to a coin flip. Scored the usual way (the gap between our chance and what happened, squared; lower is better), it comes to
{brier:.2f}, a little better than a 50/50 guess's 0.25. That makes our record {hits} of {len(m)} on graded calls.

The model expected chances worth {PRE_XG_US:.2f} goals for Buffalo and {PRE_XG_THEM:.2f} for Tampa. The game came in at {f.xg.sum():.1f} and {a.xg.sum():.1f}, close to
that. The model doesn't try to predict a night like this in goal.

## What it means for Buffalo

- **The early game is the worry, not the final score.** Coming in, Buffalo had been giving up more than
  it created: {buf_for:.1f} chances created per game ({ordn(rk_for)} of 32) and {buf_ag:.1f} allowed ({ordn(rk_ag)}; only {32 - rk_ag} {'team' if 32 - rk_ag == 1 else 'teams'} allowed more), with the league average at {lg_pg:.1f}. Tampa's {per.loc[1, THEM]:.1f} in the first period alone was {per.loc[1, THEM] / buf_ag:.0%} of what
  Buffalo usually allows in a whole game.
- **The goaltending is the kind of thing that doesn't carry over.** A night like this is rare, and in our tests a goalie's numbers swing far more
  from stretch to stretch than a team's chances do. Expect better in net; don't expect it to fix the early-game problem.

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal); TBL {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal).
- Score state: shots taken with BUF trailing by 0-1 (or leading): BUF {cf:.2f}, TBL {ca:.2f}; trailing by 2+: BUF {bf:.2f}, TBL {ba:.2f}. Five on five: BUF {es_f:.2f}, TBL {es_a:.2f}.
- Power play: chances BUF {pp_f:.2f}, TBL {pp_a:.2f}; power-play goals BUF {int(((gl.team == US) & gl.strength.isin(pp_codes)).sum())}, TBL {them_pp}.
- Score effects: league 2026-27, share of xG taken by the trailing team when the margin is 2+: {trail_share:.3f}.
- Replays: exact Poisson-binomial over shots (each an independent Bernoulli with p = xG). BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}; TBL {them_sc}+ goals {p_8:.4f}.
- GSAx = xG on unblocked shots faced minus goals allowed. Luukkonen {upl.saved:+.2f} ({int(upl.on)} SOG), Ellis {ellis.saved:+.2f} ({int(ellis.on)} SOG), Vasilevskiy
  {vasy.saved:+.2f} ({int(vasy.on)} SOG). BUF team GSAx {team_night:+.2f}, {ordn(n_worse + 1)}-lowest of {len(tg)} 2026-27 team games. Save rate on shots on goal: BUF {sv_us:.3f}, league {lg_sv:.3f}.
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0, Brier {brier:.4f}; scored a hit because p < 0.5 and the event didn't happen. Model nhl-game-v0.1.
"""
    (OUT / "2026-11-12-sabres-tbl.md").write_text(md)
    (OUT / "2026-11-12-sabres-tbl.hero.json").write_text(json.dumps({
        "label": "Chances while the game was close, in goals",
        "big": [[round(float(cf), 1), "Sabres"], [round(float(ca), 1), "Lightning"]],
        "note": f"Final: Lightning {them_sc}, Sabres {us_sc}. Tampa scored {them_sc} on shots worth {a.xg.sum():.1f}.",
        "explainer": {
            "kicker": "In goal", "title": f"The NHL's {ordn(n_worse + 1)}-worst night in goal this season.",
            "text": "Goals saved compared with an average goalie on the same shots:",
            "fmt": "goals",
            "bars": [["Luukkonen", round(float(upl.saved), 1)], ["Ellis", round(float(ellis.saved), 1)], ["Vasilevskiy, Tampa", round(float(vasy.saved), 1)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
