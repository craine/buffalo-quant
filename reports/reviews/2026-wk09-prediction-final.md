# Quant final check, round 3: Week 9 Ledger rows and status lines

Reviewed: the working tree in /home/claude/bq-a (branch wk09-part3, merge commit dc338b2) and ledger/predictions.csv. I didn't run the logger and didn't edit any files.

## Verdict: FAIL, on one line in part 1. Part 3 passes and can publish.

Part 3 and all seven Ledger rows are correct. The only problem is part 1's new status line: "These are graded" is plural, but part 1 makes one call, and the check behind the line counts a part 3 call too. It's a one-line fix.

## 1. Logged rows vs. the article: correct

- **Game and timing:** all seven rows (P0002-P0008) are for game 2026_09_BUF_MIN.
  - They were created at 2026-11-09T12:48:24Z and 12:48:25Z.
  - Kickoff is 2026-11-10T01:15Z, which matches raw_schedules (2026-11-09 20:15 ET). So every row went in about 12.5 hours before kickoff.
  - Every row's resolves_at_utc equals kickoff.
- **Probabilities:** they match the article's table and calls chart exactly.

| Row | Call | Logged | Article |
|---|---|---|---|
| P0002 | Bills win | 0.53 | 53% |
| P0003 | Bills score 20 or more | 0.63 | 63% |
| P0004 | Vikings score 20 or more | 0.61 | 61% |
| P0005 | Bills' pass plays gain points | 0.57 | 57% |
| P0006 | Vikings' pass plays gain points, with Wentz | 0.65 | 65% |
| P0007 | Bills' runs lose points | 0.63 | 63% |
| P0008 | Vikings' runs lose points | 0.81 | 81% |

- **Model versions:** correct.
  - Win call: points-win-v0.1.
  - The two 20-or-more calls: points-v0.1.
  - Pass and run calls: v0.1-locshift.
  - The Wentz call: v0.1-locshift+qb.
- **Claim wording:**
  - The win claim matches the article word for word: "a tie counts as a miss".
  - The other claims say the same thing as the article in more technical terms. The article's "pass plays gain points overall" is logged as "pass plays add points overall (EPA per dropback above zero)", and "runs lose points" as "designed runs lose points overall (rush EPA below zero)". This was accepted in earlier rounds and is fine.
- **Notes:** they carry both projections (BUF 23.4, MIN 22.8) and the Wentz detail (243 dropbacks). That backs the article's line "Both projections are written into our Ledger entries."

## 2. 12:48 UTC is 7:48 a.m. ET: correct

Nov. 9 is on Eastern Standard Time (UTC−5), so 12:48:24Z is 07:48:24 ET. The new `_et()` helper converts through America/New_York, so it handles daylight saving correctly.

## 3. Nothing else changed: correct

- `git diff HEAD -- reports/` shows exactly one changed line in each story: the Ledger status line. No chart changed.
- I regenerated both stories in a scratch copy of the repo (same database). Both markdown files and both hero JSON files come out byte-identical to the working tree.
- The generator changes are limited to the `_et()` time formatting and the status-line text.

## 4. Part 1's "These are graded": not accurate, needs fixing

- Part 1's status check counts the points-v0.1 rows for this game. That matches two rows:
  - P0004, Vikings 20 or more. This is part 1's only call (61%).
  - P0003, Bills 20 or more. This is a part 3 call.
- Part 1 publishes one call, so "These are graded" has no plural thing in part 1 to refer to.
- The check is also looser than it should be: P0003 makes the line read as "logged" even though it isn't a part 1 call.
- **Fix:** change the line to "**Logged on the Ledger on Nov. 9 at 7:48 a.m. ET, before kickoff.** This call (Vikings 20 or more points, 61%) is graded after the game, hit or miss, and stays up either way."
- Also tighten the check in src/reports/wk09_wentz_vs_bills_defense.py to `metric == "MIN_points_over"`.
- The timestamp doesn't change: both rows are 12:48:25Z.

## Not part of this check

- Part 1's next line, "Our other predictions for Monday come in part 3, after part 2 looks at…", is now out of date because parts 2 and 3 are both out. Charlie may want to update it in the same edit. Since part 1 is already published, flag any change as a dated update.
- The review gate needs the final check re-recorded on part 3's new text. Its content passes.
