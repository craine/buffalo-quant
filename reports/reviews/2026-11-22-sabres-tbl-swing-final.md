# Final check: 2026-11-22-sabres-tbl-swing (stage 4)

**Verdict: PASS.** Round 2 is in `-final-r2.md`.

What changed since round 2, and the lines those edits touch:
- The hero note and card dek now carry the required wording, so the overclaim is gone.
- Story: "half a goal" (0.49) and "about average" (-0.50).
- Chart: the subtitle, the right-panel title, and the 0 label on the -0.5 finishing bar.
- The explainer bar is 0.

All of these are consistent with the numbers re-derived in round 2. Every other line is unchanged from what passed in round 2.

The generator reproduces the md, hero JSON and PNG byte-identically, and the site build renders them.

Before publishing:
- The PNG still has to be frozen with `python3 scripts/freeze_images.py`.
