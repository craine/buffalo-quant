"""Follow-up to the NFL mismatches story: home field, rivalries, close upsets and cold, from the same 27 seasons.

Same games and definitions as src/reports/nfl_mismatches.py (regular season 1999-2025, both teams 4+ games played, mismatch = gap in
season-to-date scoring margin). No betting lines: the schedule query lists only game, team, score, division, roof, temperature and
rest columns. Writes reports/2026-11-21-nfl-mismatches-home.md, two PNGs and a hero JSON.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.nfl_mismatches import BINS, LABELS, MIN_GP, NAMES, pregame_margins
from src.reports.sabres_postgame import finish

OUT = ROOT / "reports"
SEASON, WEEK_DONE = 2026, 10
COLD = 40


def main():
    cols = "game_id, season, week, weekday, home_team, away_team, home_score, away_score, div_game, roof, temp"   # never market columns
    s = query(f"SELECT {cols} FROM raw_schedules WHERE game_type = 'REG' AND (season < {SEASON} OR week <= {WEEK_DONE}) ORDER BY season, week")
    assert s.home_score.notna().all()
    pre = pregame_margins(s)
    s = s.join(pre.rename(columns={"m_pre": "hm", "n_pre": "hn"}), on=["game_id", "home_team"]) \
         .join(pre.rename(columns={"m_pre": "am", "n_pre": "an"}), on=["game_id", "away_team"])
    d = s[(s.hn >= MIN_GP) & (s.an >= MIN_GP) & (s.season < SEASON)].copy()
    d["gap"] = (d.hm - d.am).abs()
    d["bh"] = d.hm > d.am
    d["res"] = np.where(d.bh, d.home_score > d.away_score, d.away_score > d.home_score).astype(float) + 0.5 * (d.home_score == d.away_score)
    d["marg"] = np.where(d.bh, d.home_score - d.away_score, d.away_score - d.home_score)
    d["b"] = pd.cut(d.gap, BINS, right=False, labels=LABELS)
    assert len(d) == 5205
    yr0, yr1 = int(d.season.min()), int(d.season.max())
    big = d[d.gap >= 17]
    home, road = big[big.bh], big[~big.bh]
    div, nondiv = big[big.div_game == 1], big[big.div_game == 0]
    d10 = d[d.gap >= 10]
    div10, nondiv10 = d10[d10.div_game == 1], d10[d10.div_game == 0]
    assert home.res.mean() - road.res.mean() > 0.1 and abs(div.res.mean() - nondiv.res.mean()) < 0.03
    by_side = d.groupby(["b", "bh"], observed=True).res.agg(["mean", "size"]).unstack()
    # all games: how much home field is worth on its own (no gap)
    home_all = (d.home_score > d.away_score).mean() + 0.5 * (d.home_score == d.away_score).mean()

    ups = big[big.res == 0]
    wins = big[big.res == 1]
    up_med, up_one = float((-ups.marg).median()), float(((-ups.marg) <= 8).mean())
    win_big, win_close, win_med = float((wins.marg >= 17).mean()), float((wins.marg <= 8).mean()), float(wins.marg.median())
    assert up_one > 0.6 and win_big < 0.5

    hb = big[big.bh & (big.roof == "outdoors")]
    hb_known = hb[hb.temp.notna()]
    cold = hb_known[hb_known.temp <= COLD]
    miss = 1 - len(hb_known) / len(hb)
    assert len(cold) < 40 and cold.res.mean() > 0.9

    old, new = big[big.season <= 2019], big[big.season >= 2020]
    edge = (by_side['mean'][True] - by_side['mean'][False])
    edge_shown = (by_side['mean'][True] * 100).round() - (by_side['mean'][False] * 100).round()   # as the chart labels show them
    assert edge.max() - edge.min() < 0.1   # the home edge is about the same at every gap

    bm = d[((d.home_team == "BUF") & (d.away_team == "MIA")) | ((d.home_team == "MIA") & (d.away_team == "BUF"))]
    bb = bm[(((bm.home_team == "BUF") & bm.bh) | ((bm.away_team == "BUF") & ~bm.bh)) & (bm.gap >= 10)]
    bb_w, bb_l = int((bb.res == 1).sum()), int((bb.res == 0).sum())
    assert (bb_w, bb_l) == (4, 2)

    # Sunday: same 2026 numbers as the first story
    t26 = []
    for side, opp in (("home", "away"), ("away", "home")):
        t = s[s.season == SEASON][[f"{side}_team", f"{side}_score", f"{opp}_score"]].copy(); t.columns = ["team", "pf", "pa"]; t26.append(t)
    t26 = pd.concat(t26); t26["m"] = t26.pf - t26.pa
    m26 = t26.groupby("team").m.mean()
    bm26, mm26 = float(m26["BUF"]), float(m26["MIA"])
    gap_now = bm26 - mm26
    assert 17 <= gap_now < 20

    first = (OUT / "2026-11-19-nfl-mismatches.md").read_text()
    import re
    p_buf_pub = int(re.search(r"Our model's number: Bills (\d+)%", first).group(1))
    assert p_buf_pub == 81
    # ---- chart 1: home vs road by gap
    fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=200)
    xs = np.arange(len(by_side)); w = 0.38
    hm_, rd_ = by_side["mean"][True], by_side["mean"][False]
    ax.bar(xs - w / 2, hm_, w, color=BLUE, label="Better team at home", zorder=2)
    ax.bar(xs + w / 2, rd_, w, color=GRAY, label="Better team on the road", zorder=2)
    for x_, a, b_ in zip(xs, hm_, rd_):
        ax.text(x_ - w / 2, a + 0.012, f"{a:.0%}", ha="center", fontsize=9, color=INK, fontweight="bold")
        ax.text(x_ + w / 2, b_ + 0.012, f"{b_:.0%}", ha="center", fontsize=9, color=MUTED)
    ax.axhline(0.5, color="#D5D8DE", lw=1, ls="--")
    ax.set_xticks(xs, [f"{l}\npoints" for l in by_side.index], fontsize=9.5)
    ax.set_xlabel("Gap between the two teams' scoring margins going in (points per game)")
    ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.set_ylabel("How often the team with the\nbetter scoring margin won")
    ax.legend(frameon=False, fontsize=9.5, loc="upper left"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "At every size of mismatch, the better team wins more at home",
           f"Every regular-season game {yr0}-{yr1} where both teams had played {MIN_GP}+ games ({len(d):,} games). Ties count as half a win.",
           "x")
    fig.texts[-1].set_text(f"Source: nflverse schedules, {yr0}-{yr1} regular seasons.\nScoring margin = points scored minus points allowed per game, that season, before the game.")
    fig.savefig(OUT / "nfl-mismatch-home.png"); plt.close(fig)

    # ---- chart 2: how the 17+ games ended
    fig, ax = plt.subplots(figsize=(9.5, 4.8), dpi=200)
    edges = [-60, -17, -8, 0, 1, 9, 17, 80]
    labs = ["Lost by\n17+", "Lost by\n9-16", "Lost by\n1-8", "Tie", "Won by\n1-8", "Won by\n9-16", "Won by\n17+"]
    cnt = pd.cut(big.marg, edges, right=False, labels=labs).value_counts().reindex(labs).fillna(0)
    colors = [RED, RED, RED, GRAY, BLUE, BLUE, BLUE]
    ax.bar(np.arange(len(labs)), cnt.values, color=colors, width=0.65, zorder=2)
    for i, v in enumerate(cnt.values):
        ax.text(i, v + 2, f"{int(v)}", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_xticks(np.arange(len(labs)), labs, fontsize=9.5)
    ax.set_ylabel("Games"); ax.grid(axis="y", color="#EEF0F3"); ax.set_axisbelow(True)
    finish(fig, "When the much better team loses, it's usually close",
           f"How the {len(big)} games where one team's scoring margin was 17+ points a game better ended, {yr0}-{yr1}, from the better team's side.",
           "x")
    fig.texts[-1].set_text(f"Source: nflverse schedules. One score = 8 points or fewer.")
    fig.savefig(OUT / "nfl-mismatch-endings.png"); plt.close(fig)

    md = f"""# Even a much better NFL team wins far less often on the road. Rivalry games aren't any closer.

**In the last {yr1 - yr0 + 1} seasons, when one team's scoring margin was 17 or more points a game better than its opponent's, it won {home.res.mean():.0%} of the time at home
({len(home)} games) and only {road.res.mean():.0%} on the road ({len(road)} games). Division games, the ones fans expect to be closer, came out the same as any other. And when
the much better team did lose, it was usually a close game. Sunday's Dolphins at Bills game is the home kind.**

*This follows our story on [how often big NFL mismatches go wrong](nfl-mismatches.html), using the same {len(d):,} regular-season games from {yr0} to {yr1}. A
mismatch is the gap between the two teams' scoring margins (points scored minus allowed, per game) going into the game. We don't use betting lines.*

![Home vs road](nfl-mismatch-home.png)

## Home field

Home teams won {home_all:.0%} of all these games, and the home edge shows up at every size of mismatch: in every group on the chart, the better team won {edge_shown.min():.0f} to
{edge_shown.max():.0f} more games out of every 100 at home than on the road. A big gap doesn't make it go away. Among the {int((big.res == 0).sum())} times a much better team lost, {int((road.res == 0).sum())}
were on the road.

## Sunday

The Bills have outscored opponents by {bm26:.1f} points a game this season, and Miami has been outscored by {abs(mm26):.1f}: a gap of {gap_now:.1f}, with the game in Buffalo.
Sunday fits the group that won {home.res.mean():.0%} of the time. That describes past games, not a forecast: our model's chance for the Bills on Sunday, from the first story, is {p_buf_pub}%.

## Rivalry games aren't closer

"Throw out the records" is a common line for division games. The numbers don't back it up. With a gap of 17 or more, the better team won {div.res.mean():.0%} of division
games ({len(div)}) and {nondiv.res.mean():.0%} of the rest ({len(nondiv)}). With a gap of 10 or more it was {div10.res.mean():.0%} and {nondiv10.res.mean():.0%}. The Bills, when they were the
better team by 10 or more going in, went {bb_w}-{bb_l} against Miami from {yr0} to {yr1}, too few games to read much into.

## When the upset comes, it's usually close

![How the games ended](nfl-mismatch-endings.png)

In the {len(ups)} games the much better team lost, the typical upset was decided by {up_med:.0f} points (half were closer, half wider), and {up_one:.0%} were one-score games
(8 points or fewer). When the much better team won, it won by 17 or more {win_big:.0%} of the time and by one score {win_close:.0%} of the time. Its typical winning margin was
{win_med:.0f} points.

## One smaller note

**Cold weather.** When a team 17+ points a game better hosted outdoors at {COLD}°F or colder, it won {int(cold.res.sum())} of {len(cold)}. That's a small group, and the schedule
data has no temperature for {miss:.0%} of these outdoor home games, so take it as a note, not a finding.

## For the stat-heads

- Same sample as the first story: nflverse schedules, regular season {yr0}-{yr1}, both teams with {MIN_GP}+ prior games ({len(d):,}). Ties = 0.5.
- Gap 17+: home {home.res.mean():.3f} (n={len(home)}), road {road.res.mean():.3f} (n={len(road)}); division {div.res.mean():.3f} (n={len(div)}), other {nondiv.res.mean():.3f} (n={len(nondiv)}).
  Gap 10+: division {div10.res.mean():.3f} (n={len(div10)}), other {nondiv10.res.mean():.3f} (n={len(nondiv10)}). All games: home team {home_all:.3f}.
- Upsets (gap 17+): n={len(ups)}, median margin {up_med:.1f}, share decided by 8 or fewer {up_one:.3f}. Better-team wins: n={len(wins)}, 17+ {win_big:.3f}, 8 or fewer {win_close:.3f}.
- Cold: gap 17+, better team at home, roof = outdoors, temp <= {COLD}: {len(cold)} games ({int(cold.res.sum())} wins); temp missing for {miss:.1%} of {len(hb)} outdoor home games.
- Gap 17+: {yr0}-2019 {old.res.mean():.3f} (n={len(old)}), 2020-{yr1} {new.res.mean():.3f} (n={len(new)}). Home-minus-road edge by gap group: {', '.join(f'{k}: {v:+.3f}' for k, v in edge.items())}.
- No market data read: the schedule query selects only game, team, score, division, roof and temperature columns.
"""
    (OUT / "2026-11-21-nfl-mismatches-home.md").write_text(md)
    (OUT / "2026-11-21-nfl-mismatches-home.hero.json").write_text(json.dumps({
        "label": f"Lopsided NFL games, {yr0}-{yr1}",
        "big": [[f"{home.res.mean():.0%}", "Much better team at home won (17+ point gap in scoring margin)"],
                [f"{road.res.mean():.0%}", "Much better team on the road won"]],
        "note": "Division games came out the same as any other, and when the much better team lost, it was usually a one-score game.",
        "explainer": {"kicker": "Home vs. road", "title": "How often a much better team won (17+ point gap in scoring margin)", "text": "How often the much better team won:", "fmt": "pct",
                      "bars": [["At home", round(float(home.res.mean()), 3)], ["On the road", round(float(road.res.mean()), 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
