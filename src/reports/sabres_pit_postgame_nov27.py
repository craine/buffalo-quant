"""Penguins 6, Sabres 3 (Nov. 27, 2026): Buffalo had the better chances; Pittsburgh's finishing came back all at once.

Chances = expected goals from our shot model (src/metrics/nhl_xg.py), unblocked non-empty-net shots, rescaled per season so league chances
equal league goals (each season through AS_OF). Writes reports/2026-11-27-sabres-pit-postgame.md, one PNG and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.metrics.nhl_team import shots
from src.reports.defense_baseline import BLUE, INK, MUTED, RED
from src.reports.pins import drop_late
from src.reports.sabres_postgame import finish, ordn

OUT = ROOT / "reports"
SLUG = "2026-11-27-sabres-pit-postgame"
PNG = "sabres-pit-nov27-postgame.png"
AS_OF = "2026-11-27"
GAME = 2026020413
SEASON = 20262027
PRED = "P0026"
LIZOTTE = 8481481


def clock(t):
    p, r = divmod(int(t), 1200)
    return p + 1, f"{r // 60}:{r % 60:02d}"


def main(as_of=AS_OF):
    keep = drop_late(query(f"SELECT g.game_id, g.season, g.game_date, g.home, g.away, g.home_score, g.away_score, g.last_period_type "
                           f"FROM raw_nhl_games g JOIN raw_nhl_schedule c ON c.game_id = g.game_id "
                           f"WHERE c.game_type = 2 AND g.game_date <= '{as_of}'"), as_of)
    s = shots()
    s = s[s.game_id.isin(set(keep.game_id))].merge(keep[["game_id", "game_date"]], on="game_id")
    u = s[(s.unblocked == 1) & (s.empty_net_against == 0)].copy()
    cal = u.groupby("season").goal.sum() / u.groupby("season").xg.sum()
    u["xg"] = u.xg * u.season.map(cal)
    names = query("SELECT DISTINCT player_id, first || ' ' || last AS name FROM raw_nhl_rosters WHERE season = 20262027").drop_duplicates("player_id").set_index("player_id").name

    # ---- the game
    g = keep[keep.game_id == GAME].iloc[0]
    assert (g.home, g.away, int(g.home_score), int(g.away_score), g.last_period_type) == ("BUF", "PIT", 3, 6, "REG")
    gu = u[u.game_id == GAME]
    x_b, x_p = float(gu[gu.team == "BUF"].xg.sum()), float(gu[gu.team == "PIT"].xg.sum())
    n_b, n_p = int((gu.team == "BUF").sum()), int((gu.team == "PIT").sum())
    share_g = x_b / (x_b + x_p)
    en = s[(s.game_id == GAME) & (s.goal == 1) & (s.empty_net_against == 1)]
    assert len(en) == 1 and en.team.iloc[0] == "PIT"
    en_name = names[int(en.shooter_id.iloc[0])]
    goals = gu[gu.goal == 1].sort_values(["period", "t"])
    goals = goals.assign(name=goals.shooter_id.map(names))
    pg = goals[goals.team == "PIT"]
    assert len(pg) == 5 and (goals.team == "BUF").sum() == 3
    # Buffalo's goalies: who faced which Pittsburgh shots
    fac = gu[gu.team == "PIT"].groupby("goalie_id").agg(first=("t", "min"), last=("t", "max"), n=("goal", "size"), ga=("goal", "sum"), x=("xg", "sum"))
    fac = fac.sort_values("first")
    g1, g2 = fac.iloc[0], fac.iloc[1]
    g1n, g2n = names[int(fac.index[0])], names[int(fac.index[1])]
    pull_p, pull_c = clock(g1["last"])
    assert (g1n, int(g1.n), int(g1.ga), g2n, int(g2.n), int(g2.ga)) == ("Ukko-Pekka Luukkonen", 12, 4, "Alex Lyon", 20, 1)
    pit_g = names[int(gu[gu.team == "BUF"].goalie_id.mode().iloc[0])]
    liz = pg[pg.shooter_id == LIZOTTE]
    assert len(liz) == 1 and pit_g == "Sergei Murashov" and int(g1["last"]) == int(liz.t.iloc[0])
    liz_before = int((u[(u.shooter_id == LIZOTTE) & (u.season == SEASON) & (u.game_date < as_of)]).shape[0])
    assert liz_before == 41
    far = pg.sort_values("dist").iloc[-1]
    close_b = goals[goals.team == "BUF"].sort_values("dist").iloc[0]
    assert close_b.shooter_id == goals[goals.team == "BUF"].shooter_id.iloc[-1]

    # ---- how rare: every team-game since 2023-24
    tg = u.groupby(["game_id", "season", "team"]).agg(gl=("goal", "sum"), x=("xg", "sum")).reset_index()
    me = tg[(tg.game_id == GAME) & (tg.team == "PIT")].iloc[0]
    rare = tg[(tg.gl >= me.gl) & (tg.x <= me.x)]
    rare_pit = int((rare.team == "PIT").sum())
    assert (len(rare), len(tg), rare_pit, int(me.gl)) == (21, 8700, 5, 5)
    every = int(round(len(tg) / len(rare), -2))
    assert every == 400
    near = tg[(tg.x - me.x).abs() <= 0.25]
    avg_near = float(near.gl.mean())

    # ---- the season, after the game (2026-27 only)
    k26 = keep[keep.season == SEASON]
    c = u[u.season == SEASON]
    t = pd.DataFrame({"xgf": c.groupby("team").xg.sum(), "gf": c.groupby("team").goal.sum(), "xga": c.groupby("opp").xg.sum(), "ga": c.groupby("opp").goal.sum()})
    t["gp"] = pd.concat([k26.home, k26.away]).value_counts()
    t["share"] = t.xgf / (t.xgf + t.xga)
    t["fin"] = (t.gf - t.xgf) / t.gp
    t["sv"] = (t.xga - t.ga) / t.gp
    rk = {k: t[k].rank(ascending=False, method="min").astype(int) for k in ("share", "fin", "sv")}
    B, P = t.loc["BUF"], t.loc["PIT"]
    bg = k26[(k26.home == "BUF") | (k26.away == "BUF")].copy()
    bg["gf"] = np.where(bg.home == "BUF", bg.home_score, bg.away_score)
    bg["ga"] = np.where(bg.home == "BUF", bg.away_score, bg.home_score)
    otl = (bg.gf < bg.ga) & bg.last_period_type.isin(["OT", "SO"])
    W, L, OTL = int((bg.gf > bg.ga).sum()), int(((bg.gf < bg.ga) & ~otl).sum()), int(otl.sum())
    assert (W, L, OTL) == (11, 11, 4)
    assert (rk["share"]["BUF"], rk["fin"]["PIT"]) == (21, 25)

    # ---- the Ledger
    p = pd.read_csv(ROOT / "ledger" / "predictions.csv")
    gr = pd.read_csv(ROOT / "ledger" / "grades.csv")
    pr = p[p.id == PRED].iloc[0]
    mg = gr[gr.prediction_id == PRED].iloc[0]
    m = p.merge(gr, left_on="id", right_on="prediction_id")
    m = m[m.id <= PRED]
    right = int((((m.probability > 0.5) & (m.outcome == 1)) | ((m.probability < 0.5) & (m.outcome == 0))).sum())
    assert (float(pr.probability), int(mg.outcome), round(float(mg.brier), 4), right, len(m)) == (0.51, 0, 0.2601, 15, 25)

    # ---- chart: every team-game since 2023-24, chances vs. goals
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=200)
    ax.scatter(tg.x, tg.gl + rng.uniform(-0.28, 0.28, len(tg)), s=4, color="#B8BEC8", alpha=0.35, lw=0, zorder=1)
    xs = np.arange(0.25, 6.01, 0.25)
    bins = [(a, tg[(tg.x >= a - 0.25) & (tg.x < a + 0.25)].gl) for a in xs]
    bins = [(a, v.mean()) for a, v in bins if len(v) >= 50]
    ax.plot([a for a, _ in bins], [v for _, v in bins], color=INK, lw=1.6, zorder=2, label="Average goals for chances of that size (50+ games)")
    ax.scatter([me.x], [me.gl], s=110, color=RED, edgecolor="white", lw=1.5, zorder=4)
    ax.annotate(f"Penguins on Friday: {int(me.gl)} goals on\nchances worth {me.x:.1f}", (me.x, me.gl), xytext=(me.x + 0.55, me.gl + 1.3),
                fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    mb = tg[(tg.game_id == GAME) & (tg.team == "BUF")].iloc[0]
    ax.scatter([mb.x], [mb.gl], s=110, color=BLUE, edgecolor="white", lw=1.5, zorder=4)
    ax.annotate(f"Sabres: {int(mb.gl)} goals on\nchances worth {mb.x:.1f}", (mb.x, mb.gl), xytext=(mb.x + 0.7, mb.gl - 1.6),
                fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_xlim(0, 6)
    ax.set_ylim(-0.6, 9.6)
    ax.set_xlabel("What a team's chances were worth in one game (goals)")
    ax.set_ylabel("Goals scored (not counting empty nets)")
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    ax.grid(color="#EEF0F3")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.13, top=0.80)
    finish(fig, f"{int(me.gl)}+ goals on chances as thin as Pittsburgh's: {len(rare)} times in {len(tg):,} NHL team-games",
           "Every NHL team's game since 2023-24. Each gray dot is one team in one game.", "x")
    fig.texts[-1].set_text(f"Source: NHL play-by-play; Buffalo Quant Desk chance model. Regular season through {as_of}. {len(tg):,} team-games.")
    fig.savefig(OUT / PNG)
    plt.close(fig)

    plist = "; ".join(f"{r.name} from {r.dist:.0f} feet ({r.xg:.0%})" for r in pg.itertuples())
    bl = [r.name for r in goals[goals.team == "BUF"].itertuples()]
    md = f"""# Penguins 6, Sabres 3: Buffalo had the chances, Pittsburgh had the finish

**Buffalo had the better chances on Friday, worth about {x_b:.1f} goals to Pittsburgh's {x_p:.1f}. The Penguins scored {int(me.gl)} anyway, plus an empty-netter.
Since 2023-24, a team has scored {int(me.gl)} or more on chances worth no more than Pittsburgh's only {len(rare)} times in {len(tg):,} team-games, about once every
{every}. Our preview said Pittsburgh's poor finishing probably wouldn't last over the season. One game doesn't prove that, but Friday was a big swing. Our call, Sabres {pr.probability:.0%}, was a miss.**

![{int(me.gl)}+ goals on chances as thin as Pittsburgh's: {len(rare)} times in {len(tg):,} NHL team-games]({PNG})

## The game

Buffalo had {n_b} shots that weren't blocked to Pittsburgh's {n_p}, and {share_g:.0%} of the chances. Buffalo's goals came from {", ".join(bl[:-1])} and {bl[-1]}, whose goal came from {close_b.dist:.0f} feet, a chance worth about {close_b.xg:.0%}.

Pittsburgh's five: {plist}. The percentages are each shot's chance of going in. {en_name} added an empty-netter late.

**In goal:** {g1n} allowed {int(g1.ga)} goals on {int(g1.n)} unblocked shots worth about {g1.x:.1f} and was replaced after Lizotte's goal, {pull_c} into the {ordn(pull_p)} period.
{g2n} allowed {int(g2.ga)} on {int(g2.n)} unblocked shots worth about {g2.x:.1f}. {pit_g} was in net for Pittsburgh and allowed {int(g.home_score)} on chances worth {x_b:.1f}, about what an average goalie would.

## How rare that is

Every shot that isn't blocked gets a value: the share of similar shots that go in, based on distance, angle, shot type and whether it's a rebound or rush.
Add them up and you get what a team's chances were worth. Teams with chances worth about {me.x:.1f} (within a quarter-goal) have scored {avg_near:.1f} goals on average.
Pittsburgh scored {int(me.gl)}. The chart shows every team-game since 2023-24; only {len(rare)} had {int(me.gl)} or more goals on chances worth no more than Pittsburgh's, and {rare_pit} of them, counting Friday, are Pittsburgh's.

**How we checked it.** The shot values are scaled each season so that, across the league, chances add up to goals. And the 41-shot example in our preview,
Blake Lizotte with no goals on chances worth about 3, scored on Friday from {liz.dist.iloc[0]:.0f} feet, a chance worth about {liz.xg.iloc[0]:.0%}. That's what finishing luck looks like
when it turns.

## What it means

One game doesn't change much. Buffalo gets {B.share:.0%} of the chances in its games, {ordn(rk['share']['BUF'])} in the NHL, and that's the number that carries forward.
Pittsburgh is {ordn(rk['fin']['PIT'])} in finishing after Friday; one big night only moves a season so far. The Sabres are {W}-{L}-{OTL}.

## Receipts

- **Our preview** said Pittsburgh's finishing and goaltending would probably come back toward average, and that it wouldn't necessarily show up in one game.
  One game is mostly luck either way, so Friday doesn't settle a season-long call. Murashov had an average night. We'll keep tracking both over the season.
- **The Ledger** gave the Sabres {pr.probability:.0%}. They lost, so it's a miss. On our scorecard, where 0 is perfect and a coin flip scores 0.25, it scored {mg.brier:.2f}.
  Our record is {right} of {len(m)}.

## For the stat-heads

- xG model: unblocked non-empty-net shots, rescaled per season so league xG equals league goals through {as_of} (2026-27 factor {cal.loc[SEASON]:.3f}).
- Game, all situations: xGF {x_b:.2f}, xGA {x_p:.2f} (xGF% {share_g:.3f}). {g1n.split()[-1]} GSAx {g1.x - g1.ga:+.2f}, {g2n.split()[-1]} {g2.x - g2.ga:+.2f}.
- Rarity: team-games 2023-24 on with non-empty-net G >= {int(me.gl)} and xG <= {me.x:.3f}: {len(rare)} of {len(tg):,} (PIT {rare_pit}). Mean G for xG within 0.25: {avg_near:.2f} (n {len(near)}).
- Season: BUF xGF% {B.share:.3f} ({ordn(rk['share']['BUF'])}); PIT finishing {P.fin:+.2f} per game ({ordn(rk['fin']['PIT'])}), GSAx {P.sv:+.2f} per game ({ordn(rk['sv']['PIT'])}).
- Ledger {PRED}: p = {pr.probability:.2f}, outcome {int(mg.outcome)}, Brier {mg.brier:.4f}. "Right" = the side above 50% won.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Penguins 6, Sabres 3",
        "big": [[int(me.gl), f"Pittsburgh goals on chances worth {me.x:.1f}, not counting the empty-netter"],
                [f"1 in {every}", "how often a team scores 5+ on chances that thin, since 2023-24"]],
        "note": f"Buffalo had {share_g:.0%} of the chances. Our 51% Sabres call was a miss.",
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
