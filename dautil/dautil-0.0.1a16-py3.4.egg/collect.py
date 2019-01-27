from dautil import log_api
from itertools import chain
import collections


def dict_updates(old, new):
    updates = {}

    for k in set(new.keys()).intersection(set(old.keys())):
        if old[k] != new[k]:
            updates.update({k: new[k]})

    return updates


def is_rectangular(a):
    lengths = {len(i) for i in a}

    return len(lengths) == 1


def isiterable(tocheck):
    return not isinstance(tocheck, str) and\
        not isinstance(tocheck, dict) and\
        isinstance(tocheck, collections.Iterable)


def flatten(iterable):
    assert isiterable(iterable), 'Not iterable'
    flat = iterable

    if isiterable(iterable[0]):
        flat = [i for i in chain.from_iterable(iterable)]

    return flat

class GridList():
    def __init__(self, nrows, ncols, val):
        self.nrows = nrows
        self.ncols = ncols
        self.grid = [ncols * [val] for i in range(nrows)]
        self.logger = log_api.conf_logger('collect.GridList')

    def dim_equal(self, other):
        return len(other) == self.nrows and\
               len(other[0]) == self.ncols

    def cp(self, other):
        flat_grid = flatten(self.grid)
        flat_other = chain.from_iterable(other)

        for i, value in enumerate(flat_other):
            flat_grid[i] = value

        it = iter(flat_grid)

        for i in range(self.nrows):
            for j in range(self.ncols):
                self.grid[i][j] = next(it)

    def fill(self, other):
        # If edited may become jagged
        if is_rectangular(other):
            if self.dim_equal(other):
                self.grid = other

                return

            ocells = len(other) * len(other[0])
            ncells = self.nrows * self.ncols

            if ocells > ncells:
                # might lose info
                self.logger.warning('Filling {0} with {1}'.format(ncells,
                                                                  ocells))
            else:
                self.cp(other)

    def update(self, row, col, change):
        cell = self.grid[row][col]

        if isinstance(cell, dict):
            if len(cell.keys()) == 0:
                cell = change
            else:
                (cell).update(change)

        self.grid[row][col] = cell
