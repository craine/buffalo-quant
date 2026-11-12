"""NFL player cards: one card per player with offensive or defensive snaps this season. -> reports/cards/nfl_players.json

Sources: raw_player_week (box-score stats, gsis id), raw_snap_counts (games and snaps, pfr id), raw_pfr_def (pressures, PFR
charting), raw_pbp (points added per dropback for QBs), raw_players (links gsis_id <-> pfr_id; names, positions, jerseys).
Players are identified by gsis id, never by name. Regular season only. Stats are season totals across teams; the card sits with
the team he played for most recently.
"""
import json
import sys

import numpy as np
import pandas as pd

from src.db import ROOT, query

OUT = ROOT / "reports" / "cards"
SEASON = 2026
WEEK = 9              # cards pinned through this week; the refresh passes --latest
MIN_GP = 4            # games with snaps, to be ranked
MIN_DB = 100          # QB dropbacks, to be ranked
EDGE_PRESS, EDGE_TACKLES = 1.0, 6.0   # per game: a "linebacker" who rushes the passer like an edge rusher
GROUPS = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB"]
POS_NAME = {"QB": "Quarterback", "RB": "Running back", "FB": "Fullback", "WR": "Wide receiver", "TE": "Tight end",
            "C": "Center", "G": "Guard", "OT": "Tackle", "T": "Tackle", "OL": "Offensive line", "DE": "Defensive end",
            "DT": "Defensive tackle", "NT": "Nose tackle", "DL": "Defensive line", "LB": "Linebacker", "ILB": "Inside linebacker",
            "MLB": "Middle linebacker", "OLB": "Outside linebacker", "CB": "Cornerback", "S": "Safety", "FS": "Free safety",
            "SS": "Strong safety", "SAF": "Safety", "DB": "Defensive back"}


def latest_week(season=SEASON):
    """Last week whose games are all final in the schedule and whose player stats are loaded."""
    sch = query(f"SELECT week, SUM(home_score IS NULL) open FROM raw_schedules WHERE season={season} AND game_type='REG' GROUP BY week")
    done = sch[sch.open == 0].week.max()
    have = query(f"SELECT MAX(week) w FROM raw_player_week WHERE season={season} AND season_type='REG'").w.iloc[0]
    return int(min(done, have))


def main(week=None):
    week = week or latest_week()
    pl = query("SELECT gsis_id, pfr_id, display_name, position, position_group, jersey_number FROM raw_players")
    link = pl.dropna(subset=["pfr_id"]).set_index("pfr_id").gsis_id

    # games and snaps, by week (offense or defense snaps > 0)
    # a game counts if he played any snaps (special teams included), since box-score stats include special-teams plays;
    # a player gets a card if he has offensive or defensive snaps this season
    sn = query(f"""SELECT week, team, pfr_player_id, position, offense_snaps, offense_pct, defense_snaps, defense_pct, st_snaps
                   FROM raw_snap_counts WHERE season={SEASON} AND game_type='REG' AND week<={week}""")
    sn = sn[(sn.offense_snaps.fillna(0) + sn.defense_snaps.fillna(0) + sn.st_snaps.fillna(0)) > 0].copy()
    od = sn.groupby("pfr_player_id").apply(lambda x: (x.offense_snaps.fillna(0) + x.defense_snaps.fillna(0)).sum(), include_groups=False)
    sn = sn[sn.pfr_player_id.isin(od[od > 0].index)]
    sn["gsis"] = sn.pfr_player_id.map(link)
    unlinked = sn[sn.gsis.isna()].pfr_player_id.nunique()
    sn = sn.dropna(subset=["gsis"])
    sn["snaps"] = sn.offense_snaps.fillna(0) + sn.defense_snaps.fillna(0)
    sn["pct"] = np.where(sn.offense_snaps.fillna(0) >= sn.defense_snaps.fillna(0), sn.offense_pct, sn.defense_pct)
    sn.loc[sn.snaps == 0, "pct"] = np.nan        # special-teams-only games don't count toward snap share
    games = sn.groupby("gsis").agg(snaps=("snaps", "sum"), pct=("pct", "mean"),
                                   off=("offense_snaps", "sum"), dfn=("defense_snaps", "sum"))
    pw_cur = query(f"SELECT player_id, week FROM raw_player_week WHERE season={SEASON} AND season_type='REG' AND week<={week}")
    gweeks = (pd.concat([sn[["gsis", "week"]], pw_cur.rename(columns={"player_id": "gsis"})])
              .drop_duplicates().groupby("gsis").week.apply(lambda w: sorted(w)))    # a snap row or a stat line: the snap file misses some games
    games["gp"] = gweeks.reindex(games.index).map(len)
    last = sn.sort_values("week").groupby("gsis").tail(1).set_index("gsis")
    teams_played = sn.groupby("gsis").team.unique()

    # box-score stats
    pw = query(f"SELECT * FROM raw_player_week WHERE season_type='REG' AND season BETWEEN 2018 AND {SEASON}")
    cur = pw[(pw.season == SEASON) & (pw.week <= week)]
    num = cur.select_dtypes("number").columns.drop(["season", "week"])
    tot = cur.groupby("player_id")[list(num)].sum()

    # QB points added per dropback (scrambles credit the QB as rusher)
    db = query(f"""SELECT COALESCE(passer_player_id, rusher_player_id) AS qb, week, epa FROM raw_pbp
                   WHERE season={SEASON} AND season_type='REG' AND week<={week} AND qb_dropback=1 AND epa IS NOT NULL
                   AND two_point_attempt=0""")
    qb = db.groupby("qb").agg(n_db=("epa", "size"), epa=("epa", "sum"))

    # PFR charting: pressures, missed tackles, coverage. Use only weeks where every game is charted.
    sch_n = query(f"SELECT week, COUNT(*) n FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week} GROUP BY week")
    pf_n = query(f"SELECT week, COUNT(DISTINCT game_id) n FROM raw_pfr_def WHERE season={SEASON} AND game_type='REG' AND week<={week} GROUP BY week")
    full = sch_n.merge(pf_n, on="week", how="left", suffixes=("", "_pf")).fillna(0)
    full_weeks = full[full.n_pf >= full.n].week
    pfr_week = int(full_weeks.max()) if len(full_weeks) else 0
    assert list(full_weeks) == list(range(1, pfr_week + 1)), f"PFR charting has gaps: {full.to_dict('records')}"
    games["gp_pfr"] = gweeks.reindex(games.index).map(lambda w: sum(x <= pfr_week for x in w))
    pf = query(f"""SELECT week, pfr_player_id, def_pressures, def_missed_tackles, def_targets, def_completions_allowed, def_yards_allowed
                   FROM raw_pfr_def WHERE season={SEASON} AND game_type='REG' AND week<={pfr_week}""")
    pf["gsis"] = pf.pfr_player_id.map(link)
    pft = pf.dropna(subset=["gsis"]).groupby("gsis")[["def_pressures", "def_missed_tackles", "def_targets",
                                                      "def_completions_allowed", "def_yards_allowed"]].sum()

    info = pl.set_index("gsis_id")
    rows = []
    for gid, g in games.iterrows():
        p = info.loc[gid] if gid in info.index else None
        grp = p.position_group if p is not None and p.position_group in GROUPS else None
        if grp is None:
            continue          # specialists and unknown positions: not in the first cut
        t = tot.loc[gid] if gid in tot.index else pd.Series(0, index=tot.columns)
        f = pft.loc[gid] if gid in pft.index else pd.Series(0, index=pft.columns)
        q = qb.loc[gid] if gid in qb.index else None
        tackles = int(t.def_tackles_solo + t.def_tackle_assists)
        r = dict(id=gid, name=p.display_name, team=last.loc[gid, "team"], grp=grp, pos=p.position,
                 number=int(p.jersey_number) if pd.notna(p.jersey_number) else None,
                 gp=int(g.gp), gp_pfr=int(g.gp_pfr), snaps=int(g.snaps), snap_pct=round(float(g.pct), 3),
                 other_teams=[x for x in teams_played.loc[gid] if x != last.loc[gid, "team"]],
                 cmp=int(t.completions), att=int(t.attempts), pass_yds=int(t.passing_yards), pass_td=int(t.passing_tds),
                 ints=int(t.passing_interceptions), sacked=int(t.sacks_suffered),
                 car=int(t.carries), rush_yds=int(t.rushing_yards), rush_td=int(t.rushing_tds),
                 tgt=int(t.targets), rec=int(t.receptions), rec_yds=int(t.receiving_yards), rec_td=int(t.receiving_tds),
                 fum_lost=int(t.rushing_fumbles_lost + t.receiving_fumbles_lost + t.sack_fumbles_lost),
                 tackles=tackles, tfl=int(t.def_tackles_for_loss), sacks=float(t.def_sacks), qb_hits=int(t.def_qb_hits),
                 def_int=int(t.def_interceptions), pd=int(t.def_pass_defended), ff=int(t.def_fumbles_forced),
                 pressures=int(f.def_pressures), missed_tk=int(f.def_missed_tackles), cov_tgt=int(f.def_targets),
                 cov_cmp=int(f.def_completions_allowed), cov_yds=int(f.def_yards_allowed), penalties=int(t.penalties),
                 n_db=int(q.n_db) if q is not None else 0, epa_db=float(q.epa / q.n_db) if q is not None and q.n_db else None)
        rows.append(r)
    c = pd.DataFrame(rows)
    # Edge rushers are listed as linebackers in every source. Card them with the pass rushers when they play like one:
    # at least 1 pressure and fewer than 5 tackles a game.
    edge = (c.grp == "LB") & (c.pressures / c.gp_pfr.clip(lower=1) >= EDGE_PRESS) & (c.tackles / c.gp < EDGE_TACKLES)
    c.loc[edge, "grp"] = "DL"
    c["edge"] = edge

    # headline number and the per-game measure each group is ranked on
    c["scrim"] = c.rush_yds + c.rec_yds
    big = {"QB": ("pass_yds", "passing yards"), "RB": ("scrim", "yards from scrimmage"), "WR": ("rec_yds", "receiving yards"),
           "TE": ("rec_yds", "receiving yards"), "OL": ("snaps", "snaps"), "DL": ("pressures", "pressures"),
           "LB": ("tackles", "tackles"), "DB": ("pd", "passes defended")}
    rank_on = {"QB": ("epa_db", "points added per dropback"), "RB": ("scrim", "yards from scrimmage per game"),
               "WR": ("rec_yds", "receiving yards per game"), "TE": ("rec_yds", "receiving yards per game"),
               "DL": ("pressures", "pressures per game"), "LB": ("tackles", "tackles per game"),
               "DB": ("pd", "passes defended per game")}
    c["rk"], c["of"] = None, None
    for grp, (col, _) in rank_on.items():
        m = (c.grp == grp) & ((c.n_db >= MIN_DB) if grp == "QB" else (c.gp >= MIN_GP))
        den = c.loc[m, "gp_pfr"].clip(lower=1) if col == "pressures" else c.loc[m, "gp"]
        val = c.loc[m, col] if grp == "QB" else c.loc[m, col] / den
        c.loc[m, "rk"] = val.rank(ascending=False, method="min").astype(int)
        c.loc[m, "of"] = int(m.sum())

    # week-by-week running total of the headline number (sparkline)
    wk = cur.copy()
    wk["scrim"] = wk.rushing_yards + wk.receiving_yards
    wk["tackles"] = wk.def_tackles_solo + wk.def_tackle_assists
    wk = wk.rename(columns={"passing_yards": "pass_yds", "receiving_yards": "rec_yds", "def_pass_defended": "pd"})
    pfw = pf.dropna(subset=["gsis"]).rename(columns={"def_pressures": "pressures"})
    snw = sn.groupby(["gsis", "week"]).snaps.sum()

    # history (2018 on), box-score seasons
    hs = query(f"""SELECT season, week, team, pfr_player_id FROM raw_snap_counts WHERE game_type='REG' AND season<{SEASON}
                   AND COALESCE(offense_snaps, 0) + COALESCE(defense_snaps, 0) + COALESCE(st_snaps, 0) > 0""")
    hs["player_id"] = hs.pfr_player_id.map(link)
    hw = pd.concat([hs.dropna(subset=["player_id"])[["player_id", "season", "week", "team"]],
                    pw[pw.season < SEASON][["player_id", "season", "week", "team"]]]).drop_duplicates(["player_id", "season", "week"])
    hgp = hw.groupby(["player_id", "season"]).week.nunique().rename("gp_all")
    hteam = hw.sort_values("week").groupby(["player_id", "season"]).team.agg(lambda x: "/".join(dict.fromkeys(x))).rename("teams")
    hist = pw[pw.season < SEASON].groupby(["player_id", "season"]).agg(
        team=("team", "last"), gp=("week", "nunique"), pass_yds=("passing_yards", "sum"),
        pass_td=("passing_tds", "sum"), ints=("passing_interceptions", "sum"), rush_yds=("rushing_yards", "sum"),
        rush_td=("rushing_tds", "sum"), rec=("receptions", "sum"), rec_yds=("receiving_yards", "sum"), rec_td=("receiving_tds", "sum"),
        tk_s=("def_tackles_solo", "sum"), tk_a=("def_tackle_assists", "sum"), sacks=("def_sacks", "sum"), def_int=("def_interceptions", "sum"),
        pd=("def_pass_defended", "sum")).reset_index()
    hist = hist.join(hgp, on=["player_id", "season"]).join(hteam, on=["player_id", "season"])
    hist["gp"], hist["team"] = hist.gp_all.fillna(hist.gp).astype(int), hist.teams.fillna(hist.team)

    cards = []
    for r in c.to_dict("records"):
        col, label = big[r["grp"]]
        weeks = gweeks.loc[r["id"]]
        if col == "pressures":
            per = pfw[pfw.gsis == r["id"]].groupby("week").pressures.sum()
        elif col == "snaps":
            per = snw.loc[r["id"]] if r["id"] in snw.index.get_level_values(0) else pd.Series(dtype=float)
        else:
            per = wk[wk.player_id == r["id"]].groupby("week")[col].sum()
        r["spark"] = np.cumsum([int(per.get(w, 0)) for w in weeks]).tolist()
        r["big"], r["big_label"] = r[col], label
        r["rank_what"] = rank_on.get(r["grp"], (None, None))[1]
        h = hist[hist.player_id == r["id"]].sort_values("season")
        r["seasons"] = [dict(season=int(x.season), team=x.team, gp=int(x.gp), pass_yds=int(x.pass_yds), pass_td=int(x.pass_td),
                             ints=int(x.ints), rush_yds=int(x.rush_yds), rush_td=int(x.rush_td), rec=int(x.rec),
                             rec_yds=int(x.rec_yds), rec_td=int(x.rec_td), tackles=int(x.tk_s + x.tk_a), sacks=float(x.sacks),
                             def_int=int(x.def_int), pd=int(x.pd)) for x in h.itertuples()]
        r["small"] = bool(r["gp"] < MIN_GP if r["grp"] != "QB" else r["n_db"] < MIN_DB)
        r["number"] = None if r["number"] is None or r["number"] != r["number"] else int(r["number"])
        for k, v in list(r.items()):
            if isinstance(v, (bool, np.bool_)):
                r[k] = bool(v)
            elif isinstance(v, (int, np.integer)):
                r[k] = int(v)
            elif isinstance(v, (float, np.floating)):
                r[k] = None if np.isnan(v) else float(v)
        cards.append(r)

    # league averages per game for context
    lg = {"QB_all": float(db.epa.sum() / len(db))}
    for grp, (col, label) in rank_on.items():
        m = (c.grp == grp) & ((c.n_db >= MIN_DB) if grp == "QB" else (c.gp >= MIN_GP))
        lg[grp] = round(float(c.loc[m, col].mean() if grp == "QB" else (c.loc[m, col] / c.loc[m, "gp"]).mean()), 3)
    meta = dict(season=SEASON, week=week, pfr_week=pfr_week, min_gp=MIN_GP, min_db=MIN_DB, lg=lg, n=len(cards), unlinked_snap_players=int(unlinked))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "nfl_players.json").write_text(json.dumps(dict(meta=meta, cards=cards), indent=1, allow_nan=False))
    print(f"NFL cards through week {week}: {len(cards)} players; {unlinked} snap-count players without a gsis link")
    print(c.groupby("grp").size().to_dict())
    return meta, cards


if __name__ == "__main__":
    main(None if "--latest" in sys.argv else WEEK)
