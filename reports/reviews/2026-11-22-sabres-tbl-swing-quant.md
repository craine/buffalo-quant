# Quant review, round 3: 2026-11-22-sabres-tbl-swing (stage 2, delta check)

**Verdict: PASS.** Round 2 is in `-quant-r2.md`. Only the deltas were checked; every other number was re-derived in round 2 and is unchanged.

- "by half a goal": the chance move is 0.49. The generator prints "half a goal" only when it rounds to 0.5. Correct.
- "In the second half they were about average": the top quarter's first-half finishing value is +13.8, then -0.50 in the second half. The generator prints "about average" when the absolute value is under 1 and asserts it. Fair.
- Chart: the right-panel finishing bar is drawn at its true -0.5 and labeled "0". The explainer bar is 0. Both are within a goal of average and consistent with the text. The subtitle no longer calls the bars dots. The right-panel title reads on its own.
- Hero note (generator output) and card dek (build.py) now match the required wording exactly. "Finishing rarely lasts, goaltending only partly" fits the figures: finishing r 0.10, saves r 0.22 with a third retained, combined r 0.31.
- Reproduction: in a clean copy with the outputs deleted, the generator rebuilds the md, hero JSON and PNG byte-identically, and its asserts pass. With the review gate stubbed, the site build exits 0, and the hero note, dek and explainer render as above.
