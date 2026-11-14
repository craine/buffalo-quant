# Editor re-review: Bills at Jets, week 10 (text sha256 57801beccde4)

**One-sentence version:** The Bills should beat the Jets about three times in four, and their passing game against one of the NFL's leakiest pass defenses is our surest call of the week.

**Verdict: needs edits (FAIL). One small fix is left, from the new CLAUDE.md rule.**

## Fixes checked, all in
- **Hero explainer:** the text now says what the 70% is a chance of, and the title "Our most confident calls have held up." reads on its own. Pass.
- **Calls chart:** the subtitle names the game ("Bills at Jets, Sunday, Nov. 15"). The title and five labels read on their own. Pass, except item 1 below.
- **Clarification note:** it's plain and honest. It says why we changed the wording, that no numbers changed, and quotes the Ledger's actual wording ("Bills' pass plays add points overall"). It says the entries were logged before kickoff and are never edited. Pass.
- **Explainer paragraph:** it's clear. It covers designed runs and counts scrambles as pass plays, and the 64% sentence is no longer ambiguous. Pass.
- **Matchup lines, the 78% line, the header and "faces":** all in, and all read fine. Pass.
- **Dek and hero big numbers:** unchanged, and they pass.

## Required
1. **The run-call labels need the scramble note next to them.** CLAUDE.md now says: "The run calls count designed runs only; QB scrambles count as pass plays, so say so next to any run call." In the story, only the explainer paragraph says this. The two run rows in the calls table and the two run labels on wk10-calls.png don't. The chart is the card image, so it travels without that paragraph. A fan who sees "Bills' running game hurts more than it helps (66%)" will count Josh Allen's scrambles in it.
   - **Calls table:** replace `| Bills' running game hurts more than it helps |` with `| Bills' running game hurts more than it helps (designed runs; QB scrambles count as passes) |`. Do the same for the Jets row.
   - **Chart:** to keep the labels short, add a note line to the subtitle. Replace `Bills at Jets, Sunday, Nov. 15: our chance that each one happens. Every model behind these was tested on past games first.` with `Bills at Jets, Sunday, Nov. 15: our chance that each one happens. Running game means designed runs; quarterback scrambles count as passing. Every model was tested on past games first.`
   - Or put the same "Running game means designed runs; quarterback scrambles count as passing." as the first footer line.
   - Make both changes in `src/reports/wk10_prediction.py` and re-render.

## Ledger P0012-P0016 (unchanged, for Charlie)
- **P0013-P0016** still read "pass plays add points overall" and "designed runs lose points overall", with jargon in parentheses. A fan reading only the Ledger page can take that as scoreboard points.
- **P0012:** "any result" is unclear.
- These rows can't be edited, and the story's note now quotes them honestly.
- Option: show a plain-English line next to the logged wording on the Ledger page, kept in a separate committed file keyed by id. Don't add correction rows.
