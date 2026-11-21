# Quant review: 2026-11-21-sabres-fla-pregame (stage 2, round 3, full re-review of the "three keys" rebuild)

Text: md sha256 ecd446b9..., hero JSON, card (src/site/build.py), sabres-fla-keys.png, sabres-fla-special.png, sabres-fla-model-test.png.
Earlier rounds: -quant-r1.md, -quant-r2.md. The generator reproduces md, hero and all three PNGs byte-identically in a clean copy;
special and model-test PNGs are unchanged from round 2.

**Verdict: publish with fixes (recorded as fail).** Every number is right. The framing claims necessity the data doesn't support,
one superlative is unsupported, and two Buffalo records are written in a way that hides overtime losses.

## Independent method for the keys
Goals from `raw_nhl_plays` (typeDescKey = goal, shootouts excluded), ordered by period, time, sortOrder; team from eventOwnerTeamId;
strength from situationCode on the scorer's side. Goal totals match every final score (4,294 games, shootouts handled) and match
clean_nhl_shots_xg (26,316 goals, 5,181 at 5v4/5v3/4v3). 5v5 chances: unblocked non-empty-net 5v5 shots, rescaled per season. No 5v5 ties.
Five games were 0-0 through overtime (decided in a shootout); those 10 team-games count as "didn't score first".

## Issues, ranked

1. **Necessity / causal framing.** Headline "three things Buffalo has to do to win in Florida", lead "To beat Florida, the Sabres need three
   things", "**Buffalo needs:**" under each key, and "But they're where this game will be decided." The data says these go with winning:
   teams that hit none of the three still won 13.3% (323 team-games); teams that allowed 2+ power-play goals won 25%; Buffalo won 2 of its
   5 games this season with 2+ allowed. The story's own line "better teams tend to do all three" contradicts "has to".
   Fix: headline "Sabres at Panthers: three keys for Buffalo in Florida"; lead "Three things go with winning, and they're our keys for Saturday."
   (replacing "To beat Florida, the Sabres need three things."); "**Buffalo needs:**" -> "**What to watch:**" (all three); "But they're where
   this game will be decided." -> "But they're what to watch on Saturday."

2. **"That's the strangest number on the Sabres' season, and it's a small sample."** No code supports "strangest". What is supported: Buffalo
   has won 5 of 13 when scoring first (38%), 3rd-lowest in the NHL (Chicago 2 of 9, Vancouver 3 of 9); 4 of the other 8 were overtime losses.
   Fix (writer computes the rank and the OT losses): "Only Chicago and Vancouver have won a smaller share of the games they scored first,
   though 4 of Buffalo's other 8 went to overtime. It's a small sample."

3. **"Buffalo is 6-6 in the 12 games it's done that this season, and 3-7 when it hasn't."** Correct as wins vs. non-wins, but hockey readers
   read 6-6 as a W-L record, and the "losses" include 1 and 3 overtime losses (the dek uses 9-9-4). Small samples unlabeled.
   Fix: "Buffalo has won 6 of the 12 games it's done that this season, and 3 of the 10 when it hasn't. Small samples, but the gap is there."
   (Or just "...and 3 of the 10 when it hasn't (small samples).")

4. **"Over a season that tells us which keys really matter for this team."** One team's season can't show which keys cause wins (the
   stat-heads note says "descriptive, not causal"). Fix: "Over a season, that will show how often Buffalo wins when it hits each one."

## Verified (my numbers)
- Keys, 8,588 team-games (4,294 games, 2023-24 through Nov. 19): PP goals allowed 0: 59.22% (4,608); 1: 43.95% (2,985); 2+: 25.43% (995).
  Scored first 66.59% (4,289) / didn't 33.45% (4,299). 5v5 chances more 59.66% (4,294) / fewer 40.34%. All three hit: 78.3% (2,057).
- Buffalo since 2023-24: 0 allowed 58.96% (134 games); 2+ 25.0% (28). This season: 2+ allowed in 5 games (won 2); 0 in 6, 1 in 11.
- Buffalo 2026-27 scored first 13, won 5 (4 OT losses); Florida scored first 10, won 8. 5v5 more: 12 games, 6 W (1 OTL); fewer: 10, 3 W (3 OTL).
- 5v5 share BUF 49.81% (19th), FLA 50.99% (15th).
- Thursday: Buffalo PP goals 2 (both 5v4, periods 1 and 2), Thompson one of them; Washington 1.
- Unchanged from round 2 and re-confirmed: records 9-9-4 (22) / 12-8-3 (27); PP 1.05 most / 0.81 4th-most / league 0.66; PP goals 22 in 23
  and 22 allowed in 22; Reinhart 12 and about 11 (11.25); Tkachuk 11, Ottawa through 2025-26; Thompson 14, 6th; Oct. 12 5-3, 3.4 vs 3.5,
  2 PP goals each; rest 3 and 1 days; game 5 of 6; goalie table; 13.8% / 0.8%; model 37% (0.3735), 2.8 vs 3.6, tie 15%; ratings 3.00/3.19/
  3.11/2.83; OT 55%; caution 54.9/52.2 (1,312) and 54.4/52.2 (358); backtest 55% / 52% / 60% (358) / 62% (231); Brier values.
- Hero 25% = 2+ PP goals allowed win rate. Card dek 37% matches. Ledger logger unchanged (0.37).
- Brand: no betting language ("covers" is "the chart covers"). No jargon in the body. Keys chart reads on its own, title not causal.
