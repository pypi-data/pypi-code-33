# this should help you to compare two CSV's (if you dont find the one you already made :o )
import pandas as pd


def compare_files(path_old_n, path_new_n):
    old_data = pd.read_csv(path_old_n, header=None)
    new_data = pd.read_csv(path_new_n, header=None)
    diff = old_data != new_data
    return old_data[diff.values], new_data[diff.values], diff

if __name__ == '__main__':
    path_old = '~/Documents/LEIP_PRES_1912_ST_old.csv'
    path_new = '~/Documents/LEIP_PRES_1912_ST.csv'
    write_diff = False

    diff_old, diff_new, diff_bool = compare_files(path_old, path_new)
    print('stop')