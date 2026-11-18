Round 1 failed (needs edits). Round 2: PASS. Only minor polish remains.

# Editor review, round 2: reports/2026-11-18-sabres-phi.md

Stage 3 (Editor), independent. Read: revised story body, both charts (sabres-phi-post-flow.png, sabres-phi-post-situations.png),
hero JSON, site card `sabres-flyers-postgame-nov-17` in src/site/build.py, my round-1 report and the Quant's report.

**One-sentence version (radio):** "Buffalo tied it with 15 minutes left and lost it 52 seconds later on a sharp-angle shot with about a
2% chance, but Philadelphia earned the edge on the power play and Lyon gave up more than an average goalie would have."
The lead says this.

**Verdict: ready (PASS).** Every round-1 item was handled. What's left is polish the writer can take or leave.

## Round-1 items

| # | Round-1 item | Status |
|---|---|---|
| 1 | 2% described two ways | Fixed. Lead, site card, hero note, chart annotation all say "a shot with about a 2% chance". The 0.9% frequency line is gone from the body (kept in stat-heads). |
| 2 | "Long shot" / why only 2% | Fixed. Headline: "a shot that almost never goes in"; chart title: "The winner had about a 2% chance; the Flyers had most late chances". New "Why only 2%?" paragraph explains the angle and contrasts Thompson's straight-on 27-footer (16%). Computed numbers backed in stat-heads (angle 60 vs 6 deg, 31 of 810). |
| 3 | "Chances cost it" overclaim | Fixed. Finishing bullet now says Buffalo beat its chances for once (one game) and names both gaps (0.6 chances, 1.2 in goal). |
| 4 | Repetitive "one goal from a long shot" bullet | Cut. Replaced with the Quant's "Even at five-on-five, beaten on the power play." |
| 5 | Ambiguous 75% | Fixed ("Philadelphia had about 75% of the third period's chances"). |
| 6 | Misplaced "tied three times" sentence | Moved under the goal table. |
| 7 | Repeated "52 seconds" in The winner | Cut. |
| 8 | Stat-looking numbers | "+4.5 goals saved" now "4.5 goals better than an average goalie". Scorecard line rewritten in plain words, 0.23 kept in a parenthetical with its scale explained: acceptable. |
| 9 | 3.2 / 3.2 line | Cut from body (stays in stat-heads). |
| 10 | Hero explainer signs | Fixed: "Who had the better chances, and by how many goals:" with bars "Five-on-five: Sabres ahead by 0.2" / "Power play: Flyers ahead by 0.5". Reads alone. |
| 11 | Polish (tip-in, penalty note) | Done. |
| Q4 | "What we said to watch" vs pregame | Renamed "What we said going in". |

Charts: both read in five seconds; titles are the takeaway, annotation points at the right dot, footers carry source and shot counts.
Site card and hero stand alone.

## Minor polish (optional, none blocks)

1. **The winner, last sentence: 4% next to 2% can read as "so which is it?"** Replace "Shots from spots like Dvorak's this season
   (25 to 35 feet out, at that kind of angle, no rebound or rush) have gone in 4% of the time (810 shots); our model, which also weighs
   the shot type, put this one at about 2%." with "Even shots from spots like Dvorak's this season (25 to 35 feet out, at that kind of
   angle, no rebound or rush) have gone in only 4% of the time (810 shots). Our model also accounts for the type of shot, and it put this
   one lower still, about 2%." No number changes. (If the writer wants to say *why* a wrist shot rates lower there, that needs a computed
   number.)
2. **"26 feet to the side of the net"**: the 26 is measured from the middle of the ice, not the post. Replace with "26 feet off to the
   side of the middle of the net".
3. **Woll sentence grammar.** "whom" attaches to Philadelphia. Replace "[Joseph Woll](...) started for Philadelphia, whom our pregame
   story had at 4.5 goals better than an average goalie this season." with "[Joseph Woll](...) started for Philadelphia. Our pregame
   story had him at 4.5 goals better than an average goalie this season."
4. **Bullet header "Even at five-on-five, beaten on the power play"** can parse as "even when at five-on-five". Replace with "About even
   at five-on-five, beaten on the power play." Same for the hero title and situations chart title if convenient ("About even at
   five-on-five; ...").
5. **Rounding a fan may notice:** body shows five-on-five 1.7 vs 1.6 (looks like 0.1) and power play 0.9 vs 0.3 (looks like 0.6),
   while the hero bars say "ahead by 0.2" and "ahead by 0.5" (correct from unrounded 0.17 and 0.54). Not wrong; if it bothers, write
   "about 0.2" / "about 0.5" in the bar labels. Quant to confirm any change.

None of these changes a number or a claim, so a final check on the edited text is routine.
