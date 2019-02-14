import chess
from itertools import permutations
from .match import play_match
from .openingbook import play_from_opening_book


def _get_match_id(p1, p2, round_id):
    """Return a unique integer for each pair of p1 and p2 for every value of round_id.

    Property:
        _get_match_id(p1, p2, r) == _get_match_id(p2, p1, r) for all p1, p2, r
    """
    return hash("".join(sorted(str(p1) + str(p2) + str(round_id))))


def play_tournament(
    players,
    time_control,
    n_games=1,
    opening_book=None,
    opening_book_depth=10,
    repeat=True,
):
    """Play all possible matches between the given players.

    Each possible matchup, including white/black permutations, will be played `n_games` times each.

    Arguments
    ---------
    players: list of str
        A list of executables of the UCI engines to play.
    time_control: chester.timecontrol.TimeControl
        A TimeControl instance describing the time control to use.
    n_games: int
        The number of times each match-up should be played.
    opening_book: str, optional
        If the openings should be selected from an opening book, give the
        path to a polyglot opening book as this parameter. Default is to not
        use a book.
    opening_book_depth: int, optional
        Maximum depth to play out from the `opening_book`. Has no effect if no book is given.
        Default is a depth of 10 (20 plies).
    repeat: bool, optional
        When using an opening book, setting this to True will ensure that
        each player plays both sides of the same opening vs the same opponent.
        Default value is True.

    Returns
    -------
        Generator of `chess.pgn.Game` objects, exactly `n_games * len(list(permutations(players, 2)))` long.
    """
    for round_count in range(1, n_games + 1):
        for white, black in permutations(players, 2):
            if opening_book:
                if repeat:
                    board = play_from_opening_book(
                        opening_book,
                        max_depth=opening_book_depth,
                        random_seed=_get_match_id(white, black, round_count),
                    )
                else:
                    board = play_from_opening_book(
                        opening_book, max_depth=opening_book_depth
                    )
            else:
                board = chess.Board()

            pgn = play_match(white, black, time_control, fen=board.fen())
            pgn.headers["Round"] = round_count
            yield pgn
