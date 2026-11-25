# Quant review (stage 2): 2026-11-25-sabres-nyr-pregame

**Verdict: FAIL (publish with fixes).** Every number in the body, table, chart, hero, card and stat-heads checks out against the raw
tables, and the generator reproduces the md, hero JSON and PNG byte-for-byte in a clean copy. The fail is one overclaim in the lead and
the "what lasts" paragraph: the Rangers' bad finishing (-8.4) and good goaltending (+7.2) nearly cancel (net -1.1 goals), so "better
than their goal totals look" and "a better team than its record" aren't supported. The supported claim is narrower: their scoring
should pick up, and their goaltending should cool off some.

Recomputed independently from raw_nhl_games, raw_nhl_schedule, raw_nhl_plays, raw_nhl_rosters and clean_nhl_shots_xg (read-only),
with my own grouping code. I did not call the writer's functions, except `nhl_game_model.train()` for the fitted coefficients. Ratings, expected goals and win chance were recomputed by hand.

## Must-fix

1. **Overclaim: "better than their goal totals look" / "better team than its record".**
   Evidence: NYR finishing (goals minus chance value, non-empty-net) -8.35; saves vs. average +7.25; **net -1.10**. Their goal
   difference is already about what their chances say. The split-half pattern keeps about 14% of first-half finishing
   (-11.94 -> -1.73) and about 35% of first-half saves (+13.45 -> +4.76). Applied to the Rangers' per-game rates, finishing moves from
   -0.36 to about -0.05 a game and saves from +0.32 to about +0.11. That nets to roughly +0.1 goal a game: more Rangers goals,
   partly offset by more goals against. No code compares the Rangers to their record. Their points percentage is 14th
   (27 points in 23 games) and their chance share is 9th, but the story never computes or argues that.
   - Lead: "Over the last three seasons, bad finishing hasn't lasted, so the Rangers are probably better than their goal totals look."
     -> "Over the last three seasons, bad finishing hasn't lasted, so the Rangers should score more than they have. Their goaltending
     will probably cool off some too."
   - Body: "If the Rangers follow that pattern, their shooting comes around and their goaltending stays good, just not this good. Over a
     season, that's a better team than its record."
     -> "If the Rangers follow that pattern, their shooting comes around and their goaltending stays good, just not this good. Right
     now the two nearly cancel out: about 8 goals missed, about 7 saved. Finishing is what tends to bounce back, so the bigger change
     from here is more Rangers goals."

## Should-fix

2. **Saves rank pairs a season total with a per-game rank.** "saving about 7 more than an average goalie would (6th)". Per game
   (+0.315) NYR is 6th. By season total (+7.25) they are 7th, behind MTL (+7.41 in 25 games). Someone who checks the totals would find 7th.
   -> "saving about 7 more than an average goalie would (6th per game)". Finishing (30th) and chance share (9th) rank the same either way.
3. **Empty-net consistency (disclosure).** Team finishing and Dorofeyev's "6 goals on chances worth about 9" leave out empty nets.
   Dorofeyev has no empty-net goals, so his 6 is also his official total. The player totals for Thompson (17, 0 empty-net) and Lafrenière
   (10, **2 empty-net**) are official totals that include empty nets. That's the right count for "leads the Rangers" and "5th in the NHL",
   and the claim holds either way: without empty nets Lafrenière has 8, and Bjorkstrand and Perreault have 7. Add to stat-heads:
   "Player goal totals are official, including empty-net goals (Lafrenière 2 of 10, Thompson 0 of 17)."

## Process notes (not story text)

- `reports/published_images.json` does not list `sabres-nyr-nov25-finish.png` yet. Run `python3 scripts/freeze_images.py` at publish.
- The Ledger paragraph is generated from `ledger/predictions.csv`. If the generator is re-run after the logger runs, the md text
  changes and the final-check hash breaks. Either run the logger before the final check and regenerate, or don't regenerate after logging.
- `win_prob(mu_home, mu_away, ...)`: the generator and logger both pass Buffalo (home) first. That's correct. With the arguments swapped, the
  result is 52.6%.

## Verified (my numbers)

- Data: 385 regular-season 2026-27 games through 2026-11-24, all OFF; schedule has 385 and none missing. Rescale 1.0015 (story 1.001).
- Records: BUF 10-10-4 (24 pts), home 4-6-0; NYR 13-9-1 (27 pts), road 4-6-1. No tied finals.
- Rest: both teams' last game 2026-11-22 (Sunday). Game 2026020387, NYR at BUF, start 2026-11-26T00:00Z = 7 p.m. ET.
- Last season: 3 meetings: 0-4 L at BUF (Oct 9), 5-2 W at NYR (Jan 8), 5-3 W at NYR (Apr 8). That's 2 of 3.
- Chance share: NYR 0.527 (9th; OTT .533, FLA .528 above, DAL .524 below); BUF 0.478 (22nd; EDM .482, ANA .477). No ties.
- Finishing per game: NYR -0.363 (30th; DET -0.629, CBJ -0.431 worse; LAK -0.353 next). Total -8.35 (also 30th). Chances worth 69.35; non-empty-net goals 61.
  BUF -0.086 (19th), total -2.07.
- Saves per game: NYR +0.315 (6th; NSH +0.305 7th). Total +7.25 (7th by total, see #2). BUF -0.098 (20th), total -2.35.
- Empty-net flag matches raw `goalieInNetId` null on all 2,429 non-shootout goals (136 empty-net); shootout goals (65) excluded; no
  goals on blocked shots.
- Goalies (unblocked, non-empty-net; 79 goalies; ranks by season total, method min, no ties at these ranks):
  Garand 16 appearances / **14 starts**, 90.9%, +2.35 (19th). Shesterkin 5 / 5, 92.7%, +5.02 (12th). Korpisalo 3 / 3, 94.0%, +2.79 (18th).
  Reimer 1 start (-1.98) and Martin 1 relief (-0.94) are left out of the table (fewer than 3 games). Starts sum to 23.
  Luukkonen 14 / 13, 87.8%, -0.51 (38th). Ellis 8 / 7, 87.3%, -0.30 (35th). Lyon 4 / 4, 89.0%, -1.54 (48th). "Games" means appearances,
  disclosed in stat-heads. "Played in 16 of their 23 games" is accurate. Both Garand and Shesterkin are above average: true.
  Raw `goalieInNetId` appearances match. NYR goalie total = team +7.25.
- Thompson 17 goals (raw plays agree), 5th alone (Draisaitl 23, Gauthier 22, Kaprizov/Connor 19). Lafrenière 10 (raw agrees).
- Dorofeyev: 6 goals on 9.03, gap -3.03, the team's largest (Laba -2.53 next).
- Split-half: 96 team-seasons, all 82 games. Bottom-quartile first-half finishing (n 24) -11.94 -> -1.73 ("2 below" rounds -1.7;
  "about 2 below" is more exact; 54% of them were still negative). Top-quartile saves (n 24) +13.45 -> +4.76 (62% still positive).
  First-to-second-half correlation: finishing 0.10, saves 0.22.
  "Finishing didn't carry over; goaltending partly did" is fair and matches the Nov 22 recap.
- Model (ratings re-implemented by hand): league chance value per team-game 2.974, scoring ratio 1.061. BUF off 2.992 / def 3.187;
  NYR off 2.953 / def 2.791 (10-game prior, half of last season's edge). Expected goals BUF 3.093, NYR 3.212. Tie after 60 minutes 16.2%; regulation
  ties go to the home team at 0.545. **P(BUF) = 0.4887 -> 49%.** Coefficients -0.2537, 1.0316, 0.2721. "Rates the Rangers a little ahead
  because they've gotten more of the chances": yes. Their edge is mostly fewer chances allowed (2.70 a game against 3.27 for Buffalo).
  "Doesn't count finishing or goaltending": yes, the inputs are chance values only.
  The logger uses the same inputs and `round(p,2)` = 0.49, model nhl-game-v0.1. Nothing is logged yet (0 rows for this game in the ledger CSVs).
- No betting language. Small samples: the goalie table uses 3+ games; Shesterkin's 5 is small but labeled by its game count.
- Reproducibility: fresh copy of repo + DB, deleted the three outputs, ran `python3 -m src.reports.sabres_pregame_nyr_nov25`:
  md, hero JSON and PNG byte-identical (md sha256 6c8c0af2...).
- Chart opened. Rangers at (-0.36, +0.32) in the "Don't finish, goalies bail them out" corner. Footer has source, 32 teams, 385 games.
