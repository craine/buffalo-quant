# Quant review (stage 2, round 3): 2026-wk12-kc-leonhard — PASS

Earlier rounds: `-quant-r1.md`, `-quant-r2.md`. This round checks the changed lines; everything else was verified in rounds 1-2 and is unchanged.

## Round-2 must-fixes
1. Closing line now: "When Buffalo does send five or more, it gets a sack on 6.8% of those dropbacks, 25th in the league (league average: 8.6%)."
   Own query (2026 wks 1-10, two bad FTN rows excluded): BUF 9 sacks / 133 = 0.0677 -> 6.8%; rank 25 (method min). No tie, but close:
   LAC 0.0685 (23rd), BAL 0.0684 (24th), BUF 0.0677, SEA 0.0581 (26th). League 298 / 3,474 = 0.0858 -> 8.6%. Stat-heads line matches.
2. Generator now computes the FTN check: `mism26` (asserted 1) and `match25`. Own count: 1 mismatch of 11,091 charted 2026 dropbacks against
   max(rushers - 4, 0); 2025 match 0.891 -> 89%. "(zero when four or fewer rush)" describes the comparison correctly. 11,091 = 11,093 minus
   the 2 dropped rows: correct.

## Polish edits
- "This season, Buffalo sends ..." / split points-per-dropback sentence / "compared with": wording only, no numbers changed.

## Reproducibility
Clean copy, outputs deleted, generator re-run: md, hero JSON and PNG byte-identical (PNG sha256 710505058a3b...e8a2a0, same as round 2).

No new issues. No betting language; no new jargon in the body.
