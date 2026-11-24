# Quant review (stage 2): 2026-wk12-kc-whos-left

**Verdict: FAIL (publish with fixes).** The core counts hold (13 of 21, 12 of 23, 8 of 10, 5 of 11, 6 of 11, 6 of 12, 4 of 5 OL, 4 of 6 and 3 of 5 DBs, 35%, 71%, 22 months). But one "Now with" is wrong as of today, two-point tries are counted as targets, "through Week 11" leaves out one game without saying so, one chart position is wrong, and two sentences claim more than the data shows.

Everything below was recomputed independently from raw_snap_counts, raw_rosters_weekly, raw_pbp, raw_players and raw_schedules (read-only), not by running the writer's functions.

## Must-fix

1. **Justin Reid is no longer with New Orleans.** raw_rosters_weekly 2026 shows him as NO ACT for weeks 1-10, then **NO CUT (W03) in week 11**, with no week-12 row for any team. Web reporting backs this up: the Saints agreed to release him at his request on Nov. 19, 2026, and waived him on Nov. 20 ([Yardbarker/PFR](https://www.yardbarker.com/nfl/articles/saints_s_justin_reid_agree_to_part_ways/s1_14819_44588215), [PFR player page](https://www.profootballrumors.com/justin-reid)). I found no claim or signing.
   - Body: "Justin Reid (SS, now with New Orleans)" -> "Justin Reid (SS, released by New Orleans last week)"
   - Chart: "Now with New Orleans" -> "Released by New Orleans"
   - Generator: the "now" team comes only from snaps. Add a roster check so a player whose latest 2026 weekly-roster status is CUT is labeled "released by X". No other player in the set is affected: every other "other"/"same" player is ACT, INA or RES on his team as of the latest roster week.
2. **Week 11 is not complete.** The schedule has 163 regular-season games in weeks 1-11. Snap counts have 162, and the missing game is 2026_11_CIN_WAS (Monday night, Nov. 23, not yet played). This doesn't change any status (Cook, Douglas and Omenihu are already counted with CIN/WAS), but "through Week 11" is not literally true.
   - How we counted: "2026 snaps through Week 11." -> "2026 snaps through Week 11's Sunday games (Monday night's Cincinnati-Washington game hadn't been played)."
   - Stat-heads: "(162 games in the snap counts when this ran)" -> "(162 of 163 games; 2026_11_CIN_WAS not yet played)"
   - Chart footer: "regular season through Week 11." -> "regular season through Week 11's Sunday games."
   - raw_pbp has only 8 of 13 Week 11 games, but both KC (2026_11_ARI_KC) and BUF (2026_11_MIA_BUF) are loaded: 10 games each. The target totals are complete for both teams.
3. **Two-point tries are counted as targets.** The query (`pass = 1`, not no_play, receiver not null) includes 1 KC and 4 BUF two-point passes. CLAUDE.md excludes two-point tries, and standard target counts exclude them too. Sacks and scrambles are handled correctly: 0 plays with a receiver id on a sack or scramble. With `pass_attempt = 1 AND sack = 0 AND two_point_attempt = 0`:
   - KC total 317 -> **316**; BUF 291 -> **287**.
   - KC table: Kenneth Walker III "| 37 | 12% |" -> "| 36 | 11% |". The others are unchanged (Kelce 57 18%, Worthy 54 17%, Rice 44 14%, E. Johnson 27 9%).
   - BUF table: DJ Moore "| 48 | 16% |" -> "| 48 | 17% |"; Dalton Kincaid "| 42 | 14% |" -> "| 41 | 14% |"; Keon Coleman "| 41 | 14% |" -> "| 40 | 14% |". Shakir stays 54 19%, Ty Johnson 26 9%.
   - 35% (0.3533 -> 0.3513) and 71% (0.7113 -> 0.7143) are unchanged.
   - Stat-heads: "nflverse `receiver_player_id` on pass plays, no-plays excluded. KC 2026 317, BUF 2026 291." -> "nflverse `receiver_player_id` on pass attempts; sacks, two-point tries and no-plays excluded. KC 2026 316, BUF 2026 287."
4. **Cole Bishop is labeled CB in the chart.** PFR tagged him CB for that game, but he is a safety: his 2026 snap-count position is S, and he played safety beside Hamlin. The DB counts are unaffected because CB and S are both defensive backs. Chart: "Cole Bishop  CB" -> "Cole Bishop  S". Override in the generator, e.g. use the 2026 position for players still on the team, or a one-line fix.
5. **Overclaim: "and so is Buffalo's defensive staff."** We verified a new coordinator, not a mostly new staff. -> "and Buffalo has a new defensive coordinator."
6. **Overclaim: "The sideline changed more than the roster."** Nothing measures that comparison, and the play-caller is the same man. -> "The sideline changed too."

## Should-fix

- **Kaiir Elam.** He has 1 game in 2026 for the Chargers (week 8, 5 special-teams snaps, 0 on offense or defense), and the roster shows LAC DEV (practice squad) in weeks 1-7 and 9+. "No snaps on offense or defense this season" is true, but it reads as out of football. -> "Kaiir Elam (CB, now on the Chargers' practice squad)". Chart: "On Chargers practice squad". (He left Buffalo in a March 2025 trade, so it's fine that he's "gone".)
- **Part 1 link.** `bills-chiefs-leonhard-file.html` doesn't exist on this branch. Part 1 must publish first, or the link will 404.

## Verified

- **Game:** 2024_21_BUF_KC, gameday 2025-01-26, KC 32-29 (schedule).
- **Regulars (offense_pct or defense_pct >= 0.5):** BUF 21 (10 offense, 11 defense), KC 23 (11 offense, 12 defense).
- **PFR id matching:** all 41 players with 2026 snaps have the same PFR id and the same name in 2024 and 2026. None has snaps for two teams in 2026, so there are no mid-season trades. The 3 players with no 2026 snaps (Milano, Hunt, Smith-Schuster) are on no 2026 weekly roster under their pfr_id or by name.
- **Still Bills (13):** Allen, McGovern, Torrence, Dawkins, S. Brown, Knox, Shakir, Coleman (8 of 10 on offense); Bishop, Hamlin, Oliver, Rousseau, Bernard (5 of 11 on defense).
- **Still Chiefs (12):** Mahomes, Kelce, Worthy, Humphrey, T. Smith, Caliendo (6 of 11); C. Jones, Karlaftis, Bolton, Tranquill, Conner, Hicks (6 of 12).
- **Injured or rostered checks:** every "still" player is on his team's roster in the latest week. Dawkins, S. Brown, Oliver and T. Smith had inactive weeks, but all are active now. Jaylen Watson is on Rams reserve (RES) since week 9 but still a Ram. Danna was BUF CUT in week 5, re-listed from week 6 and BUF ACT in week 12, so "now a Bill" holds. 1 game (week 2), 8 defensive snaps; 42 of 73 snaps in the title game = 58%.
- **Offensive line:** BUF T/G/C regulars are McGovern, Torrence, Edwards, Dawkins and Brown. Edwards (NO) is gone: 4 of 5.
- **Defensive backs (CB, S, FS, SS):** KC has 6 (McDuffie, Watson, Conner, Cook, Reid, Hicks); gone are McDuffie (LA), Watson (LA), Cook (CIN) and Reid, so 4 of 6. BUF has 5 (Bishop, Hamlin, Douglas, Johnson, Elam); gone are Douglas (WAS), Johnson (LV) and Elam, so 3 of 5. McDuffie's trade to the Rams and Watson's Rams deal are confirmed in the PFR Chiefs offseason review (Aug. 26, 2026).
- **"About half of the defenders":** 5 of 11 (45%) and 6 of 12 (50%); 11 of 23 combined (48%). OK.
- **"Most familiar group":** BUF offense 80%, vs. KC offense 55%, KC defense 50%, BUF defense 45%. Supported.
- **22 months:** Jan. 2025 to Nov. 2026. OK.
- **Coaching**
  - Brady was OC and play-caller before the Jan. 2025 game ([SI, Jan. 21, 2025](https://www.si.com/nfl/bills/news/one-big-change-bills-oc-brady-must-make-to-beat-the-kansas-city-chiefs)).
  - He is head coach and still calls plays; Carmichael is a non-play-calling OC ([PFR, Jan. 30, 2026](https://www.profootballrumors.com/2026/01/bills-to-hire-pete-carmichael-jr-as-oc); [Buffalo Wdown](https://buffalowdown.com/joe-brady-clarifies-pete-carmichael-s-role-in-bills-new-offensive-structure-01kgqg30w6xk)).
  - Leonhard was hired from Denver as DC the day after Carmichael, so late January 2026 (the cited [NFL.com](https://www.nfl.com/news/bills-hiring-broncos-assistant-head-coach-jim-leonhard-as-defensive-coordinator) link works).
  - Bieniemy replaced Nagy, and Spagnuolo remains DC (the cited [Yardbarker, Jan. 29, 2026](https://www.yardbarker.com/nfl/articles/chiefs_make_double_coaching_decision_on_thursday/s1_17615_43398657) link works; also [CBS, Jan. 23, 2026](https://www.cbssports.com/nfl/news/eric-bieniemy-chiefs-offensive-coordinator-matt-nagy-nfl)).
  - Reid is still head coach, and Spagnuolo is in his 8th year as DC (PFR offseason review, Aug. 2026).
- **Hero JSON and site card:** they match the body (13 of 21, 12 of 23, 4 of 6, 3 of 5).
- **Reproducibility:** a clean copy (outputs deleted, generator re-run) reproduced the md, hero JSON and PNG byte-identically (md sha256 daff9996…).
- **Brand rules:** no betting language.
