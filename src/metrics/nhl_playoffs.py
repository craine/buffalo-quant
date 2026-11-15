"""NHL playoff chances: simulate the rest of the regular season with the game model (nhl-game-v0.1) and apply the playoff format.

- Conferences and divisions come from the schedule itself: teams in the same conference meet 3+ times, teams in the same
  division 4 times for at least some pairs (true for every season 2023-24 to 2025-26). Nothing is typed in by hand.
- Each remaining game: home and away goals ~ Poisson(model expected goals); a regulation tie goes to overtime/shootout, won by
  the home team at the training-season rate; the loser there gets one point.
- Team ratings are held fixed for the rest of the season (RATING_SD = 0: no extra noise for uncertainty in team strength).
  simulate() can add normal noise to each team's ratings per simulated season via rating_sd; it is off by default.
- Format: top 3 in each division plus the next 2 by points in each conference. Ties: points, regulation wins, regulation+OT wins,
  then a coin flip (goal-differential tiebreaks are not modelled).
"""
import numpy as np
import pandas as pd

from src.ledger import nhl_game_model as M

RATING_SD = 0.0


def _components(edges):
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    groups = {}
    for x in list(parent):
        groups.setdefault(find(x), []).append(x)
    return sorted(sorted(g) for g in groups.values())


def divisions(sched):
    """sched: rows with home, away for one full season. Returns {team: (conference_id, division_id)}."""
    p = pd.concat([sched.rename(columns={"home": "a", "away": "b"}), sched.rename(columns={"away": "a", "home": "b"})])
    c = p.groupby(["a", "b"]).size()
    confs = _components([k for k, v in c.items() if v >= 3])
    divs = _components([k for k, v in c.items() if v >= 4])
    assert len(confs) == 2 and all(len(x) == 16 for x in confs), [len(x) for x in confs]
    assert len(divs) == 4 and all(len(x) == 8 for x in divs), [len(x) for x in divs]
    out = {}
    for di, d in enumerate(divs):
        ci = [i for i, cf in enumerate(confs) if d[0] in cf][0]
        assert set(d) <= set(confs[ci])
        for t in d:
            out[t] = (ci, di)
    return out


def standings(games):
    """games: final games with home, away, home_score, away_score, last_period_type. One row per team."""
    rows = []
    for side, opp in (("home", "away"), ("away", "home")):
        x = games.rename(columns={side: "team", opp: "opp", f"{side}_score": "gf", f"{opp}_score": "ga"})
        rows.append(x[["team", "gf", "ga", "last_period_type"]])
    t = pd.concat(rows)
    t["w"] = (t.gf > t.ga).astype(int)
    t["otl"] = ((t.gf < t.ga) & t.last_period_type.isin(["OT", "SO"])).astype(int)
    t["rw"] = ((t.gf > t.ga) & (t.last_period_type == "REG")).astype(int)
    t["row"] = ((t.gf > t.ga) & (t.last_period_type != "SO")).astype(int)
    s = t.groupby("team").agg(gp=("w", "size"), w=("w", "sum"), otl=("otl", "sum"), rw=("rw", "sum"), row=("row", "sum"),
                              gf=("gf", "sum"), ga=("ga", "sum"))
    s["l"] = s.gp - s.w - s.otl
    s["pts"] = 2 * s.w + s.otl
    return s


def qualify(score, teams, div):
    """score: (n_sims, n_teams) sortable standing score (ties already broken). Returns boolean (n_sims, n_teams) in-playoffs."""
    n, k = score.shape
    conf_of = np.array([div[t][0] for t in teams]); div_of = np.array([div[t][1] for t in teams])
    made = np.zeros((n, k), bool)
    for c in np.unique(conf_of):
        in_c = np.where(conf_of == c)[0]
        top3 = np.zeros((n, k), bool)
        for d in np.unique(div_of[in_c]):
            idx = np.where(div_of == d)[0]
            order = np.argsort(-score[:, idx], axis=1)[:, :3]
            rows = np.repeat(np.arange(n), 3)
            top3[rows, idx[order].ravel()] = True
        rest = np.where(top3[:, in_c], -np.inf, score[:, in_c])
        wc = np.argsort(-rest, axis=1)[:, :2]
        rows = np.repeat(np.arange(n), 2)
        made[rows, in_c[wc].ravel()] = True
        made |= top3
    return made


def simulate(t, coef, p_ot, season, date, played, remaining, div, n_sims=10000, seed=7, rating_sd=RATING_SD, adjust=None):
    """Simulate the remaining games. played: final games so far; remaining: rows with home, away.
    adjust: optional {team: (d_off, d_def)} added to that team's ratings (goals a game), for what-if runs.
    Returns (teams, made (n_sims, n_teams) bool, final points (n_sims, n_teams))."""
    off, de, lg, ratio = M.ratings(t, season, date)
    teams = sorted(div)
    ix = {tm: i for i, tm in enumerate(teams)}
    o = np.array([off.get(tm, lg) for tm in teams]); d = np.array([de.get(tm, lg) for tm in teams])
    for tm, (dx, dy) in (adjust or {}).items():
        o[ix[tm]] += dx; d[ix[tm]] += dy
    rng = np.random.default_rng(seed)
    O = o + rng.normal(0, rating_sd, (n_sims, len(teams)))
    D = d + rng.normal(0, rating_sd, (n_sims, len(teams)))
    h = remaining.home.map(ix).to_numpy(); a = remaining.away.map(ix).to_numpy()
    raw_h = (O[:, h] + D[:, a] - lg) * ratio
    raw_a = (O[:, a] + D[:, h] - lg) * ratio
    mu_h = np.maximum(0.3, coef[0] + coef[1] * raw_h + coef[2])
    mu_a = np.maximum(0.3, coef[0] + coef[1] * raw_a)
    gh, ga = rng.poisson(mu_h), rng.poisson(mu_a)
    tie = gh == ga
    home_ot = rng.random(gh.shape) < p_ot
    hw = (gh > ga) | (tie & home_ot)
    st = standings(played).reindex(teams).fillna(0)
    pts = np.tile(st.pts.to_numpy(float), (n_sims, 1))
    rw = np.tile(st.rw.to_numpy(float), (n_sims, 1))
    rowv = np.tile(st.row.to_numpy(float), (n_sims, 1))
    R = np.broadcast_to(np.arange(n_sims)[:, None], gh.shape)
    H = np.broadcast_to(h, gh.shape); A = np.broadcast_to(a, gh.shape)
    np.add.at(pts, (R, H), np.where(hw, 2, np.where(tie, 1, 0)))
    np.add.at(pts, (R, A), np.where(~hw, 2, np.where(tie, 1, 0)))
    np.add.at(rw, (R, H), (gh > ga).astype(float))
    np.add.at(rw, (R, A), (ga > gh).astype(float))
    np.add.at(rowv, (R, H), hw.astype(float))    # shootout wins aren't separated from OT wins in the simulation
    np.add.at(rowv, (R, A), (~hw).astype(float))
    score = pts + rw * 1e-3 + rowv * 1e-6 + rng.random(pts.shape) * 1e-9
    return teams, qualify(score, teams, div), pts

