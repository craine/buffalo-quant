# Editor re-review, round 3: Bills at Jets, week 10 (text sha256 a9078ec040c0...)

## One-sentence version
"We give the Bills a 75% chance to win at MetLife, about 30 to 22, and the place they win it is through the air against the Jets' 7th-worst pass defense." The lead still says this.

## Verdict: ready (PASS)

I checked the text and the diff against HEAD~1. All of the round-2 fixes are in:
- **Ladder note:** reads "still in the ladder above but aren't logged. The whole middle of the ladder has the same issue". The false "flagged" is gone.
- **Duplicate scoreboard disclaimer:** cut. The line now opens "A team's runs 'lose points' if ...".
- **Opening:** "We grade every play in points, though not scoreboard points: ...". The real Allen example to Ty Johnson follows it.
- **The 0.26 vs 0.27 shift:** now explained ("counts every game equally instead of every play").
- **Tie footnote:** removed.
- **Ledger line:** "Logged ... on Nov. 13 at 7:54 p.m. ET, before kickoff. All 5 calls ...". This matches ledger/ P0012-P0016, created 2026-11-14T00:54:53Z (7:54 p.m. EST, Nov. 13). There are five calls, all before the 2026-11-15 18:00Z kickoff, and the probabilities match the table (75/80/55/66/75).

## Notes for the Quant / final check (not editor blockers)
- **Ties.** With the footnote gone, the 63% (a tie counts as a miss) and the chart footer ("Ties count as half a win") are no longer contrasted in the text. Line 100 still states the half-win rule for the 74%. This is fine for a fan; the Quant can confirm the 63% still reads correctly on its own.
- **P0012 wording.** The Ledger claim reads "Bills beat the Jets (any result; a tie counts as a miss)". The story's table says "Bills win (overtime counts; a tie counts as a miss)". The meaning is the same, but the self-check asks for exact wording, so the final check should decide.
- **Line wrap.** Line 14-15 wraps awkwardly in the markdown ("into\npoints. Last week at Minnesota,\nJosh"). It renders as one paragraph, so it's cosmetic only.
