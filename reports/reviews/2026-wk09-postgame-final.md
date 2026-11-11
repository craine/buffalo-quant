PASS

# Quant final check (stage 4): reports/2026-wk09-postgame.md (Bills 23, Vikings 6)

Everything was re-derived read-only from raw_pbp, clean_drives, clean_team_week, raw_schedules and ledger/*.csv. I did not run the generator. Every number in the current text reproduces. The rewrite added no betting language and no jargon in the body (a scan of the body found "bet" only inside "between" and "better"; EPA, Brier and dropback appear only in the stat-heads section). None of the issues below blocks publishing.

## Issues (all minor; optional)

1. **Rounded numbers in the "gaining points" box don't add up.** Text: "about 4.1 points ... could expect about 0.2 ... cost the Vikings about 4.2 points." Evidence: play 2455 (Q3 13:17, MIN 1st-and-10 at BUF 37) has EP 4.056 and EPA -4.206. Buffalo's next play (2482) has EP 0.151, which equals -(ep+epa), so the sign logic is correct. But a fan who does the math gets 4.1 + 0.2 = 4.3, not 4.2. Fix: "could expect about 0.15", or "a little over 4 ... cost about 4.2".
2. **The scorecard chart footer says "154 plays".** That count includes 9 kickoffs, 10 punts, 7 kicks, 4 kneels, 1 spike and 3 rows with no play type. There were 120 offensive runs and passes (that matches clean_team_week.plays). Fix: "120 offensive plays", or drop the count and use "7 calls, 1 game".
3. **Carried over from stage 2, issue 6 (not fixed, not blocking).** "Both misses came from Minnesota's passing game" appears in the lead and the hero note. P0004 is a points call. Passing cost -26.2, but the aborted-snap turnover (-6.0) and two failed fourth downs weren't pass plays. "came mostly from" would be more exact.
4. **Note only.** EP is the expected net points of the next score, not literally points "from the drive". It's a fair simplification for fans, and the stat-heads section names EPA, so no change is needed.

## Verified
- **Interception example:** play 2455, Dorian Williams, 3rd quarter. EP before 4.06 ("about 4.1"), EPA -4.21 ("cost about 4.2"), Buffalo's EP after 0.15 ("about 0.2"). The other two MIN-side interceptions are the Williams one and Bernard (play 2952). Play 542 (B.Murphy) was Allen's interception, so "Allen ... 1 interception" is correct.
- **League runs:** designed runs (rush=1, not scrambles, play_type run, no 2-pt tries), 2026 weeks 1-9, regular season: 6,622 runs, mean -0.0804. 272 team-games, and 67.3% had rush EPA sum below zero. clean_team_week (off side) gives identical results.
- **Wentz** (gsis 00-0032950): 25 dropbacks, 8/24, 81 yards, 2 INT, 1 sack. Brosmer: 8 dropbacks. No Murray snaps. The Murray-out / Wentz-start line is sourced to ESPN (O'Connell, Nov. 5) in 2026-wk09-wentz-vs-bills-defense.md, line 149.
- **BUF:** 39 designed runs for 132 yards, -3.35 EPA. Allen's one scramble (play 2693) and a no-play are excluded. Allen 21/31, 234 yards, 1 INT, 4 sacks. 36 pass plays, +0.0029.
- **MIN passing:** -26.22 over 33 pass plays, -0.795 per play. That ranks 3rd-worst of 272 team-games per play (TB wk8 on 5 dropbacks, ATL wk8, then MIN). 25 short throws (the spike is excluded), -16.1.
- **MIN runs:** 11 for -1.58 ("about 2"). Drives: 3 turnovers, 2 turnovers on downs, 2 FGs, 5 punts.
- **Points per drive allowed:** BUF through week 8 2.351 (25th), through week 9 2.101 (16th). League 2.055 ("2.05"). BAL 10 points on 13 drives, MIN 6 on 12. BUF scored 23 on 13 drives. Nov. 15 at NYJ is confirmed in raw_schedules.
- **Ledger:** P0002-P0008 outcomes and Brier scores match grades.csv. 5 of 7 this week; Brier 1.5103/7 = 0.2158. With P0001 (46% on BUF, VGK won, so a hit): 6 of 8, 1.7219/8 = 0.2152. All created_at times (Nov. 9, 12:48Z) are before the 01:15Z kickoff. Probabilities in the table and chart match predictions.csv.
- **Charts:** proj-vs-final (23.4 and 22.8, finals 23 and 6, 80% bands about 11.6-35.8 and 10.9-35.1, footer n=1,234) and scorecard (7 bars, 5 blue / 2 gray) both match. Site dek and hero JSON are consistent with the body.
