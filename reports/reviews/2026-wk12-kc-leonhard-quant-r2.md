# Quant review (stage 2, round 2): 2026-wk12-kc-leonhard — FAIL (one text fix, one generator fix)

Round 1 report: `2026-wk12-kc-leonhard-quant-r1.md`. All round-1 fixes checked against the current md, hero, card and generator,
and the new numbers re-derived with my own queries (scripts in /tmp/qa, outside the repo).

## Must fix

### 1. Closing line in "Why it matters Thursday" is contradicted by the data
Text: "Extra rushers only pay off if they get home, and this year Buffalo's mostly haven't."
(This was my round-1 suggestion; I didn't check it then. It's wrong.)
- Buffalo 2026, weeks 1-10 (own query): with 5+ rushers, opponents gain -0.013 per dropback (133 db); with 4 or fewer, +0.026 (242).
  So Buffalo's extra rushers have helped, by this measure (13th of 32 on 5+ plays). "Only pay off if they get home" is also not true
  in general: league-wide, 5+ rusher plays average +0.010 vs +0.065, a gap far bigger than sacks alone explain.
- What *is* true and on-topic: when Buffalo sends 5+, it gets a sack on 6.8% of those dropbacks (9 of 133), 25th in the league;
  league average on 5+ plays is 8.6% (298 of 3,474).
Replacement (writer computes and asserts the three numbers in the generator):
> When Buffalo does send five or more, it gets a sack on 6.8% of those dropbacks, 25th in the league (league average: 8.6%).
Or simply delete the sentence.

### 2. Generator: two hard-coded numbers (no text change)
Stat-heads line "equals rushers minus four on all but 1 of {len(s26):,} dropbacks (89% in 2025)": the "1" and "89%" are literals.
Both are right (my counts: 1 mismatch of 11,093 in 2026; 89.1% match in 2025), but every published number must come from code.
Compute both and print them from variables. The md stays byte-identical, so this doesn't change the hash the final check signs.

## Verified (round-2 changes)
- Week 11 paragraph: Denver man weeks 1-8 0.557 (307 db), weeks 9-18 0.3549 -> "35%" is correct (my round-1 "36%" was a rounding slip).
  Season 44%, game 33% (49 db), 5+ 27%; Denver 5+ weeks 9+ 0.306. Mahomes +0.02 vs +0.17. Wording no longer claims a cause.
- Blitz sentence removed from body; blitz numbers removed from stat-heads; FTN note true (see item 2).
- Bad FTN rows: setting n_pass_rushers > 11 to missing affects exactly 2 rows (TB, 2026 wk 8 and 9). `profile()` and the league split
  use charted rows only. League 2026 5+ moves 0.3134 -> 0.3132 (still 31%); no Buffalo, Kansas City or Mahomes play is affected.
  "FTN coverage 100%" in stat-heads sits next to "Two FTN rows ... are dropped", which is clear enough.
- League context: league 5+ 26.7% -> 31.3%; Buffalo +0.104 vs league +0.046 (2.26x, "more than twice" holds); 24 of 32 teams up.
- "The extra rushers haven't turned into sacks": Buffalo 5.6% (20th) vs 6.8% in 2025; league 6.5%.
- Mahomes split: +0.137 (93) vs +0.179 (234); league +0.065 (7,617) vs +0.010 (3,474) -> "+0.06 / +0.01". Dip 0.043 vs league 0.055:
  "about what they cost every offense" fair. "Far above the league" (+0.14 vs +0.01) fair. Small sample labelled.
- Lead: "who has been good this season whether teams send extra rushers or not": fair (+0.14 / +0.18, KC 6th).
- Coverage rows now limited to MAN/ZONE: Denver 44.4% 1st, league 30.8%, Buffalo 31.3% 14th, Week 11 32.7%: unchanged.
- Example: 2026 Week 2, DET at BUF, "J.Goff sacked at DET 30 for -7 yards (15-G.Rousseau)", 5 rushers. raw_players: 00-0033106 Jared Goff,
  00-0036914 Greg Rousseau. Correct.
- Italic line: "the Bills' first 9 games; Week 11 isn't fully charted yet": true (FTN has 1 of 8 loaded Week 11 games).
- "Through nine games under Leonhard": 9 games, Week 7 bye. Correct.
- Hero: 35 / 25, note no longer claims cause; "pass plays" label matches the story's dropback definition. Card dek: true
  (Denver most man coverage, most sacks by rate and total, 68).
- Headline: no cause claim. Chart unchanged in content (re-opened; values 27/32/25/35, 31/44/31/n.a., 6.5/9.8/6.8/5.6; footer n's and 2026
  averages correct). PNG bytes changed from round 1 because of the MAN/ZONE filter (sub-pixel), so the image hash differs from round 1. Freeze
  it at publish time.
- Reproducibility: clean copy, outputs deleted, generator re-run: md, hero JSON and PNG byte-identical
  (PNG sha256 710505058a3b...e8a2a0).
- No betting language. Leonhard's titles unchanged and verified in round 1 (buffalobills.com, NFL.com, SI).
