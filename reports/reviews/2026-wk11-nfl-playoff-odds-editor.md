# Editor review: 2026-wk11-nfl-playoff-odds (round 2). Round 1 failed. Round 2: PASS, with two small fixes to apply before the final check

**One-sentence version:** "Our simulations give the Bills a 95% chance to win the AFC East, and they most often wrap it up in week 14 or 15, with New England's hopes falling after Drake Maye's injury."
That is the lead, and it works on radio.

**Verdict:** ready after the small fixes below. Every round-1 item is fixed or settled. The new caution paragraph is honest and easy to read, and the QB notes are fair. What's left is two small accuracy fixes (one on the site card, one in the caution paragraph) and polish.

## Round-1 items

| # | Item | Status |
|---|---|---|
| 1 | Betting language (odds, 7-point favorite, PLAYOFF LINE) | Fixed in the body, the hero, the card tag and the ladder. "odds" is still in stat-heads (see P1) |
| 2 | Clinch overclaim | Fixed: "most often in week 14 (28%) or week 15 (24%)", median week 15 stated; hero says "most common week" |
| 3 | QB table "-1 pts" | Fixed: "(down 1)", with "percentage points" in the column header |
| 4 | Seahawks +1 vs zero penalty | Fixed: the notes explain that the change comes from other teams' QB news and simulation noise |
| 5 | Jets | Fixed: not in the table; marked questionable and assumed to play, with sources |
| 6 | "biggest game left" | Replaced with "the only meeting left between the top two teams in the division" (a fact) |
| 7 | Maye hook / Next up | Fixed: both are in the Bills bullets |
| 8 | Tie the method to the headline | Fixed: "19,069 of the 20,000 ... That's the 95%." |
| 9 | Plain English | Mostly fixed. "the points it allowed drifted" is still a little stiff (P4) |
| 10 | 5 of 7 seasons | Checked against the stat-heads table: the blend matched or beat the standings in 2020-2024 = 5 (2019 lost by 0.0001; 2025 lost). Correct |
| 11 | Chart titles, ladder, overlap | Ladder: "TOP 7 MAKE IT", "WIN DIVISION" and a takeaway title are fixed. The clinch title is still a question and the "12%" still sits on the fill (P5, P6) |
| 12 | Hero 96% collision | Hero is fine now (headline 95%, explainer bar 96% is a different thing and labeled). **But the site card dek still says 96% (Fix A)** |

## Fixes to apply before the final check

**A. Site card dek is stale (src/site/build.py, "nfl-playoff-odds-wk11").** The CSV has division 0.9534, and the story, hero and clinch graphic all say 95%.
- Replace: "The Bills win the AFC East 96% of the time, most often locking it up in week 14 or 15."
- With: "The Bills win the AFC East 95% of the time, most often locking it up in week 14 or 15."

**B. The caution paragraph is right taken together, but wrong for one of the two seasons.** By season (stat-heads), the blend beat the standings in 2024 (0.1047 vs 0.1058) and lost badly in 2025. "In the 2 seasons it hadn't seen ... the standings alone did better" reads as both seasons, and it seems to clash with the "5 of 7" sentence just above it, which counts 2024 as a win for the blend. "lean" is also a betting word.
- Replace: "In the 2 seasons it hadn't seen (2024 and 2025), the standings alone did better than the half-and-half blend. So read the gaps between teams with similar records as a lean, not a sure thing."
- With: "In the 2 seasons it hadn't seen, the blend roughly tied the standings in 2024 and did clearly worse in 2025, so over those two seasons the standings alone came out ahead. So read the gaps between teams with similar records as a hint, not a sure thing."
- (No new numbers. "roughly tied" and "clearly worse" describe the stat-heads figures. The Quant should confirm the wording in the final check.)

## Polish (doesn't block)

- **P1. Stat-heads, last bullet:** "Full odds table" -> "Full table of chances". The betting-language rule covers the whole page.
- **P2. QB notes, absence pool (line 85-86).** Too much jargon for the body: "pool", "underweighted". It also doesn't say who this affects.
  Replace "and our pool leaves out absences that ran to the end of a season, so a season-ending injury is likely underweighted." with
  "and our list of past injuries leaves out ones that lasted to the end of a season. So if Maye's injury does end his season, we probably give the Patriots a little too much credit."
- **P3. Dolphins row:** "at least 3 more games" next to "IR means at least four games". A fan sees 3 and 4 and wonders which is right. Add "he has already missed one" if that's true (the writer should check), or say why the two numbers differ.
- **P4. Step 2:** "and the points it allowed drifted about 2" -> "and the points it gave up drifted about 2".
- **P5. Clinch graphic title** is a question. Suggest "The Bills most often lock up the AFC East in week 14 or 15". The red week-14 card shows 40% while the subtitle says 28%. The subtitle explains it ("adds up week to week"), but a screenshot reader could take 40% as "week 14 chance". Consider "40% by then" on the card.
- **P6. Clinch graphic:** the top of the "12%" on the week 13 card still runs into the fill edge. Lift the number or the fill.
- **P7. League chart:** the Dolphins and Cardinals are blue (QB out) but their bars are too short to see, so the color doesn't show. Optional: mark them with a symbol or a "QB out" note.
- **P8. Test chart** travels on its own, and nothing on it says 5 of the 7 seasons were in-sample. Add "(the model was built on 2019-2023)" to the footer. Also drop "quarterback status from team and news reports" from the footer, since the test uses no QB adjustments. The "60 teams" label overlaps its dot. The title could be a takeaway: "Our past chances came true about as often as we said".
- **P9. Ravens row:** "(team)" -> "(per the team)".
- **P10. Hero:** consider "Wk 14-15" / "when the Bills most often clinch the AFC East" so it matches the headline. The current wording is accurate.

## Checks done

- Read the full body, the hero JSON and the site card. Opened all four graphics.
- The body has no "odds", spread, favorite, line, pick or lock. "lean" is the only near-miss (Fix B).
- Cross-checks: 19,069 + 916 of 20,000 matches 95% and 5%. 12% + 28% + 24% ≈ 65% by week 15 (rounding). The Patriots' maximum of 12 wins = 5 + 7. 3½ games = (3 + 4)/2. 9 QB rows = "Nine teams". The Bills' CSV values match the story (0.9893 / 0.9534 / 0.3928 / 12.74).
