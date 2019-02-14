
import logging
import sys
from haidatautils import mixed_list_to_int_list

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)


def drop_cols(df, args_dict):
    intlist_to_drop = mixed_list_to_int_list(args_dict["COLS"], df.columns.values.tolist())
    df = df.drop(df.columns[intlist_to_drop], axis=1)
    return df


