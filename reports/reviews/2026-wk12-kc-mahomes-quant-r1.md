# Quant review: 2026-wk12-kc-mahomes (stage 2)

**Verdict: FAIL (don't publish as is; publish with fixes after a re-run).**

Reviewed 2026-11-25 against `data/buffalo.db` and the live nflverse release. Independent recomputation in standalone
scripts (not the writer's function), plus a reproduction run of the generator in a clean copy.

## Blocking issues

### 1. The story doesn't reproduce: nflverse revised 2026 EPA after the story was generated

- The md/PNG were written 08:04:55 EST; `raw_pbp` 2026 was reloaded at 08:05:22 EST. nflverse's
  `play_by_play_2026.parquet` (Last-Modified Wed, 25 Nov 2026 10:02:46 GMT) has a different EPA value on **all 19,356**
  filtered 2026 plays versus the older copy still in `clean_plays`; `success` (EPA > 0) flips on 634 of them. 2023-2025 are unchanged.
  The live file matches the current DB exactly (28,467 rows, 0 EPA differences).
- Running the generator in a clean copy fails: `assert (int(B.pr_rk), int(B.expl_rk), int(B.run_rk)) == (4, 20, 20)`.
- `clean_plays` (old EPA) reproduces the story's figures (BUF run rank 20, league 0.405), which confirms the cause.

Numbers that change on current data (everything else re-derives exactly):

| Item | Story | Current data |
|---|---|---|
| BUF designed-run success allowed | 42%, 20th | **45.6%, 27th** (GB 45.6% 26th, NO 46.0% 28th; no tie) |
| League designed-run success 2026 | 40% (0.405) | **43% (0.426)** |
| KC 2026 run success / rank | 46% (0.459), 6th | **48% (0.477), 5th** |
| Low-scoring games run success (17 games) | 34% vs 44% | **35% (0.347) vs 44% (0.440)** |
| OLS (pts per 1 SD) | -2.25 / +3.23 / +2.53 / +0.94 | **-2.26 / +3.25 / +2.47 / +0.92** |
| Hero, card, chart panel 3, lead | "20th against the run" / "20th in both" | **27th** |

The 55-game splits, medians, all-three/none groups, pressure and big-play figures do not change.
The generator pins weeks (WK26 = 10) but not the data vintage, so nflverse revisions break reproduction. Re-run on current data,
update the assertions, and say in "How we measured it" that the play-by-play is nflverse's file as of Nov. 25.
**This changes the story:** Buffalo's run defense is bottom-six, not mid-pack.

### 2. The success definition in the story is wrong

Code uses nflverse `success` = EPA > 0 (verified: 0 mismatches between `success` and `epa > 0` on 7,283 designed runs).
The story describes the yards rule (40%/60%/100%). Under the yards rule the numbers would be different (BUF 51.3%, 25th;
league 49.5%). Fix the description (see the replacement in the caller report). Computed examples available for the plain-English explanation
(designed runs 2023-26): on first-and-10, a 4-yard run counts as a success 9% of the time, a 5-yard run 70%, a 6-yard run 96%;
on third-and-2, a run that gets the first down 98%, one that doesn't 1%. The writer must compute any example used in the generator.

## Other issues (fix)

3. **"held the Chiefs' running backs"**: the measure is all designed runs (RB 93.7%, WR 4.7%, QB 1.0%, others 0.6% of 1,222 KC runs).
   Say "the Chiefs' running game".
4. **"won 50% of the time" in 8 games** needs an explicit small-sample label (4-4). Also say 6-2 for the none group.
5. **"In the 8 where it did none of them, 25.5 points and 75%"** is a selective comparison. By number of things done:
   0 → 25.5 pts, 75% (8); 1 → 27.5, 82% (22); 2 → 21.6, 59% (17); 3 → 16.5, 50% (8). Compare all three against the other 47 games:
   25.0 points, 72% (needs generator code), or keep the none group but don't imply a smooth recipe.
6. **"the better defenses tend to do all of them"** has no code behind it. Opponent defensive EPA/play (season, excluding the KC game)
   by number of things done is -0.017 / +0.016 / -0.031 / -0.029: weak and not monotonic. Cut it or compute it.
7. **"The games where they struggled had three things in common"** overclaims. The run split alone barely moves winning:
   67% vs 71% (about 1.3 games of 27); permutation p for points 0.16, for wins 0.77. Pressure (points p = 0.005) and big plays
   (p = 0.04) are clearer. The run effect does show up in the multi-measure check (+2.47 ± 0.84 SE) and in a neutral-score
   version (below). Soften to "tended to".
8. **"What it means Thursday": "a bit worse than the middle of the league"** is wrong for the run defense on current data (27th).

## Confounding (checked; "associations, not proof" is adequate with the softenings above)

- Opponent quality: adding the opponent's defensive EPA/play (season, excluding the KC game) moves the coefficients to
  -2.13 / +3.06 / +2.13 / +0.86 (SE about 0.85). Holds.
- Game script: in high-pressure games KC trailed on 42% of snaps vs 34%, so some pressure comes from trailing.
  Recomputing big plays and run success only on snaps within 8 points: big plays 21.9 vs 25.6 points; run 21.9 vs 25.6 points,
  63% vs 75%. Holds, and the run effect is stronger.
- Mechanical link: both "big plays" and EPA-based run success are parts of scoring, so some of the association is built in.
  Pressure is the cleanest defensive input. Worth a line in "For the stat-heads".
- Pairwise correlations among the three measures are small (|r| ≤ 0.16).

## Verified (matches the story)

- **Game selection:** 55 games (16/16/14/9), KC 38-17, no ties, no duplicate plays. Excluded correctly: 2023 W18, 2024 W18,
  2025 W16-18 (Mahomes 0 dropbacks). 2026: 9 games through Week 10 (bye). Included games with backup snaps: 2023 W3 (Gabbert 5),
  2024 W15 CLE (Wentz 3), **2025 W15 LAC** (Mahomes 35 dropbacks before injury, Minshew 5). Non-QB trick passes in 3 games.
  Including backup dropbacks in the denominators changes nothing: a Mahomes-only pressure denominator gives the identical split (27/28, same games).
- **PFR matching:** `MahoPa00` has one row per game for all 55; `times_pressured` = hurries + hits + sacks in every game;
  PFR sacks match play-by-play sacks exactly. Denominator includes 156 scrambles, consistent with part 1's def_pressures / dropbacks.
- **Medians and ties:** pressure 0.205, big plays 0.075, run 0.414, 5+ rushers 0.214. With n = 55 the median game falls in "No";
  big plays has one extra tie at the median, so 26/29. Disclose in the stat-heads line ("strictly better than the median game").
- **Splits:** pressure 21.1/59.3%/27 vs 26.4/78.6%/28; big plays 21.7/61.5% vs 25.7/75.9%; run 22.4/66.7% vs 25.1/71.4%;
  5+ rushers 24.4/70.4% vs 23.1/67.9% (FTN coverage ≥98.3% per game). All three: 8 games, 16.5, 50%. None: 8, 25.5, 75%. All 55: 23.8.
- **Buffalo 2026 (wk 1-10):** pressure 0.285, 4th (LV 0.300 3rd, DEN 0.280 5th; no tie), league 0.245. Matches part 1 (107/375, 4th).
  20+ allowed 0.0907, 20th (CIN 0.0888, PIT 0.0912; no tie), league 0.0828.
- **KC 2026:** 20+ rate 0.0887, 11th; pressure on Mahomes 0.232; no non-Mahomes dropbacks in 2026.
- **Low-scoring games:** 17 games with 20 or fewer.
- **Chart opened:** values match; panel 3 note must change to 27th; footer has source and sample size.
- **Brand:** no betting language; no ledger calls in the story.
