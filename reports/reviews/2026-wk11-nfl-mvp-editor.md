# Editor review: 2026-wk11-nfl-mvp (round 4) — rounds 1-3 failed; this round PASS (minor polish only)

Reviewed text sha256 74396903eb2b7ef9570a6c1c2c9bad16990c060458cc99db5ec71ef71fffc4f5, plus wk11-mvp-board.png, wk11-mvp-check.png,
2026-wk11-nfl-mvp.hero.json and the "nfl-mvp-wk11" card in src/site/build.py.

**One sentence:** "By how much each quarterback has added beyond an average offense, Joe Burrow is our MVP after 10 weeks; Josh Allen is fourth, mostly because the Bills throw far less than the Bengals."

**Verdict:** ready. Both round-3 must-fixes are done, the Quant's "second-lowest" concern is handled, and nothing new reads wrong.

## Round-3 items

| # | Item | Status |
|---|---|---|
| M1 | Site card dek read as a track record | Done: "Run back over the last seven full seasons, this count had the real MVP in its top three six times." |
| M2 | "Throw for throw they're about even ... a little under half a point for both" | Done: "Throw for throw Burrow has been a little better: each of those plays is worth about four-tenths of a point, a bit more for Burrow. The bigger difference is how many." "Nearly all" is now "Most of the gap". 0.415 vs 0.383 and the 30.3 / 8.7 split are in stat-heads. |
| P1 | Lead "our No. 1 / our top three" | Done: "this count had the real MVP No. 1 three times and in its top three six times." Matches hero, board footer, check chart and card. |
| P2 | Repeat of "Bills throw less" | Done: now "So the biggest reason he's fourth is volume." |
| P3 | Why a TD isn't 7 | Not done. Optional. |
| P4 / Quant 2 | "second-lowest rate" | Done: "one of the three lowest rates in the NFL"; stat-heads notes the margin. True on both filters. |
| P5 | Long sacks/turnovers parenthetical | Not done. Optional. |

## Minor polish (not blocking)

- **P6.** Line 36: "Burrow has been a little better ... a bit more for Burrow" says the same thing twice. Could be: "Throw for throw Burrow has been a little better, though both are worth about four-tenths of a point a play."
- **P7.** Line 44 "is volume": "volume" is mild stat-speak. Could be "is how much he throws."
- **P8.** Stat-heads line 94: "the Bills' rank among the lowest is within a fraction of a play of the next team" is vague. Could be: "Bills 2nd-lowest on this filter, 3rd-lowest on the standard pass/rush filter; both within a fraction of a play of the Jaguars."
- P3 and P5 above still optional.

## Bills-fan read of "Why Josh Allen is fourth"
Fair, and it's no longer generous to Allen: it now says Burrow has been a little better per throw and that volume is the bigger
part. It still credits Allen's running and cheaper turnovers, answers the 8-1 question (still No. 4), and offers two readings.

## Charts, hero, card
- Board: five-second read, takeaway title, Allen highlighted in red, footer has source, weeks 1-10, 31 QBs, 150+ dropbacks and "Looking back ... this count". Nothing clipped.
- Check: title is the takeaway and fully visible; subtitle "Top 3 in 6 of 7"; 2023 miss obvious; footer complete.
- Hero JSON: each line stands alone; note uses "Run back ... this count". Bars 100 / 92 / 87 match the table.
- Card dek: stands alone, no track-record overclaim.
- Date line: Nov. 17, 2026 is a Tuesday. Correct.

## Betting language
None (scanned for odds, lines, spreads, picks, locks, favorites, over/under, bet, wager). "EPA" appears only in stat-heads.
