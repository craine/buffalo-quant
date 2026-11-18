# Quant review (stage 2, round 3): 2026-11-18-sabres-then-now

Reviewed text SHA-256 `6bd9fe6560f4448ff8ebf1a99cdd6a36889628b16083f98278d4c4acc054ceae` (generator `src/reports/sabres_then_now.py`, AS_OF 2026-11-17).
I computed every number myself with SQL and pandas on `raw_nhl_*` and `clean_nhl_shots_xg`, using my own per-season rescale (scripts in /tmp/qa2). Goal totals and empty-net goals come straight from the `raw_nhl_plays` goal events. I did not call the writer's functions.

## Verdict: pass (publish; three optional wording fixes below)

Every round-2 finding is fixed. The new numbers all reproduce, and nothing I found is a factual error. Re-running the generator in a clean copy reproduces all five output files byte for byte. The items below are wording. If any of them is applied, the stage-4 final check covers it.

## Remaining findings (optional, ranked)

**1. The header for section 1 is no longer supported in its own paragraph.**
Text: "**1. They give up more chances, and the penalty kill is the worst of it.**" The paragraph that follows never mentions the penalty kill. The sentence "Shorthanded, it allows the 4th-most" was removed. The claim is true: the opponent power play is the biggest piece of both gaps, +2.69 of the +7.45 rise since last year and +0.133 of the +0.271 gap to league average. But a reader only finds the support two sections later.
Fix: put back one sentence after the five-on-five line: "A man down, it allows the 4th-most."

**2. "Mostly bounces, both years" calls goaltending luck.**
Text: "**3. Power-play goals against: mostly bounces, both years.**"
Evidence: of the jump from 7 to 21 power-play goals, chances account for about 2.7 goals (14.0 → 16.7). The other ~11 is goals against chances: −7.0 last year and +4.3 this year. Some of that is the goalies (Luukkonen −3.3 overall this season), and our own mirage study measured that as only weakly carrying over, not as pure luck. The body says it more carefully ("Most of the jump in goals is how many have gone in").
Fix: "**3. Power-play goals against: mostly how many went in, both years.**"

**3. Two small assertions no code backs.**
- "Over a month, finishing is mostly luck." The window is 21 games, about six weeks. The cold-shooter study shows players coming back to average, but players with hot starts (+4 or more, n=42) kept finishing at 1.12 times their chances afterward (my query), so "mostly luck" is a little strong. Fix: "Over a few weeks, finishing swings a lot."
- "That's a coaching and personnel job as much as a roster one." This is opinion with no data behind it, and "personnel" and "roster" mean nearly the same thing. Fix: cut it, or say "That's a coaching job as much as a roster one."

## Round-2 findings: status

1. Player goals leaving out empty-net goals: **fixed.** Benson: "1 goal with a goalie in net (2 counting an empty-netter)", and "10 … in each of the last three seasons (11, 10 and 13 counting empty nets)". Tuch: "32 … (33 in all)" and "11 … (12 in all)". All match the raw goal events.
2. "Mostly on the penalty kill": **fixed** ("the worst of it", which is true; see #1 above for where the support sits).
3. Tuch and "rare": **fixed.** It now reads "the year before he missed by a fraction of a goal" (−0.14), "about 13 more than luck alone would produce" and "about 1 in 4".
4. "Fix the penalty kill": **fixed.** It's now "Cut the chances allowed a man down", "If this pace held", "fewer, and less dangerous, shots", with the note about penalty data kept.
5. Goalies: **fixed** ("Luukkonen is 3.3 … the other two are about average").
6. Cold shooters: **fixed** ("though not quite their usual form").
7. Points-chart label: **fixed.** It no longer overlaps the line. "how much the numbers can tell us about each move" replaces "what each move is worth".

## New numbers verified (independently)

- Opponent power play (5v4, 5v3, 4v3), first 21 games. 2025-26: 164 shots, chances worth 13.977, 7 goals, 0.0852 per shot. 2026-27: 150 shots, 16.665, 21 goals, 0.1111 per shot. Ratio 1.303, so "about 30% more dangerous" ✓. That comparison is with last year; the league average this season is 0.104 a shot.
- Gap to league average in chances allowed per game, by game state: penalty kill +0.133, overtime 3v3 +0.062 (next-biggest ✓), 6v5 +0.030, five-on-five +0.020 ("almost none of it" ✓). 1 / 0.133 = 7.5 games, so "an extra goal's worth of chances about every 8 games" ✓ (it's 7.5, which rounds either way). Half the gap is 0.49 ✓. Over 61 games, 8.1 ✓.
- Shots a man down: BUF 7.14 a game, league 6.35 ✓.
- Three-season finishers: 197 eligible, 46 steady. Shares beating their chances by season: 0.553, 0.563 and 0.533. The baseline 197 × 0.553 × 0.563 × 0.533 = 32.7 ✓, so 46 − 32.7 = 13.3 ("about 13 more") ✓. The binomial SD is 5.2, so the excess is about 2.5 SD and "finishing is real" holds. The baseline assumes seasons are independent, which is the right null to test against.
- Goalies: Lyon −0.45 (3 games), Ellis −0.65 (8), Luukkonen −3.32 (12); combined −4.42 ✓. Last year's run: 23.25 of 36.29 from goalies, so "about 23 of the 36" ✓.
- Earlier numbers in the text, unchanged and rechecked: table 66/58 scored and 74/73 allowed, empty-net goals against 8 vs 1, "+6 with a goalie in net", 3.22 a game (6th-most), 2.04 vs 2.02, 14th in chances created, tied for 3rd in power-play goals allowed per game, 61-game split, Luukkonen, Tuch and Benson.
- Hero JSON: "(last year's was unusually low)" matches the body (7 on chances worth 14.0, about half). Site card "sabres-same-start": 8-9-4 twice, "won 50", 21 vs 7 ✓.
- Brand: no betting language (grep plus a read-through). No stat jargon in the body; stat terms appear only under "For the stat-heads". The small sample is labeled. The new headline "how we'd fix it" is matched by a hedged GM section.
- Charts: I opened the points and GM charts. Labels are clean and the values and ranks match. The compare chart is byte-identical to the one I reviewed in round 2.
- Reproduction: re-running the generator in a clean copy (/tmp/qa2/copy3) reproduces the markdown, hero JSON and all three PNGs byte for byte.
