"""Sabres post-game: BUF at DAL, Nov 14, 2026 (Dallas 2, Buffalo 0). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-15-sabres-dal.md, two PNGs and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF so the published story doesn't change. Ledger P0011 graded by src/ledger/grade_p0011.py (separate).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, INK, MUTED
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
G, SEASON, US, THEM = 2026020322, 20262027, "BUF", "DAL"
AS_OF = "2026-11-14"
PRE = "2026-11-12"   # the pregame story's data ran through this date
PRED_ID, PRED_P = "P0011", 0.38
PRE_XG_US, PRE_XG_THEM = 2.79, 3.49   # pregame expected goals, from P0011's notes in ledger/predictions.csv
DAL_GREEN = "#006847"
LYON, OETTINGER = 8479312, 8479979
PP = ("5v4", "5v3", "4v3")


def clock(t):
    t = int(t) % 1200
    return f"{t // 60}:{t % 60:02d}"


def pmf(ps):
    out = np.array([1.0])
    for q in ps:
        out = np.convolve(out, [1 - q, q])
    return out


def main(as_of=AS_OF):
    s = shots()
    keep = query(f"SELECT game_id, season, game_date, home, away FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    s = s[s.game_id.isin(set(keep.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    assert gm.home == THEM and gm.away == US and gm.game_state in ("OFF", "FINAL") and gm.last_period_type == "REG"
    us_sc, them_sc = int(gm.away_score), int(gm.home_score)
    assert (us_sc, them_sc) == (0, 2)

    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    assert int(allg[allg.team == US].goal.sum()) == us_sc and int(allg[allg.team == THEM].goal.sum()) == them_sc
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    assert len(allg[(allg.unblocked == 1) & (allg.empty_net_against == 1)]) == 0   # no empty-net shots either way
    f, a = g[g.team == US], g[g.team == THEM]
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    nper = g.groupby(["period", "team"]).size().unstack().fillna(0).astype(int)
    assert set(per.index) == {1, 2, 3}

    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    first, second = gl.iloc[0], gl.iloc[1]
    assert first.team == THEM and second.team == THEM

    # close-in and rebound shots: this game vs the pregame story's season numbers (games through PRE)
    pre = s[unb & (s.season == SEASON) & s.game_id.isin(set(keep[keep.game_date <= PRE].game_id))]
    gp = pd.concat([keep[keep.game_date <= PRE].assign(team=keep.home), keep[keep.game_date <= PRE].assign(team=keep.away)])
    gp = gp[gp.season == SEASON].groupby("team").game_id.nunique()
    close_f = pre[pre.dist < 20].groupby("team").size() / gp
    close_a = pre[pre.dist < 20].groupby("opp").size() / gp
    reb_f = pre[pre.rebound == 1].groupby("team").size() / gp
    reb_a = pre[pre.rebound == 1].groupby("opp").size() / gp
    # The pregame story published 11.1 and 2.1 for Dallas. Re-running its unchanged generator on the Nov. 15 data gives 11.0 and 2.0:
    # the NHL revised some earlier play-by-play. Buffalo's own numbers didn't move. This story uses the current data and says so.
    PUB_CLOSE_A, PUB_REB_A = 11.1, 2.1
    assert abs(close_a[THEM] - PUB_CLOSE_A) < 0.15 and abs(reb_a[THEM] - PUB_REB_A) < 0.15
    close_rank = int(close_a.rank(method="min").loc[THEM])
    reb_rank = int(reb_a.rank(method="min").loc[THEM])
    n_close, n_reb = int((f.dist < 20).sum()), int((f.rebound == 1).sum())
    n_close_a, n_reb_a = int((a.dist < 20).sum()), int((a.rebound == 1).sum())
    xg_close = f[f.dist < 20].xg.sum()
    # how often a team gets no rebound shots at all in a game (this season, through PRE)
    tg = pd.concat([keep[(keep.season == SEASON) & (keep.game_date <= PRE)].assign(team=keep.home),
                    keep[(keep.season == SEASON) & (keep.game_date <= PRE)].assign(team=keep.away)])[["game_id", "team"]]
    rb = pre[pre.rebound == 1].groupby(["game_id", "team"]).size()
    tg["reb"] = [rb.get((i, t), 0) for i, t in zip(tg.game_id, tg.team)]
    zero_reb = float((tg.reb == 0).mean())

    # by strength
    pp_f, ev_f = f[f.strength.isin(PP)], f[f.strength == "5v5"]
    ev_a = a[a.strength == "5v5"]
    pp_a = a[a.strength.isin(PP)]
    assert set(f.strength) <= {"5v5", "5v4", "4v3", "4v4", "4v5", "6v5"}

    # trailing: Buffalo's chances while down
    gs = allg.copy()
    gs["them_g"] = ((gs.team == THEM) & (gs.goal == 1)).cumsum().shift(fill_value=0)
    gs = gs[(gs.unblocked == 1) & (gs.empty_net_against == 0)]
    tied = gs[gs.them_g == 0]
    tf, ta = tied[tied.team == US].xg.sum(), tied[tied.team == THEM].xg.sum()
    n_tf, n_ta = int((tied.team == US).sum()), int((tied.team == THEM).sum())
    pulled = f[f.strength == "6v5"]

    # replays: each shot goes in or misses at its own chance, exactly (Poisson-binomial)
    pf, pa = pmf(f.xg.values), pmf(a.xg.values)
    joint = np.outer(pf, pa)
    p_win, p_tie = np.tril(joint, -1).sum(), np.trace(joint)
    p_loss = 1 - p_win - p_tie
    p_shutout = pf[0]

    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    assert len(gk) == 2
    ours, theirs = gk[gk.opp == US].iloc[0], gk[gk.opp == THEM].iloc[0]
    assert int(ours.goalie_id) == LYON and int(theirs.goalie_id) == OETTINGER
    lyon_games = s[(s.goalie_id == LYON) & (s.season == SEASON)].game_id.nunique()
    assert lyon_games == 2
    # every goalie-game this season: where Oettinger's night ranks
    gg = s[unb & (s.season == SEASON)].groupby(["game_id", "goalie_id"]).agg(xga=("xg", "sum"), ga=("goal", "sum"))
    gg["saved"] = gg.xga - gg.ga
    n_gg = len(gg)
    oet_rank = int((gg.saved > theirs.saved).sum()) + 1

    # Buffalo shutouts this season
    sab = keep.merge(query("SELECT game_id, home_score, away_score FROM raw_nhl_games"), on="game_id")
    sab = sab[(sab.season == SEASON) & ((sab.home == US) | (sab.away == US))]
    sab["buf_g"] = np.where(sab.home == US, sab.home_score, sab.away_score)
    n_sab, n_blank = len(sab), int((sab.buf_g == 0).sum())
    blank_opps = set(np.where(sab[sab.buf_g == 0].home == US, sab[sab.buf_g == 0].away, sab[sab.buf_g == 0].home))
    lyon_prev = s[unb & (s.goalie_id == LYON) & (s.season == SEASON) & (s.game_id != G)]
    assert lyon_prev.game_id.nunique() == 1
    lyon_prev_saved = lyon_prev.xg.sum() - lyon_prev.goal.sum()

    # the bounce-back: Dallas won after its 8-3 loss; the pregame story's rate
    bounce = 0.46

    # ledger record to date
    pr = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    m = pr.merge(gr, left_on="id", right_on="prediction_id")
    m = m[pd.to_datetime(m.graded_at_utc) <= pd.Timestamp(as_of, tz="UTC") + pd.Timedelta(days=2)]
    hits = int((((m.probability >= 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))).sum())
    nhl = m[m.sport == "NHL"]
    nhl_hits = int((((nhl.probability >= 0.5) & (nhl.outcome == 1)) | ((nhl.probability < 0.5) & (nhl.outcome == 0))).sum())
    row = m[m.id == PRED_ID].iloc[0]
    assert row.outcome == 0
    brier = float(row.brier)

    # extra context the reviews asked for
    W = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    TEAM_NAMES = {"WPG": "Winnipeg"}
    dal_prev = query(f"SELECT * FROM raw_nhl_games WHERE season = {SEASON} AND (home = '{THEM}' OR away = '{THEM}') AND game_date < '{AS_OF}' ORDER BY game_date DESC LIMIT 1").iloc[0]
    assert dal_prev.home == THEM and dal_prev.home_score - dal_prev.away_score == -5 and dal_prev.game_date == "2026-11-12"
    xga_pg = s[unb & (s.season == SEASON) & s.game_id.isin(set(keep[keep.game_date <= PRE].game_id))].groupby("opp").xg.sum() / gp
    xga_rank = int(xga_pg.rank(ascending=False, method="min").loc[US])
    n_missed = len(f) - int(f.on_goal.sum())
    oct8 = keep[(keep.season == SEASON) & (keep.game_date < AS_OF) & (((keep.home == US) & (keep.away == THEM)) | ((keep.home == THEM) & (keep.away == US)))]
    assert len(oct8) == 1 and oct8.game_date.iloc[0] == "2026-10-08"
    oct8_g = s[(s.game_id == oct8.game_id.iloc[0]) & unb & (s.opp == THEM)]
    oct8_oet = set(oct8_g.goalie_id.dropna().astype(int)) == {OETTINGER}
    o8 = query(f"SELECT home_score, away_score FROM raw_nhl_games WHERE game_id = {oct8.game_id.iloc[0]}").iloc[0]
    o8_buf, o8_dal = oct8_g.xg.sum(), s[(s.game_id == oct8.game_id.iloc[0]) & unb & (s.team == THEM)].xg.sum()
    assert o8_buf > o8_dal and int(o8.home_score) == 0
    oct8_sc = f"{int(o8.away_score)}-{int(o8.home_score)}"
    prior = s[unb & (s.season == SEASON) & (s.team == US) & (s.game_id != G)]
    buf_avg = prior.xg.sum() / prior.game_id.nunique()
    allt = s[unb & (s.season == SEASON)]
    tg_all = pd.concat([keep[keep.season == SEASON].assign(team=keep.home), keep[keep.season == SEASON].assign(team=keep.away)])[["game_id", "team"]]
    cl = allt[allt.dist < 20].groupby(["game_id", "team"]).size()
    tg_all["close"] = [cl.get((i, t), 0) for i, t in zip(tg_all.game_id, tg_all.team)]
    low_close = float((tg_all.close <= n_close).mean())
    buf_low = int(((tg_all.team == US) & (tg_all.close <= n_close)).sum())
    p3_pp = f[(f.period == 3) & f.strength.isin(PP)].xg.sum()
    nj_close = close_a.sort_values().index[1]
    close_gap = close_a.sort_values().iloc[1] - close_a[THEM]

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    end = 60.5
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, DAL_GREEN, "Stars")]:
        x = g[g.team == team]
        cum = x.xg.cumsum()
        ax.step(np.r_[0, x.t / 60, end], np.r_[0, cum, cum.iloc[-1]], where="post", color=col, lw=2.4, label=lab,
                ls="-" if team == US else (0, (4, 1.5)))
        gx = x.goal == 1
        ax.scatter(x.t[gx] / 60, cum[gx], s=70, color=INK, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    for x0, lab in ((10, "1st"), (30, "2nd"), (50, "3rd")):
        ax.text(x0, 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=9, color=MUTED)
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Dallas pulled ahead in the 2nd; Buffalo's late push came up empty",
           f"Sabres at Stars, Nov. 14: Dallas's chances were worth {a.xg.sum():.1f} goals, Buffalo's {f.xg.sum():.1f}. Stars won {them_sc}-{us_sc}. Black dots = Dallas's goals.",
           f"Shots that weren't blocked, empty net excluded: Sabres {len(f)}, Stars {len(a)}. Nov. 14, 2026, in Dallas.")
    fig.savefig(OUT / "sabres-dal-post-flow.png"); plt.close(fig)

    # ---- chart 2: shots from in close and rebounds, Buffalo at Dallas vs season numbers
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4.6), dpi=200)
    for ax, (lab, own, allow, sat) in zip(axs, [("Shots from within 20 feet", close_f[US], close_a[THEM], n_close),
                                                 ("Rebound shots (within 3 seconds of another shot)", reb_f[US], reb_a[THEM], n_reb)]):
        vals = [own, allow, sat]
        cols = ["#C9CDD4", "#7A8699", BLUE]
        ax.bar(range(3), vals, color=cols, width=0.62, zorder=2)
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals) * 0.02, f"{v:.1f}" if i < 2 else f"{int(v)}", ha="center", va="bottom", fontsize=10, color=INK)
        ax.set_xticks(range(3), ["Sabres'\nusual game", "Stars usually\nallow", "Sabres at Dallas,\nNov. 14"], fontsize=9)
        ax.set_title(lab, fontsize=10.5, color=INK, loc="left")
        ax.set_ylim(0, max(vals) * 1.2); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Dallas kept Buffalo away from the net, as it usually does",
           "Sabres' shots from close in and on rebounds at Dallas (blocked shots not counted), against their usual game and what Dallas usually allows.",
           f"Usual = 2026-27 games through Nov. 12 (Sabres {gp[US]}, Stars {gp[THEM]}), NHL data as of Nov. 15. Rebound = within 3 seconds of a same-team shot. Empty net excluded.")
    fig.savefig(OUT / "sabres-dal-post-close.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {int(r.period)} | {clock(r.t)} | Stars | {r.who} | {r.shot_type} shot from {r.dist:.0f} ft"
        f"{', on a rebound' if r.rebound else ''}{', on the power play' if r.strength in PP else ''} | {r.xg:.0%} | Stars {i + 1}-0 |"
        for i, r in enumerate(gl.itertuples()))
    nj_name = {"NJD": "New Jersey"}.get(nj_close, nj_close)
    md = f"""# Stars {them_sc}, Sabres {us_sc}: Dallas kept Buffalo away from the net, and Oettinger stopped the rest

**Dallas did to Buffalo what it does to most teams: it kept the Sabres away from the front of the net. Buffalo got {n_close} shots from within 20 feet and no
rebound shots at all. Even so, its chances were worth {f.xg.sum():.1f} goals, and a team with chances like that gets shut out only about {p_shutout:.0%} of the time.
Jake Oettinger made sure this was one of those nights, stopping all {int(theirs.on)} shots that reached him. Dallas's own chances were worth {a.xg.sum():.1f} goals. Our pregame call gave Buffalo a
{PRED_P:.0%} chance, making Dallas the likelier winner. That call was right.**

*One game, Nov. 14, in Dallas. [Our pregame story](sabres-stars-pregame-nov-14.html).*

It's the {'first' if n_blank == 1 else ordn(n_blank)} time in {n_sab} games this season the Sabres haven't scored{', both times against Dallas' if blank_opps == {THEM} and n_blank == 2 else ''}{' with Oettinger in net' if oct8_oet and blank_opps == {THEM} else ''}.
On Oct. 8 in Buffalo, as our pregame story noted, the Sabres actually had the better chances and still lost {oct8_sc}.

![Game flow](sabres-dal-post-flow.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Benn's rebound from {first.dist:.0f} feet had a {first.xg:.0%} chance;
Johnston's {second.shot_type} shot from {second.dist:.0f} feet, about {second.xg:.0%}. Add those chances up over a game and you get what a team's chances were worth in goals:
all {len(a)} of Dallas's shots were worth {a.xg.sum():.1f}, and Dallas scored {them_sc}. Buffalo's {len(f)} were worth {f.xg.sum():.1f}, and Buffalo scored {us_sc}. The shot locations
come from the NHL's own play-by-play. Each shot's chance comes from our model, built on past seasons and tested on a season it hadn't seen. (The full
explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

## Dallas took over in the second period

| Period | Sabres chances (worth this many goals) | Stars chances (worth this many goals) |
|---|---|---|
| 1st | {per.loc[1, US]:.1f} ({nper.loc[1, US]} shots) | {per.loc[1, THEM]:.1f} ({nper.loc[1, THEM]} shots) |
| 2nd | {per.loc[2, US]:.1f} ({nper.loc[2, US]} shots) | {per.loc[2, THEM]:.1f} ({nper.loc[2, THEM]} shots) |
| 3rd | {per.loc[3, US]:.1f} ({nper.loc[3, US]} shots) | {per.loc[3, THEM]:.1f} ({nper.loc[3, THEM]} shots) |
| Game | {f.xg.sum():.1f} ({len(f)} shots) | {a.xg.sum():.1f} ({len(a)} shots) |

"Shots" here means every shot that wasn't blocked, including ones that missed the net: {int(f.on_goal.sum())} of Buffalo's {len(f)} reached Oettinger, and the other
{n_missed} missed. There were no empty-net shots or goals.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

The first period was close. Dallas took over the second, with chances worth {per.loc[2, THEM]:.1f} goals to Buffalo's {per.loc[2, US]:.1f}, and Jamie Benn scored on a rebound
late in it. Buffalo, trailing, had more of the chances in the third ({per.loc[3, US]:.1f} to {per.loc[3, THEM]:.1f}), with {p3_pp:.1f} of Buffalo's {per.loc[3, US]:.1f} coming on the power play; {len(pulled)} of its shots
came with its goalie pulled for an extra skater. Wyatt Johnston's power-play goal came with {clock(1200 - int(second.t) % 1200)} left.

Replay the game over and over, with each shot going in or missing at its own chance, and Buffalo wins {p_win:.0%} of the time, Dallas {p_loss:.0%}, and it's tied after
regulation the other {p_tie:.0%}. Buffalo goes scoreless in only about {p_shutout:.0%} of those replays. Saturday went like one of those few.

## What we said to watch: Buffalo rarely got to the net

![In close](sabres-dal-post-close.png)

Our pregame story said Dallas allows the fewest rebound shots in the NHL and the 2nd-fewest from close in, and that if Buffalo's chances came from the point and
the outside, to expect a low-scoring night for the Sabres. Buffalo had {n_close} shots from within 20 feet, against the {close_f[US]:.1f} it gets in a usual game and the
{close_a[THEM]:.1f} Dallas usually allows. It had **no rebound shots**; it usually gets {reb_f[US]:.1f}, and Dallas usually allows {reb_a[THEM]:.1f}. Going a whole game without a rebound shot is rare:
it's happened in {zero_reb:.0%} of NHL team games this season. Dallas got to the net more: {n_close_a} shots from within 20 feet and {n_reb_a} rebounds, one of which was Benn's goal.

(Dallas's numbers here are slightly different from the pregame story's {PUB_CLOSE_A} and {PUB_REB_A}: the NHL has since corrected some of its records from earlier games.
On the corrected records, Dallas allows the fewest rebound shots and, by a hair over {nj_name}, the fewest from close in.)

Dallas's defense explains part of the shutout, not all of it. {W[n_close].capitalize() if n_close < 11 else n_close} or fewer shots from close in isn't rare: it's happened in {low_close:.0%} of NHL team games this season, and {buf_low} of
Buffalo's {n_sab}. Buffalo's chances were still worth {f.xg.sum():.1f} goals, against about {buf_avg:.1f} in its other games. The bigger reason it scored none is in goal.


## In goal

[Jake Oettinger](../cards/jake-oettinger.html) stopped all {int(theirs.on)} shots on goal. Buffalo's chances were worth {theirs.xga:.1f} goals, so he saved {theirs.saved:.1f} goals more than
an average goalie would have: the {ordn(oet_rank)}-best goalie game in the NHL this season, out of {n_gg:,}.

[Alex Lyon](../cards/alex-lyon.html) started his second straight game. He faced Dallas shots worth {ours.xga:.1f} goals and allowed {int(ours.ga)}, {ours.saved:.1f} goals fewer than an
average goalie would have. Buffalo lost with a good night in its own net.

## At full strength Saturday, Dallas had most of the chances

More than half of Buffalo's chances came on the power play: {len(pp_f)} shots worth {pp_f.xg.sum():.1f} goals. At five-on-five it had {len(ev_f)}, worth {ev_f.xg.sum():.1f}.
Dallas had {len(ev_a)} at five-on-five, worth {ev_a.xg.sum():.1f}. So at full strength, Dallas had about {ev_a.xg.sum() / (ev_a.xg.sum() + ev_f.xg.sum()):.0%} of the chances.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html), which made Dallas the likelier winner. Dallas won, so the call was right.
On our scorecard, where 0 is perfect and a coin-flip guess scores 0.25, this call scores {brier:.2f}. We've now got {hits} of our {len(m)} graded calls right, and {nhl_hits} of {len(nhl)}
on Sabres games.

The model expected about {PRE_XG_THEM:.1f} goals for Dallas and {PRE_XG_US:.1f} for Buffalo. The chances came out {a.xg.sum():.1f} and {f.xg.sum():.1f}: Dallas about what it expected,
Buffalo a little less.

**The bounce-back.** Dallas came in off an {dal_prev.away_score}-{dal_prev.home_score} home loss to {TEAM_NAMES[dal_prev.away]} on Thursday, and our pregame story found that teams coming off a loss by four or more have won
{bounce:.0%} of their next game, a little less often than usual. Dallas won this one; one game doesn't change that number.

## What it means for Buffalo

- **The zero was unlikely.** Chances like Saturday's leave Buffalo scoreless only about {p_shutout:.0%} of the time. The shutout says more about Oettinger than about Buffalo's offense.
- **Keep an eye on Buffalo's own end.** That was our pregame story's bigger concern: the Sabres allow the {ordn(xga_rank)}-most chances in the league. Saturday,
  Dallas's chances were worth {a.xg.sum():.1f} goals, and a good night from Lyon held it to {them_sc}.
- **Lyon has held up.** After Buffalo's own 8-3 loss to Tampa Bay, he was {abs(lyon_prev_saved):.1f} goals {'worse' if lyon_prev_saved < 0 else 'better'} than average in the
  overtime loss at Chicago and {ours.saved:.1f} better Saturday. Two games is a tiny sample.

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal); DAL {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal).
  By period: BUF {', '.join(f'{per.loc[p, US]:.2f}' for p in (1, 2, 3))}; DAL {', '.join(f'{per.loc[p, THEM]:.2f}' for p in (1, 2, 3))}. While 0-0: BUF {tf:.2f} ({n_tf}), DAL {ta:.2f} ({n_ta}).
  BUF xGF per game in its other {prior.game_id.nunique()} games this season: {buf_avg:.2f}.
- Strength: BUF 5v5 {ev_f.xg.sum():.2f} ({len(ev_f)}), power play (5v4, 4v3) {pp_f.xg.sum():.2f} ({len(pp_f)}; {p3_pp:.2f} in the 3rd), 6v5 {pulled.xg.sum():.2f} ({len(pulled)}); DAL 5v5 {ev_a.xg.sum():.2f} ({len(ev_a)}),
  power play {pp_a.xg.sum():.2f} ({len(pp_a)}). 5v5 xG share DAL {ev_a.xg.sum() / (ev_a.xg.sum() + ev_f.xg.sum()):.3f}. Penalty counts not shown (attribution unverified).
- Data revision: the pregame story (games through {PRE}) published DAL close-in allowed {PUB_CLOSE_A} and rebounds allowed {PUB_REB_A} a game. Re-running its
  unchanged generator on the Nov. 15 NHL data gives {close_a[THEM]:.2f} and {reb_a[THEM]:.2f} ({nj_close} close-in allowed {close_a[THEM] + close_gap:.2f}); BUF's numbers are unchanged.
  The pregame story stays as published.
- Close = within 20 ft (strictly under), rebound = within 3 s of a same-team unblocked attempt. Season rates per game through {PRE}: BUF close {close_f[US]:.2f}, rebounds {reb_f[US]:.2f};
  DAL allows close {close_a[THEM]:.2f}, rebounds {reb_a[THEM]:.2f}. BUF close-in xG Saturday {xg_close:.2f}. Team-games with zero rebound shots, 2026-27 through {PRE}: {zero_reb:.3f} (n {len(tg)}).
  Team-games with {n_close} or fewer close-in shots, 2026-27 through {AS_OF}: {low_close:.3f} (n {len(tg_all)}); BUF {buf_low} of {n_sab}.
- Replays: exact Poisson-binomial over all unblocked shots (each an independent Bernoulli with p = xG). BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f};
  P(BUF 0 goals) {p_shutout:.3f}.
- GSAx = xG on unblocked shots faced minus goals allowed. Oettinger {theirs.saved:+.2f} ({int(theirs.on)} SOG), rank {oet_rank} of {n_gg:,} goalie-games this season (any minutes);
  Lyon {ours.saved:+.2f} ({int(ours.on)} SOG), his 2nd game this season; {lyon_prev_saved:+.2f} at Chicago.
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0 (DAL won in regulation; any result counts), Brier {brier:.4f}. Model nhl-game-v0.1; its {PRE_XG_US} / {PRE_XG_THEM} are expected goals for 60 minutes.
"""
    (OUT / "2026-11-15-sabres-dal.md").write_text(md)
    (OUT / "2026-11-15-sabres-dal.hero.json").write_text(json.dumps({
        "label": "Scoring chances, worth this many goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Stars"]],
        "note": f"Final: Stars {them_sc}, Sabres {us_sc}. Dallas kept Buffalo away from the net, and Jake Oettinger stopped all {int(theirs.on)} shots that reached him.",
        "explainer": {
            "kicker": "Getting to the net", "title": f"Buffalo got {n_close} shots from in close, and no rebounds.",
            "text": "Sabres' shots from within 20 feet:",
            "fmt": "num",
            "bars": [["Sabres' usual game (through Nov. 12)", round(float(close_f[US]), 1)], ["Sabres at Dallas, Nov. 14", n_close]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
