# Editor review: 2026-11-25-allen-yolo (round 3)

**Verdict: needs one chart edit (recorded as fail).** The text is ready. The changed stat-heads lines read clearly. The
lead, headline, hero, card and chart agree. There's no jargon in the body, no betting language and none of the rejected
phrases. The headline "throw it deep" is Charlie's call, noted as polish.

## Must-fix
1. **The shaded box no longer lines up with the middle line.** When the y-axis was extended to 113, the box (drawn as a
   fraction of the axes height) moved: its bottom edge now sits at about the 55th percentile, with a visible white gap
   above the "middle" line. Allen's '19 dot sits just below the shading, so a fan reads it as outside the "few
   interceptions, long completions" group, even though it's in it. Draw the box in data coordinates, so its bottom sits on
   the middle line, e.g. `ax.add_patch(plt.Rectangle((-3, 50), 53, 63, color="#EEF2F9", zorder=0))`. Then reopen the PNG.
   The new label box itself is good: one line, no collisions.

## Checked and fine
- The label reads on its own and covers no markers.
- All the Allen year labels are legible, and the Favre dot is clear.
- Right panel unchanged.
