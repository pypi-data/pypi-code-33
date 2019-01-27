""" This module contains utilities related to collections."""

from dautil import log_api
from itertools import chain
import collections


def sort_dict_by_keys(adict):
    """ Sorts a dictionary by keys.

    :param: adict: A dictionary.

    :returns: An Ordered dictionary sorted by keys.
    """
    return collections.OrderedDict(sorted(adict.items(), key=lambda t: t[0]))


def dict_from_keys(adict, keys):
    """ Selects a subset of a dictionary with a list of keys.

    :param: adict: A dictionary.
    :param: keys: A list of keys.

    :returns: A subset of the input dictionary.
    """
    return {k: adict[k] for k in keys}


def filter_list(func, alist):
    """ Filters a list using a function.

    :param: func: A function used for filtering.
    :param: alist: The list to filter.

    :returns: The filtered list.
    """
    return [a for a in filter(func, alist)]


def filter_dict_keys(func, adict):
    """ Filters the keys of a dictionary.

    :param: func: A function used to filter the keys.
    :param: adict: A dictionary.

    :returns: A list of keys selected by the filter.
    """
    logger = log_api.env_logger()
    logger.debug('adict {}'.format(adict))

    return [k for k in filter(func, adict.keys())]


def dict_updates(old, new):
    """ This function reports updates to a dict.

    :param: old: A dictionary to compare against.
    :param: new: A dictionary with potential changes.

    :returns: A dictionary with the updates if any.
    """
    updates = {}

    for k in set(new.keys()).intersection(set(old.keys())):
        if old[k] != new[k]:
            updates.update({k: new[k]})

    return updates


def is_rectangular(alist):
    """ Checks whether a list is rectangular.

    :param alist: A list or similar data structure.

    :returns: True if the argument is rectangular.
    """
    lengths = {len(i) for i in alist}

    return len(lengths) == 1


def isiterable(tocheck):
    """ Checking for an iterable argument using a
    somewhat modified definition ie strings and dicts
    are considered not iterable.

    :param tocheck: The data structure to check.

    :returns: True if iterable
    """
    return not isinstance(tocheck, str) and\
        not isinstance(tocheck, dict) and\
        isinstance(tocheck, collections.Iterable)


def flatten(iterable):
    """ Flattens an iterable, where strings and dicts
    are not considered iterable.

    :param iterable: The iterable to flatten.

    :returns: The iterable flattened as a flat list.
    """
    logger = log_api.env_logger()
    logger.debug('Iterable {}'.format(iterable))
    assert isiterable(iterable), 'Not iterable {}'.format(iterable)
    flat = iterable

    if isiterable(iterable[0]):
        flat = [i for i in chain.from_iterable(iterable)]

    return flat


class GridList():
    """ A two-dimensional rectangular list. """
    def __init__(self, nrows, ncols, val):
        self.nrows = nrows
        self.ncols = ncols
        self.grid = [ncols * [val] for i in range(nrows)]
        self.logger = log_api.conf_logger('collect.GridList')

    def dim_equal(self, other):
        """ Checks whether the dimensions of the current GridList
        and another rectangular list are equal.

        :param other: Another rectangular list.

        :returns: True if both data structures have the same dimensions.
        """
        return len(other) == self.nrows and len(other[0]) == self.ncols

    def copy(self, other):
        """ Copies the contents of another list
        into the current GridList.

        :param other: Another list.
        """
        flat_grid = flatten(self.grid)
        flat_other = chain.from_iterable(other)

        for i, value in enumerate(flat_other):
            flat_grid[i] = value

        item = iter(flat_grid)

        for i in range(self.nrows):
            for j in range(self.ncols):
                self.grid[i][j] = next(item)

    def fill(self, other):
        """ Fills the current GridList with the contents
        of another GridList as much as possible, unless
        there is a chance of overflow.

        :param: other: Another list.
        """
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
                self.copy(other)

    def update(self, row, col, change):
        """ Updates a specific grid cell.

        :param: row: The row number of the cell.
        :param: col: The column number of the cell.
        :param: change: The content with which to update\
            the cell. If the cell is a dict and the update value\
            too then the original dict will be updated.
        """
        cell = self.grid[row][col]

        if isinstance(cell, dict):
            if len(cell.keys()) == 0:
                cell = change
            else:
                (cell).update(change)

        self.grid[row][col] = cell
