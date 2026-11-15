# Quant re-check: Are the Sabres done? (2026-11-15-sabres-playoff-chances), commit d0294b46

## Verdict: FAIL, on charts only. The text passes.

Every number and claim in the revised md, hero and dek checks out (details below). Two charts have text cut off at the right
edge. That has to be fixed before the gate opens, so I have not recorded final.

## Required fix

1. **Clipped chart text.**
   - `reports/sabres-playoffs-whatif.png`: the title "Fewer scoring chances against, or more for: either one about doubles the
     Sabres' playoff chance" is cut off at "the Sabre".
   - `reports/sabres-playoffs-points.png`: the subtitle "...Shaded: where the last Eastern playoff spot usually lands in those
     seasons." is cut off at "lands in th".
   - Fix: shorten or wrap both, e.g. title "Fewer chances against, or more for: either about doubles the Sabres' playoff chance"
     on two lines; subtitle wrapped onto a second line. Re-open both PNGs after regenerating. The md text doesn't need to change.

## New or changed numbers, re-derived independently

- Worked example: 336,462 unblocked non-empty-net shots in 2023-26; within 10 ft 13.75% (13.8%); 60+ ft 0.81% (0.8%). Exact.
- Chances-against split: 0.294 excess = 5v5 +0.049 + shorthanded +0.124 + other +0.121; shorthanded share 42%. "Most of the rest"
  in odd situations (0.121 of 0.170) and "close to even" at 5v5 are both correct. xG share 48.5%, 21st. Exact.
- Shorthanded what-if: observed BUF xGA (unrescaled) 3.286; kept share (3.190-2.988)/(3.286-2.988) = 0.678; 0.124 x 0.678 = 0.084.
  With that adjustment the simulation gives 21.6/21.7/21.4% (seeds 7/8/9), so 22% at seed 7. 87 points matches.
- Backtest at 20,000 sims (my independent implementation): Brier 0.149 (story 0.1487), by season 0.116/0.122/0.210 (story
  0.116/0.122/0.209); baseline 0.1975 (0.159/0.188/0.245) exact. 5-30% bucket: 23 teams, mean 0.161, 3 made, exact. Under 5%:
  2 of 11 made (MTL, STL 2024-25), exact. Last year's Sabres 11.6%, so 12% is right.
- Per-84 player numbers: paces 15/19/21/29/5 match points/games x 84. Ratings 48.7/43.1/41.4/46.1/18.2 per 82 become
  49.9/44.2/42.4/47.2/18.6 per 84, so 50/44/42/47/19 match. Same five players and the same three on the other side.
- Benson: 1 non-empty-net goal on 7.3 xG plus 1 empty-net goal (en_g = 1); finishing -6.3, "about 6 of the team's 7". Correct.
- Goalies: league save percentage 89.1%. Lyon 55 shots labeled. Luukkonen "about 3 more goals" (-3.2). Correct.
- Power play: xGF 0.68, GF 0.50 a game. Exact.
- Unchanged numbers re-confirmed from the round-1 review (standings, 94/74/1.16, 85 (76-95), team table, carry-over, 20.7).

## Wording and claims

- Lead and dek name the overall fix (16% to 32%, about double). Correct.
- "Most likely to last" / "least likely to fix itself" / "even that tends to ease some, which the model already builds in"
  match the carry-over numbers and the model. Correct.
- The calibration paragraph is now accurate and labeled a small sample. The 2025-26 out-of-sample result is in the body.
- The projection "assumes about average" shooting and goaltending. Accurate.
- Stat-heads: the rating-noise claim is gone, the module docstring matches RATING_SD = 0, and P0017's resolves_at mismatch is
  disclosed. No Ledger rows were changed (P0017 is unchanged: 0.16, same claim text).
- Brand rules: no betting language ("ahead of the line" is gone); jargon only in stat-heads; labels read on their own.
- The hero and the dek match the text.
