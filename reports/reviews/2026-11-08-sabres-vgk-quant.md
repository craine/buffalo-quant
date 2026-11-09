# Quant review, stage 2: Sabres post-game, VGK 4 BUF 1 (2026-11-08)
(Copied from the reviewer's report. The review ran before the gate existed, on commit fe2de20.)

Verdict: publish with fixes. Every number re-derived independently from raw_nhl_plays, raw_nhl_games and clean_nhl_shots_xg.
Re-running the generator reproduces the outputs exactly.

Issues, all fixed in commit 62fccac:
1. False claim that the goalie cards blend in last season (gsax is this season only); the -1.8 vs -1.9 gap comes from the season rescale factor.
2. "The power play is still empty" is false for the season (8 PP goals); limited to Sunday.
3. "Process held up" overstated and jargon. Replaced with the five-on-five (3.19-1.84) vs special-teams (0.72-1.81) split.
4. 1.04 of Vegas's 3.65 came in the final 69 seconds at 4-1. Now disclosed.
5. Goalie paragraph misstated the test (split-half, not "a dozen games") and overclaimed. Restated; "Neither can anyone else" cut.
6. Hero save-rate bars undercut the text. Switched to goals saved.
7. The blocked-shots sentence mixed shot counts and chance value. Fixed, with the attempt average and block shares computed.
8. Goalie season numbers lacked sample sizes. Added; "headed opposite directions" changed to "at opposite ends".
9. Ledger framing: accurate. Dropped "only"; one game can't show an edge; noted near coin flip; replay 46% is not the pregame 46%; ledger page note.
10. Charts: dot colors explained; Ellis label moved.

Verified: chances 3.91/3.65 on 50/41 unblocked shots; replays 46/16/38 (200k re-run 0.461/0.159/0.379); goals, distances and chances;
Marner shorthanded (situationCode 1451); goalie assignment (Hill faced all 50, Ellis all 41); Hill +2.91 (13th of 586); season before/after;
28 blocked (7 of 556); Vegas allowed 2.60 (4th); Buffalo created 3.09; no penalty counts; no betting content; P0001 Brier 0.2116.
