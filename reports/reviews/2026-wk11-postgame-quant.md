# Quant review (stage 2): 2026-wk11-postgame

**Verdict: FAIL (don't publish until the must-fix items are done).** Story text reviewed: sha256 574b13cf... (the self-check version).
Every number was rebuilt with my own pandas/SQLite queries against data/buffalo.db (raw_pbp, raw_schedules) and ledger/*.csv. I did not use the generator's output.

## Must-fix (ranked)

1. **Bass did not make "all 4" field-goal tries. He made 4 of 5.** raw_pbp `field_goal_attempt=1, posteam='BUF'`: 43 made, 54 made, 54 **missed** (Q3 7:37), 40 made, 28 made.
   The generator's `b_fg` counts makes only.
   - Current: "Tyler Bass made all 4 field-goal tries."
   - Replace: "Tyler Bass made 4 of 5 field goals; he missed from 54 yards in the third quarter."

2. **The efficiency numbers leave no-plays in.** CLAUDE.md's play filter excludes no-plays, and the wk09/wk10 generators do too (`play_type <> 'no_play'`). Five penalty-cancelled plays are in this game's sample (two MIA, three BUF, including a cancelled Allen interception at Q2 0:13). With no-plays out:
   - Miami: **-0.26 points per play over 55 plays, 22nd-worst of 316 team games**, success rate **25%**. The story has -0.21 / 57 / 33rd / 28%.
   - Buffalo: **+0.04** over 75 plays, 181st of 316. The story has +0.02 / 78. "About average" still holds (league team-game mean +0.002).
   - Current: "Miami's offense averaged -0.21 points per play over 57 plays, the 33rd-worst of 316 team games this season.\nOnly 28% of its plays gained enough to count as successful."
   - Replace: "Miami's offense averaged -0.26 points per play over 55 plays, the 22nd-worst of 316 team games this season.\nOnly 25% of its plays gained enough to count as successful." Make the same change in the hero bar (-0.21 to -0.26), the stat-heads line (-0.262, 0.255, rank 22) and "Buffalo's offense averaged +0.04 points per play".
   - Fix in code: add `& (p.play_type != "no_play")` to `pl`.

3. **Garbage time isn't disclosed, and it changes the Allen story.** CLAUDE.md says to report numbers with and without garbage time and to say which one a headline uses. Filtered to win probability 0.10-0.90 (`wp`, Bills' view), Allen was **18 of 25 against about 15.9 expected (+8 points)**. Only **1 of the 5** "easy misses" (Q2 14:10) falls inside that window. The other four came with Buffalo up 14+ (Q2 1:45 up 17, 1:14 up 14, 0:38 up 14, Q4 2:47 up 14).
   The 0.10-0.90 filter is crude here. The three two-minute-drill throws before halftime are real football at a 14-17 point lead, so I don't think the headline has to change. It does have to disclose this.
   The Q4 2:47 throw to D.Moore deserves its own note. Buffalo led 23-9, its win probability was 99.8%, and the throw was a -4-yard pass behind the line (a screen-type ball, where drops and batted balls are common). It is the weakest case in the table for blaming Allen.
   - Add to the body after the table: "Four of the five came with Buffalo already up by 14 or more: three in the two-minute drill before halftime and one with under three minutes left in a 23-9 game. In the moments when the game was still in doubt, Allen completed more than an average quarterback would have."
   - Add to stat-heads: "Unfiltered numbers above. Win probability 0.10-0.90 only: 25 throws, 18 completions vs 15.9 expected (CPOE +8.4); 1 of the 5 cp>=0.70 misses is in that window."
   - Table row: add a note on the 4th-quarter row, e.g. "Incomplete (Bills up 14, 2:47 left)".

4. **The career rank isn't pinned and will change without anyone noticing.** The career query (`car`) has no season/week limit. Once week 12 loads, "32nd-worst of his 133" changes on re-run, which breaks "Published stories never change silently" in CLAUDE.md.
   The generator also has no `AS_OF`, unlike wk10.
   Fix: add `AND (season < 2026 OR (season = 2026 AND week <= 11))` to `car`, and add an `AS_OF` string ("Sunday evening, Nov. 22: the late-afternoon, Sunday night and Monday games weren't in the play-by-play yet") used in the body and stat-heads.
   Related: the pregame projection is recomputed from today's data, not pinned. The stat-heads line already drifts from what was logged: **MIA 19.52 here vs 19.51 in the Nov. 19 story** (Ledger note: 19.5). Use the logged values, or pin the inputs.

5. **"Targeted" doesn't match what was counted.** All 45 attempts have air yards, but 2 have no receiver (Q1 12:30, Q4 4:19, thrown away). The depth numbers use all 45. Short share: game 30/45 = 66.7% (targeted only 29/43 = 67.4%); rest of 2026 62.6% all (targeted 62.1%, which rounds to 62%); league 67.2% (targeted 66.7%).
   - Current: "67% of his targeted throws went less than 10 yards, more than his 63% the rest of the season (league: 67%)."
   - Replace: "67% of his passes went less than 10 yards past the line, more than his 63% the rest of the season (league: 67%)."
   - Stat-heads: "0 attempt(s) had no air-yards value and are left out of the throw-depth numbers." is true but misleading. Replace with "2 attempts had no listed target (thrown away) and no completion chance; they're out of the expected-completions numbers but in the throw-depth numbers."

6. **League-context wording.** In the body, "316 team games this season" doesn't say that five week-11 games are left out. NYJ-LAC is final in raw_schedules (24-27) but wasn't in the play-by-play, so "not final at publish" in stat-heads is wrong for that game.
   - Body: "...the 22nd-worst of 316 team games this season (through Sunday's early games)."
   - Stat-heads: "League context leaves out week 11 games not in the play-by-play when this ran: ..."

## Should-fix

- "Five of his incompletions, one of them intercepted": an interception isn't an incompletion. Use "Five of his throws that fell incomplete or were picked off..." (the Editor has wording).
- The "8 and 15 yards downfield" interception depths are hard-coded literals in the f-string. They're correct, but compute them (`ints.air_yards`) so every number traces to code.
- `src/reports/wk11_postgame.py` and `src/ledger/grade_wk11.py` are **untracked**. Commit them with the story.
- Images aren't in `reports/published_images.json` yet. Run `freeze_images.py` at publish, as CLAUDE.md requires.
- The headline wording "left some easy throws on the field" assigns cause (see the Editor's review). The data shows incompletions, not whose fault they were.

## Verified (independently), correct as written

- Final 26-9, BUF home, 2026_11_MIA_BUF. **Record 9-1**: W at HOU, DET, LAC, at LA, at LV, BAL, at MIN, at NYJ, MIA; L to NE (wk 4); bye wk 7.
- **NOT_FINAL pin is right.** raw_pbp week 11 holds exactly 8 games (IND-HOU, MIA-BUF, BAL-CAR, NO-CHI, TEN-DAL, TB-DET, ARI-KC, PIT-PHI), each with END GAME. The 5 pinned games are exactly the ones missing.
- Allen (gsis 00-0034857): 48 dropbacks with pass_attempt=1, 3 sacks, so **45 attempts, 27 completions, 304 yards, 1 TD, 2 INT**. The punter T.Doman's fake-punt pass (Q1 7:19, 30 yds to Latu) is correctly not counted for Allen.
- Completion chance: 43 attempts with cp, **sum 28.90 (about 29), 27 completed**, CPOE -4.4. Rest of 2026: 243 attempts, +2.7.
- **Career rank 32 of 133** (REG, cp not null, 15+ attempts, per-attempt gap, rank min). Note: by total completions missed it would be 26th-worst. Worst game: 2024 wk5 at HOU.
- **Easy-miss table**: all 5 rows match on quarter, clock (14:10, 1:45, 1:14, 0:38, 2:47), down/distance, receiver (by id), air yards and cp (73/74/82/80/85%). The INT is the 1:45 throw to Latu.
- **Deep throws**: 7 deep (20+), 2 caught; by quarter 5/11, 1/19, 1/10, 0/5 (passes incl. throwaways). After Q1: 2 deep in 34. Both INTs in Q2 at 8 and 15 air yards.
- **Defense**: McCord was Miami's only passer (35 attempts). 2 sacks (both Rousseau), 1 INT (Hamlin, Q2 0:18), 0 TDs, 3 Carlson FGs.
- **Red zone**: 5 Bills drives reached the MIA 20 or closer (drives 1, 5, 7, 17, 19): 2 TD, 3 FG.
- **Ledger P0021**: created 2026-11-21T00:09:09Z, before kickoff 2026-11-22 13:00 ET (18:00Z); p=0.81, outcome 1, **Brier (0.19)^2 = 0.0361**; graded 2026-11-23T00:10:22Z. **13 of 20 graded calls right; 8 of 13 NFL**, and all 13 NFL calls are Bills games. P0017 and P0022 are ungraded and unresolved (TBL game not in raw_nhl_games).
- Projection 30.29 / 19.52 (logged 30.3 / 19.5); "11 fewer than expected" holds either way.
- Next game: KC at BUF, 2026-11-26 20:20 (Thanksgiving).
- **No betting language** (grep for spread/odds/favorite/underdog/cover/pick/lock/bet/vegas: none; "line" only means line of scrimmage).
- Jargon (EPA, CPOE, cp, air yards) appears only in stat-heads. "Percentage points below expected" in the body is borderline (see Editor).
- **Reproducibility**: a clean `git archive` copy plus the two untracked scripts, run against the same DB, gives byte-identical md, hero JSON and both PNGs (sha256 match).
- "Didn't stop throwing short" is right on the numbers (67% vs 63% for his season and 67% league-wide). Short share by quarter: 5/11, 13/19, 8/10, 4/5.
- **Open-receiver framing is fair.** Public play-by-play has no receiver separation or coverage data. All 5 easy misses were short throws (air yards -4 to 8), which backs the story's point: the issue wasn't skipping short receivers, it was short throws not connecting. Saying this in the body would answer Charlie's question more directly.

---

# Round 2 (md sha256 9afdd130057247ce00df2a73a3379caa9e959b1abd4e9d4ce14b2632c8d04b27)

**Verdict: PASS.** Every round-1 must-fix is in, and every number in the md, hero and card matches my own queries from round 1.

- Bass is 4 of 5, with the miss from 54 in Q3 (computed and asserted).
- No-plays are excluded. Miami -0.26 / 55 plays / 22nd of 316 / 25% (shown as "1 in 4"). BUF +0.04. Hero bar -0.26.
- Garbage time:
  - With win chance between 10% and 90%: 18 of 25 targeted throws, expected 15.9 ("about 16"). 1 of the 5 easy misses falls in that window.
  - 4 of the 5 easy misses came with the Bills up 14+, and 3 of those in the two-minute drill (all asserted).
  - The Score column matches score_differential: up 6, 17, 14, 14, 14. "23-9" matches the 4th-quarter score.
- "About 2 short" comes from 27 - round(28.9). The other nine games are +2.7 per throw, which supports "more than an average quarterback". Career rank 32 of 133 is now pinned through 2026 week 11.
- Projection now comes from P0021's logged notes and probability (30.3 / 19.5 / 0.81). "About 30 / 20" is fine.
- Depth: "passes" 67% / 63% / 67% are all-attempt shares, as labeled. Targeted-only rest of season is 62.1%, matching my receiver-based figure. The throwaway note is correct.
- The NOT_FINAL wording and "(through Sunday's early games)" are correct. The interception depths 8 and 15 are computed.
- 9-1, the P0021 timing and Brier, 13 of 20, 8 of 13, and KC on Thanksgiving are unchanged and still correct.
- No betting language. No jargon in the body.
- **Clean-copy reproduction:** `git archive HEAD`, plus the working-tree generator, grader, build.py and ledger CSVs, run against the same DB. The md, hero JSON and both PNGs are byte-identical (md 9afdd130..., hero c294a79b..., throws 3c78d3a8..., deep fbac6a32...).

Chart issue (presentation, not a number; it goes to the Editor and must be fixed before publishing): **chart 1's title is clipped at the right edge** ("...or were picked of").

Optional:
- "about 10 fewer than we expected": 19.5 - 9 = 10.5, and Python rounds half to even, so it prints 10. That's defensible, but "about 10 and a half" or "about 11" would remove any doubt.
- Still to do at publish: commit the untracked generator and grader, then run freeze_images.py.

---

# Round 3 (md sha256 9d8fe7e2c13aaf22580bfdd7171cd721e5bca93d428038ddc7948569d145f253)

**Verdict: PASS.** Compared with round 2, a diff of the clean-copy md shows only three lines changed, all text with no new numbers:
- Lead: "Four of those five came with Buffalo already up by 14 or more." The count is still asserted in code (easy_up14 == 4).
- "Two of his seven deep throws were caught." Still asserted (deep_c == 2, deep_n == 7).
- "about 10 and a half fewer than we expected." 19.5 - 9 = 10.5 exactly. The wording branch fires only when the gap is exactly 10.5, so it's correct.

The hero JSON and chart 2 are unchanged. Chart 1 changed only in its title. The scatter, labels and footer (43 throws) are as verified in round 2.
