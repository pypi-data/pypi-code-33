import numpy as np
import pandas as pd

__mod = '''# measurement model
ind60 =~ x1 + x2 + x3
dem60 =~ y1 + y2 + y3 + y4
dem65 =~ y5 + y6 + y7 + y8
# regressions
dem60 ~ ind60
dem65 ~ ind60 + dem60
# residual correlations
y1 ~~ y5
y2 ~~ y4 + y6
y3 ~~ y7
y4 ~~ y8
y6 ~~ y8
'''

def get_model():
    global __mod
    return __mod

def get_data():
    data = pd.read_csv('pd_data.txt', sep=',', index_col=0)
    return data