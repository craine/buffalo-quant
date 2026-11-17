Rounds 1-2 failed. Round 3 / final check (Quant), on text sha256 8f6e79d46af03b2932c98c44e59592b205ed6040fa5b5854abc760f82f61c0c8: PASS. All four round-2 must-fixes and editor fixes A and B are in and true. No numbers changed.

# Quant review: 2026-wk11-nfl-playoff-odds (round 3, final check)

## Verdict: publish

This check covers what changed since round 2 and anything those changes touch.

## Round-2 must-fixes
| # | Item | Status |
|---|---|---|
| 1 | Out-of-sample sentence | **Fixed and true.** The text now reads: "Across the 2 seasons it hadn't seen (2024 and 2025) taken together, the standings alone did better. The blend edged them in 2024 but fell well behind in 2025." Brier by season: 2024 mix 0.1047 vs. standings 0.1058 (blend ahead by 0.0011, so "edged" fits). 2025: 0.1508 vs. 0.1305 ("well behind"). Pooled out of sample: standings 0.1182 vs. mix 0.1277. Each figure matches the stat-heads line and my round-2 independent re-score. "lean" is now "hint" (editor B). The "5 of 7 seasons" sentence above it still holds (2020-2024; the blend lost 2019 by 0.0001 and lost 2025), so the two sentences no longer contradict each other. |
| 2 | "Full odds table" | **Fixed:** now "Full table of chances". |
| 3 | Test-chart footer and labels | **Fixed.** The chart has its own source line: "Source: nflverse schedules and results. Points model built on 2019-2023; 2024, 2025 out of sample." There is no QB-reports source left, and the in-sample note from editor P8 is covered. The labels sit below and right of their dots, and none overlap a dot, including "60 teams" and "22 teams". The SRC swap is restored after the chart (`globals()["SRC"] = _src`), so the other charts keep the shared line. The league chart still carries it, as it should. |
| 4 | Dart claim | **Fixed and true.** It now reads "Jaxson Dart opened the season for New York before Jameis Winston took over". First dropback in 2026 play-by-play: NYG weeks 1-2 J.Dart, weeks 3-6 J.Winston, weeks 7, 9 and 10 J.McCarthy (week 8 bye). For Lamar: BAL weeks 1-4 L.Jackson, then weeks 5-7 T.Huntley, so "started Baltimore's first four games before Tyler Huntley" is correct. |

## Editor fixes
- **A. Site card dek** (`src/site/build.py`, "nfl-playoff-odds-wk11"): it now says "The Bills win the AFC East 95% of the time, most often locking it up in week 14 or 15." That matches CSV division 0.9534. "96%" no longer appears in the story or in build.py.
- **B. Caution paragraph:** applied, using the Quant wording plus "hint" (see item 1 above).
- **Polish:** P2 (absence-list wording tied to Maye), P4 ("gave up") and P9 ("per the team") are in. All three are true and add no new numbers.

## Numbers unchanged vs. round 2
Every number in the body, tables, hero and stat-heads matches my round-2 verified values:
- **Bills:** division 95% (19,069 sims), playoffs 99%, top seed 39%, wins 12.7.
- **Clinch:** 12% / 28% / 24% by single week; cumulative 12 / 40 / 65 / 80 / 90 / 95; median week 15.
- **Patriots:** division 5% (916 sims), playoffs 40%, down 7.
- **QB table:** NYG -8, NE -7, BAL -3, LV -3, MIN -1, PHI -1, ARI 0, MIA 0, SEA +2.
- **QB effect:** 3,266 team games and 648 with a non-main starter; -2.5 / +0.9.
- **Absences:** 100, typical 2; 10 lasting 4+.
- **Backtest:** 29 / 97% and 60 / 2%; Brier, overall and by season.
- **Hero:** 95% / Wk 14 / 99% / 0.96 / 0.97.

The league chart title "best playoff chance in football: 99%" is true: BUF 0.9893 is the highest in the CSV (JAX 0.9792, SF 0.9678).

## Reproducibility
I ran `python3 -m src.reports.nfl_playoff_odds` (seed 2026) in a scratch copy, sharing the read-only DB. It reproduces all of these byte for byte: .md, .csv, .hero.json, and the league, AFC ladder, clinch and test PNGs. The generator writes nothing to the Ledger.

## Charts (all four viewed)
- **Test:** see item 3 above. Clean.
- **League:** shading is unchanged and correct, and the footer has its source and sample size.
- **AFC ladder:** the hatched teams (NE, LV, BAL, MIA) match the footer, the numbers match the table, and the label is "TOP 7 MAKE IT".
- **Clinch:** 12/40/65/80/90/95 and "Week 14, at Packers (28%)" match.

## Language scan
- "odds" appears only in the slug, filenames and image paths. Renaming those is Charlie's call, as noted in round 2.
- "lock up" means clinch.
- "Lock" is Drew Lock.
- I found no spreads, favorites, picks, leans or lines.

## Not blocking (carry forward)
- **Points model:** the OAK/LV 2019 abbreviation bug from round 2 is still there. Fix it in a new model version, not in this story.
- **Starter rule:** "first dropback = starter" misfires on trick plays. For example, it names D.Henry as Baltimore's week-9 starter. This adds noise to the QB-effect sample only.
- **Optional editor polish not applied:**
  - P5: the clinch graphic title is still a question.
  - P6: the "12%" still touches the top of the fill on the week-13 card.
  - P7: the Dolphins and Cardinals bars are too short to show their color.
