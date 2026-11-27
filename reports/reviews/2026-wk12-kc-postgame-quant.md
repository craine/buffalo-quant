# Quant review: 2026-wk12-kc-postgame (stage 2)

**Verdict: publish with fixes (recorded as FAIL until the two must-fixes are applied).**
Story sha256 at review: b6ca2661577462a2682fbbc1d757c368c50dc7cf18f7198546889edcd6302b8d. Every number re-derived with my own SQL
against data/buffalo.db (2026 pbp fingerprint (28843, -180.1391) confirmed) and ledger/*.csv, not by running the generator.

## Must-fix

1. **Mahomes denominator is wrong: 135 is not "his regular-season starts".**
   Evidence: raw_schedules (home_qb_id/away_qb_id = 00-0033873, REG, final) gives **137** regular-season starts: the generator's
   "15+ dropbacks, 2018 on" filter drops 2017_17_KC_DEN (his first start, KC 27) and 2019_07_KC_DEN (left injured, KC 30).
   The count of 10-or-fewer games is 5 either way (2021_07 TEN 3, 2023_08 DEN 9, 2025_14 HOU 10, 2026_07 SEA 3, 2026_12 BUF 10).
   - Replace: `something that has happened in only 5 of his 135 regular-season starts.`
   - With (writer computes 137 in the generator from raw_schedules QB ids): `something that has happened in only 5 of his 137 regular-season starts.`
   - Also update the stat-heads line `Mahomes starts: 15+ dropbacks, regular season, 2018 on.` to describe the new definition
     (starting QB per the schedule, regular season, 2017 on). Part 3's "typical game since 2023" set can stay on its own definition.

2. **"Buffalo did this one" overclaims the big-play measure.**
   Evidence: KC 2 of 31 dropbacks gained 20+ (6.45%). Mahomes' median game since 2023 (56 other games, 15+ dropbacks): 7.60%; pooled 7.72%.
   At his usual rate he'd have about 2.4 such plays on 31 dropbacks, so Thursday was less than half a play below normal. 18 of his 56
   other games (32%) were as low or lower. The rounding (6% vs 8%) makes the gap look bigger than it was.
   - Replace: `In Mahomes' typical game since\n  2023 it's 8%. Buffalo did this one.`
   - With: `In Mahomes' typical game since\n  2023 it's 8%. That's close to normal, so call this one even, not a win for Buffalo.`

## Should-fix

3. Small samples unlabeled in the part 3 section (31 dropbacks, 19 runs, one game). Add after the run bullet, or in each bullet:
   `(One game: 31 pass plays and 19 runs, so treat these as a snapshot.)` (numbers already in the generator: t.loc['KC','db'], runs count needs exposing).
4. "against 22.9 expected in dry games" slightly misstates part 4: 22.9 is what the same offenses/defenses would be expected to score
   based on their dry games. Replace `against 22.9 expected in dry games` with `against the 22.9 we'd expect from the same teams in dry weather`.
5. One KC "run" is an aborted Mahomes snap (6:07, "FUMBLES (Aborted)") counted as rush=1. Excluding it, runs worked 12 of 18 (67%); the claim
   only gets stronger. No change needed; mention in stat-heads if desired.
6. Mahomes "typical game since 2023" here uses 56 games (excl. Thursday); part 3's hero says 55 starts since 2023 through Week 11. Not a
   published number in this story, but the writer should confirm the sets match part 3's definition.

## Overclaim checks requested

- **"Fewest in any of his wins" scope:** OK. 2018 is Allen's rookie year, so 2018 on is his full career. Across *all* 152 Allen appearances
  (no attempt filter), he has 105 wins, 150 starts, 0 ties; every win had 15+ attempts, so the filter drops no win. 105 = 97 REG + 8 POST.
  Passing yards match raw_player_week exactly in all 150 overlapping games. Lowest win 81 (Thu), next 82 (2018_05_TEN_BUF), then 94.
  The one 15+ game with fewer yards is 2018_01_BUF_BAL (74, loss; a relief appearance, not a start). Also a 5-yard 2019_17 relief game
  (5 attempts, loss) is excluded by the 15+ filter; doesn't affect the claim.
- **"The rain, as forecast":** fair. Part 4 and the preview forecast rain all game; nflverse game note reads "Rain ... Wind: NE 19 mph".
  Wind came in above the 10-13 mph sustained forecast, and the story says "listed at". The section hedges ("One game proves nothing").
- **"Buffalo did this one":** not fair; see must-fix 2.
- **Cook streak:** counts games correctly. Per-game check: Cook was ACT and had touches in all 11 Bills games (W1-W6, W8-W12; W7 bye);
  TD in W2-W12 = 10 straight; no TD W1, and none in the last four 2025 games, so the streak starts in 2026. The generator's query
  would *break* (not skip) the streak on a missed game, so it can't overcount.

## Verified (my numbers)

| Claim | Story | Mine |
|---|---|---|
| Final, kick | 13-10; Bass 57 yds, 4 s left, tied 10-10 | same (FG 54 Q4 12:03, Butker miss 46 6:01, Bass 57 :04) |
| Allen line | 10/21, 81, 2 INT | 10/21 (excl. sacks, no-plays), 81, 2 |
| Allen games / wins / median | 151 / 105 / 239 | 151 / 105 / 239 |
| Fewer yards, any 15+ game | 1, a loss | 1 (2018_01 at BAL, 74) |
| Next-lowest win | 82 | 82 |
| Designed runs, share, rank | 40, 61%, 6th of 143 | 40 of 66 (60.6%), 6th, no tie; 143 REG games matches schedule |
| No 20+ pass games | 5th of 143 | 5 (2018_05, 2021_17, 2024_16, 2025_13, 2026_12), same with completions-only |
| Cook | 32-117, only BUF TD, 10 straight | 32-117; BUF TD Cook Q2 14:36 (other TD is KC E.Johnson) |
| Mahomes <=10 | 5 of 135 | 5 of 137 starts (must-fix 1) |
| Big plays | 6% vs 8% | 2/31 = 6.45% vs median 7.60% |
| KC run success | 63% vs 41% | 12/19 = 63.2% vs median 41.0%; 3rd-highest of his 57 games since 2023 |
| Projection / part 4 | 25.6-23.9; 18.3 vs 22.9; 27th | match preview, part 4 and part 3 hero files |
| Allen runs | 7 (4 designed, 3 scrambles) | 4 designed + 3 scrambles from play text |
| Ledger | both 1; 0.2025, 0.0400; 15 of 24 | (1-.55)^2=.2025, (1-.8)^2=.04; 15 right of 24 graded (P0017 ungraded, resolves 11-18) |
| Predictions logged before kickoff | | created 2026-11-25T14:44Z, kickoff 2026-11-27T01:20Z |

Generator reproduces md, PNG and hero byte-for-byte from a clean `git archive HEAD` copy with data symlinked (pre-fix text).
Chart checked: title, subtitle, footer (source + sample size) all correct. PNG not yet in reports/published_images.json (freeze at publish).
Brand: no betting language. Side note: P0017 has no grade row though it resolved 2026-11-18; not this story's issue, flag to Charlie.
