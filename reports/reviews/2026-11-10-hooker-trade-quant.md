# Quant review, stage 2: reports/2026-11-10-hooker-trade.md

Branch wk09-postgame. Data: data/buffalo.db (read-only), 2026 through week 9 (all week 9 games final, including BUF 23 at MIN 6 on Nov 9). I re-derived everything from raw_player_week, raw_pfr_def and raw_schedules with my own code. I did not run the generator, so no files were written.

## Verdict: PUBLISH WITH FIXES (substantive)

Every printed number reproduces exactly. The problem is the story built on them. Its main selling point, "a sure tackler," rests on 3 missed tackles in 7 games. His three prior seasons were average, and by the story's own logic those prior seasons are the better guide. The claim that "tackling carries over better" doesn't hold up once you allow for noise. The claim that he "beats Buffalo's safeties" leaves out that Cole Bishop, the safety he will play next to, allowed fewer yards per target than Hooker this season. The way safeties are identified also misses some well-known ones.

## Ranked issues

### 1. "A sure tackler" is a one-season, 7-game claim, and the story's own argument undercuts it (HIGH)
Text: headline Finding "What the Bills are getting is a sure tackler"; section "**A sure tackler.**"; "steady starter who tackles well"; hero note "a sure tackler"; site dek "What the Bills are getting: a sure tackler."
Evidence (PFR, safeties with 25+ targets per season; 2026 uses 15+):

| Season | Missed / attempts | Rate | Rank (1 = fewest misses) | Safety avg |
|---|---|---|---|---|
| 2023 | 8 / 93 | 8.6% | 32 of 66 | 8.7% |
| 2024 | 6 / 74 | 8.1% | 30 of 66 | 8.7% |
| 2025 | 8 / 87 | 9.2% | 42 of 63 | 9.0% |
| 2023-25 pooled | 22 / 254 | 8.7% | 38 of 72 (60+ tgt) | 8.9% |
| 2026 | 3 / 55 | 5.5% | tied 15th of 54 | 8.8% |

The 2026 figure is 3 misses. One more miss would make it 4/56 = 7.1%. The story says one season "tells you a little about the next one, not a lot," and that applies to his 2026 tackling as much as to his interceptions. His longer record says he is an average tackler.
Fix: Drop "sure tackler" from the Finding, hero and dek. Say: "He's missed 3 of 55 tackle attempts this season (5.5%, a small sample), better than the average safety's 8.8%. Over 2023-25 he was about average (8.7% vs. 8.9%)." Change "ranks 15th" to "tied for 15th." Label 55 attempts and 7 games as a small sample.

### 2. "Tackling carries over a little better" is not supported (HIGH)
Text: "The best of a weak bunch is tackling ... scored 0.30"; "**Watch the tackling.** It carries over a little better than the rest of a safety's numbers."
Evidence: The 288 pairs come from only 110 players. Each middle season appears twice, once as "this year" and once as "last year," so the pairs are not independent. A bootstrap that resamples by player (2,000 draws) gives:
- Interceptions 0.26 (95% interval 0.15 to 0.35)
- Missed tackles 0.30 (0.15 to 0.43)
- Yards per target 0.19 (0.06 to 0.31)
- Completions 0.15 (0.04 to 0.25)
- Missed tackles minus interceptions: -0.14 to +0.20. Missed tackles come out ahead in only 69% of resamples.

The order flips when you check it other ways:
- One pair per player (n=110): interceptions 0.35, missed tackles 0.26.
- Rank-based (Spearman): interceptions 0.27, missed tackles 0.24.

The point estimate itself is computed correctly, and 2026 partial seasons are correctly left out (the latest "next" season is 2025).
Fix: Say interceptions and tackling carry over about equally, and both only a little. Remove "a little better" and the "best of a weak bunch" ranking. Rewrite the "Watch the tackling" bullet so it doesn't depend on tackling being the most predictable stat. The chart can keep its order but should not be described as a ranking.

### 3. "His numbers beat what Buffalo's safeties have given up" leaves out Bishop and needs sample labels (HIGH)
Text: Finding "Even so, his numbers beat what Buffalo's safeties have given up this season"; "Hooker's numbers beat both"; hero "whose coverage beats what Buffalo's safeties have allowed."
Evidence: The Bills total (69 targets, 670 yards, 9.71 per target; 11 missed of 109 attempts, 10.1%) reproduces. By player:

| Bills safety | Targets | Yds/target | Missed tackles |
|---|---|---|---|
| Cole Bishop | 31 | 7.4 | 5/50 (10.0%) |
| C.J. Gardner-Johnson | 21 | 10.4 | 6/32 (18.8%) |
| Damar Hamlin | 13 | 13.2 | 0/21 |
| Kilgore | 2 | 22.0 | (n/a) |
| Stone | 2 | 3.5 | (n/a) |

The high Bills average comes from Gardner-Johnson and Hamlin. Bishop allowed fewer yards per target than Hooker (7.4 vs 8.3). Per buffalobills.com, Hooker will play next to Bishop, so in practice he is replacing Gardner-Johnson or Hamlin. The comparison also uses Hooker's 2023-25 numbers against Buffalo's 2026 numbers, which are different seasons.
Fix: Compare Hooker with the players whose snaps he takes. For example: "In coverage he's allowed less than Gardner-Johnson (10.4 yards per target) and Hamlin (13.2), though not Bishop (7.4)." Label all of these as small samples (13 to 31 targets each; 69 for the whole group). Add the league average beside the Bills team numbers, as CLAUDE.md requires: league safety groups allow 8.2 per target and miss 8.2% of tackles. Soften the hero line to match.

### 4. The way safeties are identified misses players (MEDIUM; numbers change a little, fix and disclose)
The method requires PFR's name to match nflverse's name exactly. Checks:
- **Exact-match failures on suffixes and nicknames.** 212 nflverse safety-seasons have no PFR match. 63 come back with a normalized name match (removing Jr./II/III and punctuation). Examples:
  - Jessie Bates (PFR "Jessie Bates III"): dropped every season 2018-2026, including 26 targets in 2026.
  - Darnell Savage Jr., Rodney McLeod, Lonnie Johnson Jr., Ronnie Hickman (22 targets in 2026), Rayuan Lane (16 in 2026), Rodney Thomas II, Kevin Winston.
  - First-name differences: "Kam Curl" vs "Kamren Curl" (2020-2026, 19 targets in 2026) and "C.J." vs "Chauncey Gardner-Johnson" (NO 2019-21, 51 to 94 targets a season).
- **Players labeled "DB".** These are left out entirely. In 2026 that includes real safeties such as Jeremy Reaves, Theo Jackson, Jalen Thompson and P.J. Locke (Daxton Hill and Chamarri Conner are hybrid players). DB labels are common in 2018-2021 (92 to 116 per season), so the 2018-25 carry-over sample is thinner in the early years.
- **OAK/LV.** PFR uses OAK for 2018-19 and nflverse uses LV, so every 2018-19 Raiders safety is dropped. CLAUDE.md says to normalize this.
- **Name variants within a matched player.** Rows are matched by name, so weeks where PFR spells the name differently get dropped. This costs 10 rows and 11 targets in total (Swearinger 2019 and others), none in 2026. A visible example is Bills CB "Dee"/"DeAundre" Alford, who is not a safety.
- **Duplicate names.** None among safeties. The only PFR duplicate is NYJ 2023 Michael Carter (an RB and a CB).
- **Mid-season movers** are handled correctly. Rows are summed by PFR id across teams (Byard, Dugger, Gardner-Johnson 2025, and others). No safety moved teams in 2026. Hooker's TEN rows are complete: 7 games, weeks 1-4 and 6-8. TEN had its bye in week 9, and Hooker has no row in week 5 from either source.
- **Bills 2026 safeties:** Bishop, Gardner-Johnson, Hamlin, Stone and Kilgore are all correctly included. Sam Franklin Jr. is labeled SAF but has no PFR rows. Te'Cory Couch and Kani Walker are labeled DB and correctly left out. Bills numbers are the same under every version I tried.

Sensitivity (writer's method / normalized names / normalized names plus all DBs):
- 2026 Hooker yards per target rank: 29 of 54 / 31 of 57 / 35 of 63
- 2026 missed-tackle rank: 15 / 16 / 19
- 2023-25 rank: 53 of 72 / 56 of 75 / 73 of 92
- Carry-over pairs: 288 / 305 / 394
- Interceptions: 0.258 / 0.266 / 0.304; missed tackles: 0.302 / 0.298 / 0.330; yards per target: 0.191 / 0.181 / 0.149; completions: 0.152 / 0.121 / 0.092
- Bills team ranks: 8th and 7th / 8th and 7th / 8th and 10th

Fix: Match on normalized names (or an id crosswalk) and normalize OAK to LV. Then regenerate. Disclose in the stat-heads section that safeties nflverse labels "DB" are left out. Also, the stat-heads section says "nflverse rosters," but the source is weekly player stats.

### 5. The "0 = not at all, 1 = perfectly" scale is fair as an anchor but invites a misreading, and there is no real example (MEDIUM)
A correlation of 0.26 means one season accounts for about 7% of the variation in the next (r²). Readers will tend to read 0.26 as "26% of the way to perfect." CLAUDE.md asks for a real computed example. Here is one: among safeties with 25+ targets in back-to-back seasons who had 5 or more interceptions in a season (n=21, PFR counts), the average was 5.5 interceptions that year and 2.5 the next. The average across all pairs was 1.9. That also gives "Don't expect five more" a computed basis, which it currently lacks (issue 6).
Fix: Keep the scale but add the 5.5 to 2.5 example in the body. Note that it uses full seasons and PFR interception counts.

### 6. Forward-looking claims with no numbers behind them (MEDIUM)
- "**Don't expect five more.**" Nothing in the code computes this. Use the 5-or-more to 2.5 example above, and say it covers a full season. Hooker has about 8 games left.
- "steady starter" and "a reliable safety for this season and two more." In 2025 he was 55th of 63 in yards per target (11.4). "Reliable" overstates his record. Suggest "a starter who's been average-to-below in coverage."
- "If Hooker's tackling travels to Buffalo, the defense that just held Minnesota to 6 points gets sturdier at the back." The 6 is correct (2026_09_BUF_MIN, home score 6). This is a hedged forecast, but it relies on the tackling claim in issue 1. Rewrite it along with that fix.
- Omission worth adding: 3 of his 5 interceptions this season came in one game (week 8 at CIN). That supports "they come in bunches" well.

### 7. Trade facts: mostly verified, one wording drift (LOW)
Both buffalobills.com articles from Nov. 10, 2026 ("Bills land impact safety Amani Hooker in trade with Titans" and "'A difference maker'...") confirm:
- Buffalo sends a 2027 2nd-round pick to Tennessee for Hooker and a 2027 5th-round pick. The trade is official, dated Nov. 10, deadline day.
- He is signed through 2028 ("two years remaining after 2026").
- He has 17 interceptions in eight seasons with Tennessee and 5 this season, tied for the NFL lead through nine weeks.

Drift: the source says "the most draft capital the team has used to acquire a player in-season **at the trade deadline** under Beane." The story says "spent on an in-season trade," which is broader. Fix: use the source's wording.
The story adds no other outside facts. "Tuesday": Nov. 10, 2026 is a Tuesday.

### 8. Interception figures: correct, with a scope note (LOW)
- nflverse regular season by year, 2019 to 2026: 0, 4, 1, 1, 1, 5, 0, 5 = **17**. This matches the Bills.
- He also has 1 playoff interception (2021 Divisional). "17 interceptions in 8 seasons" should say "regular-season."
- NFL lead: Hooker 5 (7 games) and Xavier McKinney (GB) 5 (9 games) are tied. Next are four players with 4. This is correct in nflverse.
- PFR's charting differs from nflverse: it has McKinney at 3 in 2026 and Hooker at 3 in 2020. The carry-over analysis uses PFR interceptions while the career totals use nflverse. Note this in the stat-heads section.

### 9. Charts (LOW)
- **hooker-ints.png**
  - The "N games" labels count games where he recorded a stat, not games played. They sum to 97, but the Bills say 103 regular-season games. 2019 shows "10 games."
  - Fix: relabel as "games with a recorded stat" or remove the labels. The body's "0 in 2025 over 16 games" has the same problem.
  - The footer credits PFR, but this chart uses only nflverse.
  - Otherwise clean and readable. Bills blue marks 2026, and the footer gives the sample (17 career).
- **hooker-carryover.png**
  - Its numbers match. It shows 288 pairs. The footer defines each rate.
  - Two notes: the order invites a "missed tackles is best" reading that the data doesn't support (issue 2), and the title is fine.
  - Add the number of players (110) beside the 288 pairs, because the pairs aren't independent.

### 10. Brand rules
- **No betting language.** Checked.
- **Jargon.** "Correlation" appears only in the stat-heads section. The body uses "thrown at" and "per target," which is acceptable.
- **Missing small-sample labels:**
  - Hooker's 55 tackle attempts (3 misses)
  - Bills safeties' 69 targets and 109 tackle attempts
  - Individual Bills safeties, if added
  - The 15-target cutoff for 2026 ranks
  - 5 interceptions in 7 games, 3 of them in one game
  - Hooker's 33 targets are already labeled.
- **No Ledger calls** in the story, so there is nothing to reconcile. Consistent with the week 9 postgame story (MIN scored 6).

## Verified (all reproduce exactly)
- **Interceptions:** Hooker 2026: 5 in 7 games. By season: 2024: 5 (14 games with a stat); 2025: 0 (16). Career 17 regular season. Tied with McKinney.
- **Hooker 2026 coverage and tackling:** 33 targets, 274 yards, 8.30 per target, rank 29 of 54. Safety average 8.01 (pooled). Missed tackles 3/55 = 5.45%, rank 15 (tied) of 54. Safety average 8.82%.
- **Hooker 2023-25:** 158 targets, 1,432 yards, 9.06 per target, rank 53 of 72. Average 8.21.
- **Bills safeties 2026:** 69 targets, 9.71 per target, 8th-most of 32. Missed tackles 10.09%, 7th-most.
- **Carry-over:** n=288 pairs, 2018-2025, 110 players. Interceptions 0.258, yards per target 0.191, completions 0.152, missed tackles 0.302. 2026 is excluded.
- **Hero JSON and site dek:** numbers match (5, 17, 0.30/0.26/0.19/0.15). The wording problems are in issues 1 and 3.
- **Trade terms:** match buffalobills.com except the "in-season" wording (issue 7).

## Possible memory items (from this review, not from memory)
- PFR and nflverse names don't match for Jr./II/III suffixes and some first names (Jessie Bates III, Kamren Curl, Chauncey Gardner-Johnson). PFR uses OAK for 2018-19 while nflverse player stats use LV.
- nflverse labels many safeties "DB," roughly 100 per season in 2018-21. A safety filter on SAF/FS/SS/S misses them.
