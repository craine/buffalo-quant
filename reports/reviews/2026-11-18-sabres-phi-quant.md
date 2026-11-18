# Quant review: 2026-11-18-sabres-phi.md (Flyers 4, Sabres 3)

Reviewed text sha256 1134ef81... (generator `src/reports/sabres_postgame_phi.py`, AS_OF 2026-11-17).

**Verdict: publish with fixes.** All 60+ numbers re-derive independently and the generator reproduces the md, hero JSON and both
PNGs byte-for-byte. Two claims go further than the numbers support (one is contradicted by them). Fix those before the final check.

## Required fixes

1. **"The finishing came back; the chances it allowed are what cost it."** (What we said to watch)
   - Problem: the story's own numbers contradict the second half. Philadelphia's chances beat Buffalo's by 0.59 goals
     (2.78 vs 2.19), but Lyon allowed 1.22 more than an average goalie. By the story's own framing, goaltending cost more than
     the chances did. Before the winner, chances were close to even: PHI 2.00 (1.35 through two plus 0.66 in the 3rd), BUF 1.88.
     "Came back" is also a trend claim from one game: Buffalo scored 3 on 2.19, +0.8 in one game.
   - Fix: "Tonight Buffalo scored 3 on chances worth 2.2, a bit better than its chances for once (one game). The goals it
     allowed were the bigger problem: Philadelphia's chances were worth 0.6 more than Buffalo's, and Lyon allowed 1.2 more
     than an average goalie would have." (Add before-winner xG, 2.0 vs 1.9, to the generator if you want to use it.)

2. **"The chances against are the thing to fix. Philadelphia came in creating the 5th-fewest chances in the league and still
   had more than Buffalo tonight, mostly on the power play and in the third."** (What it means for Buffalo)
   - Problem: this is advice based on one game, and the game doesn't support it. At five-on-five Buffalo had more chances
     than it gave up (1.72 vs 1.55, 53%). PHI's third-period edge came mostly after the winner (14 shots worth 0.78, 7 of them
     on the power play worth 0.40), while PHI was leading. Power-play chances depend on penalties, and we don't publish penalty
     counts. A season-level case does exist: the pregame story had Buffalo allowing 3.25 a game, 27th. But this story doesn't
     compute or cite that number.
   - Fix: describe the game instead of telling the team what to fix: "**Even at five-on-five, beaten on the power play.**
     Philadelphia came in creating the 5th-fewest chances in the league. Tonight it out-chanced Buffalo only on the power
     play (0.9 to 0.3)." If you want the season point, compute Buffalo's chances allowed through AS_OF in the generator and
     cite it.

## Recommended (minor)

3. **"the kind that goes in about 2% of the time"** (lead, site card, hero) versus **"0.9% of them have"** (The winner). Both are
   right but answer different questions, and a reader sees a contradiction. Shots rated 1.5-2.5% went in 2.2% of the time this
   season (3,275 shots) and 1.8% across all seasons (44,255). So "about 2% of the time" is accurate for shots like the winner.
   The 0.9% covers every shot rated at or below 2%. Fix: in The winner, say "shots rated that low or lower ... 0.9% of them
   have gone in, because most are even worse looks." The Editor also asked why a 30-foot shot rated 2% when a 27-foot shot
   rated 16%: the winner came from a sharp angle (60 degrees off the middle of the net, y = -26 ft). Thompson's goal came from
   6 degrees. Compute that in the generator and add one sentence.
4. **"What we said to watch"** lists "Finishing", but the pregame's "What to watch" had only the Flyers' starter and their
   recent games. The finishing point came from "The skid isn't what it looks like". Fix: rename the section "What we said going
   in", or label the bullet "Our pregame point on the skid".
5. **"long shot"** (headline, chart title, "One goal from a long shot decided it"). It's a common idiom and also describes
   distance, but it's also betting vocabulary. Safer: "a low-percentage shot" or "a sharp-angle shot".
6. **"The model expected about 3.2 goals ... The chances came out lower on both sides: 2.8 and 2.2."** The model's 3.17/3.23
   are expected goals from its goals regression on unrescaled xG, and 2.8/2.2 are rescaled chances. That's close enough for
   fans, and the stat-heads line covers it. If you keep the line, also give actual goals (4 and 3) so it doesn't read as if
   the game came in under the model.
7. **Generator:** the "each team took the lead" expression falls back to a literal "?" when the counts differ. It's correct
   tonight (2 and 2) but brittle. Fix: assert the counts are equal, or write both counts out.

Optional: "So the Flyers deserved the edge, just not by much" is supported (replays: PHI 51.3%, BUF 30.1%, tie 18.6%). It's
fine as written.

## Verified independently (own queries on raw_nhl_plays / raw_nhl_games / raw_nhl_schedule / clean_nhl_shots_xg; own rescale)

- Final PHI 4, BUF 3, REG, state OFF. The goal sequence from raw plays matches the table exactly: Samuelsson 1st 0:47 (snap,
  Woll), Drysdale 2nd 6:39, Thompson 2nd 10:59, Tippett 2nd 14:30 (tip-in), Sanheim 3rd 0:29 (situationCode 1441 = 4v4),
  Kulich 3rd 4:31 (timeRemaining 15:29), Dvorak 3rd 5:23 (wrist, Lyon in net). The gap is 52 s. Ties after goals: 3. Lead
  changes: BUF took the lead 2 times, PHI 2 times.
- Raw unblocked attempts: BUF 34 (16 SOG + 3 G + 15 missed), PHI 46 = 44 non-empty-net + 2 empty-net (both 5v6, at 58:20
  and 58:42, missed, 0 goals). On goal: BUF 19 (all on Woll), PHI 33 (all on Lyon).
- Rescale factor 2026-27: 0.9859 (0.986). xG: BUF 2.192, PHI 2.784. By period BUF 0.606/1.118/0.469 (13/11/10 shots), PHI
  0.629/0.717/1.437 (10/11/23). Through two periods 1.72 vs 1.35. PHI share of the 3rd 75.4%.
- After the winner in the 3rd: PHI 14 shots, 0.780 (power play 7, 0.404); BUF 7, 0.310. Before the winner in the 3rd: PHI 9, 0.657;
  BUF 3, 0.159.
- By strength: BUF 5v5 1.722 (28), 5v4 0.317 (3), other 0.153 (3: 4v4 1, 6v5 2). PHI 5v5 1.553 (29), 5v4 0.859 (12), other 0.372
  (3: 4v4 2, 4v5 1). BUF 5v5 share 0.526. Hero bars -0.17 and +0.54, which round to -0.2 and 0.5.
- Chance per goal: 4.0%, 12.4%, 16.0%, 9.1%, 9.8%, 13.2%, 1.89%. Distances 24.7, 26.9, 27.2, 13.0, 24.2, 28.3, 30.0 ft.
- Rarity: 28,106 unblocked non-empty-net shots in 2026-27 through Nov 17. 7,060 (25.1%) were rated at or below 0.0189, and 67 of
  those went in (0.95%).
- Replays: Monte Carlo (400k runs, a different method from the generator's exact convolution) gives BUF win 0.301, tie 0.186,
  loss 0.513. That matches 30/19/51.
- Goalies: Lyon faced 44 shots (33 on goal), 2.784 xG, 4 GA, -1.22. The winner was the lowest-rated of his 4 goals (0.019 vs
  0.091, 0.098, 0.124). This season Lyon has 3 games, -0.45 (+0.77 through Nov 15). Woll faced 34 (19 on goal), 2.192, 3 GA,
  -0.81. Woll through Nov 15: +4.41 on today's rescale and +4.50 on the Nov 15 rescale (factor 0.9882), so the published +4.5 and
  the rescale note are correct. Woll is better than Vladar (-3.5) per the pregame table.
- Pregame comparisons: the 4 skid losses before tonight (Nov 8 VGK, Nov 11 TBL, Nov 12 at CHI OT, Nov 14 at DAL) gave 6 goals on
  12.08. PHI share in its 5 games through Nov 15: 0.566. Tonight 0.559. PHI xG created per game through Nov 15 ranks 5th-fewest
  (2.671; CHI, VAN, CGY, SEA lower).
- Record: 21 games, 8-9-4. Skid is 5 straight, with one OT loss (Nov 12). Schedule: at WSH Thu Nov 19, at FLA Nov 21, at TBL
  Nov 22, home vs NYR Nov 25.
- Ledger: P0018 was logged 2026-11-17T18:41:38Z, before puck drop at 00:00Z. p = 0.48, wording matches the pregame story,
  model nhl-game-v0.1, notes 3.17/3.23. Graded outcome 0, Brier 0.2304 (= 0.48 squared). Record: 18 predictions, 17 graded,
  11 of 17 right (no 0.5 calls), and NHL 4 of 5 (P0001, P0009, P0011, P0018 right; P0010 wrong). P0017 is not yet graded.
- Site card text, hero JSON and chart titles/subtitles/footers match the body numbers. Both charts viewed: the flow chart's
  winner annotation points to the right dot (PHI running total 2.00). The situations chart labels match the text. Footers carry
  the source and shot counts.
- Jargon: none in the body (xG, GSAx, Poisson and Brier appear only in "For the stat-heads"). Betting language: no odds, lines
  or picks. "Long shot" is borderline (item 5).
- Reproducibility: re-ran the generator; the md, hero JSON and both PNGs are byte-identical to the committed files.
