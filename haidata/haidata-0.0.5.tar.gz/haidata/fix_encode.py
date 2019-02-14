# -*- coding: utf-8 -*-
"""
.. Created on Tue Nov 20 22:49:03 2018

.. module:: fix_encode
   :platform: Unix, Windows
   :synopsis: a function that fixed encoding on pandas dataframes using the :mod:`ftfy` package.

.. moduleauthor:: Hans Roggeman <hans@invalid.com>

"""

import pandas as pd
import traceback
import ftfy
import logging
import sys
from haidatautils import int_list_from_exclude_include

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)


def fix_encode(df_input, arg_dict):
    """Given a pandas DataFrame and a dictionary this fix will fix the encoding using :mod:`ftfy` according to the key-value pairs in the dictionary

    :param df_input: a pandas DataFrame
    :param arg_dict: a dictionary with the arguments
    :returns:  list -- the return code.
    :raises: ValueError, IndexError, AttributeError, KeyError

    """
    logger.info("Excecuting 'fix_encode' with arguments: {0}".format(str(arg_dict)))
    col_names_to_check = [df_input.columns.values[x] for x in
                          int_list_from_exclude_include(df_input, arg_dict, greedy=True)]

    try:
        include_types = ['object']
        used_column_names = df_input.loc[:, col_names_to_check].select_dtypes(include=include_types).columns.values
        if len(used_column_names) == 0:
            logger.warning(
                "No colums of type {0} found amoung columns {1}. No encoding fix performed.".format(include_types,
                                                                                                    col_names_to_check))
            return df_input
        to_replace_df = df_input.loc[:, used_column_names].fillna('').apply(lambda x: pd.Series(map(ftfy.fix_text, x)))
        df_input.loc[:, used_column_names] = to_replace_df
    except TypeError as te:
        logger.error(traceback.format_exc())
        raise te
    return df_input
