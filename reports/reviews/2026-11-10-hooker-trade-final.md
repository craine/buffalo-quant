FAIL (two quick wording fixes; every number reproduces)

# Quant final check (stage 4): reports/2026-11-10-hooker-trade.md

I re-derived everything with my own code (/tmp/qf/*.py, read-only DB connection). I did not run the generator. Every number in the body, the stat-heads section, the hero JSON, the dek and the three charts reproduces. Two wording problems overstate the evidence. Both are one-line fixes and need no new analysis.

## Ranked issues

### 1. "The 22 safeties" is really 22 seasons by 16 safeties (MEDIUM, factual)
Text: body "The 22 safeties with five or more interceptions in a season averaged 5.5 that year"; chart hooker-bigyears.png subtitle "The 22 safeties with 5+ interceptions in a season".
Evidence: n=22 player-seasons from 16 players.
- Repeat entries: Simmons appears 3 times (2020, 2021, 2022). Byard, Diggs, Fitzpatrick and H. Smith appear twice each.
- Hooker's own 2024 season (5 interceptions, then 0 in 2025) is one of the 22. That makes a nice example if the writer wants one.
Fix:
- Body: "The 22 times a safety had five or more interceptions in a season (16 different players), he averaged 5.5 that year."
- Chart subtitle: "22 seasons with 5+ interceptions (16 safeties), 2018-2025."

### 2. "Big interception years don't repeat" is absolute (LOW-MEDIUM, overclaim)
Text: chart title on hooker-bigyears.png; hero note "Big interception years don't repeat"; image alt text.
Evidence:
- 3 of the 22 seasons were followed by another 5+ season: Diggs 2020 (5 then 5), Simmons 2020 (5 then 5), Simmons 2021 (5 then 6).
- The next-year average of 2.5 is still above the 1.7 for all safeties, so a little does carry over. The body handles this correctly with "Mostly, no."
Fix: Change to "Big interception years rarely repeat" in the chart title, the hero note and the alt text. Optionally add "(3 of 22 did)."

### 3. Two different "average safety" figures sit side by side (LOW)
Text:
- "The average safety misses 8.9%" and "close to the average safety's 8.1"
- then "league average 8.2" and "league average 8.2%" for safety groups.
Evidence: Both are correct, but they use different groups:
- 8.9% and 8.06 come from safeties thrown at 15 or more times (n=58).
- 8.2% and 8.24 come from all 125 matched safeties pooled by team. Safeties thrown at fewer than 15 times miss only 6.4%, which pulls that average down.
A reader will see "average safety 8.9%" and then "league average 8.2%" in the next paragraph.
Fix: Label the second pair "league average for all safeties' combined numbers," or add one short clause explaining the difference.

### 4. "Even a return to his average would help there." (LOW, forecast depends on an unknown)
Evidence: His 2023-25 rate (8.7%) is below the Bills group's 10.1% and Gardner-Johnson's 19%. But Hamlin is 0 for 21, a small sample. Whether this would help depends on whose snaps Hooker takes, and the story itself says that is still unknown.
Fix: "His usual rate (8.7%) is below the Bills group's 10.1%," or "That would help if he takes Gardner-Johnson's snaps."

### 5. "coverage scored lower" (LOW, optional)
Point estimates of 0.18 and 0.11 are lower than 0.27. However, the yards-per-throw range (0.06 to 0.29) overlaps the interceptions range (0.17 to 0.37). The next sentence ("could be off by about 0.1 either way") mostly covers this. You could change it to "coverage scored a bit lower."

## Check 1: matching (passes)
- Independent rebuild gives 1,085 linked safety-seasons, 12 of them from the first-initial-plus-last-name fallback. Carry-over: 318 pairs from 118 players, 2018 to 2025-next. 2026 is excluded from the pairs.
- **All 12 fallback matches are correct:**
  - Kamren/Kam Curl, 2020-26 (7 seasons)
  - Chauncey/C.J. Gardner-Johnson, NO 2019-21 (51, 94 and 61 targets)
  - Kameron/Kam Kelly, PIT 2019
  - Christopher Smith / Chris Smith II, LV 2024
  - No false matches.
- **Jessie Bates III** is matched for every season 2018-2026 (26 targets in 2026). Name variants under one PFR id are now included because the join is on the id. Example: Quan/Jartavius Martin, WAS 2023.
- **2018-19 Raiders:** now present (Gilchrist, Harris, Joseph, Nelson, Joyner, Riley, Swearinger, the last on ARI/LV/NO).
- **Hooker:** gsis 00-0035632 / HookAm00. Malik Hooker is kept separate. His 2026 TEN rows cover weeks 1-4 and 6-8 (7 games).
- **One-to-many:** the only collision on the same team and season is the NYJ 2021-23 "Michael Carter" pair (RB and CB). It is dropped and involves no safeties. No PFR id links to two safeties, and no safety links to two PFR ids.
- **Still unmatched:** 118 of 1,203 nflverse safety-seasons. On the same team, none have a plausible PFR counterpart. The remaining cases are players with no PFR rows (e.g., Lonnie Johnson CAR 2024, Chris Smith II LV 2023) or different people who share a surname. Players labeled DB are still left out, and the stat-heads section discloses this.

## Check 2: numbers (all reproduce)
- **Carry-over scores:** interceptions 0.274, yards per throw 0.184, completions 0.111, missed tackles 0.303.
  - My bootstrap (different seed): 0.18-0.36, 0.07-0.29, 0.00-0.22, 0.17-0.41. Half-widths are 0.09 to 0.12, so "about 0.1 either way" holds.
  - Missed tackles finish ahead of interceptions in 63% of resamples.
  - Rank-based check: interceptions 0.29, missed tackles 0.25. That supports "about equally."
- **Five-plus seasons:** 22 seasons, 5.55 that year, 2.55 the next. All pairs averaged 1.74 the next season. "Much closer to the 1.7 than to their big year" is supported: 0.8 away from 1.7 versus 3.0 away from 5.5.
- **Hooker 2026 tackling:** 3 missed of 55, 5.5%. Average for safeties with 15+ targets is 8.94%. He is tied (2 players) for 16th of 58. One more miss would make it 7.1%.
- **Hooker 2026 coverage:** 33 targets, 8.30 yards per throw. Average 8.06. He ranks 31st of 58, and 29.5 is the midpoint, so "right in the middle" is supported.
- **Hooker 2023-25:** 158 targets, 9.06 yards per throw. Average 8.19. He ranks 57th of 76. Missed-tackle rate 8.66% (40th) against an average of 8.88%.
- **Hooker 2025:** 11.44 yards per throw, 58th of 66.
- **Bills safeties 2026 (group):** 69 targets, 9.71 yards per throw, 8th-most of 32 teams. 11 missed of 109, 10.09%, 8th-most. League averages 8.24 and 8.22%.
- **Bills safeties 2026 (by player):**
  - Bishop: 31 targets, 7.39 yards per throw, 5/50 missed
  - Gardner-Johnson: 21 targets, 10.38, 6/32 missed (18.75%, shown as 19%)
  - Hamlin: 13 targets, 13.23, 0/21 missed
- **Interceptions (nflverse):**
  - By season: 0, 4, 1, 1, 1, 5, 0, 5, for 17 career regular-season.
  - 2026 by week: 2 = 1, 6 = 1, 8 = 3. Week 8 was CIN 43, TEN 36, played at Cincinnati.
  - He is tied with Xavier McKinney at 5. Next best is 4.
- **"9 regular-season games left":** BUF had its bye in week 7, played 8 games through week 9, and has one game in each of weeks 10-18 (9 games). Correct.
- **Hero and dek:** 5, 17, 0.27/0.30/0.18/0.11, and "about 2.5" all match. Wording is consistent with the body except issue 2.

## Check 3: wording and brand rules
- Nothing the stage-2 review removed has come back: no "sure tackler," no "carries over better," and no claim that he beats Bishop or all Bills safeties. The text says Bishop allowed fewer yards per throw than Hooker.
- No betting language.
- Correlation, bootstrap and Pearson appear only in the stat-heads section. "Targets" is defined in plain English.
- Small samples are labeled: 33 throws, 55 tackle attempts, 69 group throws, and the individual Bills safeties.

## Check 4: trade facts
The text matches the wording verified at stage 2:
- 2027 2nd-round pick for Hooker plus a 2027 5th-round pick, on Nov. 10, deadline day
- signed through 2028
- "most draft capital ... at the trade deadline under Beane," which is now the source's exact wording
- will play alongside Bishop

A fresh web search did not bring up the buffalobills.com articles again, so these rest on the stage-2 check. Public reports of his 2025 three-year extension are consistent with "signed through 2028."

## Charts
- **hooker-ints.png:** correct. The "7 games" is right, the source line is now nflverse only, and the week-8 note is correct.
- **hooker-bigyears.png:** numbers are correct. The subtitle and title need issues 1 and 2. The footer shows the sample.
- **hooker-carryover.png:** numbers and ranges are correct. It shows 118 players, and the "overlap = no real difference" note is good.

---

# Re-check after fixes (stage 4, round 2): PASS

I re-read the current story, hooker-bigyears.png, the hero JSON and the build.py dek. I did not run the generator.

## The five fixes
1. **Counts.** The body now says "The 22 times a safety had five or more interceptions in a season (16 different players)". The chart subtitle says "22 seasons with 5+ interceptions (16 safeties), 2018-2025". Both match my independent count: 22 seasons, 16 unique PFR ids. The code computes both values in carryover() (ex['players'], ex['repeat']).
2. **"Rarely repeat (3 of 22 did)."** This matches my count of next-season interceptions at 5 or more: Diggs 2020 went 5 then 5, Simmons 2020 went 5 then 5, Simmons 2021 went 5 then 6. The chart title, hero note and alt text all say "rarely repeat".
3. **League average comparison.** The text now says "all NFL safeties combined: 8.2 / 8.2%". The added explanation, "lower than the 8.9% above because safeties who are rarely thrown at miss fewer tackles", is supported. Safeties with fewer than 15 targets in 2026 missed 6.4% of tackles (67 players). Safeties with 15 or more missed 8.94%, and all of them pooled missed 8.22%.
4. **Tackling comparison.** The text now says "His usual rate over the three seasons before this one (8.7%) is below the Bills group's 10.1%." Both figures are correct (8.66% and 10.09%). It is a plain comparison and no longer reads as a forecast.
5. **"coverage scored a bit lower".** Fine.

## Nothing else changed
- Headline, intro, trade paragraph, tackling and coverage sections, the Bills by-player figures, the "What it means" bullets (other than fix 4) and the stat-heads section are identical to the version I checked in round 1. All their numbers still reproduce.
- The hero numbers (5, 17, 0.27/0.30/0.18/0.11) and the dek are unchanged and still correct.
- The chart numbers (5.5, 2.5, 1.7, 318 pairs) are unchanged.

## Optional grammar nit (does not block)
"...(16 different players), he averaged 5.5 that year. The next year they averaged 2.5" switches pronoun from "he" to "they". A possible rewrite: "those seasons averaged 5.5 interceptions; the next year, 2.5".
