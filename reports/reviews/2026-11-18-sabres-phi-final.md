Round 1 failed on one word ("only" -> "mainly"); round 2 passes.

# Final check (stage 4, Quant, round 2): 2026-11-18-sabres-phi.md

Reviewed text sha256 a646b7138371f8a43c19cf5528b5fe55a8abf49d2d8702569538fa2ef15f83c6 (round 1 was 2798670e...7742).
Generator `src/reports/sabres_postgame_phi.py`.

**Verdict: PASS. Publish.**

## What changed since round 1 (diff against my round-1 backup of the md)

There are exactly three changed lines in the md. The hero JSON and both PNGs are byte-identical to round 1.

1. Line 90 bullet: the heading "Even at five-on-five, beaten on the power play." became "About even at five-on-five, behind on the power play.",
   and "only on the" became "mainly on the". This is the required fix. The new heading is true: at five-on-five Buffalo had 1.72 and
   Philadelphia 1.55 (Buffalo's share 53%), which is about even; on the power play Philadelphia had 0.86 and Buffalo 0.32. It is consistent with
   the hero bars ("Sabres ahead by 0.2" and "Flyers ahead by 0.5") and with the situations chart.
2. Line 53: "26 feet to the side of the net" became "26 feet to the side of the middle of the net". This is true: the winner's raw y is -26 and
   the net's centre is at y = 0. The new wording is more precise, and the 15 ft, 30 ft and 60 deg figures are unchanged.
3. Line 69: the Woll sentence became "started for Philadelphia; our pregame story had him at 4.5...". This fixes the "whom" ambiguity, and the
   4.5 figure is unchanged.

The headline's 52 seconds now comes from `{gap_s}` (int(winner.t - tyer.t)). The rendered output is still "52 seconds" in both the headline and
the lead, so the text is identical to round 1. Nothing else changed.

## Verified

- Reproducibility: I backed up the current files and re-ran the generator (rc 0). The md, hero.json, sabres-phi-post-flow.png and
  sabres-phi-post-situations.png are all byte-identical to the files under review.
- No betting language: a grep of the md and hero JSON for odds, long shot, underdog, favorite, lock, bet, spread, wager, parlay,
  sportsbook, units and pick found only false positives ("better", "goal line").
- All other numbers are carried over unchanged from my round-1 verification (they are listed in that review).
