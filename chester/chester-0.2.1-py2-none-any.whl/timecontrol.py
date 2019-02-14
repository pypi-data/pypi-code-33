import time
import chess


class TimeControl(object):
    """Class modeling an arbitrary time control.

    Starting time and increment are given in units of seconds,
    and then this class is responsible for the handling of each
    players time.

    The end user _never_ needs to use this class any further than
    instantiating an object with the desired time controls and providing
    this instance to the functions that expect it.
    """

    def __init__(self, initial_time, increment=0):
        """Initialize a time control with the given starting time and increment.

        Arguments
        ---------
        initial_time: int or float
            Starting time for both players in seconds.
        increment: int or float, optional
            Time in seconds gained after each move.
        """
        self.initial_time = initial_time
        self.increment = increment
        self.wtime = self.btime = initial_time

    def _start_new_game(self, side_to_move=chess.WHITE):
        """Reset times and set side_to_move."""
        self.wtime = self.btime = self.initial_time
        self.side_to_move = side_to_move
        self.timepoint = time.time()

    def _signal_move_made(self):
        """Update times since last call and side_to_move."""
        new_time = time.time()
        self.timepoint, delta = new_time, new_time - self.timepoint

        if self.side_to_move == chess.WHITE:
            self.wtime = self.wtime - delta + self.increment
        else:
            self.btime = self.btime - delta + self.increment

        self.side_to_move = not self.side_to_move

        return self.wtime <= 0 or self.btime <= 0
