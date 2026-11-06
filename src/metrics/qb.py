"""Quarterback play tables: clean_plays dropbacks joined to FTN, participation and PFR.

Eras for Josh Allen (offensive play-caller), verified from reporting 2026-11-05:
  daboll      2018 - 2021
  dorsey      2022 - 2023 week 10   (fired Nov 14 2023 after the week 10 loss to DEN)
  brady_oc    2023 week 11 - 2025   (first game: week 11 vs NYJ)
  brady_hc    2026 -                (Brady head coach AND still the play-caller; Carmichael is a
                                     non-play-calling OC. Verified from reporting 2026-11-05.)
"""
import numpy as np
import pandas as pd

from src.db import query

ERA_ORDER = ["daboll", "dorsey", "brady_oc", "brady_hc"]
ERA_LABEL = {"daboll": "Daboll OC\n2018-21", "dorsey": "Dorsey OC\n2022-23 wk10",
             "brady_oc": "Brady OC\n2023 wk11-25", "brady_hc": "Brady HC + play-caller\n2026"}


def buf_era(season, week):
    if season <= 2021:
        return "daboll"
    if season == 2022 or (season == 2023 and week <= 10):
        return "dorsey"
    if season <= 2025:
        return "brady_oc"
    return "brady_hc"


def dropbacks(seasons=(2018, 2026), season_type="REG", con=None):
    """All league dropbacks with weather, FTN and participation fields attached."""
    d = query(f"""
        SELECT p.season, p.week, p.game_id, p.play_id, p.posteam, p.defteam, COALESCE(r.passer_player_name, r.rusher_player_name) AS qb,
               p.epa, p.success, p.sack, p.down, p.ydstogo, p.yardline_100, p.neutral,
               COALESCE(r.passer_player_id, r.rusher_player_id) AS qb_id, r.cpoe, r.air_yards, r.qb_scramble, r.interception,
               r.fumble_lost, r.temp, r.wind, r.roof, r.pass_attempt, r.complete_pass,
               r.qb_epa, r.pass_oe, r.xpass
        FROM clean_plays p JOIN raw_pbp r ON r.game_id = p.game_id AND r.play_id = p.play_id
        WHERE p.is_dropback = 1 AND p.season_type = ? AND p.season BETWEEN ? AND ?""",
              params=(season_type, *seasons), con=con)
    ftn = query("""SELECT nflverse_game_id AS game_id, CAST(nflverse_play_id AS INTEGER) AS play_id,
                          is_qb_out_of_pocket, is_interception_worthy, is_play_action, is_rpo, is_screen_pass,
                          is_throw_away, n_blitzers, n_pass_rushers AS ftn_rushers, is_qb_fault_sack
                   FROM raw_ftn""", con=con)
    part = query("""SELECT nflverse_game_id AS game_id, CAST(play_id AS INTEGER) AS play_id, was_pressure,
                           time_to_throw, defense_man_zone_type AS man_zone, defense_coverage_type AS coverage,
                           number_of_pass_rushers AS rushers
                    FROM raw_participation""", con=con)
    d["play_id"] = d.play_id.astype(int)
    d = d.merge(ftn, on=["game_id", "play_id"], how="left").merge(part, on=["game_id", "play_id"], how="left")
    d["dome"] = d.roof.isin(["dome", "closed"]).astype(int)
    return d


ALLEN_ID = "00-0034857"  # match by gsis id: nflverse spells him both "J.Allen" and "Jos.Allen"


def is_allen(df):
    return df.qb_id == ALLEN_ID


def names(df):
    """Most common display name per qb_id."""
    return df.groupby("qb_id").qb.agg(lambda s: s.mode().iat[0] if s.notna().any() else None)


def allen_runs(con=None):
    """Josh Allen designed runs (non-scramble rushes) and scrambles."""
    return query("""SELECT p.season, p.week, p.epa, p.success, r.qb_scramble
                    FROM clean_plays p JOIN raw_pbp r ON r.game_id = p.game_id AND r.play_id = p.play_id
                    WHERE p.season_type='REG' AND r.rusher_player_id = ?
                      AND p.rush = 1""", params=(ALLEN_ID,), con=con)


def rate(x):
    x = pd.to_numeric(x, errors="coerce")
    return x.mean() if x.notna().any() else np.nan
