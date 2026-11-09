# Quant review, stage 2: Week 9 part 3 (Bills at Vikings prediction)
(Copied from the reviewer's two reports. The reviews ran before the gate existed, on commits 2f4eeea and 76b143b.)

Round 1, publish with fixes (all applied):
1. win_chance double-counted near-ties for the home team, so 52% became 53% (fixed, plus a test that the two sides' chances sum to 1).
2. Win-call wording didn't match the logger (now "overtime counts; a tie counts as a miss").
3. The injury line had no source (now ClutchPoints, Nov 5).
4. The sample is week 2 on, not "every game".
5. "Percentages held up" was too strong for pass calls; now limited to the range where Monday's calls sit.
6. The run base-rate framing was overstated.
7. "Every one tested" now discloses that the Wentz swap is untested.
8. Minor wording and labels: Murray and last season; tie handling; the "+qb" version label.

Round 2 (ladder rewrite), publish with fixes (all applied):
1. The named final 23-20 sat awkwardly with the receipts and no-betting rules; it was replaced by the model's own 23.4-22.8.
2. The ladder chances ran low in the middle (at 20+ it said 60% and 65% happened); now disclosed plainly.
3. "Small edges add up to 53%" was wrong as an explanation; now traced to the same 0.6-point gap.
4. "every time they get the ball" became "points per drive"; "close to an ordinary offense" now has a computed rank.
5. The out-of-sample note on miss sizes is added.

Verified: projections 23.44/22.81, ladder values, 1,247 pairs, win test (617 games, Brier 0.2263), matchup backtests (n=990), logger values, no leakage, no betting lines.
