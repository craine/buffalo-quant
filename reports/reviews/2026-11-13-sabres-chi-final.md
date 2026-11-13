# Stage 4 final check: reports/2026-11-13-sabres-chi.md (sha256 f62d7b303111...)

**Verdict: PASS.** Every number in the body, tables, charts, hero JSON and dek matches my own scratch code (/tmp/fc/chk.py). That code reads data/buffalo.db read-only and doesn't call the generator. The edits made after stages 2 and 3 broke nothing.

## Re-derived (scratch code, games through 2026-11-12, xG rescaled per season, 2026-27 factor 0.9922)
- Game: CHI 3, BUF 2, OT (raw_nhl_games, last_period_type OT).
- Regulation chances: BUF 2.115, CHI 1.887, so 2.1 / 1.9. OT: CHI 0.370 on 3 shots, BUF 0 shots, so 0.4. Full game: BUF 2.11 on 35 shots (23 on goal), CHI 2.26 on 31 (25 on goal). Through two periods: 1.53 / 0.84.
- Period table: P1 0.771 (10) / 0.380 (8); P2 0.756 (16) / 0.462 (7); P3 0.588 (9) / 1.044 (13); OT 0 / 0.370 (3). All match. Shares: 67% in P1, 62% in P2, 36% in P3.
- Goal table: Power 9:00, slap shot, 36 ft, 9%. Nazar 12:22, wrist, 5 ft, 5v4, 23%. Thompson 15:46, wrist, 29 ft, 5v4, 7%. Nazar 8:22 of P3, tip-in, 16 ft, 8%. Donato OT 3:12, wrist, 32 ft, 3v3, 11%. The running score matches. "11:38 left" = 1200 - 502 s.
- Third-period stretch: BUF 0.231 on 3 shots, CHI 0.693 on 8, so a share of 25.0%. 38.1% of CHI's chances came at 5v4 or 4v4. BUF's 5v5 share was 0.35. League leader share is 0.467. 31.5% of 2,319 leaders (in 2,250 games) got 25% or less. After the tie it was 0.357 / 0.351, which is even.
- Tired/rested shares by period: tired (644 games) 0.457 / 0.470 / 0.482; rested (3,107 games) 0.478 / 0.485 / 0.488. Gaps -2.1 / -1.5 / -0.6 pts. My bootstrap (different seed) gives -3.6 to -0.7, -3.0 to -0.0 and -2.1 to +0.8, which agree with the published ranges within resampling noise.
- Replays (exact convolution): win 0.438, tie 0.215, loss 0.347, so 44 / 21 / 35.
- Goalies: Lyon faced 25 shots on goal, 2.256 xGA, 3 GA, so -0.74 ("0.7 more"). Knight faced 23 shots on goal and allowed 2 (21 of 23), +0.11. This was Lyon's first game of 2026-27. Luukkonen and Ellis both played in the 8-3 loss to TBL on Nov 11.
- Pregame carry-overs: 37% and 0.06 match the pregame story (lines 57-58). The model's 3.45 / 2.97 match P0010's notes.
- Ledger: P0010 has p 0.57, outcome 0, Brier 0.3249 (0.32). A 50/50 guess scores 0.25. The record over 10 graded calls is 7 of 10 (P0004, P0006 and P0010 were misses).
- Hero bars: tired road teams won 0.3826 (643 games before Nov 12) and rested road teams 0.4676, so 0.383 / 0.468. The dek is consistent with the story.

## Charts (looked at both)
- Flow chart: the title and subtitle (2.1/1.9, 2.1/2.3) are correct. The subtitle now includes "black = Chicago's", so the stage-3 nit is resolved. The footer has the source and the shot counts.
- Periods chart: the bars are 48/46/67, 48/47/62 and 49/48/36, which match. The legend shows 3,107 / 644. The footer has the source and date range.

## Brand rules
- No betting language.
- No jargon in the body (xG/GSAx/Poisson appear only in "For the stat-heads").
- The one-game sample is labeled repeatedly.
- No uncomputed numbers found.

No required fixes.
