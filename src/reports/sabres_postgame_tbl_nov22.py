"""Sabres post-game: BUF at TBL, Nov 22, 2026 (Buffalo 6, Tampa Bay 2). Grades the preview's three keys.

Writes reports/2026-11-22-sabres-tbl-postgame.md, one PNG (sabres-tbl-nov22-post-flow.png) and a hero JSON.
Expected goals are rescaled per season (league xG = goals). Pinned to games through AS_OF (VAN-CHI, not final at
publish, is in src/reports/pins.py). Ledger P0022 graded by src/ledger/grade_p0022.py (separate). Keys defined exactly
as in src/reports/sabres_pregame_tbl_nov22.py.
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
G, SEASON, US, THEM = 2026020374, 20262027, "BUF", "TBL"
AS_OF = "2026-11-22"
PRED_ID, PRED_P = "P0022", 0.35
NOV11 = 2026020293
TB_BLUE = "#6E7B8B"
TTHOMPSON, UPL, HILDEBY, BENSON, OSTLUND = 8479420, 8480045, 8483710, 8484145, 8483500
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


def sab_all(keep, team, season):
    """Team's games this season, newest first."""
    x = keep[(keep.season == season) & ((keep.home == team) | (keep.away == team))]
    return x.sort_values("game_date", ascending=False)


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
    assert (us_sc, them_sc) == (6, 2)

    allg = s[s.game_id == G].sort_values(["period", "t", "eventId"]).copy()
    assert int(allg[allg.team == US].goal.sum()) == us_sc and int(allg[allg.team == THEM].goal.sum()) == them_sc
    en = allg[(allg.goal == 1) & (allg.empty_net_against == 1)]
    assert len(en) == 1 and en.iloc[0].team == US and int(en.iloc[0].shooter_id) == BENSON
    g = allg[(allg.unblocked == 1) & (allg.empty_net_against == 0)]
    f, a = g[g.team == US], g[g.team == THEM]
    per = g.pivot_table(index="period", columns="team", values="xg", aggfunc="sum").fillna(0)
    nper = g.groupby(["period", "team"]).size().unstack().fillna(0).astype(int)
    gper = allg[allg.goal == 1].groupby(["period", "team"]).size().unstack().reindex([1, 2, 3]).fillna(0).astype(int)
    assert set(per.index) == {1, 2, 3}
    assert (gper.loc[2, US], gper.loc[2, THEM]) == (3, 0)

    gl = allg[allg.goal == 1].copy()
    gl["who"] = gl.shooter_id.map(names)
    gl["us_run"] = (gl.team == US).cumsum()
    gl["them_run"] = (gl.team == THEM).cumsum()
    assert len(gl) == 8 and not (gl.them_run > gl.us_run).any()      # Buffalo never trailed
    tie = gl[(gl.team == THEM) & (gl.us_run == gl.them_run)]
    assert len(tie) == 1
    tie_goal = tie.iloc[0]
    go_ahead = gl[(gl.t > tie_goal.t)].iloc[0]
    assert go_ahead.team == US and go_ahead.period == 2
    tt = gl[gl.shooter_id == TTHOMPSON]
    assert len(tt) == 2 and set(tt.period) == {2}
    ost = gl[gl.shooter_id == OSTLUND].iloc[0]

    # replays (no empty-net shots)
    pf, pa = pmf(f.xg.values), pmf(a.xg.values)
    joint = np.outer(pf, pa)
    p_win, p_tie = float(np.tril(joint, -1).sum()), float(np.trace(joint))
    p_loss = 1 - p_win - p_tie

    # ---- the three keys, graded
    tb_ppg = int(gl[(gl.team == THEM) & gl.strength.isin(PP)].shape[0])
    bu_ppg = int(gl[(gl.team == US) & gl.strength.isin(PP)].shape[0])
    pp_a, pp_f = a[a.strength.isin(PP)], f[f.strength.isin(PP)]
    first_team = gl.iloc[0].team
    e5f, e5a = float(f[f.strength == "5v5"].xg.sum()), float(a[a.strength == "5v5"].xg.sum())
    g5f = int(gl[(gl.team == US) & (gl.strength == "5v5")].shape[0])
    k1, k2, k3 = tb_ppg <= 1, first_team == US, e5f > e5a
    assert (k1, k2, k3) == (True, True, False) and tb_ppg == 1 and bu_ppg == 1 and g5f == 4

    # league: hit keys 1 and 2 but lost the 5v5 chances, every game since 2023-24 (same definitions as the preview)
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
    # "gave it back": after the first goal, the other team's running total ties or passes the first scorer's (shootouts left out)
    gb = gall[gall.period < 5].copy()
    gb["ft"] = gb.game_id.map(first)
    gb["f_run"] = (gb.team == gb.ft).astype(int).groupby(gb.game_id).cumsum()
    gb["o_run"] = (gb.team != gb.ft).astype(int).groupby(gb.game_id).cumsum()
    gave_back = set(gb[gb.o_run >= gb.f_run].game_id)
    kr["gave_back"] = kr.game_id.isin(gave_back)
    spot = kr[(kr.ppga <= 1) & kr.first & kr.gave_back & ~kr.ev_won]
    spot_w, spot_n = float(spot.win.mean()), len(spot)
    combo = kr[(kr.ppga <= 1) & kr.first & ~kr.ev_won]
    combo_w, combo_n = float(combo.win.mean()), len(combo)
    allk = kr[(kr.ppga <= 1) & kr.first & kr.ev_won]
    allk_w = float(allk.win.mean())
    b_ty = kr[(kr.team == US) & (kr.season == SEASON)]
    b_f_n, b_f_w = int(b_ty.first.sum()), int(b_ty[b_ty.first].win.sum())
    assert (b_f_n, b_f_w) == (14, 6)
    kept = combo[~combo.gave_back]
    assert spot_n == 1286 and round(spot_w, 3) == 0.423 and len(kept) == 570 and kept.win.all() and G in gave_back
    # rest: road team on 0 days' rest vs a rested home team (as in the preview, through the preview's data)
    assert gm.game_date == as_of

    # goalies
    gk = g.groupby(["opp", "goalie_id"]).agg(on=("on_goal", "sum"), xga=("xg", "sum"), ga=("goal", "sum")).reset_index()
    gk["saved"] = gk.xga - gk.ga
    ours = gk[gk.opp == US].iloc[0]
    theirs = gk[gk.opp == THEM].iloc[0]
    assert int(ours.goalie_id) == UPL and int(theirs.goalie_id) == HILDEBY and len(gk) == 2
    up = cur[cur.goalie_id == UPL]
    up_gp, up_sv = up.game_id.nunique(), float(up.xg.sum() - up.goal.sum())
    sv_all = cur.groupby("goalie_id").apply(lambda d: d.xg.sum() - d.goal.sum())
    up_rank, n_gk = int(sv_all.rank(ascending=False, method="min")[UPL]), len(sv_all)

    # Nov. 11 rematch
    n11 = u[u.game_id == NOV11]
    n11f, n11a = float(n11[n11.team == US].xg.sum()), float(n11[n11.team == THEM].xg.sum())
    n11g = query(f"SELECT home, away, home_score, away_score FROM raw_nhl_games WHERE game_id={NOV11}").iloc[0]
    assert (n11g.home, n11g.home_score, n11g.away_score) == (US, 3, 8)

    # Tampa Bay at home before tonight; Buffalo's road trip
    ty = keep[(keep.season == SEASON) & (keep.game_id != G)]
    th = ty[ty.home == THEM]
    th_w = int((th.home_score > th.away_score).sum())
    th_l = len(th) - th_w
    assert (th_w, th_l) == (10, 1)
    home_pct = ty.assign(w=ty.home_score > ty.away_score).groupby("home").w.agg(["mean", "size"])
    best_home = home_pct["mean"].idxmax() == THEM and (home_pct["mean"] == home_pct.loc[THEM, "mean"]).sum() == 1
    trip, trip_rows = 0, []
    for r in sab_all(keep, US, SEASON).itertuples():
        if r.home == US:
            break
        trip += 1
        trip_rows.append(r)
    assert trip == 6
    tr = pd.DataFrame(trip_rows)
    tr_w = tr.away_score > tr.home_score
    tr_ot = tr.last_period_type.isin(["OT", "SO"])
    trip_rec = f"{int(tr_w.sum())}-{int((~tr_w & ~tr_ot).sum())}-{int((~tr_w & tr_ot).sum())}"
    assert trip_rec == "2-3-1"
    tt_d = sorted(int(round(d)) for d in tt.dist)

    # players
    goals_all = s[(s.goal == 1) & (s.season == SEASON)].groupby("shooter_id").size()
    tt_g, tt_rank = int(goals_all[TTHOMPSON]), int(goals_all.rank(ascending=False, method="min")[TTHOMPSON])
    tt_tied = int((goals_all == goals_all[TTHOMPSON]).sum()) > 1
    tt_x = float(f[f.shooter_id == TTHOMPSON].xg.sum())
    top = f.groupby("shooter_id").xg.sum().sort_values(ascending=False)
    assert top.index[0] == BENSON
    ben_x = float(top.iloc[0])
    ben_goals = int(gl[(gl.shooter_id == BENSON)].shape[0])

    # record, schedule
    sab = keep[(keep.season == SEASON) & ((keep.home == US) | (keep.away == US))].sort_values("game_date").copy()
    sab["won"] = np.where(sab.home == US, sab.home_score > sab.away_score, sab.away_score > sab.home_score)
    ot = sab.last_period_type.isin(["OT", "SO"])
    rec = f"{int(sab.won.sum())}-{int((~sab.won & ~ot).sum())}-{int((~sab.won & ot).sum())}"
    pts = int(2 * sab.won.sum() + (~sab.won & ot).sum())
    assert rec == "10-10-4" and pts == 24
    sch = query(f"SELECT game_date, start_utc, home, away FROM raw_nhl_schedule WHERE season={SEASON} AND game_type=2 AND (home='{US}' OR away='{US}') "
                f"AND game_date > '{as_of}' ORDER BY game_date LIMIT 2")
    nxt = sch.iloc[0]
    assert (nxt.home, nxt.away) == (US, "NYR")
    nxt_day = pd.Timestamp(nxt.game_date).strftime("%A")
    nxt_hr = pd.Timestamp(nxt.start_utc).tz_convert("America/New_York").strftime("%-I %p").replace("PM", "p.m.").replace("AM", "a.m.")

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

    # ---- chart: game flow
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    end = 60.0
    for team, col, lab in [(US, BLUE, "Sabres"), (THEM, TB_BLUE, "Lightning")]:
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
    t2 = tt.iloc[-1]
    ax.annotate("Three Buffalo goals in the 2nd,\ntwo by Tage Thompson", (t2.t / 60, float(f[f.t <= t2.t].xg.sum())), xytext=(20, -55),
                textcoords="offset points", fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xticks([0, 20, 40, 60], ["0", "20", "40", "60"])
    ax.set_xlabel("Game minute"); ax.set_ylabel("Goals the chances were worth (running total)")
    ax.legend(frameon=False, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Tampa Bay's chances were worth {a.xg.sum():.1f} goals, Buffalo's {f.xg.sum():.1f}. Buffalo won {us_sc}-{them_sc}",
           "Sabres at Lightning, Nov. 22. Running total of what each team's chances were worth. Dots = goals.", "x")
    fig.texts[-1].set_text(f"Source: NHL play-by-play, Buffalo Quant Desk chances model. Shots that weren't blocked: Sabres {len(f)}, "
                           f"Lightning {len(a)}.\nLeaves out Zach Benson's empty-net goal.")
    fig.savefig(OUT / "sabres-tbl-nov22-post-flow.png"); plt.close(fig)

    def shot_txt(r):
        if r.empty_net_against == 1:
            return "into an empty net"
        st = {"5v5": "", "4v4": ", four-on-four", "5v3": ", two-man advantage"}.get(
            r.strength, ", power play" if r.strength in PP else (", shorthanded" if r.strength in SH else ""))
        return f"{r.shot_type} from {r.dist:.0f} ft{', on a rebound' if r.rebound else ''}{st}"
    goal_rows = "\n".join(
        f"| {int(r.period)} | {clock(r.t)} | {'Sabres' if r.team == US else 'Lightning'} | {r.who} | {shot_txt(r)} | "
        f"{'n/a' if r.empty_net_against == 1 else f'{r.xg:.0%}'} | Sabres {r.us_run}, Lightning {r.them_run} |"
        for r in gl.itertuples())
    YN = lambda b: "**Yes**" if b else "**No**"

    md = f"""# Sabres 6, Lightning 2: Tampa Bay had more of the chances, and Buffalo finished them

**On the second night of a back-to-back, the Sabres beat Tampa Bay {us_sc}-{them_sc}. The Lightning came in {th_w}-{th_l} at home{", the NHL's best home record" if best_home else ""}. Tampa Bay's chances were worth {a.xg.sum():.1f} goals,
Buffalo's {f.xg.sum():.1f}. But Buffalo scored {us_sc - 1} on Dennis Hildeby, plus an empty-netter. At the other end, Ukko-Pekka Luukkonen allowed {int(ours.ga)}.
On Nov. 11 the chances were even, and Tampa Bay won {n11g.away_score}-{n11g.home_score}. Our pregame call gave Buffalo {PRED_P:.0%}, so it goes down as a miss.**

*One game, Nov. 22, in Tampa. [Our preview](sabres-lightning-pregame-nov-22.html).*

![Game flow](sabres-tbl-nov22-post-flow.png)

## The three keys, graded

| Key | What happened | Hit? |
|---|---|---|
| Tampa Bay gets one power-play goal at most | Nikita Kucherov scored on the power play in the 1st. It was Tampa Bay's only power-play goal. Its {len(pp_a)} power-play shots were worth {pp_a.xg.sum():.1f} goals | {YN(k1)} |
| Score first, and keep it | Jiri Kulich scored {clock(gl.iloc[0].t)} in, but Tampa Bay tied it later in the 1st. Buffalo went back ahead in the 2nd and never trailed | **Half** |
| More of the chances at five-on-five | Tampa Bay's were worth {e5a:.1f} goals, Buffalo's {e5f:.1f} | {YN(k3)} |

Since 2023-24, teams in Buffalo's spot won {spot_w:.0%} of the time ({spot_n:,} games). They allowed one power-play goal at most, scored first but saw the other team tie it,
and had fewer of the five-on-five chances. Buffalo has scored first {b_f_n} times this season and won {b_f_w} of those games, a small sample.

## What decided it

**Finishing.** Buffalo scored {g5f} of its goals at five-on-five, on chances worth {e5f:.1f}. Noah Ostlund's goal came from {ost.dist:.0f} feet, the closest of the night.
Tage Thompson's two came from {tt_d[0]} and {tt_d[1]} feet. Hildeby faced chances worth {theirs.xga:.1f} goals and allowed {int(theirs.ga)}.

**Luukkonen.** Tampa Bay's chances were worth {ours.xga:.1f} goals, and he allowed {int(ours.ga)}: about {ours.saved:.1f} fewer than an average goalie would have.
For the season he's {abs(up_sv):.1f} goals {'better' if up_sv > 0 else 'worse'} than average in {up_gp} games, {ordn(up_rank)} of {n_gk} goalies.

Play this game over and over with these chances, and Buffalo wins it in regulation about {p_win:.0%} of the time, Tampa Bay about {p_loss:.0%},
and it's tied after three periods the rest ({p_tie:.0%}). On Sunday, Buffalo won anyway. On Nov. 11, with chances worth
{n11f:.1f} for Buffalo and {n11a:.1f} for Tampa Bay, it lost {n11g.away_score}-{n11g.home_score}.

## How we measure "chances"

Every shot has a chance of going in, based on where it was taken, what kind of shot it was, and things like rebounds and power plays. Ostlund's {ost.shot_type} shot from
{ost.dist:.0f} feet had about a {ost.xg:.0%} chance. Kulich's opener, from {gl.iloc[0].dist:.0f} feet, had about {gl.iloc[0].xg:.0%}. Add those up over a game and you get
what a team's chances were worth in goals. Empty-net shots are left out. The full explanation is in our story on [last year's 50-win season](sabres-50-win-mirage.html).

## The game

| Period | Sabres goals | Sabres chances, in goals | Lightning goals | Lightning chances, in goals |
|---|---|---|---|---|
""" + "\n".join(f"| {p} | {gper.loc[p, US]} | {per.loc[p, US]:.1f} ({nper.loc[p, US]} shots) | {gper.loc[p, THEM]} | {per.loc[p, THEM]:.1f} ({nper.loc[p, THEM]} shots) |" for p in (1, 2, 3)) + f"""
| Game | {us_sc} | {f.xg.sum():.1f} ({len(f)} shots) | {them_sc} | {a.xg.sum():.1f} ({len(a)} shots) |

"Shots" means every shot that wasn't blocked, including misses. Buffalo's goal totals include Benson's empty-netter; its chances don't.

| Period | Time | Team | Scorer | Shot | Chance it went in | Score |
|---|---|---|---|---|---|---|
{goal_rows}

## Players

- **Tage Thompson** scored twice, once with a two-man advantage. He has {tt_g}, {'tied for ' if tt_tied else ''}{ordn(tt_rank)} in the NHL.
- **Zach Benson** had the best chances of anyone on the ice: his shots were worth {ben_x:.1f} goals. His only goal was the empty-netter.
- **Ukko-Pekka Luukkonen** stopped {int(ours.on - ours.ga)} of {int(ours.on)} shots on goal.

## Receipts: our pregame call

Before the game we logged **a {PRED_P:.0%} chance the Sabres win** on the [Ledger](../ledger.html). We gave Tampa Bay the better chance, and Buffalo won, so the call goes down as a miss.
It scores {brier:.2f} on our scorecard, where 0 is perfect and a coin flip scores 0.25. We've now got {int(hit.sum())} of our {len(m)} graded calls right, and {int(hit[nhl].sum())} of {int(nhl.sum())} on Sabres games.
The three keys aren't Ledger calls, but we'll keep grading them after every game.

## What's next

The Sabres are {rec} ({pts} points). They went {trip_rec} on a {trip}-game road trip and are home {nxt_day} against the Rangers ({nxt_hr}).

## For the stat-heads

- xG: our model on unblocked, non-empty-net shots, rescaled per season (2026-27 factor {cal.loc[SEASON]:.3f}). BUF {f.xg.sum():.2f} on {len(f)} ({int(f.on_goal.sum())} on goal);
  TBL {a.xg.sum():.2f} on {len(a)} ({int(a.on_goal.sum())} on goal). By period BUF {', '.join(f'{per.loc[p, US]:.2f}' for p in (1, 2, 3))}; TBL {', '.join(f'{per.loc[p, THEM]:.2f}' for p in (1, 2, 3))}.
- Strength: 5v5 BUF {e5f:.2f}, TBL {e5a:.2f}; PP BUF {pp_f.xg.sum():.2f} ({len(pp_f)}), TBL {pp_a.xg.sum():.2f} ({len(pp_a)}). PPG BUF {bu_ppg}, TBL {tb_ppg}. TBL 6v5 (goalie pulled) {a[a.strength == '6v5'].xg.sum():.2f} ({int((a.strength == '6v5').sum())}).
- Replays: exact Poisson-binomial, non-empty-net shots. BUF win {p_win:.3f}, tie {p_tie:.3f}, loss {p_loss:.3f}.
- GSAx: Luukkonen {ours.saved:+.2f} (season {up_sv:+.2f}, {up_gp} GP, {ordn(up_rank)} of {n_gk}); Hildeby {theirs.saved:+.2f}. Nov. 11 xGF BUF {n11f:.2f}, TBL {n11a:.2f}.
- Key 2 is graded "Half": BUF scored first but TBL tied it. Keys (definitions as in the preview): team-games 2023-24 through {as_of}, n = {len(kr):,}.
  PPGA <= 1, first goal, opponent later tied or led (shootouts excluded), 5v5 xG lost: win {spot_w:.3f} (n {spot_n:,}). Without the tie condition: {combo_w:.3f} (n {combo_n:,}),
  of which {len(kept)} never gave the lead back and all won. All three keys hit (first-goal definition): {allk_w:.3f} (n {len(allk):,}).
- Data through {as_of}; VAN-CHI, not final at publish, is excluded (src/reports/pins.py).
- Ledger {PRED_ID}: p = {PRED_P}, outcome 1 (BUF won in regulation), Brier {brier:.4f}.
"""
    (OUT / "2026-11-22-sabres-tbl-postgame.md").write_text(md)
    (OUT / "2026-11-22-sabres-tbl-postgame.hero.json").write_text(json.dumps({
        "label": "Scoring chances, worth this many goals",
        "big": [[round(float(f.xg.sum()), 1), "Sabres"], [round(float(a.xg.sum()), 1), "Lightning"]],
        "note": f"Final: Sabres {us_sc}, Lightning {them_sc}. Tampa Bay had more of the chances; Buffalo finished them.",
        "explainer": {"kicker": "In goal", "title": "Goals allowed vs. chances, Ukko-Pekka Luukkonen",
                      "text": "Goals Tampa Bay scored and what its chances were worth:", "fmt": "num",
                      "bars": [["Goals allowed", int(ours.ga)], ["Chances were worth", round(float(ours.xga), 1)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
