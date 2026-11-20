# Quant review: 2026-11-21-nfl-mismatches-home (stage 2)

Reviewed text: sha256 2840f7520db80b07... (md5 14245f22b1e9ddbb3cc04129a39226c0), hero JSON, both PNGs, site card `nfl-mismatches-home`.
Independent recompute: /tmp/qv/q.py reads `raw_schedules` directly and rebuilds the pregame margins with its own per-season loop. It does not use `pregame_margins` or the generator.

**Verdict: FAIL (publish with fixes).** Every number re-derives exactly, and there is no betting content. But the headline and the home-field section claim something the data contradict: that home field matters *more* in mismatches. Two other absolute claims ("rivalries don't change them", "came out the same") go further than the data allow.

## Issues (ranked)

### 1. "Home field makes mismatches far more lopsided" / "worth more than you'd guess" is contradicted by the data (must fix)
- Text (headline): "Home field makes NFL mismatches far more lopsided."
- Text (Home field): "In the lopsided ones it's worth more than you'd guess: with a gap of 17 or more, the better team won 88% at home and 73% on the road, a difference of 15 points."
- Chart 1 title: "Lopsided games are a lot more lopsided at home"
- Problem: the home/road difference is about the same at every size of gap, and the story's own chart shows it. The difference is better-team-at-home win rate minus better-team-on-the-road win rate:
  - 0-3: 59% vs 46% (+13); 3-7: 68% vs 53% (+15); 7-10: 72% vs 62% (+10); 10-14: 78% vs 65% (+13); 14-17: 81% vs 68% (+13); 17-20: 89% vs 71% (+17); 20+: 87% vs 74% (+13).
  - All 5,205 games: better team at home 70.1% (n=2,542), on the road 57.2% (n=2,663), so +13.
  - The +15 at 17+ is ordinary home field. It isn't extra, and nothing tests whether 15 vs 13 is a real difference.
- What is true: at 17+ the home/road difference is large (88% vs 73%, z = 3.8). The final scores are also more lopsided at home: the better team's median margin is +12 at home vs +7 on the road, and it won by 17+ in 42% of home games vs 27% of road games.
- Fix: reframe it as home field mattering just as much in mismatches. It doesn't fade when one team is far better. Headline suggestion: "Home field still matters in NFL mismatches: 88% at home, 73% on the road." Replace "worth more than you'd guess" with something like "worth about as much as in any other game: the better team does about 13 points better at home than on the road at every size of gap, and 15 at 17 or more." Retitle chart 1 so it reads on its own, e.g. "The better team wins more often at home, at every size of mismatch." If you keep "more lopsided", tie it to the final scores (median margin 12 vs 7).

### 2. "Rivalries don't change them" / "came out the same as any other game" is absolute; the home/road split differs inside division games (should fix)
- Text: headline "Rivalries don't change them."; lead "Division games ... came out the same as any other game."; hero note and site dek "Division games came out the same as any other".
- Pooled numbers verified: 17+ division 80.1% (171), other 78.9% (249), z = 0.3. 10+ division 74.8% (660), other 73.5% (927).
- Problem: with 171 games the uncertainty is about +/-6 points, so "the same" really means "no measurable difference". Underneath the pooled numbers, division games show a smaller home edge. Division: home 86% (72) vs road 76% (99), +10. Other games: home 89% (111) vs road 71% (138), +19. These are small groups and I wouldn't headline them, but the pooled match partly comes from two opposite moves cancelling out. "Don't change them" is stronger than the data.
- Fix: "Division games came out about the same as other games (80% vs 79%)" and headline "...Rivalries barely matter." / "Division games aren't closer." The section title "Rivalry games aren't closer" is fine. Optionally add in the stat-heads section that the home edge is smaller in division games (small samples).

### 3. Bills 4-2 vs Miami: correct, but a small sample with no label, and it splits by venue (should fix)
- Games, Bills better by 10+ with both teams 4+ games played:
  - 2016 Wk7 Bills at Miami, lost 25-28 (gap 12.5)
  - 2019 Wk7 Miami at Bills, won 31-21 (31.6)
  - 2019 Wk11 Bills at Miami, won 37-20 (19.2)
  - 2021 Wk8 Miami at Bills, won 26-11 (28.9)
  - 2024 Wk9 Miami at Bills, won 30-27 (19.1)
  - 2025 Wk10 Bills at Miami, lost 13-30 (15.5)
- That's 4-2: 3-0 at home and 1-2 in Miami. Six games is a handful. The record is also below the league's 75% for division games at 10+, which sits awkwardly in a section arguing division games aren't closer.
- Fix: label it ("a small sample: six games"). Consider adding "3-0 in Buffalo, 1-2 in Miami", which ties it to the home-field point.

### 4. "a difference of 15 points" (fix)
- Text: "a difference of 15 points."
- Problem: in a story about scoring margins in points, readers will take this as 15 points on the scoreboard.
- Fix: "15 percentage points" or "about 15 more wins per 100 games".

### 5. The lead's Sunday framing implies 88% next to the published 81% (should fix)
- Text: "Sunday's game, Dolphins at Bills, is the home kind: the gap between the two teams is 18.2 points a game."
- The gap of 18.2 is correct: BUF +9.78, MIA -8.44, 9 games each through Week 10, matching the first story. The schedule confirms `2026_11_MIA_BUF`, 2026-11-22, Bills at home.
- Problem: readers will take 88% as the Bills' chance. The first story (and any Ledger call) gives 81% from our model, which already includes home field, and says "about 4 times in 5". Leaving the two numbers side by side unexplained looks like a second, unlogged prediction. Brand rule 2: only logged probabilities count.
- Fix: add one sentence: "Our model, which already counts home field, gives Buffalo 81% (logged on the Ledger); this history is context, not a second forecast." The 17-20 home bucket alone is 89% (n=98) if it's needed.

### 6. Minor
- Cold note: 28 of 29 is correct, but there's no comparison. Add "vs. 84% (85 of 101) when it was warmer than 40°F" so a fan can judge it. The missing temperatures are 5 of 135 (3.7%), all from 2022-2023.
- "lopsided matchups don't usually end in blowouts": 42% of the better team's wins were by 17+, and 33% of all 420 games (140). This is true if blowout means 17+, but the cutoff is arbitrary. Better to say "by 17 or more" outright, which the next clause already does.
- Chart 1 has no per-bar sample sizes (bins run from 85 to 788 games). Consider adding n under the x labels or in the footer. The total 5,205 is in the subtitle.
- 15 games with a gap of exactly 0 count as "better team on the road" (`bh = hm > am`). They are only in the 0-3 bin and don't affect any published number, but they are filed under a "better team" that doesn't exist. Drop them, or note it in the stat-heads section.
- The generator docstring says the query includes "rest" columns. It doesn't: the columns are game_id, season, week, weekday, teams, scores, div_game, roof, temp. Fix the docstring. The stat-heads line is accurate.

## Brand rule #1
- Columns read: `game_id, season, week, weekday, home_team, away_team, home_score, away_score, div_game, roof, temp` (generator), plus whatever `pregame_margins` takes from that frame. No spread_line, total_line, moneyline or result. My own recompute also never selects them.
- Grep of the md, hero and generator for favorite/underdog/line/cover/odds/spread/pick/bet/lock/over-under/wager: the only hits are "We don't use betting lines" (the disclaimer, same as the first story) and '"Throw out the records" is a common line for division games'. That one isn't betting usage, but "line" next to a betting disclaimer reads badly. Suggest "a common saying".

## Verified (my recompute = published)
- Sample 5,205; 17+ n=420 (333-86-1), 0.794, consistent with the first story.
- 17+ home 0.880 (161-22, n=183); road 0.728 (172-64-1, n=237); road losses 64 of 86.
- Home team overall 0.561 (ties as half).
- Division 17+ 0.801 (171) / other 0.789 (249); 10+ 0.748 (660) / 0.735 (927).
- Upsets: n=86, median losing margin 5, 8 or fewer 0.651 (7 or fewer 0.640).
- Wins: n=333, 17+ 0.420, 8 or fewer 0.357, median 13 (mean 15.0).
- Chart 2 buckets: 10 / 20 / 56 / 1 / 119 / 74 / 140 (sum 420). Matches the PNG.
- Chart 1 bars all match my per-bin home/road rates.
- Cold: 135 outdoor home games for the better team, 5 with no temperature (3.7%), 29 at 40°F or below, 28 wins.
- Parity, 14+: 1999-2019 0.778 (631); 2020-2025 0.724 (156). z = 1.4, so "could be chance" is the right hedge.
- Bills-Dolphins gap 18.2 (through Week 10, the same pin as the first story); Bills 4-2 vs Miami (games listed above).
- Hero JSON (88% / 73%, bars 0.88 / 0.728) and site dek numbers match.
- Reproducibility: a clean copy (/tmp/qv/clean, repo without .git plus the same DB) re-run reproduces the md, hero JSON and both PNGs byte-for-byte.
- Both charts viewed: no overlaps, footers carry the source, subtitles carry the sample sizes.
- No Ledger writes. No jargon in the body.

---

# Round 2 (after editor round-1 fixes), text sha256 5f8aa600a68f...

**Verdict: PASS (stage 2).** Every round-1 issue is fixed or no longer applies, and every number in the new text re-derives from my own recompute. One wording problem is left: "17-point rout" (below). It is small, but it blocks the stage-4 final check on this text.

**Round-1 issues:**
1. "Worth more than you'd guess" is fixed. The new text says the home edge ran 10 to 17 points higher in every group. My edges by bin are +13.2, +14.7, +9.5, +12.9, +12.5, +17.5 and +12.7, and the published figures round them correctly (0.0952 rounds to 10, 0.1746 to 17).
   - The new chart 1 title, "At every size of mismatch, the better team wins more at home", matches the data and reads on its own.
   - The new headline, "Even a much better NFL team wins far less often on the road", is supported: 73% vs 88%, so the team loses about twice as often on the road (27% vs 12%).
2. "Rivalries don't change them" is gone. "Rivalry games aren't any closer" is supported (80% vs 79%, z = 0.3). "Came out the same" is still slightly absolute; "about the same" would be better (optional).
3. Bills 4-2 vs Miami now carries "too few games to read much into". The games are as listed in round 1, and "from 1999 to 2025" is correct.
4. "A difference of 15 points" is gone. "Win rate ... ran 10 to 17 points higher" is tied to the win rate, which is acceptable. "Percentage points" would be clearer (optional).
5. The Sunday reconciliation is added:
   - Bills +9.8 and Miami -8.4 give a gap of 18.2 (9 games each, through Week 10). The game is `2026_11_MIA_BUF`, in Buffalo on 2026-11-22.
   - The 81% is read by regex from the first story's "Our model's number: Bills 81%" line, and that matches.
   - "Our model already counts home field" is true: `src/ledger/points_model.py` fits score = a + b*raw + c*home.
   - "Doesn't take early-season margin at face value" matches the first story's description of the model: blended with last season and pulled toward average. The first story's shrinkage finding (the gap ends about 23% smaller) supports "tends to shrink".
6. Minor items: the cold note is now explicitly 17+. Parity is removed. My recompute of 17+ 1999-2019 vs 2020-2025 is 0.797 (n=347) vs 0.781 (n=73), matching the stat-heads line. The cold-note comparison, per-bar n on chart 1 and the gap-0 note were not adopted. All optional.

**New-text checks:**
- "Typical upset was decided by 5 points (half were closer, half wider)": 39 under 5, 7 at exactly 5, 40 over 5. Correct as a description of the median.
- Chart 2 subtitle is new; its numbers are unchanged (10/20/56/1/119/74/140). Both PNGs viewed: no clipping, and the subtitle fits.
- Hero labels ("Much better team on the road won"; explainer title with the 17+ definition) and the site card (88/73, "our model's chance for the Bills is 81%") match.
- Brand: no market columns read; same disclaimer only. "Common line" is still there. It isn't betting usage, but "a common saying" would be cleaner (optional).
- Reproducibility: a clean copy (/tmp/qv/clean2) reproduces the md, hero and both PNGs byte-for-byte.

**Remaining issue (blocks the final check):**
- Text: "When the much better team won, it was a 17-point rout 42% of the time"
- Problem: "a 17-point rout" reads as a win by exactly 17. The 42% is wins by 17 or more: 140 of 333, of which only 17 were by exactly 17.
- Fix: "it won by 17 or more 42% of the time and by one score (8 or fewer) 36% of the time."

**Operational note (not a text defect):** the 81% Bills-Dolphins call is not in `ledger/predictions.csv` yet (last entry P0019). This story and the site card now call it "our published chance". Brand rule 2 requires it to be logged before kickoff, 2026-11-22.

# Stage 4 final check on sha256 5f8aa600a68f...: FAIL

Everything that changed since round 1, and everything those changes touch, was verified as above, except the one wording issue: "17-point rout". Change that phrase as suggested, regenerate, and get the editor's round-2 pass recorded (only an editor fail is on file). The final check then needs re-running on the new text. I expect a pass if nothing else changes.

---

# Round 3 / stage 4 final check, text sha256 fe97a0fd04ea...

Record note: the quant-pass and final-fail entries above carry sha fe97a0fd04 rather than 5f8aa600. The story was regenerated (editor round 2) between my round-2 review and my `record` calls. The round-2 findings apply to 5f8aa600. The entries below supersede them.

**Changes since round 2, all verified:**
- Home edge: "in every group on the chart, the better team won 10 to 18 more games out of every 100 at home than on the road".
  - It is computed from the chart's rounded labels: 59-46=13, 68-53=15, 72-62=10, 78-65=13, 81-68=13, 89-71=18, 87-74=13. So 10 to 18 matches what a reader sees on the chart.
  - Unrounded, the range is 9.5 to 17.5. Using the chart's rounded labels is the right choice, because the text then agrees with the chart.
  - This also fixes my round-1 issue #4: no more "points" ambiguity.
- Sunday: "Sunday fits the group that won 88% of the time. That describes past games, not a forecast: our published chance for Sunday is still 81%."
  - 88% is the 17+ home group (161-22, n=183), and the Bills-Dolphins game fits it: gap 18.2, in Buffalo.
  - 81% matches the first story. With the "why" sentence removed, there are no unsupported claims about the model.
- Wins: "it won by 17 or more 42% of the time and by one score 36% of the time". 140/333 = 0.420 and 119/333 = 0.357. One score is defined in the previous sentence as 8 points or fewer. This resolves the "17-point rout" issue.
- Generator diff: only `edge_shown` and these three text changes. The hero JSON, site card and both PNGs are byte-identical to round 2.
- A clean copy (/tmp/qv/clean3) reproduces the md, hero and both PNGs byte-for-byte.

**Final check: PASS on fe97a0fd04ea.**

Still open (operational, not a text defect): the Bills-Dolphins 81% is not in `ledger/predictions.csv`. Log it before kickoff on 2026-11-22. Both stories and the site card call it published.
Optional polish (not blocking): "came out the same" could be "about the same"; "a common line" could be "a common saying".

---

# Stage 4 final check, text sha256 ce79453f06b2...

The only change since fe97a0fd04 is the Sunday line, which now reads "...our model's chance for the Bills on Sunday, from the first story, is 81%." It is accurate: the 81% is read by regex from the first story's "Our model's number: Bills 81%" line. The "17 or more 42% / one score 36%" wording is unchanged from fe97 and was verified there.

The generator diff is this one string. The hero JSON, site card and both PNGs are byte-identical. A clean copy (/tmp/qv/clean4) reproduces the md, hero and both PNGs byte-for-byte. No new betting language.

**Final check: PASS on ce79453f06b2.**

Still open: the change of wording doesn't change brand rule 2. The 81% Bills-Dolphins chance is a public model probability, and it is not in `ledger/predictions.csv`. Log it before kickoff on 2026-11-22.
