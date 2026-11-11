"""Bills trade for safety Amani Hooker (Nov 10, 2026 deadline). What the data says he brings, in plain English.

Writes reports/2026-11-10-hooker-trade.md, two PNGs and a hero JSON. Every number is computed here, except the trade terms,
which are reported facts cited to the Bills' announcement. Pinned: games through 2026 week THRU.
Coverage numbers (targets, yards allowed, missed tackles) are Pro Football Reference charting via nflverse: human-charted, noisy.
Safeties are identified by matching PFR names to nflverse weekly player stats (see match_safeties).
"""
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 9
HOOKER = "00-0035632"          # gsis id
HOOKER_PFR = "HookAm00"        # PFR id (matched by name+team+season, verified unique)
SAFETY = ("SAF", "FS", "SS", "S")
MIN_TGT, MIN_TGT_SEASON, MIN_TGT_3YR = 25, 15, 60
SLUG = "2026-11-10-hooker-trade"
SRC = "Source: nflverse player stats; Pro Football Reference coverage charting via nflverse. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})


def finish(fig, title, sub, foot, src=SRC):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{src}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def ordn(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


SUFFIX = {"jr", "sr", "ii", "iii", "iv", "v"}
TEAM_FIX = {"OAK": "LV", "SD": "LAC", "STL": "LA"}


def _tokens(n):
    return [w for w in re.sub(r"[.'’]", "", str(n)).lower().split() if w not in SUFFIX]


def full_key(n):
    return " ".join(_tokens(n))


def short_key(n):
    t = _tokens(n)
    return f"{t[0][0]}|{t[-1]}" if t else ""


def match_safeties(pw, pf):
    """PFR rows -> nflverse safeties. Tier 1: same season, team and name (suffixes and punctuation removed).
    Tier 2, only for PFR players still unmatched: first initial + last name, used only where that key is unique
    on the team-season in both sources (catches Kam/Kamren Curl, C.J./Chauncey Gardner-Johnson)."""
    pw = pw.assign(fk=pw.name.map(full_key), sk=pw.name.map(short_key))
    pf = pf.assign(team=pf.team.replace(TEAM_FIX), fk=pf.name.map(full_key), sk=pf.name.map(short_key))
    saf_ids = set(pw[pw.position.isin(SAFETY)].player_id)
    roster = pw[["season", "team", "player_id", "fk", "sk"]].drop_duplicates()
    ids = pf[["season", "team", "pfr_player_id", "fk", "sk"]].drop_duplicates()
    t1 = ids.merge(roster[["season", "team", "fk", "player_id"]].drop_duplicates(), on=["season", "team", "fk"])
    left = ids[~ids.set_index(["season", "pfr_player_id"]).index.isin(t1.set_index(["season", "pfr_player_id"]).index)]
    uniq_r = roster.groupby(["season", "team", "sk"]).player_id.nunique().rename("nr").reset_index()
    uniq_p = ids.groupby(["season", "team", "sk"]).pfr_player_id.nunique().rename("np").reset_index()
    t2 = (left.merge(uniq_r[uniq_r.nr == 1], on=["season", "team", "sk"]).merge(uniq_p[uniq_p.np == 1], on=["season", "team", "sk"])
          .merge(roster[["season", "team", "sk", "player_id"]].drop_duplicates(), on=["season", "team", "sk"]))
    link = pd.concat([t1, t2])[["season", "pfr_player_id", "player_id"]].drop_duplicates()
    link = link[~link.duplicated(["season", "pfr_player_id"], keep=False)]   # same name, two players (e.g. NYJ Michael Carter): drop
    link = link[link.player_id.isin(saf_ids)]
    # a player counts as a safety in a season if nflverse lists him at a safety position that season
    pos = pw[pw.position.isin(SAFETY)][["season", "player_id"]].drop_duplicates()
    link = link.merge(pos, on=["season", "player_id"])
    assert not link.duplicated(["season", "player_id"]).any()
    return pf.merge(link, on=["season", "pfr_player_id"]), int(len(t2.merge(link, on=["season", "pfr_player_id", "player_id"])))


def safety_seasons():
    pw = query("""SELECT season, week, team, player_id, player_display_name AS name, position, def_interceptions AS i
                  FROM raw_player_week WHERE season_type='REG'""")
    pw = pw[(pw.season < SEASON) | (pw.week <= THRU)]
    pf = query("""SELECT season, week, team, pfr_player_name AS name, pfr_player_id, def_ints, def_targets, def_completions_allowed,
                  def_yards_allowed, def_missed_tackles, def_tackles_combined FROM raw_pfr_def WHERE game_type='REG'""")
    pf = pf[(pf.season < SEASON) | (pf.week <= THRU)]
    x, n_tier2 = match_safeties(pw, pf)
    s = x.groupby(["season", "pfr_player_id"]).agg(
        name=("name", "last"), g=("week", "nunique"), ints=("def_ints", "sum"), tgt=("def_targets", "sum"),
        cmp=("def_completions_allowed", "sum"), yds=("def_yards_allowed", "sum"), mt=("def_missed_tackles", "sum"),
        tk=("def_tackles_combined", "sum")).reset_index()
    s["ypt"] = s.yds / s.tgt
    s["cmp_pct"] = s.cmp / s.tgt
    s["int_rate"] = s.ints / s.tgt
    s["mt_pct"] = s.mt / (s.mt + s.tk)
    return pw, x, s, n_tier2


def carryover(s, draws=2000, seed=0):
    q = s[(s.tgt >= MIN_TGT) & (s.season < SEASON)]
    a = q.merge(q, on="pfr_player_id", suffixes=("", "_n"))
    a = a[a.season_n == a.season + 1].reset_index(drop=True)
    mets = ("int_rate", "ypt", "cmp_pct", "mt_pct")
    out = {m: float(a[m].corr(a[m + "_n"])) for m in mets}
    # pairs share players (a middle season appears twice), so resample players, not pairs
    rng = np.random.default_rng(seed)
    players = a.pfr_player_id.unique()
    groups = {p: idx for p, idx in a.groupby("pfr_player_id").groups.items()}
    boot = {m: [] for m in mets}
    for _ in range(draws):
        idx = np.concatenate([groups[p] for p in rng.choice(players, len(players))])
        b = a.loc[idx]
        for m in mets:
            boot[m].append(b[m].corr(b[m + "_n"]))
    boot = {m: np.array(v) for m, v in boot.items()}
    ci = {m: (float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))) for m, v in boot.items()}
    mt_ahead = float((boot["mt_pct"] > boot["int_rate"]).mean())
    big = a[a.ints >= 5]
    ex = dict(n=len(big), players=int(big.pfr_player_id.nunique()), repeat=int((big.ints_n >= 5).sum()),
              this=float(big.ints.mean()), nxt=float(big.ints_n.mean()), all_nxt=float(a.ints_n.mean()))
    return out, len(a), int(a.season.min()), int(a.season_n.max()), len(players), ci, mt_ahead, ex


def main():
    pw, x, s, n_tier2 = safety_seasons()
    h = pw[pw.player_id == HOOKER]
    hs = h.groupby("season").agg(ints=("i", "sum"))
    career_ints = int(hs.ints.sum())
    lead = pw[pw.season == SEASON].groupby(["player_id", "name"]).i.sum()
    top = lead.max()
    co_leaders = [n for (pid, n), v in lead.items() if v == top and pid != HOOKER]
    h_ints = int(hs.loc[SEASON, "ints"])
    hw = h[h.season == SEASON]
    h_games = int(hw.week.nunique())
    best_game = hw.groupby("week").agg(i=("i", "sum"), opp=("team", "first")).sort_values("i").iloc[-1]
    best_wk = int(hw.groupby("week").i.sum().idxmax())
    best_opp = query(f"""SELECT CASE WHEN home_team='TEN' THEN away_team ELSE home_team END AS opp,
                         CASE WHEN home_team='TEN' THEN 'vs.' ELSE 'at' END AS ha FROM raw_schedules
                         WHERE season={SEASON} AND week={best_wk} AND (home_team='TEN' OR away_team='TEN')""").iloc[0]
    team_names = {"CIN": "Cincinnati"}

    hp = s[s.pfr_player_id == HOOKER_PFR].set_index("season")
    # 2026 among safeties
    z = s[(s.season == SEASON) & (s.tgt >= MIN_TGT_SEASON)].copy()
    z["rk_ypt"] = z.ypt.rank(method="min")
    z["rk_mt"] = z.mt_pct.rank(method="min")
    hz = z[z.pfr_player_id == HOOKER_PFR].iloc[0]
    mt_tied = int((z.mt_pct == hz.mt_pct).sum()) > 1
    lg26 = dict(ypt=z.yds.sum() / z.tgt.sum(), mt=z.mt.sum() / (z.mt.sum() + z.tk.sum()))
    # 2025 alone
    z5 = s[(s.season == SEASON - 1) & (s.tgt >= MIN_TGT)].copy()
    z5["rk_ypt"] = z5.ypt.rank(method="min")
    h25 = z5[z5.pfr_player_id == HOOKER_PFR].iloc[0]
    # 2023-2025 pooled
    p3 = s[s.season.between(SEASON - 3, SEASON - 1)].groupby(["pfr_player_id"]).agg(
        name=("name", "last"), tgt=("tgt", "sum"), yds=("yds", "sum"), mt=("mt", "sum"), tk=("tk", "sum")).reset_index()
    p3 = p3[p3.tgt >= MIN_TGT_3YR].copy()
    p3["ypt"] = p3.yds / p3.tgt
    p3["mt_pct"] = p3.mt / (p3.mt + p3.tk)
    p3["rk_ypt"] = p3.ypt.rank(method="min")
    p3["rk_mt"] = p3.mt_pct.rank(method="min")
    h3 = p3[p3.pfr_player_id == HOOKER_PFR].iloc[0]
    lg3 = dict(ypt=p3.yds.sum() / p3.tgt.sum(), mt=p3.mt.sum() / (p3.mt.sum() + p3.tk.sum()))
    # every team's safeties this season, and the Bills' by player
    xs = x[x.season == SEASON]
    tm = xs.groupby("team").agg(tgt=("def_targets", "sum"), yds=("def_yards_allowed", "sum"),
                                mt=("def_missed_tackles", "sum"), tk=("def_tackles_combined", "sum"))
    tm["ypt"] = tm.yds / tm.tgt
    tm["mt_pct"] = tm.mt / (tm.mt + tm.tk)
    tm["rk_ypt"] = tm.ypt.rank(method="min", ascending=False)   # 1 = most yards allowed
    tm["rk_mt"] = tm.mt_pct.rank(method="min", ascending=False)  # 1 = most missed tackles
    lg_tm = dict(ypt=tm.yds.sum() / tm.tgt.sum(), mt=tm.mt.sum() / (tm.mt.sum() + tm.tk.sum()))
    bufs = tm.loc["BUF"]
    bp = xs[xs.team == "BUF"].groupby("pfr_player_id").agg(name=("name", "last"), tgt=("def_targets", "sum"),
                                                          yds=("def_yards_allowed", "sum"), mt=("def_missed_tackles", "sum"),
                                                          tk=("def_tackles_combined", "sum"))
    bp["ypt"] = bp.yds / bp.tgt
    bp = bp[bp.tgt >= 10].sort_values("tgt", ascending=False)
    bn = {r.name: r for r in bp.itertuples()}
    bishop, cjgj, hamlin = (next(r for n, r in bn.items() if k in n) for k in ("Bishop", "Gardner-Johnson", "Hamlin"))
    co, n_pairs, y0, y1, n_players, ci, mt_ahead, ex = carryover(s)

    # ---- chart 1: interceptions by season
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    yrs = list(hs.index)
    ax.bar([str(y) for y in yrs], hs.ints, color=[BLUE if y == SEASON else GRAY for y in yrs], width=0.6, zorder=2)
    for i, (y, r) in enumerate(hs.iterrows()):
        ax.text(i, r.ints + 0.1, f"{int(r.ints)}", ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.text(len(yrs) - 1, hs.ints.iloc[-1] + 0.55, f"{int(best_game.i)} in one game (Wk {best_wk} {best_opp.ha} {best_opp.opp})", ha="center", fontsize=8.5, color=MUTED)
    ax.set_ylim(0, max(hs.ints) + 1.6)
    ax.set_yticks(range(0, int(max(hs.ints)) + 1))
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Amani Hooker's interceptions come in bunches",
           f"Regular-season interceptions by season, all with Tennessee. {SEASON} is through week {THRU} ({h_games} games).",
           f"{career_ints} career regular-season interceptions.", src="Source: nflverse weekly player stats. Regular season.")
    fig.savefig(OUT / "hooker-ints.png"); plt.close(fig)

    # ---- chart 2: what carries over (with ranges)
    lab = {"mt_pct": "Missed tackles", "int_rate": "Interceptions", "ypt": "Yards allowed per throw",
           "cmp_pct": "Completions allowed"}
    order = ["cmp_pct", "ypt", "int_rate", "mt_pct"]
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    ys = range(len(order))
    ax.barh([lab[k] for k in order], [co[k] for k in order], color=[BLUE if k == "int_rate" else GRAY for k in order],
            height=0.55, zorder=2)
    for i, k in enumerate(order):
        lo, hi = ci[k]
        ax.plot([lo, hi], [i, i], color=INK, lw=1.4, zorder=3)
        ax.text(hi + 0.015, i, f"{co[k]:.2f}", va="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xlim(0, 1)
    ax.set_xlabel("How well one season predicts the next (0 = not at all, 1 = perfectly)", fontsize=9.5)
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "For safeties, little carries over from one season to the next",
           f"Safeties thrown at {MIN_TGT}+ times in back-to-back years, {y0}-{y1} ({n_players} players). Black line = likely range; overlap = no real difference.",
           "Interceptions per throw, yards and completions allowed per throw, missed tackles per tackle attempt. Range: middle 95% of 2,000 reshuffles of the players.")
    fig.savefig(OUT / "hooker-carryover.png"); plt.close(fig)

    # ---- chart 3: big interception years, then the next year
    fig, ax = plt.subplots(figsize=(9.5, 4.4), dpi=200)
    bars = [("Their big year", ex["this"], BLUE), ("The next year", ex["nxt"], RED), ("Typical safety, next year", ex["all_nxt"], GRAY)]
    ax.bar([b[0] for b in bars], [b[1] for b in bars], color=[b[2] for b in bars], width=0.55, zorder=2)
    for i, b in enumerate(bars):
        ax.text(i, b[1] + 0.12, f"{b[1]:.1f}", ha="center", fontsize=13, fontweight="bold", color=INK)
    ax.set_ylim(0, ex["this"] + 1); ax.set_ylabel("Interceptions", fontsize=10)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Big interception years rarely repeat ({ex['repeat']} of {ex['n']} did)",
           f"{ex['n']} seasons with 5+ interceptions ({ex['players']} safeties), {y0}-{y1}: what they averaged that year and the next.",
           f"Safeties thrown at {MIN_TGT}+ times in both seasons ({n_pairs} pairs). Regular seasons; PFR interception counts.")
    fig.savefig(OUT / "hooker-bigyears.png"); plt.close(fig)

    lead_txt = f"tied with {co_leaders[0]} for the NFL lead" if len(co_leaders) == 1 else (
        "the NFL lead" if not co_leaders else f"tied for the NFL lead with {len(co_leaders)} others")
    left = int(query(f"""SELECT COUNT(*) AS n FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week>{THRU}
                         AND (home_team='BUF' OR away_team='BUF')""").n.iloc[0])
    words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven']
    att26 = int(hz.mt + hz.tk)
    min_pts = query("SELECT home_score FROM raw_schedules WHERE game_id='2026_09_BUF_MIN'").home_score.iloc[0]
    md = f"""# The Bills paid a second-round pick for Amani Hooker's {h_ints} interceptions. History says don't count on {h_ints} more

**Hooker arrives with {h_ints} interceptions, {lead_txt}. Don't count on that pace: safeties who had five or more in a
season averaged about {ex['nxt']:.1f} the next. Behind the interceptions is a safety who's been about average in coverage this season and below
average the three seasons before. He has still given up fewer yards per throw than C.J. Gardner-Johnson or Damar Hamlin, two of the safeties
he joins.**

*The Bills traded a 2027 second-round pick to Tennessee for Hooker and a 2027 fifth-round pick on Tuesday, Nov. 10, deadline day. He's
signed through 2028. (Trade terms as announced by the Bills.) Numbers below are through week {THRU} of the {SEASON} season.*

![Hooker's interceptions by season](hooker-ints.png)

## The interceptions are real, and they come in bunches

Hooker has {career_ints} regular-season interceptions in {len(hs)} seasons, all with Tennessee. They don't arrive evenly: he had
{int(hs.loc[SEASON - 2, 'ints'])} in {SEASON - 2}, then {int(hs.loc[SEASON - 1, 'ints'])} in {SEASON - 1}, then {h_ints} in {h_games} games this season.
{words[int(best_game.i)].capitalize()} of this year's {h_ints} came in one game, week {best_wk} {best_opp.ha} {team_names.get(best_opp.opp, best_opp.opp)}, so this
year's total rests on a handful of plays.

That's normal for safeties, and it's the main thing to understand about this trade. We looked at every safety thrown at {MIN_TGT} or more
times in back-to-back seasons from {y0} to {y1}: {n_pairs} pairs of seasons from {n_players} players. Does a big interception year repeat? Mostly,
no. The {ex['n']} times a safety had five or more interceptions in a season ({ex['players']} different players), those seasons averaged {ex['this']:.1f}
interceptions. The next year, {ex['nxt']:.1f}, much closer to the {ex['all_nxt']:.1f} the whole group averaged than to their big year. On a scale where 0 means "one season tells you nothing about the next" and
1 means "it tells you everything," interceptions scored {co['int_rate']:.2f}.

![Big interception years rarely repeat](hooker-bigyears.png)

How we got that score: from Pro Football Reference's play-by-play charting (via nflverse), we took each safety's rate in one season
(interceptions per throw at him, for example) and set it beside his rate the next season, for all {n_pairs} pairs. If the players who were
high one year were always high the next, the score would be 1. If the next year looked random, it would be 0. To check it, we re-ran the
math 2,000 times, each time on a random reshuffle of the players. That's where the "give or take about 0.1" below comes from. The
{ex['this']:.1f}-to-{ex['nxt']:.1f} drop is what a score of {co['int_rate']:.2f} looks like on the field: the next year lands much closer to average than to the
big year.

![What carries over](hooker-carryover.png)

To be fair to Hooker, little about a safety carries over well. Tackling scored about the same as interceptions ({co['mt_pct']:.2f}), and
coverage scored a bit lower: yards allowed per throw {co['ypt']:.2f}, completions allowed {co['cmp_pct']:.2f}. With this few players, each score could be off
by about 0.1 either way (the black lines on the chart). The honest reading: interceptions and tackling carry over about equally, and only a little. Safeties are hard to measure, and every number here comes with that warning.

## What the Bills are getting

**Tackling: good this season, average before.** This season Hooker has missed {int(hz.mt)} of {att26} tackle attempts ({hz.mt_pct:.1%}, a small
sample). The average safety misses {lg26['mt']:.1%}. That {'ties him for' if mt_tied else 'makes him'} {ordn(int(hz.rk_mt))}-fewest misses among {len(z)} safeties
thrown at {MIN_TGT_SEASON}+ times. One more miss would have put him at {(hz.mt + 1) / (att26 + 1):.1%}. Over {SEASON - 3} to {SEASON - 1} he missed {h3.mt_pct:.1%}, about the
same as the average safety's {lg3['mt']:.1%}.

**Coverage: about average now, below average before.** Passes thrown his way (the stat sheets call them "targets") have gained
{hz.ypt:.1f} yards per throw this season ({int(hz.tgt)} throws, a small sample), close to the average safety's {lg26['ypt']:.1f}. That's {ordn(int(hz.rk_ypt))} of
{len(z)} safeties, right in the middle. Over {SEASON - 3} to {SEASON - 1} he allowed {h3.ypt:.1f} yards per throw, more than the average safety's {lg3['ypt']:.1f} ({ordn(int(h3.rk_ypt))} of {len(p3)}
safeties thrown at {MIN_TGT_3YR}+ times). Last season alone he allowed {h25.ypt:.1f}, {ordn(int(h25.rk_ypt))} of {len(z5)}.

**How he compares with the Bills' safeties.** As a group, Buffalo's safeties have allowed {bufs.ypt:.1f} yards per throw this season (the
{ordn(int(bufs.rk_ypt))}-most of {len(tm)} teams; all NFL safeties combined: {lg_tm['ypt']:.1f}) and missed {bufs.mt_pct:.1%} of their tackle attempts (the
{ordn(int(bufs.rk_mt))}-most; all NFL safeties combined: {lg_tm['mt']:.1%}, lower than the {lg26['mt']:.1%} above because safeties who are rarely
thrown at miss fewer tackles). That's {int(bufs.tgt)} throws, a small sample, and it isn't spread evenly. Cole Bishop has
allowed {bishop.ypt:.1f} yards per throw ({int(bishop.tgt)} throws), fewer than Hooker. C.J. Gardner-Johnson has allowed {cjgj.ypt:.1f} ({int(cjgj.tgt)}
throws) and missed {cjgj.mt / (cjgj.mt + cjgj.tk):.0%} of his tackle attempts; Damar Hamlin has allowed {hamlin.ypt:.1f} ({int(hamlin.tgt)} throws). Hooker's
{hz.ypt:.1f} beats those two, and the Bills say he'll play alongside Bishop. All of these are a few dozen throws each, so treat them as hints.

## What it means

- **Don't expect {words[h_ints]} more.** Safeties with five-interception years averaged about {ex['nxt']:.1f} over the whole next season. Hooker has {left} regular-season games left with Buffalo. If the interceptions keep coming, that's a bonus. Think "starter who's been average-to-below in coverage
  and is tackling well right now," not "takeaway machine."
- **It's a real price.** Per the Bills, it's the most draft capital the team has used to acquire a player at the trade deadline under general
  manager Brandon Beane. The Bills are paying for this season and the two years left on his contract.
- **What to watch.** Whether he takes snaps from Gardner-Johnson or Hamlin, and whether this season's tackling holds up. Buffalo's safeties
  have missed tackles more often than most teams'. His usual rate over the three seasons before this one ({h3.mt_pct:.1%}) is below the Bills group's {bufs.mt_pct:.1%}.

## For the stat-heads

- Interceptions: nflverse weekly player stats (gsis {HOOKER}), regular season. {SEASON} through week {THRU}. Co-leader(s): {', '.join(co_leaders) or 'none'}.
  He also has one playoff interception (not counted). PFR's charting counts interceptions slightly differently from nflverse; the
  carry-over analysis uses PFR counts, Hooker's career totals use nflverse.
- Coverage: Pro Football Reference charting via nflverse (`pfr_advstats` def). Targets, completions, yards allowed, missed tackles,
  combined tackles. Missed-tackle rate = missed / (missed + combined tackles). Charted by humans; treat as noisy.
- Safeties: PFR rows matched to nflverse weekly player stats on season and team (OAK/SD/STL normalized), then name with suffixes and punctuation
  removed; {n_tier2} more player-seasons matched on first initial + last name where that key is unique on the team. Players nflverse lists as
  "DB" rather than a safety position are left out, which thins the {y0}-2021 sample most.
- Year-to-year: Pearson correlation of each rate between consecutive seasons, safeties with {MIN_TGT}+ targets in both, {y0}-{y1},
  n={n_pairs} pairs from {n_players} players: interceptions per target {co['int_rate']:.3f} (95% {ci['int_rate'][0]:.2f} to {ci['int_rate'][1]:.2f}),
  yards per target {co['ypt']:.3f} ({ci['ypt'][0]:.2f} to {ci['ypt'][1]:.2f}), completion rate {co['cmp_pct']:.3f} ({ci['cmp_pct'][0]:.2f} to
  {ci['cmp_pct'][1]:.2f}), missed-tackle rate {co['mt_pct']:.3f} ({ci['mt_pct'][0]:.2f} to {ci['mt_pct'][1]:.2f}). Intervals: 2,000 bootstrap draws resampling
  players (pairs share players). Missed tackles beat interceptions in {mt_ahead:.0%} of draws: no real difference. r of {co['int_rate']:.2f} means one season
  explains about {co['int_rate'] ** 2:.0%} of the next season's spread.
- Five-plus interception seasons (PFR counts, {MIN_TGT}+ targets both years): n={ex['n']}, {ex['this']:.2f} that season, {ex['nxt']:.2f} the next; all pairs
  {ex['all_nxt']:.2f} the next season.
- Hooker {SEASON}: {int(hz.tgt)} targets, {hz.ypt:.2f} yards/target, {int(hz.mt)} missed of {att26} attempts. {SEASON - 3}-{SEASON - 1}: {int(h3.tgt)} targets,
  {h3.ypt:.2f} yards/target, missed-tackle rate {h3.mt_pct:.3f} ({ordn(int(h3.rk_mt))} of {len(p3)}).
- Bills safeties {SEASON}: {int(bufs.tgt)} targets, {bufs.ypt:.2f} yards/target, {int(bufs.mt)} missed of {int(bufs.mt + bufs.tk)} attempts. League team safety
  groups: {lg_tm['ypt']:.2f} yards/target, missed-tackle rate {lg_tm['mt']:.3f}. By player (10+ targets):
  {'; '.join(f"{r.name} {int(r.tgt)} tgt, {r.ypt:.1f} yds/tgt, {int(r.mt)}/{int(r.mt + r.tk)} missed" for r in bp.itertuples())}.
- Trade terms, "most draft capital ... at the trade deadline under Beane" and Hooker playing alongside Bishop: buffalobills.com,
  "Bills land impact safety Amani Hooker in trade with Titans" and "'A difference maker'...", Nov. 10, 2026.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "The Hooker trade",
        "big": [[h_ints, "interceptions this season"], [career_ints, "in his career"]],
        "note": f"Big interception years rarely repeat: safeties with 5+ averaged about {ex['nxt']:.1f} the next season. Behind them: coverage about average this season, below average before, and better than two of the Bills safeties he joins.",
        "explainer": {"kicker": "What carries over", "title": "How well one season predicts the next.",
                      "text": f"For safeties, {y0}-{y1} (0 = not at all, 1 = perfectly):", "fmt": "score",
                      "bars": [[lab[k], round(co[k], 2)] for k in ("int_rate", "mt_pct", "ypt", "cmp_pct")]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
