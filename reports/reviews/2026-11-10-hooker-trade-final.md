# Quant final check (stage 4): reports/2026-11-10-hooker-trade.md

## FAIL: two mechanical fixes, then PASS

The headline numbers hold up, and so do all the stage-2 limits. Poyer +0.13 / +0.05, Gardner-Johnson -0.17, Hamlin +0.40 / -0.19,
the 1-in-16 check, the league ranks and the Rams example all reproduce from my own code (/tmp/qf/a.py, b.py, c.py), and every
caveat is in the text. The fail comes from two things. One QB flag is wrong in plain English, and that error is published in four
places. The PFR side of the generator is also not pinned, so re-running it will change the published story. Neither fix touches
the lede, the Poyer/Gardner-Johnson comparison or the Hamlin asterisk.

---

## Ranked issues

### 1. MUST FIX: Spencer Rattler (NO, 2025 week 4) is labeled a backup QB. He was New Orleans's starter that week.
**Text:** table row `Taylor Rapp, 2025 | 6 | +0.01 | -0.07 (4 games)`; chart label "Taylor Rapp 2025, 6 games (2 vs. backup QBs)" with
the -0.07 bar; hero bar `"Rapp (2025, 2 vs. backups)"`; stat-heads "2025 wk 4 NO (S.Rattler)".
**Evidence (NO 2025 dropback leader by week):** Rattler led weeks 1-7. Shough took over in week 8 (35 to 25) and led weeks 8-18.
So the season-wide "most games led" rule picks Shough (10 games) over Rattler (7) and flags week 4. But in week 4 Rattler was the
Saints' starter, and Shough had 0 dropbacks. The column is headed "Starting QBs only", so a Saints fan will catch this.
Every other flag holds up under a "starter at the time" reading. CAR Dalton (Young out, the only game Dalton led), HOU Mills
(weeks 9-12 while Stroud was out), NYJ week 18 Cook, BAL Fagnano (third QB used) and MIN Wentz (Murray led 6 of the previous 8)
all stay flagged. NYJ week 2 is borderline: Fields started and left, and Taylor led 16 to 15. It stays flagged under the at-the-time rule.
**Fix:** Define the regular starter as the QB who has led the team in the most games *through that week* (ties broken by dropbacks).
Under that rule only NO week 4 changes. Rapp becomes **-0.02 (5 games)** against starting QBs (163 dropbacks; my value -0.017), and
he has 1 vs. backup QBs, not 2. Update the table cell, the chart label and bar, the hero bar (`"Rapp (2025, 1 vs. backups)"`) and the
stat-heads definition and list. Poyer (+0.05, 7), Gardner-Johnson (-0.17, 5) and Hamlin (-0.19, 1) are unchanged under either rule.
For the record: if NYJ week 2 were also counted as a starter game, Rapp's starting-QB figure would be +0.01 (6 games).

### 2. MUST FIX: the PFR numbers aren't pinned, so re-running changes the published story (CLAUDE.md: "Re-running it reproduces the published numbers")
**Evidence:** The PFR queries filter `week <= THRU` (9). `pfr_thru` is computed live, and right now raw_pfr_def week 9 has only 2 teams
(BAL, JAX). When PFR posts week 9, a re-run will change several things. The dateline will flip to "through week 9". The league yards
per throw (7.2), Tennessee's rank (29th), the safety averages (8.2 for 2026), the tackling universe (58) and the 8.9% average and
16th-best rank can all move. The sentence "PFR hasn't charted Green Bay's week 9 yet" is hard-coded and would become false.
**Fix:** Pin PFR with a constant (`PFR_THRU = 8`) and use it in every raw_pfr_def query, `safety_seasons()` included. Drop the
`pfr_thru` auto-detect, or keep it only as an assert. Also add the `AS_OF` date the other generators use.

### 3. SHOULD FIX: "If the Poyer-era number comes back against real starters, the trade did its job."
**Problem:** This sentence has two issues. It credits the trade for any change, which goes against the coordinator/roster confound
the story states three paragraphs earlier. It is also unclear which number it means: Poyer against starters is +0.05, not +0.13.
**Fix:** "If the number climbs back toward Poyer-era levels against starting quarterbacks (+0.05), that fits the trade working.
It still won't separate Hooker from the coordinator."

### 4. MINOR
- "Buffalo's best stretch with Bishop came with a steady veteran beside him." Hamlin's +0.40 sits higher in the same table. Add
  "against starting quarterbacks". Poyer's +0.05 is the best of the four there.
- "Throws his way gained 8.8 yards with Poyer..." reads as a total. Make it "8.8 yards **each**", as the Editor wrote it.
- Stat-heads: "Flagged Bills opponents" lists 6, but NYJ week 18 (B.Cook) is also flagged. It's left out because week 18 isn't a
  pairing game (Bishop played 15%). Say "Flagged games in these pairings".
- Stat-heads p = 0.063 comes from 20,000 draws. Full enumeration over all 2,002 splits gives 0.064 (128/2002). "1 in 16" holds either way.
- Chart 1 footer still says "Opponent's norm". "What that opponent usually does" would match the x-axis.
- Dek "is the fix they're counting on" and the lede's "So the Bills spent..." attribute motive. They're acceptable as framing and
  don't need a change.

---

## Verified (independent code)
1. **Backup-QB rule** reproduces exactly: 2025 wk2 NYJ Taylor, wk4 NO Rattler, wk8 CAR Dalton, wk12 HOU Mills, wk18 NYJ Cook; 2026 wk8
   BAL Fagnano, wk9 MIN Wentz. No ties under games-led. Starting-QB values: Poyer +0.051 (7 games, 220 dropbacks), Rapp -0.065 (4),
   Gardner-Johnson -0.174 (5), Hamlin LV -0.187 (1). The rule is sensible except for Rattler (issue 1).
2. **Chance check:** gap 0.302. My permutation (50k draws, different seed) gives two-sided 0.064, and exact enumeration gives 0.064.
   One-sided is 0.026. Because it is two-sided, "(either way)" is accurate, and "about 1 time in 16" is fair.
3. **League context:** 2025 Bills +0.089, 9th; 2026 +0.010, 14th. +0.128 ranks 6th among 2025 defenses; -0.174 ranks 31st among
   2026 defenses (also 31st in 2025). 32 teams each season.
4. **Worked example:** 2026 wk5 LA (Stafford): 55 dropbacks, 19.44 EPA, norm 0.011, so +0.342 over usual and -0.342 for Buffalo.
   It's the worst of the 5 Gardner-Johnson games. Under the table's + = better for Buffalo convention, the sign is consistent.
5. **Other numbers:**
   - Pairings 9/283, 6/194, 5/221 and 3/105, for 803 total. Hamlin's three are LV -0.19, BAL +0.78 and MIN +0.77.
   - Bishop 8.81 on 27 and 9.19 on 21.
   - Safety averages 8.63 and 8.24 depend on the universe. Mine are 8.55 and 8.29. Either way, "both a bit worse" holds.
   - TEN 8.21, 29th of 32, league 7.23.
   - Hooker 8.30 on 33; the rest 8.20 on 232.
   - Interceptions 5 of 8, rest 3. McKinney has 5 in nflverse and play-by-play (week 9 vs. NE: 2), and nobody has more.
   - Hooker missed tackles 3 of 55, 5.5%, against a pooled 8.9%. He is 16th either way; "ties him for 16th-best of 58" is the
     generator's universe.
   - Hooker: 7 games (weeks 1-4 and 6-8), 8th season (2019-2026), 17 career regular-season interceptions.
   - 9 Bills games left.
   - PFR 2026 coverage: weeks 1-8 are complete and week 9 has 2 teams, so the "through week 8" dateline is right today.
6. **Limits:**
   - "Tracked with" appears in the headline, dek and chart.
   - "1 in 16 ... suggestive, not proof".
   - The starters-only column and the Poyer +0.05 line are both there.
   - Hamlin's asterisk is in the text, and his bar is grey on the chart.
   - The coordinator/roster confound is stated.
   - Hooker's yards per throw are the same as his teammates'.
   - Small samples are labeled.
   - No "bet" or "betting" anywhere. The body has no jargon: EPA, dropbacks and norm appear only in stat-heads.
   - The headline matches the instruction.
   - Overclaims are limited to issue 3 and the "best stretch" line.
7. **Charts:** I viewed both. They're readable, on-brand, and their labels match the text. Chart 1 needs the Rapp label and bar
   change from issue 1.

---

# Re-check after fixes (2026-11-10)

## PASS

Both must-fixes and the should-fix are applied correctly. I re-derived everything that changed with my own code (/tmp/qf/d.py, e.py)
and found no new issues. Two cosmetic nits remain; neither blocks publishing.

### 1. Starter rule: confirmed
I implemented the rule myself on all 25 Bills games in 2025 and 2026 weeks 1-9, including 2024 for the "main passer the season
before" condition. A game is flagged when its dropback leader is neither the team's games-led leader through that week (ties
broken by dropbacks) nor its main passer the season before.

**Flagged games in the pairings** (these match yours exactly):
- 2025 wk2 NYJ, Taylor
- 2025 wk8 CAR, Dalton
- 2025 wk12 HOU, Mills
- 2026 wk8 BAL, Fagnano
- 2026 wk9 MIN, Wentz

2025 wk18 NYJ (Cook) is also flagged, but it isn't a pairing game.

**Previously flagged games that are now cleared:**
- NO wk4 (Rattler): led NO's games through week 4.
- CIN wk14 (Burrow): the games-led leader through week 14 was Flacco in my data, not Browning, but Burrow is cleared as 2024's main passer either way.
- PIT wk13 (Rodgers), CLE wk16 (Sanders) and LV wk6 (Cousins): each led their team's games as of that week.

All the other games are the team's usual starter. Nothing is mis-flagged.

**Starting-QB values (dropback-weighted):**

| Partner | Starting QBs only | Games | Backup-QB games |
|---|---|---|---|
| Poyer | +0.051 | 7 | 2 |
| Rapp | -0.017 | 5 | 1 |
| Gardner-Johnson | -0.174 | 5 | 0 |
| Hamlin | -0.187 | 1 | 2 |

These match the table, the chart, the hero bars ("Rapp (2025, 1 vs. backups)") and the stat-heads text.

**Borderline game, disclosed and not blocking:** NYJ wk2. Fields started, and Taylor led 16 dropbacks to 15. Through week 2 the
games-led count is tied 1-1, and Fields wins the tie-break on dropbacks (40 to 16). If that game counted as a starter game, Rapp's
starting-QB value would be +0.01 over 6 games. It affects only the Rapp cell.

### 2. PFR pin: confirmed
The generator now uses `PFR_THRU = 8` in safety_seasons, the Bishop query and the Tennessee query, with no live detection. My
week-8-pinned recompute:

**Tennessee and Hooker:**
- TEN 8.21 yards per throw, 29th of 32. League 7.235, shown as 7.2.
- Hooker 8.30 on 33 throws; the rest 8.20 on 232.
- Interceptions: 8 for the team, 5 for Hooker, 3 for everyone else.

**Bishop:** 8.81 on 27 throws and 9.19 on 21, unchanged.

**Missed tackles (my safety universe, 55 safeties):** pooled rate 8.96%, which rounds to 9.0%. That confirms the 8.9% to 9.0% move
came from dropping PFR week 9. Hooker is 16th, untied, in my universe. "Ties him for 16th-best of 58" is the generator's universe
and is consistent with mine.

**Safety yards per throw:** 8.63 / 8.23 in the generator against 8.55 / 8.27 in mine. The difference comes from how safeties are
defined. Either way, "both a bit worse than the average safety" holds.

### 3. Wording: confirmed in the text, chart and hero
- The tracking bullet, the "Against starting quarterbacks, ... best stretch" line, "8.8 yards each", "Flagged games in these
  pairings" and the Green Bay "as of 2026-11-10" note are all present.
- The chart 1 footer now reads "What that opponent usually does = ...".
- Chart 1: Rapp is labeled "(1 vs. backup QBs)" with a -0.02 bar.
- The dek is unchanged and fine.
- No "bet" or "betting", and no jargon in the body.

### Nits (optional)
- Chart label "1 vs. backup QBs" and hero "1 vs. backups" are plural. "1 vs. a backup QB" would read better.
- The NYJ wk2 borderline above could get a stat-heads note: "(Fields started and left hurt; Taylor led 16-15)".
