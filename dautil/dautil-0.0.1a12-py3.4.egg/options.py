import pandas as pd
import matplotlib as mpl
import numpy as np


def set_pd_options():
    pd.set_option('precision', 4)
    pd.set_option('max_rows', 5)


def reset_pd_options():
    pd.reset_option('precision')
    pd.reset_option('max_rows')


def set_mpl_options():
    mpl.rcParams['legend.fancybox'] = True
    mpl.rcParams['legend.shadow'] = True
    mpl.rcParams['legend.framealpha'] = 0.7


def set_np_options():
    np.set_printoptions(precision=4, threshold=5,
                        linewidth=65)


def reset_np_options():
    np.set_printoptions(precision=8, threshold=1000,
                        linewidth=75)
