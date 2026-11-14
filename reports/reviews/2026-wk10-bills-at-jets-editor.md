# Editor review: Bills at Jets, week 10 (call-wording correction)

**One-sentence version:** The Bills should beat the Jets about three times in four, and their passing game against one of the NFL's leakiest pass defenses is our surest call of the week.

**Verdict: needs edits (FAIL on check 7).** The four reworded calls read on their own now, and so does the chart. Two lines still don't: the hero explainer and the chart's missing game name. The fixes are small. No numbers change.

## What's fixed
- Calls table and chart labels: "Bills' passing game helps more than it hurts" and the other three read on their own and follow the new house rule. Pass.
- The explainer paragraph after the table is clear and right-sized. One small fix is below (5).
- The clarification note is dated, plain, says no numbers changed, and admits the Ledger keeps the old wording. It's honest. Two accuracy tweaks are below (4).
- The dek reads on its own. Pass.
- The hero big numbers ("30 Bills, projected points", "22 Jets, projected points") and the note read on their own. Pass.

## Required (check 7)
1. **Hero explainer text** (`reports/2026-wk10-bills-at-jets.hero.json`, `explainer.text`). "Gave a passing game 70% or more" doesn't say 70% of what. Seen alone it's meaningless.
   - Replace: `When our matchup model gave a passing game 70% or more on 134 past games it hadn't seen, it said this, and this is how often it happened:`
   - With: `In 134 past games the model hadn't seen, it gave a team's passing game a 70% or better chance to help more than it hurt. Here's the chance it gave, on average, and how often it happened:`
2. **Hero explainer title.** "Its confident calls have held up." has no subject on its own. The card can show it without the story.
   - Replace: `Its confident calls have held up.`
   - With: `Our most confident calls have held up.`
3. **Chart `wk10-calls.png` doesn't name the game.** It's the site card image for this story (build.py), so it will be seen on its own, and nothing on it says Bills at Jets or Sunday, Nov. 15.
   - Replace subtitle: `Our chance that each one happens. Each comes from a kind of model we tested on past games before trusting it.`
   - With: `Bills at Jets, Sunday, Nov. 15: our chance that each one happens. Every model behind these was tested on past games first.`

## Recommended
4. **Clarification note, accuracy.** The lead (Finding) sentence was reworded too, from "pass plays gain ground". The Ledger's actual old wording is "add points overall", not "gain points overall". The note should also say why the wording changed.
   - Replace: `*Clarification, Nov. 14: we reworded the four pass and run calls into plain English (for example, "the Bills' passing game helps more than it hurts" instead of "pass plays gain points overall"). No numbers changed. The Ledger keeps the original wording, logged Nov. 13.*`
   - With: `*Clarification, Nov. 14: The old wording of our four pass and run calls, such as "pass plays gain points overall", read like scoreboard points. That's not what it meant. We reworded those calls and the lead in plain English (for example, "the Bills' passing game helps more than it hurts"). No numbers changed. The Ledger keeps the wording we logged on Nov. 13, before kickoff, because Ledger entries are never edited.*`
5. **Explainer paragraph.** "The value of every pass play" works, but tie it to the points grading above. Scrambles count as pass plays, so say that. The 64% sentence is ambiguous about which games it counts.
   - Replace: `What these mean: add up the value of every pass play (or every run) in the game, the good ones and the bad ones. If the total is above zero, that part of the offense helped more than it hurt. Running games usually hurt more than they help: in 990 past team games, that happened 64% of the time.`
   - With: `What these mean: take the points every pass play was worth in the game (sacks and scrambles count), or every designed run, and add them up, good plays and bad. If the total is above zero, that part of the offense helped more than it hurt. Running games usually hurt more than they help: in 64% of 990 past team games, a team's running game ended below zero.`
   (Writer: confirm the 64% means "rush total below zero" before using this.)
6. **Old phrasing still in the matchup section**, for consistency with the call:
   - Replace: `the Bills' passing plays leave them better off than they started.` With: `the Bills' passing game helps more than it hurts.`
   - Replace: `and the passing game came out ahead 78% of the time.` With: `and the passing game helped more than it hurt 78% of the time.` ("Came out ahead" reads as beating the other team.)
7. **Header that doesn't stand alone:** Replace `## How a 30-point projection becomes 75%` with `## How a 30-point projection becomes a 75% win chance`.
8. Optional title tweak: "Buffalo's passing game gets one of the NFL's leakiest pass defenses". "Gets" works, but "faces" is clearer.

All edits are in the generator `src/reports/wk10_prediction.py` too. Re-render from there so the report and chart stay in step.

## Ledger rows P0012-P0016 (unchanged, for Charlie)
These fail check 7 as written, and they're the wording on the Ledger page:
- P0013 / P0014: "Bills' / Jets' pass plays add points overall (EPA per dropback above zero)". Same problem as the story had: a fan reads "points" as scoreboard points. The jargon in parentheses is allowed under the rule, but it doesn't rescue the main clause.
- P0015 / P0016: "Bills' / Jets' designed runs lose points overall (rush EPA below zero)". Same problem.
- P0012: "Bills beat the Jets (any result; a tie counts as a miss)". "Any result" is unclear. The story's "overtime counts" is what it means.
- P0014's subject is "BUF pass defense" while the claim is about the Jets' pass plays. That's correct from Buffalo's side but could confuse anyone reading the CSV.
- Options, none of which edit a row: (a) leave them, and rely on the story's dated note (honest, already done). (b) Show a plain-English line next to `claim_text` on the Ledger page, kept in a separate committed file keyed by id, with the logged wording still shown. Don't add correction rows: they would look like new predictions logged after the original time. Future rows should follow the house rule from the start.
