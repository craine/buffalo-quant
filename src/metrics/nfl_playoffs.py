"""NFL season simulator: playoff chances, division titles, and the week a team clinches its division.

How it works (every input is computed from repo data):
- Team strength: the points model (src/ledger/points_model.py) projects each remaining game's score for both teams
  from points-per-drive ratings as of the simulation week. Ratings stay fixed through the simulated weeks.
- Game results: each game replays one real past game's pair of misses (home miss, away miss) from the model's training
  seasons on top of today's projections, the same way the published win chances work. A tied replay is a coin flip.
- Quarterbacks: when a team's expected starter isn't the QB who has taken most of its dropbacks this season, the team
  scores `qb_effect()['team']` fewer points and its opponent `qb_effect()['opp']` more, measured from 2019-2025 games.
  Absences without a known return are drawn from how long past absences lasted (`absence_lengths()`).
- Seeding: 4 division winners + 3 wild cards per conference. Tiebreakers are simplified (see `_rank`): head-to-head,
  division record (division ties), conference record, then a coin flip. Strength of victory/schedule, common games and
  points-based steps are skipped.
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from src.db import query
from src.ledger import points_model as pm

DIVISIONS = {
    "AFC East": ["BUF", "MIA", "NE", "NYJ"], "AFC North": ["BAL", "CIN", "CLE", "PIT"],
    "AFC South": ["HOU", "IND", "JAX", "TEN"], "AFC West": ["DEN", "KC", "LV", "LAC"],
    "NFC East": ["DAL", "NYG", "PHI", "WAS"], "NFC North": ["CHI", "DET", "GB", "MIN"],
    "NFC South": ["ATL", "CAR", "NO", "TB"], "NFC West": ["ARI", "LA", "SF", "SEA"],
}
DIV_OF = {t: d for d, ts in DIVISIONS.items() for t in ts}
CONF_OF = {t: d.split()[0] for t, d in DIV_OF.items()}
QB_SEASONS = range(2019, 2026)
ERA_ABBR = {"OAK": "LV", "SD": "LAC", "STL": "LA"}  # older abbreviations in raw tables


# ---------------------------------------------------------------- quarterbacks
def _starters(seasons):
    d = query(f"""SELECT season, week, game_id, play_id, posteam AS team, COALESCE(passer_player_id, rusher_player_id) AS qb
                  FROM raw_pbp WHERE season BETWEEN {min(seasons)} AND {max(seasons)} AND season_type='REG' AND qb_dropback=1
                  AND COALESCE(passer_player_id, rusher_player_id) IS NOT NULL""")
    st = (d.sort_values("play_id").groupby(["game_id", "team"]).first().reset_index()
          [["season", "week", "game_id", "team", "qb"]].rename(columns={"qb": "starter"}))
    cnt = d.groupby(["season", "team", "week", "qb"]).size().rename("n").reset_index()
    return st, cnt


def primary_to_date(cnt, season, team, week):
    """The QB with the most dropbacks for `team` in `season` before `week` (None before two games)."""
    x = cnt[(cnt.season == season) & (cnt.team == team) & (cnt.week < week)]
    if x.week.nunique() < 2:
        return None
    return x.groupby("qb").n.sum().idxmax()


@lru_cache(maxsize=1)
def _qb_games():
    st, cnt = _starters(QB_SEASONS)
    rows = []
    for r in st.itertuples():
        p = primary_to_date(cnt, r.season, r.team, r.week)
        if p is not None:
            rows.append((r.game_id, r.team, r.season, r.week, r.starter, p, r.starter != p))
    return pd.DataFrame(rows, columns=["game_id", "team", "season", "week", "starter", "primary", "backup"])


@lru_cache(maxsize=1)
def qb_effect():
    """Points-model misses in 2019-2025 games, split by whether the team (and its opponent) started its season's main QB."""
    coef, _ = pm.fit(pm.build_frame(pm.TRAIN))
    f = pm.build_frame(list(QB_SEASONS))
    f["miss"] = f.score - pm.predict(coef, f.raw, f.home)
    m = f.merge(_qb_games(), on=["game_id", "team", "season", "week"])
    o = m[["game_id", "team", "backup"]].rename(columns={"team": "opp", "backup": "opp_backup"})
    m = m.merge(o, on=["game_id", "opp"])
    own = m.groupby("backup").miss.agg(["mean", "count", "std"])
    opp = m.groupby("opp_backup").miss.agg(["mean", "count", "std"])
    se = lambda g: float(np.sqrt(g.loc[True, "std"] ** 2 / g.loc[True, "count"] + g.loc[False, "std"] ** 2 / g.loc[False, "count"]))
    return dict(team=float(own.loc[True, "mean"] - own.loc[False, "mean"]), team_se=se(own),
                opp=float(opp.loc[True, "mean"] - opp.loc[False, "mean"]), opp_se=se(opp),
                n_backup=int(own.loc[True, "count"]), n_games=int(own["count"].sum()),
                share_backup=float(own.loc[True, "count"] / own["count"].sum()))


@lru_cache(maxsize=1)
def absence_lengths():
    """Lengths (games) of past stretches where a team started someone other than its main QB and the main QB came back."""
    g = _qb_games().sort_values(["season", "team", "week"])
    out = []
    for _, x in g.groupby(["season", "team"]):
        x = x.reset_index(drop=True)
        i = 0
        while i < len(x):
            if x.backup[i]:
                p, j = x.primary[i], i
                while j < len(x) and x.backup[j] and x.primary[j] == p:
                    j += 1
                if j < len(x) and x.starter[j] == p:
                    out.append(j - i)
                i = j
            else:
                i += 1
    return np.array(out)


def draw_absence(rng, missed_so_far, at_least=0):
    """Games still to miss, drawn from past absences that lasted longer than `max(missed_so_far, at_least - 1)` games."""
    a = absence_lengths()
    pool = a[a > max(missed_so_far, at_least - 1)] if at_least else a[a > missed_so_far]
    return int(rng.choice(pool) - missed_so_far)


# ---------------------------------------------------------------- schedule and standings
def season_games(season):
    g = query(f"""SELECT game_id, week, gameday, home_team, away_team, home_score, away_score FROM raw_schedules
                  WHERE season={season} AND game_type='REG' ORDER BY week, gameday, gametime""")
    return g.replace({"home_team": ERA_ABBR, "away_team": ERA_ABBR})


TEAMS = sorted(DIV_OF)
TI = {t: i for i, t in enumerate(TEAMS)}
DIV_IDX = np.array([sorted(DIVISIONS).index(DIV_OF[t]) for t in TEAMS])
CONF_IDX = np.array([0 if CONF_OF[t] == "AFC" else 1 for t in TEAMS])
SAME_DIV = DIV_IDX[:, None] == DIV_IDX[None, :]
SAME_CONF = CONF_IDX[:, None] == CONF_IDX[None, :]


class Season:
    """Results of one full (real + simulated) season as matrices: W[t, o] = wins by t over o, G[t, o] = games."""

    def __init__(self, t, o, w):
        self.W = np.zeros((32, 32)); self.G = np.zeros((32, 32))
        np.add.at(self.W, (t, o), w); np.add.at(self.G, (t, o), 1)
        self.wins = self.W.sum(1); self.games = self.G.sum(1)
        self.pct = np.divide(self.wins, self.games, out=np.zeros(32), where=self.games > 0)

    def rec(self, t, mask):
        g = self.G[t][mask].sum()
        return self.W[t][mask].sum() / g if g else 0.5


def _rank(teams, S, rng, division=False):
    """Order teams by win pct, breaking ties: head-to-head among the tied teams, division record (division ties only),
    conference record, then a coin flip. Simplified: one pass over the whole tied group."""
    teams = list(teams)
    out = []
    for v in sorted({S.pct[t] for t in teams}, reverse=True):
        grp = [t for t in teams if S.pct[t] == v]
        if len(grp) > 1:
            m = np.zeros(32, bool); m[grp] = True
            key = {t: (S.rec(t, m), S.rec(t, SAME_DIV[t]) if division else 0, S.rec(t, SAME_CONF[t]), rng.random()) for t in grp}
            grp.sort(key=lambda t: key[t], reverse=True)
        out += grp
    return out


def seed(S, rng):
    """Seeds 1-7 per conference. Returns array seeds[team] (0 = out) and {division index: winner}."""
    seeds = np.zeros(32, int); winners = {}
    for c in (0, 1):
        w = []
        for d in sorted({DIV_IDX[i] for i in range(32) if CONF_IDX[i] == c}):
            win = _rank(np.where(DIV_IDX == d)[0], S, rng, division=True)[0]
            winners[d] = win; w.append(win)
        for i, t in enumerate(_rank(w, S, rng)):
            seeds[t] = i + 1
        rest = [t for t in range(32) if CONF_IDX[t] == c and t not in w]
        for i, t in enumerate(_rank(rest, S, rng)[:3]):
            seeds[t] = 5 + i
    return seeds, winners


def season_games(season):
    g = query(f"""SELECT game_id, week, gameday, home_team, away_team, home_score, away_score FROM raw_schedules
                  WHERE season={season} AND game_type='REG' ORDER BY week, gameday, gametime""")
    return g.replace({"home_team": ERA_ABBR, "away_team": ERA_ABBR})


# ---------------------------------------------------------------- strength drift
@lru_cache(maxsize=None)
def strength_drift(seasons, week=11, con=None):
    """How far teams' scoring (off) and points allowed (def) drift from the frozen week-`week` ratings over the rest of
    a season: the spread of team-season average misses beyond what game-to-game noise explains, in points per game."""
    g = pm._drives(con); sc = pm._scores(con)
    coef, _ = pm.fit(pm.build_frame(pm.TRAIN, con=con))
    rows = []
    for s in seasons:
        o, d, lg, pace, lgp = pm.ratings(g, s, week)
        for r in sc[(sc.season == s) & (sc.week >= week)].itertuples():
            rows.append((s, r.team, r.opp, r.score - pm.predict(coef, pm.raw_prediction(o, d, lg, pace, lgp, r.team, r.opp)[0], r.home)))
    f = pd.DataFrame(rows, columns=["season", "team", "opp", "miss"])
    gv = f.miss.var()
    out = {}
    for side, col in (("off", "team"), ("def", "opp")):
        tm = f.groupby(["season", col]).miss.agg(["mean", "count"])
        out[side] = float(np.sqrt(max(tm["mean"].var() - (gv / tm["count"]).mean(), 0)))
    out["n_games"] = len(f)
    return out


# ---------------------------------------------------------------- simulation
def projections(season, week, con=None, exclude=()):
    """Projected points for both teams in every game from `week` on (plus any `exclude`d earlier game, treated as unplayed),
    using ratings from games before `week`."""
    g = pm._drives(con)
    if exclude:
        g = g[~g.game_id.isin(exclude)]
    o, d, lg, pace, lgp = pm.ratings(g, season, week)
    coef, pairs = pm.paired_misses(con)
    sched = season_games(season)
    left = sched[(sched.week >= week) | sched.game_id.isin(exclude)].copy()
    left["p_home"] = [pm.predict(coef, pm.raw_prediction(o, d, lg, pace, lgp, h, a)[0], 1) for h, a in zip(left.home_team, left.away_team)]
    left["p_away"] = [pm.predict(coef, pm.raw_prediction(o, d, lg, pace, lgp, a, h)[0], 0) for h, a in zip(left.home_team, left.away_team)]
    return sched, left.reset_index(drop=True), pairs


def simulate(season, week, n=10000, qb_plan=None, seed_=2026, track_clinch=(), con=None, coin_flip=False, exclude=(), drift=True, shrink=1.0, drift_seasons=None, coin_share=0.0):
    """Simulate the rest of `season` from `week`. Returns per-team chances, seed distribution, and for teams in
    `track_clinch` a list with each sim's division-clinch week (None if the team didn't win the division).

    qb_plan: {team: {"weeks_out": set of weeks, "draw": dict(missed_so_far=k, at_least=m, first_week=w) or None}}:
    weeks in which the team's expected starter isn't its main QB. `coin_flip`: every game 50/50 (the baseline).
    `drift`: each simulated season draws a lasting scoring shift for every team's offense and defense, sized by
    `strength_drift` on the seasons before `season` (from 2019). `coin_share`: share of simulated seasons played as
    50/50 games instead (0.5 = the half-model, half-standings mix the published odds use).
    """
    rng = np.random.default_rng(seed_)
    sched, left, pairs = projections(season, week, con, exclude)
    played = sched[~sched.game_id.isin(left.game_id)].dropna(subset=["home_score"])
    hw0 = np.where(played.home_score > played.away_score, 1.0, np.where(played.home_score == played.away_score, 0.5, 0.0))
    bh, ba = played.home_team.map(TI).to_numpy(), played.away_team.map(TI).to_numpy()
    bt, bo, bw = np.r_[bh, ba], np.r_[ba, bh], np.r_[hw0, 1 - hw0]
    lh, la, lw = left.home_team.map(TI).to_numpy(), left.away_team.map(TI).to_numpy(), left.week.to_numpy()
    T, O = np.r_[bt, lh, la], np.r_[bo, la, lh]
    fx = qb_effect() if qb_plan else None
    weeks = sorted(set(lw))
    dsd = strength_drift(tuple(drift_seasons or range(2019, season)), week) if drift else None
    playoffs, division, seed1, wins = (np.zeros(32) for _ in range(4))
    seed_counts = np.zeros((32, 8))
    clinch = {t: [] for t in track_clinch}
    for _ in range(n):
        ph, pa = left.p_home.to_numpy().copy(), left.p_away.to_numpy().copy()
        if shrink != 1.0:  # pull each game's projected margin toward even, keeping the projected total
            mid = (ph + pa) / 2
            ph, pa = mid + shrink * (ph - mid), mid + shrink * (pa - mid)
        for t, plan in (qb_plan or {}).items():
            ws = set(plan.get("weeks_out", set()))
            dr = plan.get("draw")
            if dr:
                k = draw_absence(rng, dr.get("missed_so_far", 0), dr.get("at_least", 0))
                tg = sorted(w for w, h, a in zip(lw, lh, la) if (h == TI[t] or a == TI[t]) and w >= dr["first_week"])
                ws |= set(tg[:k])
            if ws:
                hm = (lh == TI[t]) & np.isin(lw, list(ws)); am = (la == TI[t]) & np.isin(lw, list(ws))
                ph[hm] += fx["team"]; pa[hm] += fx["opp"]; pa[am] += fx["team"]; ph[am] += fx["opp"]
        if dsd:
            off = rng.normal(0, dsd["off"], 32); dfn = rng.normal(0, dsd["def"], 32)
            ph = ph + off[lh] + dfn[la]; pa = pa + off[la] + dfn[lh]
        if coin_flip or rng.random() < coin_share:
            hw = (rng.random(len(left)) < 0.5).astype(float)
        else:
            idx = rng.integers(0, len(pairs), len(left))
            dlt = (ph + pairs[idx, 0]) - (pa + pairs[idx, 1])
            hw = np.where(np.abs(dlt) <= 0.5, (rng.random(len(left)) < 0.5).astype(float), (dlt > 0).astype(float))
        S = Season(T, O, np.r_[bw, hw, 1 - hw])
        seeds, winners = seed(S, rng)
        wins += S.wins
        playoffs += seeds > 0; seed1 += seeds == 1
        seed_counts[np.arange(32), seeds] += 1
        for w in winners.values():
            division[w] += 1
        for t in track_clinch:
            i = TI[t]
            clinch[t].append(_clinch_week(i, S, lh, la, lw, hw, weeks) if winners[DIV_IDX[i]] == i else None)
    tab = pd.DataFrame(dict(playoffs=playoffs / n, division=division / n, seed1=seed1 / n, wins=wins / n), index=TEAMS)
    tab["conf"] = tab.index.map(CONF_OF); tab["div"] = tab.index.map(DIV_OF)
    seeds_df = pd.DataFrame(seed_counts / n, index=TEAMS)
    return tab, seeds_df, clinch


def _clinch_week(i, S, lh, la, lw, hw, weeks):
    """First simulated week after which no division rival can reach team i's win total even by winning out.
    A possible tie at the top doesn't count as clinched (tiebreakers skipped), so the real clinch can come a week earlier."""
    rivals = [j for j in range(32) if DIV_IDX[j] == DIV_IDX[i] and j != i]
    final = S.wins
    for w in weeks:
        after = lw > w
        def wins_thru(j):  # final wins minus wins earned after week w
            return final[j] - hw[after & (lh == j)].sum() - (1 - hw[after & (la == j)]).sum()
        def left_after(j):
            return int((after & ((lh == j) | (la == j))).sum())
        mine = wins_thru(i)
        if all(wins_thru(j) + left_after(j) < mine for j in rivals):
            return int(w)
    return None


# ---------------------------------------------------------------- backtest
def actual_playoff_teams(season):
    p = query(f"SELECT home_team, away_team FROM raw_schedules WHERE season={season} AND game_type IN ('WC','DIV')")
    return {ERA_ABBR.get(t, t) for t in set(p.home_team) | set(p.away_team)}


def backtest(seasons=(2023, 2024, 2025), week=11, n=2000, shrink=1.0, drift_seasons=None):
    """Playoff chances from `week` of past seasons (no QB adjustments) scored against who made it, vs. 50/50 games."""
    rows = []
    for s in seasons:
        made = actual_playoff_teams(s)
        ds = tuple(x for x in (drift_seasons or range(2019, s)) if x != s)
        tab, _, _ = simulate(s, week, n=n, seed_=s, shrink=shrink, drift_seasons=ds)
        base, _, _ = simulate(s, week, n=n, coin_flip=True, seed_=s)
        for t in tab.index:
            rows.append(dict(season=s, team=t, p=tab.loc[t, "playoffs"], p_coin=base.loc[t, "playoffs"], made=int(t in made)))
    return pd.DataFrame(rows)
