"""Weekly Streak Watch: every active NFL streak worth a mention, ranked against every streak since 1999.

Internal tip sheet, not a published story. Anything we post from it still goes through the four-stage review.
Usage: python -m src.reports.streak_watch [--week 10]
Writes reports/streak-watch/<season>-wk<week>.md and .csv.
"""
import argparse
from pathlib import Path

import pandas as pd

from src.db import query
from src.metrics.streaks import notable, plays, scan

SEASON = 2026
OUT = Path("reports/streak-watch")


def names():
    sql = " UNION ".join(f"SELECT {c}_id id, {c}_name nm FROM {t}" for t in ("raw_pbp", "raw_pbp_history")
                         for c in ("td_player", "passer_player", "rusher_player", "receiver_player"))
    return query(sql).dropna().drop_duplicates("id").set_index("id").nm


def line(r):
    who = r["name"] if r.who == "player" else r.team
    s = f"**{who}: {r.length} straight {r.kind}.** "
    if r.franchise_rank == 1:
        s += f"Longest for {r.team} since at least 1999. "
    elif pd.notna(r.last_as_long):
        s += f"Longest for {r.team} since {int(r.last_as_long)} ({int(r.last_as_long_len)} then). "
    s += f"#{r.league_rank} of {r.league_runs:,} such runs league-wide since 1999."
    if r.unit == "drives":
        s += " Our drive count can run a few higher than official counts (end-of-half possessions)."
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, required=True)
    a = ap.parse_args(argv)
    p = plays()
    assert p[p.season == SEASON].week.max() >= a.week, "play-by-play doesn't reach this week yet"
    allr = scan(p)
    n = notable(allr).copy()
    n["name"] = n.key.map(names()).fillna(n.key)
    n["bills"] = n.team == "BUF"
    n = n.sort_values(["bills", "league_rank"], ascending=[False, True])
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / f"{SEASON}-wk{a.week:02d}"
    n.to_csv(f"{stem}.csv", index=False)
    md = [f"# Streak Watch — {SEASON} through week {a.week}", "",
          "Internal tip sheet. Data: nflverse play-by-play 1999 on, regular season and playoffs together (a playoff "
          "game continues a streak). Records here mean \"since 1999\", the start of our data. Check any claim against "
          "the official record book before saying \"franchise record\" or \"NFL record\".", "", "## Bills", ""]
    md += [f"- {line(r)}" for _, r in n[n.bills].iterrows()] or ["- Nothing notable this week."]
    md += ["", "## Around the league", ""] + [f"- {line(r)}" for _, r in n[~n.bills].iterrows()]
    Path(f"{stem}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
