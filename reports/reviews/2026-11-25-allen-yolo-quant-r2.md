# Quant review: 2026-11-25-allen-yolo (round 2)

**Verdict: publish with fixes (recorded as fail).** All seven round-1 Quant must-fixes landed, and every number re-derives.
Two small must-fixes remain. The new boundary-sensitivity sentence describes one rule but computes another, and three
new numbers are typed literals.

## Reproduction

`git archive HEAD` (3d6bb360) into a clean dir, `data` symlinked to the shared DB and cache, the three outputs deleted,
generator re-run. It exits 0. The md, PNG and hero JSON are **byte-identical** to the working copy. The md SHA-256 is
`6d563dd2…f708`. The working copy has no uncommitted changes under `reports/` or `src/`.

## Round-1 fixes, verified against my own code (/tmp/qa/r2.py)

1. "7 of his 8 full seasons": computed (`a_ypc_above`, `len(A[A.yr<=2025])`). Independent: 7 (only 2021 is below the middle).
2. "135 career games" and "330 league quarterback games": both computed. Independent: 135 and 330.
3. Chance baseline and halves: 14 and 11 for fewest, 4 and 6 for most. Binomial P = 0.0034, 0.0859 and 7.99e-05 (my own
   sum). These match the story's 0.003, 0.09 and 8e-05.
4. The game-script caveat is present. "Second half" is now "other part".
5. "9 to 15" is computed and asserted. My pool sizes: 9 to 15.
6. Unified method. Allen's table under my others-only, ties-half percentile is identical in all 27 cells: 2018 97/78/3,
   2019 48/55/32, 2020 35/68/85, 2021 53/37/47, 2022 69/78/81, 2023 94/65/52, 2024 9/89/91, 2025 69/66/78,
   2026 83/97/77. Favre 1996 is lower than 29 of 31 others, which rounds to 94%. His 90th-percentile-plus seasons are
   unchanged (1993, 2003, 2005, 2008, 2010). The ranks of 4th lowest of 36 and 6th highest of 31 are unchanged. Champion
   counts are unchanged: 25/16/9/10, 7/13/11/29, 3/6/12/39, 27, 14 and 24/9 of 53.
7. The chart says "Few interceptions", and the dead `labels` list is gone.

The hero and the site card (25, 10, 29, 60, 6th of 31) match.

## Must-fix

1. **The boundary sentence doesn't match its own numbers.** Stat-heads: `Quarter boundaries are inclusive at 25% and 75%;
   3 champions sit exactly on one (Joe Namath 1968, Ken Stabler 1976, Jim McMahon 1985). With strict boundaries the
   interception counts are 23/18/9/10 instead of 25/16/9/10.`
   - The code's "strict" moves the two 25% ties (Namath, McMahon) out of "fewest". It leaves Stabler (75%) in the 3rd
     quarter, which is where the default already puts him. So the counts aren't "strict boundaries". They are "ties go to
     the middle quarters".
   - Truly strict boundaries put Stabler in "most" and give 23/18/8/11.
   - In the default, a 75% tie is *not* counted in the "most" quarter, so "inclusive at 25% and 75%" also misdescribes it.
   - Both variants check out independently: ties to the middle 23/18/9/10, ties to the outer quarters 25/16/8/11.
   - Replace with: `Percentiles: share of the other qualified starters that season below the player (ties count half). 3 champions
     sit exactly on an interception-quarter boundary (Joe Namath 1968 and Jim McMahon 1985 at 25%, Ken Stabler 1976 at 75%);
     we count them in the lower quarter. Counting them in the middle quarters gives 23/18/9/10; counting them in the outer
     quarters gives 25/16/8/11. The direction holds either way.`
   - Compute both lists in code. Say which boundary each champion sits on.
2. **New typed numbers.** In the lead, `when chance would put about 15 there`. In "How we measured it", `about 15 of the
   {len(C)} champions`. In the halves sentence, `where chance would give 7 or 8`. All three are literals inside the
   f-string. Compute them: `len(C) / 4` gives 15, and `halves['late'][3] / 4` gives 7.5, rendered as "7 or 8" from floor
   and ceil. Assert them.

## Optional polish

- Stat-heads `p = 8e-05` reads as scientific notation. Use `p < 0.001`, computed with a threshold.
- **Headline "throw it deep": polish, not a must-fix.** The body says yards per completion is "a rough sign of throwing
  downfield". The air-yards check (0.42) is disclosed, and Allen's deep-throw percentiles are listed. "Downfield" would
  match the chart title and the body exactly. It's the writer's call.
- Round-1 optional notes still stand: the 2026 bar of 154 (McCarthy) and the 1987 strike-year bar. Neither changes any published number.

## Checked and fine

The Miami numbers, Favre's numbers, the source cross-check line and the data pins are unchanged and still verified.
There's no betting language, and the new caveat makes no new causal claim. The new sentence "a high interception rate
hasn't kept as many quarterbacks from winning as you might think" is supported by 10 of 60 (P = 0.09) and by 6 of 30 in
the modern half.
