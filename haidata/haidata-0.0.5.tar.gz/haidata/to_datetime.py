
import pandas as pd
import logging
import sys
from haidatautils import int_list_from_exclude_include

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)

def to_datetime(df, args_dict):
    """Given a pandas DataFrame and a dictionary of arguments, turn convert columns in the DataFrame to DateTime format.
    The converted columns are chosen through the "INCLUDE" and/or "EXCLUDE" elements of the "ARGS" value in the argument
    dictionary (`args_dict`). "INCLUDE" and "EXCLUDE" are both optional and are strings denoting columns by name and/or
    index, e.g. "0,'COL3','COL20',24:26,10". Another optional argument is "REPLACE", a boolean value (default to True)
    that indicates whether the columns are overridden or whether new columns are created with a string "DT_" prepended
    to the old name.

    :param df:  a pandas DataFrame
    :param args_dict: a dictionary with the arguments, e.g. { "INCLUDE": "Date","REPLACE":false}
    :return: a pandas DataFrame

    """
    column_names_to_process = [df.columns.values[x] for x in int_list_from_exclude_include(df, args_dict)]
    replace = True
    if "REPLACE" in args_dict.keys():
        replace = bool(args_dict["REPLACE"])
    if replace:
        for col_name in column_names_to_process:
            df[col_name] = pd.to_datetime(df[col_name])
    else:
        for col_name in column_names_to_process:
            df["DT_" + col_name] = pd.to_datetime(df[col_name])
    return df
