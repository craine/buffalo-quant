"""Games that weren't final in our feed when a pinned story was published.

A story pinned to "games through AS_OF" must reproduce the published numbers. When a late game on the AS_OF date
arrives in a later ingest, list it here and the story's generator leaves it out. Keyed by the AS_OF date.
"""
NOT_IN_FEED = {
    # Nov. 17, 2026: the four late-starting games (ANA-STL, NSH-MIN, DAL-VGK, CGY-SJS) loaded on Nov. 18 after the
    # PHI post-game and "If I were GM" stories were published from the first seven.
    "2026-11-17": {2026020339, 2026020340, 2026020342, 2026020343},
    # Nov. 19, 2026: the three late games (ANA-COL, VAN-SEA, DAL-VGK) weren't final when the Sabres-Capitals recap was built.
    "2026-11-19": {2026020356, 2026020357, 2026020358},
}


def drop_late(df, as_of, col="game_id"):
    return df[~df[col].astype("int64").isin(NOT_IN_FEED.get(as_of, set()))]
