# Editor review: 2026-wk12-kc-postgame (stage 3)

**One sentence:** "Josh Allen threw for just 81 yards Thursday, the fewest in any of his 105 career wins, and the Bills beat Kansas City anyway by running 40 times and winning it on a 57-yard kick."

**Verdict: needs edits (light).** The hook is strong and shareable, the lead works on radio, the chart reads in five seconds.
No betting language. None of the rejected phrases ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end") appear.
Links: `bills-chiefs-rain-and-wind.html` and `bills-chiefs-slowing-mahomes.html` match slugs in src/site/build.py. Numbers are all
template variables in the generator; the only literal digits are definitions (15+ passes, 20+ yards, since 2018/2023, 10+ mph, "4 or more"
threshold, "0 is perfect"). The "4 or more" could read from P0025's threshold but matches the Ledger claim.

## Edits, most important first

1. Apply Quant must-fixes 1 and 2 (Mahomes 137 starts; drop "Buffalo did this one").
2. Headline is slightly redundant ("fewest in any of his wins ... and Buffalo won anyway"). Replace
   `the fewest in any of his 105 wins, and Buffalo won anyway` with `the fewest in any of his 105 career wins`.
   (Optional; the current version is still shareable. If kept, fine.)
3. "runs worked" is never explained in the body. Replace
   `Kansas City's runs worked 63% of the time` with `Kansas City's runs gained enough to stay on schedule 63% of the time`.
4. "dropbacks" is football-insider. Replace `2 of Kansas City's 31 dropbacks gained 20 or more yards` with
   `2 of Kansas City's 31 pass plays gained 20 or more yards`.
5. "Scores: 0.20 and 0.04, where 0 is perfect." reads as stats. Replace with
   `Our accuracy scores: 0.20 and 0.04, where 0 is a perfect call.`
6. Chart legend "Thursday vs. Kansas City" doesn't stand alone in a screenshot. Change the legend label to
   `Nov. 26, 2026 vs. Kansas City`.
7. Small-sample label from Quant should-fix 3 belongs in the part 3 section; a fan should know it's one game.

The "behind the scenes" bar is met for the key number: the chart shows every win, the subtitle says what counts, and the body says
which games are in and which one game had fewer yards.
