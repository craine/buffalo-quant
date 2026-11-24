# Quant review (stage 2, round 4, full re-review): 2026-wk12-kc-leonhard — FAIL (publish after fixes)

Round 3 report: `-quant-r3.md`. Full re-review of the reworked story, hero, card, chart and generator. All numbers re-derived with my own
queries (scripts in /tmp/qa, outside the repo). Unchanged sections (Denver, Week 11 vs. Mahomes, Thursday) re-checked against round 3: still correct.

## Must fix (ranked)

### 1. Last season's fade was in the pressure too, not just the sacks
Text: "One more reason not to read too much into sack totals: last season's fast start didn't hold. Buffalo had 25 sacks through nine games and
11 in the last eight, finishing with 36 (20th in the NFL)."
- The sentence implies sacks are the noisy part and pressure is the solid part. Last year both faded. Over the last eight games of 2025, Buffalo had
  48 pressures on 245 dropbacks (0.196, 28th; league 0.246) and 11 sacks (0.045 per dropback, 27th; league 0.064). Through nine games it was 4th
  and 5th.
- "20th in the NFL" ranks the season total (36, tied with GB) while every other sack rank in the story is per dropback. Per dropback, 2025 full
  season was 14th (0.0679).
Replacement (writer computes and asserts 28th and 27th):
> Last year is a warning about fast starts. Through nine games, Buffalo was 4th in pressure rate and 5th in sacks per dropback. Over the last
> eight games it fell to 28th in pressure and 27th in sacks, with 11 sacks. It finished with 36, 14th in the league per dropback.

### 2. Buffalo's pressure count is tied for 3rd, with Denver
BUF 107 = DEN 107 (MIN 116, SEA 109). The generator's ordn() doesn't flag ties.
- Lead: "the Bills have 107 quarterback pressures, 3rd in the NFL" -> "the Bills have 107 quarterback pressures, tied for 3rd in the NFL"
- Hero big label: "QB pressures, 3rd in the NFL" -> "QB pressures, tied for 3rd in the NFL"
- Card: "Buffalo is 3rd as a team" -> "Buffalo is tied for 3rd as a team"
(Counts also depend on games played. The rate rank (4th) is the fair one, and the body already leads with it.)

### 3. Pressure "rate" is player credits per dropback, not a share of plays
Text: "Buffalo is getting one on 28.5% of opponents' dropbacks, 4th in the NFL (league average: 24.5%). That's about where it was at this point last year
(29.5%, also 4th), but on more plays: 107 pressures now against 84 then."
PFR's def_pressures = hurries + hits + sacks per player, with a half sack counted as a full pressure for each player (checked: pressures - (hurries +
hits + sacks) is 0 or the half-sack round-up on every row, 2022-2026). Two players can be credited on the same play, so team pressures / dropbacks
isn't the "% of dropbacks with a pressure". The definition is the same in 2025 and 2026, so the comparison is fair as a rate.
Replacement:
> Buffalo has 107 pressures on 375 opponent dropbacks, about 29 for every 100. That ranks 4th in the NFL (league average: about 25). It's about where
> Buffalo was at this point last year (29 for every 100, also 4th), but on more plays: 107 pressures now against 84 then.
Chart: panel "QB pressures per dropback" with % labels reads as a share of plays. Relabel "QB pressures per 100 dropbacks" and show 23 / 33 / 29 / 29
without % signs. Stat-heads can keep the decimals.

### 4. Two different 2025 numbers for the same stat (extra rushers)
The body says "up from 25% (21st) in 2025" (full season). The chart shows "Bills 2025 first 9 games" at 24%. Use the same window as the chart and the rest
of the story. My numbers for 2025 Weeks 1-10: BUF 0.2386, 22nd (CAR 0.2382 23rd, no tie); league 0.2684. Jump 11.6 vs league 4.5: "more than twice"
still holds.
- "up from 25% (21st) in 2025." -> "up from 24% (22nd) at this point last season."
- "(27% last season, 31% now)" -> "(27% at this point last season, 31% now)"

### 5. Crosby played one more game
Maxx Crosby's 35 came in 10 games (LV had no bye in Weeks 1-10); Rousseau's 37 came in 9.
- Hero explainer title: "Most QB pressures in the NFL, first nine games of 2026" (wrong for Crosby) -> "Most QB pressures in the NFL, Weeks 1-10 of 2026"
- Body: "(Maxx Crosby is next with 35)" -> "(Maxx Crosby is next with 35, in one more game)"

### 6. "Leads the NFL" is as of Week 10
PFR has Week 11 for 1 of 14 games, and Crosby played in Week 11. Lead: "Greg Rousseau has 37, the most of any player." -> "Greg Rousseau has 37, the
most of any player through Week 10." The headline can stay if the lead carries the date. If PFR loads Week 11 before publishing, re-check the
headline claim.

## Verified (own numbers)
- PFR coverage: all 272 games of 2025 and all 150 of 2026 Weeks 1-10 present, both teams in every game. The definition is identical across seasons
  (see 3). League pressures per game rose (2025 16.9; 2026 about 18), and the per-dropback rate in Weeks 1-10 went from 0.222 to 0.245. That could be real or a
  charting drift, so compare within seasons. Ranks do this.
- First nine games: BUF played 9 games in Weeks 1-10 in both 2025 and 2026 (bye inside the window both years).
- 2026 Weeks 1-10: BUF 375 db, 107 pressures (tied 3rd), 0.2853 (4th; LV 0.2997, DEN 0.2801), league 0.2453. Sacks 21 (pbp = PFR = 21), 0.056 (20th),
  league 0.0646. Sacks per pressure 0.1963, 28th (ATL 0.2059, WAS 0.1957, no tie); league 0.2617.
- 2025 Weeks 1-10: 285 db, 84 pressures, 0.2947 (4th), 25 sacks, 0.0877 (5th), conversion 0.2976 -> 30%. League 0.222.
- 2025 full: 132 pressures, 0.2491 (11th); 36 sacks (tied 20th in total, 14th per dropback). DEN 2025 pressures 0.329.
- Rousseau (PFR RousGr00 -> gsis 00-0036914, "Greg Rousseau"): 37 pressures in 9 games, 1st; Crosby 35 (10 g), Dallas Turner 30. Share 37/107 = 34.6%
  -> "about 35%". Earlier seasons through Week 10: 14, 10, 17, 23, 14. His first nine games played each year: 14, 14, 17, 23, 15. "23" holds either way.
- Sacks from play-by-play: Rousseau 8 (PFR also 8), plus 2 in Week 11 vs. Miami = 10. The rest of the team has 13; TJ Parker 3.5 the most; then
  Chubb 1.5 and Hoecht 1.5. Team 23 through Week 11.
- "The gap is in how often pressure becomes a sack": the pressure rate held (0.295 -> 0.285) while conversion fell (0.298 -> 0.196). The arithmetic
  supports it.
- Chart: values match (5+: 27/32/24/35; pressures 23/33/29/29; sacks 6.5/9.8/8.8/5.6; man 31/44/30/n.a.). Footer n's 693/285/375 and 2026 averages
  (31%, 25%, 6.5%) match. Opened the image; no overlaps.
- Hero: 107 / 21 / 25 / 37 / 35 / 20% / 30%: match (see 2 and 5 for labels). Card: see 2.
- The image wasn't published (only on the branch). Removing its manifest entry for re-freeze is fine.
- Reproducibility: clean copy, outputs deleted, generator re-run: md, hero JSON and PNG byte-identical (PNG sha256 a63d4bcd...f11db).
- No betting language. Leonhard's titles unchanged (verified round 1).
