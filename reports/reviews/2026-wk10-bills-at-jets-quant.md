# Quant re-review 3: 2026-wk10-bills-at-jets.md (sha256 a909c93f1252...)

Verdict: PASS. Publish.

## Checked
- Diff from HEAD~1 (.md, hero.json, wk10_prediction.py, PNG): wording only. No number changed. Table and chart values are still 75/80/55/66/75%. Hero bars are still 0.754 and 0.776. Footer still says 990 and 632.
- The run calls now read "Bills'/Jets' running game (designed runs) hurts more than it helps" in the table and the chart. That matches the model (designed runs only, src/clean/build.py:35) and Ledger P0015/P0016 ("designed runs lose points overall (rush EPA below zero)", 0.66 and 0.75).
- The chart subtitle says "QB scrambles count as pass plays." That's correct: all 489 scrambles on real plays in 2026 are counted as dropbacks. The explainer paragraph right under the table says the same.
- The hero title is now "Our most confident pass calls have held up." It matches its evidence: pass calls at 70%+, 134 games, said 75.4%, happened 77.6%.
- wk10-calls.png: labels and subtitle are fully visible and not clipped. The 50/50 line is still there. Footer has the source and sample sizes. No jargon and no betting language.
- Earlier rounds' checks still hold: clarification note, explainer, 64% of 990, 78% of 134.
