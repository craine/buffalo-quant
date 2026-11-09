# Quant final check (stage 4, second look): Week 9 part 3

Reviewed: the working tree in /home/claude/bq-a (branch wk09-part3). I didn't run the logger and didn't edit any repo files.

## Verdict: PASS. Ready to publish.

All four fixes are in and correct, and neither chart is clipped. I re-ran the generator in a scratch copy of the repo (same database). It reproduces the committed reports/2026-wk09-prediction.md and its hero JSON byte for byte, so the review gate's record will match the text that publishes.

## The four fixes

1. **Win-test chart title** now reads "In close calls like Monday's, we said 55% and the team we leaned to won 56%". It fits on one line and nothing is cut off. The numbers are correct: 306 games, said 54.9%, won 56.4%. One cosmetic note: the final "%" sits right at the right margin. It isn't clipped, but if you want breathing room, trim a word (e.g. drop "like Monday's").
2. **Calls chart title** now reads "Closest: who wins (53%). Surest: Vikings' runs lose points (81%)". It fits, with nothing clipped, and the direction is now clear. The numbers are correct: the win call is closest to 50/50 (53.0%), and the Vikings' runs call is the surest (81.0%).
3. **10-point rung:** "where the edge is under one point (92% each, rounded)" is accurate. The unrounded figures are 92.26% vs. 91.54%, a 0.72-point gap. The "1 to 3 percentage points" range for the other rungs still holds.
4. **Smaller wording fixes:**
   - The lead now says "the same edge gives the Bills a 53% chance to win", which is accurate (0.5305).
   - The hero JSON now says "the team it leaned to".
   - The blank line in the stat-heads section is gone, so the list is one list again.

Nothing else in the story changed. All numbers checked in the previous round still stand.
