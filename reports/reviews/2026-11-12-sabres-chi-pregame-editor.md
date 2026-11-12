# Editor review: 2026-11-12-sabres-chi-pregame.md

Stage 3 (Editor). Reviewer: independent editor agent. Inputs: story body, hero JSON, build.py dek, three charts,
compared against 2026-11-11-sabres-tbl-pregame.md. No numbers or claims changed; all edits reuse numbers already in the story.

## One-sentence version (radio)

"Chicago is the worst team in hockey at creating chances, but the Sabres are on the second night of a back-to-back,
and tired road teams like that have won only 38% of the time, so our 57% for Buffalo is probably too high."

That sentence is in the story, but split between the lead's first and last clauses and the "closer to a coin flip" line
at the bottom of the prediction section. The lead needs to say it in order.

## Verdict: needs edits (FAIL until the required fixes are in)

The story is in good shape and the back-to-back angle is a real "so what" a fan will repeat. Structure follows the
TBL pregame well. The back-to-back section is honest about what we know (it happens, every season) vs. what we don't
(why). Body is mostly jargon-free. Fixes below are about the lead, one backward bullet, one self-contradiction, and
the hero card.

## Required fixes (most important first)

### 1. Lead (generator line ~276-277)
Problems: "leans Buffalo" is betting-desk language ("a lean" is a soft pick); the last clause ("won 38% of the time when
our model gave them 46%") is hard to say out loud and comes after a 40-word run-up.

Replace:
> **Our model leans Buffalo in Chicago: Sabres 57%, Blackhawks 43%. Chicago creates the fewest chances in the league and allows the 2nd-most. But the model doesn't know the Sabres played last night, and that matters: last season and this one, road teams playing a second straight night against a rested home team won 38% of the time when our model gave them 46%.**

With:
> **Chicago creates the fewest chances in the NHL and allows the 2nd-most, and our model gives the Sabres a 57% chance to win (Blackhawks 43%). But Buffalo played last night, and the model doesn't know that. Road teams on the second night of a back-to-back against a rested home team have won only 38% of the time, even though our model gave them 46%. Read our 57% as too high.**

### 2. "Results vs. chances" bullet is backward (generator ~line 374-375)
It says results that "run ahead of the chances tend to fade", but Buffalo's results are running *behind* its chances
(scoring 2.94 on chances worth 3.13; allowing 3.61 on 3.29, per the table), and 2-3-0 with 48% of the chances isn't
"ahead" either. A fan will be confused about which way this cuts.

Replace:
> - **Results vs. chances.** Buffalo is 2-3-0 in its last 5 games with 48% of the chances in them. Five games is a small sample, but over a full season, results that run ahead of the chances tend to fade (see our [50-win story](sabres-50-win-mirage.html)).

With:
> - **Results vs. chances.** Buffalo's results have run a little behind its chances: 2.94 goals a game on chances worth 3.13, and 3.61 allowed on chances worth 3.29. Over a full season, gaps like that tend to close (see our [50-win story](sabres-50-win-mirage.html)).

(Quant to confirm "tend to close" applies in this direction; the 50-win story was about results running ahead.)

### 3. "That's the number we've logged" contradicts the unlogged state (generator line 348)
Line 75 says the call "counts once it's logged"; line 78 says "That's the number we've logged". As published right now
both can't be true. Make line 348 conditional the same way line 127 is, or:

Replace:
> That's the number we've logged, because it's the model we've tested.

With:
> That's the number we log, because it's the model we've tested.

And make sure the final text carries the logged timestamp line (as the TBL pregame did) before stage 4.

### 4. Hero card mismatch (hero.json, generator ~line 399)
- The explainer's title and text are about shot chances ("Every shot has a chance of going in... 13.8%"), but its bars are
  tired vs. rested road teams (38% / 47%). A fan sees a shot-distance explanation sitting on a back-to-back chart.
  Either change the bars to the shot-distance numbers (13.8% within 10 ft vs. 0.8% from 60+, already in the story), or
  change the text to match the bars:
  - title: "Tired legs cost road teams."
  - text: "Since 2023-24, road teams playing the second night in a row against a rested home team won 38% of 643 games. Rested road teams won 47%."
- Two different 38%s: the big number ("when our model gave them 46%", last season and this one, 242 games) and the note
  ("since 2023-24", 643 games) are different samples that happen to round alike. Fine for the reader as long as each is
  labeled; keep the big-number label as is and the note as is, but don't merge them anywhere.

### 5. "2.6 times what chance alone would usually produce" (generator, back-to-back section)
Reads like a stat; a fan can't tell 2.6 times *what*. The stat-heads section already has the standard error.

Replace:
> A gap that size over 242 games is about 2.6 times what chance alone would usually produce.

With:
> Over 242 games, a gap that size is too big to write off as a few bad bounces.

### 6. Decimals that look like stats (back-to-back section)
Replace:
> Tired road teams still got 46.9% of the chances in those games, only a little below the 48.3% for rested road teams.

With:
> Tired road teams still got about 47% of the chances in those games, barely below the 48% for rested road teams.

### 7. Orphan Buffalo facts (end of "less clear" paragraph and the one-line paragraph after it)
"Buffalo's only other second night this season..." is tacked onto a paragraph about goalies, and "Both Sabres goalies
played in last night's loss." stands alone with no "so what". Pull them together as the Buffalo tie-in:

Replace:
> ...Neither explains the whole gap. What we can say is how often it's happened. Buffalo's only other second night this season was Oct. 13 at Montreal, a 4-3 loss.
>
> Both Sabres goalies played in last night's loss.

With:
> ...Neither explains the whole gap. What we can say is how often it's happened.
>
> **For Buffalo tonight:** its only other second night this season was Oct. 13 at Montreal, a 4-3 loss. And both Sabres goalies played in last night's loss, so neither comes in fully rested.

(Quant: "neither comes in fully rested" is an inference from both having played; drop the clause if not acceptable.)

### 8. Two league averages (prediction section)
The table says league average chances are 2.97 a game; the prediction section says "against a league average of 3.00".
A careful fan will think one is a typo. Add a few words, or have the writer explain which average the model uses:

Replace:
> against a league average of 3.00.

With:
> against the model's league average of 3.00 (it blends in last season too, which is why it's a bit above this season's 2.97).

(Writer/Quant must confirm that's the reason before using this wording.)

## Suggested (not required)

- Model-test chart legend and labels use "favorite" ("Favorite given 55-60%"). Not a betting usage here, but our
  self-check lists "favorites" as a word to avoid. Suggest "Team the model liked" / "Model's pick given 55-60%" ...
  better: "Likelier team given 55-60%" and legend "What the model said (likelier team's chance)".
- "336,462 shots that reached the net or missed it" -> "336,462 shots that weren't blocked" (clearer).
- Chances chart: title is the takeaway and readable in five seconds. Back-to-back chart: excellent, title is the story.
  Model-test chart: fine.
- Dek in build.py is good; no change.
- Length is fine. The "Where the number comes from" paragraph is the densest part; acceptable since it mirrors the TBL pregame.

## Checks
- Betting language: only "leans" (fix 1) and chart "favorite" (suggested). No odds/lines/picks.
- Jargon in body: none of xG/GSAx/PDO in body; stat terms confined to "For the stat-heads". Good.
- Explaining the data: shot example (13.8% / 0.8%), source, math, check all present; tied back to 3.13 / 3.42. Good.
- Back-to-back: clearly separates what we know (rate, every season, model misses it) from what we don't (why). Good.
