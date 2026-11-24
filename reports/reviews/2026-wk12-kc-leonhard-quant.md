# Quant review (stage 2, round 5): 2026-wk12-kc-leonhard — PASS

Round 4 report: `-quant-r4.md`. I checked all six round-4 fixes and the three polish edits against my own round-4 queries (in /tmp/qa).

## Round-4 must-fixes
1. Late 2025: Weeks 11-18 pressure 0.196 (28th), sacks 0.045 (27th), 11 sacks. Full season 36 sacks, 14th per dropback. Matches my numbers.
2. "Tied for 3rd" (107, with DEN) appears in the lead, hero and card. Matches.
3. "107 pressures on 375 opponent dropbacks, about 29 for every 100. That ranks 4th (league average: about 25)." 2025 at this point: 29, also 4th.
   The chart panel is now per 100 (23/33/29/29). Matches.
4. 2025 first nine games, 5+ rushers: 24% (22nd). League 27% for the same weeks. Jump +0.116 vs +0.045, so "more than twice" holds. Matches.
5. "Maxx Crosby is next with 35, in one more game" (9 vs 10 games). The explainer title says Weeks 1-10. Matches.
6. "the most of any player through Week 10". PFR Week 11 still has 1 game loaded, so the pin holds.

## Polish
- "Denver also got pressure on about 33 of every 100 dropbacks last year, more than Buffalo does now": 0.329 vs 0.285. Correct.
- The new lead lines make no new numeric claims; "good whether teams send extra rushers or not" is supported by the Thursday section.

## Minor (non-blocking)
- Stat-heads "BUF 2026 107 (3)" could read "(T-3)".
- Chart subtitle "Share of opponents' dropbacks" and footer "pressures 25%" don't fit the per-100 pressure panel. Consider "Per opponent dropback" and
  "pressures 25 per 100" in a later tidy-up.

## Reproducibility
Clean copy, outputs deleted, generator re-run: md, hero JSON and PNG byte-identical (PNG sha256 7adfab3f...18a45bca). Chart opened: values match.
