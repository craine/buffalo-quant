# Editor review: Penguins 6, Sabres 3 (2026-11-27)

**One-sentence version (radio):** "The Sabres got the better looks Friday, but Pittsburgh scored five goals on chances that are usually
worth about two, something an NHL team has done only about once every 400 times since 2023."

**Verdict: FAIL (needs edits).** The story is short, well ordered, and has a good hook. Two things block it: the headline sells a
conclusion the body walks back, and three stand-alone lines (chart title, dek, hero) state the cutoff in a way that doesn't match
the count. That cutoff problem is the Quant's issue 1; take those edits from the Quant report.

## Edits, most important first
1. Headline. Old: `# Penguins 6, Sabres 3: Pittsburgh's finishing came back all at once` New: `# Penguins 6, Sabres 3: Buffalo had the chances, Pittsburgh had the finish`.
   The body says one game is mostly luck and Pittsburgh is still 25th. The headline shouldn't say the opposite.
2. Lead. Old: `It didn't take long.` Replace it with the Quant's wording: `Our preview said Pittsburgh's poor finishing probably wouldn't last over the season. One game doesn't prove that, but Friday was a big swing.`
3. Chart title, dek and hero: use the Quant's issue-1 wording. Each has to read alone, and "5 goals on chances worth 1.8: 21 times"
   is both inaccurate (26 at a 1.8 cutoff) and wrong on "5" (two of the 21 had 6).
   Hero line 2 alone, "how often a team does that", doesn't say what "that" is. Use `how often a team scores 5+ on chances that thin, since 2023-24`.
4. Repetition. Old: `Buffalo's goals came from Jiri Kulich, Rasmus Dahlin and Josh Norris;\nJosh Norris's came from 2 feet, a chance worth about 48%.`
   New: `Buffalo's goals came from Jiri Kulich, Rasmus Dahlin and Josh Norris, whose goal came from 2 feet, a chance worth about 48%.`
5. Jargon. "unblocked shots" first appears in "The game", before "How rare that is" explains it. Old: `Buffalo had 36 unblocked shots to Pittsburgh's 32`
   New: `Buffalo had 36 shots that weren't blocked to Pittsburgh's 32`. Also take the Quant's Lyon fix ("20 unblocked shots") so the two goalie lines match.
6. Optional: "team-games" is our word, not a fan's. If the writer wants it plainer, "8,700 times an NHL team has played a game" works. It's fine to keep it as is, since the chart subtitle explains it.

## Checked
- Rejected phrases ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end"): none found.
- No betting language. No stat terms in the body (xG, GSAx and the like appear only in "For the stat-heads").
- Where the key number comes from: "How rare that is" explains the shot values, the add-up, the near-1.8 baseline (2.1 goals) and the
  per-season scaling. It ties back to the headline (5 vs. 2.1) and uses the Lizotte callback as the worked example. That's the right size.
- Chart: I looked at the PNG. The title fits on one line, the annotations don't overlap the points or each other, the legend is clear, and the footer
  has the source and 8,700 team-games. A fan reads it in five seconds: the red dot sits far above the line.
- Links: the story has no inline links. The site card image `sabres-pit-nov27-postgame.png` exists and is frozen in `published_images.json`
  (re-freeze after the title fix).
- What's predictive: "What it means" points to the number that carries forward, Buffalo's 48% share (21st). Good.
