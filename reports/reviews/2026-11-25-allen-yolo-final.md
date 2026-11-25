# Final check: 2026-11-25-allen-yolo

**Verdict: pass.** The final check covers the current text, md SHA-256 `3df3b4393af28a4256c4a043b62cfa9768d95f790652e84b6e34ded3a32328e7`.

## Reproduction
I extracted `git archive HEAD` (c3307169) into a clean directory, symlinked `data` to the shared DB and cache, deleted
the three outputs and re-ran `python3 -m src.reports.allen_yolo_history_nov25`. It exits 0. The md, PNG and hero JSON
are **byte-identical** to the working copy, and nothing under `reports/` or `src/` is uncommitted. The pinned nflverse
and 2026 play-by-play fingerprints are asserted and pass.

## What changed since the Quant pass (round 3)
- Generator: one line. `axvspan` became `fill_between` for the chart's shaded box. Story text and hero are
  byte-unchanged, with the same SHA as the round-3 Quant pass.
- PNG: the shaded box now runs from 50 to the top, and from the left edge to 50, in data units. No number, label or count
  changed. The 27-champion quadrant matches the shading: no champion sits between the 50 and 55 lines where the old box
  was misdrawn.

## Edits from stages 2-3, all re-verified against independent code in rounds 1-3
- "7 of his 8 full seasons"; 135 career games and 330 league games.
- The chance baseline of 15 per quarter, 7 or 8 per half, and p = 0.003, 0.09 and < 0.001.
- Halves: fewest 14 and 11, most 4 and 6.
- Unified percentiles: Allen's table in all 27 cells, Favre at 94%, 4th lowest of 36, 6th highest of 31.
- Boundary variants 23/18/9/10 and 25/16/8/11; the 9-to-15 pool range.
- The game-script caveat.

The hero and site card match the text (25, 10, 29, 60, 6th of 31). There's no betting language and no rejected
phrasing. Before publishing, freeze the new PNG with `scripts/freeze_images.py`.
