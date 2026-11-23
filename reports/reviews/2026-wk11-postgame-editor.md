# Editor review (stage 3): 2026-wk11-postgame

**Verdict: NEEDS EDITS (fail for now).** The bones are good. The defense-plus-Allen story is clear, the open-receivers question gets an honest answer, and the drop caveat is there. Two problems stop it: the headline blames Allen for incompletions the data can't pin on him, and several lines are stacked or stilted. The Quant's number fixes (Bass 4 of 5, Miami -0.26 / 22nd / 25%, Bills +0.04) also need to flow into the text below.

**One-sentence version (radio):** "The Bills' defense kept Miami out of the end zone, and Josh Allen had five easy throws fall incomplete, though most came with the game already in hand."
That isn't quite the current lead. The lead tries to carry four points (defense, Allen, deep shots, red zone) in stacked sentences.

**Agreement check:** the headline, lead, hero, card dek and body all tell the same two-part story. The words "misses" / "left on the field" in the headline, hero note and dek all assign blame that the body itself walks back ("could be drops or tipped balls"). Fix all four together.

**Banned phrasing:** "lopsided", "the home kind", "go the other way": none found.

## Edits, most important first

1. **Headline (overclaims cause).**
   - Current: "# Bills 26, Dolphins 9: the defense held Miami without a touchdown, and Josh Allen left some easy throws on the field"
   - Replace: "# Bills 26, Dolphins 9: the defense kept Miami out of the end zone, and five easy Josh Allen throws fell incomplete"

2. **Lead (stacked clauses, stilted "by the completion chance on each throw", an interception called an incompletion, deep-shot line with no so-what).**
   - Current: "**Buffalo's defense held Miami to three field goals and no touchdowns. Josh Allen threw for 304 yards but missed more than usual: by the completion chance on each throw, an average quarterback would have completed about 29 of his 43 targeted passes; he completed 27. Five of his incompletions, one of them intercepted, were throws that get caught at least 70% of the time. He also went deep 5 times in the first quarter. And the Bills kicked 3 field goals in 5 trips inside the Miami 20.**"
   - Replace: "**Buffalo's defense held Miami to three field goals and no touchdowns. Josh Allen threw for 304 yards, but five throws that usually get caught fell incomplete or were picked off. On the same 43 throws, an average quarterback would have completed about 29. Allen completed 27. And the Bills settled for field goals on 3 of their 5 trips inside the Miami 20.**"

3. **Hero note (blame).**
   - Current: "Bills 26, Dolphins 9. Five of Allen's misses were throws usually caught 70%+ of the time."
   - Replace: "Bills 26, Dolphins 9. Five Allen throws that usually get caught (70%+ of the time) fell incomplete or were picked off."

4. **Site card dek (blame).**
   - Current: "Bills 26, Dolphins 9. The defense held Miami without a touchdown. Five of Josh Allen's misses were throws that usually get caught."
   - Replace: "Bills 26, Dolphins 9. The defense held Miami without a touchdown. Five Josh Allen throws that usually get caught fell incomplete or were picked off."

5. **Jargon in the body ("percentage points below expected", "+3").**
   - Current: "That's about 4 percentage points below expected; the rest of this season he's been +3. It ranks 32nd-worst of his 133 regular-season games\nwith 15 or more throws since 2018: a bad day, not one of his worst."
   - Replace: "That's about 2 completions short. In his other nine games this season, he'd completed more than an average quarterback would have. Of his 133 regular-season games with 15 or more throws since 2018, this ranks 32nd-worst. A bad day, but not one of his worst."
   (The numbers come from the generator: 28.9 - 27 = 1.9; rest-of-season CPOE +2.7. The writer should compute "2 completions short" in code.)

6. **Table lead-in.** It reads as if Allen usually completes them.
   - Current: "The five throws an average quarterback usually completes:"
   - Replace: "The five throws that usually get caught but weren't:"

7. **Context after the table (from the Quant's garbage-time finding; keep the drop sentence).**
   - Current: "A missed throw isn't always the quarterback's fault: some of these could be drops or tipped balls. The play-by-play doesn't say which."
   - Replace: "An incomplete pass isn't always the quarterback's fault. Some of these could be drops or tipped balls, and the play-by-play doesn't say which. Four of the five came with Buffalo already up by 14 or more: three in the two-minute drill before halftime, and one with under three minutes left in a 23-9 game."

8. **Answer Charlie's question more directly (stacked sentences; "targeted").**
   - Current: "What we can see: he didn't stop throwing short. 67% of his targeted throws went less than 10 yards, more than his 63% the rest of the season (league: 67%).\nThe deep shots came early: 5 of his 11 first-quarter passes went 20+ yards, and 2 of his 7 deep throws all game were caught. After the first quarter he went deep 2 times in 34 passes."
   - Replace: "What we can see: he didn't stop throwing short. Two of every three passes went less than 10 yards downfield, more than the rest of his season (63%) and the same as the league (67%). All five easy misses were short throws. The problem wasn't skipping the short guy; it was the short ball not connecting.\nThe deep shots came early. Five of his 11 first-quarter passes went 20 or more yards downfield. After that, he went deep just twice in 34 passes. Two of his seven deep throws were caught."
   ("All five easy misses were short" is verified by the Quant: air yards -4 to 8. It needs a line of code in the generator.)

9. **Defense paragraph (stilted counts; "successful" is jargon).** Includes the Quant's corrected numbers.
   - Current: "Only 28% of its plays gained enough to count as successful. Buffalo sacked Kyle McCord 2 times and intercepted him 1 time, and Miami's only points came on three field goals."
   - Replace: "Only 1 in 4 of its plays gained enough yards to keep a drive on track. Buffalo sacked Kyle McCord twice and picked him off once. Miami's only points came on three field goals."

10. **"Points per play" explainer ("expected points" is jargon).**
    - Current: "\"Points per play\" is how much each play changed a team's expected points, based on down, distance and field position, averaged over the game. Zero is average."
    - Replace: "\"Points per play\" measures how much each play helped or hurt a team's chances of scoring, based on down, distance and field position, averaged over the game. Zero is average."

11. **Field-goal section (two numbers jammed together, "20 5"; Bass fact from the Quant).**
    - Current: "Buffalo got inside the Miami 20 5 times and scored 2 touchdowns. Tyler Bass made all 4 field-goal tries. Buffalo's offense averaged +0.02 points per play, about average."
    - Replace: "Buffalo reached the Miami 20 five times and scored two touchdowns. Tyler Bass made 4 of 5 field goals; he missed from 54 yards in the third quarter. Overall, Buffalo's offense was about average (+0.04 points per play)."

12. **Chart 1 title (calls an interception an incompletion; "Allen's incompletions" leans on blame).**
    - Current: "Five of Josh Allen's incompletions were throws that usually get caught"
    - Replace: "Five Josh Allen throws that usually get caught fell incomplete or were picked off"
    Also move "43 throws" into the footer (CLAUDE.md wants the sample size in the footer).

13. **Chart 2 title.** It doesn't stand alone in a screenshot (no opponent) and says "2 times".
    - Current: "Allen went deep 5 times in the first quarter, 2 times after that"
    - Replace: "Josh Allen went deep 5 times in the first quarter vs. Miami, twice after that"

## Optional polish
- Table column "Yards past the line" -> "Yards past the line of scrimmage" (clear on its own, and avoids "line").
- Fourth-quarter table row: Result "Incomplete (Bills up 23-9)" so the row reads on its own.
- Chart 2 counts 45 passes (including 2 throwaways) while chart 1 shows 43. Add "includes 2 throwaways" to chart 2's footer so a fan comparing them isn't confused.
- "What's next" is one line. The brand is "predictive over descriptive": add one forward line (for example, whether the Thursday preview will carry a logged call).
- Date line: "*One game, Nov. 22, in Buffalo." is a good small-sample label. Keep it.

## Charts opened
- wk11d-allen-throws.png: clean, readable, high contrast, band and deep line labeled, legend clear, source in footer. Title fix above.
- wk11d-deep-by-quarter.png: readable in five seconds, bar labels clear ("5 deep of 11"), footer has source and 2 of 7. Title fix above.

---

# Round 2 (md sha256 9afdd130...)

**Verdict: NEEDS ONE FIX (fail).** All 13 round-1 edits landed. The headline, lead, hero note, card dek and body now agree, and none of them blames Allen for the incompletions. The drop caveat and the four-of-five context sit right after the table. The open-receivers answer is direct and fair. No banned phrasing.

## Must-fix
1. **Chart 1 title is cut off in the PNG.** It renders as "Five Josh Allen throws that usually get caught fell incomplete or were picked of". The final "f" runs off the right edge.
   - Current title: "Five Josh Allen throws that usually get caught fell incomplete or were picked off"
   - Replace: "Five easy Josh Allen throws fell incomplete or were picked off" (about 62 characters; it fits at the current size). The other option is to keep the wording and wrap it onto two lines.
   - This changes only the PNG. The md doesn't contain the chart title, so its SHA should stay the same. Re-check the PNG at the final stage.

## Optional polish
- "2 of his 7 deep throws were caught." becomes "Two of his seven deep throws were caught." (don't start a sentence with a numeral).
- "Buffalo scored 26; Miami scored 9, about 10 fewer than we expected." becomes "Buffalo scored 26. Miami scored 9, about 10 fewer than we expected."
- In the lead, "Four of those five misses" could be "Four of those five" to drop the last trace of blame.

Chart 2 reads alone and fits. Its footer explains the 45 vs 43 totals. Both charts have the source and sample size in the footer.

---

# Round 3 (md sha256 9d8fe7e2...)

**Verdict: READY (pass).** I opened chart 1. The title "Five easy Josh Allen throws fell incomplete or were picked off" fits fully, reads on its own and doesn't blame Allen. The three polish edits read cleanly. The lead no longer says "misses". The headline, lead, hero note, card dek, body and both chart titles agree. No banned phrasing, and no jargon in the body.
