# Quant re-check (sha256 07a7794d6267...)

**Verdict: PASS.** The diff from HEAD~1 changes two lines of the story. The generator template changed the same two lines, so a re-run reproduces the text. The hero JSON and dek are unchanged.

1. Oct 8: "still lost 4-0". Raw: Buffalo at home 0, Dallas 4. Chances 2.57 vs 2.11 are unchanged, so 2.6 vs 2.1 still holds. OK.
2. The 2.99 vs 2.97 sentence now gives the correct reason: the model works on chances before the season rescale (2.971 / 0.9922 = 2.994). OK.

Nothing else changed. Every other number is as verified in the previous two reviews:
- the prediction (62/38), which matches Ledger P0011 (0.38, logged 2026-11-14T00:05:13Z, before puck drop)
- the team table and ranks
- the bounce-back figures and the out-of-sample check
- the goals-allowed gap
- the goalie table
- the calibration bin
No betting language, and no jargon in the body.
