# Editor review, stage 3: reports/2026-11-10-hooker-trade.md

## Verdict: NEEDS EDITS (not a rewrite)

The story makes sense, and the interception history and the 5.5 to 2.5 example are strong. Four things stand in the way of a regular fan:
1. The headline doesn't state the finding, and the lead runs four sentences.
2. "Per target" appears all through the body and is never explained.
3. The body never says where the 0.27 score comes from (the source, the math, how we checked).
4. The site dek says interceptions are "the shakiest part of a safety's game," which the story's own data contradicts. Completions allowed (0.11) and yards allowed (0.18) carry over less.

The body also says "The bet is on this season," which is betting language.

## The one-sentence version

"The Bills paid a second-round pick for a safety tied for the NFL lead with five interceptions, but big interception years don't repeat: safeties who had five or more averaged about two and a half the next season."

Right now this sentence is not the headline, and the lead only gets to it by implication ("Don't build on them"). The 2.5 number, the best fact in the story, doesn't show up until paragraph 4.

## Edits, most important first

### 1. Site dek is factually off (src/site/build.py, "bills-trade-amani-hooker")
Old: `Amani Hooker arrives tied for the NFL lead in interceptions, the shakiest part of a safety's game to count on. Behind them: average coverage this season, and better numbers than two of the Bills safeties he joins.`
New: `Amani Hooker arrives tied for the NFL lead with 5 interceptions. Don't count on that pace: safeties with five-interception years averaged about 2.5 the next season. Behind them: average coverage this season, and fewer yards allowed than two of the Bills safeties he joins.`
Why: In the story's own chart, interceptions (0.27) carry over about as well as tackling and better than both coverage numbers, so "shakiest" is wrong. The new version uses only numbers already in the story.

### 2. Headline: put the finding in it
Old: `# The Bills paid a second-round pick for Amani Hooker. Here's what they're actually getting`
New: `# The Bills paid a second-round pick for Amani Hooker's 5 interceptions. History says don't count on 5 more`

### 3. Lead: the radio sentence first, short sentences
Old:
`**Hooker arrives with 5 interceptions, tied with Xavier McKinney for the NFL lead. Don't build on them: for safeties, a big interception year tells you little about the next one. Behind the interceptions is a safety who has been about average in coverage this season and below average the three seasons before. Even so, he has allowed fewer yards per throw than two of the Bills safeties he joins.**`
New:
`**Hooker arrives with 5 interceptions, tied with Xavier McKinney for the NFL lead. Don't count on that pace: safeties who had five or more in a season averaged about 2.5 the next. Behind the interceptions is a safety who's been about average in coverage this season and below average the three seasons before. He has still given up fewer yards per throw than C.J. Gardner-Johnson or Damar Hamlin, two of the safeties he joins.**`
Why: The computed 2.5 is what a host can repeat. Naming Gardner-Johnson and Hamlin is clearer than "two of the Bills safeties" and is backed by the body.

### 4. Remove the betting metaphor (brand rule 1)
Old: `The bet is on this season and the two years left on his contract.`
New: `The Bills are paying for this season and the two years left on his contract.`

### 5. Add the missing "where the number comes from" paragraph (Writing for fans rule)
The body has the example (5.5 to 2.5) and the range (±0.1). It does not name the source, give the math in plain words, or say how we checked. Insert this after the paragraph that ends `interceptions scored 0.27.` and before the chart:
`How we got that score: from Pro Football Reference's play-by-play charting (via nflverse), we took each safety's rate in one season (interceptions per throw at him, for example) and set it beside his rate the next season, for all 318 pairs. If the players who were high one year were always high the next, the score would be 1. If the next year looked random, it would be 0. To check it, we re-ran the math 2,000 times, each time on a random reshuffle of the players. That's where the "give or take about 0.1" below comes from. The 5.5-to-2.5 drop is what a score of 0.27 looks like on the field: the next year lands much closer to average than to the big year.`
Note: "per throw at him" is the per-target rate. No new numbers (318 and 2,000 are already in the story).

### 6. Replace "target" in the body with "throw"
Define it once, then use "throw" everywhere in the body (stat-heads section can keep "target"):
- Old: `coverage scored lower: yards allowed per target 0.18, completions allowed 0.11.`
  New: `coverage scored lower: yards allowed per throw 0.18, completions allowed 0.11.`
- Old: `Passes thrown at Hooker have gained 8.3 yards per target this season\n(33 targets, a small sample), close to the average safety's 8.1 (31st of 58, 1st = fewest yards allowed).`
  New: `Passes thrown his way (the stat sheets call them "targets") have gained 8.3 yards per throw this season (33 throws, a small sample), close to the average safety's 8.1. That's 31st of 58 safeties, right in the middle.`
- Old: `Over 2023 to 2025 he allowed 9.1 per target, more than the average safety's 8.2 (57th of 76\nsafeties thrown at 60+ times). Last season alone he allowed 11.4, 58th of 66.`
  New: `Over 2023 to 2025 he allowed 9.1 yards per throw, more than the average safety's 8.2 (57th of 76 safeties thrown at 60+ times). Last season alone he allowed 11.4, 58th of 66.`
- Old: `As a group, Buffalo's safeties have allowed 9.7 yards per target this season`
  New: `As a group, Buffalo's safeties have allowed 9.7 yards per throw this season`
- Old: `That's 69 targets, a small sample,`
  New: `That's 69 throws, a small sample,`
- Old: `Cole Bishop has\nallowed 7.4 yards per target (31 targets), fewer than Hooker. C.J. Gardner-Johnson has allowed 10.4 (21\ntargets)`
  New: `Cole Bishop has allowed 7.4 yards per throw (31 throws), fewer than Hooker. C.J. Gardner-Johnson has allowed 10.4 (21 throws)`
- Old: `Damar Hamlin has allowed 13.2 (13 targets).`
  New: `Damar Hamlin has allowed 13.2 (13 throws).`
- Hero JSON bar label: `"Yards allowed per target"` -> `"Yards allowed per throw"`.

### 7. Shorter sentences that can be read aloud
- Old: `We looked at every safety who was thrown at 25 or more times in back-to-back seasons from 2018 to 2025 (318 pairs of seasons, 118 players) and asked: does a big interception year repeat? Mostly, no.`
  New: `We looked at every safety thrown at 25 or more times in back-to-back seasons from 2018 to 2025: 318 pairs of seasons from 118 players. Does a big interception year repeat? Mostly, no.`
- Old: `The 22 safeties who had five or more interceptions in a season averaged 5.5 that year and 2.5 the\nnext: much closer to the 1.7 the whole group averaged than to their big year.`
  New: `The 22 safeties with five or more interceptions in a season averaged 5.5 that year. The next year they averaged 2.5, much closer to the 1.7 the whole group averaged than to their big year.`
- Old: `With this few players, those scores could\neach be off by about 0.1 either way (the lines on the chart), so the honest reading is that interceptions and tackling carry over about equally,\nand only a little.`
  New: `With this few players, each score could be off by about 0.1 either way (the black lines on the chart). The honest reading: interceptions and tackling carry over about equally, and only a little.`
- Old: `This season Hooker has missed 3 of 55 tackle attempts (5.5%, a small\nsample), better than the average safety's 8.9% (tied for 16th fewest of 58 safeties thrown at 15+\ntimes).`
  New: `This season Hooker has missed 3 of 55 tackle attempts (5.5%, a small sample). The average safety misses 8.9%. That ties him for 16th-fewest misses among 58 safeties thrown at 15+ times.`
  Why: in the current version, the ranking in parentheses reads as if it belongs to "the average safety."

### 8. "Don't expect five more" bullet: make the full-season framing clear
Old: `Safeties with big interception years averaged about 2.5 the next full season, and Hooker has\n  9 regular-season games left with Buffalo.`
New: `Safeties with five-interception years averaged about 2.5 over the whole next season, all 17 games. Hooker has 9 regular-season games left with Buffalo.`
Final check (stage 4): the Quant wrote "about 8 games left," and the story says 9. Please confirm the 9 against the Bills' remaining schedule.

### 9. Add a small-sample label to this season's interceptions (Quant item 10)
Old: `then 5 in 7 games this season.\nThree of this year's 5 came in one game, week 8 at Cincinnati.`
New: `then 5 in 7 games this season. Three of this year's 5 came in one game, week 8 at Cincinnati, so this year's total rests on a handful of plays.`

### 10. Carry-over chart (reports/hooker-carryover.png): passes the five-second test only partly
The title is the takeaway, which is good. But a fan won't know what "Line = likely range" means, and two blue bars against two gray ones looks like a ranking ("these two are the good ones"), which the Quant said the data doesn't support.
- Subtitle: `Line = likely range.` -> `Black line = where the true score likely falls. Overlapping lines = no real difference.`
- Subtitle: `Safeties with 25+ targets in back-to-back seasons` -> `Safeties thrown at 25+ times in back-to-back seasons`
- Bar label: `Yards allowed per target` -> `Yards allowed per throw`
- Color: make only Interceptions Bills blue (the story's subject) and the other three gray.
- Footer: `Range: 95%, resampling players.` -> `Range: middle 95% of 2,000 reshuffles of the players.`
- Optional, recommended: the 5.5 / 2.5 / 1.7 comparison is the most fan-readable fact in the story and has no chart. A three-bar chart ("Big year: 5.5. Next year: 2.5. Typical safety next year: 1.7. n = 22 safeties") would pass the five-second test better than the 0-to-1 chart and would make a stronger site hero image. It uses existing numbers only.

### 11. Interceptions chart (reports/hooker-ints.png): passes
The title is the takeaway, 2026 is highlighted, and the footer gives the source and sample. Optional: annotate the 2026 bar "3 in one game (Wk 8 at CIN)".

### 12. Hero JSON note: minor
Old: `Interceptions barely carry over for safeties.`
New: `Big interception years don't repeat: safeties with 5+ averaged about 2.5 the next season.`
Why: "barely" overstates a 0.27 score the story calls "a little." The 2.5 is more concrete. Keep the rest of the note.

## Checked and fine
- No reintroduced Quant removals: no "sure tackler," no claim that tackling carries over better than interceptions, and Bishop is shown as better than Hooker.
- Football terms are correct (snaps, trade deadline, takeaway, starter). Apart from "bet" (edit 4), no betting language.
- Small-sample labels are present for 55 tackle attempts, 33 throws, 69 Bills throws, and individual Bills safeties. The 2026 interceptions label is added in edit 9.
- Jargon: "correlation," "bootstrap," and "Pearson" appear only in the stat-heads section. "Draft capital" stays because it is the Bills' own wording, which the Quant pinned.
- Order works: lead, then interception history, then why it doesn't repeat, then what he is, then what it means. Length is about right once edit 5 is added. The "What to watch" bullet repeats the missed-tackle point from the section above, but it is short enough to keep.

No edit requires a new number.
