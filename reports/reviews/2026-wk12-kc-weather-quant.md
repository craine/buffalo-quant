# Quant review, round 3: 2026-wk12-kc-weather (stage 2)

**Verdict: PASS (publish).** Rounds 1 and 2 are saved as -quant-r1.md and -quant-r2.md.

This round changed two lines in the md (`git diff HEAD~1`). The hero, card and PNG are unchanged.

- **Stat-heads wind bullet.** The generator computes and asserts 1,337 games with both a column and a note, 194 that disagree by more than 1 mph, and 21 where the column reads 0. I got the same three counts independently in round 2.
  - The 21 all disagree by more than 1 mph with a 0 column, so the note gives at least 2 mph. "A real wind" is accurate.
  - The overstated "often … 10-14 mph" wording is gone.
- **First bullet** now reads "Each team scored 19.0 points a game." The number is unchanged.
- **Reproduction:** a `git archive HEAD` clean copy re-runs to byte-identical md, hero JSON and PNG.
- Everything verified in rounds 1 and 2 still holds.
- **Forecast:** unverified from this shell (api.weather.gov blocked). Rely on the coordinator's Chrome fetch, which needs a note in the PR.
