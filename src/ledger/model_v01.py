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


def prob_over(offense, defense, metric, threshold, season=2026, con=None):
    """Probability the OFFENSE's game value of `metric` vs this DEFENSE exceeds threshold."""
    gv = game_values(season, metric, con)
    off = gv[gv.side == "off"]
    lg = off.v.mean()
    o = off[off.team == offense].v.mean()
    d = gv[(gv.side == "def") & (gv.team == defense)].v.mean()
    expected = lg + SHRINK * ((o - lg) + (d - lg))
    dist = off.v - off.groupby("team").v.transform("mean")  # within-team game-to-game spread
    p = float(np.mean(dist + expected > threshold))
    return {"expected": expected, "p": p, "league": lg, "off_mean": o, "def_mean": d,
            "n_games_dist": len(dist)}
