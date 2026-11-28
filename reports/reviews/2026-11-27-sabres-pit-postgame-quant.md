# Quant review, round 2: Penguins 6, Sabres 3 (2026-11-27)

Reviewer: independent Quant (stage 2, round 2). Commit 117133bd. The round-1 report is in `-quant-r1.md`.

**Verdict: PASS.**

## What changed since round 1 (diff b642c7ae..117133bd), checked
- **Rarity cutoff:** the lead, the "how rare" section, the chart title and alt text, the site dek and the hero now all describe the cutoff
  as Pittsburgh's own value ("no more than Pittsburgh's" / "as thin as Pittsburgh's"). That matches the query: `x <= 1.7553`, giving 21 of
  8,700 team-games, 5 of them Pittsburgh's. I re-ran my round-1 query on the current database and got the same result. "5+" in the
  chart title is correct, since two of the 21 games had 6 goals.
- **"About once every 400" / "1 in 400":** 8,700 / 21 = 414.3, rounded to the hundred, is 400. The generator asserts it. This is acceptable
  precision given how sensitive the cutoff is (18 to 26 games across 1.75 to 1.80).
- **Headline, lead and Receipts:** the one-game overclaim is gone. The lead now says "One game doesn't prove that". Receipts says "Friday
  doesn't settle a season-long call". This is consistent with the Rangers recap.
- **Lyon:** "1 on 20 unblocked shots worth about 1.2" is correct and matches the Luukkonen sentence.
- **Norris sentence:** merged. The new assert checks that Buffalo's last-listed scorer is the one with the closest goal. My round-1
  check agrees: Norris at 2.2 feet, chance 0.478.
- **"36 shots that weren't blocked":** same count as before (36 vs. 32, not counting empty nets).
- **"Pittsburgh is 25th in finishing after Friday":** correct (-0.204 per game, min rank 25).
- **Grader docstring:** now 51%, which matches P0026's p = 0.51. This is code only.
- **Site dek:** the 62%, the 1.8 game value and the 21 in 8,700 since 2023-24 are all correct.
- **Hero:** 5 goals on chances worth 1.8, "1 in 400", 62%, and the 51% call that missed. All correct.

## Unchanged from round 1 and still verified
I checked these against the current database: the chances (2.907 vs. 1.755, 62%), the goal list and each shot's chance value, the goalie
split and the replacement (Lyon was in net for the faceoff at 2nd 3:15 after Lizotte's goal), Lizotte's 41 shots, the comparison average
of 2.1 goals (n 949), the ranks (21st and 25th), the record (11-11-4), and the Ledger (P0026 a miss, Brier 0.2601, record 15 of 25).

## Brand and chart
- No betting language. No jargon in the body. Sample sizes are stated.
- I looked at the PNG. The new title is on one line within the frame. Nothing overlaps, and the footer has the source and the 8,700 team-games.
- The manifest hash `a9b2d59e…` matches the committed PNG.
