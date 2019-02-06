
import numpy as np


def fix_empty_cols(df, args_dict):
    if args_dict is None:
        args_dict = dict()
    cols_to_drop = []
    for colname in df.columns.values:
        if not args_dict.keys() or "MINIMUM" not in args_dict.keys():
            if np.all(df[colname].isnull()):
                cols_to_drop.append(colname)
        else:
            min_ratio = float(args_dict["MINIMUM"])
            if np.sum(~df[colname].isnull())/df.shape[0] < min_ratio:
                cols_to_drop.append(colname)
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
    return df
