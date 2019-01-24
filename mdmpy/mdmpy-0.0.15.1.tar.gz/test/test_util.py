import os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 

import numpy as np
from src import util

def test_cdf():
    print(util.exp_cdf(1))
    assert(util.exp_cdf(0)==0)

def test_bisect():
    test_beta = [0.3, 0.6]
    test_x    = [[1, 4], [8, 3]]
    lamb_from_bisect = util.find_corresponding_lambda(util.exp_cdf,test_beta,test_x)
    assert(np.isclose(util.default_bisect_func(util.exp_cdf, test_beta, test_x, lamb_from_bisect),0))
