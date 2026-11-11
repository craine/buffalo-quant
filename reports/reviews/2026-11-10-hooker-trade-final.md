# Quant final check (stage 4, v3): reports/2026-11-10-hooker-trade.md, branch hooker-headline

## PASS

1. **No number changed.** PNGs and hero.json: `git diff --stat main` shows nothing. Story: comparing every number in main and branch gives two differences. "11" was added (the Nov. 11 note). One "8" was dropped because the repeated "5 of the Titans' 8 interceptions" sentence was cut from the Hooker section; it's still in the lead. Generator diff: f-strings were moved and reworded only, with no change to any computation. build.py: the dek has no new numbers (5 of 8). The hero image is now hooker-ten-ints.png, an existing, unchanged chart.
2. **Wording stays within limits.** The headline says "a new partner" and promises no improvement. The lead uses "tracked with," which is the approved wording. "Bishop's own coverage barely changed" matches 8.8 vs 9.2 yards per throw, the same as the approved "barely moved." "Whether it helps is what we'll track" makes no claim. "Hooker likely takes the spot beside Bishop that Gardner-Johnson and Hamlin have split" is fine: it hedges, and the stat-heads section backs it (CJ weeks 1-5, Hamlin weeks 6-9, week 6 shared). Nothing says the partner caused the drop. "Small samples, and other things changed" still comes right after the lead.
3. **The dated note is accurate and meets the rule.** CLAUDE.md's rule is about numbers ("Updated numbers mean a new, clearly dated story or note"), and the note is dated and says what changed. Optional, not blocking: the lead was also rewritten. "headline, lead and story order revised" would be more exact.
4. **Language and caveats are intact.** The body has no betting talk and no jargon. All caveats are still there: 1 in 16 (Luck), +0.05 (in the Quarterbacks check and the track bullet), the Hamlin asterisk with LV -0.19, the coordinator (in both the checks and the track bullet), and Hooker 8.3 vs 8.2 for his teammates.

No issues.
