# Quant re-check: reports/2026-11-15-sabres-dal.md (sha256 d237dca4...)

**Verdict: FAIL. Two fixes, both wording; no numbers change.** All five fixes from stage 2 landed and reproduce. Every new number the
Editor added is correct. Two new or reworded claims overreach, one of them against the season data.

## Issues, ranked

### 1. "Full strength is the worry." (What it means for Buffalo)
Text: "**Full strength is the worry.** Dallas had about 71% of the five-on-five chances. Our pregame story's bigger concern was
Buffalo's own end: it allows the 6th-most chances in the league. Saturday fit that."

Evidence: this draws a trend from one game, and the season data point the other way. Buffalo's five-on-five share of chances this
season is 51.3% through Nov. 12 (15th of 32) and 50.3% through Nov. 14 (18th). At full strength, Buffalo is about even. The
"6th-most chances allowed" (3.24 a game, still 6th, re-derived) counts every strength, and its all-strength share is 48.8%. So the
season shortfall comes from special teams and other non-five-on-five play, not full strength. The bullet stitches one game's 71%
onto an all-strength season rank and calls the result "the worry".

Fix: scope the 71% to Saturday and drop "the worry". For example: "**Dallas controlled full strength Saturday.** It had about 71% of
the five-on-five chances. Over the season Buffalo has been about even at five-on-five; the chances it allows (6th-most) pile up
elsewhere." Or drop the bullet. Code the 50% season share in the generator if it is used.

### 2. Section heading "What we said to watch: Buffalo never got to the net"
It is literally false: Buffalo had 9 unblocked shots from within 20 feet, worth 1.02 goals. Headings travel on their own.

Fix: "Buffalo rarely got to the net", or "Dallas kept Buffalo from the net".

### 3. Low, traceability: two hard-coded claims
"On Oct. 8 in Buffalo ... the Sabres actually had the better chances and still lost 4-0" (generator line 225) and "6th-most" (line
304) are literals. Both are true on current data:
- Oct. 8: BUF 2.563 vs DAL 2.108; the score was 0-4.
- Buffalo allows 3.238 chances a game, 6th-most.

Assert both in the generator, or compute them, so a later re-run can't silently diverge.

### 4. Optional: "Don't read the shutout as a sign the offense has stalled."
It is defensible as a statement about the shutout alone, given 6% replay odds. But Buffalo's last two games were below its usual
3.08: 2.11 at Chicago and 2.62 Saturday. "The shutout itself says little about the offense" is safer.

## Stage-2 fixes, verified
1. Receipts: "Dallas about what it expected, Buffalo a little less." DAL 3.54 vs 3.49 and BUF 2.62 vs 2.79. Correct.
2. The lead and the "explains part of the shutout, not all of it" paragraph split the credit. Chances worth 2.6, 6% shutout odds,
   and "the bigger reason ... is in goal" (Oettinger +2.62) all match.
3. "By a hair over New Jersey": DAL 11.00 vs NJD 11.05; the stat-heads note gives 11.05. Correct.
4. Hero: the title now matches the bars, labels name the team and dates, and `num` drops ".0" (renders "13.3" and "9"). The
   homepage hero is now `ARTICLES[0]` = Bills-Jets, with this story second, so this hero JSON is not shown on the homepage today.
5. Chart 2: labels read "Sabres at Dallas, Nov. 14" and "Sabres' usual game"; the footer gives the window and sample sizes. Opened
   and checked.

## New numbers, re-derived independently
| Claim | Mine |
|---|---|
| 14 shots missed the net (22 of 36 on goal) | raw: 22 shot-on-goal + 14 missed-shot |
| Both shutouts by Dallas with Oettinger in net | Oct 8 (BUF 0, DAL 4): every one of BUF's 44 unblocked shots faced 8479979 (Oettinger); Nov 14: Oettinger only |
| Oct 8: better chances, lost 4-0 | 2.563 vs 2.108 |
| 9 or fewer close-in shots: 20% of team-games, Buffalo 3 of 20 | 130 of 650 = 0.200; BUF 3 (6, 6, 9) |
| Buffalo's other-game average 3.1 (stat-heads 3.08, 19 games) | 3.0814 over 19 games |
| 0.9 of 3rd-period chances on the power play (0.93) | 5v4 0.540 + 4v3 0.389 = 0.928 |
| Oettinger the 23rd-best goalie game of 685 | 23 of 685, no ties |
| Lyon -0.75 at Chicago (OT loss), +1.54 Saturday | -0.749, +1.543 |
| "Dallas 8-3 home loss to Winnipeg on Thursday" | DAL 3, WPG 8 at DAL, 2026-11-12 |
| 8 of 11 graded calls, 3 of 4 Sabres | same as stage 2 |
| Replays 27/57/16, scoreless 6% | 0.265 / 0.573 / 0.162, 0.061 |

Unchanged numbers (periods, strength, 71%, close-in and rebound rates, Brier 0.14) were re-checked against the stage-2 derivation and
are identical. The flow chart's new title and subtitle are accurate. The dek is accurate. No betting language. No jargon in the body.
Small samples are labeled. Nothing was written to the Ledger.

"Corrected some of its records" (data-revision note) presumes the new data are the right ones. It is acceptable, since no repo code
changed since 0af34367. "Updated" would be more neutral.
