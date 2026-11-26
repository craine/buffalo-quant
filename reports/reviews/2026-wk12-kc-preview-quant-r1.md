# Quant review: 2026-wk12-kc-preview (stage 2)

Reviewed text SHA-256 83808cd0... (commit f0a34f9c). Verdict: **publish with fixes** (recorded as fail until fixes are applied).

## Must-fix

1. **Model description is wrong.** "The model projects each team's points from how many points it scores and allows per drive this season, adjusted for who it played, plus home field."
   `points_model.ratings()` does no schedule adjustment: each offense's and defense's points per drive are raw season-to-date rates, shrunk toward last season (K=60 drives, keep 0.7). The only opponent term is *this* opponent's defense rating in `raw_prediction()`.
   Replace with: "The model projects each team's points from how many points its offense scores per drive this season and how many the other team's defense gives up, blended with last season's numbers, plus home field."

2. **Rain-to-Allen inference is not supported.** "The rain could push it up. In [part 4](bills-chiefs-rain-and-wind.html) we found NFL teams run more in the rain."
   Part 4's run finding is team-level `rush = 1` (designed runs only, mostly running backs; scrambles excluded by definition). It says nothing about QB runs, and Call 2 counts scrambles. Second-way check (my own query, not for publication; starting QB = most dropbacks, outdoor REG 2018-2026 wk10, part 4's weather classifier): starting-QB runs per game 3.15 dry (2,922 team-games) vs 3.79 rain (214) vs 3.98 rain+10 mph (88), unadjusted; Allen 6.0 dry (94) vs 6.9 rain (12, small). Direction agrees, but the story cites the wrong evidence, and the generator computes none of this.
   Replace with: "Will the rain change it? [Part 4](bills-chiefs-rain-and-wind.html) found NFL teams run more in the rain, but that counted designed runs by everyone, mostly running backs, and no scrambles. It doesn't tell us about quarterbacks, so the 80% leaves the weather out."
   (Alternative: compute a QB-run rain split in the generator and cite it, with the small-sample label for Allen.)

3. **Wind direction.** "a northeast wind of 10-13 mph". Saved file `hourly_et`: 8 p.m. NE, 9 p.m. **E**, 10 p.m. NE, 11 p.m. NE. "northeast" is also a hard-coded word in the generator.
   Replace with: "a northeast to east wind of 10-13 mph" (better: derive from `h[3]` in the file).

4. **Tie handling in the backtest numbers.** The test set is **659** games (2024 wk2-18, 2025 wk2-18, 2026 wk2-11), with **2 ties** (2025_04_GB_DAL 40-40, 2026_05_NYG_WAS 27-27).
   - Body: "Its favorite won 64% of 657 games." is computed correctly (ties excluded, 419/657 = 63.8%), but the exclusion is silent and "favorite" reads as betting language.
     Replace with: "The team it gave the better chance won 64% of the 657 games that didn't end in a tie."
   - Stat-heads: "win Brier 0.224 on 657 games" is mislabeled: the Brier is computed on all 659 (ties scored as 0.5). Value is 0.2237 with ties, 0.2243 without; both round to 0.224.
     Replace "win Brier 0.224 on 657 games (50/50 guess = 0.250); favorite won 63.8%." with "win Brier 0.224 on 659 games, ties scored as half (50/50 guess = 0.250); the side given more than 50% won 63.8% of the 657 games without a tie."
   - Note: one test game has p exactly 0.500 and is counted as an away "favorite" by `g.p > 0.5`; flipping it moves 63.8% to 63.6% or 63.9%, so 64% holds.

5. **Small-sample label on Call 2.** 80% rests on 10 games. Add after "He did it in 8 of 10.": "Ten games is a small sample." (self-check rule: a handful of games gets a label).

## Should-fix (code hygiene, not accuracy today)

- Typed words not asserted in the generator: "A gap of under two points" (assert `pb - pk < 2`), "The two times he didn't" (assert `len(low) == 2` or derive), "northeast", "from 8 to 11 p.m.", "7 p.m. to 1 a.m.", "since 2018", "2024, 2025 and 2026 so far" (derive from the `test` dict). All are true for the pinned data.
- "In games like it since 2018 ... against 22.9 for the same teams in dry games": 22.9 is an expectation built from those offenses' and defenses' dry-game averages (part 4), not the same teams' actual dry games. Same wording as part 4's hero, so consistent, but more exact: "against the 22.9 we'd expect from the same offenses and defenses in dry games."
- Ledger P0024 grades a tie as a miss; `win_chance` gives a 50/50 split to the |d| <= 0.5 band (about 3.4% of mass: 0.5505 split vs 0.5333 strict). Counting that band as a loss would give 53%. It is the logged method, it's disclosed in stat-heads, and overtime breaks most regulation ties, so leave it. Don't describe the 55% anywhere as the chance under the Ledger's tie-is-a-miss grading.

## Verified independently (own code: /tmp/qa/pm.py, /tmp/qa/qbrain.py, ad hoc queries)

- Points model reimplemented from clean_drives + raw_schedules: coef (7.0685, 0.6785, 1.4527), 2,494 training team-games. BUF 25.606, KC 23.862 (story 25.6 / 23.9; 25.61 / 23.86). Win chance 0.5505 -> 55%, matches P0024 = 0.55.
- Backtest: per-season MAE 7.440 / 7.516 / 7.441 (2024/25/26), mean 7.466 -> 7.5 (pooled 7.470); league-average baseline 7.904 -> 7.9; within 7 pooled 55.16% -> 55.2%; Brier 0.2237; favorite 419/657 = 63.8%. Test seasons out of sample (fit 2019-23; K/keep tuned 2019-22); ratings use only prior weeks. No leakage found.
- Allen (gsis 00-0034857 via pfr AlleJo02): runs by week 5, 11, 7, 5, 10, 2, 7, 5, 4, 0 (wk 7 bye); 8 of 10 with 4+; median 5; low games wk 6 LV (2), wk 11 MIA (0). `rush` and `qb_scramble` are disjoint in 2026 (no double count). Second way: weekly box-score carries minus Allen kneels = 5, 11, 7, 5, 10, 2, 7, 5, 4 for wks 1-10 (box scores not loaded for wk 11); wk 11 play-by-play has no Allen run (one K.Allen kneel). Consistent with the wk 11 lab story ("didn't run once"). All 10 games have 15+ Allen plays (26-48).
- Weather vs saved file (updateTime 2026-11-26T14:57:46Z = 9:57 a.m. ET, "Thursday morning" OK): temps 37-38, wind 10-13 mph, rain chance 88-100, gusts 01-04 UTC (8-11 p.m. ET) 35/32/30/29 -> 29-35, rain 0.66 in. "Wetter than Wednesday": Wednesday file 00-06 UTC QPF 8.89 mm = 0.35 in, light rain, max game-window gust 29 mph. Gust km/h values are not kept in the Thursday file (only converted mph), so the conversion can't be re-checked from it.
- Part 4: 18.3 / 22.9 match its hero JSON and story (rain + 10+ mph wind, 44 games, 2018-2026 wk 10). Thursday's forecast wind 10-13 still fits that group.
- Ledger: P0024 0.55 points-win-v0.1, P0025 0.80 season-rate-v0, both 2026-11-25T14:44:10Z, before kickoff 2026-11-27T01:20Z. Story wording matches claim_text.
- Chart viewed: title states the finding, scrambles striped, 4-run line, source + sample in footer; reads on its own. Hero JSON and site dek numbers match.
- Pre-check reproduction (not the stage-4 check): clean clone of f0a34f9c with data symlinked; generator ran in 23 s; .md, .png and hero JSON byte-identical.
