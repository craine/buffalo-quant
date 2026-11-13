# Quant review: reports/2026-11-13-sabres-chi.md (CHI 3, BUF 2 OT, Nov 12, 2026)

**Verdict: FAIL (publish with fixes).** The game numbers are all correct. The lede's league comparison (42%) is not like-for-like, and the tired-legs section overstates what a by-period split can show.

Scratch code (read-only DB, rescaled per season, factor 2026-27 = 0.9922): /tmp/qchk/a.py, b.py, c.py, d.py.

## Required fixes, most important first

1. **"teams up a goal in the third usually get 42%" (Finding, The third period, hero note context, dek wording "with the lead").**
   0.417 (2,841 games) reproduces exactly, but it pools the whole third, including late extra-attacker time when the trailing team pulls its goalie.
   Those 6-on-5 shots count for the trailing team, and the leader's empty-net shots are dropped. Buffalo's stretch (40:00 to 48:22) had no pulled goalie.
   Like-for-like numbers:
   - Up one, 3rd period, excluding 6vX: **0.460**
   - Up one, first 8:22 of the 3rd (the same window as Buffalo's): **0.467**
   - Up one, 5v5 only, first 8:22: 0.470

   Fix: compare to about 47% ("teams up a goal early in the third usually get about 47%"), and define it in the stat-heads section.

2. **"Buffalo sat back further than that" / headline "sat on a lead it couldn't keep": overclaim.**
   - Part of Chicago's 0.69 came on special teams. Chicago 5v4: 0.14 (2 shots). 4v4: 0.12 (1 shot). Chicago 5v5: 0.43 (4 shots, including the tying goal).
   - At 5v5, Buffalo's share in the stretch was **35%**, not 25%.
   - Per game, 30.5% of teams leading by one in the first 8:22 of the 3rd got 25% or less in that window (2,251 games; median 46%). So 25% is ordinary for one stretch.

   Fix: mention the Chicago power play at the start of the third. Drop "sat back further than that" and "sat on", or soften them to "got out-chanced". Keep the existing one-stretch caveat.
   (Don't publish a penalty count; the CLAUDE.md caveat on penalty attribution applies. Strength states from situationCode are fine to cite.)

3. **Tired-legs section.** These numbers reproduce: tired P1/P2/P3 0.457/0.470/0.482, rested 0.478/0.485/0.488, 644 / 3,107 games. Three of its claims go beyond them:
   - **"by the third they've nearly caught up" is largely a score effect.** Tired road teams trail more in the third: 49% of their third-period shots come while trailing, vs 43% for rested teams. Trailing teams get more of the chances.
     Counting tied-score shots only: tired 0.442/0.474/0.462, rested 0.478/0.490/0.486. In the third the gap is still 2.3 pts (bootstrap 95% CI -5.6 to +1.0, 275 games), about the same as the first period's.
     Fix: drop "nearly caught up". "They don't fade late" is supported (no drop in the third even at tied scores), so keep it.
   - **"furthest behind in the first period" (body, chart title, hero kicker/title "trail most early, not late") is noise-level.**
     Game-level bootstrap gaps (tired minus rested): P1 -2.1 pts (CI -3.4 to -0.7), P2 -1.5 (CI -3.0 to -0.1), P3 -0.6 (CI -2.0 to +0.9). P1 and P2 can't be told apart.
     Fix: "Tired road teams are a little behind all game; they don't fade late." Retitle the chart and the hero explainer to match. The P1 bars can stay as the example.
   - **"The score explains Thursday's third period better than the schedule does" isn't supported.** Score effects take an early-third leader from about 50% to about 47%. Neither score nor schedule explains 25%; a Chicago power play plus one-stretch noise does more.
     Fix: "Neither the schedule nor the score explains much of it: part was a Chicago power play, and the rest is one stretch of one game."

4. **"The model expected chances worth 3.45 goals for Buffalo and 2.97 for Chicago; the game came in well below both, at 2.1 and 2.3."**
   The 3.45/2.97 match P0010's notes. But they are the model's *expected goals* (the pregame story says "expects about 3.5 goals"; goals = -0.254 + 1.032 x expected + 0.272 x home, on the unrescaled scale). They are not chance values.
   The 2.1/2.3 also include overtime (Chicago 0.37), while the model forecasts 60 minutes.
   Fix: "The model expected about 3.5 goals for Buffalo and 3.0 for Chicago. Through 60 minutes the chances were worth 2.1 and 1.9, and the score was 2-2." (Regulation chances: BUF 2.115, CHI 1.886.) Or drop the comparison.

5. **"Next up: Saturday at Dallas."** No query supports it; raw_nhl_games ends 2026-11-12. Verify it from a committed source or cut it.

## Verified (all match)

- **Per period** (xG, unblocked non-empty-net shots):

  | Period | BUF | CHI |
  |---|---|---|
  | 1st | 0.771 (10) | 0.380 (8) |
  | 2nd | 0.756 (16) | 0.462 (7) |
  | 3rd | 0.588 (9) | 1.044 (13) |
  | OT | 0 (0) | 0.370 (3) |
  | Game | 2.115 (35, 23 on goal) | 2.256 (31, 25 on goal) |

  No empty-net shots in the game.
- **Through two periods:** 1.527 vs 0.842, so the hero's 1.5 / 0.8 is correct.
- **Goals:** Power 9:00 slap 36 ft 5v5 8.8%; Nazar 12:22 wrist 5 ft 5v4 22.9%; Thompson 15:46 wrist 29 ft 5v4 6.7%; Nazar 3rd 8:22 tip-in 16 ft 5v5 7.7%; Donato OT 3:12 wrist 32 ft 3v3 11.5%. Scores are correct.
- **Clock:** "11:38 left" is correct. Final CHI 3-2 OT (raw_nhl_games, OFF).
- **Lead stretch:** BUF 3 shots, 0.231; CHI 8 shots, 0.693, which includes the tying shot at 48:22 (taken while trailing, so its inclusion is defensible). That makes 25%.
- **After the tie in the 3rd:** 0.357 vs 0.351. OT: Chicago 3 shots.
- **Replays** (exact Poisson-binomial, plus a 200k Monte Carlo check): win 0.438, tie 0.215, loss 0.347. Rounds to 44/21/35.
- **Road share by period:** Buffalo 67% in the 1st, 62% in the 2nd, 36% in the 3rd. BUF rest = 1 day, CHI rest = 5.
- **Goalies:** Lyon (8479312) faced 2.256 xG, allowed 3, -0.74 (25 on goal); his only 2026-27 roster appearance is this game. Knight 21 of 23, +0.115.
  Luukkonen and Ellis both played vs TBL on Nov 11 (TBL 8, BUF 3); this season they have 12 and 8 games.
- **Chicago creates the fewest chances:** 2.22 xGF per game this season, lowest in the league.
- **Ledger:** P0010 p 0.57, outcome 0, Brier 0.3249, so 0.32 is correct. The 7 of 10 record reproduces (P0001-P0010, NFL and NHL combined, hits at p >= 0.5).
  Story wording matches the logger claim. Model nhl-game-v0.1. No betting language found.
- **Charts:** both looked at. Labels are clean, and footers carry source and sample size. The periods chart title carries issue 3.
