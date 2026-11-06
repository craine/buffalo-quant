"""raw_nhl_* -> clean_nhl_shots (every shot attempt, regular season, shootouts excluded).

Conventions (verified against the data 2026-11-06):
- details_eventOwnerTeamId is the SHOOTING team for goals, shots on goal, missed AND blocked shots.
- situationCode digits = [away goalie in net][away skaters][home skaters][home goalie in net].
- homeTeamDefendingSide (left/right) per play: home attacks the net on the opposite side.
  Nets sit at x = -89 (left) and +89 (right).
- Blocked-shot coordinates are where the block happened, so xG is trained on unblocked shots only.
"""
import numpy as np
import pandas as pd

from src.db import connect, query, write

SHOT_TYPES = ("goal", "shot-on-goal", "missed-shot", "blocked-shot")


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def build():
    con = connect()
    p = query(f"""
        SELECT p.game_id, p.season, p.eventId, p.sortOrder, p.typeDescKey AS ev, p.periodDescriptor_number AS period,
               p.periodDescriptor_periodType AS ptype, p.timeInPeriod, p.situationCode, p.homeTeamDefendingSide,
               p.details_eventOwnerTeamId AS team_id, p.details_xCoord AS x, p.details_yCoord AS y,
               p.details_zoneCode AS zone, p.details_shotType AS shot_type,
               COALESCE(p.details_shootingPlayerId, p.details_scoringPlayerId) AS shooter_id,
               p.details_goalieInNetId AS goalie_id,
               g.home_id, g.away_id, g.home, g.away
        FROM raw_nhl_plays p JOIN raw_nhl_games g ON g.game_id = p.game_id
        WHERE p.periodDescriptor_periodType != 'SO'""", con=con)
    for c in ("period", "team_id", "x", "y", "shooter_id", "goalie_id", "home_id", "away_id", "sortOrder"):
        p[c] = pd.to_numeric(p[c], errors="coerce")
    p = p.sort_values(["game_id", "sortOrder"]).reset_index(drop=True)
    p["t"] = (p.period - 1) * 1200 + p.timeInPeriod.map(secs)

    # previous-event context (within game)
    grp = p.groupby("game_id")
    p["prev_ev"] = grp.ev.shift(1)
    p["prev_team"] = grp.team_id.shift(1)
    p["prev_zone"] = grp.zone.shift(1)
    p["prev_t"] = grp.t.shift(1)
    p["prev_x"] = grp.x.shift(1)
    p["prev_y"] = grp.y.shift(1)

    s = p[p.ev.isin(SHOT_TYPES)].copy()
    s["is_home"] = (s.team_id == s.home_id).astype(int)
    s["opp_id"] = np.where(s.is_home == 1, s.away_id, s.home_id)
    s["team"] = np.where(s.is_home == 1, s.home, s.away)
    s["opp"] = np.where(s.is_home == 1, s.away, s.home)

    sc = s.situationCode.fillna("1551").str.zfill(4)
    away_g, away_sk, home_sk, home_g = (sc.str[i].astype(int) for i in range(4))
    s["skaters_for"] = np.where(s.is_home == 1, home_sk, away_sk)
    s["skaters_against"] = np.where(s.is_home == 1, away_sk, home_sk)
    s["empty_net_against"] = np.where(s.is_home == 1, away_g == 0, home_g == 0).astype(int)
    s["strength"] = s.skaters_for.astype(str) + "v" + s.skaters_against.astype(str)

    # net being attacked
    home_attacks_right = s.homeTeamDefendingSide.eq("left")
    attacks_right = np.where(s.is_home == 1, home_attacks_right, ~home_attacks_right)
    net_x = np.where(attacks_right, 89.0, -89.0)
    s["dist"] = np.hypot(net_x - s.x, s.y)
    s["angle"] = np.degrees(np.arctan2(np.abs(s.y), np.abs(net_x - s.x)))
    s["behind_net"] = (np.abs(s.x) > 89).astype(int)

    s["goal"] = (s.ev == "goal").astype(int)
    s["unblocked"] = (s.ev != "blocked-shot").astype(int)
    s["on_goal"] = s.ev.isin(["goal", "shot-on-goal"]).astype(int)
    dt = s.t - s.prev_t
    s["rebound"] = (s.prev_ev.isin(["shot-on-goal", "missed-shot"]) & (s.prev_team == s.team_id) & (dt <= 3)).astype(int)
    s["rush"] = ((s.prev_zone.isin(["N", "D"])) & (dt <= 4)).astype(int)
    s["dt_prev"] = dt.clip(upper=60)
    s["shot_type"] = s.shot_type.fillna("unknown")
    keep = ["game_id", "season", "eventId", "period", "t", "ev", "team_id", "team", "opp_id", "opp", "is_home",
            "shooter_id", "goalie_id", "x", "y", "dist", "angle", "behind_net", "shot_type", "strength",
            "skaters_for", "skaters_against", "empty_net_against", "rebound", "rush", "dt_prev",
            "goal", "unblocked", "on_goal"]
    s = s[keep]
    write(s, "clean_nhl_shots", con, if_exists="replace")
    con.commit()
    return s


if __name__ == "__main__":
    s = build()
    print(len(s), s.groupby("season").goal.sum().to_dict())
