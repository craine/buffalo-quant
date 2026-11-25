# Quant review, round 2: 2026-wk12-kc-weather (stage 2)

**Verdict: FAIL. One small must-fix, in the stat-heads section.** Everything else passes. Round 1 is saved as -quant-r1.md.

## Reproduction
I extracted `git archive HEAD` into a clean directory, linked the DB and re-ran the generator. The md, hero JSON and PNG are byte-identical to the committed files.

## Round-1 fixes, re-derived independently
- **Counts:** 131 dry games with no conditions text (129 have temp/humidity/wind only, 2 have no note). 23 left out (16 snow, 7 unsure).
- **Dry baseline without those 131 games:** rain 19.03 vs 22.27 expected; rain + wind 18.34 vs 22.64. Story says 22.3 / 22.6. ✓
- **Note-first wind:** 47 games, 18.83 vs 22.80. Story says 18.8 / 22.8. ✓
- **All 11 must-fixes are in as worded:**
  - Per-team wording is in the headline, chart title and lead.
  - "a few fewer long passes" is in the hero and card.
  - The Thursday section no longer predicts ("In past games like this one …"). There is no unlogged prediction and no game-total framing.
  - "about 4½" is gone.
  - "helps a little" is in the weak-spots section.
  - Dropback is defined.
- **Polish is applied:**
  - "gusts up to 29"
  - "dropping back about 35 times"
  - "change of" listed in stat-heads
  - forecast file note says "Extracted"
- **Unchanged numbers still match round 1:** 19.0 / 22.7 / 22.4 / 22.9, OLS -3.42, Allen, Mahomes, the 2020 game, and the ranks.
- **Chart:** I opened the PNG. The title matches the headline.

## Forecast source
The coordinator says the copy was fetched through Chrome from api.weather.gov at 14:30 UTC (updateTime 11:57:35Z). I still can't reach that host from here (proxy 403, robots.txt), so I can't confirm the values myself. The internal checks from round 1 still hold: time zones, km/h-to-mph conversion, and the 00-06Z rain total. Record the Chrome fetch in the PR, as planned.

## Must-fix
In "For the stat-heads", the wind bullet makes a claim no code computes, and it overstates.
- Of the 1,337 games with both a column value and a note value, 194 disagree by more than 1 mph. In 21 of those the column reads 0, and in only 5 does the note give 10+ mph. "Often" and "10-14 mph" aren't supported.
- **Now:** "The column often reads 0 where the note gives 10-14 mph; reading the note first makes the rain + wind 10+ group 47 games, 18.8 vs 22.8 expected."
- **Replace:** "Where they disagree, the column sometimes reads 0 when the note gives a real wind; reading the note first makes the rain + wind 10+ group 47 games, 18.8 vs 22.8 expected."
- Alternatively, have the generator compute the counts (21 of 194 disagreements read 0) and state those.
