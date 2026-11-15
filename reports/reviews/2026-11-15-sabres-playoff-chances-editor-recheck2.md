# Editor re-check (stage 3, round 3): 2026-11-15-sabres-playoff-chances, charts

I opened both re-rendered PNGs. The story text is unchanged from round 2, which was already ready.

## Points chart: ready
- The subtitle fits now: "...Shaded: where the last Eastern playoff spot usually lands."
- The title is the takeaway, and the "about 94" note reads on its own.

## What-if chart: one fix needed (FAIL this round)
Nothing is clipped any more, and the title and subtitle no longer overlap. The problem is the title's wording.

**"Either fix" misreads.** The chart shows four changes. On a screenshot, a fan reads "either fix" as any of the bars, including the
shorthanded one, which moves the Sabres from 16% to 22%. That's not double. The subtitle ("Allow fewer scoring chances, or create
more") doesn't rescue it, because the shorthanded bar is also a way to allow fewer scoring chances.

**Required:** in `src/reports/sabres_playoff_chances.py`, replace the title
`Either fix about doubles the Sabres' playoff chance`
with
`Average defense or more offense about doubles Sabres' playoff chance`

Why this wording works:
- The two bars that double the chance are labeled "All scoring chances allowed cut to league average" (32%) and "Create 0.2 more...", and the last bar says "average defense".
- So the new title points at exactly those two bars. The shorthanded bar is plainly a piece of "average defense", not all of it.
- It's 68 characters, which should fit on one line (the current 51-character title uses about two-thirds of the width).
- Re-open the PNG to confirm it fits. If it doesn't, use the shorter `Average defense or more offense about doubles the playoff chance`. The subtitle already says Sabres.

Keep the subtitle as it is.

Once that title is in and fits on one line, the editor stage passes. No further text review is needed.
