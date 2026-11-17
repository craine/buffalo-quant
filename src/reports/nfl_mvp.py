"""Our NFL MVP vote after week 10: points added by each quarterback, with share of his team's offense and team record.

Writes reports/2026-wk11-nfl-mvp.md, two PNGs and a hero JSON. Every number is computed here from raw_pbp, raw_schedules
and raw_players; past MVP winners (for the check) are listed in MVP_WINNERS with the sources we used.
Pinned: 2026 regular season through week 10.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, INK, MUTED, RED
from src.reports import infographics as IG
from src.reports.nfl_playoff_odds import NAMES

OUT = ROOT / "reports"
SLUG = "2026-wk11-nfl-mvp"
SEASON, THRU = 2026, 10
AS_OF = "Tuesday, Nov. 17 (every week 10 game final)"
MIN_DROPBACKS = 150
PAST = range(2019, 2026)
MVP_WINNERS = {2019: ("Lamar Jackson", "00-0034796"), 2020: ("Aaron Rodgers", "00-0023459"), 2021: ("Aaron Rodgers", "00-0023459"),
               2022: ("Patrick Mahomes", "00-0033873"), 2023: ("Lamar Jackson", "00-0034796"), 2024: ("Josh Allen", "00-0034857"),
               2025: ("Matthew Stafford", "00-0026498")}   # AP MVP, keyed by gsis id
MVP_SOURCES = ["https://www.nfl.com/news/matthew-stafford-rams-qb-most-valuable-player-2025", "https://www.pro-football-reference.com/awards/ap-nfl-mvp-award.htm",
               "https://foxsports.com/stories/nfl/nfl-most-valuable-player-complete-list-winners-year"]
ALLEN = "00-0034857"
SRC = "Source: nflverse play-by-play. Regular season."
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
                     "font.size": 11})
PLAYS = """FROM raw_pbp WHERE season={s} AND season_type='REG' AND week<={w} AND epa IS NOT NULL
           AND COALESCE(two_point_attempt,0)=0 AND COALESCE(play_type,'')<>'no_play' AND COALESCE(qb_kneel,0)=0
           AND (qb_dropback=1 OR rush=1)"""


def finish(fig, title, sub, foot):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.905, sub, fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, f"{SRC}\n{foot}", fontsize=7.3, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.89))


def names():
    return query("SELECT gsis_id, display_name, position FROM raw_players").set_index("gsis_id")


def plays(season, week=18):
    p = query(f"""SELECT game_id, play_id, posteam AS team, qb_dropback, rush, epa, wp, passer_player_id, rusher_player_id,
                  receiver_player_id {PLAYS.format(s=season, w=week)}""")
    p["team"] = p.team.replace({"OAK": "LV", "SD": "LAC", "STL": "LA"})
    # The quarterback is responsible for every dropback (passes, sacks, scrambles); a runner for his designed runs.
    p["who"] = np.where(p.qb_dropback == 1, p.passer_player_id.fillna(p.rusher_player_id), p.rusher_player_id)
    return p


def qb_board(season, week=18):
    """Points added by every quarterback (dropbacks + his designed runs), share of his team's offensive plays."""
    p = plays(season, week)
    qbs = set(p.loc[p.qb_dropback == 1, "who"].dropna())
    q = p[p.who.isin(qbs)]
    g = q.groupby("who").agg(pts=("epa", "sum"), n=("epa", "size"), dropbacks=("qb_dropback", "sum"), team=("team", "last"))
    close = q[(q.wp >= 0.10) & (q.wp <= 0.90)].groupby("who").epa.sum()
    g["pts_close"] = close.reindex(g.index).fillna(0)
    team_n = p.groupby("team").size()
    g["share"] = g.n / g.team.map(team_n)
    g = g[g.dropbacks >= MIN_DROPBACKS].join(names())
    g["per_play"] = g.pts / g.n
    g["rank"] = g.pts.rank(ascending=False, method="min").astype(int)
    g["rank_close"] = g.pts_close.rank(ascending=False, method="min").astype(int)
    return g.sort_values("pts", ascending=False)


def non_qb_board(season, week=18):
    """Runners and receivers: points added on their runs and on passes thrown to them (the passer is credited too)."""
    p = plays(season, week)
    r = p[(p.rush == 1) & (p.qb_dropback != 1)][["rusher_player_id", "team", "epa"]].rename(columns={"rusher_player_id": "pid"})
    t = p[p.receiver_player_id.notna()][["receiver_player_id", "team", "epa"]].rename(columns={"receiver_player_id": "pid"})
    x = pd.concat([r, t]).groupby("pid").agg(pts=("epa", "sum"), n=("epa", "size"), team=("team", "last")).join(names())
    return x[x.position != "QB"].sort_values("pts", ascending=False)


def breakdown(season, week, ids):
    """Each quarterback's points added split into designed runs, sacks, turnovers and his other dropbacks."""
    p = plays(season, week)
    r = query(f"SELECT game_id, play_id, sack, interception, fumble_lost, fumbled_1_player_id, fumbled_2_player_id FROM raw_pbp WHERE season={season}")
    p = p[p.who.isin(ids)].merge(r, on=["game_id", "play_id"], how="left")
    own_fum = (p.fumble_lost == 1) & ((p.fumbled_1_player_id == p.who) | (p.fumbled_2_player_id == p.who))
    db, to = p.qb_dropback == 1, (p.interception == 1) | own_fum   # his own turnovers; a receiver's fumble stays in "rest"
    sk = (p.sack == 1) & ~to                 # a strip-sack counts once, as a turnover
    runs = ~db
    rest = db & ~to & ~sk
    out = pd.DataFrame({"runs": p[runs & ~to].groupby("who").epa.sum(), "n_runs": p[runs & ~to].groupby("who").size(),
                        "sacks": p[sk].groupby("who").epa.sum(), "n_sacks": p[sk].groupby("who").size(),
                        "to": p[to].groupby("who").epa.sum(), "n_to": p[to].groupby("who").size(),
                        "rest": p[rest].groupby("who").epa.sum(), "n_rest": p[rest].groupby("who").size()}).fillna(0)
    out["per_rest"] = out.rest / out.n_rest
    tot = p.groupby("who").epa.sum()
    assert np.allclose(out[["runs", "sacks", "to", "rest"]].sum(axis=1), tot.reindex(out.index)), "split doesn't add up"
    return out


def win_share(season):
    """Regular-season win share by team (ties count half), full season."""
    s = query(f"SELECT home_team, away_team, home_score, away_score FROM raw_schedules WHERE season={season} AND game_type='REG'").dropna()
    hw = (s.home_score > s.away_score) + 0.5 * (s.home_score == s.away_score)
    w = pd.concat([pd.Series(hw.to_numpy(), index=s.home_team), pd.Series(1 - hw.to_numpy(), index=s.away_team)])
    return w.groupby(level=0).mean().rename(lambda t: {"OAK": "LV", "SD": "LAC", "STL": "LA"}.get(t, t))


def records(season, week):
    s = query(f"SELECT home_team, away_team, home_score, away_score FROM raw_schedules WHERE season={season} AND game_type='REG' AND week<={week}")
    s = s.dropna(subset=["home_score"])
    r = {}
    for x in s.itertuples():
        for t, us, them in ((x.home_team, x.home_score, x.away_score), (x.away_team, x.away_score, x.home_score)):
            a = r.setdefault(t, [0, 0, 0])
            a[0 if us > them else (1 if us < them else 2)] += 1
    return {t: f"{a}-{b}" + (f"-{c}" if c else "") for t, (a, b, c) in r.items()}


def main():
    cur = qb_board(SEASON, THRU)
    rec = records(SEASON, THRU)
    cur["record"] = cur.team.map(rec)
    top = cur.head(10)
    lead = top.iloc[0]
    allen = cur.loc[ALLEN]
    nq = non_qb_board(SEASON, THRU)
    best_nq = nq.iloc[0]

    # ---- the check: would this measure have picked the real MVPs?
    hist, var = [], []
    for s in PAST:
        b = qb_board(s)
        win, wid = MVP_WINNERS[s]
        assert wid in b.index, (s, win)
        hit = b.loc[[wid]]
        hist.append(dict(season=s, winner=win, rank=int(hit["rank"].iloc[0]), our_top=b.iloc[0].display_name,
                         our_top_pts=float(b.iloc[0].pts), win_pts=float(hit.pts.iloc[0])))
        # variants, tested and not used: weight by team win share, by share of team plays
        wr = win_share(s)
        for name, sc in (("points x team win share", b.pts * b.team.map(wr)), ("points x share of team plays", b.pts * b.share)):
            var.append(dict(season=s, variant=name, rank=int(sc.rank(ascending=False, method="min").loc[wid])))
    hist = pd.DataFrame(hist)
    var = pd.DataFrame(var)
    vs = var.groupby("variant")["rank"].agg(n1=lambda r: int((r == 1).sum()), n3=lambda r: int((r <= 3).sum()), avg="mean")
    ws = vs.loc["points x team win share"]
    n1, n3 = int((hist["rank"] == 1).sum()), int((hist["rank"] <= 3).sum())
    miss = hist.loc[hist["rank"].idxmax()]

    words = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven']
    ordw = ['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']
    allen_rank_w = ordw[int(allen['rank'])] if allen['rank'] <= 10 else f"No. {int(allen['rank'])}"
    # ---- pin: the published board is saved; a later nflverse revision must not silently change a re-run
    pin = OUT / f"{SLUG}.board.csv"
    board = cur[["display_name", "team", "pts", "n", "share", "rank", "rank_close"]].round(4)
    board.index.name = "gsis_id"
    if pin.exists() and not __import__("os").environ.get("REPIN"):
        old = pd.read_csv(pin, index_col=0)
        same = old.index.equals(board.index) and np.allclose(old.pts.to_numpy(), board.pts.to_numpy(), atol=1e-3)
        assert same, "nflverse data changed since publication; this story is pinned. Publish a dated update instead (REPIN=1 only before publication)."
    else:
        board.to_csv(pin)
    # ---- graphic 1: the race board (top seven)
    IG.mvp_board([dict(name=r.display_name, team=NAMES.get(r.team, r.team), record=r.record, pts=float(r.pts), share=float(r.share),
                       highlight=(i == ALLEN)) for i, r in top.head(7).iterrows()],
                 OUT / "wk11-mvp-board.png", f"Buffalo Quant · MVP vote · after week {THRU}", f"{lead.display_name.split()[-1]} leads,<br>Allen is {allen_rank_w}",
                 "Every pass, sack, scramble and designed run, by how much it raised or lowered the points his team could expect from the drive.",
                 f"Ring = share of his team's offensive plays that were his. Source: nflverse play-by-play, weeks 1-{THRU}, "
                 f"{len(cur)} QBs with {MIN_DROPBACKS}+ dropbacks. Looking back over {PAST.start}-{PAST.stop - 1}, this count had the real MVP No. 1 in {n1} of 7 seasons, top 3 in {n3}.")

    # ---- chart 2: the check
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    cols = [BLUE if r == 1 else ("#7F93BF" if r <= 3 else "#9AA3B2") for r in hist["rank"]]
    ax.axhspan(0.5, 3.5, color="#EEF2FA", zorder=0)
    ax.scatter(hist.season, hist["rank"], s=160, color=cols, zorder=3)
    for r in hist.itertuples():
        ax.text(r.season, r.rank + 0.75, f"{r.winner}\n#{r.rank}", ha="center", va="top", fontsize=8.5, color=INK)
    ax.text(PAST.stop - 0.55, 2, "our top 3", ha="right", va="center", fontsize=8.5, color=MUTED)
    ax.set_ylim(max(hist["rank"]) + 2.2, 0.3); ax.set_yticks([1, 3, 5, 7, 9, 11])
    ax.set_ylabel("Real MVP's rank by points added"); ax.set_xticks(hist.season); ax.set_xlim(PAST.start - 0.6, PAST.stop - 0.4)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Looking back: the real MVP was No. 1 by this count in {n1} of 7 seasons",
           f"Each season's AP MVP and where he ranked by points added over the full regular season. Top 3 in {n3} of 7.",
           f"{PAST.start}-{PAST.stop - 1}. Winners from the AP's list (sources in the story).")
    fig.savefig(OUT / "wk11-mvp-check.png"); plt.close(fig)

    rows = "\n".join(f"| {k + 1} | {r.display_name} | {NAMES.get(r.team, r.team)} | {r.record} | {r.pts:.0f} | {r.share:.0%} | {r.rank_close} |"
                     for k, (_, r) in enumerate(top.iterrows()))
    nq_rows = "\n".join(f"| {r.display_name} | {r.position} | {NAMES.get(r.team, r.team)} | {r.pts:.0f} | {int(r.n)} |"
                        for _, r in nq.head(5).iterrows())
    ex = plays(SEASON, THRU)
    ex = ex[(ex.who == lead.name)].sort_values("epa", ascending=False).iloc[0]
    exd = query(f"SELECT down, ydstogo, yards_gained, desc, ep FROM raw_pbp WHERE game_id='{ex.game_id}' AND play_id={ex.play_id}").iloc[0]
    second = top.iloc[1]
    bd = breakdown(SEASON, THRU, [lead.name, ALLEN])
    A, L = bd.loc[ALLEN], bd.loc[lead.name]
    a24 = hist.set_index("season").loc[2024]
    assert a24.winner == "Josh Allen" and a24["rank"] == 1
    gap = lead.pts - allen.pts
    ln = lead.display_name.split()[-1]
    assert 0.3 < A.per_rest < L.per_rest < 0.5        # wording below: both about four-tenths, a bit more for the leader
    vol_pts = (L.n_rest - A.n_rest) * L.per_rest; rate_pts = (L.rest - A.rest) - vol_pts
    assert vol_pts > rate_pts > 0
    to_each = (-L.to / L.n_to, -A.to / A.n_to)
    _wp = cur.record.str.split("-").map(lambda r: (int(r[0]) + (0.5 * int(r[2]) if len(r) > 2 else 0)) / sum(int(x) for x in r))
    wsh = (cur.pts * _wp).rank(ascending=False, method="min")
    allen_ws_rank = int(wsh.loc[ALLEN])
    _pp = plays(SEASON, THRU)                  # the story's own play filter
    dbr = _pp.groupby("team").qb_dropback.mean()
    dbrk = dbr.rank(method="min")              # 1 = fewest dropbacks
    ordn_ = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
    few = lambda t: "the fewest" if dbrk[t] == 1 else (f"the {ordn_(int(dbrk[t]))}-fewest" if dbrk[t] <= 16 else ("the most" if dbrk[t] == len(dbr) else f"the {ordn_(len(dbr) + 1 - int(dbrk[t]))}-most"))

    md = f"""# Our MVP vote after 10 weeks: {lead.display_name}

**{lead.display_name}'s plays have been worth about {lead.pts:.0f} points more than an average offense would expect from the same situations,
more than any other quarterback. {second.display_name} is second at {second.pts:.0f}. Josh Allen is {allen_rank_w} at {allen.pts:.0f}.
We ran this measure over the last seven full seasons (the same seasons we used to choose it): this count had the real MVP No. 1 {words[n1]} times
and in its top three {words[n3]} times.**

*Points added for every quarterback with {MIN_DROPBACKS}+ dropbacks, through week {THRU}. Numbers as of {AS_OF}. We'll update the vote as the season goes.*

![The MVP race, by points added](wk11-mvp-board.png)

## Our ballot

| # | Player | Team | Team record | Points added | Share of team's plays | Rank, close games only |
|---|---|---|---|---|---|---|
{rows}

*Points added: every pass, sack and scramble, plus his own designed runs. Share of team's plays: the share of his team's offensive plays that were his passes, sacks, scrambles or runs. Close games only: the same count leaving out plays when either team was below a
10% chance to win.*

## Why Josh Allen is {allen_rank_w}

The same count had Josh Allen No. 1 in 2024, the year he won MVP. This year he's at {allen.pts:.0f}, {gap:.0f} behind {lead.display_name}. Most of the gap comes from one
thing: **Allen has thrown far less.** He wins some of it back with his legs and with less costly turnovers.

- **Throwing.** {ln} has {int(L.n_rest)} throws and scrambles (not counting sacks and his own turnovers); Allen has {int(A.n_rest)}, {int(L.n_rest - A.n_rest)} fewer. The Bills drop back to pass on
  {dbr['BUF']:.0%} of their plays, {"one of the three lowest rates" if dbrk['BUF'] <= 3 else few('BUF')} in the NFL; the {NAMES[lead.team]}, {dbr[lead.team]:.0%}, {few(lead.team).replace('the most', 'the highest')}. Throw for throw {ln} has been a little better: each of those plays is
  worth about four-tenths of a point, a bit more for {ln}. The bigger difference is how many: {ln}'s add up to about {L.rest:.0f} points, Allen's to about {A.rest:.0f}.
- **Sacks and turnovers.** Allen has more of them ({int(A.n_sacks)} sacks and {int(A.n_to)} turnovers of his own, against {ln}'s {int(L.n_sacks)} and {int(L.n_to)}; a sack that loses the ball counts once, as a turnover), but {ln}'s turnovers have been
  costlier: about {to_each[0]:.1f} points each, to {to_each[1]:.1f} for Allen's. All told they've cost Allen about {-(A.sacks + A.to):.0f} points and {ln} about {-(L.sacks + L.to):.0f}.
- **Running.** Allen's {int(A.n_runs)} designed runs have added about {A.runs:.0f} points, against {L.runs:.0f} for {ln}.

Add those up and you get each total: {L.rest:.0f} - {-(L.sacks + L.to):.0f} + {L.runs:.0f} = {lead.pts:.0f} for {ln}, {A.rest:.0f} - {-(A.sacks + A.to):.0f} + {A.runs:.0f} = {allen.pts:.0f} for Allen (rounded).

So the biggest reason he's {allen_rank_w} is volume. You can read that two ways: he's had fewer chances to help, so he's helped less, or a count
like ours undersells a quarterback on a team that runs well. Decide for yourself.

**What about the Bills' {allen.record} record?** It isn't in our score. Looking back over the last seven seasons, giving extra credit for team wins ranked the real MVP
No. 1 less often ({words[int(ws.n1)]} times vs. {words[n1]}), in the top three just as often ({words[int(ws.n3)]}), and a bit closer to the top on average. With it, Allen would be
No. {allen_ws_rank} this year. This is our vote on who has added the most, not a guess at the voters', so we left record out.

## How we score it

**Points added.** Every snap starts from a spot where an average offense can expect a certain number of points from the drive.
A good play raises that number and a bad one lowers it. {lead.display_name}'s best play this season: on {['', 'first', 'second', 'third', 'fourth'][int(exd.down)]}-and-{int(exd.ydstogo)},
from a spot where an average offense could expect just over {int(exd.ep)} points, a {int(exd.yards_gained)}-yard {'touchdown' if 'TOUCHDOWN' in exd.desc else 'gain'} added about
{ex.epa:.1f} points to that. Add up every play a quarterback is responsible for, good and bad, and you get his points added. A quarterback
who throws an interception or takes a sack loses points the same way. {lead.display_name}'s {int(lead.n)} plays add up to about {lead.pts:.0f}.

**Why it's a quarterback.** Every pass starts with him, so he touches far more plays than anyone else. The best non-quarterback,
{best_nq.display_name} ({best_nq.position}, {NAMES.get(best_nq.team, best_nq.team)}), is at about {best_nq.pts:.0f} (see "Best of the rest" below), and a catch counts for the thrower too, so his total overlaps with his quarterback's.

**Share of the offense.** The table's "share of team's plays" column is context only; adding it to the score didn't match past MVPs better.

**The check.** We ran the same count over full past seasons and asked where each real AP MVP ranked:

![The check](wk11-mvp-check.png)

The miss was {int(miss.season)}: {miss.winner} won the award but ranked No. {int(miss['rank'])} by points added ({miss.win_pts:.0f}, behind
{miss.our_top}'s {miss.our_top_pts:.0f}). Voters see things this count doesn't, so treat it as our vote, not a forecast of theirs.

## Best of the rest (not quarterbacks)

| Player | Pos. | Team | Points added | Runs + passes thrown his way |
|---|---|---|---|---|
{nq_rows}

*A catch's points also count for the quarterback who threw it.*

## What about defense?

We don't rank defenders here. We can't yet split a defense's points saved among its players fairly. It's next on our list.

## For the stat-heads

- Points added = nflverse expected points added (EPA), regular season weeks 1-{THRU}, excluding two-point tries, kneels and
  no-plays. QB credit: all dropbacks (passer, or rusher on scrambles) plus designed runs where he is the rusher. Minimum
  {MIN_DROPBACKS} dropbacks. Example play: game {ex.game_id}, play {int(ex.play_id)}, EP {exd.ep:.2f}, EPA {ex.epa:+.2f}.
- Allen split (QB's own turnovers only; receiver fumbles stay in throws): per throw/scramble {L.per_rest:.3f} ({ln}) vs {A.per_rest:.3f} (Allen);
  of the {L.rest - A.rest:.1f}-point throwing gap, about {vol_pts:.1f} is volume ({int(L.n_rest - A.n_rest)} plays x {L.per_rest:.3f}) and {rate_pts:.1f} is value per play.
  Dropback rate uses this story's play filter; the Bills' rank among the lowest is within a fraction of a play of the next team.
- Close-games rank: same sum over plays with win probability 0.10-0.90.
- Check: full regular seasons {PAST.start}-{PAST.stop - 1}; real MVP's rank by this measure:
  {'; '.join(f"{r.season} {r.winner} #{r.rank}" for r in hist.itertuples())} (mean rank {hist['rank'].mean():.1f}). Variants tested on the same seven seasons and not
  used: {'; '.join(f"{v}: No. 1 {int(r.n1)}, top 3 {int(r.n3)}, mean rank {r.avg:.1f} ({', '.join(f'{x.season} #{x.rank}' for x in var[var.variant == v].itertuples())})" for v, r in vs.iterrows())}.
  The measure was chosen on these same seasons, so the check is in-sample. Winners matched by gsis id.
  MVP winners from {' and '.join(MVP_SOURCES)}.
- Non-QB credit: designed runs plus every target (full EPA), so it double counts with the passer.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Our MVP vote",
        "big": [[f"{lead.pts:.0f}", f"{lead.display_name}: points added beyond an average offense"], [f"#{int(allen['rank'])}", f"Josh Allen, Bills ({allen.pts:.0f} points added)"]],
        "note": f"After 10 weeks. Run back over the last 7 full seasons, this count had the real MVP No. 1 {words[n1]} times and top 3 {words[n3]} times.",
        "explainer": {"kicker": "The vote", "title": "Points added, top three.", "text": "Points each quarterback has added beyond an average offense, through week 10:",
                      "fmt": "num", "bars": [[r.display_name, int(round(float(r.pts)))] for _, r in top.head(3).iterrows()]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
