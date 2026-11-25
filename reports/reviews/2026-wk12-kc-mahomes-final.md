# Final check: 2026-wk12-kc-mahomes (stage 4)

**Verdict: PASS.**

I reviewed every change since round 1 and everything those changes touch, on the current text.

## Reproduction and data pin
- The clean-copy re-run reproduces the md, hero JSON and PNG byte-identically.
- The fingerprint assertion matches my independent query (25,946 plays, EPA sum -222.5969).

## Changed numbers, each re-derived independently
- Buffalo: 27th against the run, 46% allowed (league 43%)
- KC: runs work 48% (5th)
- Low-scoring games: 35% vs 44%
- All three vs the other 47 games: 4-4 vs 25.0 points and 72%
- Run examples: 9% / 69% / 96% / 99%
- OLS: -2.26 / +3.25 / +2.47 / +0.92

## Changed wording
All 13 round-1 must-fixes are in, as worded in the round-1 reports. None introduces a new claim without code behind it.

## Consistency across outputs
The hero JSON, the card dek in `src/site/build.py` and the chart panel all match the text.

## Open items (not blocking)
- Extend the fingerprint to 2023-25 play-by-play and to the PFR/FTN inputs.
- Editor polish 1-3.
- Freeze the PNG with `scripts/freeze_images.py` at publish.

If the writer applies editor polish 2 (chart footer), the PNG changes and needs this final check again. Polish 1 or 3 changes the md, so the recorded hash would also need re-checking.
