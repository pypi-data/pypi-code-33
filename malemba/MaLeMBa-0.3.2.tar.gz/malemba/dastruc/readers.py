import numpy as np


def read_tsv_by_line(tsv_path, header=True):
    with open(tsv_path) as csv_f:
        n = 0
        for line_ in csv_f:
            if header and n == 0:
                n += 1
                continue
            line = line_.strip()
            yield list(map(autotype, line.split("\t")))
            line = None


def autotype(x):
    if x == "":
        return np.nan
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x
