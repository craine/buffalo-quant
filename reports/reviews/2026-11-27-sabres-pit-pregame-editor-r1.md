# Editor review: 2026-11-27-sabres-pit-pregame (commit 3a61acf6)

**Verdict: PASS. Two optional suggestions below.**

- **Plain English:** the body has no jargon. xG, quartile and similar terms appear only in "For the stat-heads". The lead works on radio: "The Penguins have 16 points, 2nd-fewest in the NHL. But they get 50% of the chances..."
- **Rejected phrases:** none found in the md, hero or generator ("lopsided", "the home kind", "go the other way", "in reverse", "good end/bad end").
- **Numbers come from the generator:** every digit in the body is an f-string or an asserted constant. The hard-typed "Friday, Nov. 27, 8 p.m. ET", "Wednesday" and "So does the goaltending." are each backed by an assert (start_utc, rest = 1, the bottom-quarter goaltending condition). The site dek in `build.py` is typed by hand, as on every card; its values (2nd-fewest, half the chances, 51%) match.
- **Each piece reads on its own:** the chart title "Pittsburgh's shooting and goaltending have both let it down" fits inside the 1900 px image. The subtitle gives season, cutoff and "per game, empty-net goals left out". Axes are in plain English, the quadrants are labelled, and the footer gives source and sample (32 teams, 399 games). The hero label, both big numbers and the note each stand alone. The headline "Pittsburgh is better than its record" is supported by the share of chances.
- **Links:** `sabres-lightning-postgame-nov-22.html` is an ARTICLES slug. `../ledger.html` is a top-level site page. All five goalie card links resolve in `card_slugs()` (ukko-pekka-luukkonen, colten-ellis, alex-lyon, arturs-silovs, sergei-murashov).
- **Story:** clear arc: record, then the reason, then what usually happens next, then the model. "It won't necessarily show up in one game" is a good hedge.

Optional:
1. In the stat-heads section, "(Novak and Rakell 0 combined, Thompson 0 of 17)" is unclear. Suggested: "(Novak and Rakell 0 of 18 combined, Thompson 0 of 17)". In the generator: `(Novak and Rakell {n1_en} of {n1_g * len(lead_ids)} combined, ...)`.
2. See Quant's note on "So does the goaltending." Suggested: "So, mostly, does the goaltending."
