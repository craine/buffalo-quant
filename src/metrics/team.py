"""Season-level team metrics with league ranks, built from clean_team_week sums.

Rank 1 = best for that side. For defense, lower EPA/success/explosive/etc. is better;
higher sack and turnover rate is better. Offense is the mirror image.
"""
import pandas as pd

from src.db import query

RATE_DEFS = {  # metric -> (numerator, denominator)
    "epa_play": ("epa_sum", "plays"),
    "epa_play_neutral": ("neutral_epa_sum", "neutral_plays"),
    "success_rate": ("success_sum", "plays"),
    "dropback_epa": ("dropback_epa_sum", "dropbacks"),
    "rush_epa": ("rush_epa_sum", "rushes"),
    "sack_rate": ("sacks", "dropbacks"),
    "explosive_rate": ("explosives", "plays"),
    "turnover_rate": ("turnovers", "plays"),
    "third_down_rate": ("third_conv", "third_downs"),
    "rz_td_rate": ("rz_tds", "rz_trips"),
    "pts_per_drive": ("points", "drives"),
}
LABELS = {
    "epa_play": "EPA/play", "epa_play_neutral": "EPA/play (neutral WP 10-90%)",
    "success_rate": "Success rate", "dropback_epa": "Dropback EPA", "rush_epa": "Designed-rush EPA",
    "sack_rate": "Sack rate", "explosive_rate": "Explosive play rate", "turnover_rate": "Turnover rate",
    "third_down_rate": "3rd-down conversion rate", "rz_td_rate": "Red-zone TD rate",
    "pts_per_drive": "Points per drive",
}
# metrics where a HIGHER value is good for the offense
OFFENSE_GOOD_HIGH = set(RATE_DEFS) - {"sack_rate", "turnover_rate"}


def season_table(side, seasons, season_type="REG", max_week=None, con=None):
    sql = "SELECT * FROM clean_team_week WHERE side = ? AND season_type = ?"
    tw = query(sql, params=(side, season_type), con=con)
    tw = tw[tw.season.isin(seasons)]
    if max_week is not None:
        tw = tw[tw.week <= max_week]
    sums = tw.groupby(["season", "team"]).sum(numeric_only=True)
    out = pd.DataFrame(index=sums.index)
    out["games"] = tw.groupby(["season", "team"]).game_id.nunique()
    out["plays"] = sums.plays
    for m, (n, d) in RATE_DEFS.items():
        out[m] = sums[n] / sums[d]
    out = out.reset_index()
    for m in RATE_DEFS:
        good_high = (m in OFFENSE_GOOD_HIGH) if side == "off" else (m not in OFFENSE_GOOD_HIGH)
        out[m + "_rk"] = out.groupby("season")[m].rank(ascending=not good_high, method="min").astype(int)
        out[m + "_lg"] = out.groupby("season")[m].transform("mean")
    return out
