# Quant review, round 2: 2026-wk12-kc-mahomes (stage 2)

**Verdict: PASS (publish).** Round 1 is in -quant-r1.md.

## Reproduction
- I re-ran the generator in a clean copy (repo without .git or data, with the DB linked in). The md, hero JSON and PNG all come out byte-identical:
  - md sha256 a53c48f3…
  - hero 5cd06161…
  - PNG 4264ae9b…
- The fingerprint check holds. My own query of 2026 regular-season play-by-play (weeks 1-10, EPA not null) returns 25,946 plays and an EPA sum of -222.5969, which matches `PBP26_FINGERPRINT`.
- The current database still matches the live nflverse file (Last-Modified 2026-11-25 10:02:46 GMT).

## Every number re-derived independently (current data)
- **Games:** 55 starts (16/16/14/9), KC 38-17.
- **Medians:** pressure 0.205, big plays 0.075, runs that work 0.414, five or more rushers 0.214.
- **Splits** (points / win rate / games):
  - Pressure: 21.1 / 59% / 27 vs 26.4 / 79% / 28
  - Big plays: 21.7 / 62% vs 25.7 / 76%
  - Runs: 22.4 / 67% vs 25.1 / 71%
  - Five or more rushers: 24.4 vs 23.1
- **All three:** 8 games, 16.5 points, 4-4. The other 47 games: 25.02 points, 72.3% won. All 55: 23.8 points.
- **Low-scoring games:** 17 games with 20 or fewer points. Runs worked 0.347 in those games vs 0.440 in the rest (35% / 44%).
- **Second check (OLS, points per 1 SD):** -2.26 / +3.25 / +2.47 / +0.92.
- **Buffalo:**
  - Pressure 0.285, 4th (league 0.245)
  - 20+ yard plays allowed 0.0907, 20th (league 0.083)
  - Runs that work allowed 0.456, 27th (league 0.426)
  - No ties at any of the three ranks
- **KC 2026:** 20+ yard rate 0.089 (11th), runs that work 0.477 (5th), pressure on Mahomes 0.232.
- **Run examples** (designed runs 2023 to 2026 Week 10, same play filter):
  - First-and-10: 4 yards 8.7% (n=2,547), 5 yards 69.3% (1,944), 6 yards 96.2% (1,405)
  - Third-and-2, first down gained: 98.6% (501). Third-and-2, first down not gained: 0% (334).
- **Definitions:** "worked" = EPA > 0, now stated correctly in the body and in stat-heads. "Running game" wording is fixed. The 8-game sample is labeled. The unsupported "better defenses" clause is gone. The Thursday section matches the 27th rank.
- **Card, hero and chart** all show 4th / 20th / 27th. I opened the chart.
- No betting language.

## Recommended, not blocking
- **The fingerprint pins only 2026 weeks 1-10.** It doesn't cover 2023-25 play-by-play, PFR, FTN or schedules. A quiet re-post of those could still shift the split numbers without tripping any check: the current asserts catch only the game count, the 16.5 points, the 8-game count, the direction of each split and the ranks.
  - Suggest asserting a fingerprint for the KC game table too, e.g. the sum of `kc`, `pr` and `db` over the 55 games, plus a 2023-25 count and EPA sum.
- **"won 50%" in the chart footer vs "went 4-4" in the body.** Both are correct. See the editor polish.
