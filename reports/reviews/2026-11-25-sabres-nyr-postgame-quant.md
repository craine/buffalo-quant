# Quant review: Sabres 5, Rangers 1 (2026-11-25-sabres-nyr-postgame)

Reviewer: independent Quant (stage 2). Reviewed commit 62c1e633, story sha d6824a2d.

## Verdict: fail. Publish after fixes.

The numbers are right. Every figure in the body, table, chart, hero and dek re-derives independently. Three claims need
fixing: the goalie "usual starter" line isn't supported, the Receipts section grades two season-long calls on one game
(once against us, once in our favour), and the "paid back" wording teaches the reverse of our own Tampa finding.

## Must-fix

### 1. "usual starter" is not supported by the data

Text: "At the other end, the Rangers started Joonas Korpisalo instead of their usual starter, Dylan Garand (16 games)."

Evidence (first NYR goalie to face a shot in each game, raw_nhl_plays): Garand started 14 of New York's 23 earlier games,
Shesterkin 5 (none since Oct. 9), Korpisalo 3, Reimer 1. "16" is Garand's appearances, including 2 in relief, not his starts.
Since Nov. 7 the two have strictly alternated: Korpisalo Nov. 7, 11 and 16; Garand Nov. 9, 13 and 22. Korpisalo starting on
Nov. 25 was his turn, not a swap. The generator's guard `nyr_starts.iloc[-1] > 3 * k_games` counts appearances, so it can't
catch this.

Replace with: "At the other end, the Rangers started Joonas Korpisalo, who has been taking turns with Dylan Garand since early November."
(If a number is wanted, compute starts in the generator: "Garand has started 14 of their 24 games, Korpisalo 4.")

### 2. Receipts: grades two season-long calls on one game, in both directions

Text: "**Our preview** said the Rangers' finishing (30th in the NHL) probably wouldn't last. It lasted one more night: 1 goal on
chances worth 2.3. It said their goaltending would probably cool off. It did, though with Korpisalo, not Garand, in net: 5 goals allowed."

Problems: (a) The preview said both were season-long expectations and stated outright, "It won't necessarily show up in one game."
Scoring the finishing call as a one-night miss is unfair to the preview. (b) Scoring the goaltending call as a hit ("It did") on one
game is the same mistake in our favour. (c) "not Garand" suggests the preview expected Garand. It didn't: it said "Starters weren't
confirmed when we published." Also see issue 1.

Replace with: "**Our preview** said the Rangers' poor finishing (30th in the NHL) probably wouldn't last and their goaltending would
probably cool off. It also said one game wouldn't settle either. On Wednesday New York scored 1 goal on chances worth 2.3, and
Korpisalo allowed 5 on chances worth 2.5. Both are season-long calls, and we'll keep tracking them."

The Ledger bullet is fair: the miss is stated plainly, Brier 0.2601 is right, and "about what a coin flip earns" (0.25) is fair. 13 of 22 is right.

### 3. "paid back" says bad luck gets repaid, which our own Tampa finding contradicts

Text (lead): "The last four games paid most of that back."
Text (site dek, src/site/build.py): "...paying back an unlucky first 21 games."

The arithmetic is right. The first 21 games had a gap of 10.5 goals (finishing -7.1, goaltending -3.4), and the last four made up
9.9 of it. "Paid back" describes it as a debt being repaid. The Tampa recap (r = 0.10 for finishing between first and second halves)
found the opposite: finishing doesn't carry over in either direction, so a cold start creates nothing that has to be repaid. The four-game
hot streak was just as much luck as the cold start. The "What to expect" section says this correctly. The lead and dek should match it.

Replace lead sentence with: "A hot four games has cancelled most of that out, and the hot streak is no more likely to last than the cold start was."
Replace dek phrase with: "cancelling out an unlucky first 21 games".
The headline "the early bad luck has evened out" is acceptable as a statement about the running total, because the chart shows
exactly that. It does lean the same way, though. The Editor may prefer "cancelled out".

## Should-fix

4. "That's why the record, 11-10-4, looks like a team that gets a little less than half the chances." Loose: 11-10-4 is 26 of 50
   points (.520), above .500. What does match the chances is goal difference. Not counting empty nets, they've been outscored 75-82, and
   their chances say 74.5-81.0. Suggest: "That's why they've been outscored by 7, close to what their chances say." (The generator needs
   to compute these numbers; they're from my derivation.)
5. Table footnote "Goals in the table leave out empty-net goals." The figures also leave out the shootout winner on Oct. 13 at Montreal.
   The scoreboard says Buffalo allowed 74 in its first 21 games; the table says 72 (minus 1 empty-net goal, minus 1 shootout goal).
   Suggest: "Goals in the table leave out empty-net and shootout goals."
6. Window choice: the "last 4 games" split starts at the beginning of the hot streak (SPLIT hard-coded to 2026-11-19), so "paid back"
   partly reflects choosing the window afterward. Fine to describe the run. Just don't make anything of how big the gap closure is.
   For context, the run isn't unusual: 18 non-empty-net goals in a 4-game span has been done by 19 teams this season, and Buffalo's
   +7.6 over chances is 7th among teams' best 4-game spans this season. Don't call it rare.
7. Chance-share rank 22nd is right but fragile: BUF 0.4792, ANA 0.4788 (23rd).
8. Typed literals in the generator ("four games", "lone goal", `x_n - 1`, "Season (25 games)", "Korpisalo GSAx", "Wednesday").
   All are guarded by asserts (l['n']==4, the 5-1 score, k_games==3, Korpisalo name), so none is wrong now. Prefer variables.

## Verified (independent derivation from raw_nhl_games, raw_nhl_plays, clean_nhl_shots_xg, ledger CSVs)

- Pin: all 399 regular-season 2026-27 games through 2026-11-25 are in the feed, all OFF; ids 1-399 contiguous. No NOT_IN_FEED entry is
  needed for 11-25. Rescale = 2370 goals / 2366.73 xG = 1.0014 ("1.001"), games through AS_OF only.
- Clean reproduction (git archive HEAD, data symlinked, generator re-run): md, hero JSON and PNG are byte-identical.
- Game: BUF 5-1 REG, Wednesday. Shots on goal 30-30 from raw plays (25+5 and 29+1; the feed's running SOG counter leaves out goals).
  Chances worth BUF 2.47, NYR 2.35. Goals in order: Dahlin, Norris, Benson (BUF); Gavrikov (NYR, 56 ft, 0.023); Quinn, Kulich. No empty-net goals.
  Goalies in net (goalieInNetId): Korpisalo for all 5 BUF goals and 41 unblocked BUF shots; Luukkonen for all 42 NYR shots,
  2.35 - 1 = 1.35 ("about 1.3"). Closest BUF goal Norris 13.5 ft, 0.124 ("13 feet", "about 12%").
- Korpisalo before: 3 games (Nov. 7, 11, 16), 7.79 xGA vs 5 GA = +2.79. On the night 2.47 - 5 = -2.53.
- Season split: first 21 games 57 GF on 64.09, 72 GA on 68.64. Last 4: 3-1, 20 GF (18 non-EN, 2 EN on Nov. 19 and 22) on 10.44,
  10 GA on 12.34. Season finishing +0.47, goaltending -1.02. Record 11-10-4.
- Ranks (games through 11-25): BUF chance share 0.479, 22nd; finishing +0.019/gp, 15th; saves -0.041/gp, 18th. NYR finishing 30th
  (also 30th in the preview).
- Tampa recap supports "chances carry over far better than either" (r 0.77 vs 0.10 and 0.22). Note that goaltending "partly" carries over,
  so "come and go" is slightly strong for goaltending but acceptable.
- Ledger: P0023 logged 2026-11-25T14:42:57Z, before the 2026-11-26T00:00Z puck drop. p 0.49, outcome 1, Brier 0.2601. 22 graded,
  13 with the side above 50% winning, none at exactly 0.5. Consistent with the Tampa recap's 13 of 21. The grader only reads raw_nhl_games.
- Shot model description (distance, angle, shot type, rebound, rush) matches FEATURES in src/metrics/nhl_xg.py (which also has strength).
- Chart opened: numbers (-7.9, -5.3, +0.5, -1.0, 18 on 10.4) match. Footer has source, empty-net exclusion and date. Sample size (25 games) is in the subtitle.
- No betting language. No stat jargon in the body; stat terms are only in "For the stat-heads".
