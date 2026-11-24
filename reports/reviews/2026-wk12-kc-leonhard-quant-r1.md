# Quant review (stage 2): 2026-wk12-kc-leonhard — FAIL (publish after fixes)

Reviewed: story md, hero JSON, PNG, site card `bills-chiefs-leonhard-file`, generator `src/reports/bills_kc_leonhard_wk12.py`.
All numbers re-derived with my own queries on `data/buffalo.db` (scripts in /tmp/qa, not in the repo), not by re-running the writer's functions.

Most numbers are correct. One paragraph is wrong in substance (Denver vs. Mahomes), one stat is a duplicate presented as
a second measure (FTN "blitz" in 2026), and the Mahomes split lacks the league context that changes what it means.

## Must fix (ranked)

### 1. Denver vs. Mahomes, Week 11: "went away from its usual style" is not supported
Text: "Against Mahomes, Denver went away from its usual style. It played man on 33% of his 49 dropbacks, well below its season
rate, and sent five or more rushers 27% of the time. ... But Denver didn't need its usual heavy dose of man coverage to slow him down."

Evidence (own query, 2025 participation joined to dropbacks):
- Denver's man rate by week: wk1 56%, wk2 68%, wk3 62%, wk4 48%, wk5 62%, wk6 59%, wk7 35%, wk8 50%, **wk9 19%, wk10 17%**,
  wk11 33%, wk13 45%, wk14 41%, wk15 37%, wk16 33%, wk17 46%, wk18 48%.
- Weeks 1-8: 55.7% (1st, 307 db). Weeks 9-18: 35.5% (8th, 386 db). Denver's other 16 games: 45.3%.
- So 33% against Mahomes was in line with what Denver was already doing by mid-season (the two games just before were 19% and 17%).
  It was not a plan for Mahomes and not "going away" from its style at that point of the season. It was also still above the
  league average (31%).
- 5+ rushers: 27% (13 of 49) vs. Denver's 31% in weeks 9-18 and 32% for the season: a gap of about 2 plays.
- 49 dropbacks: the standard error on a 33% share is about 7 points, so "well below" is not supportable either.
- Mahomes +0.017 vs. his 2025 +0.165 is correct. But Denver allowed -0.078 per dropback all season vs. a league +0.043,
  so a simple expectation for Mahomes against Denver is about +0.04. He was a bit below that, not dramatically.
- "Slow him down" credits a cause (coverage choice) that one game can't show.

Replacement (writer must add the 56% and 36% to the generator: Denver man share weeks 1-8 and weeks 9-18):
> Against Mahomes, Denver played man on 33% of his 49 dropbacks. That's below its 44% for the season, but it's about what Denver
> was doing by then: after playing man on 56% of dropbacks through Week 8, it dropped to 36% from Week 9 on. It sent five or more
> rushers 27% of the time. Mahomes was held to +0.02 points per dropback, below his 2025 average of +0.17. One game is a small
> sample, and it can't tell us which part of Denver's plan worked.

### 2. "It blitzes on 35% of dropbacks, as FTN charts it (8th)." Delete
In 2026 FTN's blitzer count equals rushers minus four on 11,092 of 11,093 dropbacks (2025: 89%). So in 2026 "blitz" and
"5+ rushers" are the same stat (BUF 0.3547 both, rank 8 both; league 0.3134 vs 0.3133). The sentence reads like a second,
independent confirmation and it isn't. FTN appears to have changed how it records blitzers in 2026.
- Body: delete the sentence.
- Stat-heads: the 2025 blitz numbers (DEN 0.302, BUF 0.309, league 0.294) and 2026 (BUF 0.355, league 0.313) are not comparable.
  Replace the blitz entries with a note: "FTN's 2026 blitzer count equals rushers minus four on all but 1 of 11,093 dropbacks
  (89% in 2025), so we use rushers only."
- "How we measured it": "records how many players rushed the passer and how many of them were blitzers on every NFL play. For example,
  in Week 2 FTN charted a Bills sack with 5 rushers, 1 of them blitzing." -> "records how many players rushed the passer on every NFL
  play. For example, on a Week 2 sack of Jared Goff (by Greg Rousseau), FTN counted 5 Bills rushers." (verified: 2026 wk2 BUF vs DET,
  "J.Goff sacked at DET 30 for -7 yards (15-G.Rousseau)", 5 rushers.)

### 3. The rise in extra rushers needs the league's own rise next to it
Text: "up from 25% (21st) in 2025. The league average this season is 31%."
League 5+ rate rose too: 26.7% (2025) to 31.3% (2026), and 26.8% to 31.3% on weeks 1-10 only; 24 of 32 teams are up. Whether that's
real or a charting change (see item 2) I can't tell. Buffalo's rise (+10.4 points; +11.6 vs. its own 2025 weeks 1-10) is more than twice
the league's (+4.6), and the rank move 21st -> 8th holds, so the claim survives with context. The chart's grey bar is the 2025 average
sitting next to the 2026 Bills bar; the body should carry both averages.
Replacement:
> up from 25% (21st) in 2025. Teams across the league are sending more this year (27% last season, 31% now), but Buffalo's jump is
> more than twice as big.

### 4. "The pressure hasn't turned into sacks."
2026 pressure isn't measured (participation not published; asserted 0 rows). The sentence is about extra rushers.
Replacement: "The extra rushers haven't turned into sacks."

### 5. Mahomes vs. extra rushers: small-sample label and league context
Text: "Against five or more rushers, Mahomes has averaged +0.14 points per dropback (93 dropbacks). Against four or fewer: +0.18 (234).
Extra rushers have slowed him only a little."
Verified: +0.1365 (93), +0.1794 (234). But league-wide in 2026 (weeks 1-10) passing plays average +0.065 against four or fewer and
+0.010 against five or more (7,617 / 3,476 db). Mahomes' dip (0.04) is about the league's (0.055); what stands out is his level
against extra rushers (+0.14 vs. the league's +0.01). 93 < 100: needs the explicit small-sample label (CLAUDE.md).
Replacement (writer adds the two league numbers to the generator):
> Against five or more rushers, Mahomes has averaged +0.14 points per dropback; against four or fewer, +0.18. That's a small
> sample (93 and 234 dropbacks). Extra rushers cost him about what they cost every offense (league-wide: +0.06 against four or
> fewer, +0.01 against five or more). The difference is that even against extra rushers, he's far above the league.
Lead, last sentence: "On Thursday they face Patrick Mahomes, and extra rushers haven't slowed him much this season." ->
"On Thursday they face Patrick Mahomes, who has been good this season whether teams send extra rushers or not."

### 6. Hero note overclaims cause
Text: "The extra rushers came with Leonhard from Denver. The sacks haven't: Buffalo is 20th in sack rate."
We can show timing, not that Leonhard brought the approach (Brady is also new as head coach; Denver's 32% was 6th, not extreme).
Replacement: "Since Leonhard arrived from Denver, the Bills send extra rushers far more often. The sacks haven't followed: Buffalo is 20th in sack rate."
(Headline: see Editor report; same issue, softer.)

## Should fix / minor
- "Man or zone coverage comes from the NFL's own play tracking, published by nflverse." I could not verify the upstream source of
  `defense_man_zone_type`; the nflreadr participation dictionary names no source for it. Say "comes from play-by-play charting
  published by nflverse" unless the writer can cite the source.
- Mahomes' 2025 average includes his injury-shortened Week 15 (35 db, -0.035). Excluding it: +0.178 (552). Either is defensible; say
  which in stat-heads. Doesn't change the sentence.
- "first 9 games": correct (2026 weeks 1-10, bye Week 7; 9 games). By publication the Bills have played 10; Week 11 isn't charted
  (FTN has 1 of 8 loaded Week 11 games). Suggest "Through Week 10 (9 games; the Miami game isn't charted yet)" somewhere visible.
- Consistency: the Nov. defense baseline story had the pass defense 24th through Week 8. I reproduce 24th (+0.124) through Week 8 with
  this definition; it's 11th through Week 10. Not a contradiction, but it's a big two-game swing worth a clause ("up from 24th after Week 8").
- Generator: `mz.notna()` keeps 19 empty-string coverage rows in the denominator (league 0.3078 vs 0.3081 if excluded; no published
  number changes). Two FTN rows with 56 and 67 rushers (TB, 2026 wk8/wk9) are data errors counted as 5+; TB only, no published number
  changes. Comment "a Bills play with 6 rushers" is stale (query takes 5+). No `AS_OF` constant (week pin only).

## Verified (own numbers)
- Dropbacks: `pass==1`, EPA not null, `play_type <> 'no_play'`, no 2-pt, no spikes, REG. 2025: 19,736; 2026 wk1-10: 11,093. 4 rows with
  qb_dropback 0 (play_type run, no sack/scramble) are included, negligible. No duplicate (game_id, play_id) in pbp, FTN or participation.
- FTN LEFT JOIN keeps all rows (30,829 = 30,829); coverage 100% in 2025 and 2026 wk1-10. All 150 wk1-10 games final; pbp has all 150.
- Man: values present are MAN_COVERAGE (2_MAN, COVER_0, COVER_1), ZONE_COVERAGE, '' (19 db), NULL. `str.contains("MAN")` is correct.
- DEN 2025: 693 db; man 44.44% (1st; PHI 43.61% 2nd, no tie); Cover 1 30.9% (most common); 5+ 32.18% (6th); sack 9.81% (1st; CLE 9.43%,
  no tie; also most total sacks, 68 vs ATL 57, so the card's "the most sacks" holds); EPA/db -0.078 (5th); pressure 34.5% (2nd).
- League 2025: man 30.8%, 5+ 26.7%, sack 6.52%, pressure 29.8%. League 2026 wk1-10: 5+ 31.3%, sack 6.46%.
- BUF 2025: 530; 5+ 25.09% (21st); sack 6.79% (14th); EPA/db -0.067 (8th); man 31.3% (14th); pressure 33.8% (5th).
- BUF 2026 wk1-10: 375 db, 9 games; 5+ 35.47% (8th); sack 5.60% (20th; LA 6.00% 19th, ATL 5.50% 21st, no tie); EPA/db +0.012 (11th; DEN
  +0.0099 10th, CIN +0.0152 12th).
- DEN-KC: 2025_11_KC_DEN, DEN 22-19 home; 2025_17_DEN_KC, DEN won 20-13 at KC. Mahomes: 49 db in wk11 (all KC dropbacks), +0.017; man
  32.7%, 5+ 26.5%, pressure 30.6%. Mahomes' last 2025 game Week 15 (weeks 16-18 KC passers were other QBs); 2025 +0.165 (587).
- KC 2026 offense +0.167 (6th), 327 dropbacks, all Mahomes (so "Kansas City's passing game" = Mahomes here). Mahomes vs 5+ +0.137 (93),
  vs <=4 +0.179 (234).
- Chart: all bar values match (27/32/25/35; 31/44/31/n.a.; 6.5/9.8/6.8/5.6). Footer n's 693/530/375 and 2026 averages match.
- Hero: 35 / 25, Denver 0.444 vs 0.308: match. Card: matches story; "most sacks" true by rate and total.
- Leonhard's titles: 2024 DB coach / pass game coordinator; 2025 assistant head coach (and pass game coordinator); Vance Joseph DC.
  Sources: buffalobills.com ("Bills hire former Buffalo safety Jim Leonhard as defensive coordinator"), NFL.com ("Bills hiring Broncos
  assistant head coach Jim Leonhard as defensive coordinator"), SI Mile High Huddle ("Broncos lose Jim Leonhard ...", names
  "defensive coordinator Vance Joseph"). None says who called Denver's defense; the story doesn't claim it. OK.
- Reproducibility: copied the repo to a clean directory, deleted the three outputs, ran `python3 -m src.reports.bills_kc_leonhard_wk12`:
  md, hero JSON and PNG byte-identical (PNG sha256 9c2355b6...ec63a).
- No betting language. Stat terms confined to stat-heads except "points per dropback" (see Editor).
