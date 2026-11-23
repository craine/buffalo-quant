# Quant review, round 2: reports/2026-wk11-lab.md (stage 2)

Reviewer: independent Quant. Date: 2026-11-22. Commit 6948c64a. Story sha256: 24cffa72118e72df6dc0b991b1a46ecc5979200caf2438fa096bd0b0181ae1ca
Round 1: 2026-wk11-lab-quant-r1.md

**Verdict: PASS.** All nine round-1 must-fixes are applied correctly, and I found no new errors.

## Round-1 items
1. The 135 qualifier is now in the lead, section 1, hero and card. The new "How we counted" numbers match my round-1 queries:
   136 games with any involvement, 1 left out (2019_17_NYJ_BUF, 5 plays, 0 runs), fewest before = 1, in 6 games
   (2020_04, 2020_17, 2021_10, 2021_15, 2022_02, 2024_02). All are asserted in the generator.
2. The fake punt is now a "30-yard gain". air_yards 27 and own 34 are asserted.
3. The touchdown now reads Grable twice and Corbett twice, "including on Cook's 1-yard touchdown". The TD line follows Corbett, which is correct (play 1707).
   It is asserted from the touchdown flag.
4. The kneel note is fixed, and the career query drops qb_kneel and two_point_attempt. The result is unchanged (only zero-run game = 2026_11).
5. The hero says "onside-kick formation", with no intent claimed.
6. Both "than ever" spots now say "this season".
7. "A home game against a struggling division rival" (MIA 1-9). The timing problem is gone.
8. These are now computed and asserted: twice (2), 2 yds, 1-yd TD, own 34, 23-9 (kicking team = defteam on the kickoff, correct sign), "5 yards"
   (string-asserted in the play description), and 26-9 (from raw_schedules).
9. The footer now reads "10 games; 78 Bills pass and run plays vs. Miami", which matches my count (78 plays, 46 from shotgun).

## Re-checked
- Same database as round 1 (byte-identical; bq-lab/data is a symlink to the shared data folder), so the round-1 table stands.
- Clean-copy regeneration: md, hero JSON and PNG are byte-identical to the committed files.
- New chart title "Against Miami: zero Allen runs, most extra linemen, most shotgun": week 11 is the season extreme in all
  three panels (0 runs; 4 against a previous max of 2; 59% against 36.6–52.5%). Correct.
- Card and hero agree with the body (135, 14-point lead, four extra-lineman plays, most shotgun).
- No betting language. "Signs the Bills were trying things out" is hedged by the lead ("looked a lot like") and by "None of this proves a plan."

## Optional
- The season run table (average and chart) filters on rush == 1 or pass == 1, which would include a two-point run, while the stat-heads
  says two-point tries are excluded. Allen had none in 2026, so no number changes. Add `two_point_attempt == 0` for consistency.
- Stat-heads: "Fake punt: 27 air yards, 30-yard gain" sits under the eligible-linemen bullet. Move it to the fake-punt bullet.
- Before publishing, run `scripts/freeze_images.py` (wk11lab-season.png is not yet in published_images.json).
