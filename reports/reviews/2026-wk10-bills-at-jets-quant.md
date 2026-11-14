# Quant re-review 2: 2026-wk10-bills-at-jets.md (sha256 57801beccde4...)

Verdict: FAIL. No numbers changed, and every reworded line matches what was computed and logged. Two small text fixes remain.

## Required fixes
1. The run calls don't say "designed runs" anywhere they appear on their own (CLAUDE.md rule: "The run calls count designed runs only; QB scrambles count as pass plays, so say so next to any run call").
   - Where: table rows and chart labels "Bills' running game hurts more than it helps" / "Jets' running game hurts more than it helps", and wk10-calls.png. The chart image travels without the story and says nothing about designed runs or scrambles. The explainer below the chart does say it, but it isn't next to the calls.
   - Fix: change the labels to "Bills' running game (designed runs) hurts more than it helps" (same for the Jets), and end the chart subtitle with "QB scrambles count as pass plays." Or put both in the chart subtitle and in a one-line note directly under the table.
2. The hero explainer title claims more than the evidence. Text: "Our most confident calls have held up."
   - The bars show only the matchup model's pass calls at 70%+ (n=134: said 75.4%, happened 77.6%). Nothing shown covers the win model's confident calls, and the title travels on its own. (I also checked the run "hurts" calls at 70%+: n=287, said 76%, happened 74%. They held up too, but the story doesn't show it.)
   - Fix: "Our most confident pass calls have held up."

## Verified (nothing numeric changed)
- Diff HEAD~1 for the .md, hero.json, wk10_prediction.py and the PNG: wording only. Every value is unchanged, including 29.9/22.1, 75/80/55/66/75%, 0.27/0.19/0.05/0.23, 990, 134, 75%/78%, 64%, 2,494, 632. The hero bars are still 0.754/0.776. The PNG bars and footer are unchanged; only the subtitle changed.
- "passing game helped more than it hurt 78% of the time" = top dropback bucket, y = game dropback EPA > 0. Matches the backtest (said 75%, happened 78%, n=134).
- "in 64% of 990 past team games, a team's designed runs added up to less than zero": re-derived from clean_team_week (2023-25 REG, weeks 8+, offense side, rushes>0): n=990, 0.639 with rush_epa_sum < 0.
- Explainer definitions match the code: dropbacks include sacks and scrambles (qb_dropback=1; all 489 real-play 2026 scrambles have it); designed run = rush==1 and not a dropback (src/clean/build.py:35). A total above zero has the same sign as the per-play average used by the model and the Ledger.
- Clarification note: accurate. The Ledger quote matches P0013 exactly. The entries were logged 2026-11-14T00:54:53Z = Nov. 13 7:54 p.m. ET, before kickoff, and Ledger rows are append-only. "and the lead" is true: the lead changed from "pass plays gain ground".
- "a 75% win chance" header, "faces" title, the chart subtitle naming the game, the matchup line "the Bills' passing game helps more than it hurts" (P0013, 80%): all accurate.
- No betting language and no new jargon.
