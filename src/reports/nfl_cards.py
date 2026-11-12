"""NFL player cards: one card per player with offensive or defensive snaps this season. -> reports/cards/nfl_players.json

Sources (all regular season):
  raw_snap_counts  games, snaps and the player's position (Pro Football Reference ids)
  raw_player_week  box-score stats (gsis ids)
  raw_pfr_def      Pro Football Reference game charting: pressures, missed tackles, coverage (only fully charted weeks)
  raw_pbp          QB points added per dropback
  raw_players      links PFR ids to gsis ids; jersey numbers
Players are identified by gsis id. A PFR id is linked through raw_players only when that player is active in this era; otherwise
(e.g. a rookie who shares a retired player's PFR id) it is matched to the box-score player with the same team, name and weeks.
Stats are season totals across teams; the card sits with the team he played for most recently. Pinned to WEEK; --latest refreshes.
"""
import json
import re
import sys

import numpy as np
import pandas as pd

from src.db import ROOT, query

OUT = ROOT / "reports" / "cards"
SEASON = 2026
WEEK = 9              # cards pinned through this week; --latest uses the newest complete week
ROSTER_WEEK = 10      # rosters as of this week (each player's latest entry up to it); --latest uses the newest
ROSTERED = {"ACT": "Active roster", "INA": "Active roster (inactive for the latest game)", "RES": "Injured reserve or other reserve list",
            "DEV": "Practice squad"}
MIN_FGA, MIN_PUNTS = 10, 15
MIN_GP = 4            # games played, to be ranked
MIN_DB = 100          # QB dropbacks, to be ranked
EDGE_PRESS, EDGE_TACKLES = 1.0, 6.0   # per game: a linebacker who rushes the passer like an edge rusher
HIST_FROM = 2018

# PFR snap-count position -> card group
POS_GROUP = {"QB": "QB", "RB": "RB", "HB": "RB", "FB": "FB", "WR": "WR", "TE": "TE", "C": "OL", "G": "OL", "T": "OL", "OL": "OL",
             "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL", "LB": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB",
             "CB": "CB", "S": "S", "FS": "S", "SS": "S", "SAF": "S", "K": "K", "P": "P", "LS": "LS"}
ROSTER_GROUP = {"QB": "QB", "RB": "RB", "FB": "FB", "WR": "WR", "TE": "TE", "OL": "OL", "DL": "DL", "LB": "LB", "K": "K", "P": "P", "LS": "LS"}
GROUPS = ["QB", "RB", "FB", "WR", "TE", "OL", "DL", "LB", "CB", "S", "K", "P", "LS", "ST"]
POS_NAME = {"QB": "Quarterback", "RB": "Running back", "HB": "Running back", "FB": "Fullback", "WR": "Wide receiver",
            "TE": "Tight end", "C": "Center", "G": "Guard", "T": "Offensive tackle", "OT": "Offensive tackle", "OL": "Offensive lineman",
            "DE": "Defensive end", "DT": "Defensive tackle", "NT": "Nose tackle", "DL": "Defensive lineman", "LB": "Linebacker",
            "ILB": "Inside linebacker", "MLB": "Middle linebacker", "OLB": "Outside linebacker", "CB": "Cornerback", "S": "Safety",
            "FS": "Safety", "SS": "Safety", "SAF": "Safety", "DB": "Defensive back", "K": "Kicker", "P": "Punter", "LS": "Long snapper"}
# group -> (headline column, headline label); group -> (rank column, rank wording); FB and OL are not ranked
BIG = {"QB": ("pass_yds", "passing yards"), "RB": ("scrim", "yards from scrimmage"), "FB": ("scrim", "yards from scrimmage"),
       "WR": ("rec_yds", "receiving yards"), "TE": ("rec_yds", "receiving yards"), "OL": ("snaps", "snaps"),
       "DL": ("pressures", "pressures"), "LB": ("tackles", "tackles"), "CB": ("pd", "passes defended"), "S": ("tackles", "tackles"),
       "K": ("fg_made", "field goals"), "P": ("punts", "punts"), "LS": ("st_snaps", "special-teams snaps"),
       "ST": ("st_snaps", "special-teams snaps")}
RANK_ON = {"QB": ("epa_db", "points added per dropback"), "RB": ("scrim", "yards from scrimmage per game"),
           "WR": ("rec_yds", "receiving yards per game"), "TE": ("rec_yds", "receiving yards per game"),
           "DL": ("pressures", "pressures per game"), "LB": ("tackles", "tackles per game"),
           "CB": ("pd", "passes defended per game"), "S": ("tackles", "tackles per game"),
           "K": ("fg_pct", "field-goal percentage"), "P": ("net_avg", "net punting average")}
NOT_PER_GAME = {"QB", "K", "P"}   # ranked on a rate, not a per-game total


def norm(name):
    import unicodedata
    name = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()   # Estimé -> Estime
    name = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b\.?", "", str(name).lower())
    return re.sub(r"[^a-z]", "", name)


def latest_week(season=SEASON):
    """Newest week whose games are all final and whose player stats are loaded."""
    sch = query(f"SELECT week, SUM(home_score IS NULL) open FROM raw_schedules WHERE season={season} AND game_type='REG' GROUP BY week ORDER BY week")
    first_open = sch[sch.open > 0].week.min()
    done = (first_open - 1) if pd.notna(first_open) else sch.week.max()
    have = query(f"SELECT MAX(week) w FROM raw_player_week WHERE season={season} AND season_type='REG'").w.iloc[0]
    return int(min(done, have))


def tackles(df):
    # solo + the tackler credited on a shared tackle + assists: matches ESPN's and PFR's combined tackles
    return df.def_tackles_solo + df.def_tackles_with_assist + df.def_tackle_assists


def main(week=WEEK, roster_week=ROSTER_WEEK):
    week = week or latest_week()
    roster_week = roster_week or int(query(f"SELECT MAX(week) w FROM raw_rosters_weekly WHERE season={SEASON}").w.iloc[0])
    pl = query("SELECT gsis_id, pfr_id, display_name, position, jersey_number, rookie_season, last_season FROM raw_players ORDER BY gsis_id")
    pl = pl.drop_duplicates("gsis_id")
    info = pl.set_index("gsis_id")

    # ---- snaps: every game he played (special teams included); a card needs offensive or defensive snaps this season
    sn = query(f"""SELECT week, team, player, pfr_player_id, position, offense_snaps, offense_pct, defense_snaps, defense_pct, st_snaps
                   FROM raw_snap_counts WHERE season={SEASON} AND game_type='REG' AND week<={week} ORDER BY week, team, pfr_player_id""")
    for c in ("offense_snaps", "defense_snaps", "st_snaps"):
        sn[c] = sn[c].fillna(0)
    sn = sn[sn.offense_snaps + sn.defense_snaps + sn.st_snaps > 0].copy()
    sn["od"] = sn.offense_snaps + sn.defense_snaps

    # ---- link PFR id -> gsis id
    pw = query(f"SELECT * FROM raw_player_week WHERE season_type='REG' AND season BETWEEN {HIST_FROM} AND {SEASON} ORDER BY season, week, player_id")
    cur = pw[(pw.season == SEASON) & (pw.week <= week)]
    direct = pl.dropna(subset=["pfr_id"]).drop_duplicates("pfr_id", keep=False)
    direct = direct[direct.last_season.fillna(SEASON) >= SEASON - 1].set_index("pfr_id").gsis_id     # active in this era only
    link = {p: direct[p] for p in sn.pfr_player_id.unique() if p in direct.index}
    # fallback: same team, same normalized name, overlapping weeks in the box scores
    curn = cur.assign(n=cur.player_display_name.map(norm))[["player_id", "team", "week", "n"]]
    fallback = 0
    for pid, g in sn[~sn.pfr_player_id.isin(link)].groupby("pfr_player_id"):
        m = curn[(curn.n == norm(g.player.iloc[0])) & curn.team.isin(g.team) & curn.week.isin(g.week)].player_id.unique()
        if len(m) == 1 and m[0] not in link.values():
            link[pid] = m[0]
            fallback += 1
    unlinked = sorted(set(sn.pfr_player_id) - set(link))
    sn["gsis"] = sn.pfr_player_id.map(link)
    sn = sn.dropna(subset=["gsis"])
    inv = {}
    for p, g in link.items():
        inv.setdefault(g, []).append(p)
    assert all(len(v) == 1 for v in inv.values()), "two PFR ids linked to one player"

    # ---- per-player season basics
    sn["pct"] = np.where(sn.offense_snaps >= sn.defense_snaps, sn.offense_pct, sn.defense_pct)
    sn.loc[sn.od == 0, "pct"] = np.nan                     # special-teams-only games don't count toward snap share
    named = sn[sn.position.fillna("").str.strip() != ""]          # a few snap rows have a blank position
    pos = named[named.od > 0].groupby("gsis").position.agg(lambda x: x.mode().iloc[0])
    pos_any = named.groupby("gsis").position.agg(lambda x: x.mode().iloc[0])
    games = sn.groupby("gsis").agg(snaps=("od", "sum"), st_snaps=("st_snaps", "sum"), pct=("pct", "mean"))
    games["snap_data"] = True
    # players with a box-score line but no linkable snap row (e.g. an unlinked PFR id) still played: count them from their stat lines
    box_only = sorted(set(cur.player_id.dropna()) - set(games.index))
    games = pd.concat([games, pd.DataFrame(index=box_only, data=dict(snaps=0, st_snaps=0, pct=np.nan, snap_data=False))])
    played_rows = pd.concat([sn[["gsis", "week", "team"]], cur[["player_id", "week", "team"]].rename(columns={"player_id": "gsis"})])
    played_rows = played_rows[played_rows.gsis.isin(games.index)].drop_duplicates(["gsis", "week"])
    gweeks = played_rows.groupby("gsis").week.apply(sorted)        # a snap row or a stat line: the snap file misses some games
    games["gp"] = gweeks.reindex(games.index).map(len)
    last = played_rows.sort_values(["week", "team"]).groupby("gsis").tail(1).set_index("gsis")
    teams_played = played_rows.sort_values("week").groupby("gsis").team.agg(lambda x: list(dict.fromkeys(x)))
    tw = query(f"""SELECT home_team AS team, week FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week}
                   UNION SELECT away_team, week FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week}""")
    team_last = tw.groupby("team").week.max()
    week_date = query(f"SELECT MAX(gameday) d FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week={week}").d.iloc[0]

    # ---- rosters: each player's latest entry up to ROSTER_WEEK
    ro = query(f"""SELECT week, team, gsis_id, full_name, status, position, depth_chart_position, jersey_number FROM raw_rosters_weekly
                   WHERE season={SEASON} AND game_type='REG' AND week<={roster_week} AND gsis_id IS NOT NULL ORDER BY week, team, gsis_id""")
    team_ro_week = ro.groupby("team").week.max()                   # each team's newest roster (byes skip a week)
    ro = ro.sort_values(["week", "team"]).groupby("gsis_id").tail(1).set_index("gsis_id")
    # on a roster now = his latest entry is on his team's newest roster, with a rostered status; reserve players are listed every week
    current = (ro.week == ro.team.map(team_ro_week)) & ro.status.isin(ROSTERED)
    on_roster = ro[current]

    num = cur.select_dtypes("number").columns.drop(["season", "week"])
    tot = cur.groupby("player_id")[list(num)].sum()
    tot["fg_long"] = cur.groupby("player_id").fg_long.max()     # a long is a max, not a sum
    # blocked field goals count as attempts; put them in their distance range (fg_blocked_list holds the distances)
    blk = cur[cur.fg_blocked > 0][["player_id", "fg_blocked_list"]].copy()
    blk = blk.assign(d=blk.fg_blocked_list.astype(str).str.split(r"[;,]")).explode("d")
    blk["d"] = pd.to_numeric(blk.d.str.strip(), errors="coerce")
    assert blk.d.notna().all(), "unparsed blocked field goal distance"
    blk_rng = pd.crosstab(blk.player_id, pd.cut(blk.d, [0, 39, 49, 100], labels=["u40", "40", "50"]))
    assert int(blk_rng.values.sum()) == int(cur.fg_blocked.sum()), "blocked field goals don't add up"

    # ---- QB points added per dropback (scrambles credit the QB as rusher; no two-point tries)
    db = query(f"""SELECT COALESCE(passer_player_id, rusher_player_id) AS qb, week, epa FROM raw_pbp
                   WHERE season={SEASON} AND season_type='REG' AND week<={week} AND qb_dropback=1 AND epa IS NOT NULL
                   AND two_point_attempt=0 ORDER BY game_id, play_id""")
    qb = db.groupby("qb").agg(n_db=("epa", "size"), epa=("epa", "sum"))

    # ---- PFR charting, through the last week with every game charted (and no gaps before it)
    sch_n = query(f"SELECT week, COUNT(*) n FROM raw_schedules WHERE season={SEASON} AND game_type='REG' AND week<={week} GROUP BY week ORDER BY week")
    pf_n = query(f"SELECT week, COUNT(DISTINCT game_id) n FROM raw_pfr_def WHERE season={SEASON} AND game_type='REG' AND week<={week} GROUP BY week")
    full = sch_n.merge(pf_n, on="week", how="left", suffixes=("", "_pf")).fillna(0)
    gap = full[full.n_pf < full.n].week.min()
    pfr_week = int(gap - 1) if pd.notna(gap) else week
    games["gp_pfr"] = gweeks.map(lambda w: sum(x <= pfr_week for x in w))
    pf = query(f"""SELECT week, pfr_player_id, def_pressures, def_missed_tackles, def_targets, def_completions_allowed, def_yards_allowed
                   FROM raw_pfr_def WHERE season={SEASON} AND game_type='REG' AND week<={pfr_week} ORDER BY week, pfr_player_id""")
    pf["gsis"] = pf.pfr_player_id.map(link)
    pf = pf.dropna(subset=["gsis"])
    pft = pf.groupby("gsis")[["def_pressures", "def_missed_tackles", "def_targets", "def_completions_allowed", "def_yards_allowed"]].sum()

    rows, dropped = [], []
    roster_only = [g for g in on_roster.index if g not in games.index]
    for gid in list(games.index) + roster_only:
        played = gid in games.index
        g = games.loc[gid] if played else None
        if played:
            p = pos.get(gid, pos_any.get(gid))
            if p is None:                 # no snap position: use the roster's, then the players file
                p = ro.loc[gid, "position"] if gid in ro.index else (info.loc[gid, "position"] if gid in info.index else None)
            if p == "DB" and gid in info.index:
                p = "S" if info.loc[gid, "position"] in ("S", "FS", "SS", "SAF") else "CB"
            grp = POS_GROUP.get(p)
            if grp is not None and g.snap_data and g.snaps == 0 and grp not in ("K", "P", "LS"):
                grp = "ST"              # played only on special teams
        else:
            r0 = ro.loc[gid]
            p = r0.position
            if p == "DB":
                p = "S" if r0.depth_chart_position in ("S", "FS", "SS") else "CB"
            grp = ROSTER_GROUP.get(p, POS_GROUP.get(p))
        if grp is None:
            dropped.append((gid, "no position"))
            continue
        t = tot.loc[gid] if gid in tot.index else pd.Series(0, index=tot.columns)
        b = {k: int(blk_rng.loc[gid, k]) if gid in blk_rng.index and k in blk_rng.columns else 0 for k in ("u40", "40", "50")}
        f = pft.loc[gid] if gid in pft.index else pd.Series(0, index=pft.columns)
        q = qb.loc[gid] if gid in qb.index else None
        jn = ro.loc[gid, "jersey_number"] if gid in ro.index and ro.loc[gid, "jersey_number"] == ro.loc[gid, "jersey_number"] else (
            info.loc[gid, "jersey_number"] if gid in info.index else None)
        name = (info.loc[gid, "display_name"] if gid in info.index else ro.loc[gid, "full_name"] if gid in ro.index
                else last.loc[gid, "player"] if played else None)
        if not isinstance(name, str) or not name.strip():
            dropped.append((gid, "no name"))
            continue                    # never publish a card without a name
        played_team = last.loc[gid, "team"] if played else None
        last_wk = int(last.loc[gid, "week"]) if played else 0
        # current team: the roster's, when the roster entry is at least as new as his last game; else the team he last played for
        rteam = ro.loc[gid, "team"] if gid in on_roster.index and ro.loc[gid, "week"] >= last_wk else None
        team = rteam or played_team
        rows.append(dict(
            id=gid, name=name, team=team, last_week=last_wk, played_team=played_team,
            team_last_week=int(team_last.get(played_team, week)) if played else 0,
            status=ro.loc[gid, "status"] if gid in on_roster.index else None, grp=grp, pos=p,
            # for players who played but aren't on a roster now: his latest roster entry (released, cut, or simply gone)
            off_roster=(None if gid in on_roster.index or not played else
                        dict(team=ro.loc[gid, "team"], week=int(ro.loc[gid, "week"]), status=ro.loc[gid, "status"]) if gid in ro.index else {}),
            number=int(jn) if jn is not None and jn == jn else None,
            gp=int(g.gp) if played else 0, gp_pfr=int(g.gp_pfr) if played else 0, snaps=int(g.snaps) if played else 0,
            st_snaps=int(g.st_snaps) if played else 0,
            snap_data=bool(g.snap_data) if played else True,
            snap_pct=float(g.pct) if played and g.pct == g.pct else None,
            other_teams=[x for x in teams_played.loc[gid] if x != team] if played else [],
            cmp=int(t.completions), att=int(t.attempts), pass_yds=int(t.passing_yards), pass_td=int(t.passing_tds),
            ints=int(t.passing_interceptions), sacked=int(t.sacks_suffered),
            car=int(t.carries), rush_yds=int(t.rushing_yards), rush_td=int(t.rushing_tds),
            tgt=int(t.targets), rec=int(t.receptions), rec_yds=int(t.receiving_yards), rec_td=int(t.receiving_tds),
            fum_lost=int(t.rushing_fumbles_lost + t.receiving_fumbles_lost + t.sack_fumbles_lost),
            tackles=int(tackles(t)), tfl=int(t.def_tackles_for_loss), sacks=float(t.def_sacks),
            def_int=int(t.def_interceptions), pd=int(t.def_pass_defended), ff=int(t.def_fumbles_forced), def_td=int(t.def_tds),
            pressures=int(f.def_pressures), missed_tk=int(f.def_missed_tackles), cov_tgt=int(f.def_targets),
            cov_cmp=int(f.def_completions_allowed), cov_yds=int(f.def_yards_allowed), penalties=int(t.penalties),
            n_db=int(q.n_db) if q is not None else 0, epa_db=float(q.epa / q.n_db) if q is not None and q.n_db else None,
            fg_made=int(t.fg_made), fg_att=int(t.fg_att), fg_long=int(t.fg_long) if t.fg_long == t.fg_long else 0,
            fg_u40=[int(t.fg_made_0_19 + t.fg_made_20_29 + t.fg_made_30_39), int(t.fg_made_0_19 + t.fg_made_20_29 + t.fg_made_30_39
                     + t.fg_missed_0_19 + t.fg_missed_20_29 + t.fg_missed_30_39) + b["u40"]],
            fg_40=[int(t.fg_made_40_49), int(t.fg_made_40_49 + t.fg_missed_40_49) + b["40"]],
            fg_50=[int(t.fg_made_50_59 + t.fg_made_60_), int(t.fg_made_50_59 + t.fg_made_60_ + t.fg_missed_50_59 + t.fg_missed_60_) + b["50"]],
            pat_made=int(t.pat_made), pat_att=int(t.pat_att),
            punts=int(t.pt_att), punt_yds=int(t.pt_yards), punt_net=int(t.pt_net_yards), punt_i20=int(t.pt_inside_20), punt_tb=int(t.pt_touchback),
            pr=int(t.punt_returns), pr_yds=int(t.punt_return_yards), kr=int(t.kickoff_returns), kr_yds=int(t.kickoff_return_yards),
            st_td=int(t.special_teams_tds)))
    c = pd.DataFrame(rows)
    c["scrim"] = c.rush_yds + c.rec_yds
    c["fg_pct"] = (c.fg_made / c.fg_att).where(c.fg_att > 0)
    c["net_avg"] = (c.punt_net / c.punts).where(c.punts > 0)
    # edge rushers are listed as linebackers: card them with the pass rushers when they play like one
    per_press = c.pressures / c.gp_pfr.clip(lower=1)
    c["edge"] = (c.grp == "LB") & (per_press >= EDGE_PRESS) & (c.tackles / c.gp < EDGE_TACKLES)
    c.loc[c.edge, "grp"] = "DL"
    # a skill player with no carries or targets whose work is returning kicks gets the special-teams card
    c["ret_yds"] = c.kr_yds + c.pr_yds
    returner = c.grp.isin(["RB", "FB", "WR", "TE"]) & (c.car == 0) & (c.tgt == 0) & (c.kr + c.pr > 0)
    c.loc[returner, "grp"] = "ST"

    qualified = {"QB": lambda d: d.n_db >= MIN_DB, "K": lambda d: d.fg_att >= MIN_FGA, "P": lambda d: d.punts >= MIN_PUNTS}

    def per_game(df, col):
        return df[col] / (df.gp_pfr.clip(lower=1) if col == "pressures" else df.gp)

    c["rk"], c["of"] = None, None
    lg = {"QB_all": float(db.epa.sum() / len(db))}
    for grp, (col, _) in RANK_ON.items():
        m = (c.grp == grp) & (qualified[grp](c) if grp in qualified else (c.gp >= MIN_GP))
        if col == "pressures":
            m &= c.snap_data            # no charting data: not ranked on it
        val = c.loc[m, col] if grp in NOT_PER_GAME else per_game(c[m], col)
        c.loc[m, "rk"] = val.rank(ascending=False, method="min").astype(int)
        c.loc[m, "of"] = int(m.sum())
        lg[grp] = lg["QB_all"] if grp == "QB" else (
            float(c[c.grp == grp].fg_made.sum() / c[c.grp == grp].fg_att.sum()) if grp == "K" else
            float(c[c.grp == grp].punt_net.sum() / c[c.grp == grp].punts.sum()) if grp == "P" else float(val.mean()))

    # ---- week-by-week running totals for the sparkline
    wk = cur.assign(scrim=cur.rushing_yards + cur.receiving_yards, tackles=tackles(cur)).rename(
        columns={"passing_yards": "pass_yds", "receiving_yards": "rec_yds", "def_pass_defended": "pd"})
    wk = wk.rename(columns={"pt_att": "punts"})
    by_week = {col: wk.groupby(["player_id", "week"])[col].sum() for col in ("pass_yds", "scrim", "rec_yds", "tackles", "pd", "fg_made", "punts")}
    by_week["st_snaps"] = sn.groupby(["gsis", "week"]).st_snaps.sum()
    by_week["ret_yds"] = (wk.kickoff_return_yards + wk.punt_return_yards).groupby([wk.player_id, wk.week]).sum()
    by_week["pressures"] = pf.groupby(["gsis", "week"]).def_pressures.sum()
    by_week["snaps"] = sn.groupby(["gsis", "week"]).od.sum()

    # ---- history: every season (from 2018) with a snap or a stat line; this season included
    hs = query(f"""SELECT season, week, team, pfr_player_id FROM raw_snap_counts WHERE game_type='REG' AND season BETWEEN {HIST_FROM} AND {SEASON - 1}
                   AND COALESCE(offense_snaps, 0) + COALESCE(defense_snaps, 0) + COALESCE(st_snaps, 0) > 0""")
    hs["player_id"] = hs.pfr_player_id.map(lambda p: link.get(p, direct.get(p)))
    hw = pd.concat([hs.dropna(subset=["player_id"])[["player_id", "season", "week", "team"]],
                    pw[pw.season < SEASON][["player_id", "season", "week", "team"]],
                    cur[["player_id", "season", "week", "team"]],
                    sn[["gsis", "week", "team"]].rename(columns={"gsis": "player_id"}).assign(season=SEASON)])
    hw = hw[hw.player_id.isin(c.id)].drop_duplicates(["player_id", "season", "week"]).sort_values(["player_id", "season", "week"])
    hg = hw.groupby(["player_id", "season"]).agg(gp=("week", "nunique"), team=("team", lambda x: "/".join(dict.fromkeys(x))))
    hp = pd.concat([pw[pw.season < SEASON], cur])
    hp = hp[hp.player_id.isin(c.id)].assign(tk=tackles(hp[hp.player_id.isin(c.id)])).groupby(["player_id", "season"]).agg(
        pass_yds=("passing_yards", "sum"), pass_td=("passing_tds", "sum"), ints=("passing_interceptions", "sum"),
        rush_yds=("rushing_yards", "sum"), rush_td=("rushing_tds", "sum"), rec=("receptions", "sum"), rec_yds=("receiving_yards", "sum"),
        rec_td=("receiving_tds", "sum"), tackles=("tk", "sum"), sacks=("def_sacks", "sum"), def_int=("def_interceptions", "sum"),
        pd=("def_pass_defended", "sum"), fg_made=("fg_made", "sum"), fg_att=("fg_att", "sum"), punts=("pt_att", "sum"),
        punt_yds=("pt_yards", "sum"))
    hist = hg.join(hp).fillna(0).reset_index()
    hist_by = {pid: g for pid, g in hist.groupby("player_id")}

    cards = []
    for r in c.to_dict("records"):
        col, label = BIG[r["grp"]]
        if r["grp"] == "ST" and r["kr"] + r["pr"] > 0:
            col, label = "ret_yds", "return yards"
        if not r["snap_data"] and col in ("pressures", "snaps", "st_snaps"):     # never show a number we couldn't compute
            col, label = ("tackles", "tackles") if r["grp"] in ("DL", "LB", "CB", "S", "LS", "ST") else ("gp", "games")
        weeks = gweeks.loc[r["id"]] if r["gp"] else []
        s = by_week[col]
        r["spark"] = np.cumsum([int(s.get((r["id"], w), 0)) for w in weeks]).tolist()
        r["big"], r["big_label"] = r[col], label
        r["rank_what"] = RANK_ON[r["grp"]][1] if r["grp"] in RANK_ON else None
        h = hist_by.get(r["id"], pd.DataFrame())
        r["seasons"] = [dict(season=int(x.season), team=x.team, gp=int(x.gp), pass_yds=int(x.pass_yds), pass_td=int(x.pass_td),
                             ints=int(x.ints), rush_yds=int(x.rush_yds), rush_td=int(x.rush_td), rec=int(x.rec),
                             rec_yds=int(x.rec_yds), rec_td=int(x.rec_td), tackles=int(x.tackles), sacks=float(x.sacks),
                             def_int=int(x.def_int), pd=int(x.pd), fg_made=int(x.fg_made), fg_att=int(x.fg_att), punts=int(x.punts),
                             punt_yds=int(x.punt_yds)) for x in h.itertuples()]
        if not r["gp"]:              # on a roster, hasn't played this season: headline is his NFL games since 2018
            r["big"], r["big_label"] = sum(s["gp"] for s in r["seasons"]), "NFL games since 2018"
        r["small"] = bool(r["gp"] > 0 and (r["n_db"] < MIN_DB if r["grp"] == "QB" else r["gp"] < MIN_GP))
        r["number"] = None if r["number"] is None or r["number"] != r["number"] else int(r["number"])
        for k, v in list(r.items()):
            if isinstance(v, (bool, np.bool_)):
                r[k] = bool(v)
            elif isinstance(v, (int, np.integer)):
                r[k] = int(v)
            elif isinstance(v, (float, np.floating)):
                r[k] = None if np.isnan(v) else float(v)
        cards.append(r)

    meta = dict(season=SEASON, week=week, roster_week=roster_week, rostered=ROSTERED, min_fga=MIN_FGA, min_punts=MIN_PUNTS, week_date=str(week_date), pfr_week=pfr_week, min_gp=MIN_GP, min_db=MIN_DB,
                edge_press=EDGE_PRESS, edge_tackles=EDGE_TACKLES, hist_from=HIST_FROM, lg=lg, n=len(cards),
                linked_by_name=fallback, unlinked=unlinked, dropped=dropped)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "nfl_players.json").write_text(json.dumps(dict(meta=meta, cards=cards), indent=1, allow_nan=False))
    print(f"NFL cards through week {week} (charting through {pfr_week}): {len(cards)} players; "
          f"{fallback} linked by team/name/weeks; unlinked {unlinked}")
    print(c.groupby("grp").size().to_dict())
    return meta, cards


if __name__ == "__main__":
    main(*((None, None) if "--latest" in sys.argv else (WEEK, ROSTER_WEEK)))
