"""Sabres post-game: BUF at PHI, Nov 17, 2026 (Philadelphia 4, Buffalo 3). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-18-sabres-phi.md, two PNGs and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF so the published story doesn't change. Ledger P0018 graded by src/ledger/grade_p0018.py (separate).
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
G, SEASON, US, THEM = 2026020337, 20262027, "BUF", "PHI"
AS_OF = "2026-11-17"
PRE = "2026-11-15"   # the pregame story's data ran through this date
PRED_ID, PRED_P = "P0018", 0.48
PRE_XG_US, PRE_XG_THEM = 3.17, 3.23   # pregame expected goals, from P0018's notes in ledger/predictions.csv
PHI_ORANGE = "#F74902"
LYON, WOLL = 8479312, 8479361
PP = ("5v4", "5v3", "4v3")
SH = ("4v5", "3v5", "3v4")
NAMES = {"WSH": "Washington", "FLA": "Florida", "TBL": "Tampa Bay", "NYR": "the Rangers"}


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
    assert (us_sc, them_sc) == (3, 4)

    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    assert int(allg[allg.team == US].goal.sum()) == us_sc and int(allg[allg.team == THEM].goal.sum()) == them_sc
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    en = allg[(allg.unblocked == 1) & (allg.empty_net_against == 1)]
    assert set(en.team) <= {THEM} and en.goal.sum() == 0      # Philadelphia's late empty-net tries, no goals
    f, a = g[g.team == US], g[g.team == THEM]
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    nper = g.groupby(["period", "team"]).size().unstack().fillna(0).astype(int)
    assert set(per.index) == {1, 2, 3}

    # goals, with the running score
    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    gl["us_run"] = (gl.team == US).cumsum()
    gl["them_run"] = (gl.team == THEM).cumsum()
    assert len(gl) == 7
    winner = gl.iloc[-1]
    tyer = gl.iloc[-2]
    assert winner.team == THEM and tyer.team == US and tyer.us_run == 3 and tyer.them_run == 3
    gap_s = int(winner.t - tyer.t)
    # how rare a goal from a shot like the winner is: share of this season's unblocked shots with a chance at or below it
    season_unb = s[unb & (s.season == SEASON)]
    rare = float((season_unb.xg <= winner.xg).mean())
    rare_goal = float(season_unb[season_unb.xg <= winner.xg].goal.mean())
    marg = gl.us_run - gl.them_run
    prev = marg.shift(fill_value=0)
    us_took = int(((marg > 0) & (prev <= 0)).sum())
    them_took = int(((marg < 0) & (prev >= 0)).sum())
    ties = int((marg == 0).sum())
    assert us_took == them_took == 2
    thompson = gl[gl.who == "Tage Thompson"].iloc[0]
    out_from_line = 89 - abs(winner.x)
    like = s[unb & (s.season == SEASON) & (s.angle >= 55) & s.dist.between(25, 35) & (s.rebound == 0) & (s.rush == 0)]
    like_rate = like.goal.mean()

    # by strength
    ev_f, ev_a = f[f.strength == "5v5"], a[a.strength == "5v5"]
    pp_f, pp_a = f[f.strength.isin(PP)], a[a.strength.isin(PP)]
    oth_f = f[~f.strength.isin(("5v5",) + PP)]
    oth_a = a[~a.strength.isin(("5v5",) + PP)]
    ev_share = ev_f.xg.sum() / (ev_f.xg.sum() + ev_a.xg.sum())
    pulled = f[f.strength == "6v5"]
    third_share_a = per.loc[3, THEM] / (per.loc[3, THEM] + per.loc[3, US])
    a3 = a[a.period == 3]; f3 = f[f.period == 3]
    a3_after, f3_after = a3[a3.t > winner.t], f3[f3.t > winner.t]
    assert a3_after.xg.sum() > a3[a3.t <= winner.t].xg.sum()     # most of PHI's 3rd came after the winner
    pp_after = a3_after[a3_after.strength.isin(PP)]

    # replays
    pf, pa = pmf(f.xg.values), pmf(a.xg.values)
    joint = np.outer(pf, pa)
    p_win, p_tie = np.tril(joint, -1).sum(), np.trace(joint)
    p_loss = 1 - p_win - p_tie

    # goalies
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    assert len(gk) == 2
    ours, theirs = gk[gk.opp == US].iloc[0], gk[gk.opp == THEM].iloc[0]
    assert int(ours.goalie_id) == LYON and int(theirs.goalie_id) == WOLL
    lyon_games = s[(s.goalie_id == LYON) & (s.season == SEASON)].game_id.nunique()
    lyon_season = s[unb & (s.goalie_id == LYON) & (s.season == SEASON)]
    lyon_saved = lyon_season.xg.sum() - lyon_season.goal.sum()
    woll_pre = s[unb & (s.goalie_id == WOLL) & (s.season == SEASON) & s.game_id.isin(set(keep[keep.game_date <= PRE].game_id))]
    woll_pre_saved = woll_pre.xg.sum() - woll_pre.goal.sum()
    PUB_WOLL = 4.5   # published in the pregame story; this season's rescale, now including Tuesday's games, gives a little less
    assert abs(woll_pre_saved - PUB_WOLL) < 0.15

    # finishing: the skid's four losses (pregame story) vs tonight
    sab = keep.merge(query("SELECT game_id, home_score, away_score, last_period_type FROM raw_nhl_games"), on="game_id")
    sab = sab[(sab.season == SEASON) & ((sab.home == US) | (sab.away == US))].sort_values("game_date")
    sab["buf_g"] = np.where(sab.home == US, sab.home_score, sab.away_score)
    sab["opp_g"] = np.where(sab.home == US, sab.away_score, sab.home_score)
    sab["won"] = sab.buf_g > sab.opp_g
    skid = 0
    for w in sab.won[::-1]:
        if w:
            break
        skid += 1
    skid_ids = sab.game_id.tail(skid)
    skid_ot = int(sab.tail(skid).last_period_type.isin(["OT", "SO"]).sum())
    prev4 = s[unb & s.game_id.isin(set(skid_ids) - {G}) & (s.team == US)]
    w_ = int((sab.won).sum()); l_ = int(((~sab.won) & ~sab.last_period_type.isin(["OT", "SO"])).sum())
    otl = int(((~sab.won) & sab.last_period_type.isin(["OT", "SO"])).sum())
    rec = f"{w_}-{l_}-{otl}"
    sch = query(f"SELECT game_date, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') "
                f"AND game_date > '{AS_OF}' ORDER BY game_date")
    road_left = 0
    for r in sch.itertuples():
        if r.away != US:
            break
        road_left += 1
    stops = [NAMES[x] for x in sch.home.iloc[:road_left]]
    nxt = sch.iloc[0]
    home_next = sch.iloc[road_left]

    # Philadelphia's recent form, as the pregame story's "watch"
    phi5 = s[unb & (s.season == SEASON) & ((s.team == THEM) | (s.opp == THEM))]
    phi_ids = sorted(set(phi5.game_id))
    pre5 = [i for i in phi_ids if i in set(keep[keep.game_date <= PRE].game_id)][-5:]
    x5 = phi5[phi5.game_id.isin(pre5)]
    phi5_share = x5[x5.team == THEM].xg.sum() / x5.xg.sum()
    assert abs(phi5_share - 0.566) < 0.006      # the pregame story's 57%
    tonight_share = a.xg.sum() / (a.xg.sum() + f.xg.sum())
    pre_ids = set(keep[(keep.season == SEASON) & (keep.game_date <= PRE)].game_id)
    xgf_pg = s[unb & s.game_id.isin(pre_ids)].groupby("team").xg.sum() / s[unb & s.game_id.isin(pre_ids)].groupby("team").game_id.nunique()
    phi_few = int(xgf_pg.rank(method="min").loc[THEM])
    assert phi_few == 5      # the pregame story's "5th-fewest"

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

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    end = 60.5
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, PHI_ORANGE, "Flyers")]:
        x = g[g.team == team]
        cum = x.xg.cumsum()
        ax.step(np.r_[0, x.t / 60, end], np.r_[0, cum, cum.iloc[-1]], where="post", color=col, lw=2.4, label=lab,
                ls="-" if team == US else (0, (4, 1.5)))
        gx = x.goal == 1
        ax.scatter(x.t[gx] / 60, cum[gx], s=70, color=col, zorder=4, edgecolor="white", lw=1.5)
    for v in (20, 40):
        ax.axvline(v, color="#D5D8DE", lw=1, ls="--")
    for x0, lab in ((10, "1st"), (30, "2nd"), (50, "3rd")):
        ax.text(x0, 0.02, lab, transform=ax.get_xaxis_transform(), ha="center", fontsize=9, color=MUTED)
    ax.annotate(f"Winner: {winner.who.split()[-1]}, {clock(winner.t)} of the 3rd,\na shot with about a {winner.xg:.0%} chance",
                (winner.t / 60, a[a.t <= winner.t].xg.sum()), xytext=(-150, 40), textcoords="offset points", fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"The winner had about a {winner.xg:.0%} chance; the Flyers had most late chances",
           f"Sabres at Flyers, Nov. 17: Philadelphia's chances were worth {a.xg.sum():.1f} goals, Buffalo's {f.xg.sum():.1f}. Flyers won {them_sc}-{us_sc}. Dots = goals.",
           f"Shots that weren't blocked, empty net excluded: Sabres {len(f)}, Flyers {len(a)}. Nov. 17, 2026, in Philadelphia.")
    fig.savefig(OUT / "sabres-phi-post-flow.png"); plt.close(fig)

    # ---- chart 2: chances by situation
    labs = ["Five-on-five", "Power play", "Everything else"]
    us_v = [ev_f.xg.sum(), pp_f.xg.sum(), oth_f.xg.sum()]
    th_v = [ev_a.xg.sum(), pp_a.xg.sum(), oth_a.xg.sum()]
    us_n = [len(ev_f), len(pp_f), len(oth_f)]
    th_n = [len(ev_a), len(pp_a), len(oth_a)]
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    xs = np.arange(3); w = 0.36
    ax.bar(xs - w / 2, us_v, w, color=BLUE, label="Sabres", zorder=2)
    ax.bar(xs + w / 2, th_v, w, color=PHI_ORANGE, label="Flyers", zorder=2)
    for i in range(3):
        ax.text(xs[i] - w / 2, us_v[i] + 0.03, f"{us_v[i]:.1f}\n({us_n[i]} shots)", ha="center", va="bottom", fontsize=9, color=INK)
        ax.text(xs[i] + w / 2, th_v[i] + 0.03, f"{th_v[i]:.1f}\n({th_n[i]} shots)", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xticks(xs, labs); ax.set_ylim(0, max(us_v + th_v) * 1.35)
    ax.set_ylabel("Goals the chances were worth")
    ax.legend(frameon=False, loc="upper right"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Even at five-on-five; Philadelphia's edge was the power play",
           "Sabres at Flyers, Nov. 17: what each side's chances were worth, by situation on the ice.",
           "Everything else = four-on-four, short-handed and extra-attacker shots. Shots that weren't blocked, empty net excluded.")
    fig.savefig(OUT / "sabres-phi-post-situations.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Flyers'} | {r.who} | {r.shot_type}{'' if r.shot_type == 'tip-in' else ' shot'} from {r.dist:.0f} ft"
        f"{', on a rebound' if r.rebound else ''}{', on the power play' if r.strength in PP else ''}{', four-on-four' if r.strength == '4v4' else ''}"
        f" | {r.xg:.0%} | Sabres {r.us_run}, Flyers {r.them_run} |"
        for r in gl.itertuples())
    W = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    md = f"""# Flyers {them_sc}, Sabres {us_sc}: Buffalo tied it in the third, and Philadelphia answered {gap_s} seconds later on a shot that almost never goes in

**Jiri Kulich tied the game 3-3 with {clock(1200 - int(tyer.t) % 1200)} left. {gap_s} seconds later, Christian Dvorak beat Alex Lyon with a {winner.dist:.0f}-foot wrist shot
that had about a {winner.xg:.0%} chance of going in, and the Flyers won {them_sc}-{us_sc}. The loss wasn't all bad luck: Philadelphia's chances were worth {a.xg.sum():.1f}
goals to Buffalo's {f.xg.sum():.1f}, most of the difference coming on the power play and in a lopsided third period. Our pregame call gave Buffalo a {PRED_P:.0%} chance,
a near toss-up that leaned Philadelphia. The Sabres have now lost {W[skid]} straight ({W[skid_ot]} in overtime).**

*One game, Nov. 17, in Philadelphia. [Our pregame story](sabres-flyers-pregame-nov-17.html).*

![Game flow](sabres-phi-post-flow.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Dvorak's winner, from {winner.dist:.0f} feet, had about a {winner.xg:.0%} chance;
Owen Tippett's tip-in from {gl.iloc[3].dist:.0f} feet, about {gl.iloc[3].xg:.0%}. Add those chances up over a game and you get what a team's chances were worth in goals: all
{len(a)} of Philadelphia's shots were worth {a.xg.sum():.1f}, and the Flyers scored {them_sc}. Buffalo's {len(f)} were worth {f.xg.sum():.1f}, and the Sabres scored {us_sc}. The shot
locations come from the NHL's own play-by-play. Each shot's chance comes from our model, built on past seasons and tested on a season it hadn't seen. (The full
explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

## The game, period by period

| Period | Sabres chances (worth this many goals) | Flyers chances (worth this many goals) |
|---|---|---|
| 1st | {per.loc[1, US]:.1f} ({nper.loc[1, US]} shots) | {per.loc[1, THEM]:.1f} ({nper.loc[1, THEM]} shots) |
| 2nd | {per.loc[2, US]:.1f} ({nper.loc[2, US]} shots) | {per.loc[2, THEM]:.1f} ({nper.loc[2, THEM]} shots) |
| 3rd | {per.loc[3, US]:.1f} ({nper.loc[3, US]} shots) | {per.loc[3, THEM]:.1f} ({nper.loc[3, THEM]} shots) |
| Game | {f.xg.sum():.1f} ({len(f)} shots) | {a.xg.sum():.1f} ({len(a)} shots) |

"Shots" here means every shot that wasn't blocked, including ones that missed the net: {int(f.on_goal.sum())} of Buffalo's {len(f)} reached Joseph Woll, and {int(a.on_goal.sum())} of
Philadelphia's {len(a)} reached Lyon. Philadelphia also had {len(en)} shots at an empty net late; neither went in, and they're not counted above.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

It was tied {W[ties]} times, and each team took the lead twice.

Buffalo had slightly more of the chances through two periods ({per.loc[[1, 2], US].sum():.1f} to {per.loc[[1, 2], THEM].sum():.1f}). The third belonged to Philadelphia: {nper.loc[3, THEM]} shots worth
{per.loc[3, THEM]:.1f} goals to Buffalo's {nper.loc[3, US]}, worth {per.loc[3, US]:.1f}. Philadelphia had about {third_share_a:.0%} of the third period's chances. Most of that came after the winning goal: {len(a3_after)} Flyers shots
worth {a3_after.xg.sum():.1f} ({len(pp_after)} of them on the power play, worth {pp_after.xg.sum():.1f}), while Buffalo, chasing the tie, managed {len(f3_after)} worth {f3_after.xg.sum():.1f}.

Replay the game over and over, with each shot going in or missing at its own chance, and Philadelphia wins {p_loss:.0%} of the time, Buffalo {p_win:.0%}, and it's tied after
regulation the other {p_tie:.0%}. So the Flyers deserved the edge, just not by much.

## The winner

Why only {winner.xg:.0%}? Dvorak shot from a sharp angle: about {out_from_line:.0f} feet out from the goal line and {abs(winner.y):.0f} feet to the side of the middle of the net, with no rebound and no
rush to help. Thompson's goal came from about the same distance, {thompson.dist:.0f} feet, but nearly straight on, which is why it rated {thompson.xg:.0%}. Shots from spots like Dvorak's this
season (25 to 35 feet out, at that kind of angle, no rebound or rush) have gone in {like_rate:.0%} of the time ({len(like):,} shots); our model, which also weighs the shot type,
put this one at about {winner.xg:.0%}.

## Where the chances came from

![By situation](sabres-phi-post-situations.png)

At five-on-five, it was about even, with Buffalo slightly ahead: {len(ev_f)} shots worth {ev_f.xg.sum():.1f} goals, to Philadelphia's {len(ev_a)} worth {ev_a.xg.sum():.1f}, about {ev_share:.0%} of the chances. The difference was the power
play: Philadelphia had {len(pp_a)} power-play shots worth {pp_a.xg.sum():.1f}, Buffalo {len(pp_f)} worth {pp_f.xg.sum():.1f}. (We don't count penalties yet.)

## In goal

[Alex Lyon](../cards/alex-lyon.html) faced chances worth {ours.xga:.1f} goals and allowed {int(ours.ga)}, {abs(ours.saved):.1f} {'more' if ours.saved < 0 else 'fewer'} than an average goalie would have. The winner was the least likely of the four. This was his {ordn(lyon_games)} game this season; across them he's {abs(lyon_saved):.1f} goals {'worse' if lyon_saved < 0 else 'better'} than average.

[Joseph Woll](../cards/joseph-woll.html) started for Philadelphia; our pregame story had him at {PUB_WOLL:.1f} goals better than an average goalie this season. Tonight he faced chances worth
{theirs.xga:.1f} and allowed {int(theirs.ga)}, about {abs(theirs.saved):.1f} {'more' if theirs.saved < 0 else 'fewer'} than average.

## What we said going in

- **Finishing.** Our pregame story said Buffalo's skid was mostly cold shooting: in the {skid - 1} losses before tonight, it scored {int(prev4.goal.sum())} goals on chances worth about
  {prev4.xg.sum():.1f}. Tonight Buffalo scored {us_sc} on chances worth {f.xg.sum():.1f}, a bit better than its chances for once (one game). The goals it allowed were the bigger
  problem: Philadelphia's chances were worth {a.xg.sum() - f.xg.sum():.1f} more than Buffalo's, and Lyon allowed {abs(ours.saved):.1f} more than an average goalie would have.
- **Philadelphia's recent games.** The Flyers had {phi5_share:.0%} of the chances in their five games before this one. Tonight they had {tonight_share:.0%}. That held.
- **Who started for Philadelphia.** Woll, the better of the Flyers' two goalies by our numbers. He was a little below average tonight.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html), which made Philadelphia the slightly likelier winner. Philadelphia won, so the call
leaned the right way. A call this close to 50-50 can only earn a little credit when it's right, and that's what it got
(it scores {brier:.2f} on our scorecard, where 0 is perfect and a coin flip scores 0.25). We've now got {hits} of our {len(m)} graded calls right, and {nhl_hits} of {len(nhl)} on Sabres games.

## What it means for Buffalo

- **{W[skid].capitalize()} straight losses, {rec} on the season.** The trip goes on: {', '.join(stops[:-1])} and {stops[-1]} before the Sabres are home against {NAMES.get(home_next.away, home_next.away)} on
  {pd.Timestamp(home_next.game_date).strftime('%b. %-d')}. Next up: at {NAMES[nxt.home]}, {pd.Timestamp(nxt.game_date).strftime('%A')}.
- **About even at five-on-five, behind on the power play.** Philadelphia came in creating the {ordn(phi_few)}-fewest chances in the league. Tonight it out-chanced Buffalo mainly on the
  power play ({pp_a.xg.sum():.1f} to {pp_f.xg.sum():.1f}).

## For the stat-heads

- Expected goals (xG): our gradient-boosted model on unblocked, non-empty-net shots, rescaled per season so league xG equals league goals
  (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} xG on {len(f)} unblocked shots ({int(f.on_goal.sum())} on goal); PHI {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal).
  By period: BUF {', '.join(f'{per.loc[p, US]:.2f}' for p in (1, 2, 3))}; PHI {', '.join(f'{per.loc[p, THEM]:.2f}' for p in (1, 2, 3))}. PHI empty-net attempts: {len(en)}, 0 goals.
- Strength: BUF 5v5 {ev_f.xg.sum():.2f} ({len(ev_f)}), PP {pp_f.xg.sum():.2f} ({len(pp_f)}), other {oth_f.xg.sum():.2f} ({len(oth_f)}; 6v5 {len(pulled)}); PHI 5v5 {ev_a.xg.sum():.2f} ({len(ev_a)}),
  PP {pp_a.xg.sum():.2f} ({len(pp_a)}), other {oth_a.xg.sum():.2f} ({len(oth_a)}). 5v5 xG share BUF {ev_share:.3f}. Penalty counts not shown (attribution unverified).
- Winner: xG {winner.xg:.4f}; x {winner.x:.0f}, y {winner.y:.0f}, angle {winner.angle:.0f} deg (Thompson {thompson.angle:.0f} deg). Similar shots (angle 55+, 25-35 ft, no rebound/rush), 2026-27: {like.goal.sum()} of {len(like)}.
- Winner rarity: Unblocked non-empty-net shots in 2026-27 through {AS_OF} with xG at or below it: {rare:.3f} of all; their goal rate {rare_goal:.4f}.
- Replays: exact Poisson-binomial over all unblocked non-empty-net shots. BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx = xG on unblocked shots faced minus goals allowed. Lyon {ours.saved:+.2f} ({int(ours.on)} SOG; season {lyon_saved:+.2f} over {lyon_games} games); Woll {theirs.saved:+.2f} ({int(theirs.on)} SOG;
  {woll_pre_saved:+.2f} through {PRE} on today's season rescale; the pregame story published {PUB_WOLL:+.1f} on the rescale as of {PRE}).
- Skid finishing: BUF in the {skid - 1} losses before tonight, {int(prev4.goal.sum())} goals on {prev4.xg.sum():.2f} xG. PHI xG share, 5 games before tonight: {phi5_share:.3f}; tonight {tonight_share:.3f}.
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0 (PHI won in regulation; any result counts), Brier {brier:.4f}. Model nhl-game-v0.1; its {PRE_XG_US} / {PRE_XG_THEM} are expected goals for 60 minutes.
"""
    (OUT / "2026-11-18-sabres-phi.md").write_text(md)
    (OUT / "2026-11-18-sabres-phi.hero.json").write_text(json.dumps({
        "label": "Scoring chances, worth this many goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Flyers"]],
        "note": f"Final: Flyers {them_sc}, Sabres {us_sc}. Buffalo tied it with {clock(1200 - int(tyer.t) % 1200)} left; Dvorak won it {gap_s} seconds later on a shot with about a {winner.xg:.0%} chance.",
        "explainer": {
            "kicker": "Where the chances came from", "title": "Even at five-on-five; Philadelphia's edge was the power play.",
            "text": "Who had the better chances, and by how many goals:",
            "fmt": "num",
            "bars": [["Five-on-five: Sabres ahead by", round(float(ev_f.xg.sum() - ev_a.xg.sum()), 1)], ["Power play: Flyers ahead by", round(float(pp_a.xg.sum() - pp_f.xg.sum()), 1)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
