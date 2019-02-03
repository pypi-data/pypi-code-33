# -*- coding: utf-8 -*-
"""
This is a submodule of fk_lib.
The moudle contains several functions that are basic data structure operations.
"""
import random
import numpy as np
from .fkl_math import *

def FKLDeleteList(arg_list,del_indexs):
    """
    Args:
        arg_list: A list of arguments.
        del_indexs: A list that contains several indexes that be deleted.
    Returns:
        Return a list of deleted arguments.
    Raises:
        None
    """
    del_indexs.sort()
    new_del_indexs=[del_indexs[i]-i for i in range(len(del_indexs))]
    for del_index in new_del_indexs:
        del arg_list[del_index]
    return arg_list
def FKLRandomSelectDatas(datas,select_ratio=1):
    """
    Args:
        datas: A list of datas.
        select_ratio: A float that represent the ratio of random selection.
    Returns:
        Return a list of selected datas.
    Raises:
        None
    """
    datas_len=len(datas)
    select_datas_len=round(datas_len*select_ratio)
    random.shuffle(datas)
    selected_datas=datas[:select_datas_len]
    return selected_datas
def FKLRandomSplitXY(x,y,train_ratio=0.9,test_ratio=0.1):
    """
    Args:
        x: A list of datas of x.
        y: A list of datas of y.
        train_ratio: A float that represent the ratio of train set.
        test_ratio: A float that represent the ratio of test set.
    Returns:
        Return a tuple of 2 dimensional, the first element contains train_x and 
        train_y, the second element contains test_x and test_y.
    Raises:
        Exception: The x_len not equal to y_len.
    """
    x_len=len(x)
    y_len=len(y)
    if(x_len!=y_len):raise Exception("FKLRandomSplitXY Error: The x_len not equal to y_len.")
    datas_len=x_len
    train_len=round(datas_len*train_ratio)
    test_len=datas_len-train_len
    x,y=FKLShuffle(x,y)
    test_x=x[:test_len]
    test_y=y[:test_len]
    train_x=x[test_len:train_len]
    train_y=y[test_len:train_len]
    return ((train_x,train_y),(test_x,test_y))
def FKLRandomSelectXY(x,y,select_ratio=1):
    """
    Args:
        x: A list of datas of x.
        y: A list of datas of y.
        select_ratio - A float that represent the ratio of random selection.
    Returns:
        Return a tuple of 2 dimensional, contains datas of x of random selection and 
        datas of y of random selection.
    Raises:
        Exception: The x_len not equal to y_len.
    """
    x_len=len(x)
    y_len=len(y)
    if(x_len!=y_len):raise Exception("FKLRandomSelectXY Error: The x_len not equal to y_len.")
    datas_len=x_len
    select_datas_len=round(datas_len*select_ratio)
    x,y=FKLShuffle(x,y)
    selected_x=x[:select_datas_len]
    selected_y=y[:select_datas_len]
    return (selected_x,selected_y)
def FKLShuffle(x,y):
    """
    Args:
        x: A list of datas of x.
        y: A list of datas of y.
    Returns:
        Return a tuple of 2 dimensional, contains datas of x of shuffle and 
        datas of y of shuffle.
    Raises:
        None
    """
    x=np.array(x)
    y=np.array(y)
    permutation = np.random.permutation(y.shape[0])
    x = x[permutation]
    y = y[permutation]
    return (x,y)