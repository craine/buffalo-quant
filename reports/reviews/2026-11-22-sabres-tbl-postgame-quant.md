# Quant review: 2026-11-22-sabres-tbl-postgame (stage 2, round 2)

Text: md sha256 8f3cced10a379d538e4099c277b14717f1c07bdaa99769d13cf3e46a9eec2689. Round 1: -quant-r1.md (every number verified there still applies to unchanged lines).

**Verdict: publish (pass).**

- Must-fix 1 resolved. Key 2 stays "Half". The comparison now uses Buffalo's actual spot: 42% of 1,286. That matches my independent
  build (0.4230, n 1,286). The generator's definition matches mine: game-level running totals relative to the first scorer, periods < 5
  (no shootout). The "hit all three" line is out of the body. Stat-heads gives 0.600 of 1,856, of which 570 never gave the lead back
  and all won, plus all three keys (first-goal definition) 0.781 of 2,063. All match my numbers, and the generator asserts them.
- Trip record 2-3-1 (W CHI OTL, DAL L, PHI L, WSH W, FLA L, TBL W) matches raw_nhl_games and is asserted. 10-10-4 (24 points) unchanged.
- "7 p.m." now comes from strftime and is correct (2026-11-25 00:00 UTC = Wednesday 7 p.m. ET).
- Key 1 row: 7 power-play shots worth 0.70. Correct. Key 3 row: 2.6 vs 2.4. Correct.
- "0.6 goals worse than average": season -0.57. Correct. "Small sample" label on 6 of 14 is fine.
- Nov. 11 sentence: 3.56 / 3.59, rounding to 3.6 each; lost 8-3. Correct.
- Chart: only the footer changed ("Leaves out Zach Benson's empty-net goal."). Everything else is identical to round 1. Shot counts 37/50 correct.
- Hero and card unchanged and consistent.
- No betting language, no jargon in the body, no penalty counts.
- Clean copy (git archive HEAD + generator, pins.py, grades.csv, same DB) reproduces the md, hero and PNG byte-identically.
