# Final check (stage 4): 2026-11-18-sabres-then-now

Checked text SHA-256 `0d56c8aec389af90471a021557e950d5f7ac56e40e164620ffe705184b97dc2e`. Scope: every edit since round 4 (`4ff3ec6a…fc3f`), including the editor's round-5 fixes. I diffed the text line by line.

## Verdict: pass

- Round-4 fixes: "on its own" for the 22% what-if, "tied for 28th" (body and stat-heads), and "After 20 games last season" / "at the same point". All present ✓.
- Round-5 changes:
  - Section 1 restores "A man down, it allows the 4th-most; more on that below." This is correct: BUF allows 0.794 a game, league 0.661, 4th-most of 32. It means the header ("the penalty kill is the worst of it") is backed up in its own paragraph again.
  - The verb in move 4 is fixed: "but they're tied for 28th in goals". BUF and CHI are both at 0.476 a game.
  - "Small sample, too." is shortened and changes no number.
- What-if table: 16/22/32/31/52% matches the playoff story. "One more goal's worth of chances every 5 games" equals the playoff story's 0.2 a game. The date note ("through Nov. 14, before the Nov. 17 loss to Philadelphia") is correct.
- GM calls (don't sell; trade at 40 games for penalty-kill help; not a goalie) are first-person judgment marked by the "— Charlie" line. None is presented as a finding, and all are consistent with the playoff story's carry-over numbers.
- Reproduction: re-running the generator in a fresh copy (/tmp/qa2/copy8) gives a markdown file, hero JSON and three PNGs byte-identical to the committed files. The hero JSON and charts haven't changed since round 3. The site card ("sabres-if-i-were-gm", "By Charlie…", GM chart as hero) matches.
- Brand: no betting language, and stat terms appear only under "For the stat-heads".

Optional, not blocking:
- GM intro, "that kind of luck doesn't carry over well": the study found goaltending and finishing carry over weakly, which isn't the same as luck. "That kind of edge" would be more exact.
- The "— Charlie" line signs calls that were drafted for him. Charlie should approve the calls themselves, not just the numbers, when he reviews the story.
