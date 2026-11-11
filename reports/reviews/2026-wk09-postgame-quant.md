# Quant review, stage 2: Week 9 post-game (Bills 23, Vikings 6)

Story: reports/2026-wk09-postgame.md (generator src/reports/wk09_postgame.py, branch wk09-postgame), charts wk09d-proj-vs-final.png and wk09d-scorecard.png, hero 2026-wk09-postgame.hero.json, site dek in src/site/build.py.
Everything below was re-derived from raw_pbp, raw_schedules, clean_drives, clean_team_week and raw_ftn using read-only SQL. I did not run grade_wk09.main() or the generator, and wrote nothing to the Ledger.

## Verdict: publish with fixes

All seven grades are correct, and so are the hit count, the Brier math and the season-to-date record. One factual error has to be fixed before publishing: Carson Wentz's stat line is really the whole Vikings team's passing line, and it includes the backup's garbage-time snaps. Two claims overstate what happened: "a miss that big … 3 in 100" and "closed the gap". The rest are wording fixes.

## Issues, ranked

### 1. MUST FIX: Wentz's line includes Max Brosmer's snaps
Text: "Carson Wentz went 14 of 31 for 139 yards, threw 2 interceptions (Dorian Williams and Terrel Bernard) and was sacked 2 times."
Evidence: the generator adds up every MIN dropback (`q[t]` is grouped by posteam, not by QB). By gsis id (COALESCE(passer_player_id, rusher_player_id)), the passers were:
| QB | dropbacks | cmp/att | yds | INT | sacks (yds) | points value |
|---|---|---|---|---|---|---|
| C.Wentz 00-0032950 | 25 | 8/24 | 81 | 2 | 1 (-6) | -24.5 |
| M.Brosmer 00-0040494 | 8 | 6/7 | 58 | 0 | 1 (-6) | -1.7 |
| Team | 33 | 14/31 | 139 | 2 | 2 (-12) | -26.2 |
Brosmer came in with 4:40 left (MIN win chance 0.4%). Wentz's only other sack (play 1308, Rousseau) was wiped out by Hamlin's defensive holding, so officially he was sacked once.
Fix: "Carson Wentz went 8 of 24 for 81 yards, threw 2 interceptions (Dorian Williams and Terrel Bernard) and was sacked once before Max Brosmer took over with under five minutes left." The team-level "about 26 points over 33 dropbacks" can stay, but call it Minnesota's passing, not Wentz's. P0006 stays a miss under either count: the team value was -0.795 per dropback, and Wentz alone was -0.98 per dropback.
Also suggest adding to the stat-heads section: the P0006 grade uses the team value (33 dropbacks, 8 of them Brosmer's in garbage time), which matches how the call was defined.

### 2. SHOULD FIX: "a miss that big happened only about 3 times in 100" is the one-sided rate
Text (Finding): "They scored 6, a miss that big happened only about 3 times in 100 when we tested the model."
Evidence (MIN projection 22.81, miss -16.81):
- Out of sample (n=1,234): falling 16.8+ points short happened 3.2%. A miss of 16.8+ in either direction happened 7.2%.
- Training (n=2,494): 3.4% one-sided, 7.7% either direction.
"A miss that big" reads as either direction, so it overstates the rarity by about 2x. The body is worded correctly ("fell that far short").
Fix: "…they scored 6. Falling that far short happened only about 3 times in 100 when we tested the model."

### 3. SHOULD FIX: "the Bills' defense closed the gap we pointed at" overclaims
Evidence: Bills defense against short throws (attempts, not sacks, air yards under 20), in points per 100 throws:
- Through week 8: +23.6, 25th of 32 (league +12.1), n=242. Opponent-adjusted gap 20.5 points, which reproduces part 1's 21.
- Through week 9: +15.4, 19th of 32 (league +11.4), n=267. Close games: 20th. Opponent-adjusted gap 8.8 points.
- Minnesota's 25 short throws cost -16.1. That's correct. 16 of those throws came in close-game situations (-13.1).
The gap shrank by more than half, but the Bills are still below average on short throws. It also came against a backup QB whose offense averaged +4.6 per 100 on short throws in its other games. That explains part of the drop, and the adjusted number already accounts for it.
Fix: "…but the Bills' defense cut the gap we pointed at by more than half in one night. Even so, it still ranks 19th of 32 on short throws."

### 4. SHOULD FIX: "might be turning a corner" frames it as one game, but it's two
Text: "Its numbers jumped in one game; one game is a small sample."
Evidence: this is the second straight strong game. Week 8 against Baltimore allowed 10 points on 13 drives, and Monday allowed 6 on 12. The jump from 25th to 16th is real: 2.351 (25th) to 2.101 (16th), league 2.055. But teams ranked 13th through 20th sit between 1.93 and 2.23, so a small change moves the rank a lot. BUF at 2.1011 is tied with NE (2.1010) to three decimals.
Fix: keep the hedge, but say "two straight strong games (10 points to Baltimore, 6 to Minnesota)". Also note that the 25th-to-16th move happened in a tightly bunched middle of the pack. The "corner" wording itself is hedged enough to keep.

### 5. MINOR: "including last week's Sabres call"
P0001 was logged and graded on Sunday, Nov. 8, the day before this game. Fix: "including Sunday's Sabres call".

### 6. MINOR: "Both misses came from Minnesota's passing game"
This is accurate for P0006. P0004 (Vikings 20+) is a points call. Passing was most of the damage: -26.2 on dropbacks vs. -1.6 on designed runs. But the aborted-snap fumble (play 569, -6.0) and two failed fourth downs aren't dropbacks. Safer wording for the finding and hero note: "Both misses came from Minnesota's offense, mostly its passing game."

### 7. MINOR: "points of field position"
Text: "cost it about 26 points of field position". These values also count down, distance and turnovers, not just field position. Part 3 used "gain/lose points". Fix: "cost it about 26 points" or "26 points of scoring value".

### 8. MINOR: the "3rd-worst passing game" ranking
It's correct as stated in the stat-heads (per dropback, 3 of 272 team-games, 1 = worst). But the body pairs it with the total ("26 points … the 3rd-worst"). Ranked by total, Minnesota is 2nd-worst (-26.22, behind ATL wk2's -26.56). Ranked per dropback, #1 is TB in week 8 on only 5 dropbacks. Either "2nd-worst total of any team this season" or "3rd-worst per pass play" is clean. Pick one and say which.

### 9. MINOR: the hit rule text vs. code
The story says "more than 50%". The code uses p >= 0.5. No call is at exactly 50%, so nothing changes now. Make them match.

### 10. NOTE: P0006 aborted-snap play is outside both dropbacks and runs
Play 569 was Wentz's reversed incompletion, ruled an aborted fumble that Buffalo recovered (-6.0). nflverse tags it play_type run, pass=1, qb_dropback=0, rush=0, so clean_team_week counts it as neither a dropback nor a designed run. That's consistent with the model's definition, and the grade doesn't change. It's worth one line in the stat-heads because it's one of the 3 turnovers but isn't in the 26.

### 11. NOTE: Brier wording on P0002
"Including the one that matters most: the Bills win" is a 53% call, close to a coin flip, the same as the P0005 caveat. Optional: add "at 53%, close to a coin flip" so the receipts framing stays consistent.

### 12. Charts: fine, with one CLAUDE.md gap
- proj-vs-final: the numbers match (23.44 / 22.81; 80% ranges 11.6–35.8 BUF, 10.9–35.1 MIN). The title rounds MIN to "we said 23", while the body and hero say 22.8. That's acceptable but inconsistent. Sample size is missing from the footer (CLAUDE.md requires it). Add "80% range from 2,494 training misses".
- scorecard: the probabilities, hit/miss and colors all match the Ledger. Sample size is missing from the footer here too ("7 calls, 1 game").
- The chart subtitle "where we expected 8 games in 10 to land" is fine.

## What I verified (all match unless noted above)
- Final score: BUF 23, MIN 6 (raw_schedules). Drive points match the scoreboard: BUF 2 TD + 3 FG = 23, MIN 2 FG = 6.
- Projections: BUF 23.44 (raw 24.14 = 2.208 ppd × 10.93 drives), MIN 22.81. These match part 3 and the Ledger notes. "2.2 our model expected … the 11 it planned on" is correct.
- BUF drives: 13 (23/13 = 1.77, so "about 1.8"). The 13 include two end-of-half/kneel drives. The model's drive counts are built the same way, so the comparison is consistent.
- Grades. Every one matches clean_team_week, and also an independent raw_pbp recount (0 mismatches across all 272 2026 team-games):
  - P0002: 23 > 6, hit, Brier 0.2209
  - P0003: 23 ≥ 20, hit, 0.1369
  - P0004: 6 < 20, miss, 0.3721
  - P0005: BUF dropback +0.00293 total over 36 = +0.00008 per dropback > 0, hit, 0.1849. The 36 dropbacks are 31 attempts, 4 sacks and 1 scramble. No BUF dropback was wiped out by a penalty, and none has a null value. The result is the same under the qb_relative definition in this repo, so it holds under every repo definition. It's still a coin landing on its edge; the story says so and that's appropriate.
  - P0006: -26.22/33 = -0.795, miss, 0.4225
  - P0007: -3.347/39 = -0.086, hit, 0.1369
  - P0008: -1.583/11 = -0.144, hit, 0.0361
- Week: 5/7, Brier 1.5103/7 = 0.2158 (shown as 0.22). Season: P0001 (0.46 on BUF; BUF lost, so a hit) brings it to 6/8, Brier 1.7219/8 = 0.2152 (0.22). 50/50 baseline 0.25. Hero and site dek match.
- Ledger timing: P0002–P0008 were created at 12:48Z Nov 9, before kickoff (20:15 ET = 01:15Z Nov 10). Graded at 03:43Z Nov 11.
- Allen: 21/31, 234 yds, 1 TD, 1 INT (B.Murphy), sacked 4 times for 29 yds, plus 1 scramble for 5. That matches box-score convention (gross passing yards, sack yards separate). One sack-fumble (play 1609) was reversed on review, so BUF had only 1 turnover. The story doesn't mention the TD; that's fine.
- BUF designed runs: 39 for 132 yds (4 of them Allen keepers). MIN: 11 for 51.
- Interceptions: play 2455 by Dorian Williams (00-0038557, BUF), play 2952 by Terrel Bernard (00-0037254, BUF). Both correct.
- MIN turnovers: 3 (2 INT + aborted-snap fumble). Turnovers on downs: 2 (drives 22 and 24; the second was Brosmer's).
- Short throws: MIN 25 for -16.1; there are no null air-yards throws.
- "One game doesn't erase seven": BUF defense played 7 games through week 8. Correct.
- Defense points per drive: through week 8, 2.351 (181/77), 25th of 32, league 2.075. Through week 9, 2.101 (187/89), 16th, league 2.055. Correct.
- 272 team-games in 2026 through week 9: schedule and play-by-play both complete (15 week-9 games).
- Claims about earlier parts:
  - Part 1 said short throws were the Bills' weakest area (25th). Correct.
  - Part 3 said "best offense vs. best defense … mostly cancel out" and said the Wentz swap was the untested piece. Both correct.
  - Part 3 said the Vikings were "around 23, mostly from Murray's games and last season", with a range of 11–35. Correct.
  - The FTN claim is true: raw_ftn has 14 of 15 week-9 games, and BUF_MIN is missing (pulled 2026-11-10 12:14Z).
- Rarity: P(MIN ≤ 6) from training misses is 3.4%, and the out-of-sample one-sided rate is 3.2%. See issue 2 for the two-sided rate.
- Jargon and betting: there's no betting language. The stat-terms (EPA, Brier, residual) appear only in the stat-heads section. "Dropbacks" appears in the body but the earlier parts used it too, which is acceptable.
- AS_OF pin: the generator pins THRU=9, and the projections use PRE_THRU=8. A later nflverse revision could still change clean_drives and play values. The P0005 margin of +0.003 is fragile to that, but the Ledger grade is already recorded.
