"""Week 9 matchup story A: Carson Wentz and the Vikings offense vs. the Bills defense (MNF, Nov. 9, 2026).

Writes reports/2026-wk09-wentz-vs-bills-defense.md, two PNGs and a homepage hero JSON. Every number is computed here.
Pinned: 2025 full regular season and 2026 through week 8 (AS_OF), so reruns reproduce the published story.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.ledger.model_v01 import SHRINK, VERSION, prob_over, qb_relative
from src.metrics.team import season_table
from src.reports.bills_vikings_preview import ordn, finish
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED

OUT = ROOT / "reports"
SEASON, THRU = 2026, 8  # AS_OF: 2026 regular season through week 8
WENTZ, MURRAY = "00-0032950", "00-0035228"
MIN_DB = 150
GAME = "2026_09_BUF_MIN"
EP_SEASONS = (2018, 2026)
WHERE = (f"p.season_type='REG' AND p.qb_dropback=1 AND p.epa IS NOT NULL AND COALESCE(p.two_point_attempt,0)=0 "
         f"AND (p.season=2025 OR (p.season={SEASON} AND p.week<={THRU}))")


def dropbacks():
    p = query(f"""SELECT p.season, p.week, p.game_id, p.play_id, p.posteam, p.defteam,
                  COALESCE(p.passer_player_id, p.rusher_player_id) AS pid, p.epa, p.sack, p.pass_attempt, p.complete_pass,
                  p.air_yards, p.cpoe, p.interception, p.fumble_lost, p.yards_gained, p.wp,
                  f.n_blitzers, f.is_interception_worthy
                  FROM raw_pbp p LEFT JOIN raw_ftn f ON f.nflverse_game_id = p.game_id AND f.nflverse_play_id = p.play_id
                  WHERE {WHERE}""")
    p["att"] = (p.pass_attempt == 1) & (p.sack == 0)
    p["deep"] = p.att & (p.air_yards >= 20)
    p["short"] = p.att & (p.air_yards < 20)
    p["to"] = (p.interception.fillna(0) + p.fumble_lost.fillna(0)) > 0
    p["blitz"] = p.n_blitzers > 0
    p["expl"] = (p.yards_gained >= 20) & (p.sack == 0)
    p["close"] = (p.wp >= 0.10) & (p.wp <= 0.90)
    return p


def qb_line(x):
    a = x[x.att]
    c = x[x.close]
    return pd.Series(dict(db=len(x), g=x.game_id.nunique(), epa=x.epa.mean(), epa_close=c.epa.mean(), n_close=len(c),
                          sk=x.sack.mean(), deep_share=a.deep.mean(), n_att=len(a), n_deep=int(x.deep.sum()),
                          short_epa=x[x.short].epa.mean(), cpoe=a.cpoe.mean(), to=x.to.mean(),
                          intw=a.is_interception_worthy.mean(), n_intw=int(a.is_interception_worthy.sum()),
                          blitz_faced=x.blitz.mean(), epa_blitz=x[x.blitz == True].epa.mean(), n_blitz=int((x.blitz == True).sum())))


def def_line(x):
    a = x[x.att]
    c = x[x.close]
    return pd.Series(dict(db=len(x), short_epa=x[x.short].epa.mean(), short_epa_close=c[c.short].epa.mean(),
                          n_short=int(x.short.sum()), deep_epa=x[x.deep].epa.mean(), deep_epa_close=c[c.deep].epa.mean(),
                          n_deep=int(x.deep.sum()), deep_share=a.deep.mean(), short_ypa=x[x.short].yards_gained.mean(),
                          blitz=x.blitz.mean(), n_blitz=int((x.blitz == True).sum()), sk_blitz=x[x.blitz == True].sack.mean(),
                          sk_noblitz=x[x.blitz == False].sack.mean(), expl=x.expl.mean(), to=x.to.mean()))


def rank(s, team, low_is_good):
    return int(s.rank(ascending=low_is_good, method="min").loc[team])


def ep_examples():
    a, b = EP_SEASONS
    w = (f"season BETWEEN {a} AND {b} AND NOT (season = {SEASON} AND week > {THRU}) AND season_type='REG' "
         "AND (pass=1 OR rush=1) AND epa IS NOT NULL")
    ep = query(f"SELECT yardline_100 y, AVG(ep) ep, COUNT(*) n FROM raw_pbp WHERE {w} AND down=1 AND ydstogo=10 GROUP BY 1").set_index("y")
    third = query(f"""SELECT CASE WHEN sack=1 THEN 'sack' WHEN third_down_converted=1 THEN 'conv' ELSE 'fail' END o,
                      COUNT(*) n, AVG(epa) epa FROM raw_pbp WHERE {w} AND down=3 AND ydstogo=8 AND qb_dropback=1 GROUP BY 1""").set_index("o")
    return ep, third


def main():
    p = dropbacks()
    q = p.groupby(["season", "pid"]).apply(qb_line)
    lgq = {se: qb_line(p[p.season == se]) for se in (2025, SEASON)}
    pool = {se: q.loc[se][q.loc[se].db >= MIN_DB] for se in (2025, SEASON)}
    n_pool = {se: len(pool[se]) for se in pool}
    w25, w26, m26 = q.loc[(2025, WENTZ)], q.loc[(SEASON, WENTZ)], q.loc[(SEASON, MURRAY)]
    r25 = lambda col, low: rank(pool[2025][col], WENTZ, low)
    w_rk = dict(epa=r25("epa", False), epa_close=r25("epa_close", False), sk=r25("sk", True), intw=r25("intw", True),
                to=r25("to", True), short_epa=r25("short_epa", False), deep_share=r25("deep_share", False))
    sk_most = n_pool[2025] - w_rk["sk"] + 1        # 1 = sacked most often
    intw_most = n_pool[2025] - w_rk["intw"] + 1    # 1 = most interception-worthy throws
    m_rk = rank(pool[SEASON]["epa"], MURRAY, False)
    m_rk_close = rank(pool[SEASON]["epa_close"], MURRAY, False)

    d = p[p.season == SEASON]
    D = d.groupby("defteam").apply(def_line)
    lgd = def_line(d)
    bd = D.loc["BUF"]
    b_rk = dict(short=rank(D.short_epa, "BUF", True), short_close=rank(D.short_epa_close, "BUF", True),
                deep=rank(D.deep_epa, "BUF", True), deep_close=rank(D.deep_epa_close, "BUF", True),
                short_ypa=rank(D.short_ypa, "BUF", True), deep_share=rank(D.deep_share, "BUF", True),
                blitz=rank(D.blitz, "BUF", False), expl=rank(D.expl, "BUF", True), to=rank(D.to, "BUF", False))

    off = season_table("off", [SEASON], max_week=THRU).set_index("team")
    de = season_table("def", [SEASON], max_week=THRU).set_index("team")
    mo, bdt = off.loc["MIN"], de.loc["BUF"]
    t3 = query(f"""SELECT defteam, SUM(third_down_converted) c, SUM(third_down_converted) + SUM(third_down_failed) n FROM raw_pbp
                   WHERE season={SEASON} AND week<={THRU} AND season_type='REG' AND down=3 AND (pass=1 OR rush=1)
                   GROUP BY 1""").set_index("defteam")
    t3["r"] = t3.c / t3.n
    t3_rk = rank(t3.r, "BUF", True)
    ep, third = ep_examples()

    # Ledger calls (same model and inputs as the week 9 card), pinned to week 8
    w_db, n_db = qb_relative(WENTZ, "dropback_epa", [2025, SEASON], max_week=THRU)
    w_sk, n_sk = qb_relative(WENTZ, "sack_rate", [2025, SEASON], max_week=THRU)
    c1 = prob_over("MIN", "BUF", "dropback_epa", 0.0, off_override=w_db, max_week=THRU)
    c2 = prob_over("MIN", "BUF", "rush_epa", 0.0, max_week=THRU)
    c3 = prob_over("MIN", "BUF", "sack_rate", 0.06, off_override=w_sk, max_week=THRU)
    from src.ledger.ledger import PRED_COLS, PRED_CSV, _read
    lp = _read(PRED_CSV, PRED_COLS)
    lp = lp[lp.game_id == GAME] if not lp.empty else lp
    if len(lp):
        ledger_status = (f"**Logged on the [Ledger](../ledger.html) at {lp.created_at_utc.min()} UTC, before kickoff.** "
                         "These are graded after the game, hit or miss, and stay up either way.")
    else:
        ledger_status = ("**Our model's numbers for this game.** A call only counts once it's logged on the "
                         "[Ledger](../ledger.html) before kickoff, and every logged call is graded after the game.")

    pts = lambda v: "0.00" if abs(v) < 0.005 else f"{v:+.2f}"
    close25 = p[(p.season == 2025) & p.close & p.short]
    sc = close25.groupby("pid").epa.mean()
    sc = sc[sc.index.isin(pool[2025].index)]
    w_short_close_rk = rank(sc, WENTZ, False)
    n_short_close_pool = len(sc)
    n_deep_close = int(d[(d.defteam == "BUF") & d.close & d.deep].shape[0])
    # ---- chart 1: Bills pass defense, short vs deep, all plays and close games
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), dpi=200, sharey=True)
    panels = [("All plays", "short_epa", "deep_epa", b_rk["short"], b_rk["deep"]),
              ("Close games only (win chance 10-90%)", "short_epa_close", "deep_epa_close", b_rk["short_close"], b_rk["deep_close"])]
    for ax, (title, s_col, dc, rs, rd) in zip(axes, panels):
        x = np.arange(2); w = 0.36
        buf = [bd[s_col], bd[dc]]; lg = [lgd[s_col], lgd[dc]]
        ax.bar(x - w / 2, buf, w, color=BLUE, label="Bills defense", zorder=2)
        ax.bar(x + w / 2, lg, w, color=GRAY, label="League average", zorder=2)
        for i, (v, r_) in enumerate(zip(buf, (rs, rd))):
            ax.text(i - w / 2, max(v, 0) + 0.01, f"{pts(v)}\n{ordn(r_)} of 32", ha="center", va="bottom", fontsize=9, color=INK)
        for i, v in enumerate(lg):
            ax.text(i + w / 2, v + 0.01, f"{pts(v)}", ha="center", va="bottom", fontsize=9, color=MUTED)
        ax.set_xticks(x, ["Short throws\n(under 20 yards in the air)", "Deep throws\n(20+ yards)"], fontsize=9.5)
        ax.axhline(0, color=INK, lw=1); ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK)
        ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    axes[0].set_ylabel("Points added per throw (lower = better defense)")
    axes[0].legend(frameon=False, fontsize=9, loc="upper left")
    hi = max(D[["short_epa", "deep_epa", "short_epa_close", "deep_epa_close"]].loc["BUF"].max(), lgd.deep_epa, lgd.deep_epa_close)
    axes[0].set_ylim(min(0, bd.deep_epa_close) - 0.08, hi + 0.18)
    finish(fig, "The Bills bend most on short throws",
           f"Points added per pass attempt against the Bills vs. the league average, 2026 through week {THRU}. 1st = best defense.",
           f"Bills: {int(bd.n_short)} short and {int(bd.n_deep)} deep attempts faced. Both deep samples are small ({int(bd.n_deep)} all plays, {n_deep_close} in close games).")
    fig.savefig(OUT / "wk09a-bills-short-deep.png"); plt.close(fig)

    # ---- chart 2: Wentz's risk profile, 2025
    items = [("Sacked, share of dropbacks", w25.sk, lgq[2025].sk, f"{ordn(sk_most)}-highest rate of {n_pool[2025]}"),
             ("Throws that should have been intercepted", w25.intw, lgq[2025].intw, f"{ordn(intw_most)}-highest rate of {n_pool[2025]}"),
             ("Turnovers, share of dropbacks", w25.to, lgq[2025].to, f"{ordn(w_rk['to'])} of {n_pool[2025]}, 1st = fewest")]
    fig, ax = plt.subplots(figsize=(9.5, 4.9), dpi=200)
    ys = np.arange(len(items))[::-1]
    for y, (lab, v, lg, note) in zip(ys, items):
        ax.barh(y + 0.18, v, 0.34, color=RED, zorder=2)
        ax.barh(y - 0.18, lg, 0.34, color=GRAY, zorder=2)
        ax.text(v + 0.002, y + 0.18, f"Wentz {v:.1%}  ({note})", va="center", fontsize=9, color=INK)
        ax.text(lg + 0.002, y - 0.18, f"League {lg:.1%}", va="center", fontsize=9, color=MUTED)
    ax.set_yticks(ys, [i[0] for i in items], fontsize=10)
    ax.set_xlim(0, max(max(i[1], i[2]) for i in items) * 1.9)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.02))
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="x", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "Wentz's 2025: lots of sacks and risky throws, average turnovers",
           f"Carson Wentz, 2025 regular season, vs. the league. Ranks among {n_pool[2025]} QBs with {MIN_DB}+ dropbacks.",
           f"Wentz: {int(w25.db)} dropbacks, {int(w25.n_att)} pass attempts. Risky throws charted by FTN Data.")
    fig.savefig(OUT / "wk09a-wentz-risk.png"); plt.close(fig)

    md = f"""# Carson Wentz vs. the Bills defense: short passes, sacks and risky throws

**Finding: Compared with the rest of the league, the Bills' defense is weakest on short passes, the ones thrown less than 20 yards downfield. They rank
{ordn(b_rk['short'])} of 32 there, and {ordn(b_rk['short_close'])} with garbage time removed. That's where most of Minnesota's passing will go: like most quarterbacks, Carson Wentz threw short
on {1 - w25.deep_share:.0%} of his attempts last season. But Wentz brings two weak spots of his own. He was sacked on {w25.sk:.1%} of his dropbacks, the
{ordn(sk_most)}-highest rate among {n_pool[2025]} quarterbacks, and his share of throws that should have been intercepted was the {ordn(intw_most)}-highest.**

*Bills at Vikings, Monday Night Football, Nov. 9, 8:15 p.m. ET, U.S. Bank Stadium (indoors). Kyler Murray is out with a
strained hamstring, so Wentz starts. Numbers are 2026 through week {THRU} unless noted, and Wentz's are mostly from 2025,
since he has dropped back only {int(w26.db)} times this year.*

![Bills short vs deep](wk09a-bills-short-deep.png)

## How we measure it: points per play

Every play changes how many points a drive is worth. 1st-and-10 at your own 25 is worth about **{ep.loc[75, 'ep']:.1f} points**
on average; at the opponent's 25, about **{ep.loc[25, 'ep']:.1f}**. On 3rd-and-8, a quarterback who converts adds about
**{third.loc['conv', 'epa']:+.1f} points**, and one who gets sacked costs his team about **{abs(third.loc['sack', 'epa']):.1f}**.

![Points per play](wk09-points-per-play.png)

**The source:** the NFL's official play-by-play, published free by the nflverse project, covering every snap. For
blitzes and risky throws we add charting from FTN Data, whose analysts watch every play and mark things the official
feed doesn't, like how many defenders rushed and whether a throw should have been picked off.

**The math:** take what the drive was worth after the play, subtract what it was worth before, and that's the play's
value. Average it over many plays and you get **points added per play**. A good defense keeps that number low.

**How we checked it:** we ran the efficiency numbers two ways, on all plays and on close-game plays only (when either team
had between a 10% and 90% chance to win), so a few blowout drives can't drive the story. Where the two disagree, we say so.

## Where the Bills bend: short throws

Against short throws, the Bills allow **{pts(bd.short_epa)} points per attempt** ({ordn(b_rk['short'])} of 32; league average {pts(lgd.short_epa)}). The
second check agrees: in close games it's {pts(bd.short_epa_close)} ({ordn(b_rk['short_close'])}), and they give up {bd.short_ypa:.1f} yards per short attempt
({ordn(b_rk['short_ypa'])}; league {lgd.short_ypa:.1f}).

Deep throws are a different story. Opponents have tried them on only {bd.deep_share:.1%} of attempts against Buffalo
({ordn(b_rk['deep_share'])}-fewest), and in close games the Bills have allowed {pts(bd.deep_epa_close)} points per deep throw, {ordn(b_rk['deep_close'])} in the league
(league average {pts(lgd.deep_epa_close)}; only {n_deep_close} attempts, a small sample). Counting blowouts they're {ordn(b_rk['deep'])}, but that's only {int(bd.n_deep)} deep attempts.

Overall the Bills rank {ordn(bdt.dropback_epa_rk)} against the pass ({pts(bdt.dropback_epa)} points per dropback; league {pts(bdt.dropback_epa_lg)}), give up 20-yard plays on {bd.expl:.1%} of dropbacks ({ordn(b_rk['expl'])}; league {lgd.expl:.1%}),
and allow third-down conversions {t3.loc['BUF', 'r']:.0%} of the time ({ordn(t3_rk)}; league {t3.c.sum() / t3.n.sum():.0%}).

## What Wentz brings

| | Wentz 2025 | Wentz 2026 | Murray 2026 | League 2026 |
|---|---|---|---|---|
| Dropbacks | {int(w25.db)} | {int(w26.db)} (small sample) | {int(m26.db)} | |
| Points added per dropback, all plays | {pts(w25.epa)} | {pts(w26.epa)} | {pts(m26.epa)} ({ordn(m_rk)} of {n_pool[SEASON]}) | {pts(lgq[SEASON].epa)} |
| Points added per dropback, close games | {pts(w25.epa_close)} | {pts(w26.epa_close)} | {pts(m26.epa_close)} ({ordn(m_rk_close)}) | {pts(lgq[SEASON].epa_close)} |
| Sacked | {w25.sk:.1%} | {w26.sk:.1%} | {m26.sk:.1%} | {lgq[SEASON].sk:.1%} |
| Share of throws 20+ yards downfield | {w25.deep_share:.1%} | {w26.deep_share:.1%} | {m26.deep_share:.1%} | {lgq[SEASON].deep_share:.1%} |
| Throws that should have been intercepted | {w25.intw:.1%} | {w26.intw:.1%} | {m26.intw:.1%} | {lgq[SEASON].intw:.1%} |

League averages for 2025: {pts(lgq[2025].epa)} per dropback, {pts(lgq[2025].epa_close)} in close games, sacked {lgq[2025].sk:.1%}, deep share {lgq[2025].deep_share:.1%},
should-have-been-intercepted {lgq[2025].intw:.1%}.

Two things stand out.

**Wentz looks better overall than in close games.** Counting every play, he was about league average last season
({pts(w25.epa)} per dropback; league {pts(lgq[2025].epa)}). With garbage time removed he drops to {pts(w25.epa_close)}, {ordn(w_rk['epa_close'])} of {n_pool[2025]}.
Some of his best numbers came when games were already decided ({int(w25.db - w25.n_close)} dropbacks outside close games, a small sample). Murray this year was {ordn(m_rk)} of {n_pool[SEASON]} overall and {ordn(m_rk_close)} in close
games. By these numbers, neither has been an above-average passer when the game is still in doubt.

**Risk.** Wentz was sacked on {w25.sk:.1%} of dropbacks ({ordn(sk_most)}-highest rate of {n_pool[2025]}) and threw {int(w25.n_intw)} passes that FTN's charters
marked as should-have-been-intercepted, {w25.intw:.1%} of his attempts ({ordn(intw_most)}-highest rate; league {lgq[2025].intw:.1%}). He got away with most of
them: his actual turnover rate was {w25.to:.1%}, about league average ({lgq[2025].to:.1%}).

![Wentz risk profile](wk09a-wentz-risk.png)

## Where it meets

- **Short passes are the matchup.** Most of Wentz's throws are short ({1 - w25.deep_share:.0%}, about the league norm) and the Bills are at
  their weakest there. His own short-throw numbers were good overall ({ordn(w_rk['short_epa'])} of {n_pool[2025]}) but {ordn(w_short_close_rk)} in close games.
  That's where we'd expect the Vikings to attack.
- **The Bills blitz a lot without getting home.** Buffalo sends extra rushers on {bd.blitz:.0%} of dropbacks ({ordn(b_rk['blitz'])}-most), but
  gets sacks on only {bd.sk_blitz:.1%} of those plays (league {lgd.sk_blitz:.1%}) and {bd.sk_noblitz:.1%} without a blitz (league {lgd.sk_noblitz:.1%}).
  Wentz's sack habit is the best chance for that to change. Against the blitz last season, his points per dropback ranked
  {ordn(rank(pool[2025]['epa_blitz'], WENTZ, False))} of {n_pool[2025]}, on only {int(w25.n_blitz)} plays.
- **The ground game shouldn't scare anyone.** Minnesota's designed runs rank {ordn(mo.rush_epa_rk)} ({pts(mo.rush_epa)} per run); the Bills' run defense
  ranks {ordn(bdt.rush_epa_rk)} ({pts(bdt.rush_epa)} allowed, right around the league average of {pts(mo.rush_epa_lg)}).
- **Turnovers.** Buffalo forces turnovers on {bd.to:.1%} of dropbacks ({ordn(b_rk['to'])}; league {lgd.to:.1%}). That's about average. If Wentz keeps
  putting the ball in harm's way, Monday is a chance for that number to go up.

## What we're watching

{ledger_status}

| # | What we expect | Chance |
|---|---|---|
| 1 | Minnesota's pass plays add points overall (more than zero points per dropback; the league average is {pts(mo.dropback_epa_lg)}) | **{c1['p']:.0%}** |
| 2 | Minnesota's designed runs lose points overall (less than zero per run; the league average is {pts(mo.rush_epa_lg)}) | **{1 - c2['p']:.0%}** |
| 3 | The Bills sack the quarterback on more than 6% of his dropbacks | **{c3['p']:.0%}** |

How we get these: start from each side's season average, pull it halfway back toward the league average (seven games is a
small sample), combine offense and defense, and look at how much a single game usually bounces around. For calls 1 and 3
we used Wentz's own passing and sack numbers in place of the Vikings' team numbers, which were mostly Murray's games.

## For the stat-heads

- Points added = EPA (nflverse expected points). Dropbacks: `qb_dropback == 1`, EPA not null, no two-point tries, QB by
  gsis id via `COALESCE(passer_player_id, rusher_player_id)` (scrambles included). Short/deep: pass attempts excluding
  sacks, `air_yards` < 20 vs >= 20. Close games: `wp` between 0.10 and 0.90. Regular season; 2026 through week {THRU}.
- QB ranks among quarterbacks with {MIN_DB}+ dropbacks ({n_pool[2025]} in 2025, {n_pool[SEASON]} in 2026). League values in the QB table are
  play-weighted over all dropbacks; the Ledger calls use the average of team-game values, which is why call 1 shows a
  slightly different league average than the QB table. Wentz 2025 close-game sample: {int(w25.n_close)} dropbacks; 2026: {int(w26.n_close)}. Wentz 2025 short throws, close games: {ordn(w_short_close_rk)} of {n_short_close_pool}.
- FTN charting (`raw_ftn`, joined on game and play id): blitz = `n_blitzers` > 0; should-have-been-intercepted =
  `is_interception_worthy` on pass attempts. Wentz 2025: {int(w25.n_intw)} of {int(w25.n_att)} attempts; {int(w25.n_blitz)} dropbacks vs. the blitz.
- Bills defense: {int(bd.db)} dropbacks faced, {int(bd.n_short)} short and {int(bd.n_deep)} deep attempts, {int(bd.n_blitz)} blitzes. Team ranks are among 32
  defenses (1st = best, except blitz rate where 1st = most). Team tables from `src/metrics/team.py` (`max_week={THRU}`).
- Calls: Ledger model {VERSION}, shrink {SHRINK}, pinned to week {THRU}. Wentz substitution {n_db} dropbacks (2025-26):
  EPA/dropback {w_db:+.4f}, sack rate {w_sk:+.4f} vs. league. Expected: call 1 {c1['expected']:+.3f}, call 2 {c2['expected']:+.3f}, call 3 {c3['expected']:.3f}.
- Injury news: Kevin O'Connell announced Nov. 5, 2026 that Wentz starts with Murray out (strained hamstring). Source: ESPN.
"""
    (OUT / "2026-wk09-wentz-vs-bills-defense.md").write_text(md)
    (OUT / "2026-wk09-wentz-vs-bills-defense.hero.json").write_text(json.dumps({
        "label": "Monday night: where the matchup is",
        "big": [[ordn(b_rk["short"]), "Bills defense vs. short throws (of 32)"],
                [f"{1 - w25.deep_share:.0%}", "Wentz throws that were short, 2025"]],
        "note": (f"With garbage time removed the Bills are still {ordn(b_rk['short_close'])}. Wentz was sacked on {w25.sk:.1%} of dropbacks last "
                 f"season, the {ordn(sk_most)}-highest rate among {n_pool[2025]} QBs."),
        "explainer": {
            "kicker": "How we know", "title": "Every play is worth points.",
            "text": (f"We judge every snap by how many points it adds to or takes away from the drive. On 3rd-and-8, a "
                     f"conversion adds about {third.loc['conv', 'epa']:+.1f} points; a sack costs about {abs(third.loc['sack', 'epa']):.1f}. "
                     f"Here's what 1st-and-10 is worth depending on where you start."),
            "fmt": "pts",
            "bars": [["Own 25", round(float(ep.loc[75, 'ep']), 2)], ["Midfield", round(float(ep.loc[50, 'ep']), 2)],
                     ["Opp. 25", round(float(ep.loc[25, 'ep']), 2)], ["Opp. 10", round(float(ep.loc[10, 'ep']), 2)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
