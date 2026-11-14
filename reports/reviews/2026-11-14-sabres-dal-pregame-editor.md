# Editor re-review: 2026-11-14 Sabres at Stars pregame (text sha256 5b40732dce48...)

**Verdict: needs one edit (FAIL on this text). Otherwise ready.**

All six required fixes and all four suggestions from round 1 are in, and they read well. The lead is now clean and agrees with the body. The Oct. 8 caution is honest. The "how we measure" box has its source, math, check and tie-back to Buffalo's numbers. The Chicago contrast paragraph is the best paragraph in the story. The links resolve to real slugs (`sabres-blackhawks-pregame-nov-12`, `sabres-50-win-mirage`).

**Radio line (unchanged):** "Our model has Dallas winning about 62 times in 100 because the Stars keep teams away from their net and the Sabres don't. And forget the bounce-back talk after Dallas got hammered 8-3 Thursday: teams coming off a blowout actually win a little less often than usual."

## Required fix

1. **The score is written backwards.** "still lost 0-4" should be "still lost 4-0". Hockey scores are written winner first, the same way the story writes "lost 8-3" and "lost 3-2". A fan will stumble on it.
   - Generator `src/reports/sabres_pregame_dal.py` line 299: replace `still lost {m1_sc_us}-{m1_sc_them}.` with `still lost {m1_sc_them}-{m1_sc_us}.`
   - The rendered text becomes `still lost 4-0.` No number changes, and the assert on line 252 still holds.

## Notes (not blocking)

- "Much of that gap is in goal... about 0.23 goals a game" is fine as wording. The number is for the Quant, as you said.
- The hero card and the dek ("a little less than usual") match the story.
- No betting language. Stat terms appear only in "For the stat-heads".
