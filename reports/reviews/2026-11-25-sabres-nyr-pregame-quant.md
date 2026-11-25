# Quant review (stage 2, round 2): 2026-11-25-sabres-nyr-pregame

**Verdict: PASS.** All round-1 must-fix and should-fix items are applied, and each new number matches my independent recomputation.
I reran the generator in a fresh copy of the repo and database. It reproduces the md (sha256 4b4c3488...), hero JSON and PNG byte-for-byte.
Round 1 is in `2026-11-25-sabres-nyr-pregame-quant-r1.md`. Everything verified there still holds, because no inputs or pinned data changed.

## Round-1 items, checked

1. Overclaim. The lead now says "the Rangers should score more than they have. Their goaltending will probably cool off some too."
   The body says "the two nearly cancel out: about 8 goals missed, about 7 saved ... the bigger change from here is more Rangers goals."
   Both are supported. Net -8.35 + 7.25 = -1.10 (stat-heads -1.1). Share kept: worst-finishing quarter -1.73 / -11.94 = 14.5% (14%);
   best-goaltending quarter 4.76 / 13.45 = 35.4% (35%). The generator asserts |net| < 2 and that finishing keeps less than goaltending.
   "Better than its record" and "better than their goal totals look" are gone.
2. "(6th per game)": correct. The stat-heads season-total saves rank of 7 is correct (MTL +7.41 ahead).
3. Empty-net disclosure: Lafrenière 2 of 10 and Thompson 0 of 17 are correct.
4. Shot example: this season's unblocked, non-empty-net shots. Within 10 feet 0.13489 (4,500 shots), shown as "about 13%", which is the
   correct rounding. 40 feet or more 0.02218 (10,911 shots), shown as "about 2%". Both are asserted in the generator.
5. Lead shares 53% and 48% (0.527 and 0.478) with ranks 9th and 22nd. Card and hero wording changed with no new numbers.
6. "about 2 below" (-1.7) is fine. "Already treats the Rangers as average shooters with average goalies" is accurate: the model uses
   only team chance values and a league-wide scoring ratio.

## Checked again for this text

- Unchanged numbers in the lead, body, table and model section still match: 69/61, 30th, only 2 worse, Dorofeyev 6 on 9, 16/5
  appearances, records, rest, 2 of 3, 3.1/3.2, 16%, 49/51.
- Chart opened. The new corner labels match their quadrants: top-right is "finish well, goalies stop more" and bottom-left is "don't
  finish, weak goaltending". The Rangers are still alone in the top-left area, and the footer is unchanged.
- No betting language. None of Charlie's rejected phrases appear.

## Polish (optional, not blocking)

- Stat-heads names players two ways: "(Alexis Lafrenière 2 of 10, Thompson 0 of 17)" -> "(Lafrenière 2 of 10, Thompson 0 of 17)".

## Process (unchanged)

- Not logged yet. Final check is on hold until the call is logged and the story is regenerated (the Ledger paragraph text will change).
- Freeze `sabres-nyr-nov25-finish.png` with `scripts/freeze_images.py` at publish.
