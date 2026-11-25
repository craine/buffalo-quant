# Editor review (stage 3): 2026-11-25-sabres-nyr-pregame

**One-sentence version (radio):** "The Rangers miss more of their chances than almost anybody, and over the last three seasons that
hasn't lasted, so expect them to start scoring. Tonight's close to a coin flip: our model has the Sabres at 49%."

**Verdict: needs edits.** The angle is fresh and not a template preview. It's built on one idea (bad shooting comes back, hot goalies
cool off), and the chart, hero, card and headline all point at it. Three things need fixing before stage 4: the lead promises more
than the data supports, the opening sentence stacks numbers inside parentheses, and the story skips the required real-number example
of how a chance gets its value. None of Charlie's rejected phrases appear ("lopsided", "the home kind", "go the other way", "in reverse",
"good end/bad end").

## Must-fix (most important first)

1. **The lead overclaims (agrees with Quant #1).** The Rangers' missed finishing (about 8 goals) and their goalies' saves (about 7)
   nearly cancel, so "better than their goal totals look" and "a better team than its record" go too far. A host who repeats them will
   get pushback. The honest version is still a good angle: they'll score more.
   - "Over the last three seasons, bad finishing hasn't lasted, so the Rangers are probably better than their goal totals look."
     -> "Over the last three seasons, bad finishing hasn't lasted, so the Rangers should score more than they have. Their goaltending
     will probably cool off some too."
   - "If the Rangers follow that pattern, their shooting comes around and their goaltending stays good, just not this good. Over a
     season, that's a better team than its record."
     -> "If the Rangers follow that pattern, their shooting comes around and their goaltending stays good, just not this good. Right
     now the two nearly cancel out: about 8 goals missed, about 7 saved. Finishing is what tends to bounce back, so the bigger change
     from here is more Rangers goals."
2. **The first sentence stacks four numbers in a parenthesis.** It can't be read on air, and "more of the chances than Buffalo does"
   sounds like a head-to-head number.
   - "The Rangers get more of the chances than Buffalo does (52.7% of them, 9th in the NHL, against Buffalo's 47.8%, 22nd). What they
     don't do is finish:"
     -> "The Rangers get 53% of the chances in their games, 9th in the NHL. Buffalo gets 48%, 22nd. What the Rangers don't do is finish:"
     (formatting change only: `{n.share:.0%}` / `{b.share:.0%}`. The decimals stay in stat-heads.)
   - Site card: "The Rangers get more of the chances than Buffalo but finish them worse than all but two teams. Their goalies have covered
     for it. Our model: Sabres 49%."
     -> "The Rangers get more of the chances in their games than Buffalo does, but only two teams finish them worse. Their goalies have
     covered for it. Our model: Sabres 49%."
3. **No real example of how a chance gets its value (standing rule: "Every story explains where its key number comes from ... with
   real computed examples").** "Every shot has a chance of going in, based on where it was taken..." explains the idea but gives no
   number a fan can hold on to. Add one sentence after "...rebounds and power plays." **New numbers: the writer must compute them in the
   generator.** For reference, my check on this season's unblocked, non-empty-net shots: within 10 feet 13.5% of 4,500 shots; 40 feet or
   more 2.2% of 10,911.
   -> "This season, a shot from within 10 feet has gone in about 14% of the time; one from 40 feet or more, about 2%."

## Optional polish

- Saves rank (Quant #2): "(6th)" -> "(6th per game)".
- "In the second half, 2 below." -> "In the second half, about 2 below." The value is -1.7.
- Model paragraph: tie it to the angle. "It doesn't count finishing or goaltending." -> "It doesn't count finishing or goaltending, so it
  already treats the Rangers as average shooters with average goalies."
- Hero second line: "where the Rangers rank in finishing their chances, of 32" -> "the Rangers' rank in finishing their chances, out
  of 32 teams". It reads better when it stands alone.
- Chart corner labels: "Both" -> "Finish well,\ngoalies stop more"; "Neither" -> "Don't finish,\nweak goaltending". "Both" and "Neither"
  only make sense after you work out the other two corners. Also, the Rangers and Sabres markers are nearly the same blue. The
  hollow-vs-filled markers and the labels carry it, so this is minor.
- Stat-heads disclosure for player goals including empty nets (Quant #3).

## What works

- The headline, hero ("30th", 49%), card, chart title and body all tell the same story.
- Plain English throughout the body. No xG, GSAx or PDO outside stat-heads. "Save %" in the table is fine for hockey fans.
- The chart reads on its own in five seconds: title is the takeaway, corner labels explain the axes, and the Rangers sit alone in the
  top-left. The footer has source and sample size.
- The "what lasts" section reuses the Nov 22 recap's method and links to it. That's the "how we checked it" for the main claim, and it's
  the right length.
- "It won't necessarily show up in one game" is the right hedge for a single-game preview.
- Ledger paragraph wording matches the logger (Sabres 49%, any result counts).
