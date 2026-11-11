# Quant review (stage 2): reports/2026-11-10-hooker-trade.md (v2, Bishop's-partner angle)

## Verdict: PUBLISH WITH FIXES

Every published number reproduces from my own code (raw_pbp, raw_snap_counts, raw_pfr_def, raw_player_week). The angle can stand.
What fails is the framing around the numbers. The Poyer vs. Gardner-Johnson gap is at the edge of game-to-game noise. It is
partly a story about which quarterbacks Buffalo faced. Hamlin's +0.40 comes almost entirely from two games against backup or
emergency quarterbacks. Issues 1-4 must be fixed before publishing.

---

## Ranked issues

### 1. MUST FIX: Hamlin's +0.40 (and "+0.23 without MIN") come from facing backup QBs. The text implies the opposite.
**Text:** table row `Damar Hamlin, 2026 | 3 | +0.40 (better, see below)`; "Leave that game out and the Hamlin stretch is still +0.23."
Chart bar: Hamlin +0.40, the largest bar, with no caveat.
**Evidence (per game, + = better than the opponent's norm):**
- Wk 6 LV (Kirk Cousins, Las Vegas's regular starter): **-0.19**. This is the only Hamlin game against a team's usual QB, and it was as bad as the Gardner-Johnson games.
- Wk 8 BAL: +0.78. Buffalo faced J. Fagnano (25 dropbacks) and T. Huntley (5), with L. Jackson on 1. Baltimore's norm (+0.121) is built largely on Lamar Jackson's weeks 1-4.
- Wk 9 MIN: +0.77. Carson Wentz started. Minnesota's other games were mostly Kyler Murray.
- So "+0.23 without MIN" means LV (-0.19) plus a backup-QB BAL game (+0.78). With a starting QB, Hamlin's stretch is -0.19.
- 2026 weeks 1-6, all against starting QBs: -0.18. Weeks 8-9: +0.78. Within 2026, timing and opponent explain the swing at least as well as partner does.

**Fix:** In the asterisk paragraph, replace the "+0.23" sentence with: "Two of the three came against quarterbacks their teams
didn't plan to start: Baltimore was down to its third option, and Minnesota started Carson Wentz. In the one Hamlin game against a
regular starter (Las Vegas), the defense was 0.19 worse than normal." Change the table cell to "+0.40 (3 games, 2 vs. backup QBs)".
On the chart, label the Hamlin bar "3 games, 2 vs. backup QBs", or grey it out.

### 2. MUST FIX: "lived and died with whoever plays next to Bishop" and the chart title overclaim cause
**Text:** lede and dek "The Bills' pass defense has lived and died with whoever plays next to Cole Bishop"; chart title
"Cole Bishop's partner has made or broken the Bills' pass defense"; body "The difference was around him, which is exactly the kind
of problem a better partner fixes."

**Noise check, Poyer (9 games, 283 dropbacks) vs. Gardner-Johnson (5 games, 221):** observed gap 0.30 per play.
- Per-game spread: SD 0.34 (Poyer) and 0.17 (Gardner-Johnson). League team-game SD in 2025 is 0.32. Welch t on game means = 2.13.
- Bootstrap over games: 95% interval for the gap is 0.06 to 0.53, and P(gap ≤ 0) = 0.8%. Poyer alone: -0.06 to +0.31, which includes zero. Gardner-Johnson alone: -0.29 to -0.02.
- Permutation test (shuffle the 14 games between the two labels): two-sided p = 0.063.
- League benchmark: split each 2025 defense's games at random into 9 and 5. A gap of 0.30 or more shows up 6.3% of the time (median 0.11).
- Verdict on noise: probably bigger than noise, but only at the margin.

**Confounds the text doesn't mention in the body:**
- The partner split is the season split. Poyer and Rapp = 2025 (McDermott/Babich). Gardner-Johnson and Hamlin = 2026 (Leonhard DC). Scheme, corners and pass rush all changed with it.
- The one same-season comparison, Poyer vs. Rapp in 2025 (+0.13 vs. +0.01), is pure noise: permutation p = 0.40.
- Opposing QBs: two of the Poyer games were against backups. CAR played Andy Dalton (+0.54) and HOU played Davis Mills (+0.25). Without them Poyer is **+0.05** over 7 games. All 5 Gardner-Johnson games were against regular starters (Stroud, Goff, Herbert, Maye, Stafford).

**Fix:** Keep the angle and soften the cause. Lede: "The Bills' pass defense has tracked with whoever plays next to Cole Bishop".
Chart title: "The Bills' pass defense has tracked Cole Bishop's partner". Drop "which is exactly the kind of problem a better partner
fixes". Use instead: "The difference was around him. The partner is one piece of that, along with a new defensive coordinator, the
cornerbacks, the pass rush and who was at quarterback." Add a short "How we checked it" paragraph. The plain-English version: "If you
shuffle these 14 games at random between the two partners, a gap this big shows up about 1 time in 16. Two of Poyer's best games
also came against backup quarterbacks; take them out and his number falls to +0.05." Label every row as a small sample (5-9 games).

### 3. MUST FIX: PFR numbers are labeled "through week 9" but run through week 8
**Text:** "Numbers are through week 9 of the 2026 season." The chart 2 subtitle says "Interceptions, 2026 weeks 1-9".
**Evidence:** raw_pfr_def for 2026 week 9 covers only 2 teams (BAL, JAX: the Thursday game). Weeks 5-8 cover 28-32 teams, as byes
allow, and no played team-game in weeks 1-8 is missing. Tennessee is unaffected: its bye was week 9, it played weeks 1-8, Hooker
played weeks 1-4 and 6-8, and the TEN totals are complete. The league average (7.23 vs. 7.235 on weeks ≤ 8), the TEN rank (29th)
and the tackling rank also come out the same. The pass-defense and nflverse interception numbers really do run through week 9. In
PFR, McKinney shows 3 INTs because GB's week 9 (2 INTs vs. NE, confirmed in play-by-play) hasn't been charted.
**Fix:** In the dateline: "Play-by-play numbers are through week 9. Pro Football Reference charting (yards per throw, tackles) is
through week 8, since week 9 isn't posted yet." Leave the chart 2 subtitle as is (Tennessee's season is complete through week 9),
or add "(Tennessee's bye was week 9)". In stat-heads, say McKinney's tie is from nflverse play-by-play/player stats (5), not PFR (3 so far).

### 4. MUST FIX: no league context next to the Bills numbers (CLAUDE.md "Always give context")
**Evidence (my code, same opponent-adjusted method applied to all 32 defenses):**
- +0.13 (Poyer) would rank about 6th of 32 among 2025 team-seasons. -0.17 (Gardner-Johnson) would rank about 31st of 32 in 2025 or 2026.
- Range across teams: 2025 from +0.21 to -0.25; 2026 from +0.25 to -0.20. League team-level SD is about 0.12.
- Bills full-season figures: 2025 +0.09 (9th); 2026 through week 9 +0.01 (14th).

**Fix:** Add a line under the table: "For scale: over a full season, +0.13 would be about a top-6 pass defense and -0.17 about
31st of 32. Overall, Buffalo was 9th in 2025 and is 14th so far in 2026."

### 5. SHOULD FIX: "betting" language (brand rule 1)
**Text:** lede "Amani Hooker is the fix the Bills are betting on". Dek (build.py) "is the fix they're betting on". Body bullet
"**The bet is on the pair, not just the player.**"
**Assessment:** This is a figure of speech, not wagering content: no odds, spreads or picks. It doesn't strictly break rule 1. But
on a brand defined by "no betting content", "bet" shows up three times, once in a bold header, and a skim reader or radio host will
hear it as gambling talk. Recommend changing all three: "the fix the Bills are counting on"; "**It's about the pair, not just the
player.**"

### 6. SHOULD FIX: Bishop's coverage numbers lack context and "Bishop's 2025 went well" has no number behind it
**Text:** "Bishop's 2025 went well, and so did the pass defense around him." "Bishop himself barely changed: ... 8.8 yards per throw
with Poyer next to him and 9.2 with Gardner-Johnson."
**Evidence:** I reproduced 27 targets / 238 yds = 8.81 and 21 / 193 = 9.19. League safeties allowed 8.55 yds/target in 2025 and 8.29
in 2026 through week 8 (my position mapping from snap counts). So both Bishop figures are a little worse than an average safety. His
full-season numbers are 8.26 (2025, 43 targets) and 7.39 (2026, 31 targets). "Barely changed" holds, but on 21-27 targets it is a
small sample. Nothing computed shows his own 2025 "went well".
**Fix:** "Bishop's own numbers barely changed ... (an average safety allows about 8.3-8.6; both samples are small, 21-27 throws)".
Replace "Bishop's 2025 went well" with "Last season the pass defense around Bishop was good".

### 7. SHOULD FIX: "with Bishop on the field" is not what is measured
**Text:** "Here's how the defense did with Bishop on the field, by who played next to him"; chart subtitle "with Bishop and each
partner on the field".
**Evidence:** The metric uses every Bills defensive dropback in the game, including snaps when Bishop or the partner was off. Bishop
played 75-91% in several counted games: 2025 week 6 79%, week 14 75%; 2026 week 1 91%, week 8 88%. In 2026 week 6, Gardner-Johnson
also played 42%.
**Fix:** "in games where Bishop and that partner played most of the snaps".

### 8. MINOR: Pairing assignments
- All four counts and play totals reproduce: Poyer 9 games / 283 dropbacks (weeks 8-16), Rapp 6 / 194 (1-6), Gardner-Johnson 5 / 221 (1-5), Hamlin 3 / 105 (6, 8, 9). Chart total 803.
- 2025 has no misassignments. Week 6 ATL: Rapp 96%, Bishop 79%, Poyer 26%, so Rapp is correct.
- Excluded games: 2025 week 17 PHI is excluded because no other S-labeled player reached 50% (Savage 2%). Cameron Lewis, labeled DB in snap counts, played 100% that day, and 100% / 92% in weeks 9-10. He was effectively a third safety in some Poyer games. Week 18 is excluded because Bishop played 15%.
- 2026 week 6 (Hamlin 68%, Gardner-Johnson 42%): assigning it to Hamlin under the stated rule is sensible. It was a mixed game, though. Moving it to Gardner-Johnson leaves him at -0.18. Mention it in stat-heads: "week 6 was shared: Hamlin 68%, Gardner-Johnson 42%".
- Stat-heads says "safeties (S/FS/SS)". The code also accepts SAF. All Bills rows are "S", so this changes nothing.

### 9. MINOR: The explainer lacks a worked example and the "how we checked it" step (CLAUDE.md writing rule)
Suggested real example from my numbers: "The Rams usually gain about 0.01 points per pass play. Against Buffalo in week 5 they threw
55 times and gained 19.4 points, about 19 more than normal, or 0.34 a play." Then add the noise check from issue 2.

### 10. MINOR: Hero JSON big number
"-0.17 / Bills pass D per play with Gardner-Johnson" has no reference point. Use "Bills pass defense vs. opponents' norm, per play,
with Gardner-Johnson". "Pass D" is mild jargon. The hero explainer's Hamlin bar (0.4) needs the same backup-QB note as issue 1.

---

## Verified (independent code, /tmp/q_*.py)
- Opponent adjustment: norm = opponent's dropback EPA in its other games (2026 weeks ≤ 9), vs = EPA - norm × dropbacks. The method is sound, the plain-English description is accurate, and the sign is right. Poyer +0.128, Rapp +0.009, Gardner-Johnson -0.174, Hamlin +0.399, Hamlin without MIN +0.229. No spikes among dropbacks; two-point tries excluded. Garbage-time filtered (WP 10-90%): Poyer +0.17, Rapp -0.01, Gardner-Johnson -0.13, Hamlin +0.41, so the direction holds.
- Bishop coverage by partner: 8.81 on 27 and 9.19 on 21.
- Tennessee: 2176 yds / 265 targets = 8.21, 29th of 32 (league 7.23). Hooker 274 / 33 = 8.30; rest 8.20 on 232.
- Interceptions: TEN 8 in PFR, nflverse player stats and play-by-play. Hooker 5 in all three. Rest 3. McKinney 5 in nflverse and play-by-play (PFR 3: week 9 not charted). Nobody has more than 5.
- Hooker: 7 games (weeks 1-4, 6-8); seasons 2019-2026 = 8th season; 17 career regular-season INTs.
- Tackling: 3 missed / 55 attempts = 5.5%. I built my own safety universe from snap-count positions (55 safeties with 15+ targets vs. the generator's 58). Hooker ranks 16th there, untied. Pooled safety average 8.9%. "Tied for 16th of 58" depends on the universe but is consistent.
- 9 Bills games left (weeks 10-18).
- No jargon in the body (EPA, dropbacks and r appear only in stat-heads).
- Trade facts: the text matches the previously verified terms (2027 2nd for Hooker + 2027 5th, Nov. 10, signed through 2028, "most draft capital ... at the trade deadline under Beane"). I did not re-fetch buffalobills.com in this pass.
- Charts viewed. Both are readable and on-brand. Chart 1 needs the issue 1, 2 and 7 fixes.
