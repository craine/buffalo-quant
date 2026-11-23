# Quant review: reports/2026-wk11-lab.md (stage 2)

Reviewer: independent Quant. Date: 2026-11-22. Story sha256 at review: 0b3c3eaff56e4112372dbcc9046051adbcfe8353d1c788065caf2ff924e023f6

**Verdict: FAIL (publish with fixes).** All seven headline numbers reproduce from raw_pbp with my own queries, and the
zero-run claim holds under the strictest definition. The failures are definitions and wording: the "135 games" count
needs its qualifier, the fake-punt distance is the gain and not the throw, the touchdown is pinned on the wrong lineman,
the stat-heads note on kneel-downs is wrong, the hero claims intent ("fake onside look"), and one literal number is
typed into the generator.

Reproduction: copied the repo to a clean directory, deleted the three outputs, ran `python3 -m src.reports.bills_lab_wk11`.
The md, hero JSON and PNG all came out byte-identical (same SHA-256).

## Must fix (ranked)

1. **"135 games" needs its qualifier (lead, section 1, hero, site card).** Allen played in 136 Bills regular-season games
   from 2018 through week 11 of 2026. The 135 are the games where he was passer or rusher on 20+ plays. The one left out,
   2019_17_NYJ_BUF (5 plays), *also* had zero runs. So "his 135 regular-season games" and "In every one of those games
   before Sunday, he ran at least once" are only true with the 20-play filter. The 135 set is not "starts" either: it
   includes 2018 week 1 (relief of Peterman, 22 plays) and leaves out the 2019 finale he started.
   - Lead: "For the first time in 135 regular-season games since 2018, Josh Allen didn't run the ball once against Miami"
     -> "For the first time in 135 regular-season games since 2018 where he played more than a handful of plays, Josh Allen didn't run the ball once against Miami"
   - Section 1: "It's the first time it's happened in any of his\n135 regular-season games with Buffalo since 2018."
     -> "That had never happened in any of his 135 regular-season games since 2018 where he played more than a handful of plays."
   - Hero: "Allen's regular-season games since 2018. This is the first with no runs."
     -> "Allen's regular-season games since 2018 with more than a handful of plays. First with no runs."
   - Card: "For the first time in 135 regular-season games, Josh Allen didn't run once."
     -> "For the first time in 135 regular-season games where he played more than a handful of plays, Josh Allen didn't run once."
2. **Fake punt: 30 yards is the gain, not the throw.** air_yards = 27, yards_gained = 30 (play 549).
   "punter Tommy Doman Jr. threw 30 yards to tight end Keleki Latu for a first down"
   -> "punter Tommy Doman Jr. threw to tight end Keleki Latu for a 30-yard gain and a first down"
3. **Touchdown attributed to the wrong lineman.** The four plays: 138 Corbett (4th-and-1), 854 Grable, 1419 Grable,
   1707 Corbett (Cook 1-yard TD). The sentence hangs the touchdown on Grable.
   "Corbett twice and Tylan Grable twice, including on Cook's 1-yard touchdown."
   -> "Tylan Grable twice and Corbett twice, including on Cook's 1-yard touchdown."
4. **Stat-heads kneel line is wrong.** In this data a kneel is `play_type = 'qb_kneel'` with `rush = 0`, so the season
   table and chart (filter `rush == 1 or pass == 1`) leave kneels out, while the career query (any `rusher_player_id`)
   counts them. And the Bills did kneel in this game: backup Kyle Allen (00-0034577) at 0:20 of Q4. Neither change
   moves a number: with kneels and two-point runs removed from the career count, the only 20+ play game with zero runs
   is still this one, the fewest before was 1 (six games), and the 2026 average is still 6.2.
   "(designed runs and scrambles; kneels count as runs in nflverse, and there were none)"
   -> "(designed runs and scrambles, not kneel-downs; Josh Allen had none, and backup Kyle Allen took the final kneel)"
   The generator should also use one definition for both queries (exclude `qb_kneel` and `two_point_attempt` in the career query).
5. **Hero claims intent.** "a fake onside look": the data shows an onside-kick formation, a delay of game, then a deep
   kick. Nothing shows it was a fake.
   "A fake punt, a fake onside look, four extra-lineman plays and the most shotgun of the season."
   -> "A fake punt, an onside-kick formation with a 14-point lead, four extra-lineman plays and the most shotgun of the season."
6. **"Than ever" overclaims.** Only 2026 was checked.
   - Header: "## 5. More extra linemen than ever" -> "## 5. More extra linemen than in any game this season"
   - Lead: "put an extra lineman on the field more than in any other game" -> "put an extra lineman on the field more than in any other game this season"
7. **"What it means" gets the order of events wrong.** "A blowout win against a struggling division rival is the natural
   place to try a fake". The fake came at 3-0 in the first quarter, and Allen's no-run day started on the first drive, so it
   wasn't a blowout yet. Miami was 1-9 (raw_schedules), so "struggling" holds.
   "A blowout win against a struggling division rival is the natural place to try a fake"
   -> "A home game against a struggling division rival is a natural place to try a fake"
8. **Literal number in the generator (brand rule 5).** "then went deep only twice the rest of the game": "twice" is
   typed, not computed. It is correct (my query gives 2 throws of 20+ air yards after Q1, matching the recap's "just
   twice in 34 passes"), but compute it and assert it. The same goes for "for 2 yards" (Cook, 4th-and-1), "1-yard
   touchdown", "own 34", "23-9", "5-yard" and "26-9". I checked each one against raw_pbp and all are correct. They
   should still be derived, or at least asserted, in code.
9. **Chart footer has no sample size** (house chart rule and self-check). Add it to the footer, e.g. "10 games; 78 Bills pass
   and run plays vs. Miami". This changes the PNG, so re-freeze at publish.

## Verified (my own queries on data/buffalo.db)

| Claim | Story | Mine | Notes |
|---|---|---|---|
| Allen runs vs MIA | 0 | 0 | No `rusher_player_id` = Allen. No scramble, kneel, 2-pt try, no-play run, or aborted snap for Allen in desc. Only Allen-named runs are K.Allen (MIA kick returner) and Kyle Allen's kneel |
| First zero-run game | first in 135 | holds | Strict definition (designed runs excl. 2-pt + scrambles, no kneels): only 2026_11 among 20+ play games; min before = 1 (6 games) |
| 2026 avg first nine | 6 (hero 6.2) | 6.22 | 5,11,7,5,10,2,7,5,4 |
| 4th-and-1 before wk 11 | Allen 6 of 9 | 6 of 9 | down 4, ydstogo ≤1, run/pass, no punt formation, no no-plays. The other 3: Cook run, 2 Allen passes. Includes one 4th-and-goal at the 1 (wk 8 Allen TD) |
| 4th-and-1 play | Cook, Corbett eligible, 2 yds, opening drive, near midfield | yes | play 138, BUF 48 to 50 |
| Fake punt | Doman to Latu, 4th-and-8, own 34, 3-0, Q1, first down | yes, but 27 air yds / 30 gain | play 549; Doman = P, Latu = TE in raw_players |
| Bills' first fake punt of 2026 | yes | yes | Only other BUF punt-formation play was a wk 9 false start |
| Teams with a fake punt | 5 | 5 (KC, LV, DET, MIA, BUF) | 7 non-no-play punt-formation plays; 2 aborted snaps (MIA, CLE) excluded. Checked for fakes not tagged "(Punt formation)": every 4th-down run/pass by a non-QB on 3+ yards to go was a punt or FG formation play. No "fake" text anywhere |
| Onside kicks | 28, all by trailing teams | 28, all trailing | Kicking team = `defteam` on kickoffs. Lead checked both from `score_differential` and from `total_home/away_score`; the kicking team trailed by 2 to 21 every time. None by BUF |
| BUF onside look | 23-9, start of Q4, delay, deep kick | yes | play 3347 no-play (Onside Kick formation), 3376 Doman 65 yds from BUF 30 |
| Eligible-lineman plays | 4; previous max 2 | 4; max 2 (wk 2, wk 6) | Same with no-plays included |
| League ≥4 team-games | 54 of 316 | 54 of 316 | 57 if no-plays, special teams and 2-pt tries are counted. Note the text match also catches defensive linemen used on offense (e.g. KC's K.Tonga) |
| Shotgun | 59%, others 37–53%, league 62% | 59.0% (46/78), 36.6–52.5%, 62.0% | Excluding BUF: 62.5%; team-game mean 61.9% |
| No-huddle (stat-heads) | 8%, high before 8% | 7.7%, high before 7.9% | Correct as rounded, but this game was *not* a no-huddle high. Fine as written |
| Q1 deep | 5 of 11 | 5 of 11 (air ≥20) | 2 more after Q1; matches recap |
| Player names | | gsis ids verified | Cook 00-0037248 RB, Corbett 00-0034261 G, Doman 00-0041126 P, Grable 00-0039882 OT, Latu 00-0040363 TE |
| KC on Thanksgiving night | | 2026_12_KC_BUF, Thu 11-26 20:20 | |
| Pinned games | 5 not loaded | 8 of 13 wk-11 games in pbp | |

Onside-rule context: the NFL owners passed a rule on March 31, 2026 that lets teams try an onside kick at any score
(it still has to be declared; surprise onsides stay banned). Sources: NBC Sports/PFT and AOL, both dated 2026-03-31.
So "every one came from a team that was behind" describes a choice teams made, not a rule, and the Bills' look at +14
was legal. That context is worth one plain clause in section 4 (optional, see below).

## Brand and claims

- No betting language (grep for odds/spread/pick/bet/line/lock: nothing).
- Jargon: body is mostly clean. "jumbo packages" and "reported in as eligible" are borderline (Editor's call).
- Intent: section 1 hedges well. The hero "fake onside look" (item 5) and the headline/label "lab game" (Editor) state
  intent. The rest uses "looked like".
- Small samples: this is a one-game story and says so ("One game, Nov. 22"). OK.

## Optional

- Section 3: "Across the league, only 5 teams have run a fake punt this season" counts Buffalo. Clearer: "Buffalo is one of only 5 teams to run one this season."
- Section 4: add "Teams have been allowed to try one at any score since this season's rule change," before the 28 figure. Cite the source in the stat-heads.
- Stat-heads no-huddle line adds nothing (it wasn't a high). Drop it or say "No-huddle 8%, about normal."
- The generator has no explicit AS_OF constant. It is effectively pinned by WEEK = 11 plus the NOT_FINAL list, the same style as wk11_postgame.py.
- At publish, run `scripts/freeze_images.py`. wk11lab-season.png is not in reports/published_images.json yet.
