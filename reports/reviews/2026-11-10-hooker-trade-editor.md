# Editor review (stage 3): reports/2026-11-10-hooker-trade.md (v2, Bishop's-partner angle)

## Verdict: NEEDS EDITS (light). No rewrite needed.

The angle works and every Quant limit is in the text: "tracked with", 1 in 16, Poyer +0.05 vs. starters, Hamlin's backup QBs,
the coordinator confound, Hooker's yards per throw matching his teammates'. "Bet" and "betting" appear nowhere (checked story, dek
and hero). The problems are order and wording, not substance:
1. The caveats come in the wrong order. A fan sees Hamlin's +0.40, the biggest bar, and has to read three paragraphs before
   learning it's mostly backup QBs. The caveats are also spread over four paragraphs; three short bullets would cover them.
2. The lede's comparison phrasing ("0.13 points per pass play less than... gave up 0.17 more") makes the reader do sign math.
3. "Norm" appears in the table header, the track bullet and the hero. Fans don't say "norm".
4. The worked example never says what "gained 19.4" means. It reads like the Rams scored 19.4 points.

No edit below needs a new number. Every figure used is already in the story.

## One-sentence version (radio)

"The Bills' pass defense has tracked with whoever plays next to Cole Bishop: good with Jordan Poyer last year, near the bottom
of the league with C.J. Gardner-Johnson this year. So they spent a second-round pick on Amani Hooker, who has 5 of Tennessee's
8 interceptions."

The lede says this, but in four bold sentences and with awkward sign wording. The headline ("Cole Bishop needed a partner") is a
causal claim, a notch stronger than "tracked with". See edits 1-2.

## Edits, most important first

### 1. Headline: match the "tracked with" limit
OLD: `# Cole Bishop needed a partner. The Bills just traded for the playmaker on a bad Tennessee defense`
NEW: `# The Bills' pass defense has tracked with Cole Bishop's partner. Now they've traded for a playmaker`
Reason: "needed" says the partner caused it, and the Quant limited that claim. The new headline is still a hook and leaves Hooker
for the dek and lede. If you want Tennessee in the headline: "...Now they've traded for the playmaker on a bad Tennessee defense".

### 2. Lede: plain direction, a shorter bold block, one built-in hedge
OLD:
```
**The Bills' pass defense has tracked with whoever plays next to Cole Bishop. With Jordan Poyer beside him last season, Buffalo gave up
0.13 points per pass play less than its opponents usually gain, about 6th-best in the league. With C.J. Gardner-Johnson this
season, it gave up 0.17 more, about 31st of 32. Amani Hooker is the fix the Bills are counting on: on a Tennessee defense that ranks
29th of 32 in yards allowed per throw, he made 5 of the team's 8 interceptions.**
```
NEW:
```
**The Bills' pass defense has tracked with whoever plays next to Cole Bishop. With Jordan Poyer beside him last season, opponents'
passing did 0.13 points a play worse than usual against Buffalo, about 6th-best in the league. With C.J. Gardner-Johnson this season,
it's done 0.17 better than usual, about 31st of 32. Amani Hooker is the fix the Bills are counting on: on a Tennessee defense that
ranks 29th of 32 in yards allowed per throw, he made 5 of the team's 8 interceptions.**

Small samples, and other things changed along with the partner. Details below.
```
Reason: "Gave up 0.17 more" makes the reader work out whether more is good. Saying what opponents did against their usual answers
it. The one-line hedge right under the lede means a reader who stops there still gets the caveat.

### 3. Dateline: replace "coverage charting"
OLD: `Game results are through week 9 of the 2026 season; coverage charting
is through week 8.*`
NEW: `Game results are through week 9 of the 2026 season. Yards-per-throw and tackling numbers come from Pro Football
Reference's charting, which is through week 8.*`

### 4. Table: drop "norm", say which way is good, shorter headers
OLD:
```
| Bishop's partner | Games | Points per pass play vs. the opponent's norm | Against regular starting QBs only |
```
NEW:
```
| Bishop's partner | Games | Points per pass play vs. opponent's usual (+ = better) | Starting QBs only |
```
Keep 4 columns. They read fine once the headers are short, and the 4th column is the caveat itself. Under the table, change
OLD: `For scale: across all 32 defenses, the Bills were +0.09 over all of 2025 (9th) and are +0.01 so far this season (14th).`
NEW: `For scale: across all 32 defenses, the Bills were +0.09 over all of 2025 (9th) and are +0.01 so far this season (14th).
Every row is a small sample, 3 to 9 games.`

### 5. Reorder the caveats: Hamlin right after the table, then the explainer, then one "How we checked it" with three bullets
Move the Hamlin paragraph up so it directly follows the "For scale" line (unchanged text, slightly tightened):
OLD:
```
**The Hamlin games need an asterisk.** Two of the three, Baltimore and Minnesota, came against backup quarterbacks.
The one against a regular starter, Las Vegas, came out -0.19, as bad as the Gardner-Johnson games.
```
NEW (placed right after the table and "For scale" line):
```
**Ignore Hamlin's +0.40.** Two of his three games, Baltimore and Minnesota, came against backup quarterbacks. In the one against
a regular starter, Las Vegas, the defense came out -0.19, as bad as the Gardner-Johnson games.
```
If "Ignore" feels too strong to Charlie, use "**Hamlin's +0.40 needs an asterisk.**"

Then merge "How we checked it" and "What else changed" into one paragraph with bullets:
OLD: the two paragraphs beginning `**How we checked it.** Two things can fake a pattern...` and `**What else changed.** The partner isn't the only difference...`
NEW:
```
**How we checked it.** Three things could fake a pattern like this:

- **Luck.** We shuffled the 14 Poyer and Gardner-Johnson games between the two groups at random, 20,000 times. A gap this big,
  in either direction, showed up about 1 time in 16. That's suggestive, not proof.
- **Quarterbacks.** Two of Poyer's games came against backups. Take them out and his number drops to +0.05. All 5 Gardner-Johnson
  games came against regular starters.
- **Everything else that changed.** This season also brought a new defensive coordinator, Jim Leonhard, and other roster changes.
  These numbers can't separate those from the safety next to Bishop.

Bishop himself barely moved. Throws his way gained 8.8 yards each with Poyer beside him and 9.2 with Gardner-Johnson, both a bit
worse than an average safety that year (8.6 and 8.2). That's only 27 and 21 throws. The difference was around him.
```
Reason: all the same caveats and numbers, about 20% shorter, and each one is a scannable label. "The difference was around him"
(from the Quant's wording) explains why the Bishop numbers are there at all.

### 6. Worked example: say what "19.4" is and tie it to the table
OLD:
```
Example: the Rams normally gain about 0.01 points per pass play. In week 5
they gained 19.4 on 55 pass plays against Buffalo, about 0.34 a play more than usual. The partner is the other safety on the
field for the most snaps, from the league's snap counts.
```
NEW:
```
Example: the Rams' pass plays are normally worth about 0.01 points each. In week 5 against Buffalo, their 55 pass plays were worth
19.4 points combined, about 0.34 a play more than usual. That game counts as -0.34 for Buffalo, one of the five games behind
Gardner-Johnson's -0.17. The partner is the other safety who played the most snaps that game, from the league's snap counts.
```
Check for the writer and the final Quant: week 5 2026 is a Gardner-Johnson game (weeks 1-5, Stafford listed). The game-level
-0.34 is the sign-flipped version of the published +0.34, not a new number. If the generator doesn't produce that game value as
signed, phrase it as "That game counts against Buffalo".

### 7. Hooker tackling sentence: too many parentheses
OLD: `He's missed 3 of 55 tackle attempts (5.5%), better than the average
safety's 8.9% (tied for 16th-fewest misses among 58 safeties thrown at 15+ times).`
NEW: `He tackles well, too: 3 misses on 55 tries (5.5%), against 8.9% for the average safety. That ties him for 16th of 58
regular safeties.`
("Thrown at 15+ times" is already in stat-heads as "safeties with 15+ targets".)

### 8. "What we'll track": remove "norm"
OLD: `Bills pass defense against each opponent's norm with Bishop and Hooker together`
NEW: `Bills pass defense against what each opponent usually does, with Bishop and Hooker together`

### 9. Hero JSON: jargon
- big[1] label OLD: `Bills pass D vs. opponents' norm, with Gardner-Johnson` -> NEW: `Bills pass defense per play vs. what opponents usually do, with Gardner-Johnson`
- note OLD: `...beat opponents' norms by 0.13 points a play. With Gardner-Johnson, it lost 0.17.` -> NEW: `...held opponents 0.13 points a play below their usual. With Gardner-Johnson, they've been 0.17 above it.`
- explainer title OLD: `Bills pass defense vs. opponents' norm, per pass play.` -> NEW: `Bills pass defense vs. what opponents usually do, per pass play.`

### 10. Chart 1 (hooker-bishop-partner.png): passes, but just barely
The title already carries the takeaway and the "tracked" limit. Five-second problems:
- The dark/light key lives only in the subtitle. Add direct labels on the Poyer pair ("All games" next to the dark bar,
  "Starting QBs only" next to the light one), then shorten the subtitle to "+ = better than that opponent usually does. Small samples (3-9 games)."
- The light bars change color by sign (pale blue, pale red), so color carries two meanings. Optional: make all light bars
  one neutral grey and keep blue/red for the dark bars only.
- Hamlin's +0.40 is the biggest mark on the page. The label "(2 vs. backup QBs)" is there, but consider greying his dark bar, as
  the Quant suggested.
No numbers change.

### 11. Chart 2 (hooker-ten-ints.png): passes the five-second test. Optional subtitle fix: "Interceptions, 2026 weeks 1-9 (Tennessee's bye was week 9)."

### 12. Small things
- "Hooker has been the exception where it matters most" -> "Hooker has been the exception". "Where it matters most" is an
  opinion the numbers don't show, and the next sentences make the point.
- Dek (build.py) is fine as is. It uses "tracked with" and "counting on".

## Not changed, on purpose
Every Quant limit stays: "tracked with", 1 in 16, +0.05, Hamlin's backups, the coordinator confound, "about the same as his
teammates", "small sample". Edits 2 and 5 make them easier to find, not weaker.
