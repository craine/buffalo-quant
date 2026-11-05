"""Opponent adjustment and independent cross-checks.

adjusted defensive EPA for game g = (EPA/play allowed in g) - (opponent's offensive EPA/play
in all its OTHER games that season). Negative = held the opponent below its norm.
"""
import pandas as pd

from src.db import query


def opp_adjusted_defense(team, season, con=None):
    tw = query("""SELECT season, week, game_id, team, side, plays, epa_sum, dropbacks, dropback_epa_sum
                  FROM clean_team_week WHERE season_type='REG' AND season = ?""", params=(season,), con=con)
    off = tw[tw.side == "off"]
    d = tw[(tw.side == "def") & (tw.team == team)]
    rows = []
    for _, g in d.iterrows():
        opp_row = off[(off.game_id == g.game_id) & (off.team != team)].iloc[0]
        opp = opp_row.team
        other = off[(off.team == opp) & (off.game_id != g.game_id)]
        base = other.epa_sum.sum() / other.plays.sum()
        base_db = other.dropback_epa_sum.sum() / other.dropbacks.sum()
        rows.append({"week": g.week, "opp": opp, "plays": g.plays,
                     "epa_allowed": g.epa_sum / g.plays, "opp_off_epa_other": base,
                     "adj_epa": g.epa_sum / g.plays - base,
                     "db_epa_allowed": g.dropback_epa_sum / g.dropbacks, "opp_db_epa_other": base_db,
                     "adj_db_epa": g.dropback_epa_sum / g.dropbacks - base_db})
    return pd.DataFrame(rows)


def league_adjusted_rank(season, con=None):
    """Play-weighted opponent-adjusted EPA/play allowed for every defense; rank 1 = best."""
    teams = query("SELECT DISTINCT team FROM clean_team_week WHERE season=? AND side='def'",
                  params=(season,), con=con).team
    out = []
    for t in teams:
        a = opp_adjusted_defense(t, season, con)
        out.append({"team": t, "adj_epa": (a.adj_epa * a.plays).sum() / a.plays.sum(),
                    "adj_db_epa": (a.adj_db_epa * a.plays).sum() / a.plays.sum()})
    df = pd.DataFrame(out)
    df["adj_epa_rk"] = df.adj_epa.rank(method="min").astype(int)
    df["adj_db_epa_rk"] = df.adj_db_epa.rank(method="min").astype(int)
    return df


def pass_defense_crosscheck(season, con=None):
    """Second, EPA-free view of pass defense straight from raw_pbp: yards per dropback,
    dropback success rate. Rank 1 = best (lowest)."""
    df = query("""SELECT defteam AS team, AVG(yards_gained) AS yds_per_db, AVG(success) AS db_success
                  FROM raw_pbp WHERE season = ? AND season_type='REG' AND qb_dropback = 1
                    AND play_type IN ('pass','run') AND epa IS NOT NULL GROUP BY defteam""",
               params=(season,), con=con)
    df["yds_per_db_rk"] = df.yds_per_db.rank(method="min").astype(int)
    df["db_success_rk"] = df.db_success.rank(method="min").astype(int)
    return df
