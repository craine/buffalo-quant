# Quant review: Penguins 6, Sabres 3 (2026-11-27)

Reviewer: independent Quant (stage 2). Commit b642c7ae. Every number re-derived with my own queries against `raw_nhl_games`,
`raw_nhl_schedule`, `raw_nhl_plays`, `raw_nhl_rosters` and `clean_nhl_shots_xg` (per-shot model xG only; filters, per-season
rescale, team-game build, goalie split, ranks, record and Ledger all recomputed independently). Generator not used.

**Verdict: FAIL (publish with fixes).** The numbers are right. The rarity cutoff is misdescribed in four places, and the
headline and lead treat one game as proof that the preview was right.

## Required fixes

### 1. The cutoff is "Pittsburgh's own 1.755", not "1.8 or less". At "1.8 or less" the count is 26, not 21.
The count (21 of 8,700, PIT 5) uses `xG <= 1.755` (Pittsburgh's exact value). The fan-facing text rounds the cutoff to 1.8, and the
count at a literal 1.8 cutoff is different:

| Cutoff (5+ non-empty-net goals) | Team-games | PIT |
|---|---|---|
| <= 1.50 | 6 | 0 |
| <= 1.75 | 18 | 3 |
| **<= 1.755 (PIT's value, used)** | **21** | **5** |
| <= 1.80 | 26 | 5 |
| <= 2.00 | 47 | 6 |

Three of the 21 (VGK 1.751, PIT 1.753, PIT 1.755) sit within 0.005 of the cutoff, so the count is very sensitive to it. Using the
team's own value as an "at least this extreme" cutoff is fair, but the text has to say so. Fixes (writer computes nothing new):

- Lead. Old: `a team has scored 5 or more on chances worth 1.8 or less only 21 times in 8,700 team-games, about once every
414.` New: `a team has scored 5 or more on chances worth no more than Pittsburgh's only 21 times in 8,700 team-games, about once every
400.`
- How rare. Old: `only 21 had 5 or more goals on chances worth 1.8 or less, and 5 of them` New: `only 21 had 5 or more goals on chances worth no more than Pittsburgh's, and 5 of them`
- Chart title and image alt text. Old: `5 goals on chances worth 1.8: 21 times in 8,700 NHL team-games` New: `5+ goals on chances as thin as Pittsburgh's: 21 times in 8,700 NHL team-games`
  (also fixes "5 goals": two of the 21 had 6). Width checked against the current title; it fits. Re-freeze the PNG hash afterward.
- Site dek (`src/site/build.py`). Old: `Pittsburgh scored 5 on chances worth 1.8, something that's happened 21 times in 8,700 team-games since 2023-24.`
  New: `Pittsburgh scored 5 on chances worth 1.8. Since 2023-24, a team has scored 5 or more on chances that thin only 21 times in 8,700 team-games.`
- Hero `big[1]` label. Old: `how often a team does that, since 2023-24` New: `how often a team scores 5+ on chances that thin, since 2023-24`

**"About once every 414"** is arithmetically right (8,700 / 21 = 414.3), but three significant figures overstate the precision of
a count that moves from 18 to 26 across a 0.05 change in the cutoff. Say "about once every 400" in the lead and "1 in 400" in the hero
(format as `round(len(tg)/len(rare), -2)`). Strongly recommended.

### 2. Overclaim: the headline and lead treat one game as proof
- Headline: `Pittsburgh's finishing came back all at once`. Lead: `Our preview said Pittsburgh's poor finishing probably wouldn't last. It didn't take long.`
  The preview made a season-long call and said it "won't necessarily show up in one game". Five goals on 1.8 isn't finishing
  "coming back" to average. It's a one-game outlier the other way, and the story itself says "one game is mostly luck either way" and
  that Pittsburgh is still 25th. The Rangers recap (Nov. 25) handled a one-game *miss* on the same kind of call as "season-long calls,
  and we'll keep tracking them". Claiming a one-game *hit* here is asymmetric scorekeeping.
  - Headline. Old: `# Penguins 6, Sabres 3: Pittsburgh's finishing came back all at once` New: `# Penguins 6, Sabres 3: Buffalo had the chances, Pittsburgh had the finish`
  - Lead. Old: `Our preview said Pittsburgh's poor finishing probably wouldn't last. It didn't take long.` New: `Our preview said Pittsburgh's poor finishing probably wouldn't last over the season. One game doesn't prove that, but Friday was a big swing.`
  - Receipts. Old: `The finishing showed up in one game, though one game is mostly luck either way.` New: `One game is mostly luck either way, so Friday doesn't settle a season-long call.`

## Minor fixes
3. Lyon's "shots" are unblocked shots, including misses. Lyon faced 18 shots on goal (17 saves), and a fan checking the box score sees
   18, not 20. Old: `Alex Lyon allowed 1 on 20 shots worth about 1.2.` New: `Alex Lyon allowed 1 on 20 unblocked shots worth about 1.2.`
   This matches the Luukkonen sentence. (Luukkonen faced 10 shots on goal and 12 unblocked shots.)
4. Not published: the `src/ledger/grade_p0026.py` docstring says "49%". P0026 is 0.51. Old: `(Sabres beat the Penguins, Nov 27, 2026, 49%)` New: `(Sabres beat the Penguins, Nov 27, 2026, 51%)`.
5. Optional: "Pittsburgh is still 25th in finishing". The preview had it 28th, so "still" could read as unchanged. Consider "is 25th in finishing even after Friday".

## What I verified (all match)
- Data scope: 4,350 regular-season games through 2026-11-27, all `OFF`. 1,312 per season for 2023-24 to 2025-26 and 414 for 2026-27, so 8,700 team-games, none with zero shots. All 15 Nov. 27 games were final, and the pins need no late games.
- Rescale factors: 1.0227, 1.0104, 0.9713, and 1.0031 for 2026-27 (stat-heads says 1.003).
- Game 2026020413: BUF 3, PIT 6 in regulation (REG) at Buffalo. Unblocked non-empty-net shots BUF 36, PIT 32 (PIT 33 counting the empty-net goal). Chances BUF 2.907, PIT 1.755, share 0.6235 (62%).
- Goals, from raw plays and shots: Kulich 1st 0:31 (8 ft), Dahlin 1st 9:19 (7 ft, 5v4), Norris 2nd 12:11 (2.2 ft, 0.478, the closest BUF goal).
  PIT goals: Kindel 18.2 ft 0.045, Letang 42.6 ft 0.049 (4v4), McGroarty 11.0 ft 0.124, Lizotte 31.0 ft 0.116, Koivunen 25.6 ft 0.124. Malkin empty-net goal 3rd 17:59.
  The rounded distances and percentages in the story are all correct.
- Goalie split: Luukkonen 12 unblocked / 4 GA / 0.578 chances (GSAx -3.42). Lyon 20 / 1 / 1.177 (+0.18). Murashov 36 / 3 / 2.907 (about -0.09, so "about average" holds).
- Replacement: raw plays show Lizotte's goal at 2nd 3:15 (sortOrder 295, goalie in net Luukkonen), then the faceoff at 3:15, then the next
  PIT shot at 3:23 with `goalieInNetId` = Lyon. Lyon came in right after Lizotte's goal, not later. The 2nd-period clock 3:15 is correct.
- Lizotte before Friday (2026-27): 41 unblocked shots, 0 goals, chances 3.26, so "about 3" holds.
- Rarity: 21 of 8,700. PIT has 5 (2024-04-02, 2024-12-03, 2024-12-19, 2025-10-23, 2026-11-27). Near-1.755 (±0.25) mean 2.148 on n 949, so "2.1" holds.
- Season through Nov. 27: BUF chance share 0.4835, 21st (min rank). PIT finishing -0.204 per game, 25th, and also 25th on the total. PIT saves -0.278 per game, 27th.
- BUF record from scores: 11-11-4 (26 GP).
- Ledger: P0026 was logged at 00:32:32Z, before the 01:00Z puck drop. p = 0.51, outcome 0, Brier 0.51² = 0.2601. The record (side above 50% won, P0017 ungraded, no 0.50 calls) is 15 of 25. That follows from 13 of 22 in the NYR recap, plus P0024 and P0025 right and P0026 wrong.
- Brand: no betting language. Stat terms only in "For the stat-heads". Sample sizes stated (8,700, n 949, 41 shots). The chart footer has the source and the sample.
- Chart: I looked at the PNG. Title fits, no label overlap, and the two highlighted points sit at (1.76, 5) and (2.91, 3).
