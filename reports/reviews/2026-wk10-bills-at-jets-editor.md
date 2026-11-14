# Editor review: Bills at Jets, week 10 prediction (reports/2026-wk10-bills-at-jets.md)

Generator: src/reports/wk10_prediction.py. Charts, hero JSON and dek (src/site/build.py, slug bills-jets-prediction) also reviewed.

## One-sentence version (radio line)

"We give the Bills a 75% chance to win at MetLife, about 30 to 22, and the place they win it is through the air against the Jets' 7th-worst pass defense."

The lead says this. Good. The one-combined-story format beats last week's three parts: 1,386 words against 1,923 for part 3 alone, and the most interesting thing (the passing mismatch) now comes first.

## Verdict: needs edits (FAIL until fix 1 is done; the rest are small)

## Required fixes, most important first

### 1. "Points" per pass play has no real example, and the explanation is split across the story
The story's sharpest call (80%, the chart title and the hero card) rests on "points per pass play." The only explanation at first use is one abstract sentence (gen line 235): "Every play moves a drive closer to scoring or further away; we measure that in points." The sentence that tells fans these aren't scoreboard points comes 50 lines later (gen line 275). The fan rule calls for a real computed example, and this explanation has none. **The writer needs to compute new numbers for this:** one or two real Bills 2026 plays with their point value (for example, a completion that gained X yards on 3rd-and-long was worth +N; a sack was worth -N). I am not supplying numbers.

- Replace (gen 235) `Every play moves a drive closer to scoring or further away; we measure that in points.`
  with `These aren't scoreboard points. Every play moves a drive closer to scoring or further away, and we turn that into points: [REAL EXAMPLE A: e.g. "Allen's N-yard completion on 3rd-and-N against X was worth +N.NN"]; [REAL EXAMPLE B: e.g. "a sack on 2nd-and-10 cost about N.NN"]. Add up every pass play and divide by how many there were.`
- Then cut the first clause of gen 275: replace `What "gain points" and "lose points" mean: these aren't scoreboard points. A team's runs "lose points" if` with `A team's runs "lose points" if`.

### 2. The numbers look like stat lines: drop the plus signs and "dropbacks"
`+0.25`, `+0.16`, `+0.05` and `+0.23` read like a box score. "Dropbacks" is a scout's word.
- Gen 236-237: replace `{R['buf_off']:+.2f} points each on average` with `{R['buf_off']:.2f} points each on average` (and the same for `opp_def`, `lg` and the +0.23 in the next paragraph: use `.2f`, not `+.2f`).
- Replace `over {R['n_off']} dropbacks` with `over {R['n_off']} pass plays (sacks and scrambles count)`, and `over {R['n_def']} dropbacks` with `over {R['n_def']} pass plays`.

### 3. The headline contradicts the lead
The headline says "The NFL's best offense," and the next sentence says the passing game is 4th-best. A fan reads that as a mistake: the "best" is points per drive, and that isn't explained until the last third of the story. Headline (gen 222), and keep the dek consistent:
- Replace `The NFL's best offense gets one of its leakiest pass defenses`
  with `Buffalo's passing game gets one of the NFL's leakiest pass defenses`.
  (Or, if you want to keep "best offense," use `The NFL's highest-scoring offense per drive`, which the Quant should confirm.)

### 4. The "Is 80% too bold?" paragraph is hard to follow
Replace `On 990 past team games (2023-2025) it hadn't seen, when it gave a passing game 70% or more, it said 75% on average and it happened 78% of the time (134 games).`
with `We tested it on 990 past team games from 2023-2025 that it had never seen. In the 134 where it gave a passing game 70% or more, it said 75% on average, and the passing game came out ahead 78% of the time.`

### 5. The Jets' numbers change mid-story with no warning
The matchup section says the Jets score 1.92 per drive and the Bills allow 2.10. "Where the 30 comes from" then says 1.81 and 2.08. A careful fan sees a contradiction.
- Replace `The Jets go through the same steps from the other direction: an offense at 1.81 per drive against a Bills defense at 2.08, plus the home bump.`
  with `The Jets go through the same steps from the other direction. After mixing in last season, their offense rates 1.81 per drive against a Bills defense at 2.08, plus the home bump.`

### 6. "Favor" in step 3 (betting-adjacent wording)
Replace `Both sides favor Buffalo, which leaves about 3.07 points per drive.` with `Both sides tilt toward Buffalo: their offense is well above average and the Jets' defense is below it, which leaves about 3.07 points per drive.`

## Recommended (not blocking)

7. **Tie the win check to Sunday's 75%.** The win-test chart already shows the most useful fact: when the model gave a team 70% or more, it said 75% and the team won 74% (102 games, ties as half). The text never says this. After the 63%/52% sentence (gen 300), add: `And when it was as sure as it is about Sunday (70% or more), it said 75% and that team won 74% of the time (102 games; ties count as half).` Then the tie footnote under the chart can go. The Quant should confirm the figures against the chart data.
8. **"Lean" is sportsbook slang** ("my lean this week"). Replace `the team it leaned to` with `the team it gave the better chance`. In the win-test chart, change the bucket labels "Leans / Strong leans" to "Likely (60-70%) / Very likely (70%+)" and the legend to "Chance we gave the likelier team."
9. **Order.** "How a 30-point projection becomes 75%" explains the 30 before "Where the 30 comes from" does. Move "Where the 30 comes from" up to sit right after the ladder.
10. **Ambiguous "its."** Replace `(On games it had never seen, its average miss was 7.5 points.)` with `(On games the model had never seen, our average miss was 7.5 points.)`
11. **Step 4 jump.** "About 11 drives a game gets you to about 34," then 29.9 a sentence later. Replace `pulls extreme projections back toward normal` with `pulls extreme projections like this 34 back toward normal`.

## Charts
- **wk10-ladder.png:** Readable in 5 seconds. The title is the takeaway. The footer has the source and sample. OK.
- **wk10-calls.png:** The title is the takeaway ("Our surest call..."). The 50/50 line helps. The footer has no sample size: add "Matchup calls tested on 990 past team games; win chance on 632." OK otherwise.
- **wk10-win-test.png:** Clear, with a good title. See item 8 for the "leans" labels. The text should use it (item 7).
- **Hero card:** Good. 30/22 rounds 29.9/22.1 cleanly, and "what it said / what happened" (75% / 78%) is the right explainer.
- **Dek:** Fine. Keep it consistent with the headline if fix 3 is made ("one of the NFL's leakiest pass defenses" already matches).

## Betting language
No odds, spreads or picks. The only betting-adjacent words are "favor" (fix 6) and "lean/leaned" (item 8). The stat-heads section is properly fenced, and the body has no EPA, Brier or calibration terms.
