"""Are the Sabres done? Playoff chances, what's going wrong, what lasts, who's underperforming, and what would change it.

Every number computed here from raw_nhl_games, raw_nhl_schedule (the NHL's full schedule, future games included),
clean_nhl_shots_xg and the skater cards (src/reports/skater_cards.py), pinned to games through AS_OF.
Writes reports/2026-11-15-sabres-playoff-chances.md, three PNGs and a hero JSON.
"""
import json
import pathlib
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger import nhl_game_model as M
from src.metrics import nhl_playoffs as P
from src.metrics.nhl_team import goalie_season, shots
from src.reports.defense_baseline import BLUE, INK, MUTED
from src.reports.sabres_postgame import finish, ordn
import src.reports.skater_cards as SC

OUT = ROOT / "reports"
SLUG = "2026-11-15-sabres-playoff-chances"
AS_OF, NEXT = "2026-11-14", "2026-11-15"     # games through AS_OF; ratings use games before NEXT
SEASON, US = 20262027, "BUF"
PAST = (20232024, 20242025, 20252026)
N_SIMS, CUT_GP = 20000, 20
PP, PK = ("5v4", "5v3", "4v3"), ("4v5", "3v5", "3v4")
GOLD, LIGHT = "#FFB81C", "#C9CDD4"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#D5D8DE", "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK, "font.size": 11})


def pmf(ps):
    out = np.array([1.0])
    for q in ps:
        out = np.convolve(out, [1 - q, q])
    return out


def cut_date(g, n=CUT_GP):
    """First date by which teams have played n games on average (the same point of the season as now)."""
    x = pd.concat([g[["game_date", "home"]].rename(columns={"home": "team"}), g[["game_date", "away"]].rename(columns={"away": "team"})])
    for d in sorted(x.game_date.unique()):
        if x[x.game_date <= d].groupby("team").size().mean() >= n:
            return d


def nxt(d):
    return (pd.Timestamp(d) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")


def main():
    t, coef, p_ot, _ = M.train()
    G = query("SELECT * FROM raw_nhl_games")
    sched = query(f"SELECT * FROM raw_nhl_schedule WHERE season = {SEASON}")
    played = G[(G.season == SEASON) & (G.game_date <= AS_OF)]
    assert played.game_date.max() == AS_OF
    rem = sched[~sched.game_id.isin(played.game_id)]
    assert set(rem.game_state) <= {"FUT"} or rem.game_date.min() > AS_OF
    div = P.divisions(sched)
    gpt = pd.concat([sched.home, sched.away]).value_counts()
    assert gpt.nunique() == 1
    n_season = int(gpt.iloc[0])                                   # 84 games a team this season
    ours = sorted(t_ for t_, v in div.items() if v == div[US])
    east = sorted(t_ for t_, v in div.items() if v[0] == div[US][0])

    # ---- standings now
    st = P.standings(played)
    b = st.loc[US]
    gp, n_left = int(b.gp), n_season - int(b.gp)

    # ---- the Ledger call (logged by src/ledger/log_sabres_playoffs.py before the next game)
    led = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    call = led[led.game_id == "NHL_20262027_season_BUF_playoffs"].iloc[0]

    # ---- the projection
    teams, made, pts = P.simulate(t, coef, p_ot, SEASON, NEXT, played, rem, div, n_sims=N_SIMS)
    ix = teams.index(US)
    p_buf = float(made[:, ix].mean())
    assert round(p_buf, 2) == float(call.probability)
    e_ix = [teams.index(x) for x in east]
    cut = np.array([pts[i, e_ix][made[i, e_ix]].min() for i in range(N_SIMS)])
    cut_med, cut_lo, cut_hi = np.median(cut), *np.percentile(cut, [10, 90])
    buf_med, buf_lo, buf_hi = np.median(pts[:, ix]), *np.percentile(pts[:, ix], [10, 90])
    need = cut_med - b.pts
    need_pg = need / n_left
    east_tab = pd.DataFrame({"team": east, "p": [float(made[:, teams.index(x)].mean()) for x in east],
                             "pts": [int(st.loc[x, "pts"]) for x in east], "gp": [int(st.loc[x, "gp"]) for x in east],
                             "proj": [float(np.median(pts[:, teams.index(x)])) for x in east]}).sort_values("p", ascending=False)
    buf_rank_p = int((east_tab.p > p_buf).sum()) + 1
    lw = P.standings(G[G.season == 20252026]).loc[US]

    # ---- did it work before? same point of the season, 2023-24 to 2025-26
    t_ = t
    bt = []
    for season in PAST:
        g = G[G.season == season]; dv = P.divisions(g); d = cut_date(g)
        tm, mk, _ = P.simulate(t_, coef, p_ot, season, nxt(d), g[g.game_date <= d], g[g.game_date > d], dv, n_sims=4000)
        fin = P.standings(g).reindex(tm)
        actual = P.qualify((fin.pts + fin.rw * 1e-3 + fin.row * 1e-6).to_numpy()[None, :], tm, dv)[0]
        now = P.standings(g[g.game_date <= d]).reindex(tm)
        rng = np.random.default_rng(1)
        inspot = P.qualify((now.pts / now.gp).to_numpy()[None, :] + rng.random((1, len(tm))) * 1e-9, tm, dv)[0]
        for k, x in enumerate(tm):
            bt.append(dict(season=season, team=x, p=float(mk[:, k].mean()), made=int(actual[k]), inspot=int(inspot[k])))
    bt = pd.DataFrame(bt)
    brier = float(((bt.p - bt.made) ** 2).mean())
    rate = bt.groupby("inspot").made.mean()          # "in a playoff spot today" baseline, all three seasons
    brier_spot = float(((bt.inspot.map(rate) - bt.made) ** 2).mean())
    lo = bt[(bt.p >= 0.05) & (bt.p <= 0.30)]
    lo_n, lo_made, lo_said = len(lo), int(lo.made.sum()), float(lo.p.mean())
    buf_last = bt[(bt.season == 20252026) & (bt.team == US)].iloc[0]
    assert buf_last.made == 1

    # ---- what's going wrong
    keep = G[G.game_date <= AS_OF]
    s = shots(); s = s[s.game_id.isin(set(keep.game_id))].copy()
    unb = (s.unblocked == 1) & (s.empty_net_against == 0)
    cal = s[unb].groupby("season").goal.sum() / s[unb].groupby("season").xg.sum()
    s["xg"] = s.xg * s.season.map(cal)
    u = s[unb & (s.season == SEASON)]
    gpn = st.gp
    T = pd.DataFrame({"xgf": u.groupby("team").xg.sum() / gpn, "xga": u.groupby("opp").xg.sum() / gpn,
                      "fin": (u[u.goal == 1].groupby("team").size() - u.groupby("team").xg.sum()) / gpn,
                      "gk": (u.groupby("opp").xg.sum() - u[u.goal == 1].groupby("opp").size()) / gpn})
    ev = u[u.strength == "5v5"]
    T["ev"] = ev.groupby("team").xg.sum() / (ev.groupby("team").xg.sum() + ev.groupby("opp").xg.sum())
    T["ev_xga"] = ev.groupby("opp").xg.sum() / gpn
    sh = u[u.strength.isin(PP)]                       # opponent on the power play = Buffalo shorthanded
    T["sh_xga"] = sh.groupby("opp").xg.sum() / gpn
    T["sh_ga"] = sh[sh.goal == 1].groupby("opp").size().reindex(T.index).fillna(0) / gpn
    T["pp_xgf"] = sh.groupby("team").xg.sum() / gpn
    T["pp_gf"] = sh[sh.goal == 1].groupby("team").size().reindex(T.index).fillna(0) / gpn
    T = T.fillna(0)
    hi = lambda c: int(T[c].rank(ascending=False, method="min").loc[US])     # 1 = highest
    loo = lambda c: int(T[c].rank(ascending=True, method="min").loc[US])     # 1 = lowest
    B, L = T.loc[US], T.mean()
    n_sh_ga = int(round(B.sh_ga * gp))

    # points the chances were worth (regulation shots replayed; ties split at the OT rate)
    bg = played[(played.home == US) | (played.away == US)]
    e_pts = 0.0
    for r in bg.itertuples():
        x = u[(u.game_id == r.game_id) & (u.period <= 3)]
        j = np.outer(pmf(x[x.team == US].xg.values), pmf(x[x.team != US].xg.values))
        pw, pt = np.tril(j, -1).sum(), np.trace(j)
        e_pts += 2 * pw + pt * (1 + (p_ot if r.home == US else 1 - p_ot))

    # what lasts: first 20 games vs the rest of the season, every team, 2023-24 to 2025-26
    ua = s[unb & s.season.isin(PAST)]
    rows = []
    for season in PAST:
        g = G[G.season == season]
        tg = pd.concat([g[["game_id", "game_date", "home"]].rename(columns={"home": "team"}),
                        g[["game_id", "game_date", "away"]].rename(columns={"away": "team"})]).sort_values(["game_date", "game_id"])
        tg["n"] = tg.groupby("team").cumcount() + 1
        early = set(zip(tg[tg.n <= CUT_GP].game_id, tg[tg.n <= CUT_GP].team))
        us_ = ua[ua.season == season].copy()
        us_["e_t"] = [(a, c) in early for a, c in zip(us_.game_id, us_.team)]
        us_["e_o"] = [(a, c) in early for a, c in zip(us_.game_id, us_.opp)]
        for tm in sorted(g.home.unique()):
            rec = {}
            for lab, e in (("1", True), ("2", False)):
                fo, ag = us_[(us_.team == tm) & (us_.e_t == e)], us_[(us_.opp == tm) & (us_.e_o == e)]
                n = fo.game_id.nunique()
                rec.update({f"xga_{lab}": ag.xg.sum() / n, f"xgf_{lab}": fo.xg.sum() / n,
                            f"fin_{lab}": (fo.goal.sum() - fo.xg.sum()) / n, f"gk_{lab}": (ag.xg.sum() - ag.goal.sum()) / n,
                            f"sh_{lab}": ag[ag.strength.isin(PP)].xg.sum() / n})
            rows.append(rec)
    c = pd.DataFrame(rows)
    carry = {k: float(c[f"{k}_1"].corr(c[f"{k}_2"])) for k in ("xgf", "xga", "sh", "fin", "gk")}
    n_carry = len(c)

    # ---- who's underperforming (skater cards, pinned to AS_OF, written to a temp folder)
    with tempfile.TemporaryDirectory() as tmp:
        SC.OUT = pathlib.Path(tmp)
        SC.main(as_of=AS_OF, league=False)
        cards = json.loads((pathlib.Path(tmp) / "skaters.json").read_text())
    cd = pd.DataFrame(cards["cards"])
    cd = cd[cd.gp >= 10].copy()
    cd["gap"] = cd.pace_p82 - cd.rate_p82
    slow = cd.sort_values("gap").head(5)
    fast = cd.sort_values("gap", ascending=False).head(3)
    fin_low = cd.sort_values("fin").iloc[0]
    team_fin = float(B.fin * gp)
    gl = goalie_season(s[s.season == SEASON])
    gl = gl[gl.team == US].sort_values("shots_faced", ascending=False)
    all_g = goalie_season(s[s.season == SEASON])

    # ---- what would change it: what-ifs
    off, de, lg, ratio = M.ratings(t, SEASON, NEXT)
    sh_fix = float(B.sh_xga - L.sh_xga)                 # shorthanded chances allowed above league average, per game
    cases = [("As things stand", None),
             ("Shorthanded chances allowed\ncut to league average", {US: (0, -sh_fix)}),
             ("All chances allowed\ncut to league average", {US: (0, lg - de[US])}),
             ("Create 0.2 more goals'\nworth of chances a game", {US: (0.2, 0)}),
             ("Both: average defense\nand 0.2 more created", {US: (0.2, lg - de[US])})]
    wi = []
    for lab, adj in cases:
        tm, mk, pt_ = P.simulate(t, coef, p_ot, SEASON, NEXT, played, rem, div, n_sims=N_SIMS, adjust=adj)
        wi.append((lab, float(mk[:, tm.index(US)].mean()), float(np.median(pt_[:, tm.index(US)]))))
    assert abs(wi[0][1] - p_buf) < 1e-9

    # ---- chart 1: where the season could finish
    fig, ax = plt.subplots(figsize=(9.5, 5.0), dpi=200)
    bins = np.arange(pts[:, ix].min() - 0.5, pts[:, ix].max() + 1.5, 2)
    ax.hist(pts[:, ix], bins=bins, color=BLUE, alpha=0.9, zorder=2, weights=np.full(N_SIMS, 1 / N_SIMS))
    ax.axvspan(cut_lo, cut_hi, color=GOLD, alpha=0.25, zorder=1)
    ax.axvline(cut_med, color=INK, lw=1.5, ls="--")
    ax.text(cut_med + 0.6, ax.get_ylim()[1] * 0.92, f"Points it usually takes\nto get in: about {cut_med:.0f}", fontsize=9.5, color=INK)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_xlabel("Sabres' final points"); ax.set_ylabel("Share of simulated seasons")
    ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, f"The Sabres finish ahead of the line in about {p_buf:.0%} of seasons",
           f"Sabres' final points in {N_SIMS:,} simulated seasons, from {int(b.pts)} points in {gp} games. Shaded: where the last Eastern playoff spot usually lands.",
           f"Model nhl-game-v0.1 ratings from games through Nov. 14, 2026; the NHL's remaining schedule ({n_left} Sabres games, {len(rem):,} in all). {n_season}-game season.")
    fig.savefig(OUT / "sabres-playoffs-points.png"); plt.close(fig)

    # ---- chart 2: what carries over
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=200)
    lab2 = [("Chances created", carry["xgf"]), ("Chances allowed", carry["xga"]), ("Chances allowed\nwhile shorthanded", carry["sh"]),
            ("Finishing\n(goals vs. chances)", carry["fin"]), ("Goaltending\n(goals saved vs. average)", carry["gk"])]
    ax.barh(range(5)[::-1], [v for _, v in lab2], color=[BLUE, BLUE, BLUE, LIGHT, LIGHT], zorder=2)
    for k, (l_, v) in enumerate(lab2):
        ax.text(max(v, 0) + 0.01, 4 - k, f"{v:.2f}", va="center", fontsize=10, color=INK)
    ax.set_yticks(range(5)[::-1], [l_ for l_, _ in lab2], fontsize=9.5)
    ax.set_xlim(0, 1); ax.set_xlabel("How much the first 20 games tell you about the rest (0 = nothing, 1 = everything)")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Chances carry over. Finishing and goaltending streaks don't",
           "Each NHL team's first 20 games against the rest of its season, per game.",
           f"All 32 teams, 2023-24 to 2025-26 ({n_carry} team-seasons). Correlation between first-20-game and rest-of-season values.")
    fig.savefig(OUT / "sabres-playoffs-carry.png"); plt.close(fig)

    # ---- chart 3: what-ifs
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    vals = [v for _, v, _ in wi]
    ax.barh(range(len(wi))[::-1], vals, color=[INK] + [BLUE] * (len(wi) - 1), zorder=2)
    for k, v in enumerate(vals):
        ax.text(v + 0.01, len(wi) - 1 - k, f"{v:.0%}", va="center", fontsize=10, color=INK)
    ax.set_yticks(range(len(wi))[::-1], [l_ for l_, _, _ in wi], fontsize=9.5)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_xlabel("Sabres' chance to make the playoffs")
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Fewer chances against or more chances for: either one about doubles it",
           "Sabres' playoff chance if each change held for the rest of the season. Everything else as it stands.",
           f"{N_SIMS:,} simulated seasons each, games through Nov. 14, 2026. One goal's worth of chances = shots whose chances of going in add up to one.")
    fig.savefig(OUT / "sabres-playoffs-whatif.png"); plt.close(fig)

    def frac(p):
        return f"about a 1-in-{round(1 / p)}" if p < 0.5 else f"a {p:.0%}"

    east_rows = "\n".join(
        f"| {'**' if r.team == US else ''}{r.team}{'**' if r.team == US else ''} | {r.pts} in {r.gp} | {r.proj:.0f} | {r.p:.0%} |"
        for r in east_tab.itertuples())
    slow_rows = "\n".join(
        f"| {r.name} | {r.pos} | {r.gp} | {r.g}-{r.a}-{r.p} | {r.pace_p82:.0f} | {r.rate_p82:.0f} |" for r in slow.itertuples())
    g_rows = "\n".join(
        f"| {r['name']} | {int(r.shots_faced)} | {r['sv%']:.1%} | {r.GSAx:+.1f} |" for _, r in gl.iterrows())
    wi_rows = "\n".join(f"| {l_.replace(chr(10), ' ')} | {v:.0%} | {m:.0f} |" for l_, v, m in wi)

    md = f"""# Are the Sabres done? Not yet, but they need to stop giving up so many chances

**After {gp} games, our model gives the Sabres {frac(p_buf)} chance to make the playoffs ({p_buf:.0%}). They're {int(b.w)}-{int(b.l)}-{int(b.otl)} with {int(b.pts)} points, and it
usually takes about {cut_med:.0f} points to get the last spot in the East: {need:.0f} more in their last {n_left} games. Their scoring slump and shaky
goaltending rarely last. The real problem is how many chances they give up, especially when they're
shorthanded, and that kind of problem tends to stick. Fix it, and their chances roughly double.**

*Numbers are through Nov. 14, 2026, the Sabres' first 20 games of {n_season}. Early-season numbers move a lot.*

![Where the season could finish](sabres-playoffs-points.png)

## Where they stand

The Sabres have {int(b.pts)} points from {gp} games ({int(b.w)}-{int(b.l)}-{int(b.otl)}). Our model plays out the other {len(rem):,} games left on the NHL's schedule {N_SIMS:,} times.
In the middle of those seasons, Buffalo finishes with about **{buf_med:.0f} points** (eight times in ten, between {buf_lo:.0f} and {buf_hi:.0f}), and the last playoff spot in
the East goes to a team with about **{cut_med:.0f}** ({cut_lo:.0f} to {cut_hi:.0f}). To get there, Buffalo needs about {need:.0f} points from its last {n_left} games,
{need_pg:.2f} a game. So far it's earned {b.pts / gp:.2f} a game. Last season's {int(lw.w)}-win team earned {lw.pts / lw.gp:.2f}.

| Eastern team | Points now | Projected finish | Playoff chance |
|---|---|---|---|
{east_rows}

Buffalo's {p_buf:.0%} ranks {ordn(buf_rank_p)} of 16 in the East. The top three in each division and the next two in the conference get in.

**We've put this on the [Ledger](../ledger.html):** "{call.claim_text}," {float(call.probability):.0%}, logged {pd.Timestamp(call.created_at_utc):%b. %-d at %-I:%M %p} UTC, before
the Sabres' next game. It's graded after the last regular-season game in April, hit or miss.

## How we got the {p_buf:.0%}, and how we checked it

**The source:** the NHL's own play-by-play for every game so far and its schedule for every game left. **The reasoning:** a team's results come
from the chances it creates and allows. Our game model rates every team on those chances (blended with last season while the sample is small),
turns two teams' ratings into expected goals for each game, and plays the game out, overtime included. **The math:** we play out the full schedule
{N_SIMS:,} times, add up the points, apply the playoff format, and count how often Buffalo gets in.

**How we checked it:** we ran the same thing from this point of the season (about 20 games in) in 2023-24, 2024-25 and 2025-26 and compared it
with who actually made it. On our scorecard, where 0 is perfect and a coin flip scores 0.25, it scored {brier:.2f}. Going by who's in a playoff spot
after 20 games scored {brier_spot:.2f}. One honest caution: of the {lo_n} teams we gave between 5% and 30%, the model said {lo_said:.0%} on average and
{lo_made} made it. **One of them was last year's Sabres**: at this point we'd have given them {buf_last.p:.0%}, and they finished with {int(lw.pts)} points.

## Their record is about what they've earned

Replay each of Buffalo's games from its shots, with every shot going in or missing at its own chance, and the Sabres' chances were worth about
**{e_pts:.1f} points**. They have {int(b.pts)}. This isn't a good team having bad luck in the standings. It's a middle-of-the-pack team playing like one.

## What's going wrong

| Per game, 2026-27 | Sabres | League average |
|---|---|---|
| Chances created (goals they were worth) | {B.xgf:.2f} ({ordn(hi('xgf'))} of 32) | {L.xgf:.2f} |
| Chances allowed | {B.xga:.2f} ({ordn(hi('xga'))}-most) | {L.xga:.2f} |
| At full strength (five-on-five), share of the chances | {B.ev:.1%} ({ordn(hi('ev'))}) | 50% |
| Chances allowed while shorthanded | {B.sh_xga:.2f} ({ordn(hi('sh_xga'))}-most) | {L.sh_xga:.2f} |
| Goals allowed while shorthanded | {B.sh_ga:.2f} ({ordn(hi('sh_ga'))}-most) | {L.sh_ga:.2f} |
| Goals scored vs. what their chances were worth | {B.fin:+.2f} ({ordn(loo('fin'))}-worst) | {L.fin:+.2f} |
| Goaltending: goals saved vs. an average goalie | {B.gk:+.2f} ({ordn(loo('gk'))}-worst) | {L.gk:+.2f} |

Three problems stand out:

1. **They give up too much when they're shorthanded.** At full strength, Buffalo is about even ({B.ev:.0%} of the chances). The extra chances against come
   while a man down: the {ordn(hi('sh_xga'))}-most in the league, and {n_sh_ga} goals allowed. (That count mixes how often they're shorthanded with how well they kill
   penalties; we can't yet split the two.)
2. **They aren't finishing.** Buffalo has scored about {abs(team_fin):.0f} fewer goals than its chances were worth, {ordn(loo('fin'))}-worst in the league.
3. **Goaltending has been a little below average**, about {abs(B.gk):.2f} of a goal a game.

## Which problems will last

![What carries over](sabres-playoffs-carry.png)

We checked every team's first 20 games against the rest of its season over the last three years. How many chances a team creates and allows
carries over strongly ({carry['xgf']:.2f} and {carry['xga']:.2f} on a scale where 1 means the first 20 games tell you everything). Chances allowed while
shorthanded carry over about halfway ({carry['sh']:.2f}). Finishing ({carry['fin']:.2f}) and goaltending ({carry['gk']:.2f}) barely carry over at all: a team that
can't buy a goal or a save over 20 games is about as likely as anyone to be fine the rest of the way.

That's why our projection already expects Buffalo's shooting and goaltending to be about average from here. **The part that won't fix itself is the
chances they give up.**

## Who's underperforming

Each Sabre's points pace this season against his rating, our best guess at his points per 82 games from here, built from this season and the last
three. Ten or more games played.

| Player | Pos. | Games | G-A-P | Points pace (per 82) | Rating (per 82) |
|---|---|---|---|---|---|
{slow_rows}

These are the players furthest below their track records. Most of them should drift back up, but it's {int(slow.gp.min())} to {int(slow.gp.max())} games, so read it as
a guess, not a verdict. The flip side: {', '.join(fast.name.iloc[:-1])} and {fast.name.iloc[-1]} are running furthest ahead of theirs.

The biggest single finishing gap belongs to **{fin_low['name']}**: {fin_low.g} goals on chances worth {fin_low.ixg:.1f}. That's about {abs(fin_low.fin):.0f} of the
team's {abs(team_fin):.0f} missing goals. He's still producing ({fin_low.a} assists), and finishing streaks like that rarely last.

In goal:

| Goalie | Shots faced | Save percentage | Goals saved vs. average |
|---|---|---|---|
{g_rows}

## What would change it

We reran the season with one thing fixed at a time, holding everything else as it is now:

![What-ifs](sabres-playoffs-whatif.png)

| If Buffalo... | Playoff chance | Projected points |
|---|---|---|
{wi_rows}

- **Give up less while shorthanded** (fewer penalties, a better penalty kill, or both). Cutting the chances allowed a man down to league average is worth
  about {sh_fix:.2f} goals a game and moves Buffalo to {wi[1][1]:.0%}. It's the most specific fix on the list, and about half of a problem like this tends to
  last if nothing changes.
- **Allow league-average chances overall** and the Sabres are at {wi[2][1]:.0%}.
- **Do that and create a little more** (0.2 goals' worth of chances a game) and it's {wi[4][1]:.0%}: about a coin flip.
- **Wait for the shooting and the saves to come around.** Our projection already counts on that. It's built into the {p_buf:.0%}.

## The bottom line

The Sabres aren't done. They've earned about a point a game and played like it, in a conference where about {cut_med:.0f} points gets you in. The goals
should come, and the saves should be about average. What won't change on its own is how many chances they allow, especially a man down. That's
where the season gets decided.

## For the stat-heads

- Playoff simulation (`src/metrics/nhl_playoffs.py`): nhl-game-v0.1 team ratings from games before {NEXT} (xGF/xGA per game shrunk with K=10 toward
  league + 0.5 x last season's edge), frozen for the rest of the season; independent Poisson goals per game; regulation ties to the home team at the
  training-season OT/SO rate ({p_ot:.3f}); {N_SIMS:,} seasons. Format: top 3 per division + 2 wild cards per conference (assumed unchanged for 2026-27).
  Ties: points, regulation wins, ROW, random. Divisions and conferences derived from the {n_season}-game schedule (4-game pairs, 3+ game pairs).
  BUF ratings: xGF {off[US]:.3f}, xGA {de[US]:.3f}, league {lg:.3f} (unrescaled).
- Backtest at the 20-game mark ({', '.join(str(cut_date(G[G.season == s_])) for s_ in PAST)}), {len(bt)} team-seasons, actual schedules: Brier {brier:.4f};
  in-a-playoff-spot baseline {brier_spot:.4f}; coin 0.25. Rating noise (sd) chosen on 2023-24 and 2024-25 (0 was best) and kept. Teams given 5-30%:
  mean p {lo_said:.3f}, made {lo_made} of {lo_n}. The model's coefficients were fit on 2023-24 and 2024-25, so those two backtest seasons aren't fully out of sample.
- Points the chances were worth: Poisson-binomial over regulation shots per game, regulation ties valued at 1 + P(OT/SO win). {e_pts:.2f} vs {int(b.pts)}.
- Carry-over: Pearson r, first {CUT_GP} games vs rest, per game, {n_carry} team-seasons 2023-24 to 2025-26: xGF {carry['xgf']:.2f}, xGA {carry['xga']:.2f},
  shorthanded xGA {carry['sh']:.2f}, finishing (G - xG) {carry['fin']:.2f}, GSAx {carry['gk']:.2f}.
- xG rescaled per season so league xG = league goals (2026-27 factor {cal.loc[SEASON]:.3f}). Shorthanded = opponent at 5v4, 5v3 or 4v3.
  BUF 5v5 xGA/game {B.ev_xga:.2f} (league {L.ev_xga:.2f}); PP xGF {B.pp_xgf:.2f}, PP GF {B.pp_gf:.2f} a game. Penalty counts not shown (attribution unverified).
- What-ifs adjust BUF's ratings for the rest of the season only: shorthanded fix = BUF shorthanded xGA/game minus league ({sh_fix:.3f}) off xGA;
  average defense = league minus BUF xGA rating ({lg - de[US]:+.3f}); +0.2 xGF. Same seed in every run.
- Player ratings: skater cards (`src/reports/skater_cards.py`) as of {AS_OF}; pace = points / games x 82. Rating = projected points per 82 from this
  season and the last three. Finishing = goals minus individual xG. Team finishing {team_fin:+.1f} goals.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Sabres' chance to make the playoffs",
        "big": [[f"{p_buf:.0%}", "Now"], [f"{wi[2][1]:.0%}", "If they allowed league-average chances"]],
        "note": f"{int(b.w)}-{int(b.l)}-{int(b.otl)} after {gp} games. It usually takes about {cut_med:.0f} points to get the last spot in the East.",
        "explainer": {
            "kicker": "What lasts", "title": "Chances carry over. Finishing and goaltending streaks don't.",
            "text": "How much a team's first 20 games tell you about the rest of its season (1 = everything):",
            "fmt": "score",
            "bars": [["Chances allowed", round(carry["xga"], 2)], ["Goaltending", round(carry["gk"], 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
