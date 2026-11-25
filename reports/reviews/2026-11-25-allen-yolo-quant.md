# Quant review: 2026-11-25-allen-yolo (round 3)

**Verdict: pass (publish once the Editor's chart fix lands).** Both round-2 must-fixes are applied, and every number
in the story is correct.

## Reproduction
I extracted `git archive HEAD` (25af6574) into a clean directory, symlinked `data`, deleted the three outputs and re-ran the
generator. It exits 0. The md, PNG and hero JSON are **byte-identical** to the working copy. The md SHA-256 is
`3df3b439…28e7`. Nothing under `reports/` or `src/` is uncommitted. The site card is unchanged from round 2.

## Round-2 fixes, verified
1. **Boundary sentence.** My own code counts the tied champions in the middle quarters as 23/18/9/10 and in the outer
   quarters as 25/16/8/11. The story matches, and both lists are asserted. Namath 1968 and McMahon 1985 sit at 25%, and
   Stabler 1976 at 75%, as stated.
2. **Chance figures.** The "15" comes from `len(C)/4` and the "7 or 8" from `30/4` (floor and ceiling). Both are asserted
   and no longer typed in.
3. **Stat-heads p-value.** "p < 0.001" is asserted (8.0e-05).

The only text diff from round 2 is the stat-heads p-value and the boundary sentence. The lead and body read the same
because 15 and 7/8 render identically. Every other number was verified in rounds 1 and 2 and is unchanged.

## Chart
The counts are unchanged. **One drawing bug** (Editor must-fix 1). The shaded "few interceptions, long completions" box is
drawn with `axvspan(ymin=0.5, ymax=1)`, which is a fraction of the axes height. With the new `ylim(-3, 113)`, its bottom
edge lands at y = 55, not on the middle line at 50. No champion falls between 50 and 55, so no gray dot is shown on the
wrong side. But the gap is visible, and Allen's '19 dot (55th percentile) sits just under the box edge, so he looks like he's
outside the quadrant he belongs to. Draw the box in data coordinates instead, e.g.
`ax.add_patch(plt.Rectangle((-3, 50), 53, 63, color="#EEF2F9", zorder=0))` or `ax.fill_between([-3, 50], 50, 113, ...)`.
Then re-check the PNG.
