"""Load older nflverse play-by-play (1999-2017) into raw_pbp_history, a separate table, for record and streak checks.

Kept apart from raw_pbp on purpose: existing models and pinned stories read raw_pbp, and some of their queries assume
it starts in 2018. Only the columns streak checks need are kept. Idempotent: re-running replaces a season's rows.
Usage: python -m src.ingest.pbp_history [--from 1999] [--to 2017]
"""
import argparse

import pandas as pd

from src.db import connect

BASE = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{}.parquet"
COLS = ["season", "season_type", "week", "game_id", "game_date", "play_id", "posteam", "defteam", "home_team", "away_team",
        "fixed_drive", "fixed_drive_result", "play_type", "pass", "rush", "qb_dropback", "sack", "interception",
        "fumble_lost", "touchdown", "pass_touchdown", "rush_touchdown", "return_touchdown", "td_team",
        "yards_gained", "passing_yards", "rushing_yards", "receiving_yards", "passer_player_id", "rusher_player_id",
        "receiver_player_id", "td_player_id", "passer_player_name", "rusher_player_name",
        "receiver_player_name", "td_player_name", "epa", "wp", "two_point_attempt", "qb_kneel", "total_home_score",
        "total_away_score"]
TABLE = "raw_pbp_history"


def load(season, con):
    df = pd.read_parquet(BASE.format(season), columns=COLS)
    for c in df.columns:
        if str(df[c].dtype) in ("string", "large_string") or df[c].dtype == object:
            df[c] = df[c].astype(object)
    try:
        con.execute(f"DELETE FROM {TABLE} WHERE season = ?", (season,))
    except Exception:
        pass
    df.to_sql(TABLE, con, if_exists="append", index=False)
    return len(df)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", type=int, default=1999)
    ap.add_argument("--to", dest="end", type=int, default=2017)
    a = ap.parse_args(argv)
    con = connect()
    for s in range(a.start, a.end + 1):
        n = load(s, con)
        con.commit()
        print(s, n, flush=True)
    con.execute(f"CREATE INDEX IF NOT EXISTS ix_{TABLE}_team ON {TABLE}(season, defteam, posteam)")
    con.commit()


if __name__ == "__main__":
    main()
