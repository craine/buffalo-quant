# Quant review, round 2: 2026-wk12-kc-preview

Text SHA-256 8a76608d... (commit b2d857cc). Verdict: **publish**. Round 1 is in -quant-r1.md.

## Round-1 must-fixes, checked against the diff f0a34f9c..b2d857cc
1. Model description: now "its offense scores per drive ... the other team's defense gives up, blended with last season's numbers, plus home field". Matches `ratings()`/`raw_prediction()` (K=60 shrink to last season). OK.
2. Rain/QB paragraph: replaced; no longer implies QB evidence. "mostly running backs" is supported: in my round-1 check, starting-QB designed runs were 1.44 of 23.98 team designed runs per dry game. OK.
3. Ties: body "64% of the 657 games that didn't end in a tie"; stat-heads "Brier 0.224 on 659 games, ties scored as half"; generator asserts (659, 657). Re-derived: 659 games, 2 ties, Brier 0.2237, 419/657. OK.
4. Wind: "northeast to east", derived from the file's direction list (NE, E, NE, NE) and asserted. OK.
5. "Ten games is a small sample." added. OK.
6. Receipts: "Wednesday at 9:44 a.m. Eastern". 2026-11-25T14:44:10Z = 9:44 a.m. EST, a Wednesday; asserted in the generator. UTC stamp in stat-heads; P0025 has the same stamp in ledger/predictions.csv. OK.
Applied recommendation: "In games with rain and a 10+ mph wind since 2018 ... the 22.9 we'd expect from the same offenses and defenses in dry games" matches part 4's definition (rain + wind 10+, 44 games, expected 22.87). OK.

No other numbers changed. Hero JSON and chart are unchanged (not in the diff) and still match.

## Non-blocking note (my round-1 wording; fix if there's time)
- One test game, 2024_08_CHI_WAS, has a win chance of exactly 0.500. The code (`g.p > 0.5`) counts it as an away pick, and the home team won, so it is scored as a miss. The stat-heads line "the side given more than 50% won 63.8% of the 657 games without a tie" is therefore off by one game: only 656 games had a side above 50%, and that side won 419/656 = 63.9%. The body's 64% is right either way, and the current figure understates the model.
  Optional replacement: "the side given more than 50% won 63.8% of the 657 games without a tie (one game at exactly 50% counted as a miss)."

## Typed words still in the generator (answering the coordinator)
"under two points", "The two times", "Ten games", "8 to 11 p.m.", "7 p.m. to 1 a.m.", "since 2018", "2024, 2025 and 2026". All are true. The 2026 play-by-play fingerprint assert pins the data, so a re-run can't silently make them wrong. Not must-fixes for this story. For future generators: derive these words or assert them.

## Publish step reminder
reports/published_images.json doesn't list bills-kc-wk12-preview.png yet. Run `python3 scripts/freeze_images.py` when publishing.
