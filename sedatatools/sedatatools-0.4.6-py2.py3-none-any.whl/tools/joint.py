"""
This is used to merge multiple CSV file, created after we realized that MergeTool written in Java doesn't handle
FIPS columns properly (removes zeros)
v0.1
"""

import pandas as pd
import os
import sys
import time

import simplelogging

def cols_to_remove(cols, pkeys):
    """
    remove repeating columns
    :return:
    """
    cols_rm = [i for i in cols if i in cols_list and i not in pkeys]
    cols_list.extend(cols)
    return cols_rm


def get_file_names(wf=''):
    return [f for f in os.listdir(wf) if f.endswith('.csv')]


def read_and_merge(fn, keys, str_keys, wf=''):
    stats = []  # get some statistics for error checking
    dtype = {}
    main_df = pd.DataFrame()
    for i, f in enumerate(fn):
        if str_keys:
            dtype = {keys[i]: 'str'}
        if i == 0:
            log.info(f'Starting with {fn[0]}')
            main_df = pd.read_csv(os.path.join(wf, fn[0]), dtype=dtype)
            stats.append(main_df.shape)
            cols_to_remove(main_df.columns, [])
        else:
            log.info(f'Adding {fn[i]}...')
            add_df = pd.read_csv(os.path.join(wf, f), dtype=dtype)
            add_df.drop(cols_to_remove(add_df.columns, keys), axis=1)
            stats.append(add_df.shape)
            main_df = main_df.merge(add_df, how='inner', left_on=keys[i-1], right_on=keys[i])
    return main_df, stats


def check_column_exuality(acol, bcol):
    return all(acol == bcol)


def analyze_inputs(fn, top_limit):
    """
    This columns should recognize what columns can be use for merging
    :param fn:
    :param top_limit:
    :return:
    """
    base_df = pd.read_csv(fn[0], nrows = top_limit)
    matching_columns = []
    for i, f in enumerate(fn):
        if i == 0:
            continue
        else:
            tmp_df = pd.read_csv(fn[0], nrows=top_limit)
            for col in tmp_df.columns:
                for index, base_col in enumerate(base_df.columns):
                    if check_column_exuality(tmp_df[col], base_df[base_col]):
                        matching_columns.append(col)
                        cols_diff = list(base_df.columns.difference(tmp_df.columns)) + [col]
                        tmp_df_short = tmp_df.loc[:, cols_diff]
                        base_df = tmp_df_short.merge(base_df, how='inner', left_on=col, right_on=base_col)
                    if index == base_df.shape[1] and len(matching_columns) == 0:
                        log.info('No auto match!')
                        return None
    return matching_columns


def checks_stats(statist):
    for i, stat in enumerate(statist):
        if stat[0] > 0 and stat[0] != statist[i - 1][0]:
            log.info(f'Some rows are lost between dfs {i} and {i-1}')


def write_stats(stat):
    for i, s in enumerate(stat):
        log.info(f'Table nr. {i+1}: {s}')


if __name__ == '__main__':

    log = simplelogging.get_logger()

    if len(sys.argv) > 0:
        log.info('enter arguments')

    start_time = time.time()

    string_keys = True
    auto_keys = False
    top_key = 100
    working_folder = r'D:\SHARE\C1990_SL150'
    output_file_name = 'final.csv'
    keys = ['Geo_FIPS', 'Geo_FIPS', 'Geo_FIPS']  # TODO parametrize all of this

    global cols_list
    cols_list = []

    file_names = get_file_names(working_folder)
    if auto_keys:
        keys = analyze_inputs(file_names, top_key)
        if not keys:
            log.info('Please add keys!')
            sys.exit()
    if len(keys) != len(file_names):
        log.error('NUMBER OF KEYS MUST HAVE MATCHING NUMBER OF FILES!!!')
        # sys.exit()

    result_df, statistic = read_and_merge(file_names, keys, string_keys, working_folder)
    checks_stats(statistic)
    log.info('Writing output file!')

    result_df.to_csv(os.path.join(working_folder, output_file_name), index=False)
    statistic.append(result_df.shape)
    write_stats(statistic)
    log.info(f'Done in {time.time() - start_time} seconds.')
