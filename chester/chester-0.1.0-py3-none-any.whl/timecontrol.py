import time
import chess


class TimeControl(object):
    def __init__(self, initial_time, increment=0):
        self.initial_time = initial_time
        self.increment = increment
        self.wtime = self.btime = initial_time

    def start_new_game(self, side_to_move=chess.WHITE):
        self.wtime = self.btime = self.initial_time
        self.side_to_move = side_to_move
        self.timepoint = time.time()

    def signal_move_made(self):
        new_time = time.time()
        self.timepoint, delta = new_time, new_time - self.timepoint

        if self.side_to_move == chess.WHITE:
            self.wtime = self.wtime - delta + self.increment
        else:
            self.btime = self.btime - delta + self.increment

        self.side_to_move = not self.side_to_move

        return self.wtime <= 0 or self.btime <= 0
