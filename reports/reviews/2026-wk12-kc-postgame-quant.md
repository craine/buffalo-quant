# Quant review, round 2: 2026-wk12-kc-postgame (stage 2)

**Verdict: publish.** Story sha256: bf4236b5214965fa0bee01944b9119696bcfc865b20831a8fc11f48ed1e48b99 (commit 32a781f3). Round 1 report: -quant-r1.md.

## Round-1 must-fixes
1. Mahomes 137 starts: generator now counts starts from raw_schedules starting-QB ids (REG, final, through 2026 Week 12) and asserts
   (137, 5). Matches my independent count: 137 starts, 2017 W17 on; <=10 points in 2021_07 TEN, 2023_08 DEN, 2025_14 HOU, 2026_07 SEA,
   2026_12 BUF. The stat-heads line describes the new rule. Fixed.
2. Big plays: "That's close to normal, so call this one even, not a win for Buffalo." Matches 2/31 = 6.45% vs median 7.60%. Fixed.

## New text checked
- "(19 runs)" and "31 pass plays and 19 runs": KC rush = 1 plays under the story filter = 19 (none are scrambles); dropbacks = 31. Correct.
- Writer's deviation, "runs worked, leaving it more likely to score": accepted. nflverse success = EPA > 0, i.e. the play raised the
  team's expected points. On this game success share and EPA>0 share are identical (12/19 = 63.2%). The wording is accurate; "stay on
  schedule" (my round-1 editor suggestion) would have described a different rule.
- "the 22.9 we'd expect from the same teams in dry weather": matches part 4's method text ("18.3 when we'd expect 22.9"). Fixed.
- Headline "fewest in any of his 105 career wins": 105 = all career wins, regular season + playoffs, and none dropped by the 15+ filter
  (round 1). Correct.
- Part 3 game count: 56 other games + Thursday under the 15+ dropback rule through Week 12; the writer's explanation (part 3 pinned
  through Week 10) accounts for it. No published number affected.
- P0017: notes say it resolves after the 2027-04-10 regular-season finale; resolves_at_utc holds the logging deadline. Not overdue; withdrawn.

All other numbers unchanged from round 1 and still match my derivations (Allen 81, 10/21, 2 INT, 151/105, 1 lower (loss), 82, 239;
40 runs, 61%, 6th of 143; 5th no-20+ game; Cook 32-117, 10 straight; 63% vs 41%; Bass 57, 4 s, tied; Ledger 1/1, 0.2025/0.0400, 15 of 24).
Chart re-viewed: legend now dated, title/subtitle/footer correct. No betting language.
