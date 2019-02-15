# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 17:08:16 2019

@author: yili.peng
"""
from scipy import stats
import matplotlib.pyplot as plt
from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.performance import factor_information_coefficient
import os
import numpy as np
from joblib import Parallel,delayed
import pandas as pd
from multiprocessing import Pool

def ic_test(db,factor_name,periods=[1]):
    try:
        table=get_clean_factor_and_forward_returns(factor=db.Factor[factor_name].shift().stack(),prices=db.Price,groupby=db.Ind.stack(),periods=periods)
    except:
        return None
    ic = factor_information_coefficient(table,group_adjust=True,by_group=False)
    return ic

def ic_test_mul_wrapup(X):
    db,factor_name,periods=X
    ic=ic_test(db,factor_name,periods)
    return ic
    
def run_all_ic(db,periods=[1],n_jobs=-1,back_end=None,**kwargs):
    assert back_end in (None,'loky'),'wrong backend type'
    if back_end is 'loky':
        ic_lst=Parallel(n_jobs=n_jobs,**kwargs)(delayed(ic_test)(db,factor_name,periods=periods) for factor_name in db.Factor.columns.levels[0])
    elif back_end is 'multiprocessing':        
        X=[(db,factor_name,periods) for factor_name in db.Factor.columns.levels[0]]
        pool=Pool(processes=n_jobs,**kwargs)
        ic_lst=pool.map(ic_test_mul_wrapup,X)
        pool.close()
        pool.join()    
    elif back_end is None:
        ic_lst=[ic_test(db,factor_name,periods=periods) for factor_name in db.Factor.columns.levels[0]]
    else:
        raise Exception('wrong backend type')        
    ic_lst2,k_lst=[],[]
    for i,j in zip(ic_lst,db.Factor.columns.levels[0]):
        if i is not None:
            ic_lst2.append(i)
            k_lst.append(j)
    return pd.concat(ic_lst2,keys=k_lst,axis=1)

def plot_ic_ts(ic,factor_name='factor', show=False,save_path=None):
    """
    Plots Spearman Rank Information Coefficient and IC moving
    average for a given factor.

    Parameters
    ----------
    ic : pd.DataFrame
        DataFrame indexed by date, with IC for each forward return.
    ax : matplotlib.Axes, optional
        Axes upon which to plot.

    Returns
    -------
    ax : matplotlib.Axes
        The axes that were plotted on.
    """
    ic = ic.copy()

    num_plots = len(ic.columns)
    f, ax = plt.subplots(num_plots, 1, figsize=(18, num_plots * 7))
    ax = np.asarray([ax]).flatten()

    ymin, ymax = (None, None)
    for a, (period_num, ic) in zip(ax, ic.iteritems()):
        ic.plot(alpha=0.7, ax=a, lw=0.7, color='steelblue')
        ic.rolling(window=22).mean().plot(
            ax=a,
            color='forestgreen',
            lw=2,
            alpha=0.8
        )

        a.set(ylabel='IC', xlabel="")
        a.set_title(
            "{} Period Forward Return Information Coefficient (IC)"
            .format(period_num))
        a.axhline(0.0, linestyle='-', color='black', lw=1, alpha=0.8)
        a.legend(['IC', '1 month moving avg'], loc='upper right')
        a.text(.05, .95, "Mean %.3f \n Std. %.3f" % (ic.mean(), ic.std()),
               fontsize=16,
               bbox={'facecolor': 'white', 'alpha': 1, 'pad': 5},
               transform=a.transAxes,
               verticalalignment='top')

        curr_ymin, curr_ymax = a.get_ylim()
        ymin = curr_ymin if ymin is None else min(ymin, curr_ymin)
        ymax = curr_ymax if ymax is None else max(ymax, curr_ymax)
    for a in ax:
        a.set_ylim([ymin, ymax])    
    if save_path is not None:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(os.path.join(save_path,'IC_{}.png'.format(factor_name)))
    if show:
        plt.show()
    else: 
        plt.close('all')

def run_plot_ic(IC,save_path=None,show=False):
    for i in IC.columns.get_level_values(0):
        plot_ic_ts(IC[i],i,save_path=save_path,show=show)

def ic_summary(ic_data):
    ic_summary_table = pd.DataFrame()
    ic_summary_table["IC Mean"] = ic_data.mean()
    ic_summary_table["IC Std."] = ic_data.std()
    ic_summary_table["Risk-Adjusted IC (IR)"] = \
        ic_data.mean() / ic_data.std()
    t_stat, p_value = stats.ttest_1samp(ic_data, 0)
    ic_summary_table["t-stat(IC)"] = t_stat
    ic_summary_table["p-value(IC)"] = p_value
    ic_summary_table["IC Skew"] = stats.skew(ic_data)
    ic_summary_table["IC Kurtosis"] = stats.kurtosis(ic_data)
    return ic_summary_table.apply(lambda x: x.round(3)).T

def run_ic_summary(IC):
    return pd.concat([ic_summary(IC[i].dropna()) for i in IC.columns.levels[0]],axis=1,keys=IC.columns.levels[0])
