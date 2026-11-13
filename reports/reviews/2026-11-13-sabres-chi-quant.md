# Quant re-check 3: reports/2026-11-13-sabres-chi.md (sha256 f62d7b303111...)

**Verdict: PASS.** Both round-2 fixes are in, and every figure that changed matches my independent numbers.

## Changes checked

- **Headline** "had more of the chances for 60 minutes and still lost": Buffalo 2.115 to Chicago 1.886 in regulation, so it's true.
- **"(2,319 teams in that spot)"**: correct. That's 2,319 team-leads, which come from 2,250 games.
- **Overtime numbers**: Chicago's overtime shots were worth 0.370, which rounds to 0.4. Chicago's game total is 1.886 + 0.370 = 2.256, which rounds to 2.3. With "31 shots, overtime included" this is correct, and the rounding is consistent (1.9 + 0.4 = 2.3).
- **"That's what happened: 2-2 after 60"**: correct (Nazar tied it 8:22 into the third, and Donato scored in OT).
- **"That fits the pattern" / "Thursday fit that"**: properly hedged, and the next sentence keeps "One game can't prove it".
- **Flow chart** (I looked at the image):
  - The title "Buffalo led the chances for 60 minutes; Chicago had all of overtime" holds up. Buffalo's running total stays above Chicago's for all of regulation, and Chicago had all 3 overtime shots.
  - Subtitle figures 2.1/1.9 and 2.1/2.3 are correct. The footer still shows source and sample size (35/31 shots).
- **Nothing else in the diff** touches numbers. The hero and dek are unchanged from re-check 2 and were verified there.

## Optional nit (not blocking)

- The new subtitle explains only the blue dots ("Blue dots = Sabres goals"). The black dots mark Chicago's goals but are no longer labeled. Consider adding "black = Chicago's" back.
