# Quant re-check (stage 2, round 2): reports/2026-wk10-bills-at-jets.md

Text checked: sha256 ff02a816ce8749d0bd23a266574b4cde41b0d56714a009b3e2f22bfd5d05d668. I didn't run the generator or the logger. The Ledger still has 11 predictions; nothing for week 10 is logged.

**Verdict: PASS.** Every number in the new text reproduces from my own scratch code. There's one small wording fix to make before the final check.

## My four fixes from round 1
1. **Two-point tries:** `pass_ranks` now has `COALESCE(two_point_attempt,0)=0`. The body says 0.26 over 273 (4th) and 0.16 over 312 (7th-most of 32), league 0.05. Stat-heads says +0.263 and +0.047. These match my numbers from raw_pbp (+0.2633/273, +0.1608/312, +0.0466). Fixed.
2. **The 0.23 paragraph:** it now uses 0.27, 0.19 and 0.05. 0.049 + 0.5 x (0.221 + 0.146) = 0.233, so 0.23. These are the model's game-averaged values, which I recomputed from clean_team_week (+0.2705, +0.1950, +0.0486). Fixed.
3. **"lines":** the word is gone from the body. Stat-heads now says "8 scorelines". The only "lines" left is "No betting lines are used", which is a disclaimer and fine. Fixed.
4. **Calls chart:** I looked at the new wk10-calls.png. The footer is "Matchup calls tested on 990 past team games; win chance on 632". Both are correct, and it no longer says the calls are logged. Fixed.

## The Editor's changes, checked
- **The two example plays:** I checked them in raw_pbp, game 2026_09_BUF_MIN, Bills on offense.
  - The completion is play 2588, Q3 3rd-and-8, 36 yards. Passer gsis 00-0034857 is Josh Allen; receiver 00-0035537 is Ty Johnson ("T. Johnson" is fine). EPA +3.775, so about 3.8.
  - The sack is play 132, Q1 3rd-and-14, -7 yards, Allen sacked. EPA -1.755, so about 1.8.
  - Neither play is a penalty or a two-point try. The asserts in example_plays() pin each to a single row.
- **The win-test sentence:** 70%+ bucket said 75.0%, won 74.0%, 102 games, ties counted as half. The win chart shows the same. "As it gives Buffalo Sunday" is right: Buffalo is at 74.7%, which is in the 70%+ bucket.
- **"pulls extreme projections like this 34":** the raw projection is 33.6, which rounds to 34. That matches "about 11 drives (10.92) ... about 34".
- **The Jets' blend:** their offense rates 1.805, so 1.81, and the Bills' defense 2.078, so 2.08. Then the home bump of 1.45 gives 22.08, so 22.1. Correct.
- **"Both sides tilt toward Buffalo":** Bills offense 2.73 is above the league's 2.05, and the Jets' defense 2.40 allows more than average. Points per drive 3.074, so 3.07. Correct.
- **The headline**, "Buffalo's passing game gets one of the NFL's leakiest pass defenses": the Jets are 7th-most allowed per pass play. This also fixes the "best offense" vs. "4th-best passing" tension.
- **Unchanged and still right:** the ladder (all 16 cells), 29.9 / 22.1 / 75%, the 80/55/66/75 calls, 134 games said 75 / happened 78, the 990-game backtest, 64% of runs losing points, the 632-game test (63% / 52%), the 1,744-case caveat (50 → 55), 2,494 misses, 1,247 pairs, the 18-42 range, "within 6 / 12", the average miss of 7.5, the ranks (19th, 16th, 1st, 6th-most), and "5 of 7".
- **Logger:** log_wk10.py is unchanged and still pulls `points_block()` and `matchup_calls()`, which this round didn't touch. It would log 0.75 / 0.80 / 0.55 / 0.66 / 0.75, matching the story.
- **Hero JSON and dek:** unchanged and consistent (30, 22, 75%, 4th, 7th-worst, 134, 0.754/0.776).
- **Brand:** no betting language. The body uses plain decimals with no "EPA", and the jargon stays in the stat-heads section.

## Fix before the final check (wording only)
- **"they're still shown in the ladder, flagged, but not logged until fixed. The ladder has the same issue: ..."**
  - Nothing in the ladder table or chart flags the 20+ row; the only flag is this paragraph.
  - "The ladder has the same issue" right after "still shown in the ladder" also reads as a repeat.
  - Suggested: "We haven't fixed it yet, so we're not logging them; they're still in the ladder above, with this caveat: on games the model never saw, when it gave a team a 40-60% chance ..."
  - Alternatively, add a marker to the 20+ row.

## Note for the final check
After the logger runs, `ledger_status()` swaps in the "Logged on ... before kickoff" sentence. That changes the text's sha256, so the final check has to be on the post-logging text. Also confirm that the logged rows are 0.75 / 0.80 / 0.55 / 0.66 / 0.75 and that created_at_utc is before 2026-11-15 18:00Z.
