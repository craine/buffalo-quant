import pandas as pd

from src.metrics.streaks import Kind, notable, ranked, runs


def units(rows):
    return pd.DataFrame(rows, columns=["key", "team", "game_id", "season", "ok"])


def test_runs_split_and_active():
    u = units([("A", "BUF", "g1", 2025, True), ("A", "BUF", "g2", 2025, True), ("A", "BUF", "g3", 2025, False),
               ("A", "BUF", "g4", 2026, True), ("A", "BUF", "g5", 2026, True), ("A", "BUF", "g6", 2026, True)])
    r = runs(u, "key", latest={"BUF": "g6"})
    assert list(r.length) == [2, 3]
    assert list(r.active) == [False, True]


def test_retired_player_is_not_active():
    # The player's last game is g2, but his team has played since (g9): his run is over, not alive.
    u = units([("P", "NE", "g1", 2010, True), ("P", "NE", "g2", 2010, True)])
    assert not runs(u, "key", latest={"NE": "g9"}).active.any()


def test_longest_since_and_franchise_rank():
    u = units([("BUF", "BUF", f"a{i}", 1999, True) for i in range(40)] + [("BUF", "BUF", "x", 1999, False)]
              + [("BUF", "BUF", f"b{i}", 2026, True) for i in range(33)])
    r = runs(u, "key", latest={"BUF": "b32"})
    k = ranked(r, Kind("drives without allowing a touchdown", "drives", "team")).iloc[0]
    assert (k.length, k.franchise_rank, k.last_as_long, k.last_as_long_len) == (33, 2, 1999, 40)
    assert len(notable(ranked(r, Kind("drives without allowing a touchdown", "drives", "team")))) == 1
