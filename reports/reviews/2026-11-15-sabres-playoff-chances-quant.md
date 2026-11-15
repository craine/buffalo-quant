# Quant review (stage 2): Are the Sabres done? (2026-11-15-sabres-playoff-chances)

Reviewed: story md at sha d7c4eab6..., generator `src/reports/sabres_playoff_chances.py`, `src/metrics/nhl_playoffs.py`,
`src/ledger/log_sabres_playoffs.py`, Ledger row P0017, hero JSON, site dek, three charts. Branch nhl-schedule, commit 6d73089a.
DB: games through 2026-11-14 (325 played, 1,019 future in raw_nhl_schedule, 84 games a team). Nothing written to the Ledger.

## Verdict: publish with fixes (recorded as FAIL until fixes are in; stage 4 checks them)

The headline numbers hold up. An independent simulation (my own ratings from clean_nhl_shots_xg, my own season loop,
tiebreaks and playoff format; only the fitted model coefficients reused) gives 15.3-15.9% across seeds vs the story's 16.19%
(seed 7, at the high end of seed noise: the generator's own seeds 8/9/10 give 15.6/15.6/15.4%). 16% and "1-in-6" are fine.
Every table value re-derives exactly. The problems are attribution, overclaims and two internal-consistency errors.

## Required fixes (ranked)

1. **Wrong attribution: the extra chances against don't mostly come shorthanded.**
   Text: "At full strength, Buffalo is about even (50% of the chances). The extra chances against come while a man down"
   (also the lead "especially when they're shorthanded" and the bottom line "especially a man down").
   Evidence: BUF allows 3.254 vs league 2.960 a game, +0.294. Split by game state: 5v5 +0.049 (2.077 vs 2.028), shorthanded
   (opponent at 5v4/5v3/4v3) +0.124 (0.794 vs 0.670), all other states +0.121 (0.383 vs 0.263, **2nd-most in the NHL**:
   opponent shots at 4v5 while Buffalo is on the power play (26 shots), opponents' extra attacker 6v5 (23), 3v3 OT (15), 4v4 (14)).
   Shorthanded is 42% of the excess, not all of it.
   Fix: "About 40% of the extra chances against come while a man down, the 5th-most in the league; most of the rest come in
   odd situations (on their own power play, against an extra attacker, and in overtime)." Keep "especially shorthanded" only if
   it's framed as the largest single piece. Put the 0.049/0.124/0.121 split in stat-heads.

2. **Benson arithmetic doesn't add up.**
   Text: "**Zach Benson**: 2 goals on chances worth 7.3. That's about 6 of the team's 7 missing goals."
   Evidence: 7.3 - 2 = 5.3, not 6. One of his 2 goals was into an empty net (game 2026020198, 3rd period 19:05,
   situationCode 1560 = home net empty; xg null). The card's finishing (-6.3) uses his 1 non-empty-net goal against 7.34 xG
   (rescaled). The team's -7.2 also excludes empty-net goals. "About 6 of 7" is right; "2 goals" is the wrong count for it.
   Fix: "1 goal on chances worth 7.3 (plus an empty-netter). That's about 6 of the team's 7 missing goals." 13 assists checks.

3. **"Won't fix itself" contradicts the carry-over numbers and the model itself.**
   Text: "The part that won't fix itself is the chances they give up." Dek: "the chances they give up, especially shorthanded,
   won't on their own." Lead: "that kind of problem tends to stick."
   Evidence: chances allowed carry over 0.66, shorthanded 0.46. On average about a third of a chances-allowed gap and more than
   half of a shorthanded gap fades. The projection already assumes partial improvement: BUF's xGA rating is 3.190 vs its observed
   3.286 (unrescaled), i.e. the model regresses it.
   Fix: "The chances they give up are the part most likely to last" (body and dek); for shorthanded say "about half of that
   tends to last." "Tends to stick" in the lead is fine.

4. **Lead: "Fix it, and their chances roughly double" is only true for the overall fix.**
   "It" reads as "chances given up, especially shorthanded". The shorthanded fix gives 25% (1.5x, and see #5); only league-average
   chances allowed overall gives 32%. Fix: "Allow a league-average number of scoring chances and their playoff chance roughly
   doubles, to 32%." Also separate "scoring chances" from "playoff chance" in the lead and throughout.

5. **Shorthanded what-if is on a different scale from the overall what-if (overstates 25%).**
   Code: `sh_fix = B.sh_xga - L.sh_xga` (0.124, the raw observed 20-game gap, rescaled xG) is subtracted from the shrunk rating,
   while "all chances allowed" closes the shrunk rating gap (0.202 of an observed 0.294). On the same scale (shrink by
   20/(20+10)), the shorthanded fix is 0.083 and moves Buffalo to about 21% (my sim: 21.1%, 87 points), not 25%.
   Fix: apply the shrink (or state that it's the full observed gap applied to an already-regressed rating, and that it's
   therefore generous). Update table, chart, bullet ("worth about 0.12 goals a game") and stat-heads.

6. **Untraceable claim in stat-heads.** "Rating noise (sd) chosen on 2023-24 and 2024-25 (0 was best) and kept." No code in the
   repo tunes RATING_SD (grep finds only the constant 0.0). Brand rule 5. Fix: commit the tuning script/output or drop the claim.
   Relatedly, sd = 0 treats team strength as known, and the tails show it (next item).

7. **Calibration paragraph is mis-framed and misses the real warning.**
   Text: "One honest caution: of the 23 teams we gave between 5% and 30%, the model said 16% on average and 3 made it."
   Evidence: 3 of 23 = 13% vs 16% said: that bucket is *well* calibrated, so it isn't a caution. The real miss is the tail: in my
   backtest 11 teams were given under 5% (mean 1.4%) and **2 made it** (MTL 2024-25 at 1.9%, STL 2024-25 at 1.6%). Also the 30-70%
   bucket: said 51%, 40% made (25 teams). Small samples throughout.
   Fix: "Teams we gave 5-30%, like Buffalo now, made it 3 times in 23 (13%), close to what we said. Where we were too sure was the
   bottom: 2 of 11 teams we gave under 5% made it anyway." Label it as a small sample. Consider whether TOR 2%/PHI 1% need a note.

8. **Out-of-sample scorecard.** Brier 0.149 overall re-derives (mine 0.148; baseline 0.1975 exact), but by season it's 0.115,
   0.122, **0.208** (baseline 0.159, 0.188, 0.245). The model's coefficients were fit on the first two seasons; 2025-26 is the only
   fully fresh one. Fix: add one plain sentence: "On the one season the model hadn't seen, it scored 0.21 vs 0.25 for the
   standings-only guess." Keep per-season numbers in stat-heads.

9. **"Points pace (per 82)" and "Rating (per 82)" in an 84-game season.** Fix: per 84 (or per game), in the table, prose and stat-heads.

10. **Ledger P0017 resolves_at_utc says 2026-11-18T00:00:00Z** (the next game's puck drop), while the story, the logger docstring
    and the notes say it resolves after the last regular-season game (2027-04-10). `add_prediction` sets resolves_at_utc = kickoff.
    The site's Ledger page doesn't show the field, but the downloadable CSV does. Don't add a duplicate prediction row. Fix: give
    `add_prediction` a separate `resolves_at` for season-long calls going forward; when P0017 is graded, note the discrepancy in
    the grade row; optionally add one stat-heads line ("Ledger field resolves_at_utc records the cutoff game; the call resolves
    2027-04-10"). Flag to Charlie.

## Should fix (smaller)

11. Points chart title "The Sabres finish ahead of the line in about 16% of seasons": "the line" is undefined on its own and reads
    as betting language, and 16% is the qualify rate, not "ahead of the median cutoff". Fix: "The Sabres make the playoffs in about
    16% of 20,000 simulated seasons."
12. "It's a middle-of-the-pack team playing like one": BUF's share of all chances is 48.5%, **21st of 32**. Fix: "a slightly
    below-average team playing like one."
13. "That's why our projection already expects Buffalo's shooting and goaltending to be about average": the game model doesn't
    model finishing or goaltending at all; it assumes average. Fix: "Our projection assumes average shooting and goaltending from
    here, and history backs that up."
14. Goalie table has no league average or small-sample label. League save percentage on shots on goal (non-empty-net) is 89.1%.
    Alex Lyon's 55 shots needs a "small sample" note. Add the league-average row.
15. "-0.00" league-average cells: print "0.00".
16. "it usually takes about 94 points": that's the median of our simulations, not a historical norm. Fix: "in our simulations
    the last spot usually goes to about 94."
17. Last year's Sabres "13%": the backtest uses 4,000 sims; my independent run gave 11.8%. Say "about 1 in 8" or run the backtest
    at 20,000.
18. "finishing streaks like that rarely last" (Benson): team-level carry is 0.05; player-level finishing carry is 0.24 (skater cards
    meta, 673 pairs). Fine as "usually don't last"; "rarely" is a touch strong.

## Brand rules
- No betting language apart from #11 ("the line"). "Coin flip" is fine.
- Jargon stays in stat-heads. "Five-on-five" is glossed. OK.
- Labels: what-if rows and hero labels read on their own, apart from the "chances" ambiguity (#4).
- Small samples: the player table is labeled; the goalie table and calibration buckets aren't (#7, #14).

## What I verified (independently, from raw tables)
- Standings from raw_nhl_games: all 16 East rows (points, GP) exact; BUF 8-8-4, 20 pts, GF 55, GA 70. 2025-26 BUF 50-23-9, 109 pts,
  1.33/game. Total 1,344 games = 32x84/2; 325 played, 1,019 left. 64 BUF games left; 94-20 = 74, 74/64 = 1.16.
- Divisions from schedule pair counts: 112 pairs x4 (4 divisions x 28), 128 pairs x3, 256 pairs x2. Atlantic/Metro/Central/Pacific
  as expected; BUF's 4-game opponents are the 7 Atlantic teams. All schedule and games rows are game_type 2 (no playoffs mixed in).
- Simulation: independent re-implementation: BUF 15.3-15.9% (seeds), median 85, 10-90% 75-95, cut median 94 (90-97); every East
  team's chance within 1 pt and projected finish within 1. What-ifs: league defense 31.5%/90, +0.2 31.1%/89, both 51.5%/94,
  shorthanded (0.124) 24.6-25.1%/88. BUF ratings xGF 3.056, xGA 3.190, league 2.988 exact. p_ot 0.545 exact.
- Playoff format code: top 3 per division plus 2 wild cards per conference, points then RW then ROW then random. Correct.
- Backtest: cut dates 2023-11-26, 2024-11-23, 2025-11-20 exact; 96 team-seasons; Brier 0.148 (story 0.149), baseline 0.1975 exact;
  5-30% bucket 24 teams, 16.6%, 3 made (story 23/15.9%/3, seed noise). Ratings use only games before the cut date and the prior
  season: no leakage beyond the disclosed coefficient fit.
- Expected points from chances: Monte Carlo over BUF regulation shots, 20.72 (story 20.71).
- Team table (rescaled xG, factor 0.990): xGF 3.06 (10th), xGA 3.25 (6th-most), 5v5 share 50.3% (18th), SH xGA 0.79 (5th-most;
  league 0.67), SH GA 1.05 (3rd-most; 21 goals), finishing -0.36 (5th-worst; -7.2 total), goaltending -0.15 (11th-worst; -2.9 total).
- Carry-over (96 team-seasons): xGF 0.674, xGA 0.659, SH xGA 0.464, finishing 0.047, goaltending 0.010. All exact. Bootstrap 90%
  intervals: finishing -0.11 to 0.20, goaltending -0.14 to 0.17, SH 0.29 to 0.59.
- Players: G-A-P for Zucker, McLeod, Doan, Norris, Crevier from goal events, and the paces. Ratings are consistent with the
  committed Nov-10 cards (McLeod 43.4, Doan 42.2, Norris 45.2, Crevier 18.7); the rating model itself wasn't re-derived. Benson:
  2 G (1 empty net), 13 A, 7.34 xG, team's largest gap (next is -1.4).
- Goalies: Luukkonen 301 SOG, 40 GA, 86.7%, -3.2; Ellis 181/23/87.3%/-0.6; Lyon 55/5/90.9%/+0.8. All exact.
- Ledger: claim text and 16% match P0017; logged 2026-11-15 13:58 UTC, before BUF at PHI 2026-11-18 00:00 UTC; model version
  nhl-game-v0.1+playoff-sim; unrounded 0.1619 matches the generator's seed 7. Earlier stories (6th/5th-most chances allowed,
  Luukkonen -3.2) are consistent.
- Charts: all three opened. Footers have source and sample. Issues only in #11 and #4/#5.
