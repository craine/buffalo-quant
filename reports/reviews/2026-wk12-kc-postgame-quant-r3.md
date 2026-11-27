# Quant review, round 3: 2026-wk12-kc-postgame (stage 2, full review of the reframed story)

**Verdict: don't publish as is (FAIL).** Story sha256 7c3c4cbecc17a9cb733fefa6143406441db3d18a143ac5ecbd460a3d29e6ecb1, commit ad9bb606.
Round-2 report: -quant-r2.md. Re-derived with my own SQL against data/buffalo.db (fingerprint confirmed).

## Must-fix

1. **"Since 1999" claims actually cover 2018 on.** `raw_pbp` holds 2018-2026 only (9,318 field-goal attempts, min season 2018). The
   generator's `season >= 1999` filters on both the field-goal and carries queries are no-ops. 1999-2017 is in `raw_pbp_history`, which
   has no kick columns (no kick_distance, field_goal_result, kicker).

2. **Cook: "the only 2 games since 1999" is false, and so is the hero's "tied for the most by a Bill since 1999".**
   From `raw_pbp_history` (Bills, rush = 1, no no-plays or kneels), Bills games with 32+ carries, 1999-2017:
   McGahee 37 (2004_09_NYJ_BUF, confirmed by name), T. Henry 35 (2002_13_MIA_BUF), F. Jackson 33 (2009_17_IND_BUF),
   T. Henry 32 (2003_14_NYJ_BUF), L. McCoy 32 (2017_14_IND_BUF). So since 1999 there are 7 such games, and the most is 37.
   Since 2018, Cook's 2 games are the only ones (next-highest is Cook's 31 at MIN in 2026).
   - Replace `Those are the only 2 games since 1999 in which any Bill has carried 32 times.`
     with `Those are the only 2 games since 2018 in which any Bill has carried 32 times.` (or compute the 1999-on figures from raw_pbp_history and say so).
   - Hero: replace `James Cook carries, tied for the most by a Bill since 1999` with `James Cook carries, tied for the most by a Bill since 2018`.
   - Stat-heads: `Bills games with a 32+ carry rusher since 1999: 2` -> `since 2018: 2`.
   - Generator: point the 1999-2017 part at raw_pbp_history, or drop the 1999 wording. Assert the window.

3. **Late long field goals: the window is 2018 on, and "tied or won" doesn't match the definition.**
   - Window: the 11 kicks are 2018-2026 (the earliest is Gano, 2018_05_NYG_CAR). Nothing before 2018 can be checked here, because raw_pbp_history has no kick distance.
   - Definition: you count kicks made with the kicking team tied or down 1-2. Every such make puts the team ahead, and in all 11 the kicking
     team won (checked against raw_schedules). Tying kicks (down 3) are *excluded*: there are 2 (Ryland 58, 2024_16_ARI_CAR; Aubrey 64,
     2025_02_NYG_DAL). So none of the 11 "tied" a game.
   - Replace `Since 1999, there have been 11 field goals of 57 yards or more that tied\nor won a game in its last 10 seconds.`
     with `Since 2018, there have been 11 field goals of 57 yards or more that won a game in its last 10 seconds.`
   - Stat-heads: change `every attempt in nflverse since 1999` to `every attempt in nflverse, 2018 on`, and describe "late" as a
     go-ahead make (tied or down 1-2) with 10 seconds or fewer left.
   - "No other kicker has more than one" holds (the other 9 kickers have 1 each). If you choose to count tying kicks too, it's 13, and Bass still leads with 2.

4. **The chart image changed after it was frozen.** `reports/published_images.json` still has the round-2 hash (b3c448bc...). The new PNG is
   14af66b7..., so `tests/test_published_images.py` fails now (I ran it). Per CLAUDE.md, a new chart gets a new file name, e.g. `bills-kc-wk12-postgame-wp.png`.
   Unfreeze or replace the old entry with `freeze_images.py --change ... --reason` before re-freezing.

## Should-fix

5. **Summing win-chance changes is fair as accounting, but the story has to say what the pieces add up to.**
   Buffalo's swings sum to +45: 55% before kickoff (nflverse `wp`) to 100% at the end. That breaks down as kicking +63.6, runs +20.0,
   passing -36.2 and penalty no-plays -2.7. A fan seeing +64 will ask how a chance can rise 64 points.
   Add a sentence, after the writer computes 55 and the penalty share:
   `Buffalo started at a 55% chance and finished at 100%; the swings on every play add up to that 45-point gain.`
   Caveats for stat-heads:
   - The credit goes to whoever was on the field when the swing happened. The 57-yarder gets +24, but the punt return before it gets +22.
   - The "kicking game" nets both teams' kicks. It includes Butker's miss (+6.5) and the Araiza fumble (+4.2). It even
     counts Butker's 26-yard make at the end of the half as +5.7 for Buffalo, because settling for 3 there lowered KC's chance. It subtracts two Doman punts (-9.6, -6.1).
   - So "the kicking game and returns added about 64 points" is both teams' kicking plays, not "the Bills' special teams". Say "the kicks,
     punts and returns, both teams'" once in the body.
6. **"Percentage points" is accurate. "+64 points of win chance" in the body and "64 points" in the hero can be read as scoreboard points.**
   Use "percentage points" everywhere: in the body replace `about **+64 points** of win chance` with `about **+64 percentage points** of win chance`,
   and in the hero replace `added about 64 points to Buffalo's chance to win` with `added about 64 percentage points to Buffalo's chance to win`.
7. **"Kansas City's punt unit had a bad day"** overstates the Dortch play. It was a 45-yard punt from the KC 11 with a 17-yard return. Its
   value (+22) came from field position, because it put Bass in range. Suggest: `and with 15 seconds left Greg Dortch returned a punt 17 yards to the Kansas City 39, putting Bass in range.`
   Keep "bad day" only for the fumble.
8. **Araiza's "13-yard punt":** kick_distance is 13, but that is net from the line of scrimmage (KC 31 to KC 44). After the fumble he punted
   from the KC 19. That wording is acceptable. "A punt that netted 13 yards" is more exact.
9. **Orphan stat-heads line:** the Mahomes 137 line no longer has a body claim. Remove it, or restore the claim.
10. **Site dek** in src/site/build.py still carries the Allen framing. It's accurate, but it no longer matches the story. Update it, and have the Quant re-check it.

## Verified (mine)

| Claim | Mine |
|---|---|
| Kicking / runs / passing / INTs (wpa, BUF side) | +63.6 / +20.0 / -36.2 / -33.1. Passing includes sacks -11.1 and scrambles +8.3; penalties -2.7; total +44.8 |
| 57+ made 60%, 205 tries, 2023-2026 Wk 12 | 0.595 on 205 (203 REG; blocked counted as misses) |
| 11 late 57+ makes, Bass 2 (61 vs MIA 2024_09, 10 s), none other >1 | Yes, **2018 on**, and all were winning kicks (must-fix 3) |
| Bass's 2nd career game with two 54+ makes | 2020_10_BUF_ARI (3) and this game; his data starts 2020, so full career |
| Cook 32 ties career high (2025_13_BUF_PIT) | Yes (playoffs included) |
| Only 2 Bills 32-carry games since 1999 | **False**: 7, max 37 (must-fix 2); true since 2018 |
| Cook success 56%, league designed runs 43% | 18/32 = 56.25%; 2026 Wk 1-12 designed runs 0.4276 (8,115 runs) |
| Araiza fumble, 13-yard punt, Q2 | Q2 12:25; kick_distance 13 (net, see 8) |
| Dortch 17 to KC 39, 15 s | (:15) Q4, return 17, to KC 39 |
| Butker miss 46, 6:01, tied | Yes, 10-10 |
| Bass 54 tied 10-10, Q4 12:03 | Yes |
| Bass 57, 4 s, tied before | Yes |
| Unchanged sections (Allen, run share, rain, part 3, Receipts) | As in round 2 |

## Chart
Labels are accurate. Dots: fumble 79.6%, 54-yarder about 52%, miss about 59%, Dortch about 76%, 57-yarder 100%. Text labels don't overlap,
but the Butker and Dortch leader lines cross each other and the curve. Move "Butker misses from 46" above the line (e.g. near 0.75 at x 50)
so the leaders don't cross. The line starts at a hard-coded 50% at kickoff (`np.r_[0.5, ...]`); the model's pregame chance was 55%.
Start it at the first play's `wp` (from Buffalo's side) or drop the added point. "Blue dots: Bills kicking plays" includes the Dortch return,
so call them "Bills kicks and returns". Footer has source and sample size. No betting: `home_wp_post` is the non-betting model.

Reproduction: a clean `git archive HEAD` with data symlinked reproduces md, PNG and hero byte-for-byte (informational only; final not run).
