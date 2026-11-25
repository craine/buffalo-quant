# Quant review: 2026-11-25-allen-yolo (round 1)

**Verdict: publish with fixes (recorded as fail).** Every number in the story, hero and site card reproduces from an
independent re-derivation. A clean-copy re-run is byte-identical. The must-fixes are one overclaim ("every year"), one
mislabel ("starts"), a missing chance baseline that makes the "most interceptions" half of the finding look stronger
than it is, a missing game-script caveat, one number typed in by hand, and an undisclosed sensitivity to how quarter
boundaries are drawn.

## Reproduction

- Clean copy (`tar` of the working tree without `data/` and `site/`, `data` symlinked to the shared DB and cache), the
  three outputs deleted, then `python3 -m src.reports.allen_yolo_history_nov25`. It exits 0, and the md, PNG and hero JSON are
  **byte-identical** to the working copy. The md SHA-256 is `78f5b970…a585`, the same as the self-check record.
- Caveat: the nflverse parquet cache is shared through the symlink, so the re-run did not re-download. The
  `NFLV_FINGERPRINT` and `PBP26_FINGERPRINT` asserts are what protect against upstream drift. Both passed.

## Independent re-derivation (/tmp/qa/rederive.py, own code)

I wrote my own code. Traded players keep the 2TM row. Team games for 2003+ came from `raw_schedules` (finals only, 2026
through Week 11), not from player stats. nflverse is summed by gsis id. Each percentile is the share of the *other*
qualified starters below the player, counting ties as half. Results:

| Claim | Story | Mine |
|---|---|---|
| Interceptions by quarter (fewest to most) | 25/16/9/10 | 25/16/9/10 |
| Yards per completion by quarter (shortest to longest) | 7/13/11/29 | 7/13/11/29 |
| Passing value by quarter | 3/6/12/39 | 3/6/12/39 |
| "Both" (int <= 50%, ypc > 50%) / careful-but-short | 27 / 14 | 27 / 14 (others: 13 high-int long, 6 high-int short) |
| Non-qualifiers | 7 | 7: Foles 2017 (101 att), Hostetler 1990 (87), D. Williams 1987 (143), Bradshaw 1974 (148), Griese 1972 (97), Morrall 1970 (93), Dawson 1969 (166) |
| Qualified only, fewest / most | 24 / 9 of 53 | 24 / 9 of 53 |
| 1966-95 fewest / most | 14 / 4 | 14 / 4 |
| 1996-2025 fewest / most | 11 / 6 | 11 / 6 |
| Gunslinger list (10) | as listed | same 10 (Dawson 1969 is a non-qualifier in a 9-starter AFL pool) |
| Favre 1996 | 13 int / 543, 12.0 ypc, 7.5 value | 13/543, 3899/325 = 12.0, (3899+780-585)/543 = 7.54; value rank 2nd of 32 |
| Favre seasons >= 90th pct interceptions | 1993, 2003, 2005, 2008, 2010 | same (1.000 in 2005 and 2010; 0.967, 0.938, 0.969) |
| Allen table, all 9 rows | as printed | identical (att, int and all 27 percentiles) |
| Allen 2024 int rate | 4th lowest of 36 | 4th lowest of 36, no tie |
| Allen 2026 int rate | 6th highest of 31 | 6th of 31 (9/302 = .02980; Winston 5/167 = .02994 is 5th, Penix .02893 7th, so it's a near tie) |
| Allen 2026 att/int, second way (play-by-play, `pass_attempt=1 & sack=0`) | 302 / 9 | 302 / 9 (2024: 483/6, 2025: 460/10, also match) |
| Allen ypc above middle | 7 of 8 | 7 of 8 (2021 = 39th) |
| Miami: dropbacks, EPA, int, sacks, runs | 48, -0.032, 2, 3, 0 | 48, -0.0321, 2, 3, 0. No scrambles or kneels in his rows |
| Miami vs career | 22% of 135 worse | 30/135 = 22.2% |
| Miami 2026 rank | 2nd-worst | 2nd of 10 (only LAC Wk 3 worse) |
| League QB-games 2026 worse | 39% | 130/330 = 39.4% |
| 1960s pool sizes (caveat) | 9 to 15 | 9 (AFL '68, '69) to 15 (NFL '67). True, but typed by hand |
| ypc vs deep-throw correlation | 0.42 | not re-derived independently; the generator's query is correct (true attempts, scrambles via COALESCE, no 2-pt) |

**PFR source file, internal checks.** cmp <= att, td <= cmp and int <= att - cmp hold on all 1,443 rows. No player has
more than 16 games, and the max games per season are right (14, then 16 from 1978, 9 in 1982, 15 in 1987). Where a 2TM
row and both team rows are present (Hadl 1974, Kemp 1991, Collins 1998), the team rows sum exactly to the 2TM row. After
dropping team rows there are no duplicate (season, league, player) rows. The extremes look plausible (top ypc Morton
1970 17.8; worst completion rate Marangi 1976 35%). The file is a *subset* of PFR. Most rows have 100+ attempts, plus a
handful of low-volume rows for players of interest (Favre 1991, Hostetler 1988-90, Morrall). That's fine, because the
lowest qualification bar (126 in 1982) is above it. Completeness check: every nflverse 1999-2002 QB with 224+ attempts
is in the PFR file. Jim Miller (CHI 2001-02) looked missing only because `raw_players` has no pfr link for him.

**Cross-source check, more detail.** In 1999-2002, attempts differ by 1-3 on 19 of 144 same-games QB-seasons, mostly
1999 (nflverse is lower). Completions differ only on Fiedler 2001. The stat-heads line says "agree exactly on yards, TDs
and INTs", which is accurate. Because ranks are within one season and each season uses one source, this doesn't move
any rank.

## Must-fix

1. **Overclaim: "every year."** "What it means": `Champions throw downfield; Allen does that every year.` is false. In 2021
   his yards per completion was 39th percentile, and his deep-throw share was below the middle in 2021 (45%) and 2025
   (48%). Replace with `Champions throw downfield; Allen has done that in 7 of his 8 full seasons.` Generate the number
   from `a_ypc_above` and `len(A[A.yr <= 2025])`.

2. **"Starts" are games with 15+ dropbacks.** The 135 includes 2018 Week 1 at Baltimore, where Allen came on in relief;
   the schedule lists Peterman as the starter. The schedule's QB ids give 134 Allen starts through Week 11. The league
   pool likewise includes relief appearances.
   - `only 22% of his\n135 career starts were worse` -> `only 22% of his\n135 career games were worse`
   - `39% of all NFL starts this season have been worse` -> `39% of all NFL quarterback games this season have been worse`
   - Stat-heads: `his career starts with 15+ dropbacks: 135` -> `his career regular-season games with 15+ dropbacks: 135 (league games this season: 330)`. Compute the 330 as `len(lg)`.

3. **Missing chance baseline. The "most interceptions" side is close to chance.** By construction, about 15 of 60 champions
   land in each quarter if a stat doesn't matter. The fewest-interceptions count (25) is far above chance (binomial
   P(>=25) = 0.003). The most-interceptions count (10) is not far below it (P(<=10) = 0.09). In 1996-2025 it is 6 of 30
   against 7.5 expected, which is chance. The "both halves" sentence presents 11 and 6 as the same pattern.
   - After `Then we found where each Super Bowl winner ranked the year he won: top quarter, bottom quarter, or in between.` add
     `If a stat had nothing to do with winning, about {len(C)//4} of the {len(C)} champions would land in each quarter.`
   - Replace `It holds in both halves of Super Bowl history too: 14 of the first 30 champions (1966-1995) were in the
     fewest-interceptions quarter and 4 in the most; for the last 30 (1996-2025), 11 and 6.` with
     `The few-interceptions side holds in both halves of Super Bowl history: 14 of the first 30 champions (1966-1995) and 11
     of the last 30 (1996-2025), where chance would give 7 or 8. The other side is weaker: 4 of the first 30 were in the
     most-interceptions quarter, but 6 of the last 30, close to chance.` Generate every number in code.
   - Stat-heads, add: `Chance check (binomial, p = 0.25): 25+ of 60 in the fewest-interceptions quarter, P = 0.003; 10 or fewer
     in the most, P = 0.09; 29+ top-quarter yards per completion, P < 0.001.` Compute with scipy, or exactly in code.

4. **Game script: an alternative explanation that the story never names.** Champions play on good teams that lead more
   often, and quarterbacks with a lead throw fewer desperate late passes. Part of a champion's low interception rate is a
   *result* of winning, not only a cause. The headline is prescriptive ("throw it deep, but don't throw it away"), and
   "What separates most champions" reads as causal. Add a Caveats bullet: `Winning teams play with the lead more, and
   quarterbacks with a lead throw fewer desperate passes. Some of a champion's low interception rate comes from being
   ahead, not only from being careful.` "What it means": `What separates most champions is the second half:` ->
   `What sets most champions apart is the other part:` (see the editor note on "second half").

5. **Hand-typed number.** Caveats: `In the 1960s there were only 9 to 15 starters per league` is a literal. It's correct
   (9 = AFL 1968/1969, 15 = NFL 1967), but it breaks the every-number-computed rule. Compute it as the min/max of qualified
   pool sizes over 1966-69 in the leagues used, and assert it.

6. **Disclose quarter-boundary and method sensitivity.** The champions use an exclude-self mid-rank percentile, and three
   champions sit exactly on a boundary: McMahon 1985 and Namath 1968 at 25% (counted in "fewest"), Stabler 1976 at 75%
   (counted in "3rd", not "most"). With strict boundaries, interceptions are 23/18/8/11. With the method the Allen table and
   Favre use (pandas `rank(pct=True)`, self included), they are 22/19/8/11. So the headline "25" and "10" depend on the
   method, though the direction holds every way. Add a stat-heads line, computed:
   `Ties at a boundary count in the lower quarter (McMahon 1985 and Namath 1968 sit exactly at 25%, Stabler 1976 at 75%). With
   strict boundaries the interception counts are 23/18/8/11; with the self-included rank used in Allen's table, 22/19/8/11.`
   Better still, use one percentile method throughout. Champions and Allen/Favre/the chart's Allen dots currently use
   different formulas.

7. **Chart annotation uses "picks".** `Few picks, long completions` is football slang, but "picks" is on the brand rule 1
   banned list, and the chart travels alone. -> `Few interceptions, long completions`. Also delete the unused `labels = ["Fewest\npicks", ...]`.

## Optional polish

- 2026 "6th highest of 31" is a near tie: Winston (.02994) is 5th, Allen (.02980) 6th. Fine as is. If it goes on radio,
  "about 6th" is safer.
- The 2026 bar is 14 x 11 = 154 attempts. QBs on teams that have had their bye are held to a 154 bar over 10 games. Only
  McCarthy (142 att, 2 int) is affected. Adding him makes Allen 6th of 32, so the rank holds but the denominator changes.
  Consider bar = 14 x that QB's team games, or say it.
- 1987: a bar of 210 (15 team games including replacement games) excludes strike-year regulars (Tomczak 178, Hogeboom 168,
  Testaverde 165...). It doesn't affect Doug Williams's placement much (he's a non-qualifier either way), but the pool is
  thinner. A one-line note, or a per-team bar.
- Favre: `lower than 91% of starters'` uses the self-included rank (29 of 32). Against other starters it's 29 of 31 = 94%.
  Either is defensible, but "lower than 29 of 31 other starters" is cleaner.
- Stat-heads: the cross-source line could add "attempts differ by 1-3 on 19 of 144, mostly 1999".
- "Throw it deep" in the headline rests on yards per completion, a loose proxy (0.42). The body says "rough sign". The
  headline is OK, but "throw it downfield" would match the chart title.

## Checked and fine

- League handling: 1966-67 champions (Packers) are ranked within NFL only, and 1968-69 (Jets, Chiefs) within the AFL. 1966-67
  AFL tables aren't in the file, which is fine because no champion needs them. The "1968-69 AFL" stat-heads line is accurate.
- Traded players: the PFR 2TM row is kept and its team rows dropped. nflverse sums across teams. All 60 champions match exactly one row.
- Circularity: "passing value" includes -45 per interception, and the stat-heads say so. No body claim uses passing value
  to support the interception claim. "Both" uses interceptions and yards per completion, which are independent constructions.
- Brand: no betting language in the body, hero or card. No ledger calls in this story. Regular season only throughout.
- Hero JSON and site card numbers (25, 10, 29, 60, 6th of 31) match.
- Chart: counts in the right panel match the table above. Allen's dots match his table. The footer has the source and the
  starter definition. The sample size is in the subtitle (60).
