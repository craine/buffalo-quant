# Editor review: 2026-11-22-sabres-tbl-postgame (stage 3, round 1)

Reviewed: md (sha256 8609fa8f...22bb), hero JSON, card dek in src/site/build.py, flow PNG (opened).

**Verdict: needs edits (fail).** Good angle, and headline, lead, hero and card agree: Tampa Bay had more chances, Buffalo finished them,
6-2, 35% call is a miss. Four lines need fixing.

## Must fix

1. **Key 2 paragraph contradicts the "Half" grade** (also Quant must-fix 1). Table says Half; the next line says "teams that hit all
   three". The sentence also stacks three clauses.
   - Current: `Since 2023-24, teams that allowed one power-play goal at most and scored first, but had fewer of the five-on-five chances, won 60% of the time (1,856 games).`
     `Teams that hit all three won 78%. Buffalo scored first for the 14th time this season and has won 6 of those games.`
   - Replace: `Since 2023-24, teams in Buffalo's spot won 42% of the time (1,286 games). They allowed one power-play goal at most, scored first but saw the other team tie it, and had fewer of the five-on-five chances.`
     `Buffalo has scored first 14 times this season and won 6 of those games.`

2. **Key 1 row reads as if Kucherov's goal came on 7 shots.**
   - Current: `Nikita Kucherov scored on the power play in the 1st. That was Tampa Bay's only one, on 7 shots worth 0.7 goals`
   - Replace: `Nikita Kucherov scored on the power play in the 1st. It was Tampa Bay's only power-play goal. Its 7 power-play shots were worth 0.7 goals`

3. **"Good end / bad end" is the idiom family Charlie rejects ("go the other way", "in reverse").**
   - Current: `Buffalo got the good end of that on Sunday. On Nov. 11 it got the bad end: chances worth`
     `3.6 for Buffalo and 3.6 for Tampa Bay, and an 8-3 loss.`
   - Replace: `On Sunday, Buffalo won anyway. On Nov. 11, with chances worth 3.6 for each team, it lost 8-3.`

4. **Chart footer: "and the shot behind it" is confusing** (the empty-net goal is the shot). The chart otherwise reads on its own:
   title, legend, dots, period labels and annotation are clear, no overlaps, source and sample size in the footer.
   - Current: `Leaves out Zach Benson's empty-net goal and the shot behind it.`
   - Replace: `Leaves out Zach Benson's empty-net goal.`
   (New PNG; it isn't frozen yet.)

## Optional polish

- Lead: `The Lightning were 10-1 at home, the NHL's best home record.` -> `The Lightning came in 10-1 at home, the NHL's best home record.`
- Lead: `But Buffalo scored 5 on Dennis Hildeby, plus an empty-netter, and Ukko-Pekka Luukkonen allowed 2.` ->
  `But Buffalo scored 5 on Dennis Hildeby, plus an empty-netter. At the other end, Ukko-Pekka Luukkonen allowed 2.`
- `For the season he's 0.6 worse than average in 14 games, 38th of 77 goalies.` -> `For the season he's 0.6 goals worse than average in 14 games, 38th of 77 goalies.`
- Key 3 row `Tampa Bay 2.6, Buffalo 2.4` -> `Tampa Bay's were worth 2.6 goals, Buffalo's 2.4` (reads alone in a screenshot).
- What's next has no forward look beyond the date. Brand rule 3 favors one: e.g. the trip record (2-3-1, computable) and what to watch Wednesday.
- "won 6 of those games" (14 games) could carry a small-sample note.

## Checked

- Headline, lead, hero note, hero explainer and card dek all say the same thing; nothing in them overclaims.
- No betting language. No stat jargon in the body; hockey terms (power play, five-on-five, empty-netter) match earlier published recaps.
- None of the rejected phrasing ("lopsided", "the home kind", "go the other way", "in reverse") appears.
- "How we measure chances" gives real examples (Ostlund 17%, Kulich 4%) and ties back to the table.
