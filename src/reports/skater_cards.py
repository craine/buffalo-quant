"""Skater cards: one baseball-card-style record per Sabres skater, pinned to AS_OF. Every number computed here.

Writes reports/cards/skaters.json, which src/site/build.py renders on /cards/ beside the goalie cards.

What a card shows (all from the NHL play-by-play feed; regular season):
- Games: games the player dressed for (game rosters).
- Goals and assists: goal events (shootouts excluded). Cross-checked against the feed's own running season goal total.
- Chances created: the goals his own unblocked shots were worth (our xG model, empty net excluded, rescaled per season so
  league xG = league goals). Finishing = goals on those shots minus chances.
- Power-play goals: the other side short-handed by a penalty (skaters compared without an extra attacker); penalty shots excluded.
- Faceoffs, hits, blocked shots, takeaways, giveaways: event counts (recorded by the league's scorers, which vary by rink).
- Ranks: among all NHL forwards or defensemen with MIN_GP+ games this season, per game.
No ice time: our feed has no shift data yet, so nothing here is per minute or "on the ice".
"""
import json

import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots

AS_OF = "2026-11-10"
SEASON = 20262027
TEAM = "BUF"
MIN_GP = 8
OUT = ROOT / "reports" / "cards"
SEASON_LABEL = lambda s: f"{str(s)[:4]}-{str(s)[6:]}"
FWD = {"C", "L", "R"}


def team_map():
    g = query("SELECT home_id AS id, home AS ab FROM raw_nhl_games UNION SELECT away_id, away FROM raw_nhl_games")
    return dict(zip(g.id, g.ab))


def main(as_of=AS_OF, league=False):
    gm = query(f"SELECT game_id, game_date, season FROM raw_nhl_games WHERE game_date <= '{as_of}'")
    ids = set(gm.game_id)
    tm = team_map()
    ros = query("SELECT game_id, season, team_id, player_id, first, last, pos, number FROM raw_nhl_rosters")
    ros = ros[ros.game_id.isin(ids) & (ros.pos != "G")].copy()
    ros["team"] = ros.team_id.map(tm)
    name = ros.groupby("player_id").apply(lambda x: f"{x['first'].iloc[-1]} {x['last'].iloc[-1]}")
    pos_of = ros[ros.season == SEASON].groupby("player_id").pos.agg(lambda p: p.mode().iloc[0])
    gp = ros.groupby(["season", "player_id", "team"]).game_id.nunique().rename("gp")

    pl = query("""SELECT game_id, season, typeDescKey AS ev, periodDescriptor_periodType AS ptype, details_eventOwnerTeamId AS owner,
                  details_scoringPlayerId AS scorer, details_scoringPlayerTotal AS scorer_total, details_assist1PlayerId AS a1,
                  details_assist2PlayerId AS a2, details_hittingPlayerId AS hitter, details_blockingPlayerId AS blocker,
                  details_playerId AS pid, details_winningPlayerId AS fo_w, details_losingPlayerId AS fo_l FROM raw_nhl_plays""")
    pl = pl[pl.game_id.isin(ids)]
    goals = pl[(pl.ev == "goal") & (pl.ptype != "SO")]

    # each player's team in each game, so season-team splits are right for traded players
    pt = ros[["game_id", "player_id", "team"]].drop_duplicates()

    def count(df, col, label):
        x = df[df[col].notna()][["game_id", "season", col]].rename(columns={col: "player_id"})
        x["player_id"] = x.player_id.astype(int)
        x = x.merge(pt, on=["game_id", "player_id"], how="left")
        return x.groupby(["season", "player_id", "team"]).size().rename(label)

    parts = [gp, count(goals, "scorer", "g"), count(goals, "a1", "a1"), count(goals, "a2", "a2"),
             count(pl[pl.ev == "hit"], "hitter", "hits"), count(pl[pl.ev == "blocked-shot"], "blocker", "blocks"),
             count(pl[pl.ev == "takeaway"], "pid", "take"), count(pl[pl.ev == "giveaway"], "pid", "give"),
             count(pl[pl.ev == "faceoff"], "fo_w", "fow"), count(pl[pl.ev == "faceoff"], "fo_l", "fol")]

    s = shots()
    s = s[s.game_id.isin(ids) & s.shooter_id.notna()].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    s["player_id"] = s.shooter_id.astype(int)
    s = s.merge(pt, on=["game_id", "player_id"], how="left", suffixes=("_shot", ""))
    s["team"] = s["team"].fillna(s["team_shot"])
    u = s[unb.reindex(s.index, fill_value=False) if False else ((s.unblocked == 1) & (s.empty_net_against == 0))]
    sc = query("SELECT game_id, eventId, situationCode FROM raw_nhl_plays WHERE typeDescKey='goal'")
    gl = s[s.goal == 1].merge(sc, on=["game_id", "eventId"], how="left")
    code = gl.situationCode.astype(str).str.zfill(4)
    ag, ask, hsk, hg = (code.str[i].astype(int) for i in range(4))   # [away goalie][away skaters][home skaters][home goalie]
    own_g, own_sk = np.where(gl.is_home == 1, hg, ag), np.where(gl.is_home == 1, hsk, ask)
    opp_g, opp_sk = np.where(gl.is_home == 1, ag, hg), np.where(gl.is_home == 1, ask, hsk)
    # skaters not counting an extra attacker (a pulled goalie); a power play = the other side short-handed by a penalty
    pp = gl[((own_sk - (own_g == 0)) > (opp_sk - (opp_g == 0))) & (opp_sk >= 3)]
    en_goals = s[(s.goal == 1) & (s.empty_net_against == 1)]
    parts += [u.groupby(["season", "player_id", "team"]).xg.sum().rename("ixg"),
              u.groupby(["season", "player_id", "team"]).goal.sum().rename("ig_unb"),
              s.groupby(["season", "player_id", "team"]).on_goal.sum().rename("sog"),
              u[u.dist < 20].groupby(["season", "player_id", "team"]).size().rename("close"),
              u[u.rebound == 1].groupby(["season", "player_id", "team"]).size().rename("reb"),
              pp.groupby(["season", "player_id", "team"]).size().rename("ppg"),
              en_goals.groupby(["season", "player_id", "team"]).size().rename("en_g")]
    t = pd.concat(parts, axis=1).fillna(0).reset_index()
    first = pt.merge(gm[["game_id", "game_date"]], on="game_id").merge(ros[["game_id", "player_id", "season"]].drop_duplicates(), on=["game_id", "player_id"])
    first = first.groupby(["season", "player_id", "team"]).game_date.min().rename("first_game").reset_index()
    t = t.merge(first, on=["season", "player_id", "team"], how="left")
    t = t[t.gp > 0]
    t["a"] = t.a1 + t.a2
    t["p"] = t.g + t.a

    # ---- cross-check: our goal counts vs. the feed's own running season total (max seen per scorer this season)
    fe = goals[goals.season == SEASON].dropna(subset=["scorer", "scorer_total"])
    feed_total = fe.groupby(fe.scorer.astype(int)).scorer_total.max()
    ours = t[t.season == SEASON].groupby("player_id").g.sum()
    chk = pd.concat([ours.rename("ours"), feed_total.rename("feed")], axis=1).dropna()
    mism = chk[chk.ours != chk.feed]

    # ---- league ranks this season, per game, by position group (players' whole season, all teams)
    cur = t[t.season == SEASON].groupby("player_id")[["gp", "g", "a", "p", "ixg", "ig_unb", "sog", "ppg"]].sum()
    cur["grp"] = cur.index.map(lambda i: "F" if pos_of.get(i) in FWD else "D")
    elig = cur[cur.gp >= MIN_GP].copy()
    for c in ["p", "g", "ixg"]:
        elig[c + "_pg"] = elig[c] / elig.gp
        elig[c + "_rk"] = elig.groupby("grp")[c + "_pg"].rank(ascending=False, method="min")
    n_grp = elig.grp.value_counts().to_dict()
    lg = elig.groupby("grp")[["p", "ixg", "gp"]].sum()
    lg_rates = {k: dict(p_pg=round(float(lg.loc[k, "p"] / lg.loc[k, "gp"]), 2), ixg_pg=round(float(lg.loc[k, "ixg"] / lg.loc[k, "gp"]), 2)) for k in lg.index}

    # ---- how well chances and finishing carry over from one season to the next (complete seasons, 40+ games in both)
    tot = t[t.season < SEASON].groupby(["season", "player_id"])[["gp", "ixg", "ig_unb"]].sum().reset_index()
    tot = tot[tot.gp >= 40]
    tot["c_pg"], tot["f_pg"] = tot.ixg / tot.gp, (tot.ig_unb - tot.ixg) / tot.gp
    nxt = tot.assign(season=tot.season + 10001)
    pair = tot.merge(nxt, on=["season", "player_id"], suffixes=("", "_prev"))
    pos_all = ros.groupby("player_id").pos.agg(lambda p: p.mode().iloc[0])
    pair = pair[pair.player_id.map(pos_all).isin(FWD)]        # forwards only, so position differences don't inflate it
    carry = dict(chances=round(float(pair.c_pg.corr(pair.c_pg_prev)), 2), finishing=round(float(pair.f_pg.corr(pair.f_pg_prev)), 2), pairs=int(len(pair)))

    # ---- cards. Sabres mode: every skater who has dressed for the Sabres this season (skaters.json, pinned for stories).
    # League mode: every skater in the league, on the team he played for most recently (skaters_league.json).
    dates = dict(zip(gm.game_id, gm.game_date))
    cur_games = set(gm[gm.season == SEASON].game_id)
    gpt = pd.concat([goals[["game_id", c]].rename(columns={c: "player_id"}) for c in ("scorer", "a1", "a2")]).dropna()
    gpt = gpt.assign(player_id=gpt.player_id.astype(int)).groupby(["game_id", "player_id"]).size()
    tcur = t[t.season == SEASON]
    if league:
        last = pt[pt.game_id.isin(cur_games)].assign(d=lambda x: x.game_id.map(dates)).sort_values(["d", "game_id"])
        now = last.groupby("player_id").team.last()
        rows = tcur[tcur.team == tcur.player_id.map(now)]
    else:
        rows = tcur[tcur.team == TEAM]
    rows = rows.sort_values(["team", "p", "g", "gp"], ascending=[True, False, False, False])
    team_games = {}
    for tm_ in rows.team.unique():
        team_games[tm_] = int(query(f"SELECT game_id FROM raw_nhl_games WHERE (home='{tm_}' OR away='{tm_}') AND season={SEASON}")
                              .game_id.isin(cur_games).sum())
    num_mode = ros[ros.season == SEASON].dropna(subset=["number"]).groupby(["player_id", "team"]).number.agg(lambda n: n.mode().iloc[0])
    cards = []
    for r in rows.itertuples():
        pid, team = int(r.player_id), r.team
        c = cur.loc[pid]
        e = elig.loc[pid] if pid in elig.index else None
        mine = sorted(set(pt[(pt.player_id == pid) & (pt.team == team)].game_id) & cur_games, key=lambda g: dates[g])
        gpts = [int(gpt.get((g, pid), 0)) for g in mine]
        num = num_mode.get((pid, team))
        seasons = [dict(season=SEASON_LABEL(x.season), team=x.team, gp=int(x.gp), g=int(x.g), a=int(x.a), p=int(x.p),
                        ixg=round(float(x.ixg), 1)) for x in t[t.player_id == pid].sort_values(["season", "first_game"]).itertuples()]
        fo = int(r.fow + r.fol)
        cards.append(dict(
            id=pid, name=name.get(pid, str(pid)), team=team, number=int(num) if num is not None and num == num else None,
            pos=pos_of.get(pid, ""), grp="F" if pos_of.get(pid) in FWD else "D",
            gp=int(r.gp), g=int(r.g), a=int(r.a), p=int(r.p), ppg=int(r.ppg), sog=int(r.sog),
            ixg=round(float(r.ixg), 1), ixg_pg=round(float(r.ixg / r.gp), 2), fin=round(float(r.ig_unb - r.ixg), 1), en_g=int(r.en_g),
            close=int(r.close), reb=int(r.reb),
            hits=int(r.hits), blocks=int(r.blocks), take=int(r.take), give=int(r.give),
            fo_pct=round(float(r.fow / fo), 3) if fo >= 50 else None, fo_n=fo,
            p_rk=int(e.p_rk) if e is not None else None, ixg_rk=int(e.ixg_rk) if e is not None else None,
            of=int(n_grp.get("F" if pos_of.get(pid) in FWD else "D", 0)),
            other_team=bool(c.gp > r.gp), team_gp=team_games[team], remaining=82 - team_games[team],
            spark=list(np.cumsum(gpts).astype(int).tolist()), seasons=seasons, small=bool(r.gp < MIN_GP)))
    # ---- projections from multi-season history (src/metrics/nhl_player_ratings.py; tested on 2025-26, see player_model_backtest.json)
    from src.metrics.nhl_player_ratings import player_games, project
    pr = project(player_games(max_date=as_of), SEASON, as_of)
    team_gp = team_games.get(TEAM, 0)
    remaining = 82 - team_gp
    for c in cards:
        if c["id"] in pr.index:
            r = pr.loc[c["id"]]
            rem = c["remaining"]
            c.update(fin_ratio=round(float(r.fin_ratio), 3), rate_g82=round(float(r.g_pg * 82), 1), rate_p82=round(float(r.p_pg * 82), 1),
                     pace_p82=round(c["p"] / c["gp"] * 82, 1) if c["gp"] else None, pace_g82=round(c["g"] / c["gp"] * 82, 1) if c["gp"] else None,
                     # season totals count every team he's played for this season (traded players included)
                     proj_g=round(float(cur.loc[c["id"], "g"]) + float(r.g_pg) * rem, 1),
                     proj_p=round(float(cur.loc[c["id"], "p"]) + float(r.p_pg) * rem, 1))
            if c["other_team"]:
                c.update(season_g=int(cur.loc[c["id"], "g"]), season_p=int(cur.loc[c["id"], "p"]))
        if not league:
            c.pop("team_gp"); c.pop("remaining")
    OUT.mkdir(parents=True, exist_ok=True)
    meta = dict(team_gp=team_gp, remaining=remaining, as_of=as_of, season=SEASON_LABEL(SEASON), team=TEAM, min_gp=MIN_GP, n_groups=n_grp, lg=lg_rates,
                goal_check=dict(players=int(len(chk)), mismatches=int(len(mism))), cal=round(float(cal.loc[SEASON]), 3), carry=carry)
    if league:
        meta.update(team=None, team_gp=None, remaining=None, teams=team_games)
    (OUT / ("skaters_league.json" if league else "skaters.json")).write_text(json.dumps(dict(meta=meta, cards=cards), indent=1))
    for c in (cards if not league else []):
        print(f"{c['number']!s:>3} {c['name']:<24} {c['pos']} GP {c['gp']:>2} {c['g']}-{c['a']}-{c['p']} PPG {c['ppg']} SOG {c['sog']} "
              f"ixG {c['ixg']} fin {c['fin']:+} FO {c['fo_pct']} rk P {c['p_rk']}/{c['of']} ixG {c['ixg_rk']}")
    print(meta)
    if len(mism):
        print("GOAL MISMATCHES:\n", mism.head(20))


def latest_date():
    """Date of the most recent completed game in the data (the league cards follow the data; Sabres files stay pinned)."""
    return str(query("SELECT MAX(game_date) d FROM raw_nhl_games WHERE game_state IN ('OFF', 'FINAL')").d.iloc[0])


if __name__ == "__main__":
    import sys
    league = "--league" in sys.argv
    main(as_of=latest_date() if league and "--latest" in sys.argv else AS_OF, league=league)
