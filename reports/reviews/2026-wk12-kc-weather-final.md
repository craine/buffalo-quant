# Final check: 2026-wk12-kc-weather (stage 4)

**Verdict: PASS.**

## Reproduction
- The committed text (HEAD 6f614df7) reproduces byte-identically from a clean `git archive`: md, hero JSON and PNG.
- The 2026 play-by-play fingerprint assertion holds.

## Changes since stage 2-3 began, all re-checked
- **Must-fixes:** the 11 round-1 must-fixes and the round-2 wind-bullet fix are all in.
- **Numbers re-derived independently:**
  - 131 no-note dry games; 23 left out
  - Baseline without the no-note games: 22.3 / 22.6
  - Note-first wind: 47 games, 18.8 vs 22.8
  - Wind disagreements: 1,337 / 194 / 21
- **Unchanged numbers still match:** 19.0 / 22.7 / 22.4 / 22.9, OLS -3.42 and -0.155, Allen 13 games at .578 vs .651, Mahomes 2, the 2020 game (46 carries, 245 yards, 26-17), ranks 20 / 27 / 5.
- **Consistency:** the headline, lead, hero, card dek and chart agree (per team, 3 to 4 / about 3½, 27th).
- **Brand rules:** no unlogged prediction, no betting framing.

## Open items (not blocking)
- The forecast values were checked for internal consistency only from here: time zone, km/h-to-mph, rain total. Note the coordinator's live Chrome fetch from api.weather.gov in the PR.
- Freeze the PNG with `scripts/freeze_images.py` at publish.
