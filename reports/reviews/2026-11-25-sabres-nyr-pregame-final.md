# Final check (stage 4): Sabres vs. Rangers preview, Nov. 25, 2026

Story: `reports/2026-11-25-sabres-nyr-pregame.md` (SHA-256 `ed8795febe3e8df188a3c2fa428c4d5689737ca133344844a40b46cbc15199c7`)
Generator: `src/reports/sabres_pregame_nyr_nov25.py` (AS_OF 2026-11-24)

**Verdict: PASS.** Nothing must be fixed.

## 1. Reproducibility

I copied the full working tree, including untracked files, to `/tmp/bqfinal` with `data -> /home/claude/bq-p/data`. I deleted the three outputs
there and ran `python3 -m src.reports.sabres_pregame_nyr_nov25` (exit 0, fresh mtimes 09:45:33 ET). I used a copy instead of `git worktree` because the
story, generator and logger are untracked and a worktree from HEAD would not include them. All three outputs are byte-identical to bq-p:

| File | SHA-256 |
|---|---|
| 2026-11-25-sabres-nyr-pregame.md | ed8795fe...199c7 |
| 2026-11-25-sabres-nyr-pregame.hero.json | 6e33a32d...78934 |
| sabres-nyr-nov25-finish.png | 199f6adf...1e8f2 |

## 2. Ledger paragraph vs. ledger/predictions.csv

P0023, `NHL_20262027_2026-11-25_NYR_at_BUF`, probability 0.49, created 2026-11-25T14:42:57Z, resolves 2026-11-26T00:00:00Z, model nhl-game-v0.1.
This is the only ledger row for this game.

- Story: "Sabres 49%, Rangers 51%". Logged probability 0.49. Matches.
- Story: "Logged ... at 2026-11-25 14:42:57 UTC". Matches `created_at_utc`.
- Before puck drop: 14:42:57 UTC is about 9h17m before 00:00 UTC Nov. 26. The generator asserts the schedule's start_utc is 2026-11-26T00:00:00Z.
- Story: "3.1 for Buffalo and 3.2 for New York, about a 16% chance ... tied after 60". Ledger notes say BUF 3.09, NYR 3.21, tie 0.162. Matches.
- The claim wording matches the logger script (`src/ledger/log_sabres_nyr_nov25.py`). The story doesn't print the id, and it doesn't need to.

## 3. Read-through of the current text

Internal consistency:
- Chance share 53% (9th) and 48% (22nd) match the stat-heads line: 0.527 (9) and 0.478 (22).
- Finishing: "about 8 fewer" and "30th of 32" match "only 2 teams have finished worse", "worth about 69 ... scored 61" and the stat-heads G - xG of -8.4.
- Saves: "about 7 more, 6th per game" matches xGA - GA +7.2 (6). The stat-heads line also gives the season-total rank of 7 and labels both ranks clearly.
- Net: -8.4 + 7.2 = -1.2 from the rounded figures, and the stat-heads line says -1.1. That's a rounding difference. The body says "about 8 missed, about 7 saved", which is consistent.
- Goalie table vs. the team figure: the Rangers rows add up to +10.1 while the team figure is +7.2. I checked this against the data. Two other Rangers goalies
  played one game each (-2.0 and -0.9). With them, the goalies total +7.25, which matches the team. The table is labeled "Goalies with three or more games." Sabres rows add up to -2.3 vs. team -2.4. Consistent.
- Split-half: about 12 below and about 2 below matches -11.9 -> -1.7. About 13 better and 5 better matches +13.4 -> +4.8. "Share kept" 14% and 35% are consistent.
  The cited Nov. 22 recap also says 96 team-seasons, "13 goals better than average to 5" and "about a third of it stuck". Consistent.
- Records: 10-10-4 = 24 points, 13-9-1 = 27 points, and the Rangers' 23 games match "16 of their 23 games". Nov. 22, 2026 is a Sunday and Nov. 25 is a Wednesday. Rest and last-season meetings are asserted in the generator.
- Hero JSON (49%/51%, 30th of 32) matches the body.

Links:
- `sabres-lightning-postgame-nov-22.html` is a registered ARTICLES slug in `src/site/build.py` (the Nov. 22 swing recap). Its relative path from `analysis/` is correct.
- `../ledger.html` is built by `build.py`.
- All six `../cards/<slug>.html` goalie links are in `card_slugs()` values: luukkonen, ellis, lyon, garand, shesterkin, korpisalo.
- The image `sabres-nyr-nov25-finish.png` exists.

Jargon and betting:
- The body has no xG, GSAx, PDO, Corsi or correlation. Stat terms appear only under "For the stat-heads". "Save %" in the goalie table is a standard fan term, and I'm leaving it.
- There's no betting language: no odds, lines, spreads, picks, locks, favorites or over/under. "Rates the Rangers a little ahead" is model language.

## Notes (not must-fix)

- The generator prints "before puck drop" whenever a ledger row exists. It doesn't compare `created_at_utc` with the start time. It's true here. A future
  generator could assert it.
- Publishing step still open: `sabres-nyr-nov25-finish.png` isn't in `reports/published_images.json` yet. Run
  `python3 scripts/freeze_images.py` and commit the manifest when publishing. Until then, `make test` will fail on the unfrozen image.
- Korpisalo (3 games, +2.8) and Lyon (4 games) are small samples. The table's 3-game floor is disclosed, and Quant passed it.
