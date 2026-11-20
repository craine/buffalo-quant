"""Sabres post-game: BUF at WSH, Nov 19, 2026 (Buffalo 6, Washington 3). Every number computed here from clean_nhl_shots_xg / raw_nhl_*.

Writes reports/2026-11-20-sabres-wsh.md, two PNGs and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF (late games that weren't final at publish are listed in src/reports/pins.py).
Ledger P0019 graded by src/ledger/grade_p0019.py (separate).
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
G, SEASON, US, THEM = 2026020351, 20262027, "BUF", "WSH"
AS_OF = "2026-11-19"
PRED_ID, PRED_P = "P0019", 0.42
RED_W = "#C8102E"
UPL, LTHOMPSON, LINDGREN = 8480045, 8480313, 8479292
TUCH, BENSON, TTHOMPSON = 8477949, 8484145, 8479420
PP = ("5v4", "5v3", "4v3")
NAMES = {"FLA": "Florida", "TBL": "Tampa Bay", "NYR": "the Rangers"}
W = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


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
    keep = drop_late(query(f"SELECT game_id, season, game_date, home, away FROM raw_nhl_games WHERE game_date <= '{as_of}'"), as_of)
    s = s[s.game_id.isin(set(keep.game_id))].copy()
    allg_season = s[(s.unblocked == 1) & (s.goal == 1) & (s.season == SEASON)]
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    cur = u[u.season == SEASON]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    assert gm.home == THEM and gm.away == US and gm.game_state in ("OFF", "FINAL") and gm.last_period_type == "REG"
    us_sc, them_sc = int(gm.away_score), int(gm.home_score)
    assert (us_sc, them_sc) == (6, 3)

    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    assert int(allg[allg.team == US].goal.sum()) == us_sc and int(allg[allg.team == THEM].goal.sum()) == them_sc
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    en = allg[(allg.unblocked == 1) & (allg.empty_net_against == 1)]
    en_goals = int(en[en.team == US].goal.sum())
    assert en_goals == 1
    f, a = g[g.team == US], g[g.team == THEM]
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    nper = g.groupby(["period", "team"]).size().unstack().fillna(0).astype(int)
    gper = g.groupby(["period", "team"]).goal.sum().unstack().fillna(0).astype(int)
    assert set(per.index) == {1, 2, 3}

    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    gl["us_run"] = (gl.team == US).cumsum()
    gl["them_run"] = (gl.team == THEM).cumsum()
    assert len(gl) == 9

    # replays
    pf, pa = pmf(f.xg.values), pmf(a.xg.values)
    joint = np.outer(pf, pa)
    p_win, p_tie = float(np.tril(joint, -1).sum()), float(np.trace(joint))
    p_loss = 1 - p_win - p_tie
    assert p_win < 0.2

    # finishing tonight vs the season
    gd = cur.groupby(["game_id", "team"]).agg(gf=("goal", "sum"), x=("xg", "sum"))
    gd["d"] = gd.gf - gd.x
    bd = gd.xs(US, level="team")
    fin_rank, n_bg = int(bd.d.rank(ascending=False, method="min").loc[G]), len(bd)
    assert fin_rank == 2
    first_g, first_x = int(gper.loc[1, US]), float(per.loc[1, US])

    # goalies
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum"), t0=("t", "min"), t1=("t", "max")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    ours = gk[gk.opp == US].iloc[0]
    assert int(ours.goalie_id) == UPL
    lt = gk[gk.goalie_id == LTHOMPSON].iloc[0]
    li = gk[gk.goalie_id == LINDGREN].iloc[0]
    assert int(lt.ga) == 3 and int(lt.on) == 5 and lt.t1 < li.t0
    pulled_at = int(lt.t1)            # Thompson's last shot faced was Buffalo's third goal
    assert gl[(gl.team == US)].iloc[2].t == pulled_at
    upl_season = cur[cur.goalie_id == UPL]
    upl_gp, upl_sv = upl_season.game_id.nunique(), float(upl_season.xg.sum() - upl_season.goal.sum())

    # players
    ben_goal = gl[gl.shooter_id == BENSON].iloc[0]
    ben_prev = allg_season[(allg_season.shooter_id == BENSON) & (allg_season.empty_net_against == 0) & (allg_season.game_id != G)]
    assert len(ben_prev) == 1
    ben_prev_date = keep.set_index("game_id").game_date.loc[int(ben_prev.game_id.iloc[0])]
    ben_all = int((allg_season.shooter_id == BENSON).sum())
    assert ben_all == 3 and allg_season[(allg_season.shooter_id == BENSON) & (allg_season.game_id != G)].game_id.nunique() == 2
    ben_g = int(cur[cur.shooter_id == BENSON].goal.sum()); ben_x = float(cur[cur.shooter_id == BENSON].xg.sum())
    goals_all = allg_season.groupby("shooter_id").size()
    tt_g, tt_rank = int(goals_all[TTHOMPSON]), int(goals_all.rank(ascending=False, method="min")[TTHOMPSON])
    tt_tied = int((goals_all == goals_all[TTHOMPSON]).sum()) > 1
    tt_goal = gl[gl.shooter_id == TTHOMPSON].iloc[0]
    tuch_goal = gl[gl.shooter_id == TUCH].iloc[0]
    tuch_g = int(goals_all[TUCH])
    quinn = gl[gl.who == "Jack Quinn"]
    assert len(quinn) == 2 and quinn.empty_net_against.iloc[-1] == 1

    # special teams tonight, and Washington's power play coming in
    pp_f, pp_a = f[f.strength.isin(PP)], a[a.strength.isin(PP)]
    ev_f, ev_a = f[f.strength == "5v5"], a[a.strength == "5v5"]
    pre = keep[(keep.season == SEASON) & (keep.game_date < as_of)]
    pre_u = cur[cur.game_id.isin(set(pre.game_id))]
    gp_pre = pd.concat([pre.home, pre.away]).value_counts()
    wpp_pre = float(pre_u[pre_u.strength.isin(PP) & (pre_u.team == THEM)].xg.sum() / gp_pre[THEM])
    assert abs(wpp_pre - 0.52) < 0.01        # the preview's 0.52

    # skid that ended, record, schedule
    sab = keep.merge(query("SELECT game_id, home_score, away_score, last_period_type FROM raw_nhl_games"), on="game_id")
    sab = sab[(sab.season == SEASON) & ((sab.home == US) | (sab.away == US))].sort_values("game_date")
    sab["won"] = np.where(sab.home == US, sab.home_score > sab.away_score, sab.away_score > sab.home_score)
    prior = sab[sab.game_id != G]
    skid = 0
    for w_ in prior.won[::-1]:
        if w_: break
        skid += 1
    assert skid == 5
    skid_u = cur[cur.game_id.isin(set(prior.game_id.tail(skid)))]
    sk_gf, sk_xf = int(skid_u[skid_u.team == US].goal.sum()), float(skid_u[skid_u.team == US].xg.sum())
    ot = sab.last_period_type.isin(["OT", "SO"])
    rec = f"{int(sab.won.sum())}-{int((~sab.won & ~ot).sum())}-{int((~sab.won & ot).sum())}"
    sch = query(f"SELECT game_date, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') "
                f"AND game_date > '{as_of}' ORDER BY game_date LIMIT 4")
    assert list(sch.home[:2]) == ["FLA", "TBL"] and sch.home.iloc[2] == US

    # ledger record
    pr = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    m = pr.merge(gr, left_on="id", right_on="prediction_id")
    m = m[pd.to_datetime(m.graded_at_utc) <= pd.Timestamp(as_of, tz="UTC") + pd.Timedelta(days=2)]
    hit = ((m.probability >= 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))
    nhl = m.sport == "NHL"
    row = m[m.id == PRED_ID].iloc[0]
    assert row.outcome == 1
    brier = float(row.brier)

    # ---- chart 1: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    end = 60.5
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, RED_W, "Capitals")]:
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
    ax.annotate(f"Buffalo: {first_g} goals in the 1st\non chances worth {first_x:.1f}", (gl[(gl.team == US) & (gl.period == 1)].t.max() / 60, f[f.period == 1].xg.sum()), xytext=(20, 60), textcoords="offset points",
                fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Buffalo scored {us_sc - en_goals} (plus an empty-netter) on chances worth {f.xg.sum():.1f}",
           f"Sabres at Capitals, Nov. 19. Running total of what each team's chances were worth. Dots = goals. Sabres won {us_sc}-{them_sc}.",
           f"Shots that weren't blocked, empty net excluded: Sabres {len(f)}, Capitals {len(a)}. Buffalo's sixth goal was into an empty net.")
    fig.texts[-1].set_text(f"Source: NHL play-by-play, Buffalo Quant Desk chances model.\nShots that weren't blocked, empty net excluded: Sabres {len(f)}, Capitals {len(a)}. Buffalo's sixth goal was into an empty net.")
    fig.savefig(OUT / "sabres-wsh-post-flow.png"); plt.close(fig)

    # ---- chart 2: Buffalo's goals minus chances, every game this season
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    order = sab.game_id.tolist()
    dv = bd.d.reindex(order)
    skid_ids = set(prior.game_id.tail(skid))
    cols = [BLUE if gid == G else ("#C60C30" if gid in skid_ids else GRAY) for gid in order]
    ax.bar(np.arange(1, len(order) + 1), dv.values, color=cols, width=0.7, zorder=2)
    ax.axhline(0, color=INK, lw=0.8)
    ax.text(len(order), dv.loc[G] + 0.1, "Nov. 19 at WSH", ha="center", fontsize=9, color=BLUE, fontweight="bold")
    lo = float(min(dv.min(), 0)) - 0.9
    ax.set_ylim(lo, float(dv.max()) + 0.6)
    ax.text(len(order) - 3, lo + 0.25, "the 5-game skid", ha="center", fontsize=9, color="#C60C30")
    ax.set_xticks(range(1, len(order) + 1, 3))
    ax.set_xlabel("Sabres game number, 2026-27"); ax.set_ylabel("Goals scored minus\nwhat the chances were worth")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True); ax.set_xlim(0.3, len(order) + 0.7)
    finish(fig, "Nov. 19 was the Sabres' second-best shooting night of the season",
           f"Each bar: Buffalo's goals minus what its chances were worth that game ({n_bg} games). Above zero = scored more than its chances.",
           "x")
    fig.texts[-1].set_text("Source: NHL play-by-play, Buffalo Quant Desk chances model. Empty-net goals excluded.")
    fig.savefig(OUT / "sabres-wsh-post-finishing.png"); plt.close(fig)

    goal_rows = "\n".join(
        f"| {int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Capitals'} | {r.who} | "
        + ("empty net" if r.empty_net_against else f"{'poked in' if r.shot_type == 'poke' else r.shot_type} from {r.dist:.0f} ft{', on a rebound' if r.rebound else ''}{', power play' if r.strength in PP else ''}{', four-on-four' if r.strength == '4v4' else ''}")
        + f" | {'' if r.empty_net_against else f'{r.xg:.0%}'} | Sabres {r.us_run}, Capitals {r.them_run} |"
        for r in gl.itertuples())

    md = f"""# Sabres 6, Capitals 3: the skid is over, even though Washington had the better chances

**The Sabres scored four goals in the first period and beat Washington {us_sc}-{them_sc}, ending a five-game losing streak. They didn't win it with better chances:
Washington's were worth {a.xg.sum():.1f} goals and Buffalo's {f.xg.sum():.1f}. Play this game over and over with those chances, and Buffalo wins it in regulation only about {p_win:.0%} of the time (it's tied after three periods another {p_tie:.0%}).
This time the puck went in. After a cold-shooting skid, it was Buffalo's second-best shooting night of the season. Zach Benson scored, Tage Thompson got his {ordn(tt_g)},
and former Sabre Alex Tuch scored for Washington.**

*One game, Nov. 19, in Washington. [Our preview](sabres-capitals-pregame-nov-19.html).*

![Game flow](sabres-wsh-post-flow.png)

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays. Jack Quinn's first goal, a snap shot from {quinn.iloc[0].dist:.0f} feet,
had about a {quinn.iloc[0].xg:.0%} chance. Tuch's, from {tuch_goal.dist:.0f} feet, had about {tuch_goal.xg:.0%}. Add those chances up
over a game and you get what a team's chances were worth in goals. The shot locations come from the NHL's own play-by-play; the full explanation is in our story on
[last year's 50-win season](sabres-50-win-mirage.html).

## The game

| Period | Sabres goals | Sabres chances, in goals | Capitals goals | Capitals chances, in goals |
|---|---|---|---|---|
""" + "\n".join(f"| {p} | {gper.loc[p, US]} | {per.loc[p, US]:.1f} ({nper.loc[p, US]} shots) | {gper.loc[p, THEM]} | {per.loc[p, THEM]:.1f} ({nper.loc[p, THEM]} shots) |" for p in (1, 2, 3)) + f"""
| Game | {us_sc - en_goals} (+{en_goals} empty net) | {f.xg.sum():.1f} ({len(f)} shots) | {them_sc} | {a.xg.sum():.1f} ({len(a)} shots) |

"Shots" means every shot that wasn't blocked, including misses. Shots at an empty net aren't counted.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

Logan Thompson gave up 3 goals on the {int(lt.on)} shots he faced, and Washington pulled him for Charlie Lindgren after Buffalo's third goal, {clock(pulled_at)} in. In the third period Washington took over: its chances were worth {per.loc[3, THEM]:.1f} goals to Buffalo's {per.loc[3, US]:.1f}, and it
scored twice before Jack Quinn's empty-netter.

## Was it luck?

Mostly, yes. Every team needs nights like this. In the five losses before Thursday, Buffalo scored {sk_gf} goals on chances worth about {sk_xf:.1f}. On Thursday it scored {us_sc - en_goals} (not counting the
empty-netter) on chances worth {f.xg.sum():.1f}, about {f.goal.sum() - f.xg.sum():.0f} more than chances like that usually produce. That's its {'second' if fin_rank == 2 else ordn(fin_rank)}-best shooting night in {n_bg} games this season.

![Finishing by game](sabres-wsh-post-finishing.png)

Our [GM story](sabres-if-i-were-gm.html) said cold shooting tends to even out. For one night, at least, the puck went in. It said the first thing to fix was the penalty kill. More on that below.

## Players

- **Zach Benson** scored at four-on-four in the first, his first goal since {pd.Timestamp(ben_prev_date):%b. %-d}. Not counting an empty-netter, he has {ben_g} goals this season on shots worth about {ben_x:.1f} goals.
- **Tage Thompson** scored on the power play in the second. His {tt_g} goals are {'tied for ' if tt_tied else ''}{ordn(tt_rank)} in the NHL.
- **Alex Tuch** scored for Washington in the first, his {ordn(tuch_g)} of the season.
- **Ukko-Pekka Luukkonen** faced chances worth {ours.xga:.1f} goals and allowed {int(ours.ga)}, about {abs(ours.saved):.1f} {'fewer' if ours.saved > 0 else 'more'} than an average goalie would have.
  This season he's {abs(upl_sv):.1f} goals {'worse' if upl_sv < 0 else 'better'} than average in {upl_gp} games.

## The penalty kill

Our preview called Buffalo's penalty kill against Washington's quiet power play the matchup to watch. The power play wasn't quiet on Thursday: Washington had {len(pp_a)} power-play shots
worth {pp_a.xg.sum():.1f} goals and scored once. Coming in, its power play averaged chances worth {wpp_pre:.2f} goals a game. Buffalo's own power play scored twice on chances worth {pp_f.xg.sum():.1f}.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). We gave the Sabres less than an even chance, so this one goes down as a miss. It scores
{brier:.2f} on our scorecard, where 0 is perfect and a coin flip scores 0.25. We've now got {int(hit.sum())} of our {len(m)} graded calls right, and {int(hit[nhl].sum())} of {int(nhl.sum())} on Sabres games.

## What's next

The Sabres are {rec}. The trip ends with back-to-back games at {NAMES[sch.home.iloc[0]]} on {pd.Timestamp(sch.game_date.iloc[0]).strftime('%A')} and {NAMES[sch.home.iloc[1]]} on
{pd.Timestamp(sch.game_date.iloc[1]).strftime('%A')}, then they're home against {NAMES[sch.away.iloc[2]]} on {pd.Timestamp(sch.game_date.iloc[2]).strftime('%b. %-d')}.

## For the stat-heads

- xG: our model on unblocked, non-empty-net shots, rescaled per season (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} on {len(f)} ({int(f.on_goal.sum())} on goal); WSH {a.xg.sum():.2f} on {len(a)}
  ({int(a.on_goal.sum())} on goal). By period BUF {', '.join(f'{per.loc[p, US]:.2f}' for p in (1, 2, 3))}; WSH {', '.join(f'{per.loc[p, THEM]:.2f}' for p in (1, 2, 3))}. BUF empty-net goals: {en_goals}.
- Strength: BUF 5v5 {ev_f.xg.sum():.2f} ({len(ev_f)}), PP {pp_f.xg.sum():.2f} ({len(pp_f)}); WSH 5v5 {ev_a.xg.sum():.2f} ({len(ev_a)}), PP {pp_a.xg.sum():.2f} ({len(pp_a)}). WSH PP xG/GP before tonight {wpp_pre:.3f}.
- Replays: exact Poisson-binomial. BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx: Luukkonen {ours.saved:+.2f} (season {upl_sv:+.2f}, {upl_gp} GP); L. Thompson {lt.saved:+.2f} ({int(lt.on)} SOG); Lindgren {li.saved:+.2f} ({int(li.on)} SOG).
- G - xG tonight {f.goal.sum() - f.xg.sum():+.2f}; rank {fin_rank} of {n_bg} BUF games. Skid (5 games): {sk_gf} G on {sk_xf:.2f} xG.
- Data through {as_of}; the three late Nov. 19 games not final at publish are excluded (src/reports/pins.py).
- Ledger {PRED_ID}: p = {PRED_P}, outcome 1 (BUF won in regulation), Brier {brier:.4f}.
"""
    (OUT / "2026-11-20-sabres-wsh.md").write_text(md)
    (OUT / "2026-11-20-sabres-wsh.hero.json").write_text(json.dumps({
        "label": "Scoring chances, worth this many goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Capitals"]],
        "note": f"Final: Sabres {us_sc}, Capitals {them_sc}. The skid is over. Buffalo scored {first_g} in the first period on chances worth {first_x:.1f}.",
        "explainer": {"kicker": "Was it luck?", "title": "Goals vs. chances, Sabres",
                      "text": "Goals scored and what the chances were worth (empty net excluded):", "fmt": "num",
                      "bars": [["Goals", int(f.goal.sum())], ["Chances were worth", round(float(f.xg.sum()), 1)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
