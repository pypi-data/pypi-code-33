# -*- coding: utf-8 -*-
"""
.. Created on Wed Nov 21 22:28:41 2018

.. module:: haidatautils
   :platform: Windows, Linux
   :synopsis: Utility functions used by the haidata package

.. moduleauthor:: Hans Roggeman <hans@invalid.com>


"""

import sys
import copy
import logging

from operator import itemgetter
from itertools import chain

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)


def int_list_to_element_list(input_string, list_of_strings):
    """Given a string representing a list of slices, (e.g. '4:6,1:3,200,40:44'), extract the corresponding elements from a supplied list

    :param input_string: a string representing a list of slices, (e.g. '4:6,1:3,200,40:44')
    :param list_of_strings:  a supplied list (e.g.  ["A", "B", "C", "D", "E", "F"] )
    :return:  a list that is a subset of the supply `list_of_strings`
    :raises: ValueError, IndexError
    :Example: int_list_to_element_list("0,1,5:7", "ABCDEFGHIJKLMNOPQRSTUVWXYZ") returns "ABFG"

    """

    int_list = sorted(list(set(to_int_list(input_string))))
    if type(list_of_strings) is list:
        return list(itemgetter(*int_list)(list_of_strings))
    else:
        return ''.join([list_of_strings[i] for i in int_list])


def element_list_to_int_list(input_list, reference_list, sort_and_unique=True):
    """ returns the (sorted) indices of the elements of `input_list` in `reference_list`

    :param input_list: a list which is a subset of the elements of `reference_list`
    :param reference_list:  a supplied list
    :param sort_and_unique: a boolean
    :return:  a (sorted) unique list that consists of the integer indices of the elements of `input_list` in `reference_list`
    :raises: ValueError, IndexError
    :Example: element_list_to_int_list( ["A","Y","Z"], "ABCDEFGHIJKLMNOPQRSTUVWXYZ") returns [0,24,25]

    """
    used_input_list = input_list
    if type(used_input_list[0]) is str:
        used_input_list = map(str.strip, used_input_list)
    if sort_and_unique:
        used_input_list = list(sorted(set(input_list)))
    int_list = [reference_list.index(i) for i in used_input_list]
    if sort_and_unique:
        int_list = sorted(int_list)
    return int_list


def mixed_list_to_int_list(input_string, reference_list):
    """Given a string indicating a mixed list of indicators (e.g. "0:2,'G','E',24:26,1") and a reference list (e.g.
    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S","T", "U", "V", "W",
    "X", "Y", "Z"]) an list of integers giving unique indices in the list is returned (e.g. [0,1,4,6,24,25])
    :param input_string: a string indicating a mixed list of indicators (e.g. "0:2,'G','E',24:26,1")
    :param reference_list: a reference list of elements
    :return: list of integers
    """

    int_list = []
    for x in input_string.split(','):
        test_string = x.strip()
        if test_string[0].isdigit():
            int_list.extend(slice_string_to_list(test_string) if ":" in test_string else [int(test_string)])
        else:
            if test_string != ":":
                int_list.append(reference_list.index(test_string))
        pass
    return sorted(set(int_list))


def slice_string_to_list(slice_str):
    """Given a string given as an INCREASING slice (e.g. '4:6') this will give a list of int of the covered range (e.g.
    [4,5])

    :param slice_str: the string representing a increasing slice (e.g. 1:3, 0:10, 304:501, etc.)
    :type slice_str: str
    :returns:  list -- the return code.
    :raises: ValueError, IndexError, AttributeError, KeyError

    """
    idxs = itemgetter(0, -1)(slice_str.split(":"))
    list_of_idxs = list(range(int(idxs[0]), int(idxs[1])))
    if len(list_of_idxs) < 1:
        err_msg = "Invalid slice specification provided {0}.".format(slice_str)
        raise ValueError(err_msg)
    return list_of_idxs


def to_int_list(input_string):
    """Given a string representing a list of slices, (e.g. '4:6,1:3,200,40:44') this will give a list of sorted int for the covered range (e.g. [1,2,4,5,200,40,41,42,43])

    :param input_string: the string representing a list increasing slice (e.g. '1:3', '0:10,304:501', '20,25:28', '11,13', etc.)
    :type input_string: str
    :returns:  list -- the return code.
    :raises: ValueError, IndexError, AttributeError, KeyError

    """
    return sorted(set(chain.from_iterable([slice_string_to_list(x) \
                                               if ":" in x else [int(x)] \
                                           for x in input_string.split(',')])))


def listify_strings(x, y):
    """This function creates a flatList of strings or lists of strings without de-listing the string to the character level

    :Example:

    The calls:
    listify_strings(["AA"], ["BB", "CC"])
    listify_strings("AA", ["BB", "CC"])
    listify_strings([ "AA", "BB" ] , "CC")
    listify_strings([ "AA", "BB" ] , ["CC"])

    will return the list ["AA", "BB", "CC"]

    :param x: a string or list of strings
    :param y: a string or list of strings
    :return: a list of strings
    """
    x1 = copy.deepcopy(x)
    y1 = copy.deepcopy(y)
    if isinstance(x, list):
        if isinstance(y, list):
            x1.extend(y)
        else:
            x1.append(y)
        return x1
    else:
        if isinstance(y, list):
            t1 = [x1]
            t1.extend(y1)
            return t1  # string would be interpreted as a list, keep the order
        else:
            return [x1, y1]


def dicts_get(s, *ds):
    """This helper functions allows for registering functions within a class that are no longer in scope at the time of registration

    `Source of this function <https://stackoverflow.com/questions/53678884/setting-imported-functions-as-members-in-a-static-dictionary>`_

    """
    for d in ds:
        if s in d:
            return d[s]
    # if s is not found in any of the dicts d, treat it as an undefined symbol
    raise NameError("name %s is not defined" % s)


def int_list_from_exclude_include(df, args_dict, greedy=False):

    original_column_names = df.columns.values.tolist()
    column_idxs_to_process = list(range(len(original_column_names))) if greedy else []

    if 'EXCLUDE' in args_dict.keys():
        column_names_to_process = original_column_names
        exclude_idxs = mixed_list_to_int_list(args_dict['EXCLUDE'], column_names_to_process)
        column_idxs_to_process = [x for x in column_idxs_to_process if x not in exclude_idxs]

    if 'INCLUDE' in args_dict.keys():
        column_idxs_to_process.extend(mixed_list_to_int_list(args_dict['INCLUDE'], original_column_names))

    return sorted(list(set(column_idxs_to_process)))



