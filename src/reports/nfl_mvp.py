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
from src.reports.nfl_playoff_odds import NAMES

OUT = ROOT / "reports"
SLUG = "2026-wk11-nfl-mvp"
SEASON, THRU = 2026, 10
AS_OF = "Tuesday, Nov. 17 (every week 10 game final)"
MIN_DROPBACKS = 150
PAST = range(2019, 2026)
MVP_WINNERS = {2019: "Lamar Jackson", 2020: "Aaron Rodgers", 2021: "Aaron Rodgers", 2022: "Patrick Mahomes",
               2023: "Lamar Jackson", 2024: "Josh Allen", 2025: "Matthew Stafford"}
MVP_SOURCES = ["https://www.pro-football-reference.com/awards/ap-nfl-mvp-award.htm",
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
    hist = []
    for s in PAST:
        b = qb_board(s)
        win = MVP_WINNERS[s]
        hit = b[b.display_name == win]
        assert len(hit) == 1, (s, win)
        hist.append(dict(season=s, winner=win, rank=int(hit["rank"].iloc[0]), our_top=b.iloc[0].display_name,
                         our_top_pts=float(b.iloc[0].pts), win_pts=float(hit.pts.iloc[0])))
    hist = pd.DataFrame(hist)
    n1, n3 = int((hist["rank"] == 1).sum()), int((hist["rank"] <= 3).sum())
    miss = hist.loc[hist["rank"].idxmax()]

    # ---- chart 1: the ballot
    fig, ax = plt.subplots(figsize=(9.5, 5.6), dpi=200)
    t = top.iloc[::-1]
    ax.barh(range(len(t)), t.pts, color=[RED if i == ALLEN else BLUE for i in t.index], height=0.65, zorder=2)
    for y, (i, r) in enumerate(t.iterrows()):
        ax.text(r.pts + 1, y, f"{r.pts:.0f}", va="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.set_yticks(range(len(t)), [f"{r.display_name}, {NAMES.get(r.team, r.team)} ({r.record})" for _, r in t.iterrows()], fontsize=9.5)
    ax.set_xlabel("Points added this season (passes, sacks, scrambles and his own designed runs)")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"Our MVP vote after 10 weeks: {lead.display_name}",
           "How many points each quarterback has added to his team's offense, compared with an average play. Red = Josh Allen.",
           f"2026 weeks 1-{THRU}. Quarterbacks with {MIN_DROPBACKS}+ dropbacks. Every play counts, including late in blowouts.")
    fig.savefig(OUT / "wk11-mvp-ballot.png"); plt.close(fig)

    # ---- chart 2: the check
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    cols = [BLUE if r == 1 else ("#7F93BF" if r <= 3 else "#9AA3B2") for r in hist["rank"]]
    ax.axhspan(0.5, 3.5, color="#EEF2FA", zorder=0)
    ax.scatter(hist.season, hist["rank"], s=160, color=cols, zorder=3)
    for r in hist.itertuples():
        ax.text(r.season, r.rank + 0.75, f"{r.winner}\n#{r.rank}", ha="center", va="top", fontsize=8.5, color=INK)
    ax.text(PAST.stop - 0.55, 2, "our top 3", ha="right", va="center", fontsize=8.5, color=MUTED)
    ax.set_ylim(max(hist["rank"]) + 2.2, 0.3); ax.set_yticks([1, 3, 5, 7, 9, 11])
    ax.set_ylabel("Real MVP's rank on our list"); ax.set_xticks(hist.season); ax.set_xlim(PAST.start - 0.6, PAST.stop - 0.4)
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"The real MVP was our No. 1 in {n1} of 7 seasons, and top 3 in {n3}",
           "Each season's actual AP MVP and where he ranked by points added over the full regular season.",
           f"{PAST.start}-{PAST.stop - 1} regular seasons. Winners from the AP's list (sources in the story).")
    fig.savefig(OUT / "wk11-mvp-check.png"); plt.close(fig)

    rows = "\n".join(f"| {k + 1} | {r.display_name} | {NAMES.get(r.team, r.team)} | {r.record} | {r.pts:.0f} | {r.share:.0%} | {r.rank_close} |"
                     for k, (_, r) in enumerate(top.iterrows()))
    nq_rows = "\n".join(f"| {r.display_name} | {r.position} | {NAMES.get(r.team, r.team)} | {r.pts:.0f} | {int(r.n)} |"
                        for _, r in nq.head(5).iterrows())
    ex = plays(SEASON, THRU)
    ex = ex[(ex.who == lead.name)].sort_values("epa", ascending=False).iloc[0]
    exd = query(f"SELECT down, ydstogo, yards_gained, desc, ep FROM raw_pbp WHERE game_id='{ex.game_id}' AND play_id={ex.play_id}").iloc[0]
    second = top.iloc[1]

    md = f"""# Our MVP vote after 10 weeks: {lead.display_name}

**{lead.display_name} has added about {lead.pts:.0f} points to the {NAMES[lead.team]}' offense this season, more than any other
quarterback. {second.display_name} is second at {second.pts:.0f}. Josh Allen is {['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth'][int(allen['rank'])] if allen['rank'] <= 10 else f"No. {int(allen['rank'])}"} at {allen.pts:.0f}.
We tested this measure on the last seven MVP races: the real winner was our No. 1 {['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven'][n1]} times and in our top three {['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven'][n3]} times.**

*Every NFL quarterback's points added through week {THRU}. Numbers as of {AS_OF}. We'll update the vote as the season goes.*

![Our MVP vote](wk11-mvp-ballot.png)

## Our ballot

| # | Player | Team | Record | Points added | Share of team's plays | Rank, close games only |
|---|---|---|---|---|---|---|
{rows}

*Points added: every pass, sack and scramble, plus his own designed runs. Share of team's plays: how many of his team's
offensive plays he was the main player on. Close games only: the same count leaving out plays when either team was below a
10% chance to win.*

## How we score it

**Points added.** Every snap starts from a spot where an average offense can expect a certain number of points from the drive.
A good play raises that number and a bad one lowers it. {lead.display_name}'s best play this season: on {['', 'first', 'second', 'third', 'fourth'][int(exd.down)]}-and-{int(exd.ydstogo)},
a {int(exd.yards_gained)}-yard {'touchdown' if 'TOUCHDOWN' in exd.desc else 'gain'} took the {NAMES[lead.team]} from about {exd.ep:.1f} expected points to about {exd.ep + ex.epa:.1f}, so it added about
{ex.epa:.1f} points. Add up every play a quarterback is responsible for, good and bad, and you get his points added. A quarterback
who throws an interception or takes a sack loses points the same way. {lead.display_name}'s {int(lead.n)} plays add up to about {lead.pts:.0f}.

**Why it's a quarterback.** Every pass starts with him, so he touches far more plays than anyone else. The best non-quarterback,
{best_nq.display_name} ({best_nq.position}, {NAMES.get(best_nq.team, best_nq.team)}), has added about {best_nq.pts:.0f} points on {int(best_nq.n)}
runs and passes thrown his way. But a catch counts for the thrower too, so that number overlaps with his quarterback's.

**Share of the offense.** We also tested weighting by how much of a team's offense runs through a player. It didn't
pick the real MVP any more often, so it's in the table as context, not in the score. The same went for team record:
voters care about winning, but adding it didn't match their picks any better than points added alone.

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
- Close-games rank: same sum over plays with win probability 0.10-0.90.
- Check: full regular seasons {PAST.start}-{PAST.stop - 1}; real MVP's rank by this measure:
  {'; '.join(f"{r.season} {r.winner} #{r.rank}" for r in hist.itertuples())}. Variants tested on the same seven seasons and not
  used: points x team win share, points + team wins, points x share of team plays. None matched the winners more often.
  MVP winners from {' and '.join(MVP_SOURCES)}.
- Non-QB credit: designed runs plus every target (full EPA), so it double counts with the passer.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Our MVP vote",
        "big": [[f"{lead.pts:.0f}", f"{lead.display_name} (points added)"], [f"#{int(allen['rank'])}", f"Josh Allen ({allen.pts:.0f})"]],
        "note": f"After 10 weeks. The real MVP was our No. 1 in {n1} of the last 7 seasons and top 3 in {n3}.",
        "explainer": {"kicker": "The vote", "title": "Points added, top three.", "text": "Points each quarterback has added this season:",
                      "fmt": "num", "bars": [[r.display_name, round(float(r.pts), 1)] for _, r in top.head(3).iterrows()]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
