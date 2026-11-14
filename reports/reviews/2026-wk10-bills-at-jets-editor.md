# Editor re-review: Bills at Jets, week 10 (text sha256 ff02a816ce87...)

## One-sentence version
"We give the Bills a 75% chance to win at MetLife, about 30 to 22, and the place they win it is through the air against the Jets' 7th-worst pass defense." The lead still says this.

## Verdict: needs edits (FAIL). These are four small text-only fixes, and none needs a new number.

Most of round 1 landed well. The headline now matches the lead. The Allen example makes "points" concrete, which was the hardest part. The plain decimals, the 80% check, the explanation of the Jets' blended numbers, "tilt", the 70%+ tie to Sunday, the section order and "our average miss" all read cleanly. The charts pass: the win-test chart now says "Likely / Very likely" and "the likelier team", and the calls footer carries its sample sizes. No betting language remains.

## Required (most important first)

1. **The ladder note says the chances are "flagged", but nothing in the ladder is.** The table and chart show 85% and 58% at 20 points with no mark, so a fan will look for a flag and find none.
   Replace `We haven't fixed it yet, so they're still shown in the ladder, flagged, but not logged until fixed. The ladder has the same issue:`
   with `We haven't fixed it yet, so they're still in the ladder above but aren't logged. The whole middle of the ladder has the same issue:`
   (Alternatively, actually mark the 20-point row in the table and chart.)

2. **The "these aren't scoreboard points" line wasn't cut, so it now appears twice** (lines 14 and 87).
   Replace `What "gain points" and "lose points" mean: these aren't scoreboard points. A team's runs "lose points" if` with `A team's runs "lose points" if`.

3. **The section opens on a negation before "points" has come up.** Line 14 starts with "These aren't scoreboard points," but the reader has seen no "points" to contrast with yet.
   Replace `These aren't scoreboard points. Every play moves a drive closer to scoring or further away, and we turn that into points.`
   with `We grade every play in points, though not scoreboard points: every play moves a drive closer to scoring or further away, and we turn that into points.`

4. **"T. Johnson" reads like a data feed.** Use the receiver's full name, checked against the gsis id in the roster, not guessed.

## Recommended (not blocking)

5. **Two numbers for the same thing, one line apart.** The Bills are at 0.26 a play for the season, then "about 0.27" in a typical game, and the Jets go from 0.16 to 0.19. Say why:
   replace `Our matchup model averages those game by game.` with `Our matchup model counts every game equally instead of every play, so the numbers shift a little.`
6. **The tie footnote under the win-test chart is now redundant.** Line 100 already says ties count as half for the 74%. Cut `*The chart counts a tied game as half a win; the 63% above counts it as a miss.*`, or keep it only if the Quant wants the 63% caveat.
