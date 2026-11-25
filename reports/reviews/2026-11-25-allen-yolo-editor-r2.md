# Editor review: 2026-11-25-allen-yolo (round 2)

**One-sentence version:** "Most Super Bowl quarterbacks threw downfield and protected the ball. Josh Allen almost always
does the first, but this year he's 6th in the league in interception rate."

**Verdict: needs edits (recorded as fail). There is one must-fix, in the chart.** All round-1 text edits landed and read
well. The chance baseline in the lead ("when chance would put about 15 there") is exactly what a fan needs. "Other part",
the percentile headers and the new footnote are clear. The card dek reads on its own. There's no jargon in the body,
no betting language, and none of Charlie's rejected phrases.

## Must-fix

1. **The chart label now collides with Allen's '19 marker.** The longer annotation `Few interceptions, long completions:` runs
   into the `'19` label and dot at the middle line, and the Favre dot sits on the start of "Few". On a screenshot it reads
   "completions:'19". Fix any of these ways:
   - Break it into three lines: `Few interceptions,\nlong completions:\n27 of 60 champions`.
   - Move it to the top-left corner of the shaded box.
   - Give it a white semi-transparent background (`bbox=dict(facecolor="white", alpha=0.8, edgecolor="none")`).

   Then reopen the PNG to check it.
2. **Endorse Quant must-fixes 1-2.** The boundary sentence (stat-heads only) and the typed "15" and "7 or 8". The words don't change.

## Polish (optional)

- **Headline "throw it deep": polish, not a must-fix.** "Deep" vs. the chart's "downfield" is a small mismatch, but the body
  explains it, and "throw it deep" is the better radio line. It's Charlie's call.
- Lead: `Allen throws downfield like a champion.` and later `7 of his 8 full seasons`. Fine as is. "Allen almost always
  throws downfield like a champion" would preview the exception.
- Stat-heads `p = 8e-05` -> `p < 0.001`.

## Checked and fine

- Lead, headline, hero, card and chart agree (25, 10, 29, 60, 6th of 31).
- The new halves paragraph is clear. "Close to chance" is plain English.
- The Darnold repeat is gone, and "did both" and "protected the ball" read well.
- Table rows read alone with the percentile footnote.
