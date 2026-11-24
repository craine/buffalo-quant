# Final check (stage 4): 2026-wk12-kc-whos-left

**Verdict: PASS.** I reviewed everything that changed between round 1 and the current text (md sha256 89e48fb2…), plus anything those changes touch.

## What changed, and what I checked
- **Reid, Elam and Watson labels.** All three match the weekly roster for weeks 11-12.
- **Target table.** Walker is now 36 (11%), Moore 17%, Kincaid 41 and Coleman 40. The totals are 316 and 287. All of these match my recompute that excludes sacks and two-point tries.
- **35% and 71%.** Unchanged, and still correct.
- **Week 11 caveat.** CIN-WAS is the only game missing, and the text, the stat-heads and the chart footer all say so.
- **Positions.** The DB labels don't change any count.
- **Text replacements.** The new wording claims nothing the data doesn't support.
- **Hero JSON and site card.** Unchanged and consistent with the body.
- **Reproducibility.** A clean re-run reproduces the md, the hero JSON and the PNG byte-identically.

## Before publishing
Part 1 (PR #60) has to merge first, or the link to bills-chiefs-leonhard-file.html will 404.
