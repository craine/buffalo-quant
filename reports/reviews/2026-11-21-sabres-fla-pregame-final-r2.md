# Final check: 2026-11-21-sabres-fla-pregame (stage 4)

Text checked: md sha256 712b924cf96b3dd91c92c86905a1a8f193c54b4185035cd2bfd54f2a25849342, plus hero JSON, card and three PNGs.

**Passes.**

Diff against the round-1 text: lines 40, 42, 51, 79-81, 83-84 of the md; hero big[1]; card dek; chart 1 layout; chart 2 ticks; chart 3 title.
Each changed sentence was checked against my independent numbers (see the round-2 quant report): Thursday PP goals 2; Reinhart 12 goals,
11.25 in chances, most on FLA; attack 3.1 / allowed 3.2; OT share 55% from 2023-24 and 2024-25; caution 54.9/52.2 (1,312) and 54.4/52.2 (358);
model-test 60-65% bin won 62% (231); hero 1st of 32. No number or claim elsewhere was touched. The edits added no new claims and no betting
words or jargon. Clean-copy run of `src/reports/sabres_pregame_fla.py` reproduces the md, hero and all three PNGs byte-identically.
Ledger logger unchanged (0.37, nhl-game-v0.1, ratings before 2026-11-20) and matches the story; it must be run before 23:00 UTC Nov. 21.
