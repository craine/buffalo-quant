"""Ledger model v0.1: empirical location-shift.

For a game-level metric X (e.g. dropback EPA in one game):
  expected = league_mean + shrink * [(team_side_mean - league_mean) + (opp_side_mean - league_mean)]
  P(X > t) = share of all 2026 team-games whose value, re-centered to `expected`, exceeds t.
Shrink 0.5 regresses 7-8 game samples halfway to the league. Simple, auditable, no betting inputs.
"""
import numpy as np
import pandas as pd

from src.db import query

SHRINK = 0.5
VERSION = "v0.1-locshift"
GAME_METRICS = {  # metric -> (numerator, denominator) in clean_team_week
    "dropback_epa": ("dropback_epa_sum", "dropbacks"),
    "rush_epa": ("rush_epa_sum", "rushes"),
    "sack_rate": ("sacks", "dropbacks"),
    "epa_play": ("epa_sum", "plays"),
}


def game_values(season, metric, con=None):
    n, d = GAME_METRICS[metric]
    tw = query(f"""SELECT game_id, week, team, side, {n} AS num, {d} AS den FROM clean_team_week
                   WHERE season = ? AND season_type='REG'""", params=(season,), con=con)
    tw["v"] = tw.num / tw.den
    return tw


def prob_over(offense, defense, metric, threshold, season=2026, con=None, off_override=None):
    """Probability the OFFENSE's game value of `metric` vs this DEFENSE exceeds threshold.

    off_override: optional league-relative offense level (e.g. a backup QB's own number minus the league
    average, from qb_relative). Replaces the team's season mean minus league; the defense side is unchanged.
    """
    gv = game_values(season, metric, con)
    off = gv[gv.side == "off"]
    lg = off.v.mean()
    o = off[off.team == offense].v.mean() if off_override is None else lg + off_override
    d = gv[(gv.side == "def") & (gv.team == defense)].v.mean()
    expected = lg + SHRINK * ((o - lg) + (d - lg))
    dist = off.v - off.groupby("team").v.transform("mean")  # within-team game-to-game spread
    p = float(np.mean(dist + expected > threshold))
    return {"expected": expected, "p": p, "league": lg, "off_mean": o, "def_mean": d,
            "n_games_dist": len(dist)}


QB_METRICS = {"dropback_epa": "epa", "sack_rate": "sack"}


def qb_relative(player_id, metric, seasons, con=None):
    """A QB's dropback-weighted value of `metric` relative to each season's league average.

    Dropbacks = qb_dropback plays with EPA, regular season, no two-point tries; the QB is
    COALESCE(passer_player_id, rusher_player_id) so scrambles count. Returns (relative value, dropbacks).
    """
    col = QB_METRICS[metric]
    seasons = tuple(int(s) for s in seasons)
    ph = ",".join("?" * len(seasons))
    base = (f"FROM raw_pbp WHERE season IN ({ph}) AND season_type='REG' AND qb_dropback=1 AND epa IS NOT NULL "
            "AND COALESCE(two_point_attempt,0)=0")
    lg = query(f"SELECT season, AVG({col}) v {base} GROUP BY season", params=seasons, con=con).set_index("season").v
    q = query(f"SELECT season, COUNT(*) n, AVG({col}) v {base} AND COALESCE(passer_player_id, rusher_player_id)=? GROUP BY season",
              params=seasons + (player_id,), con=con)
    if q.empty:
        raise ValueError(f"no dropbacks for {player_id} in {seasons}")
    rel = ((q.v - q.season.map(lg)) * q.n).sum() / q.n.sum()
    return float(rel), int(q.n.sum())
