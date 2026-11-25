# Editor review: 2026-11-25-allen-yolo (round 1)

**One-sentence version (radio):** "Almost every Super Bowl quarterback threw the ball downfield, and most of them rarely
threw interceptions. Josh Allen always does the first part, but this year he's 6th in the league in interception rate."

**Verdict: needs edits (recorded as fail).** It's a good story with a good hook, and the lead does the job. The fixes are
small. One football phrase reads wrong to football fans, the table labels contradict the text, "picks" appears on the
chart, and I endorse the Quant's baseline and "every year" fixes (Quant must-fixes 1-4). No jargon in the body, no betting
framing. Charlie's rejected phrases ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end")
are absent. The headline matches the findings once the Quant's fixes land.

## Must-fix (most important first)

1. **"Second half" means something else to a football fan.** In "What it means": `What separates most champions is the
   second half: they kept the ball away from the defense.` A Bills fan hears second half *of the game*. -> `What sets most
   champions apart is the other part: they kept the ball away from the defense.` Same issue, smaller, in the Allen section:
   `That's the champion half.` -> `That's the part he shares with champions.`

2. **The table says "rank", but the numbers are percentiles, and they contradict the text.** The 2024 row shows "11th" in
   "Interception rate, rank*", and the paragraph below says "the 4th lowest rate of 36 starters". A fan reading the table
   alone thinks Allen ranked 97th of about 33 in 2018. Change the three headers `Interception rate, rank*`, `Yards per completion, rank*`,
   `Passing value, rank*` to `Interception rate, percentile*`, `Yards per completion, percentile*`, `Passing value, percentile*`.
   Change the footnote `*Percentile among that season's starters: 99th is highest. For interceptions, higher means more.` to
   `*Percentile among that season's starters: 99th is the top, 50th is the middle. For interceptions, higher means more of them.`

3. **"Picks" on the chart.** `Few picks, long completions: 27 of 60 champions` -> `Few interceptions, long completions: 27 of 60 champions`
   (brand rule 1 lists "picks", and the chart is screenshotted alone). The label also sits on top of a gray dot. Nudge it down/left, or shorten it to two lines.

4. **Endorse the Quant's must-fixes 1-4.** "Allen does that every year" is false (2021). "Starts" -> "games". Add the "about
   15 in each quarter by chance" sentence. Soften the last-30 claim. Add the game-script caveat. The baseline matters for
   fans as well as for accuracy: without it a reader can't tell whether 29 of 60 is a lot.

## Polish (optional)

- Lead: `But they rarely threw it to the other team: 25 were in the quarter with the fewest interceptions` -> `But they
  protected the ball: 25 were in the quarter with the fewest interceptions`. Every QB "rarely" throws picks, so the sentence undersells the finding.
- `The most common champion was both:` -> `The most common champion did both:`
- `Last season's champion, Sam Darnold, is one of them.` He's already in the list just before. Cut it, or make it the hook:
  `The most recent is last season's champion, Sam Darnold.`
- Miami section: `For Allen it was a dud. That's part of the "reckless" story: the bar is high.` -> `For Allen it was a dud,
  and that's part of the "reckless" story: his bar is higher than everyone else's.`
- Site card dek (`src/site/build.py`): `Only 10 were among the most.` -> `Only 10 were in the quarter with the most.` (it
  reads alone as "the most what?").
- Headline: "throw it deep" vs. the chart's "throw the ball downfield". "Downfield" is the more honest word for yards per
  completion. Optional: `...60 Super Bowl champions say: throw it downfield, but don't throw it away`.

## Checked and fine

- Body has no stat jargon. "Passing value" is defined with a worked Favre example. "Starter" is defined (14 throws per team
  game). EPA is only in stat-heads.
- The explanation is right-sized: three measures, one real example each (Favre 1996), how ranking works, and how we checked
  it (non-qualifiers, halves).
- Headers tell the story. Paragraphs are short. Caveats are honest.
- Hero: both big numbers read alone ("of 60 champions were in the quarter of starters with the fewest interceptions"), and so does the note.
- Chart: the title is the takeaway, the right panel reads in five seconds, the axis ends are labeled in words, and the footer has the source and the starter definition.
- No betting language. No rejected phrases.
