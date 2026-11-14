# Final check (stage 4): reports/2026-wk10-bills-at-jets.md
sha256 a909c93f1252bba10c352644d569b545c9daf328f872da53d138133304cb70a4 (matches a909c93f1252).

Verdict: PASS (publish).

## 1. Every line stands alone
- Calls table rows, calls chart labels and title ("Our surest call: the Bills' passing game helps more than it hurts (80%)"),
  hero note and explainer title, ladder and win-test chart titles all read as plain sentences. Run calls carry "(designed runs)";
  calls chart subtitle and the "What these mean" paragraph say scrambles count as pass plays. No "gain/lose points" wording
  outside the clarification note's quote of the Ledger.
- Jargon (EPA, dropback, Brier, calibration, residual) appears only in "For the stat-heads".
- Non-blocking: ladder chart title "72% to 41% to reach 24" is a bit terse; hero explainer says "134 past games" where they are team games.

## 2. Betting language
grep for picks/odds/lock/lean/favorite/value/edge/fade/lines/spreads/bet/units/cover: one hit only, "No betting lines are used
anywhere in these models" (a disclaimer in stat-heads). Clean.

## 3. Numbers vs Ledger and data
- Ledger P0012-P0016 probabilities 0.75 / 0.80 / 0.55 / 0.66 / 0.75 match table, chart and text.
- Generator functions: win 0.7466; Bills dropback P(over 0)=0.798 (exp +0.233); Jets dropback 0.551 (exp +0.028);
  Bills rush P(over)=0.338 -> under 0.66 (exp -0.067); Jets rush P(over)=0.25 -> under 0.75 (exp -0.113). Projections 29.86 / 22.08.
- Independent SQL on raw_pbp (2026 wk1-9 REG, qb_dropback, no 2pt): Bills offense 273 plays, +0.263/play; Jets defense 312 plays,
  +0.161 (rank 26 of 32 = 7th-most). Matches story. Points per drive 2.89 (1st), Jets D 2.37 (6th-most), Jets O 1.92 (19th), Bills D 2.10 (16th) match.
- Example plays: Ty Johnson 36-yd on 3rd-and-8 = 3.77 ("about 3.8"); 7-yd sack on 3rd-and-14 = -1.76 ("about 1.8"). Match.
- Ladder chart values equal table; ladder footer 1,264 team-games = 2 x 632 games. Win-test chart (102 games, 75%/74%) matches text.
- Non-blocking, pre-existing: the logged win call counts a tie as a miss while the 75% treats a tie as half; tie probability is tiny, disclosed.

## 4. Clarification note
Says no numbers changed (consistent: all probabilities equal Ledger rows logged before the reword). Quoted logged wording
"Bills' pass plays add points overall" is exact text of P0013's claim_text (parenthetical omitted, introduced as "for example").
"Four pass and run calls" is correct (P0013-P0016). Dated Nov. 14.

## 5. Kickoff / timing
raw_schedules: 2026_10_BUF_NYJ, Sunday 2026-11-15 13:00 ET, NYJ home. Ledger created_at_utc 2026-11-14T00:54:53Z = Nov 13 7:54 p.m. ET,
before kickoff; story's "Nov. 13 at 7:54 p.m. ET" matches. resolves_at 18:00Z = 1 p.m. ET.
