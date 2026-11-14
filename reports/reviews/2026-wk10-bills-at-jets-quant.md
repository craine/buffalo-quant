# Quant re-review (narrow): 2026-wk10-bills-at-jets.md, plain-English call labels

Verdict: FAIL as-is. Publish with two one-line text fixes (no number or model change needed).

## Required fixes
1. Clarification note misquotes the Ledger. Text: "...instead of "pass plays gain points overall"). No numbers changed. The Ledger keeps the original wording, logged Nov. 13."
   Evidence: "pass plays gain points overall" was the story's old label, not the Ledger's. P0013/P0014 claim_text say "pass plays add points overall (EPA per dropback above zero)"; P0015/P0016 say "designed runs lose points overall (rush EPA below zero)". A reader who checks the Ledger finds different wording than the note implies is "original".
   Fix: "...instead of "pass plays gain points overall"). No numbers changed. The Ledger entries, logged Nov. 13 (ET), keep the wording they were logged with (for example, "Bills' pass plays add points overall")."
   (Timing is fine: created_at_utc 2026-11-14T00:54:53Z = Nov. 13, 7:54 p.m. ET, before the 2026-11-15T18:00Z kickoff.)
2. Explainer says "every run" but the run calls count designed runs only. Text: "add up the value of every pass play (or every run) in the game".
   Evidence: rush_epa = rush_epa_sum/rushes from clean_team_week, where is_designed_rush = rush==1 AND qb_dropback!=1 on play_type 'run', kneels/spikes/2-pt/no-plays excluded (src/clean/build.py:35, 22-25, 86). 2026 raw_pbp: all 489 real-play scrambles have qb_dropback=1, rush=0, so they sit in the pass number. Ledger P0015/P0016 say "designed runs". Josh Allen scrambles are a large part of what fans call the Bills' running game, and the table is far from line 22's "(sacks and scrambles count)".
   Fix: "add up the value of every pass play (or every designed run; QB scrambles count as pass plays) in the game..."

## Verified
- Numbers: diff touches labels, the explainer, the note, the chart title only. All values unchanged: 75/80/55/66/75%, 990, 64%, 632, projections. Chart redraw shows same bars and footer.
- Labels vs Ledger: "passing game helps more than it hurts" = P(dropback EPA/play > 0) = P0013/P0014 (0.80, 0.55). "running game hurts more than it helps" = 1 - P(rush EPA > 0) = P0015/P0016 (0.66, 0.75). Per-play average above/below zero has the same sign as the total, so "add up ... total above zero" is equivalent. Dropbacks include scrambles and sacks (qb_dropback=1), as the story says. "Running game" = designed runs in model and Ledger; acceptable plain English once fix 2 lands.
- 990 / 64%: re-derived from clean_team_week, 2023-25 REG weeks 8+, offense side, rushes>0: n=990, share with rush_epa_sum<0 = 0.639 (no exact zeros). Matches model_v01_backtest (rate of v>0 = 36%).
- Chart wk10-calls.png: title and labels read on their own, no jargon, 50/50 line, footer with source and samples.
- No betting language; no jargon added in body.
