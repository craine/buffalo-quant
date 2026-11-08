"""raw_* -> clean_*.

clean_plays            filtered offensive plays (pass or rush, EPA not null), REG + POST tagged
clean_drives           one row per offensive drive with points and red-zone flag
clean_team_week        one row per team-week, offense AND defense side, unfiltered + neutral
"""
import numpy as np
import pandas as pd

from src.db import connect, query, write

TEAM_NORMALIZE = {"OAK": "LV", "SD": "LAC", "STL": "LA", "LAR": "LA"}
DRIVE_POINTS = {"Touchdown": 7, "Field goal": 3}

PLAY_SQL = """
SELECT season, season_type, week, game_id, play_id, posteam, defteam, home_team, away_team,
       down, ydstogo, yardline_100, drive, fixed_drive_result,
       epa, success, wp, pass, rush, qb_dropback, sack, yards_gained,
       interception, fumble_lost, third_down_converted, third_down_failed,
       passer_player_name, play_type, qb_kneel, qb_spike, two_point_attempt
FROM raw_pbp
WHERE (pass = 1 OR rush = 1) AND epa IS NOT NULL
  AND play_type IN ('pass', 'run')
  AND COALESCE(qb_kneel, 0) = 0 AND COALESCE(qb_spike, 0) = 0
  AND COALESCE(two_point_attempt, 0) = 0
"""


def build_plays(con):
    p = query(PLAY_SQL, con=con)
    for c in ("posteam", "defteam", "home_team", "away_team"):
        p[c] = p[c].replace(TEAM_NORMALIZE)
    p["neutral"] = p.wp.between(0.10, 0.90).astype(int)
    p["is_dropback"] = (p.qb_dropback == 1).astype(int)
    p["is_designed_rush"] = ((p.rush == 1) & (p.qb_dropback != 1)).astype(int)
    p["explosive"] = (((p["pass"] == 1) & (p.yards_gained >= 20)) |
                      ((p.rush == 1) & (p.yards_gained >= 10))).astype(int)
    p["turnover"] = ((p.interception == 1) | (p.fumble_lost == 1)).astype(int)
    p["third_down"] = (p.down == 3).astype(int)
    return p.drop(columns=["qb_kneel", "qb_spike", "two_point_attempt"])


def build_drives(con):
    """One row per possession (nflverse fixed_drive within a game). The possessing team is the team with the most
    scrimmage plays in the drive, so a kickoff or extra-point row tagged to the drive can't create a fake one-play
    drive for the other team. Offensive points count a touchdown only when that team scored it (td_team == posteam)."""
    p = query("""
        SELECT season, season_type, week, game_id, fixed_drive, posteam, defteam, play_type, yardline_100,
               fixed_drive_result, touchdown, td_team
        FROM raw_pbp
        WHERE fixed_drive IS NOT NULL AND posteam IS NOT NULL AND defteam IS NOT NULL""", con=con)
    key = ["game_id", "fixed_drive"]
    scrim = p[p.play_type.isin(["pass", "run", "punt", "field_goal", "qb_kneel", "qb_spike", "no_play"])]
    pick = lambda x: (x.groupby(key + ["posteam", "defteam"]).size().rename("n").reset_index()
                      .sort_values("n", ascending=False).drop_duplicates(key)[key + ["posteam", "defteam"]])
    owner = pick(scrim)
    # possessions with no scrimmage snap (e.g. a kickoff returned as the half ends) still count as a drive
    rest = p.merge(owner[key], on=key, how="left", indicator=True)
    owner = pd.concat([owner, pick(rest[rest._merge == "left_only"].drop(columns="_merge"))], ignore_index=True)
    mine = p.merge(owner, on=key + ["posteam", "defteam"])
    d = mine.groupby(["season", "season_type", "week"] + key + ["posteam", "defteam"]).agg(
        result=("fixed_drive_result", "max"), best_yardline=("yardline_100", "min"),
        off_td=("touchdown", lambda s: int(((s == 1) & (mine.loc[s.index, "td_team"] == mine.loc[s.index, "posteam"])).any()))
    ).reset_index().rename(columns={"fixed_drive": "drive"})
    for c in ("posteam", "defteam"):
        d[c] = d[c].replace(TEAM_NORMALIZE)
    d["points"] = np.where(d.off_td == 1, 7, np.where(d.result == "Field goal", 3, 0)).astype(int)
    d["red_zone"] = (d.best_yardline <= 20).astype(int)
    d["rz_td"] = ((d.red_zone == 1) & (d.off_td == 1)).astype(int)
    return d.drop(columns="off_td")


def side_week(plays, drives, side):
    """side='off' groups by posteam, 'def' by defteam."""
    key = "posteam" if side == "off" else "defteam"
    g = plays.groupby(["season", "season_type", "week", "game_id", key])
    out = pd.DataFrame({
        "plays": g.size(),
        "epa_sum": g.epa.sum(),
        "success_sum": g.success.sum(),
        "neutral_plays": g.neutral.sum(),
        "neutral_epa_sum": g.apply(lambda x: x.epa[x.neutral == 1].sum(), include_groups=False),
        "dropbacks": g.is_dropback.sum(),
        "dropback_epa_sum": g.apply(lambda x: x.epa[x.is_dropback == 1].sum(), include_groups=False),
        "rushes": g.is_designed_rush.sum(),
        "rush_epa_sum": g.apply(lambda x: x.epa[x.is_designed_rush == 1].sum(), include_groups=False),
        "sacks": g.sack.sum(),
        "explosives": g.explosive.sum(),
        "turnovers": g.turnover.sum(),
        "third_downs": g.third_down.sum(),
        "third_conv": g.third_down_converted.sum(),
    })
    dg = drives.groupby(["season", "season_type", "week", "game_id", key])
    out = out.join(pd.DataFrame({"drives": dg.size(), "points": dg.points.sum(),
                                 "rz_trips": dg.red_zone.sum(), "rz_tds": dg.rz_td.sum()}))
    out = out.reset_index().rename(columns={key: "team"})
    out["side"] = side
    return out


def main():
    con = connect()
    plays = build_plays(con)
    drives = build_drives(con)
    write(plays, "clean_plays", con, if_exists="replace")
    write(drives, "clean_drives", con, if_exists="replace")
    tw = pd.concat([side_week(plays, drives, "off"), side_week(plays, drives, "def")])
    write(tw, "clean_team_week", con, if_exists="replace")
    con.commit()
    print(f"clean_plays {len(plays)}  clean_drives {len(drives)}  clean_team_week {len(tw)}")


if __name__ == "__main__":
    main()
