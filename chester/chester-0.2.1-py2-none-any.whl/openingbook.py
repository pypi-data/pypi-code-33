import chess
import chess.polyglot
import random


def play_from_opening_book(
    book, max_depth=10, fen=chess.STARTING_FEN, random_seed=None
):
    """Play out moves from an opening book and return the resulting board.

    From the given `fen` starting position, draw weighted random moves from the opening book
    to a maximum depth of `2 * max_depth` plies. Whenever there are no move moves in the book,
    the play stops and the board returned.

    If a seed integer is given, then this will always return the same final position.

    Arguments
    ---------
    book: str
        Path to a polyglot opening book file.
    max_depth: int, optional
        The maximum depth to play to. The number of moves (plies) made will at most be 2 times this.
        Default is 10.
    fen: str, optional
        Starting position in FEN notation. Default is the standard opening position.
    random_seed: int, optional
        Seed the random number generator to produce the same results each call. Default is to not seed,
        and so successive calls will in general yield different boards.

    Returns
    -------
        A `chess.Board` with the resulting position.
    """
    if random_seed is not None:
        random.seed(random_seed)

    board = chess.Board(fen)

    with chess.polyglot.MemoryMappedReader(book) as reader:
        try:
            for _ in range(2 * max_depth):
                move = reader.weighted_choice(board).move()
                board.push(move)
        except IndexError:
            pass

    return board
