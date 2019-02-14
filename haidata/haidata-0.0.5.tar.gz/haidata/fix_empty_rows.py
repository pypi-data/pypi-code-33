import numpy as np
import pandas as pd
from distutils.util import strtobool


def fix_empty_rows(df, args_dict):
    if args_dict is None:
        args_dict = dict()

    minimum_ratio_for_drop = 1.0
    if "MINIMUM" in args_dict.keys():
        minimum_ratio_for_drop = float(args_dict["MINIMUM"])

    consider_zero = False
    if "ZERO" in args_dict.keys():
        consider_zero = strtobool(args_dict["ZERO"])

    ratio_of_useless = df.apply(lambda x: (np.sum(np.absolute(x) < 1E-14) + np.sum(np.isnan(x))) / df.shape[1],
                                axis=1) if consider_zero else df.apply(lambda x: (np.sum(np.isnan(x))) / df.shape[1],
                                                                       axis=1)
    df.drop(df.index[[np.where(ratio_of_useless >= minimum_ratio_for_drop)[0].tolist()]], inplace=True)
    return df
