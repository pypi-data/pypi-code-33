# coding=utf-8
from __future__ import print_function

import pandas as pd

from suanpan import path


def load(file, *args, **kwargs):
    kwargs.setdefault("index_col", 0)
    return pd.read_csv(file, *args, **kwargs)


def dump(dataframe, file, *args, **kwargs):
    path.safeMkdirsForFile(file)
    dataframe.to_csv(file, **kwargs)
    return file
