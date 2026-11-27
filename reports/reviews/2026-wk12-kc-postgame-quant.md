# Quant review, round 4: 2026-wk12-kc-postgame (stage 2)

**Verdict: publish.** Story sha256 68ec3c001e8aafe1229e2563ac8247f8a259e625f6425aa4e5d0323ca7b56f35, commit a16a0435. Round 3: -quant-r3.md.

## Round-3 must-fixes
1. Field-goal window: now 2018 on, asserted, and disclosed in stat-heads. My numbers still match: 11 late winners, Bass 2, every other kicker 1; all 11 kicking teams won (raw_schedules). Fixed.
2. Cook: carries now come from raw_pbp_history + raw_pbp. Independently: 7 Bills games with 32+ carries since 1999 (McGahee 37 2004, Henry 35 2002,
   F. Jackson 33 2009 (33 by name too), Henry 32 2003, McCoy 32 2017, Cook 32 x2). The last game with more than 32 is 2009_17_IND_BUF, so "No Bill has carried more
   in a game since Fred Jackson's 33 in 2009" and the hero "no Bill has had more since 2009" are correct. Fixed.
3. "Won a game in its last 10 seconds" now matches the definition (tied or down 1-2, made). Fixed.
4. Chart renamed to bills-kc-wk12-postgame-wp.png and frozen (96d56453...); tests/test_published_images.py passes. Removing the old
   entry is correct: bills-kc-wk12-postgame.png was never on main (git log main has no commit touching it), so it was never published and `--change` doesn't apply.

## New numbers
| Claim | Mine |
|---|---|
| Started at 55% | first home_wp 0.5525 |
| 57-yarder 76% to 100% | pre-kick 0.761, wpa +0.239 |
| Punt return about 22 points | +0.216 for BUF |
| +64 / +20 / -36 / -33, penalties -3 | +63.6 / +20.0 / -36.2 / -33.1 / -2.7; 0.552 + 0.637 + 0.200 - 0.362 - 0.027 = 1.000 |
| Punt netted 13 | line of scrimmage KC 31 (yardline_100 69), punt out of bounds at KC 44, before the 5-yard penalty |

Unchanged claims re-checked as in round 3: Cook 32-117, 56% vs 43%, TD streak 10, 57+ at 60% on 205, Bass's 2nd game with two 54+ makes,
Butker 46 at 6:01 tied, Dortch 17 to KC 39 at :15, Bass 54 tied 10-10, Bass 57 with 4 s. Allen, run share, rain, part 3 and Receipts as in round 2.

## Note (not blocking)
- raw_pbp_history is missing one Bills game, 2000_06_BUF_MIA (schedule has it; history doesn't). That can't touch the "since 2009" claim.
  It could only affect the stat-heads count "since 1999: 7". Suggest adding "(one 2000 game, at Miami, missing from our play-by-play)" next time the generator is touched.
- Overclaim hunt: no all-time wording. "Career high" (Cook, 2022 on) and "his career" (Bass, 2020 on) fall fully inside our data.
- Fairness of summing win-chance changes by play type: it is fair, now that the story shows the start, the finish and the pieces adding up, and says "by both teams".

Chart checked by eye: the line starts at 55%. Labels are accurate (fumble about 80%, 54-yarder about 52%, Butker miss about 59%, Dortch about 76%,
57-yarder 100%). No label text overlaps, and no leader lines cross each other (the Dortch leader crosses the game line only). Footer has source and 151 plays. No betting.
