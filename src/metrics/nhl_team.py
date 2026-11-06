"""Team-season and goalie-season metrics from clean_nhl_shots_xg. Regular season, shootouts excluded.

CF = all shot attempts, FF = unblocked attempts, SF = shots on goal. xG on unblocked non-empty-net shots.
Shooting% / save% exclude empty-net goals and shots. PDO = 5v5 sh% + 5v5 sv%.
"""
import numpy as np
import pandas as pd

from src.db import query


def shots():
    return query("SELECT * FROM clean_nhl_shots_xg")


def records():
    g = query("SELECT * FROM raw_nhl_games")
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        x = g.rename(columns={f"{side}": "team", f"{side}_score": "gf", f"{opp}_score": "ga"})[["season", "game_id", "game_date", "team", "gf", "ga", "last_period_type"]]
        rows.append(x)
    r = pd.concat(rows)
    r["w"] = (r.gf > r.ga).astype(int)
    r["otl"] = ((r.gf < r.ga) & r.last_period_type.isin(["OT", "SO"])).astype(int)
    r["l"] = ((r.gf < r.ga) & ~r.last_period_type.isin(["OT", "SO"])).astype(int)
    r["one_goal"] = ((r.gf - r.ga).abs() == 1) | r.last_period_type.isin(["OT", "SO"])
    return r


def team_season(s, strength=None):
    x = s if strength is None else s[s.strength == strength]
    ne = x[x.empty_net_against == 0]
    f = x.groupby(["season", "team"]).agg(CF=("ev", "size"), FF=("unblocked", "sum"), SF=("on_goal", "sum"))
    f = f.join(ne.groupby(["season", "team"]).agg(GF=("goal", "sum"), SFne=("on_goal", "sum"), xGF=("xg", "sum")))
    a = x.groupby(["season", "opp"]).agg(CA=("ev", "size"), FA=("unblocked", "sum"), SA=("on_goal", "sum"))
    a = a.join(ne.groupby(["season", "opp"]).agg(GA=("goal", "sum"), SAne=("on_goal", "sum"), xGA=("xg", "sum")))
    a.index.names = ["season", "team"]
    t = f.join(a)
    t["CF%"] = t.CF / (t.CF + t.CA); t["xGF%"] = t.xGF / (t.xGF + t.xGA); t["GF%"] = t.GF / (t.GF + t.GA)
    t["sh%"] = t.GF / t.SFne; t["sv%"] = 1 - t.GA / t.SAne; t["PDO"] = t["sh%"] + t["sv%"]
    t["G-xG"] = t.GF - t.xGF; t["xGA-GA"] = t.xGA - t.GA
    return t.reset_index()


def goalie_season(s):
    x = s[(s.unblocked == 1) & (s.empty_net_against == 0) & s.goalie_id.notna()]
    g = x.groupby(["season", "goalie_id", "opp"]).agg(shots_faced=("on_goal", "sum"), unblocked=("unblocked", "size"),
                                                        GA=("goal", "sum"), xGA=("xg", "sum")).reset_index()
    g = g.rename(columns={"opp": "team"})
    g["GSAx"] = g.xGA - g.GA
    g["sv%"] = 1 - g.GA / g.shots_faced
    g["xsv%"] = 1 - g.xGA / g.shots_faced
    g["GSAx_per100"] = 100 * g.GSAx / g.shots_faced
    names = query("SELECT player_id, MAX(first) first, MAX(last) last FROM raw_nhl_rosters GROUP BY player_id")
    names["name"] = names["first"] + " " + names["last"]
    return g.merge(names[["player_id", "name"]], left_on="goalie_id", right_on="player_id", how="left")


def ranks(t, cols, higher_better=True):
    out = t.copy()
    for c in cols:
        out[c + "_rk"] = out.groupby("season")[c].rank(ascending=not higher_better, method="min").astype(int)
    return out
