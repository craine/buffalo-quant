# Editor review: 2026-11-21-nfl-mismatches-home.md

Reviewer: independent Editor (stage 3). Read the story body, both charts (nfl-mismatch-home.png, nfl-mismatch-endings.png),
the hero JSON and the site card. No files edited.

## One-sentence version

"Over 27 years, a much better NFL team won about 9 in 10 at home but only about 7 in 10 on the road, division games were no
closer than any other, and Sunday's Bills-Dolphins game is the home kind."

That is the lead, which is good. But the story never says what 88% means for Sunday next to the 81% our model published two
days ago, and that is the first question a host will ask (issue 1).

## Verdict: needs edits (fail)

Clean, tight, no betting language, no stat jargon past "median". Three fixes go beyond polish: the 88% history number now clashes
with Thursday's "history and our model agree" line; "a difference of 15 points" reads as scoreboard points; and the home section
and chart title claim home field matters *more* in lopsided games, which the chart doesn't show.

## Edits, most important first

1. **88% vs. our 81% (conflict with the first story).** Thursday's story: "Our model's number: Bills 81%, right next to the 79%
   history gives." This story ends the lead with "Sunday's game, Dolphins at Bills, is the home kind", so a fan does the math: 88%.
   Now history and our model are 7 points apart, and we never say so. Add one line after the lead, or at the end of "Home field",
   for example: "Our model, which already counts home field, gives the Bills 81% on Sunday. [Reason it's below 88%: writer and
   Quant supply]." If no reason can be computed, at least say plainly that the 88% describes past games and our published
   chance for Sunday is still 81%. Don't leave the two numbers side by side unexplained.

2. **"a difference of 15 points"** (Home field section). In a story where every other "points" is scoreboard points, this reads
   as 15 points on the scoreboard. Replace with: "a difference of 15 percentage points, or about 15 more wins in every 100 games."
   Also tighten the paragraph, since 88/73 repeats the lead word for word. Replace "In the lopsided ones it's worth more than you'd
   guess: with a gap of 17 or more, the better team won 88% at home and 73% on the road, a difference of 15 points." with
   "And a big gap doesn't make it go away: the much better team won 88% at home and 73% on the road, about 15 more wins in every
   100 games."

3. **Overclaim: home field "worth more" in lopsided games.** The chart shows the home boost is about the same at every gap: 59
   vs. 46 at 0-3 (13 apart), 89 vs. 71 at 17-20 (18), 87 vs. 74 at 20+ (13). "Worth more than you'd guess" in lopsided games, the
   chart title "Lopsided games are a lot more lopsided at home" and the headline's "far more lopsided" all suggest home field
   grows with the gap. The true and still interesting point is that it doesn't shrink: even a far better team gives a lot back
   on the road.
   - Headline: replace "Home field makes NFL mismatches far more lopsided. Rivalries don't change them." with "Even a much
     better NFL team wins far less often on the road. Rivalry games aren't any closer." (or keep the current headline if the
     Quant confirms the "more" reading, but drop "far").
   - Chart title (nfl-mismatch-home.png): replace "Lopsided games are a lot more lopsided at home" with "At every size of
     mismatch, the better team wins more at home". The current title also doesn't fit the 0-3 bars, which aren't lopsided games.
   - Writer/Quant: if you want to keep "worth more", compute the home-minus-road edge by gap band and show it. Don't assert it.

4. **Sunday tie: say who's better and show the math.** "the gap between the two teams is 18.2 points a game" doesn't say which
   team is better, and the decimal looks like a stat. The first story has the worked example. Replace with: "the Bills have
   outscored opponents by [X] a game and Miami has been outscored by 8.4, a gap of 18.2." (Use the Bills' figure from the
   first story's generator.) This is also the "where the number comes from" example a reader who missed Thursday needs.

5. **Threshold switch in Parity.** Everything else uses 17+. "With a gap of 14 or more" comes with no reason, and a fan will
   suspect cherry-picking. Either use 17+ (writer computes), or add why: "We drop to 14 or more here because there are only
   [n] games of 17+ since 2020." Also the earlier-period sample (631) is only in the stat-heads section. Give it in the body:
   "78% from 1999 to 2019 (631 games) and 72% since 2020 (156 games)."

6. **Bills vs. Miami 4-2 is a tiny sample, and it doesn't say what it proves.** Replace "The Bills, when they were the better
   team by 10 or more going in, are 4-2 against Miami since 1999." with "The Bills, when they were the better team by 10 or more
   going in, went 4-2 against Miami from 1999 to 2025, too few games to read much into." ("Since 1999" with "are" sounds like
   it includes this season, but the sample stops at 2025.)

7. **"median" is a stats word.** Replace "the median final margin was 5 points" with "the typical upset was decided by 5 points
   (half were closer, half wider)", and "Its median winning margin was 13 points." with "Its typical winning margin was 13
   points."

8. **Mixed message on blowouts.** "lopsided matchups don't usually end in blowouts" is followed by the much better team winning
   by 17+ 42% of the time, which is the biggest single outcome on the chart (140 of 420). Replace "And lopsided matchups don't
   usually end in blowouts: when the much better team won, it won by 17 or more 42% of the time, and by one score or less 36%
   of the time." with "When the much better team won, it was a 17-point rout 42% of the time and a one-score game 36% of the
   time." ("One score or less" is redundant: one score already means 8 or fewer.)

9. **Cold weather: which teams?** "When the much better team hosted outdoors at 40°F or colder" doesn't say what "much better"
   means here. Replace with "When a team 17+ points a game better hosted outdoors at 40°F or colder, it won 28 of 29." (Writer
   should confirm the cold cut uses 17+; the stat-heads line says "better team at home" without a gap.)

10. **Site card has no Bills hook.** The card runs under "Bills · By the numbers" but never mentions the Bills. Append: "Sunday's
    Dolphins at Bills game is the home kind." Keep it in step with whatever fix 1 adds, so the card doesn't imply 88% for
    Sunday by itself.

11. **Endings chart subtitle doesn't stand alone.** "How the 420 games with a gap of 17+ points ended" leaves out what the gap is.
    Replace with "How the 420 games where one team's scoring margin was 17+ points a game better ended, 1999-2025, from the
    better team's side." The bars, labels and title read fine on their own.

12. **Hero lines (polish).** "Same kind of team on the road" doesn't make sense alone in a screenshot. Replace with "Much better
    team on the road won". Explainer title "Better team's win rate, gap of 17+": replace with "How often a much better team
    won (17+ point gap in scoring margin)".

## Checked and fine

- Brand rule 1: no odds, spreads, picks, locks, favorites or over/under. "We don't use betting lines" is a disclaimer, as in the
  first story. "Upset" is ordinary sports language here, defined by scoring margin and not by a market.
- Stands alone for someone who missed Thursday: the lead defines the mismatch inline and the italic note defines scoring
  margin. Adding fix 4 completes it.
- Length is right for a Saturday follow-up. "Throw out the records" is a good radio hook. The cold-weather caveat ("a note,
  not a finding") is well judged.
- The home chart reads in five seconds once the title is fixed. Its 17-20/20+ bars (89%/87%) match the 88% combined figure
  in the text.

---

# Round 2 (re-read of the regenerated story, charts, hero and card)

## Verdict: needs edits (fail), narrowly

All 12 round-1 findings are in and mostly well done. The new headline is clearer and true, the Sunday section gives a reader who
missed Thursday everything they need, both charts now read on their own, and the hero and card hold up alone. Two sentences
still need fixing. One brings back the round-1 "points" problem; the other gives a reason for 81% vs. 88% that doesn't hold.

## Remaining edits

1. **Home field: "ran 10 to 17 points higher"** has the same scoreboard-points problem as round-1 finding 2. The top of the range
   also disagrees with the chart: the 17-20 group is 89% vs. 71% on the chart, 18 apart, and the stat-heads line gives +0.175.
   Replace "the better team's win rate at home ran 10 to 17 points higher than on the road in every group on the chart" with
   "in every group on the chart, the better team won 10 to 18 more games out of every 100 at home than on the road." The
   writer/Quant should settle the 17 vs. 18 rounding so text and chart match.

2. **Sunday: the reason given for 81% vs. 88% doesn't follow.** "it comes out lower partly because it doesn't take a team's
   early-season scoring margin at face value, which the first story showed tends to shrink" doesn't explain the gap. History's
   88% is also built on margins measured before each game, so any shrinking is already in that 88%. Shrinking would explain the
   gap only if the model shrinks margins more than real seasons do, and that isn't shown. The first story does have a reviewed,
   traceable number for this: the model runs cautious in big mismatches. Replace that clause with: "Our model already counts
   home field, and in big mismatches it runs a little cautious: since 2018, in the 61 games where it expected the better team
   to win by 10 or more, it gave those teams 82% and they won 87%." (From the first story's stat-heads line: 10+: n=61, said
   0.823, won 0.869.) The Quant should confirm this is the honest explanation, or drop the "why" and keep only "It describes
   past games, not a forecast: our published chance for Sunday is still 81%."

## Polish (optional)

3. "That's history's 88% spot." Replace with "Sunday fits the group that won 88% of the time."
4. "it was a 17-point rout 42% of the time" could be read as exactly 17. Replace with "it won by 17 or more 42% of the time".

## Checked and fine in round 2

- Headline, lead and dek: clear, shareable, and they stand alone. Rivalry section unchanged and good. Cutting the parity note
  was the right call.
- Home chart title "At every size of mismatch, the better team wins more at home" is true and reads in five seconds. The
  endings chart subtitle now stands alone.
- Hero lines and the site card read alone. The card now pairs the 88% with "our model's chance for the Bills is 81%", so it
  doesn't imply 88% for Sunday.
- Cold note names the 17+ cut and keeps its small-sample caveat. Still no betting language anywhere.

---

# Round 3

## Verdict: ready (pass)

- Fix 1 is in. "10 to 18 more games out of every 100" matches the chart's rounded bars (13, 15, 10, 13, 13, 18, 13 apart) and
  can't be read as scoreboard points.
- Fix 2 is in. Sunday now makes no unsupported causal claim and states plainly that 88% is history and our published chance
  is still 81%. It matches the site card.
- Polish 3 and 4 are in.

Optional, not required: in Sunday, "our published chance" could read "our model's published chance" to match the site card's
wording and tell a first-time reader where the 81% comes from.
