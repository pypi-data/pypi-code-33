from itertools import permutations
from .match import play_match


def play_tournament(players, time_control, n_games=1):
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

    Returns
    -------
        Generator of `chess.pgn.Game` objects, exactly `n_games * len(list(permutations(players, 2)))` long.
    """
    for round_count in range(1, n_games + 1):
        for white, black in permutations(players, 2):
            pgn = play_match(white, black, time_control)
            pgn.headers["Round"] = round_count
            yield pgn
