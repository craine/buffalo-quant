"""nflverse-data releases -> raw_* tables. Idempotent: a season's rows are replaced, never duplicated.

Fails loudly if a source is unreachable. Never substitutes data.
"""
import io
import sys
import urllib.request

import pandas as pd
import yaml

from src.db import ROOT, connect, write

BASE = "https://github.com/nflverse/nflverse-data/releases/download/"
SOURCES = {  # config key -> (table, path template)
    "pbp": ("raw_pbp", "pbp/play_by_play_{y}.parquet"),
    "team_week": ("raw_team_week", "stats_team/stats_team_week_{y}.parquet"),
    "player_week": ("raw_player_week", "stats_player/stats_player_week_{y}.parquet"),
    "pfr_pass": ("raw_pfr_pass", "pfr_advstats/advstats_week_pass_{y}.parquet"),
    "pfr_def": ("raw_pfr_def", "pfr_advstats/advstats_week_def_{y}.parquet"),
    "ftn": ("raw_ftn", "ftn_charting/ftn_charting_{y}.parquet"),
    "participation": ("raw_participation", "pbp_participation/pbp_participation_{y}.parquet"),
    "snap_counts": ("raw_snap_counts", "snap_counts/snap_counts_{y}.parquet"),
    "rosters_weekly": ("raw_rosters_weekly", "weekly_rosters/roster_weekly_{y}.parquet"),   # verified 2026-11-12
}
SINGLE_FILE = {"raw_schedules": "schedules/games.parquet",
               "raw_ngs_passing": "nextgen_stats/ngs_passing.parquet",
               "raw_players": "players/players.parquet"}   # master list: gsis_id <-> pfr_id; verified 200 on 2026-11-12


def fetch(path):
    with urllib.request.urlopen(BASE + path, timeout=300) as r:
        return pd.read_parquet(io.BytesIO(r.read()))


def table_exists(con, t):
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()


def load_season(con, table, df, season):
    if table_exists(con, table):
        con.execute(f"DELETE FROM {table} WHERE season = ?", (season,))
        have = {r[1] for r in con.execute(f"PRAGMA table_info({table})")}
        for col in df.columns:  # source schemas grow over the years: add, never drop
            if col not in have:
                con.execute(f'ALTER TABLE {table} ADD COLUMN "{col}"')
    write(df, table, con)


def main(argv=None):
    """make ingest: everything in config/seasons.yaml. Subsets for scheduled jobs:
    --only player_week,snap_counts   sources (config keys) to load; single-file tables load only if named too (e.g. raw_schedules)
    --from 2026                      first season to load (default: the config's)"""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--from", dest="start", type=int)
    a = ap.parse_args(argv)
    only = {x for x in a.only.split(",") if x}
    unknown = only - set(SOURCES) - set(SINGLE_FILE)
    if unknown:
        ap.error(f"unknown --only name(s): {sorted(unknown)}; use {sorted(SOURCES)} or {sorted(SINGLE_FILE)}")
    cfg = yaml.safe_load(open(ROOT / "config" / "seasons.yaml"))
    con = connect()
    for table, path in SINGLE_FILE.items():
        if only and table not in only:
            continue
        write(fetch(path), table, con, if_exists="replace")
        print(table, "ok", flush=True)
    for key, (table, tmpl) in SOURCES.items():
        if only and key not in only:
            continue
        lo, hi = cfg[key]
        lo = max(lo, a.start) if a.start else lo
        for y in range(lo, hi + 1):
            try:
                df = fetch(tmpl.format(y=y))
            except Exception as e:  # stop, do not substitute
                sys.exit(f"BLOCKED: {table} {y}: {e}")
            if "season" not in df.columns:
                df["season"] = y
            load_season(con, table, df, y)
            print(table, y, len(df), flush=True)
        con.commit()
    con.close()


if __name__ == "__main__":
    main()
