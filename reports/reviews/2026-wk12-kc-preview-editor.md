# Editor review: 2026-wk12-kc-preview (stage 3)

Reviewed text SHA-256 83808cd0... (same text as the Quant review). Verdict: **needs edits** (small; no rewrite).

**One sentence a radio host would say:** "Buffalo Quant gives the Bills a 55% chance to beat the Chiefs, it's close because their model has Buffalo by only about two points, and it gives Josh Allen an 80% chance to run at least four times." That is the lead. Good.

Checks passed: no rejected phrases ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end"); no spreads, odds, lines or picks; the projected points and the "Buffalo by about 2 points" margin are framed as a model projection. All four series links match slugs in `src/site/build.py` ARTICLES; `../ledger.html` is correct from `analysis/<slug>.html`. Chart title is the takeaway, the scramble striping is explained in the subtitle, the 4-run line is labeled, source and sample are in the footer; it reads on its own. Hero lines and site dek read on their own and match the story.

## Must-fix (most important first)

1. **"Favorite" reads as betting language** and hides the ties (see Quant #4).
   Replace "Its favorite won 64% of 657 games." with "The team it gave the better chance won 64% of the 657 games that didn't end in a tie."

2. **The rain line promises more than we know** (see Quant #2).
   Replace "The rain could push it up. In [part 4](bills-chiefs-rain-and-wind.html) we found NFL teams run more in the rain." with "Will the rain change it? [Part 4](bills-chiefs-rain-and-wind.html) found NFL teams run more in the rain, but that counted designed runs by everyone, mostly running backs, and no scrambles. It doesn't tell us about quarterbacks, so the 80% leaves the weather out."

3. **Raw machine timestamp in the fan body.** "Both calls were logged at 2026-11-25T14:44:10Z UTC, before kickoff" ("Z UTC" is also redundant).
   Replace with "Both calls were logged Wednesday at 9:44 a.m. Eastern, before kickoff" — the generator should format this from `logged_at` (14:44:10Z = 9:44 a.m. ET) rather than type it. Keep the raw UTC stamp in "For the stat-heads".

4. **Plain-English model description** (also a factual fix, Quant #1).
   Replace "from how many points it scores and allows per drive this season, adjusted for who it played, plus home field." with "from how many points its offense scores per drive this season and how many the other team's defense gives up, blended with last season's numbers, plus home field."

## Recommended

- Add after "He did it in 8 of 10.": "Ten games is a small sample." (Quant #5; required by the self-check list.)
- "a northeast wind of 10-13 mph" -> "a northeast to east wind of 10-13 mph" (Quant #3).
- "In games like it since 2018" is vague on its own. Suggest "In past NFL games with rain and at least a 10 mph wind (part 4)", and "against 22.9 for the same teams in dry games" -> "against the 22.9 we'd expect from the same offenses and defenses in dry games."
- "To turn that into a win chance, we replay how far real games have landed from the model's projections." A fan can follow it, but one concrete example (for instance: "if Buffalo scores 7 more than projected and Kansas City 3 fewer, the way real games have gone...") would land better. Optional given the deadline.
- Typed words in the generator ("under two points", "The two times", "northeast", hours) should be derived or asserted (Quant should-fix).
