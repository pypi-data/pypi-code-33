"""simulation code"""
import numpy as np
from scipy.interpolate import BSpline as bsl
from scipy.stats import pearsonr
from sklearn.preprocessing import scale
from stcorr.stc import STC


def simulation():
    """
    simulations
    """
    np.random.seed(10)
    # generate true data
    nbasis = 7
    norder = 5
    t_interval = np.linspace(0, 1, 1000)
    t0, t1 = t_interval[0], t_interval[-1]
    tmp_list = np.linspace(t0, t1, nbasis - norder + 1).tolist()
    knots = [t0] * norder + tmp_list + [t1] * norder
    spl = bsl(knots, np.eye(nbasis), norder)
    phi = spl(t_interval)
    A = np.random.uniform(size=(nbasis, 1))
    B = np.random.uniform(size=(nbasis, 1))
    f = np.dot(phi, A)
    g = np.dot(phi, B)
    cor_true = pearsonr(f, g)[0]
    # generate samples
    n = 300
    p = 50
    q = 51
    sigma = 0.1
    t_interval = np.linspace(0, 1, 300)
    phi = spl(t_interval)
    f = np.dot(phi, A)
    g = np.dot(phi, B)
    u = np.random.uniform(size=(p, 1))
    v = np.random.uniform(size=(q, 1))
    Y = np.dot(f, u.T) + sigma * np.random.normal(size=(n, p))
    X = np.dot(g, v.T) + sigma * np.random.normal(size=(n, q))
    Y = scale(Y)
    X = scale(X)
    tuning = [10, 1e2, 1e3, 1e4]
    stc_exp = STC(Y, X, tuning, tuning, t_interval, norder, nbasis)
    stc_exp.stc_tuning()
    stc_exp.compute_final()
    stc_exp.compute_metric(u, v, abs(cor_true))
    return stc_exp
