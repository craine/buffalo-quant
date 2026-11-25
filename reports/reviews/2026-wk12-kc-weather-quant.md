# Quant review, round 4 (re-opened by the final check): 2026-wk12-kc-weather

**Verdict: FAIL. One must-fix.**

The new "What it means Thursday" text (commit 44569e55) says: "Pressure doesn't depend on the weather. The other two do."
- No code supports this. Part 4 never measures pressure.
- I checked it against the same games. PFR defensive pressures per dropback:
  - Dry games (1,461): 23.9 per 100
  - Rain games (107): 24.7 per 100
  - Same-team expectation for the rain games: 23.9 per 100
- So pressure was slightly higher in rain, not unaffected.
- I also missed the earlier version of this claim ("pressure, doesn't depend on the weather") in round 2. That was my error.

## Must-fix
- **Now:** "Pressure doesn't depend on the weather. The other two do. Rain has meant slightly fewer big plays, which helps a little where Buffalo ranks 20th. It has also meant more runs, which puts more weight on a run defense that ranks 27th."
- **Replace:** "Rain has meant slightly fewer big plays, which helps a little where Buffalo ranks 20th. It has also meant more runs, which puts more weight on a run defense that ranks 27th."
- **Alternative:** if the writer wants to keep a pressure line, compute it in the generator and assert it (rain 24.7 vs 23.9 expected per 100 dropbacks). Write something like "Rain hasn't cut down on pressure."

## Everything else in the change passes
- The part 3 link and slug resolve.
- "tended to do three things" matches part 3.
- The ranks 20th and 27th are computed.
- Clean `git archive HEAD` reproduction: md, hero JSON and PNG are byte-identical. The PNG matches `published_images.json` (208591…).
