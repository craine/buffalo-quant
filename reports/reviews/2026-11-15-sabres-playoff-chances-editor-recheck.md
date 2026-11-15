# Editor re-check (stage 3, round 2): 2026-11-15-sabres-playoff-chances

I re-read the current story body (not "For the stat-heads"), all three charts as rendered PNGs, the hero JSON and the site dek.

## One-sentence version

"The Sabres aren't done, but they're about a 1-in-6 shot. The cold shooting and goaltending should even out. The scoring chances they give up won't fix themselves. Cut those to league average and their playoff chance doubles, to 32%." This is now the lead.

## Verdict: needs edits (FAIL this round). The text is ready; two charts are clipped

Every round-1 text edit landed and reads well:
- The lead names the 32% fix.
- "Scoring chances" and "playoff chance" are kept apart everywhere.
- The shorthanded share is now "the biggest single piece" (about 42%), with where the rest comes from.
- Benson is now 1 goal on 7.3 plus an empty-netter, so "about 6 of 7" checks out.
- Player numbers are per 84 games, with the column "Track record says".
- The shot example is in: 13.8% within 10 feet, 0.8% from 60+ feet.
- The scorecard now says lower is better.
- The new under-5% caution is honest and clear.
- Units, the standings column, "0.00", the "10th-most of 32" wording and the goalie so-what line are all fixed.
- The hero and dek read on their own. The Ledger call is unchanged and fine.

The round fails only because two chart texts run off the edge of the image. A fan sharing a screenshot loses the end of the takeaway.

## Required edits

### 1. What-if chart title is cut off ("…doubles the Sabre")
`src/reports/sabres_playoff_chances.py:267`. Replace
`"Fewer scoring chances against, or more for: either one about doubles the Sabres' playoff chance"`
with
`"Allow fewer scoring chances or create more: either one about doubles the Sabres' playoff chance"`
Also check the rendered PNG. If it still overflows, wrap it with `\n` after `create more:`. Wrapping is the only way to keep the whole takeaway at this font size.

### 2. Points chart subtitle is cut off ("…usually lands in th")
`src/reports/sabres_playoff_chances.py:238`. Replace
`Shaded: where the last Eastern playoff spot usually lands in those seasons.`
with
`Shaded: where the last Eastern playoff spot usually lands.`
The title already says "our simulated seasons", so nothing is lost. Re-open the PNG to confirm it fits.

## Optional polish (doesn't block a pass)

### 3. "fit on" is model talk
Line 327: replace `Last season, the one the model was never fit on, was the hardest:` with `Last season, the one the model never learned from, was the hardest:`

### 4. "about half of a gap like this" still reads awkwardly
Line 409: replace `It's the most specific fix on the list, and if nothing changes, about half of a gap like this tends to stick around.` with
`It's the most specific fix on the list, and it's the kind of problem that tends to stick around if nothing changes.`

## Charts
- Points: the title is the takeaway and the "about 94" note reads on its own. The subtitle is clipped (edit 2).
- Carry-over: ready.
- What-if: the bar labels stand alone and the 22% matches the Quant's fix. The title is clipped (edit 1).

When edits 1 and 2 are in and the PNGs are re-checked, this passes. Nothing else needs another full round.
