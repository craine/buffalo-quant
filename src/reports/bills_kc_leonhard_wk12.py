"""Bills-Chiefs series, part 1 (Nov. 24, 2026): the Leonhard file.

What Denver's 2025 defense did (Jim Leonhard was its pass game coordinator), how it played Patrick Mahomes in their one
2025 meeting with him, and whether Buffalo's 2026 defense under Leonhard plays the same way.

Writes reports/2026-wk12-kc-leonhard.md, one PNG (bills-kc-wk12-leonhard.png) and a hero JSON.

Sources and pins:
- Results: nflverse play-by-play. Dropbacks = pass plays (sacks and scrambles included), regular season, EPA not null,
  no two-point tries, spikes or no-plays.
- Rushers and blitzers per play: FTN charting (raw_ftn), 2025 and 2026.
- Man/zone coverage and pressure: nflverse participation (raw_participation). Published through 2025 only; 2026 not out.
- 2026 is pinned to weeks 1-10 (every game final and FTN-charted). 2025 is the full regular season.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.db import ROOT, query
from src.reports.defense_baseline import BLUE, GRAY, INK, MUTED, RED
from src.reports.wk11_postgame import finish, ordn as _ordn


def ordn(n):
    return _ordn(int(n))

OUT = ROOT / "reports"
SLUG = "2026-wk12-kc-leonhard"
PNG = "bills-kc-wk12-leonhard.png"
WK26 = 10                      # 2026 pinned to weeks 1-10
MAHOMES = "00-0033873"
DEN_KC_25 = "2025_11_KC_DEN"   # Denver's only 2025 game against Mahomes (Week 17 was against a backup)
DEN_KC_25B = "2025_17_DEN_KC"
SRC_NOTE = "Source: nflverse play-by-play and participation, FTN charting. Regular season."


def dropbacks():
    d = query(f"""SELECT p.season, p.week, p.game_id, p.posteam, p.defteam, p.play_id, p.epa, p.sack, p.yards_gained,
                  p.passer_player_id, p.rusher_player_id, p.home_score, p.away_score, p.home_team,
                  f.n_blitzers, f.n_pass_rushers
                  FROM raw_pbp p LEFT JOIN raw_ftn f ON f.nflverse_game_id = p.game_id AND f.nflverse_play_id = p.play_id
                  WHERE p.season_type = 'REG' AND p.pass = 1 AND p.epa IS NOT NULL AND p.play_type <> 'no_play'
                    AND COALESCE(p.two_point_attempt, 0) = 0 AND COALESCE(p.qb_spike, 0) = 0
                    AND (p.season = 2025 OR (p.season = 2026 AND p.week <= {WK26}))""")
    d.loc[d.n_pass_rushers > 11, "n_pass_rushers"] = np.nan      # two bad FTN rows (56 and 67 rushers)
    d["five"] = d.n_pass_rushers >= 5
    d["blitz"] = d.n_blitzers > 0
    return d


def profile(x):
    c = x[x.n_pass_rushers.notna()]
    return pd.Series(dict(n=len(x), charted=len(c), five=c.five.mean(), blitz=c.blitz.mean(), epa=x.epa.mean(),
                          sack=x.sack.mean()))


def main():
    d = dropbacks()
    s26 = d[d.season == 2026]
    assert s26.week.max() == WK26 and (d[d.season == 2025].n_pass_rushers.notna().mean() == 1.0)
    assert int(s26.n_pass_rushers.isna().sum()) == 2                      # weeks 1-10 fully charted except the 2 bad rows

    t = d.groupby(["season", "defteam"]).apply(profile)
    assert len(t.loc[2025]) == 32 and len(t.loc[2026]) == 32
    for k, asc in (("five", False), ("blitz", False), ("epa", True), ("sack", False)):
        t[f"{k}_rk"] = t.groupby(level=0)[k].rank(ascending=asc, method="min").astype(int)
    lg = d.groupby("season").apply(profile)
    rk_cols = [c for c in t.columns if c.endswith("_rk")]
    t[rk_cols] = t[rk_cols].astype(int)
    den, b25, b26 = (t.loc[k].copy() for k in ((2025, "DEN"), (2025, "BUF"), (2026, "BUF")))
    for r in (den, b25, b26):
        for c_ in rk_cols:
            r[c_] = int(r[c_])
    b26_games = s26[s26.defteam == "BUF"].game_id.nunique()
    assert b26_games == 9

    # coverage and pressure, 2025 only (participation)
    pa = query("""SELECT nflverse_game_id AS game_id, play_id, defense_man_zone_type AS mz, defense_coverage_type AS cov,
                  was_pressure FROM raw_participation WHERE season = 2025""")
    assert query("SELECT COUNT(*) n FROM raw_participation WHERE season = 2026").n.iloc[0] == 0
    c = d[d.season == 2025].merge(pa, on=["game_id", "play_id"], how="inner")
    c = c[c.mz.isin(["MAN_COVERAGE", "ZONE_COVERAGE"])]
    c["man"] = c.mz.str.contains("MAN")
    cv = c.groupby("defteam").agg(n=("man", "size"), man=("man", "mean"), press=("was_pressure", "mean"))
    cv["man_rk"] = cv.man.rank(ascending=False, method="min").astype(int)
    cv["press_rk"] = cv.press.rank(ascending=False, method="min").astype(int)
    lg_man, lg_press = float(c.man.mean()), float(c.was_pressure.mean())
    den_cov = c[c.defteam == "DEN"]["cov"].value_counts(normalize=True)
    den_c1 = float(den_cov.get("COVER_1", 0))
    assert cv.loc["DEN", "man_rk"] == 1
    dc = c[c.defteam == "DEN"]
    den_man_early, den_man_late = float(dc[dc.week <= 8].man.mean()), float(dc[dc.week >= 9].man.mean())
    den_five_late = float(d[(d.season == 2025) & (d.defteam == "DEN") & (d.week >= 9) & d.n_pass_rushers.notna()].five.mean())
    assert round(den_man_early, 2) == 0.56 and round(den_man_late, 2) == 0.35

    # Denver vs. Mahomes, Week 11 2025
    g = d[(d.game_id == DEN_KC_25) & (d.defteam == "DEN")]
    qb = g.assign(q=g.passer_player_id.fillna(g.rusher_player_id))
    assert (qb.q == MAHOMES).all()
    gm = query(f"SELECT home_team, away_team, home_score, away_score FROM raw_schedules WHERE game_id = '{DEN_KC_25}'").iloc[0]
    assert (gm.home_team, gm.home_score, gm.away_score) == ("DEN", 22, 19)
    gc = c[(c.game_id == DEN_KC_25) & (c.defteam == "DEN")]
    g_man, g_press = float(gc.man.mean()), float(gc.was_pressure.mean())
    g_epa, g_n = float(g.epa.mean()), len(g)
    g_five = float(g.five.mean())
    mah25 = d[(d.season == 2025) & (d.passer_player_id.fillna(d.rusher_player_id) == MAHOMES)]
    mah25_epa = float(mah25.epa.mean())
    # the Week 17 game: Mahomes didn't play
    g2 = d[(d.game_id == DEN_KC_25B) & (d.defteam == "DEN")]
    assert not (g2.passer_player_id.fillna(g2.rusher_player_id) == MAHOMES).any()
    gm2 = query(f"SELECT home_team, home_score, away_score FROM raw_schedules WHERE game_id = '{DEN_KC_25B}'").iloc[0]
    assert (gm2.home_team, gm2.home_score, gm2.away_score) == ("KC", 13, 20)
    mah_last = query(f"""SELECT MAX(week) w FROM raw_pbp WHERE season = 2025 AND season_type = 'REG' AND passer_player_id = '{MAHOMES}'""").w.iloc[0]
    assert int(mah_last) == 15

    # Kansas City's 2026 offense
    off = d.groupby(["season", "posteam"]).epa.mean()
    kc26, kc26_rk = float(off.loc[(2026, "KC")]), int(off.loc[2026].rank(ascending=False, method="min")["KC"])
    m26 = s26[s26.passer_player_id.fillna(s26.rusher_player_id) == MAHOMES]
    m_five = float(m26[m26.five].epa.mean())
    m_four = float(m26[~m26.five].epa.mean())
    m_five_n, m_four_n = int(m26.five.sum()), int((~m26.five).sum())
    assert m_five < m_four and m_four - m_five < 0.1
    lc = s26[s26.n_pass_rushers.notna()]
    lg_four26, lg_five26 = float(lc[~lc.five].epa.mean()), float(lc[lc.five].epa.mean())
    jump_b, jump_lg = float(b26.five - b25.five), float(lg.loc[2026, "five"] - lg.loc[2025, "five"])
    assert jump_b > 2 * jump_lg
    n_up = int((t.loc[2026, "five"] > t.loc[2025, "five"]).sum())
    f26 = lc[lc.five]
    five_sack = f26.groupby("defteam").sack.mean()
    b_five_sack, b_five_n = float(five_sack["BUF"]), int((f26.defteam == "BUF").sum())
    b_five_sack_rk = int(five_sack.rank(ascending=False, method="min")["BUF"])
    lg_five_sack = float(f26.sack.mean())
    assert (round(b_five_sack, 3), b_five_sack_rk, round(lg_five_sack, 3)) == (0.068, 25, 0.086)
    s25 = d[(d.season == 2025) & d.n_blitzers.notna() & d.n_pass_rushers.notna()]
    mism26 = int((lc.n_blitzers != (lc.n_pass_rushers - 4).clip(lower=0)).sum())
    match25 = float((s25.n_blitzers == (s25.n_pass_rushers - 4).clip(lower=0)).mean())
    assert mism26 == 1

    # one real example of the charting: the first 2026 Bills sack with 5+ rushers
    ex = query(f"""SELECT p.week, p.desc, p.passer_player_id, p.sack_player_id, p.half_sack_1_player_id, f.n_pass_rushers, f.n_blitzers FROM raw_pbp p JOIN raw_ftn f
                   ON f.nflverse_game_id = p.game_id AND f.nflverse_play_id = p.play_id
                   WHERE p.season = 2026 AND p.week <= {WK26} AND p.defteam = 'BUF' AND p.sack = 1 AND f.n_pass_rushers >= 5
                   ORDER BY p.week, p.play_id LIMIT 1""").iloc[0]
    nm = query("SELECT gsis_id, display_name FROM raw_players").set_index("gsis_id").display_name
    ex_qb = nm[ex.passer_player_id]
    ex_sacker = nm[ex.sack_player_id or ex.half_sack_1_player_id]

    # ---- chart: three small panels, four bars each
    groups = ["NFL average\n2025", "Denver\n2025", "Bills\n2025", "Bills\n2026"]
    cols = [GRAY, "#FB4F14", "#7F95C2", BLUE]
    panels = [
        ("Sends 5 or more pass rushers", [lg.loc[2025, "five"], den.five, b25.five, b26.five], True, None),
        ("Plays man coverage", [lg_man, cv.loc["DEN", "man"], cv.loc["BUF", "man"], np.nan], True, "Not charted\nyet for 2026"),
        ("Sacks per dropback", [lg.loc[2025, "sack"], den.sack, b25.sack, b26.sack], True, None),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.9), dpi=200)
    for ax, (ttl, vals, pct, na_txt) in zip(axes, panels):
        x = np.arange(4)
        ax.bar(x, [0 if np.isnan(v) else v for v in vals], 0.66, color=cols, zorder=2)
        for i, v in enumerate(vals):
            if np.isnan(v):
                ax.text(i, 0.01, na_txt, ha="center", va="bottom", fontsize=8, color=MUTED, style="italic")
            else:
                ax.text(i, v + max(vals[j] for j in range(4) if not np.isnan(vals[j])) * 0.02, f"{v:.0%}" if v >= 0.1 else f"{v:.1%}",
                        ha="center", va="bottom", fontsize=10, fontweight="bold", color=INK)
        ax.set_xticks(x, groups, fontsize=8.5)
        ax.set_title(ttl, fontsize=11, color=INK, loc="left")
        ax.yaxis.set_visible(False)
        for sp in ("left",):
            ax.spines[sp].set_visible(False)
        ax.tick_params(axis="x", length=0)
    finish(fig, "Buffalo now sends extra rushers like Denver did. The sacks haven't followed",
           f"Share of opponents' dropbacks. Denver 2025: Jim Leonhard was its pass game coordinator. Bills 2026: weeks 1-{WK26}, Leonhard's first year as coordinator.",
           f"{SRC_NOTE} Dropbacks: Denver 2025 {int(den.n)}, Bills 2025 {int(b25.n)}, Bills 2026 {int(b26.n)}. Man coverage: nflverse participation, published through 2025.\n2026 NFL averages, weeks 1-{WK26}: 5+ rushers {lg.loc[2026, 'five']:.0%}, sacks per dropback {lg.loc[2026, 'sack']:.1%}.")
    fig.texts[-1].set_text(fig.texts[-1].get_text().replace("Source: nflverse play-by-play and schedules (completion chance: nflverse model). Regular season.\n", ""))
    fig.savefig(OUT / PNG)
    plt.close(fig)

    md = f"""# Buffalo hired Denver's pass-defense coach. Now the Bills send extra rushers like Denver did. The sacks haven't come

**Before Jim Leonhard became Buffalo's defensive coordinator, he coached Denver's pass defense. In 2025 that defense played more man coverage than
any team in the NFL and got more sacks per dropback than anyone. Through {"nine" if b26_games == 9 else b26_games} games under Leonhard, the Bills send five or more pass rushers
on {b26.five:.0%} of dropbacks, up from {b25.five:.0%} last season. But their sack rate has dropped to {ordn(b26.sack_rk)} in the league. On Thursday they face
Patrick Mahomes, who has been good this season whether teams send extra rushers or not.**

*Part 1 of our Bills-Chiefs series. Regular-season data: all of 2025, and 2026 through Week {WK26} (the Bills' first {b26_games} games; Week 11 isn't fully charted yet).
A "dropback" is any pass play: completions, incompletions, sacks and scrambles.*

![Buffalo now sends extra rushers like Denver did. The sacks haven't followed]({PNG})

## What Denver did in 2025

Leonhard was Denver's defensive backs coach and pass game coordinator, and in 2025 its assistant head coach. Vance Joseph was the coordinator.
Denver's pass defense had a clear style:

- **Man coverage.** Denver played man on {cv.loc['DEN', 'man']:.0%} of dropbacks, the most in the NFL. The league average was {lg_man:.0%}. Its most common
  look was one deep safety with everyone else in man ({den_c1:.0%} of dropbacks).
- **Extra rushers.** Denver sent five or more on {den.five:.0%} of dropbacks, {ordn(den.five_rk)} in the league.
- **Sacks.** Denver got a sack on {den.sack:.1%} of dropbacks, {ordn(den.sack_rk)} in the NFL.

## The one time Denver faced Mahomes

Denver and Kansas City met twice in 2025, and Denver won both. But Mahomes played in only one of them: Week {DEN_KC_25.split('_')[1]}, a {int(gm.home_score)}-{int(gm.away_score)} Denver win.
He didn't play after Week {int(mah_last)}, so the Week 17 game ({int(gm2.away_score)}-{int(gm2.home_score)} Denver) was against a backup, and we leave it out.

Against Mahomes, Denver played man on {g_man:.0%} of his {g_n} dropbacks. That's below its {cv.loc['DEN', 'man']:.0%} for the season, but it's about what Denver was doing
by then: after playing man on {den_man_early:.0%} of dropbacks through Week 8, it dropped to {den_man_late:.0%} from Week 9 on. It sent five or more rushers {g_five:.0%} of the time.
Mahomes was held to {g_epa:+.2f} points per dropback, below his 2025 average of {mah25_epa:+.2f}.
(Points per dropback is how much each pass play helped the offense, on average, measured in points.)
One game is a small sample, and it can't tell us which part of Denver's plan worked.

## What Buffalo does now

This season, Buffalo sends five or more rushers on {b26.five:.0%} of dropbacks ({ordn(b26.five_rk)} in the league), up from {b25.five:.0%}
({ordn(b25.five_rk)}) in 2025. Teams across the league are sending more this year ({lg.loc[2025, 'five']:.0%} last season, {lg.loc[2026, 'five']:.0%} now), but Buffalo's jump is more than twice as big.

The extra rushers haven't turned into sacks. Buffalo gets a sack on {b26.sack:.1%} of dropbacks, {ordn(b26.sack_rk)} in the league, down from {b25.sack:.1%} in 2025 (league average this season: {lg.loc[2026, 'sack']:.1%}).
And the pass defense overall has slipped: opponents gain {b26.epa:+.2f} points per dropback ({ordn(b26.epa_rk)}), compared with {b25.epa:+.2f} ({ordn(b25.epa_rk)}) last season.

We can't tell yet whether Buffalo plays as much man coverage as Denver did. That data for 2026 isn't out.

## Why it matters Thursday

Kansas City's passing game ranks {ordn(kc26_rk)} this season at {kc26:+.2f} points per dropback. Against five or more rushers, Mahomes has averaged
{m_five:+.2f} points per dropback; against four or fewer, {m_four:+.2f}. That's a small sample ({m_five_n} and {m_four_n} dropbacks). Extra rushers cost him about what they
cost every offense (league-wide: {lg_four26:+.2f} against four or fewer, {lg_five26:+.2f} against five or more). The difference is that even against extra rushers, he's
far above the league. When Buffalo does send five or more, it gets a sack on {b_five_sack:.1%} of those dropbacks, {ordn(b_five_sack_rk)} in the league
(league average: {lg_five_sack:.1%}).

Tomorrow: what has slowed Mahomes down over the last four seasons.

## How we measured it

FTN, a charting service, records how many players rushed the passer on every NFL play. For example, on a Week {int(ex.week)} sack of {ex_qb}
(by {ex_sacker}), FTN counted {int(ex.n_pass_rushers)} Bills rushers. We count every dropback (passes, sacks and scrambles) and divide.
Man or zone coverage comes from charting published by nflverse; it's out through 2025 only. "Points per dropback" measures how much each pass play moved
the offense closer to or further from scoring, in points. Above zero helps the offense; below zero hurts it. It's the same measure we use in every Bills story.
Plays wiped out by penalties are left out.

## For the stat-heads

- Dropbacks: `pass == 1`, EPA not null, no two-point tries, spikes or no-plays; regular season. 2025 full season; 2026 weeks 1-{WK26} (all final, FTN coverage 100%).
- FTN's 2026 blitzer count equals rushers minus four (zero when four or fewer rush) on all but {mism26} of {len(lc):,} dropbacks ({match25:.0%} in 2025), so we use rushers only. Two FTN rows with impossible rusher counts are dropped.
- DEN 2025: {int(den.n)} dropbacks; 5+ rushers {den.five:.3f} ({den.five_rk:.0f}); man wk 1-8 {den_man_early:.3f}, wk 9+ {den_man_late:.3f}; 5+ wk 9+ {den_five_late:.3f}; sack rate {den.sack:.3f} ({den.sack_rk:.0f}); EPA/db {den.epa:+.3f} ({den.epa_rk:.0f}).
  Participation: man {cv.loc['DEN', 'man']:.3f} (1st), pressure {cv.loc['DEN', 'press']:.3f} ({cv.loc['DEN', 'press_rk']:.0f}).
- BUF 2025: {int(b25.n)}; 5+ {b25.five:.3f} ({b25.five_rk:.0f}); sack {b25.sack:.3f} ({b25.sack_rk:.0f}); EPA/db {b25.epa:+.3f} ({b25.epa_rk:.0f});
  man {cv.loc['BUF', 'man']:.3f} ({cv.loc['BUF', 'man_rk']:.0f}); pressure {cv.loc['BUF', 'press']:.3f} ({cv.loc['BUF', 'press_rk']:.0f}).
- BUF 2026 on 5+ rusher dropbacks: sack rate {b_five_sack:.3f} on {b_five_n} ({b_five_sack_rk}); league {lg_five_sack:.3f}.
- BUF 2026 wk 1-{WK26}: {int(b26.n)}; 5+ {b26.five:.3f} ({b26.five_rk:.0f}); change {jump_b:+.3f} vs league {jump_lg:+.3f} ({n_up} of 32 teams up); sack {b26.sack:.3f} ({b26.sack_rk:.0f}); EPA/db {b26.epa:+.3f} ({b26.epa_rk:.0f}).
- League 2026 wk 1-{WK26}: 5+ {lg.loc[2026, 'five']:.3f}; sack {lg.loc[2026, 'sack']:.3f}; EPA/db vs 4 or fewer {lg_four26:+.3f}, vs 5+ {lg_five26:+.3f}.
- League 2025: 5+ {lg.loc[2025, 'five']:.3f}; sack {lg.loc[2025, 'sack']:.3f}; man {lg_man:.3f}; pressure {lg_press:.3f}.
- DEN vs. KC, {DEN_KC_25}: {g_n} Mahomes dropbacks, EPA/db {g_epa:+.3f}; man {g_man:.3f}, pressure {g_press:.3f}, 5+ {g_five:.3f}. Mahomes 2025 EPA/db {mah25_epa:+.3f} ({len(mah25)}, all of his 2025 dropbacks including his partial Week 15).
- KC 2026 offense EPA/db {kc26:+.3f} ({kc26_rk}). Mahomes vs 5+ rushers {m_five:+.3f} (n {m_five_n}); vs 4 or fewer {m_four:+.3f} (n {m_four_n}). Small samples.
- Leonhard's Denver titles: defensive backs coach and pass game coordinator (2024); assistant head coach and pass game coordinator (2025). Coordinator: Vance Joseph.
"""
    (OUT / f"{SLUG}.md").write_text(md)
    (OUT / f"{SLUG}.hero.json").write_text(json.dumps({
        "label": "Buffalo's pass rush under Jim Leonhard",
        "big": [[round(float(b26.five) * 100), "% of pass plays with 5+ rushers, 2026"], [round(float(b25.five) * 100), "% in 2025"]],
        "note": f"Since Leonhard arrived from Denver, the Bills send extra rushers far more often. The sacks haven't followed: Buffalo is {ordn(b26.sack_rk)} in sack rate.",
        "explainer": {"kicker": "Denver 2025", "title": "Man coverage: Denver vs. the NFL, 2025",
                      "text": "Share of dropbacks in man coverage:", "fmt": "pct",
                      "bars": [["Denver", round(float(cv.loc['DEN', 'man']), 3)], ["NFL average", round(lg_man, 3)]]},
    }, indent=1))
    print(md)


if __name__ == "__main__":
    main()
