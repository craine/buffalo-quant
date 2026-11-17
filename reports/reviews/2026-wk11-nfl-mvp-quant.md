# Quant review: 2026-wk11-nfl-mvp (round 4, final check): PASS. Rounds 1-3 failed.

Rounds 1-3 failed (see the review record history). This round reviews the text with SHA-256
`74396903eb2b7ef9570a6c1c2c9bad16990c060458cc99db5ec71ef71fffc4f5`. I diffed it against my round-3 copy (/tmp/q3/repo), and both the
story and the generator changed in only these places:

- the lead now says "this count had the real MVP No. 1 ... in its top three";
- "Nearly all of the gap" became "Most of the gap";
- the throwing bullet ("one of the three lowest rates"; the per-throw sentence was rewritten);
- "So the biggest reason he's fourth is volume.";
- three new stat-heads lines;
- the generator's asserts were tightened.

No other text or number changed. The hero JSON and both PNGs are byte-identical to round 3. The pin CSV's only difference from my
round-3 scratch copy is the +0.5 I added there to perturb the pin. All of the numbers below come from my own pandas queries on raw_pbp
(/tmp/q4), not from the writer's functions.

## Changed sentences: all true

1. **Per-throw sentence:** "Throw for throw Burrow has been a little better: each of those plays is worth about four-tenths of a
   point, a bit more for Burrow."
   - Burrow: 343 throws/scrambles, 142.21 points, **0.4146 per play**.
   - Allen: 270 throws/scrambles, 103.29 points, **0.3825 per play**.
   - Both round to 0.4, and Burrow is higher. "About 142 / about 103" is correct. The split still sums to the totals: 100.032 and 73.929.
2. **"one of the three lowest rates in the NFL"** holds in every filter variant I tried. Only the order of second and third place moves.
   Fourth place (SEA, 55.50%) is about 2 points clear, so the claim isn't fragile.

   | Filter | Lowest three dropback rates | BUF rank |
   |---|---|---|
   | Story: `qb_dropback OR rush` | TB 52.79%, BUF 53.539%, JAX 53.571% | 2 |
   | Standard: `pass OR rush`, `pass` as numerator, with or without spikes | TB 52.79%, BUF 53.54%, JAX 53.66% | 2 |
   | Standard: `pass OR rush`, `qb_dropback` as numerator (round 3's version) | TB 52.79%, JAX 53.47%, BUF 53.54% | 3 |

   The Bengals are highest at 66.85% under every filter, so "the Bengals, 67%, the highest" holds.
3. **New stat-heads line (volume vs. value per play).**
   - Throwing gap: 142.21 - 103.29 = **38.9**.
   - From volume: 73 x 0.4146 = **30.3**.
   - From value per play: 38.9 - 30.3 = **8.7** (also 270 x 0.032 = 8.66).
   - The printed "0.415 vs 0.383" is correct.
   - "Within a fraction of a play of the next team": on the story's filter, BUF and JAX differ by 0.00032 x 551 plays, or 0.18 of a play. True.
4. **"Most of the gap comes from one thing" / "the biggest reason ... is volume":** the 30.3 from volume is the largest part, and it's
   larger than the whole 26-point gap. True.
5. **Lead wording ("this count had the real MVP No. 1 three times and in its top three six times"):** the check ranks are 1, 2, 3, 1, 10,
   1, 3, so No. 1 three times and top 3 six times. This now matches the hero, the board footer and the check chart.
6. **Site card dek** (src/site/build.py, "nfl-mvp-wk11"): it reads "Burrow first, Purdy second, Allen fourth. Run back over the last seven full
   seasons, this count had the real MVP in its top three six times." Both parts are correct, and the track-record wording is fixed.

## Unchanged items (re-confirmed)

- **Hero JSON:** 100; "#4 Josh Allen, Bills (74 points added)"; the note says No. 1 three times and top 3 six times; the bars are
  100 / 92 / 87. It is identical to round 3.
- **Images:** I viewed both again.
  - Board: the numbers, records, rings and the Allen highlight are correct, the footer is complete and nothing is clipped.
  - Check chart: the title and subtitle are fully visible, and the ranks are correct.
- **Reproduction:** I deleted the .md, hero JSON and both PNGs in a clean copy (src, assets, reports, config, scripts, db) and re-ran
  `python3 -m src.reports.nfl_mvp`. It reproduced the .md, hero JSON, pin CSV and both PNGs **byte for byte**. When I perturbed the pin
  by +0.5 on row 1, the run stopped with "nflverse data changed since publication; this story is pinned."
- **New generator asserts:** `0.3 < A.per_rest < L.per_rest < 0.5` and `vol_pts > rate_pts > 0` both pass, and they guard the new wording.
- **Tests:** pytest has 50 passed and 18 skipped. I deselected the review-gate test because it fails until the final check is recorded.
- **Language:** none of the changed text contains betting words or jargon in the body.

## Nits (not blocking)

- "a little better ... a bit more for Burrow" says the same thing twice. Optional trim.
- The stat-heads "within a fraction of a play of the next team" is a literal, with no assert behind it. It is true today, and the
  story is pinned.
- The assert's lower bound of 0.3 is looser than "about four-tenths" (0.35 would be safer). It's moot for this pinned story.

**Verdict: PASS. Publish.** No numbers changed, and every edited sentence is supported by my own queries.
