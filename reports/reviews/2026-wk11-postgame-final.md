# Final check (stage 4): 2026-wk11-postgame

**Verdict: PASS.** Text checked: md sha256 9d8fe7e2c13aaf22580bfdd7171cd721e5bca93d428038ddc7948569d145f253.

## What changed since the stage-2 review
- Round 2 applied all Quant and Editor must-fixes. I re-verified each against my own queries: Bass 4/5 and the 54-yard miss; no-plays excluded (MIA -0.26/55/22nd/25%, BUF +0.04); win-chance 10-90% split 18/25 vs 15.9 with 1 of 5 easy misses inside it; 4 of 5 up 14+; Score column; career rank pinned (32/133); projection from P0021's notes; depth labels; interception depths computed.
- Round 3 changed chart 1's title, which now fits, and three wording lines with no new numbers.

## Clean-copy reproduction
I rebuilt from `git archive HEAD`, plus the working-tree `src/reports/wk11_postgame.py`, `src/ledger/grade_wk11.py`, `src/site/build.py` and `ledger/*.csv`, against the same DB. Output is byte-identical:
- md 9d8fe7e2...
- hero c294a79b...
- wk11d-allen-throws.png 88462be1...
- wk11d-deep-by-quarter.png fbac6a32...

## Before publish (process, not text)
- Commit the untracked generator and grader.
- Run `scripts/freeze_images.py` for the two wk11d PNGs.
