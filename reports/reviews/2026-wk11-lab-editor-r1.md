# Editor review: reports/2026-wk11-lab.md (stage 3)

Reviewer: independent Editor. Date: 2026-11-22. Story sha256 at review: 0b3c3eaff56e4112372dbcc9046051adbcfe8353d1c788065caf2ff924e023f6

**One-sentence version (radio):** "Josh Allen didn't run the ball once against Miami. It's the first time that's happened
in his career, and with a fake punt and an onside-kick look up 14, the Bills looked like a team trying things out."

**Verdict: NEEDS EDITS (fail for now).** It's a fun, easy read, and the strongest fact comes first. Four problems: the headline
and labels state as fact what the lead only suggests ("lab game"), the lead's third sentence stacks four actions, the
body never shows a fan how we counted the headline number, and a couple of phrases are stilted or jargon. The Quant's
wording fixes (135 qualifier, 30-yard gain, the touchdown lineman, "than ever", the hero "fake onside look") also apply.
Their replacements are in the Quant report and are not repeated here.

## Must fix (most important first)

1. **Headline states intent; the story doesn't back it.** The lead hedges ("it looked a lot like"), but the headline says
   it was a lab game. "Other things Buffalo hadn't done all season" also isn't right for every item: the Bills had used
   extra linemen and shotgun before, just less.
   "# The Bills' lab game: Josh Allen didn't run once, and other things Buffalo hadn't done all season"
   -> "# Josh Allen didn't run once, and six more signs the Bills were trying things out against Miami"
2. **Hero label and site card say "lab game" as fact.** Both travel without the story.
   - Hero label: "The Bills' lab game" -> "Bills vs. Miami: trying things out?"
   - Card: "A fake punt, an onside look with a 14-point lead, and more: the Bills' lab game against Miami."
     -> "A fake punt, an onside-kick look with a 14-point lead, and more. Against Miami, the Bills looked like a team trying things out."
3. **Lead sentence 3 stacks four actions in one breath.**
   "The Bills also ran their first fake punt of the season, lined up for an onside kick while leading by 14 and
   then kicked deep, and put an extra lineman on the field more than in any other game."
   -> "The Bills also ran their first fake punt of the season. They lined up for an onside kick with a 14-point lead, then kicked deep. And they sent in an extra lineman more often than in any other game this season."
4. **Show how we got the headline number (standing rule).** Section 1 gives the result but not the counting. Add a short
   "how we counted" paragraph after "...or chance." It needs three new numbers the writer must compute in the generator:
   the plays in the excluded 2019 game (5), the fewest runs before Sunday (1), and how many games that happened (6).
   I saw these in the Quant's queries; the generator must produce them.
   Add: "How we counted: we went through the play-by-play of every Bills regular-season game since 2018 and counted each
   play where Allen carried the ball, not counting kneel-downs. We kept the 135 games where he threw, ran or was sacked
   at least 20 times. That leaves out one game, the 2019 finale, when he was in for 5 plays. Before Sunday, his fewest
   runs in any of those games was 1, and that happened 6 times. Never zero."
5. **Stilted line.** "Seven things don't add up to a secret." -> "None of this proves a plan."
6. **Jargon in the body.**
   - "whether the jumbo packages stay" -> "whether the extra linemen stay"
   - "or put a new package on film for future opponents" -> "or show future opponents something new to study"
   - First use of "reported in as an eligible receiver" (section 2): "This time guard Austin Corbett reported in as an eligible receiver, and"
     -> "This time guard Austin Corbett checked in with the referee as an eligible receiver, an extra blocker on the field, and"

## Optional polish

- Section 3: "Across the league, only 5 teams have run a fake punt this season (not counting botched snaps)."
  -> "Buffalo is one of only 5 teams to run a fake punt this season (not counting botched snaps)."
- Section 6 header: "More shotgun than in any other game" -> "More shotgun than in any other game this season"
- Section 4: one clause of context would help a fan: teams can try an onside kick at any score since this season's rule
  change (NFL, March 31, 2026). Without it, "every one came from a team that was behind" sounds like a rule, not a choice.
- Section 7 needs a "so what": "...then went deep only twice the rest of the game." could add "Miami took the deep ball
  away, or Buffalo stopped looking for it; the recap has the details." Only if the recap supports it; otherwise leave as is.

## Agreement check

- The headline, lead, hero, card and body agree on the numbers (0 runs, 135 games, 6.2/6 average, 14-point lead, 4
  extra-lineman plays, 59% shotgun). The intent word "lab" is the only real mismatch: in the headline, hero and card it's
  a fact, in the lead it's "looked like". Fixes 1–2 settle it.
- Hero big number "6.2" against body "6": fine, rounding.
- No banned phrasing ("lopsided", "the home kind", "go the other way"). No betting language.

## Chart (opened wk11lab-season.png)

It reads on its own in five seconds. The title is the takeaway, Week 11 stands out in blue in all three panels, the bye
is explained, and the shotgun axis is in percent. The footer has the source and a definition but no sample size (Quant
item 9). Labels don't overlap. The title "hadn't done all season" holds for each panel: week 11 is the season extreme in all three.
