import logging
import sys
import numpy as np
from distutils.util import strtobool
import pandas as pd

# from haidata.haidatautils import mixed_list_to_int_list
from haidatautils import mixed_list_to_int_list

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)


def fix_excess_stdev(input_df, args_dict):

    int_list_to_drop = mixed_list_to_int_list(args_dict["COLS"], input_df.columns.values.tolist())
    use_diff = strtobool(args_dict["DIFF"]) if "DIFF" in args_dict.keys() else False

    # args_dict = dict({'NUM_STD': "3,6,5"})
    std_multipliers = [float(x) for x in str(args_dict["NUM_STD"]).split(",")] if \
        "NUM_STD" in args_dict.keys() else [10.0] * len(int_list_to_drop)

    if len(int_list_to_drop) > 1 and len(std_multipliers) == 1:
        std_multipliers = [std_multipliers[0]] * len(int_list_to_drop)

    if len(std_multipliers) != len(int_list_to_drop):
        raise ValueError(
            "Length of Std dev multipliers ({0}) does not match length of column identifiers ({1})".format(
                len(std_multipliers), len(int_list_to_drop)))

    iterative = strtobool(args_dict["ITER"]) if "ITER" in args_dict.keys() else False

    by_names = None if "BY" not in args_dict.keys() else \
        [int(x) for x in mixed_list_to_int_list(args_dict["BY"], input_df.columns.values.tolist())]
    if by_names is not None:
        if len(by_names) == 1 and len(int_list_to_drop) > 1:
            # nonlocal by_names
            by_names = [by_names[0]] * len(int_list_to_drop)

    if by_names is None:
        for column_name, std_multiplier in zip(input_df.columns[int_list_to_drop].values.tolist(), std_multipliers):
            input_diff_px = input_df.iloc[:, input_df.columns.get_loc(column_name)].diff(
                -1) if use_diff else input_df.iloc[:, input_df.columns.get_loc(column_name)]
            mean_diff = input_diff_px.mean()
            std_diff = input_diff_px.std()
            test_series = np.abs((input_diff_px - mean_diff) / std_diff)

            while any(test_series > std_multiplier):
                input_df = input_df.iloc[np.where(test_series < std_multiplier)]
                if not iterative:
                    break
                input_diff_px = input_df.iloc[:, input_df.columns.get_loc(column_name)].diff(
                    -1) if use_diff else input_df.iloc[:, input_df.columns.get_loc(column_name)]
                mean_diff = input_diff_px.mean()
                std_diff = input_diff_px.std()
                test_series = np.abs((input_diff_px - mean_diff) / std_diff)
        
        return input_df
        
    else:

        new_dfs = []
        
        for column_name, std_multiplier, by_name in zip(input_df.columns[int_list_to_drop].values.tolist(),
                                                        std_multipliers, by_names):

            by_column_name = input_df.columns.values[by_name]
            by_values = input_df[by_column_name].unique()

            for by_value in by_values:  # by_value = by_values[0]
                input_df_subset = input_df[input_df[by_column_name] == by_value]
                input_diff_px = input_df_subset[column_name].diff(-1) if use_diff else input_df_subset[column_name]
                mean_diff = input_diff_px.mean()
                std_diff = input_diff_px.std()
                test_series = np.abs((input_diff_px - mean_diff) / std_diff)

                while any(test_series > std_multiplier):
                    idxs = np.where(test_series.values <= std_multiplier, True, False).flatten()
                    # len(idxs); test_series.shape
                    input_df_subset = input_df_subset.iloc[idxs]
                    if not iterative:
                        break
                    input_diff_px = input_df_subset[column_name].diff(-1) if use_diff else input_df_subset[column_name]
                    mean_diff = input_diff_px.mean()
                    std_diff = input_diff_px.std()
                    test_series = np.abs((input_diff_px - mean_diff) / std_diff)

                new_dfs.append(input_df_subset)
                # print(by_value)

            input_df = pd.concat(new_dfs)
            
        input_df.sort_index(inplace=True)
        return input_df

#
