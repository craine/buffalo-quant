"""Sabres post-game: BUF at FLA, Nov 21, 2026 (Florida 4, Buffalo 3). Grades the preview's three keys.

Writes reports/2026-11-22-sabres-fla.md, one PNG and a hero JSON. Expected goals are rescaled per season (league xG = goals).
Pinned to games through AS_OF (late games not final at publish are in src/reports/pins.py). Ledger P0020 graded by
src/ledger/grade_p0020.py (separate). Keys defined exactly as in src/reports/sabres_pregame_fla.py.
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
from src.reports.pins import drop_late
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
G, SEASON, US, THEM = 2026020361, 20262027, "BUF", "FLA"
AS_OF = "2026-11-21"
PRED_ID, PRED_P = "P0020", 0.37
RED_F = "#C8102E"
BENNETT, KULICH, TTHOMPSON, LYON, MARKSTROM = 8477935, 8483468, 8479420, 8479312, 8474593
PP = ("5v4", "5v3", "4v3")
SH = ("4v5", "3v5", "3v4")


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
    keep = drop_late(query(f"SELECT g.game_id, g.season, g.game_date, g.home, g.away, g.home_score, g.away_score, g.last_period_type "
                           f"FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id "
                           f"WHERE c.game_type = 2 AND g.game_date <= '{as_of}'"), as_of)
    s = s[s.game_id.isin(set(keep.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb]
    cur = u[u.season == SEASON]
    names = query("SELECT player_id, MAX(first)||' '||MAX(last) AS name FROM raw_nhl_rosters GROUP BY player_id").set_index("player_id").name
    gm = query(f"SELECT * FROM raw_nhl_games WHERE game_id={G}").iloc[0]
    assert gm.home == THEM and gm.away == US and gm.game_state in ("OFF", "FINAL") and gm.last_period_type == "REG"
    us_sc, them_sc = int(gm.away_score), int(gm.home_score)
    assert (us_sc, them_sc) == (3, 4)

    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    assert int(allg[allg.team == US].goal.sum()) == us_sc and int(allg[allg.team == THEM].goal.sum()) == them_sc
    assert not (allg.empty_net_against == 1).any()
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    f, a = g[g.team == US], g[g.team == THEM]
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    nper = g.groupby(["period", "team"]).size().unstack().fillna(0).astype(int)
    gper = g.groupby(["period", "team"]).goal.sum().unstack().fillna(0).astype(int)
    assert set(per.index) == {1, 2, 3}

    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    gl["us_run"] = (gl.team == US).cumsum()
    gl["them_run"] = (gl.team == THEM).cumsum()
    assert len(gl) == 7
    win_goal = gl.iloc[-1]
    assert win_goal.team == THEM and win_goal.period == 3
    left = 3600 - int(win_goal.t)

    # replays
    pf, pa = pmf(f.xg.values), pmf(a.xg.values)
    joint = np.outer(pf, pa)
    p_win, p_tie = float(np.tril(joint, -1).sum()), float(np.trace(joint))
    p_loss = 1 - p_win - p_tie

    # ---- the three keys, graded
    fla_ppg = int(gl[(gl.team == THEM) & gl.strength.isin(PP)].shape[0])
    fla_shg = gl[(gl.team == THEM) & gl.strength.isin(SH)]
    pp_a, pp_f = a[a.strength.isin(PP)], f[f.strength.isin(PP)]
    first_team = gl.iloc[0].team
    lead = gl[(gl.us_run > gl.them_run)]
    assert len(lead) == 1                      # Buffalo led once
    lead_start = int(lead.iloc[0].t)
    lead_end = int(gl[gl.t > lead_start].iloc[0].t)
    lead_secs = lead_end - lead_start
    e5f, e5a = float(f[f.strength == "5v5"].xg.sum()), float(a[a.strength == "5v5"].xg.sum())
    k1, k2, k3 = fla_ppg <= 1, first_team == US, e5f > e5a
    assert (k1, k2, k3) == (True, False, True) and len(fla_shg) == 1 and lead_secs == 18

    # league: teams that hit keys 1 and 3 but allowed the first goal, every game since 2023-24 (same definitions as the preview)
    sa = s.sort_values(["game_id", "period", "t", "eventId"])
    gall = sa[sa.goal == 1]
    first = gall.groupby("game_id").head(1).set_index("game_id").team
    kr = []
    for side, opp in (("home", "away"), ("away", "home")):
        kr.append(keep.rename(columns={side: "team", f"{side}_score": "gf", f"{opp}_score": "ga"})[["game_id", "season", "team", "gf", "ga"]])
    kr = pd.concat(kr)
    kr = kr[kr.season >= 20232024].copy()
    kr["win"] = kr.gf > kr.ga
    kr["first"] = kr.game_id.map(first) == kr.team
    ppg_a = gall[gall.strength.isin(PP)].groupby(["game_id", "opp"]).size()
    kr["ppga"] = [int(ppg_a.get((gid, tm), 0)) for gid, tm in zip(kr.game_id, kr.team)]
    e5 = u[u.strength == "5v5"]
    ef, ea = e5.groupby(["game_id", "team"]).xg.sum(), e5.groupby(["game_id", "opp"]).xg.sum()
    kr["ev_won"] = [ef.get((gid, tm), 0) > ea.get((gid, tm), 0) for gid, tm in zip(kr.game_id, kr.team)]
    combo = kr[(kr.ppga <= 1) & ~kr.first & kr.ev_won]
    combo_w, combo_n = float(combo.win.mean()), len(combo)
    allk = kr[(kr.ppga <= 1) & kr.first & kr.ev_won]
    allk_w = float(allk.win.mean())
    b_ty = kr[(kr.team == US) & (kr.season == SEASON)]
    b_nf_n, b_nf_w = int((~b_ty.first).sum()), int(b_ty[~b_ty.first].win.sum())
    assert 0.4 < combo_w < 0.5 and 0.75 < allk_w < 0.8 and (b_nf_n, b_nf_w) == (10, 4)

    # goalies
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    ours = gk[gk.opp == US].iloc[0]
    theirs = gk[gk.opp == THEM].iloc[0]
    assert int(ours.goalie_id) == LYON and int(theirs.goalie_id) == MARKSTROM and len(gk) == 2
    ly = cur[cur.goalie_id == LYON]
    ly_gp, ly_sv = ly.game_id.nunique(), float(ly.xg.sum() - ly.goal.sum())

    # players
    ben = gl[gl.shooter_id == BENNETT]
    assert len(ben) == 3 and (ben.dist >= 30).all()
    ben_x = float(ben.xg.sum())
    kul = gl[gl.shooter_id == KULICH].iloc[0]
    kul_x = float(f[f.shooter_id == KULICH].xg.sum())
    assert g.groupby("shooter_id").xg.sum().idxmax() == KULICH
    goals_all = s[(s.unblocked == 1) & (s.goal == 1) & (s.season == SEASON)].groupby("shooter_id").size()
    tt_g, tt_rank = int(goals_all[TTHOMPSON]), int(goals_all.rank(ascending=False, method="min")[TTHOMPSON])
    tt_tied = int((goals_all == goals_all[TTHOMPSON]).sum()) > 1
    ben_season = int(goals_all[BENNETT])

    # record, schedule
    sab = keep[(keep.season == SEASON) & ((keep.home == US) | (keep.away == US))].sort_values("game_date").copy()
    sab["won"] = np.where(sab.home == US, sab.home_score > sab.away_score, sab.away_score > sab.home_score)
    ot = sab.last_period_type.isin(["OT", "SO"])
    rec = f"{int(sab.won.sum())}-{int((~sab.won & ~ot).sum())}-{int((~sab.won & ot).sum())}"
    assert rec == "9-10-4"
    sch = query(f"SELECT game_date, start_utc, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') "
                f"AND game_date > '{as_of}' ORDER BY game_date LIMIT 2")
    assert (sch.game_date.iloc[0], sch.home.iloc[0], sch.start_utc.iloc[0]) == ("2026-11-22", "TBL", "2026-11-22T22:00:00Z")
    assert sch.home.iloc[1] == US

    # ledger record
    pr = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    m = pr.merge(gr, left_on="id", right_on="prediction_id")
    m = m[pd.to_datetime(m.graded_at_utc) <= pd.Timestamp(as_of, tz="UTC") + pd.Timedelta(days=2)]
    hit = ((m.probability >= 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))
    nhl = m.sport == "NHL"
    row = m[m.id == PRED_ID].iloc[0]
    assert row.outcome == 0
    brier = float(row.brier)

    # ---- chart: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    end = 60.0
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, RED_F, "Panthers")]:
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
    ax.axvspan(lead_start / 60, lead_end / 60, color=BLUE, alpha=0.12, lw=0)
    ax.annotate(f"Buffalo's only lead\nlasted {lead_secs} seconds", (lead_start / 60, float(f[f.t <= lead_start].xg.sum())), xytext=(-110, 40),
                textcoords="offset points", fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate(f"Florida's winner,\n{clock(win_goal.t)} of the 3rd", (win_goal.t / 60, float(a.xg.sum())), xytext=(-120, 12),
                textcoords="offset points", fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Buffalo's chances were worth {f.xg.sum():.1f} goals, Florida's {a.xg.sum():.1f}. Florida won {them_sc}-{us_sc}",
           f"Sabres at Panthers, Nov. 21. Running total of what each team's chances were worth. Dots = goals.",
           "x")
    fig.texts[-1].set_text(f"Source: NHL play-by-play, Buffalo Quant Desk chances model.\nShots that weren't blocked: Sabres {len(f)}, Panthers {len(a)}. No empty-net shots.")
    fig.savefig(OUT / "sabres-fla-post-flow.png"); plt.close(fig)

    def shot_txt(r):
        st = {"5v5": "", "4v4": ", four-on-four"}.get(r.strength, ", power play" if r.strength in PP else (", shorthanded" if r.strength in SH else ""))
        return f"{'poked in' if r.shot_type == 'poke' else r.shot_type} from {r.dist:.0f} ft{', on a rebound' if r.rebound else ''}{st}"
    goal_rows = "\n".join(
        f"| {int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Panthers'} | {r.who} | {shot_txt(r)} | {r.xg:.0%} | Sabres {r.us_run}, Panthers {r.them_run} |"
        for r in gl.itertuples())
    lead_goal, tie_goal = gl[gl.t == lead_start].iloc[0], gl[gl.t == lead_end].iloc[0]
    YN = lambda b: "**Yes**" if b else "**No**"

    md = f"""# Panthers {them_sc}, Sabres {us_sc}: Buffalo hit two of its three keys and still lost

**Florida scored with {left // 60}:{left % 60:02d} left to beat the Sabres {them_sc}-{us_sc}. Before the game we named three keys. Buffalo kept Florida's power play off the board
and got more of the chances at five-on-five. It didn't score first, and its only lead lasted {lead_secs} seconds. The chances were close: Buffalo's were worth
{f.xg.sum():.1f} goals, Florida's {a.xg.sum():.1f}. The difference was in goal, and Sam Bennett scored three.**

*One game, Nov. 21, in Florida. [Our preview](sabres-panthers-pregame-nov-21.html).*

![Game flow](sabres-fla-post-flow.png)

## The three keys, graded

| Key | What happened | Hit? |
|---|---|---|
| Florida gets one power-play goal at most | Florida's power play scored {fla_ppg} on {len(pp_a)} shots worth {pp_a.xg.sum():.1f} goals | {YN(k1)} |
| Score first, and keep it | Florida scored first, {clock(gl.iloc[0].t)} in. Buffalo led {lead_goal.us_run}-{lead_goal.them_run} in the second, and Florida tied it {lead_secs} seconds later | {YN(k2)} |
| More of the chances at five-on-five | Buffalo {e5f:.1f}, Florida {e5a:.1f} | {YN(k3)} |

Since 2023-24, teams that hit the first and third keys but didn't score first have won {combo_w:.0%} of the time ({combo_n:,} games). Teams that hit all three won {allk_w:.0%}.
Teams in Buffalo's spot win a little less than half the time. This season the Sabres have won {b_nf_w} of the {b_nf_n} games where the other team scored first.

The penalty kill held, but Buffalo's own power play gave up a goal: Bennett scored shorthanded {clock(fla_shg.iloc[0].t)} into the third to put Florida ahead {fla_shg.iloc[0].them_run}-{fla_shg.iloc[0].us_run}.

## What decided it

**Goaltending.** Florida's chances were worth {ours.xga:.1f} goals and Alex Lyon allowed {int(ours.ga)}, about {abs(ours.saved):.1f} more than an average goalie would have.
At the other end, Jacob Markstrom faced chances worth {theirs.xga:.1f} and allowed {int(theirs.ga)}. Play this game over and over with these chances, and Buffalo wins it in regulation
about {p_win:.0%} of the time, Florida about {p_loss:.0%}, and it's tied after three periods the rest ({p_tie:.0%}).

**Sam Bennett.** All three of his goals came from 30 feet or more. Together those three shots were worth {ben_x:.1f} goals. He has {ben_season} this season.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays. Jiri Kulich's goal, a {kul.shot_type} shot from
{kul.dist:.0f} feet, had about a {kul.xg:.0%} chance. Bennett's shorthanded goal, from {fla_shg.iloc[0].dist:.0f} feet, had about {fla_shg.iloc[0].xg:.0%}. Add those chances up over a game and you get
what a team's chances were worth in goals. The full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## The game

| Period | Sabres goals | Sabres chances, in goals | Panthers goals | Panthers chances, in goals |
|---|---|---|---|---|
""" + "\n".join(f"| {p} | {gper.loc[p, US]} | {per.loc[p, US]:.1f} ({nper.loc[p, US]} shots) | {gper.loc[p, THEM]} | {per.loc[p, THEM]:.1f} ({nper.loc[p, THEM]} shots) |" for p in (1, 2, 3)) + f"""
| Game | {us_sc} | {f.xg.sum():.1f} ({len(f)} shots) | {them_sc} | {a.xg.sum():.1f} ({len(a)} shots) |

"Shots" means every shot that wasn't blocked, including misses. Florida took more of them, but Buffalo's were worth more.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

## Players

- **Jiri Kulich** had the best chances of anyone on the ice: his shots were worth {kul_x:.1f} goals. He scored once, from {kul.dist:.0f} feet.
- **Tage Thompson** tied it 3-3 in the third, his {ordn(tt_g)} goal. That's {'tied for ' if tt_tied else ''}{ordn(tt_rank)} in the NHL.
- **Alex Lyon** is {abs(ly_sv):.1f} goals {'worse' if ly_sv < 0 else 'better'} than an average goalie this season, in {ly_gp} games.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). We gave Florida the better chance, and Florida won, so the call goes down as right.
It scores {brier:.2f} on our scorecard, where 0 is perfect and a coin flip scores 0.25. We've now got {int(hit.sum())} of our {len(m)} graded calls right, and {int(hit[nhl].sum())} of {int(nhl.sum())} on Sabres games.
The three keys aren't Ledger calls, but we'll keep grading them after every game.

## What's next

The Sabres are {rec}. They play again {pd.Timestamp(sch.game_date.iloc[0]).strftime('%A')}, the second night of a back-to-back, at Tampa Bay ({pd.Timestamp(sch.start_utc.iloc[0]).tz_convert('America/New_York').hour - 12} p.m.), then come home for the Rangers.

## For the stat-heads

- xG: our model on unblocked shots, rescaled per season (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} on {len(f)} ({int(f.on_goal.sum())} on goal); FLA {a.xg.sum():.2f} on {len(a)}
  ({int(a.on_goal.sum())} on goal). By period BUF {', '.join(f'{per.loc[p, US]:.2f}' for p in (1, 2, 3))}; FLA {', '.join(f'{per.loc[p, THEM]:.2f}' for p in (1, 2, 3))}.
- Strength: 5v5 BUF {e5f:.2f}, FLA {e5a:.2f}; PP BUF {pp_f.xg.sum():.2f} ({len(pp_f)}), FLA {pp_a.xg.sum():.2f} ({len(pp_a)}). FLA PPG {fla_ppg}, SHG {len(fla_shg)}.
- Replays: exact Poisson-binomial. BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx: Lyon {ours.saved:+.2f} (season {ly_sv:+.2f}, {ly_gp} GP); Markstrom {theirs.saved:+.2f}. Bennett: 3 G on {ben_x:.2f} xG.
- Keys (definitions as in the preview): team-games 2023-24 through {as_of}, n = {len(kr):,}. PPGA <= 1 and 5v5 xG won but opponent scored first: win {combo_w:.3f} (n {combo_n:,});
  all three keys: {allk_w:.3f} (n {len(allk):,}).
- Data through {as_of}; the nine late Nov. 21 games not final at publish are excluded (src/reports/pins.py).
- Ledger {PRED_ID}: p = {PRED_P}, outcome 0 (FLA won in regulation), Brier {brier:.4f}.
"""
    (OUT / "2026-11-22-sabres-fla.md").write_text(md)
    (OUT / "2026-11-22-sabres-fla.hero.json").write_text(json.dumps({
        "label": "Scoring chances, worth this many goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Panthers"]],
        "note": f"Final: Panthers {them_sc}, Sabres {us_sc}. Buffalo hit two of its three keys; its only lead lasted {lead_secs} seconds.",
        "explainer": {"kicker": "In goal", "title": "Goals allowed vs. chances, Alex Lyon",
                      "text": "Goals Florida scored and what its chances were worth:", "fmt": "num",
                      "bars": [["Goals allowed", int(ours.ga)], ["Chances were worth", round(float(ours.xga), 1)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
