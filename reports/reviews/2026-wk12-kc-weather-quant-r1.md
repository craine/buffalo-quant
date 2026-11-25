# Quant review: 2026-wk12-kc-weather (stage 2)

**Verdict: FAIL (publish with fixes).** The core finding holds under every check I ran. The fixes are about disclosure, one fragile number, and overclaims.

## Reproduction
- A clean-copy re-run (no .git or data; DB linked) reproduces the md, hero JSON and PNG byte-identically.
- The 2026 fingerprint (25,946 plays, EPA sum -222.5969) holds.

## Independent re-derivation (my own SQL and pandas, not the writer's functions)
- **Outdoor/open games, 2018 to 2026 Wk10:** 1,591 games: dry 1,461, rain 107, snow 16, unsure 7.
- **Dry games:** 22.68 points, completion 0.6465, 20+ rate 0.0817, runs 23.98.
- **Rain games:** 19.03 points, completion 0.6101, 20+ rate 0.0746, runs 25.78.
- **Rain with 10+ mph wind:** 44 games, 18.34 points, completion 0.611, runs 26.22, 34.6 dropbacks.
- **Same-team expectation:** rain 22.43, rain with wind 22.87.
- **Fixed-effects OLS on points:** rain -3.416 (naive SE 0.71, team rows), wind -0.155 per mph (SE 0.038). Runs +1.54 in rain. n = 3,120 team-games.
- **Josh Allen:** 13 rain games, completion 0.578 vs 0.647 dry, same-season expectation 0.651. Rain games: 2018 BAL, 2018 DET, 2019 PHI, 2020 KC, 2020 NE, 2021 HOU, 2022 BAL, 2022 NYJ, 2023 NYJ, 2023 WAS, 2023 PHI, 2023 DAL, 2025 PHI.
- **Mahomes:** 2 rain starts (2020 at BUF; 2023_09_MIA_KC).
- **2020_06_KC_BUF:** played 2020-10-19, KC won 26-17, KC 46 carries for 245 yards (box-score carries, including kneels). Weather note: "Cloudy with showers".
- **Later KC games at Orchard Park:** 2023 divisional (Jan. 21, 2024) "Cloudy", 2024 Wk11 "Cloudy", 2025 Wk9 "Fair". So "the last time … in the rain in Orchard Park" holds, playoffs included.
- **Buffalo 2026 ranks:** 20th / 27th, and KC 5th (same as part 3).
- **"One fewer 20-yard pass every other game":** 2 × 34.6 × (0.0814 − 0.0735) = 0.55. Checks out.

## Question 1: the weather sorting
- **Rain list:** I read all 107 rain notes. Every one describes rain, showers or drizzle at the game ("Rain" ×70, "Light rain" ×8, "Steady rain from Hurricane Isaias", etc.). No false positives.
- **Unsure list:** the 7 unsure games are:
  - "Scattered Showers"
  - "Rain Chance 40%"
  - "50% change of rain"
  - "Light Rain Forecasted"
  - "Threat of rain …"
  - "Cloudy with more rain possible"
  - "chance of rain"

  Leaving them out is right. "more rain possible" implies it had already rained, but one game won't move anything. The regex also matches "change of"; the stat-heads list leaves that out (polish).
- **Dry list problem (must-fix):** 131 "dry" games have no conditions text: 129 have only "Temp/Humidity/Wind" and 2 have no weather note at all. They're counted as dry by default.
  - By season: 6, 10, 4, 14, 17, 20, 20, 25, 15.
  - That's 9% of the dry group. They score 21.8 per team vs 22.8 for dry games with a note.
  - Excluding them, rain is 19.0 vs an expected 22.27 (3.2 fewer), and rain with wind is 18.3 vs 22.64 (4.3 fewer).
  - The finding holds, but the body says games were sorted "by the weather recorded for it", and for these 131 no weather was recorded.
- **Wind fill:** the `wind` column equals `raw_schedules.wind` exactly (1,367 games), so the 85% agreement is column vs text. In the disagreements, the column often reads **0** where the text says 10 or 14 mph:
  - 2021_17_DET_SEA: 0 vs 10
  - 2021_18_WAS_NYG: 0 vs 14
  - 2022_17_DAL_TEN: 4 vs 10

  A 0 there looks like "missing" coded as zero.
  - Filling from the text only when the column is empty is reasonable. But the 10+ mph rain group is 44 games with the column first and 47 with the text first.
  - With the text first: 18.8 vs 22.8 expected, a gap of 4.0, not 4.6.
  - So "about 4½ fewer" in rain with wind ranges from 4.0 to 4.6 depending on the wind source and the no-note games. It is fragile.
  - The text regex also misses "10MPH mph" and ranges like "10-15 mph" (both become NaN), but no rain game is affected.

## Question 2: the forecast copy
- **Live check failed:** I could not reach api.weather.gov. The agent proxy returns 403 on CONNECT, and WebFetch is refused by robots.txt, so the copy is **unverified against the live source**. Per CLAUDE.md, say so in the PR. The forecast will also have updated since 11:57Z.
- **Internal checks pass:**
  - **Time zones:** the hourly rows are local (-05:00), and the 8-11 p.m. rows are all on 2026-11-26 (the file holds only 7 p.m. to midnight Nov. 26). Gusts are looked up at the matching UTC hour:
    - 8 p.m. = 01Z: 46.30 km/h = 28.8 mph → 29
    - 9 p.m. = 02Z: 44.448 → 27.6 → 28
    - 10 p.m. = 03Z: 40.744 → 25.3 → 25
    - 11 p.m. = 04Z: 37.04 → 23.0 → 23

    km/h ÷ 1.609344 is the right conversion.
  - **Rain:** the 00-06Z precipitation is 8.89 mm = 0.350 in, and 7 p.m.-1 a.m. EST is correct.
  - **Fragile lookup:** the gust lookup keys only on each period's start hour. It works here only because the 22Z PT2H period isn't needed. If a future copy has a multi-hour gust period over game time, it raises a KeyError rather than giving a wrong number, so it's safe.
  - **File note:** it says "Copied verbatim from api.weather.gov", but the file is an extract (selected fields, rearranged into arrays). Reword to "Extracted from …" (polish; not story text).

## Question 3: overclaims and "3 to 4" / "about 3½"
- **The three checks:** raw 3.7, same-team 3.4, regression 3.4. Dropping the 131 no-note games gives 3.2. "3 to 4" in the headline and "about 3½" in the lead are consistent with all of them.
- **Must-fix, per team:** "3 to 4 points a game" in the headline and chart title reads to a fan as the game's combined score. It is points **per team**: two teams lose about 7 together. Say "a team".
- **Causation:** weather isn't chosen by teams, and the regression holds each team's season fixed, so "rain has cost" is defensible. But several lines overstate the passing effect, which is small: about 0.6 to 0.7 fewer 20-yard plays per 100 dropbacks, roughly one fewer per two games for both teams together.
  - Lead: "Rain takes away some of the long passes …" is OK.
  - Hero: "Rain takes away long passes" overclaims.
  - Body: "Rain helps with the first" overclaims.
  - Thursday section: "the rain should help Buffalo against big plays" overclaims.

## Question 4: betting framing and predictions
- No betting terms. No game total is projected.
- "Expect a lower-scoring game than either offense usually plays …" is an unlogged prediction: brand rule 2 says every public prediction is logged with a probability. It also sits next to totals talk. Reword it as a description of past rain games (see must-fix 5), or log a Ledger call.

## Must-fixes (exact text → replacement)
1. **Headline:**
   - "Rain has cost NFL offenses 3 to 4 points a game, and it brings on the run"
   - → "Rain has cost NFL teams 3 to 4 points each, and it brings on the run"
   - The chart title needs the same change: "Rain has cost NFL offenses 3 to 4 points a game, and teams run more" → "Rain has cost NFL teams 3 to 4 points each, and they run more".
2. **Sorting sentence:**
   - "We sorted every regular-season outdoor game since 2018 by the weather recorded for it: 1,461 dry, 107 with rain, and a handful with snow or only a chance of rain (left out)."
   - → "We sorted every regular-season outdoor game since 2018 by the weather note recorded for it: 1,461 dry, 107 with rain, and 23 with snow or only a chance of rain (left out). In 131 of the dry games the note doesn't describe conditions at all, so we counted them as dry."
   - Compute 23 and 131 in the generator. Add to stat-heads the result without those games: 19.0 vs 22.3 expected; rain with wind 18.3 vs 22.6.
3. **Rain with wind:**
   - "In rain with wind, 18.3 when we'd expect 22.9, about 4½ fewer."
   - → "In rain with wind, 18.3 when we'd expect 22.9."
   - Add to stat-heads, computed: "Wind source matters: reading the note's wind before the column gives 47 games, 18.8 vs 22.8."
4. **Hero note:**
   - "Rain takes away long passes and brings more runs."
   - → "Rain has meant a few fewer long passes and more runs."
5. **What it means Thursday:**
   - "Expect a lower-scoring game than either offense usually plays, more runs, and fewer long passes on both sides."
   - → "In past games like this one, teams scored less than usual, ran more and hit a few fewer long passes."
6. **Thursday section:**
   - "The other two do: the rain should help Buffalo against big plays, and put more weight on its run defense."
   - → "The other two do: rain has meant slightly fewer big plays, and more weight on the run defense."
7. **Buffalo's two weak spots:**
   - "Rain helps with the first and leans on the second."
   - → "Rain helps a little with the first and leans on the second."

## Polish
- "gusts near 29 mph" → "gusts up to 29 mph". The gusts are 23-29, easing through the night.
- "For two teams throwing about 35 times each" → "For two teams dropping back about 35 times each". The 34.6 figure counts dropbacks.
- Add "change of" to the stat-heads list of forecast words.
- The note in the saved forecast file: "Copied verbatim" → "Extracted".
- The naive OLS SE treats the two team rows of a game as independent. Clustering by game would be more honest if an SE is ever published.
