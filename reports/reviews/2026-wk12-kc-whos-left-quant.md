# Quant review (stage 2, round 2): 2026-wk12-kc-whos-left

**Verdict: PASS.** All six round-1 must-fixes and both should-fixes are in, and every number matches my independent recompute. Round 1 is saved as -quant-r1.md.

## Round-1 items, checked again
1. **Justin Reid.** The weekly roster shows him as NO ACT through week 10, then NO CUT in weeks 11 and 12. The text "Justin Reid (released by New Orleans)" and the chart label "Released by New Orleans" are correct. Leaving out "last week" is fine. The stat-heads line ("Week 12 weekly roster (CUT, DEV)") is accurate, because Reid has a week-12 CUT row.
2. **Targets.** I filtered on pass_attempt=1, sack=0 and two_point_attempt=0 and got:
   - **Chiefs (316 total):** Kelce 57 (18%), Worthy 54 (17%), Rice 44 (14%), Walker 36 (11%), E. Johnson 27 (9%).
   - **Bills (287 total):** Shakir 54 (19%), Moore 48 (17%), Kincaid 41 (14%), Coleman 40 (14%), Ty Johnson 26 (9%).
   - **Title-game targets:** 35.1% for KC and 71.4% for BUF.
   - Every figure matches the story.
3. **Week 11.** The schedule has 163 games through Week 11 and the snap counts have 162. The missing game is 2026_11_CIN_WAS (Monday Nov. 23). The generator asserts this, and the text, the stat-heads and the chart footer all disclose it. The play-by-play has both KC's and BUF's Week 11 games.
4. **Positions.** Every defensive back is now labeled "DB", so the Bishop problem is gone. The DB counts are unchanged: KC lost 4 of 6, BUF 3 of 5.
5. **Overclaims removed.** "Buffalo has a new defensive coordinator" and "The sideline changed too" are both supported.
6. **Elam and Watson.** Elam is LAC DEV in weeks 9-12, so "the Chargers' practice squad" is right. Watson is LA RES from week 9, so "injured reserve" is right.

## Unchanged and still verified
- Snap counts: 13 of 21, 12 of 23, 8 of 10, 5 of 11, 6 of 11, 6 of 12, 4 of 5 offensive linemen, 58% (Danna, 42 snaps).
- 22 months; "about half" (11 of 23); "most familiar group" (80% kept, the highest of the four units).
- The coaching claims and their links (sources are in -quant-r1.md).
- The hero JSON and site card agree with the body.

## Reproducibility
A clean copy with the outputs deleted and the generator re-run reproduced the md, the hero JSON and the PNG byte-identically. The md sha256 is 89e48fb2…

## Note (not blocking)
Roster status is joined on pfr_id, and many offensive linemen have no pfr_id in raw_rosters_weekly. As a result a lineman's release or IR stint wouldn't be labeled. That doesn't matter for this story: Edwards, Thuney and Taylor are all ACT by name. The asserts pin the current state.
