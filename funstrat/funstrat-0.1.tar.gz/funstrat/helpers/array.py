import numpy as np
from copy import deepcopy
"""
    Array Manipulation for the rest of the application
"""

def split_range(arr, split_num=3, shape="normal0"):
    # Splits a range into various parts for fuzzy logic
    # The fuzzy logic will effectively form into
    r = []
    for i in range(split_num):
        r.append([])
    return r


def main(arr):
    
    x = split_range([1, 2, 3, 4, 5])
    print(x)
    return x

def col_filter(y, start="RSI"):
    if not isinstance(y, list):
        raise TypeError("Not a list")
    # x = deepcopy(y)
    filter_col = [col for col in y if col.startswith(start)]
    return filter_col

if __name__ == "__main__":
    bitch  = np.arange(0, 26, 1)
    main(bitch)

