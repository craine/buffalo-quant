# Final check: 2026-11-21-sabres-fla-pregame (stage 4, after the "three keys" rebuild)

Text checked: md sha256 89a42f80f40e1aa17d7765846317c404e6d1d519b7ec73bd3c66f74c29e2ff52, hero JSON, card, three PNGs. Earlier final: -final-r2.md.

**Passes.**

Changed lines since round 3 (md lines 1, 3, 12, 16, 19, 29, 32, 36, 38, 86, 90; hero big[1] label; card dek), each checked against my independent
numbers in -quant-r3.md and the round-4 quant report: 59% (134) / 25% (28); 5 of 13, CHI and VAN lower, 4 OT losses; 6 of 12 / 3 of 10; scoreless-game
note. No other numbers or claims were touched. No new claims, betting words or jargon. Clean-copy run of `src/reports/sabres_pregame_fla.py` reproduces
the md, hero and all three PNGs byte-identically. Ledger logger unchanged (0.37, nhl-game-v0.1, ratings before 2026-11-20); it must be run, with
Charlie's go-ahead, before 23:00 UTC Nov. 21.
