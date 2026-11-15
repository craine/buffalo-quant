# Quant re-check and stage-4 final check: reports/2026-11-15-sabres-dal.md (sha256 572279f3...)

**Verdict: PASS (quant and final).** Both round-2 fixes are in. The Editor's round-2 edits introduce no wrong numbers and no new
overclaims. Running the generator into a scratch folder reproduces the story markdown and the hero JSON byte for byte.

## Changed lines, checked
- **"Keep an eye on Buffalo's own end ... the Sabres allow the 6th-most chances in the league."** This is now computed as `xga_rank`
  (games through Nov. 12, the pregame window). I re-derived it independently: BUF allows 3.238 a game, 6th-most, and is still 6th
  (3.254) through Nov. 14. The bullet is framed as the pregame story's concern, not as a trend from one game. It replaces the
  one-game "Full strength is the worry" claim, so stage-3 fix 1 is resolved.
- **"Saturday, Dallas's chances were worth 3.5 goals, and a good night from Lyon held it to 2."** DAL 3.543 with 2 goals; Lyon +1.54. Correct.
- **Heading "Buffalo rarely got to the net."** 9 close-in shots against a usual 13.3. True, so stage-3 fix 2 is resolved.
- **Full-strength heading "At full strength Saturday, Dallas had most of the chances."** Now scoped to the game. 5v5: DAL 2.609 vs
  BUF 1.065, a 71.0% share. Correct.
- **Oct. 8 "had the better chances and still lost 4-0."** Now computed and asserted: BUF 2.563 vs DAL 2.108. Raw `raw_nhl_games`
  2026020057 has BUF 0, DAL 4 at Buffalo. Oettinger was the only goalie who faced Buffalo's unblocked shots (44). Correct.
- **Winnipeg.** Now pulled from `raw_nhl_games` and asserted: Dallas's previous game was 2026-11-12, DAL (home) 3, WPG 8, a
  5-goal margin. "8-3 home loss to Winnipeg on Thursday" is correct, since Nov. 12, 2026 was a Thursday.
- **"The shutout says more about Oettinger than about Buffalo's offense."** Supported: 6.1% replay shutout odds, and Oettinger's
  +2.62 covers the whole gap.
- **"Going a whole game without a rebound shot is rare: ... 6% of NHL team games this season."** 37 of 618 = 0.060, through Nov. 12.
  The stat-heads section states the window. Correct.
- **Lead rewording ("made sure this was one of those nights").** No number changed: 22 saves, 2.6, 6%, 3.5, 38%.
- **"Buffalo's own 8-3 loss to Tampa Bay."** Still a literal in the generator, but raw has TBL 8 at BUF 3 on 2026-11-11. Correct.

## Untouched, and still consistent
Periods, strength, replays (0.265 / 0.162 / 0.573), close-in and rebound rates, 9-or-fewer (130 of 650; BUF 3 of 20), the
other-game average (3.08), 14 missed, the goalie ranks (23 of 685), the Ledger figures (Brier 0.1444; 8 of 11; 3 of 4), the hero
JSON (unchanged and regenerated identically) and the dek all match my earlier derivations. Both charts were opened last round and
their labels hold. The site entry is second in ARTICLES, so Bills-Jets stays the homepage hero.

No betting language. No jargon in the body. Small samples are labeled. Nothing was written to the Ledger.

Leftover, not blocking: the data-revision note says the NHL "corrected" its records. "Updated" would be more neutral. This is an
editor's call.
