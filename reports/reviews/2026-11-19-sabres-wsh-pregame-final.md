# Final check (stage 4): 2026-11-19-sabres-wsh-pregame

**Verdict: pass.** This covers the edits made after the round-2 quant pass. I diffed the story against the round-2 version; four lines changed, the hero JSON is unchanged, and the model-test chart title changed.

1. Model-test chart title: "Teams given a 55-60% chance to win, like Washington Thursday, won 54%". It fits (I opened the image), and the subtitle
   names the 2025-26 test, so the title reads on its own. 54% of 426 games, checked again.
2. Tuch: "In his last two seasons in Buffalo he scored about 10 and 9 more goals than his chances were worth". Tuch played for BUF in 2024-25 and 2025-26
   (all his shots that season are for BUF). Goals minus chances, empty nets left out: +9.72 (34 on 24.28) and +8.88 (32 on 23.12). Correct, and it matches the GM story.
   The order "after help a man down" still matches the GM story. Removing "ahead again this year" leaves "so he's beating his chances again" (11 on 7.2) above it, which is still true.
3. "These include every game played around the league Tuesday, so a few numbers differ slightly from the GM story." This is the real reason. `src/reports/pins.py`
   leaves out 4 late Nov. 17 games (2026020339, -340, -342, -343) for the GM story. With those 4 left out I reproduce the GM story's numbers: 2026-27 rescale factor 0.986, BUF chances allowed 3.22 a game,
   league 2.95. With all 11 games (this story) I get 0.992, 3.24 and 2.96. Both of Tuesday's BUF and WSH games are in both stories, so the difference comes only from the other teams' late games
   and the league-wide rescale.
4. "Neither tends to carry over from one part of a season to the next (see our playoff chances story)". The playoff story compares each team's first 20 games with the rest of its season:
   finishing 0.05, goaltending 0.01, "barely carry over at all". Supported.

Not changed and still verified: every table value and rank, power-play and penalty-kill numbers, the skid, Oct. 24, the goalies, the model (BUF 42.2%, expected goals 3.19 and 3.67, tied after 60 minutes 15.3%),
home-ice calibration, Brier scores, and the ledger script (0.42, puck drop 2026-11-20 00:00 UTC). The site card is dated 2026-11-18, the day it publishes. A clean copy regenerates the story, hero JSON
and all three charts byte-for-byte. No betting language, no jargon in the body.

## Round 3 final check

**Pass.** The only change since the last final check is the new "Notes for Thursday" section, and every number in it is verified (see the quant review, round 3). The rest of the story,
the hero JSON, the site card and the charts are unchanged. A clean copy regenerates them byte-for-byte. Optional wording: "772 players who have had a shot at a goalie".

## Round 3b final check

**Pass** on the current text, which includes the editor's polish to the Benson and overtime lines (verified in the quant review, round 3b). Nothing else changed. A clean copy regenerates everything byte-for-byte.
