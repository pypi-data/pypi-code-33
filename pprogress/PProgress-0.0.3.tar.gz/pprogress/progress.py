"""
File: progress.py
Author: Fergus Horrobin (fergus.horrobin@mail.utoronto.ca)

This program implements a simple Python based progress bar that is designed to
be used to show multiple progress bars when a program is run in parallel.
"""
import sys


class ProgressBar:
    """
    The main class for a PProgress bar. Each instance of this class initializes
    a new PProgress bar.

    Attributes
    ----------
    iterations : int
        The toal number of iterations until completion. If more than one process
        is specified, this number is divided by size (number of processes).
    prefix : str
        The prefix string for the progress bar.
    iteration : int
        The current iteration number
    fill : str
        The character to fill the bar with.
    length : int
        The length of the progress bar.
    rank : int
        The rank of the process (0 if there is only 1 process).
    size : int
        The number of processes running PProgress bars.
    """
    def __init__(self: 'ProgressBar', iterations: int, **kwargs) -> None:
        """
        Initialize a PProgress bar object. Specify the total number of
        iterations and any other parameters to specify the behaviour of the
        progress bar.

        Parameters
        ----------
        iterations : int
            The number of iterations to be completed in total.

        Keyword Args
        -----------
        prefix : str (Default "Progress")
            The prefix for the PProgress bar.
        iteration : int (Default 0)
            The starting iteration number.
        fill_char : str (Default "█")
            The string to fill the progress bar with.
        length : int (Default 60)
            Length of the progress bar.
        rank : int (Default 0)
            The rank for the process (starts from process 0)
        size: int (Default 1)
            The number of processes.
        """
        if 'prefix' not in kwargs:
            kwargs['prefix'] = "Progress"
        if 'iteration' not in kwargs:
            kwargs['iteration'] = 0
        if 'fill_char' not in kwargs:
            kwargs['fill_char'] = '█'
        if 'length' not in kwargs:
            kwargs['length'] = 60

        self.__iterations = iterations
        self.__prefix = kwargs['prefix']
        self.__iteration = kwargs['iteration']
        self.__fill = kwargs['fill_char']
        self.__length = kwargs['length']
        self.__rank = 0
        self.__size = 1

        if ('rank' in kwargs and 'size'
                not in kwargs) or ('size' in kwargs and 'rank' not in kwargs):
            raise Exception("If using MPI must pass rank and size.")

        if 'rank' in kwargs:
            self.__rank = kwargs['rank']
            self.__prefix += f" (process {self.__rank})"
            self.__size = kwargs['size']
            self.__iterations = self.__iterations / float(self.__size)

    def done(self: 'ProgressBar') -> None:
        """
        Perform finishing tasks when done with the PProgress bar. Prints
        blanklines such that the terminal prompt is after the progress bars at
        the end. Could also be useful for implementing timing functionality in
        the future.
        """
        print()

    def update(self: 'ProgressBar', increment: int = 1) -> None:
        """
        Updates the progress bar by incrementing the current iteration by
        increment. Requires increment >= 1.

        Parameters
        ----------
        increment : int
            The increment by which to increase the progress bar.
        """
        self.__iteration += increment
        percent = self.__iteration / float(self.__iterations) * 100
        fill_length = int(self.__length * self.__iteration // self.__iterations)

        self.__print_progress(percent, fill_length)

    def __print_progress(self: 'ProgressBar', percent: float, filled_length: int) -> None:
        fill = self.__fill * filled_length + " " * (self.__length -
                                                    filled_length)

        pbar = f"\r{self.__prefix}: |{fill}| {percent: .1f}%"

        for _ in range(self.__rank):
            print()
        print(pbar, end="")
        sys.stdout.flush()

        for _ in range(self.__rank):
            sys.stdout.write('\x1b[1A')
            sys.stdout.flush()
