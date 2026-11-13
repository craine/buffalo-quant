# Editor review: 2026-11-13-sabres-chi.md (Blackhawks 3, Sabres 2, OT)

**One-sentence version (radio):** "Buffalo outplayed Chicago for two periods, then sat back on a 2-1 lead in the third, got a quarter of the chances while a team up a goal usually gets about 42%, and lost in overtime."

**Verdict: needs edits (FAIL until fixes 1-4 are in).** The lead is right, the headline works, the third-period comparison (25% vs. 42%) is a great radio number, and both charts read in five seconds. Four problems: the story never explains how "chances" are measured (standing rule), the back-to-back follow-up overclaims "not tired legs" and skips the goalie connection the pregame set up, the whole-game paragraph contradicts itself (Chicago had more chances but Buffalo wins more replays), and "did what the numbers said they should" conflicts with the model numbers later in the story.

## Required edits, most important first

### 1. Add the "how we measure chances" explanation (standing rule: show the reasoning every time)
Both earlier Sabres stories have it. This one has none, though "chances" carries every headline number. Insert after the scorer table and before "Over the whole game it was close to even":

> ## How we measure "chances"
>
> Every shot has a chance of going in, based on where it was taken and what kind of shot it was. Add those up and you get what a team's chances were worth in goals. Thursday shows the range: Frank Nazar's first goal, from 5 feet on the power play, had a 23% chance of going in; Tage Thompson's power-play goal from 29 feet had 7%. Add up all 31 of Chicago's shots that weren't blocked and they were worth 2.3 goals. Chicago scored 3. The shot locations come from the NHL's own play-by-play. (The full explanation, and how we tested it, is in our story on [last year's 50-win season](sabres-50-win-mirage.html).)

All numbers are already in the story (scorer table, game table). No new computation.

### 2. Make the back-to-back follow-up honest (story body, dek, hero card)
The pregame said tired road teams *win* less often, that the model misses it, and that **the drop doesn't show up in chances** ("Tired road teams still got about 47% of the chances... Where the drop comes from is less clear"). So "chances by period don't fade late" can't rule out tiredness; it only rules out one version of it (running out of gas in the third). The pregame also pointed at goalies (usual starter in net only 37% of the time on tired nights), and that's exactly what happened: Buffalo's third goalie, first game of the season. The wrap should say so.

- Replace `The easy story is that Buffalo ran out of gas on the second night of a back-to-back. The numbers don't back that up.`
  with `The easy story is that Buffalo ran out of gas on the second night of a back-to-back. The third period doesn't look like that.`
- Replace `The score explains Thursday's third period better than the schedule does.`
  with `The score explains Thursday's third period better than the schedule does. That doesn't mean the back-to-back didn't matter. Our pregame story found that tired road teams lose more often without falling much behind in chances, and we still don't know why. One thing it did flag: tired teams often play a backup in goal. Buffalo did.`
- In "In goal", replace `Alex Lyon started for Buffalo after both of the Sabres' regular goalies played in Wednesday's 8-3 loss to Tampa Bay.`
  with `Alex Lyon started for Buffalo after both of the Sabres' regular goalies played in Wednesday's 8-3 loss to Tampa Bay. That's the back-to-back at work: in our pregame look, tired road teams had their usual starter in net only 37% of the time.` (37% is from the pregame; Quant to confirm it's fine to repeat.)
- Dek (`src/site/build.py`, slug sabres-blackhawks-postgame-nov-12): replace `It wasn't the usual tired-legs pattern.`
  with `It didn't look like the usual back-to-back pattern, which shows up early, not late.`
- Hero card `explainer.kicker`: replace `"Not the legs"` with `"Not a late fade"`.
- Hero card bars only show the 1st period, so the title "trail most early, not late" can't be read from them. Replace the explainer `text` and `bars` with
  `"text": "Tired road teams' share of the chances, since 2023-24:"`, bars `["1st period", 0.457]`, `["3rd period", 0.482]`. (Both numbers are in the stat-heads section.)

### 3. Fix the whole-game paragraph (reads as a contradiction)
Replace `Over the whole game it was close to even: Buffalo's chances were worth 2.1 goals, Chicago's 2.3. Replay the 60 minutes over and over,`
with `Over the whole game it was close to even: Buffalo's chances were worth 2.1 goals, Chicago's 2.3, but Chicago's last 0.4 came in overtime. Over the 60 minutes of regulation, Buffalo had the edge. Replay those 60 minutes over and over,`
A fan sees "Chicago had more chances" followed by "Buffalo wins 44%, Chicago 35%" and thinks it's a mistake. The overtime 0.37 is in the period table; the writer should state the regulation totals (needs a computed number, about 2.1 to 1.9; writer computes, don't hand-add rounded table values).

### 4. Fix a claim that conflicts with the story's own numbers
"What it means" says `For two periods they did what the numbers said they should against the league's weakest team at creating chances.` But Receipts says the model expected 3.45 goals' worth of chances for Buffalo and the game came in at 2.1. Buffalo won the share but created far less than expected.
Replace with `For two periods they had the better of the team that creates the fewest chances in the league, as expected, though both teams created less than our model thought.`
And give the Receipts sentence a "so what": replace `the game came in well below both, at 2.1 and 2.3.` with `the game came in well below both, at 2.1 and 2.3: a low-chance game, which is part of why one tip-in and one overtime shot could decide it.`

## Should-fix

5. **Follow up the pregame's "what to watch."** The pregame said: "The first period... If Buffalo's legs are there early, the Sabres should be the team with the puck." They were (67% of first-period chances). That's a satisfying receipt. Add to "Was it tired legs?" after `Buffalo did the opposite: 67% of the chances in the first, 36% in the third.`: `Our pregame said to watch the first period for tired legs. They weren't there.`
6. **Shorten the lead.** Five sentences in bold is a lot. Replace `The Sabres had the better of Chicago for 40 minutes: their chances were worth 1.5 goals to Chicago's 0.8, and they led 2-1 going into the third. Then Chicago took over.` with `The Sabres had the better of Chicago for 40 minutes, with chances worth 1.5 goals to Chicago's 0.8, and led 2-1. Then they sat on the lead.` (Drop "Finding:" label? Keep for consistency with the TBL wrap; Charlie's call.)
7. **Two-decimal numbers look like stats.** The period table (0.77, 0.38...), "worth 0.23 goals ... 0.69", and "(0.36 to 0.35)" read like a spreadsheet. Suggest one decimal in the body (0.8, 0.4, ...; "0.2 goals ... 0.7"), as the TBL wrap does; keep two decimals in stat-heads. Writer reruns so rounding comes from code. "0.36 to 0.35" can simply become "about even".
8. **"Scored the usual way (the gap between our chance and what happened, squared; lower is better), it comes to 0.32"** is fine and matches the prior wrap. Keep.

## Charts

- **Flow chart:** reads in five seconds, title is the takeaway, shaded "3rd, Sabres up 2-1" band is excellent. One fix: Sabres goals are *red* dots while the Blackhawks line is dark red, so a fan links red dots to Chicago. Make Sabres goal dots blue (match the Sabres line) and Chicago's black, and change the subtitle to "Dots = goals, in each team's color."
- **Periods chart:** title is the takeaway and works. Minor: Buffalo is red and "tired road teams" is Bills/Sabres blue; swap so the Sabres bar is blue and tired road teams another color (e.g. dark gray), since fans read blue as Buffalo. If fix 2 is applied, consider softening the title to "Tired road teams don't fade late. Buffalo did" (same meaning, matches the new body).

## Fine as is
Headline; scorer table (great plain "chance it went in" column); "It's 11 shots in about eight minutes, so it's one stretch of one game, not a trend"; goalie section length; Receipts owning the miss and not hiding behind the back-to-back warning ("the 57% is what we logged and what gets graded"). No jargon in the body; "3-on-3", "power play", "tip-in" are fine for hockey readers. Length is right.
