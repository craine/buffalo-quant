# Quant review: 2026-11-19-nfl-mismatches (stage 2)

Reviewed text: md5 b8e9a65bda3bd17b8db97141901853e6 (regenerated 18:22 ET after editor round 2), hero JSON, both PNGs, site card `nfl-mismatches`.

**Verdict: FAIL (publish with fixes).** Two factual errors in the body; everything else re-derives. No betting content.

## Issues (ranked)

### 1. Wrong threshold on the early/late split (must fix)
- Text: "Early in the season the effect is stronger: with a 14-point gap or more, the better team won 75% through Week 8 and 82% after."
- Problem: the generator computes `early, late` from `big` (gap >= 17), not 14. My recompute:
  - 17+: through Wk 8 n=164, 0.750; after n=256, 0.822 (these are the published 75%/82%).
  - 14+: through Wk 8 n=269, 0.736; after n=518, 0.784 (74%/78%).
- Fix: change the text to "with a 17-point gap or more" (and add the counts, 164 and 256 games), or compute on 14+ and publish 74%/78%.

### 2. "with Mitchell Trubisky starting" is false (must fix)
- Text: "at Patriots in 2024 (Week 18, with Mitchell Trubisky starting while the starters rested)."
- Problem: `raw_schedules.away_qb_name` is the wrong source. Josh Allen took the first snap. `raw_snap_counts` for 2024_18_BUF_NE: Allen 1 offensive snap, Trubisky 48, Mike White 20. In `raw_pbp`, BUF's first play is a J.Cook run; the second reads "BUF 11-M.Trubisky in at QB." Also "while the starters rested" is hard-coded text, and no query backs it.
- Fix: source it from `raw_snap_counts`, e.g. "(Week 18: Josh Allen played one snap, then backups Mitchell Trubisky and Mike White played the rest)."

### 3. "never by more than 15" (should fix)
- The largest projected margin is 15.09 (2019 Wk 3 MIA at DAL, 30.94 vs 16.77). Rounded, "15" is literally false.
- Fix: "never by more than about 15", or print one decimal (15.1).

### 4. The 87% mixes the seasons the model was built on (low; framing is otherwise honest)
- Text: "that team won 87% of 61 games."
- Split by era (projected margin 10+): 2019-23 (training) 36-8, 0.818 (said 0.828); 2018 2-0; 2024-26 (blind) 15-0. Blind count and "15-0" confirmed.
- The body already separates out the blind 15-0. Suggest adding "(36 of 44 in the seasons it was built on)" so the 87% isn't read as all out of sample.

### 5. Disclosures (low)
- "2,133 games since 2018": the model starts at Week 2. 2,277 REG games exist 2018 to 2026 Wk 10, and 2,133 is the Week 2+ count. Add "Weeks 2+" to the stat-heads section.
- In 71 of the 2,133 games, the team with the higher projected score had a win chance under 50%. "Said" uses max(p, 1-p) while "won" uses the higher projection, so the two sides are defined slightly differently. This is negligible and confined to the 0-3 band.
- 15 history games had exactly equal pregame margins and are counted with the away team as "better" (0-3 bin). Negligible.
- The 23% shrink uses full-season margins that include the pregame games themselves. That understates how much the gap shrinks, but the sentence as worded ("by the end of those seasons") is accurate.

### 6. Lead sentence (low, optional)
- "Two different ways of measuring land in the same place: teams in Buffalo's spot have won about 4 times in 5." The model's 81% is a forecast, not a record of how teams in Buffalo's spot did. This is acceptable as plain English; the editor can decide.

## Brand rule #1: PASS
- The generator's schedule query selects only `game_id, season, week, gameday, home_team, away_team, home_score, away_score`, plus `away_qb_name` for the 2024 note (not a market column). It never reads `spread_line`, moneylines, `total_line`, odds, `result` or `total`. `points_model._scores` reads only score and roof columns, and `_drives` reads `clean_drives`.
- I grepped the story, hero JSON and site dek for favorite/underdog/cover/spread/odds/bet/pick/lock/line. The only hit is the disclaimer "We don't use betting lines". "Bills by 11" has been removed. "Upset" is not market language.

## Verified (independent queries, /tmp/qa/hist.py and model.py)

**History**
- 5,205 games (1999-2025, both teams 4+ prior games).
- Bucket table exact: 1,254/.520, 1,524/.600, 840/.669, 800/.713, 367/.737, 220/.791, 200/.797.
- 17+: 420 games, .794, 86 losses + 1 tie ("about 1 in 5", "86 of 420, plus 1 tie" correct). 20+: 200, .797.
- Shrink: ratio 0.775, so "about 23%" holds.
- Worked example: 2021 BUF going in +17.14, JAX -11.43, gap 28.57; season end BUF +11.41, JAX -12.00, gap 23.41.
- Upset table: all 8 rows match on season, week, winner/score, better team and gap.
- 2006 MIA 31 at CHI 13: CHI is home, so "in Chicago" is correct.

**Bills as the better team (17+ gap)**
- 16 games, 11-5, 0 ties.
- Losses: at TEN 2021, at JAX 2021, vs JAX 2023 (BUF listed as home, location Neutral, Tottenham), at NE 2023, at NE 2024 Wk 18.
- The Bills were never on the wrong side of a top upset other than as the better team.

**2026 through Week 10**
- 150 games, all final, no nulls in weeks 1-10. Every team has 9 or 10 games (300 team-games).
- BUF +9.78 (2nd, behind JAX +13.89). MIA -8.44 (30th = 3rd-lowest). Gap 18.22 falls in the 17-20 bucket (.791, n=220).
- Week 11 is unplayed (13 games, no scores). 2026_11_MIA_BUF has BUF at home, 2026-11-22.

**Model**
- Bands match the stat-heads section exactly (1088/.548/.574; 791/.652/.687; 193/.751/.733; 61/.823/.869).
- 14+ projected margin: 6 games.
- BUF 30.29 vs MIA 19.51, P(BUF) 0.808, so 81% is correct.
- Leakage:
  - Ratings use only weeks before the game. I hand-checked BUF's offense rating for Week 11 from `clean_drives`: 2.7359, matching the model. It uses 101 BUF drives through Week 10.
  - Calibration coefficients and miss pairs come from 2019-23 only.
- "At every level, about as often as it said" holds on blind seasons (2024-26: 0-3 .549 vs .588; 3-7 .651 vs .665; 7-10 .751 vs .758; 10+ .813 vs 15-0, n=15). Brier: blind 0.224, training 0.226. The model is slightly underconfident, not overconfident.

**Reproducibility, charts, ledger**
- Clean copy (/tmp/qa/clean2) re-run reproduces the md, hero JSON and both PNGs byte-for-byte.
- Charts viewed:
  - Labels match the table and bands, nothing overlaps, and the 2024-26 framing is honest.
  - Both footers carry the source line; the history chart's sample size is in the subtitle.
- Ledger: no MIA_BUF Week 11 row yet. The story correctly says the number counts only once it's logged.

---

# Round 2 re-check (text md5 7b18e03cd9dc4650a845f34ccb882d4f, generated 18:24 ET)

**Verdict: PASS.** All round-1 issues are fixed and verified against my independent queries.

1. **Early/late split.** It now reads "17-point gap or more ... 75% through Week 8 (164 games) and 82% after (256 games)". This matches my recompute: 164 games at .750 and 256 games at .822.
2. **2024 Week 18.** The note now comes from `raw_snap_counts`: "Josh Allen played 1 snap, then Mitchell Trubisky and Mike White played the rest". This matches Allen 1, Trubisky 48 and White 20 snaps, and the pbp line "Trubisky in at QB" on BUF's second play. The hard-coded "starters rested" is gone.
3. **Largest projected margin.** The text now says "never by more than about 15". The max is 15.09.
4. **The 87% figure.** It now carries "(36 of 44 in the seasons it was built on)". This matches the 2019-23 split of 36-8.
5. **Week 1 exclusion.** The stat-heads section now notes "Weeks 2+ only". 2,133 games is correct.
6. **Lead line.** It now reads "History and our model point the same way: about 4 times in 5." This holds: history gives 79% and the model 81%.

Unchanged numbers were spot-checked against the round-1 recompute and are identical: bucket table, 86 of 420 plus 1 tie, 23%, the worked example, the upset table, 11-5, +9.8 (2nd), -8.4 (30th), 18.2, 79% (220 games), 6 projections of 14+, BUF 30/MIA 20 at 81%, and 15-0.

**Brand rule.** No betting language anywhere. The new `raw_snap_counts` query is not a market source.

**Reproducibility.** A clean-copy re-run (/tmp/qa/clean3) reproduces the md, hero JSON and both PNGs byte-for-byte. The chart PNGs are byte-identical in size to the versions I viewed.

**Still open, low and optional.** In 71 games the team with the higher projected score had a win chance under 50%, and in 15 games the two teams had exactly equal margins going in. Neither moves a published number.

# Stage 4 final check (same text, md5 7b18e03c...)

**PASS.** I checked what changed since round 1: the early/late sentence, the Week 18 note, "about 15", the 36-of-44 aside, the Weeks 2+ note and the lead line. I also checked everything those changes touch: hero JSON note, site dek and both charts. All are consistent with the data and with each other.

# Final check after the plain-language rewrite

**PASS.** Compared with the previously final-checked text (sha256 f75652c7..., git HEAD): only wording changed. Every number removed or added in the md was a lead number that is also in the body: removed "17" x2, "27", "30", "20", "4 in 5"; added "1999", "9.8", "8.4", "18.2". The hero JSON adds "16", the Bills' 16 games as the much better team, already in the body. The tables and stat-heads section are unchanged. "18.2 points a game better" is the same gap shown in the table and on the chart. A clean-copy re-run (/tmp/qa/clean5, tracked files plus the current generator) reproduces the md, hero JSON, nfl-mismatch-history.png and nfl-mismatch-model.png byte-for-byte. Charts viewed.
