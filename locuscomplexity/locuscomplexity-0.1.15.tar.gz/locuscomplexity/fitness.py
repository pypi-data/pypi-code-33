"""
Module that computes the fitness of communities and the complexity of functions

"""
import pandas as pd
import numpy as np
import locuscomplexity.complexity as cmplx
N_ITERATION = 50

def iter_fitness(n, m):
    """

    From Tacchella et al., 2012, compute fitness of a community with n iterations

    :param n: number of iteration
    :type n: int
    :param m: Matrix m
    :type m: pd.Dataframe
    :return: Fitness vector where [i] is the fitness of instance i
    :rtype: pd.Series
    """
    if n == 0:
        return pd.DataFrame(np.ones((len(m.index), 1)), index=m.index, columns=['f'])
    else:
        q = iter_complexity(n - 1, m)
        f = np.dot(m, q)
        return pd.DataFrame(f / np.mean(f), index=m.index, columns=['f'])


def iter_complexity(n, m):
    """
    From Tacchella et al., 2012, compute complexity of an instance of dimension1 with n iterations

    :param n: number of iteration
    :type n: int
    :param m: Matrix m
    :type m: pandas.DataFrame
    :return: Complexity vector where [i] is the complexity of function i
    :rtype: pandas.Series
    """
    if n == 0:
        return pd.DataFrame(np.ones((len(m.columns), 1)), index=m.columns, columns=['q'])
    else:
        q = np.dot(m.T, 1 / iter_fitness(n - 1, m))
        q = 1 / q
        return pd.DataFrame(q / np.mean(q), index=m.columns, columns=['q'])


def fitness(m, dimension1, n=N_ITERATION):
    """
    Runs the iteration to compute communities fitness scores

    :param m: M binary RCA matrix
    :type m: pandas.DataFrame
    :return: Fitness vector with <dimension1> and 'f' as columns
    :rtype: pandas.Dataframe
    """
    areas = pd.DataFrame(list(m.index.values), columns=[dimension1])
    # Remove column and rows with all zeros
    m = m.loc[~(m == 0).all(axis=1)]
    m = m.loc[:, (m != 0).any(axis=0)]
    f = iter_fitness(n, m)
    fit = f.merge(areas, left_index=True, right_on=dimension1, how='outer').replace(np.nan, 0)
    return fit


def complexity(m, n=N_ITERATION):
    """
    Runs the iteration to compute function complexity scores

    :param m: M binary RCA matrix
    :type m: pandas.DataFrame
    :return: Fitness vector with <function_name> and 'q' as columns
    :rtype: pandas.DataFrame
    """
    # Remove column and rows with all zeros
    m = m.loc[~(m == 0).all(axis=1)]
    m = m.loc[:, (m != 0).any(axis=0)]
    comp = iter_complexity(n, m)
    return comp.reset_index()


def outlook(m, df_complexity):
    """
    Compute the outlook (or opportunity value) of every community in the dataset using the M matrix and
    the Functional Complexity vector (from the Fitness algorithm)

    :param m: M binary RCA matrix
    :type m: pandas.Dataframe
    :param df_complexity: Functional Complexity vector, returned by complexity
    :type m: pandas.DataFrame
    :return: Outlook vector with <dimension1> as index and 'opportunity_value' column
    :rtype: pandas.DataFrame
    """
    m = m.loc[~(m == 0).all(axis=1)]
    d = cmplx.distance_to_function(m)
    col0 = df_complexity.columns.values[0]
    df_complexity = df_complexity[[col0, 'q']].set_index(col0)
    weighted_m = (1 - m).multiply(df_complexity['q'])
    outlook = pd.DataFrame(np.dot(1 - d, weighted_m.T).diagonal(), index=d.index, columns=['opportunity_value'])
    return outlook


def gain(m, df_complexity):
    """
    Compute the opportunity gain for each community and each function in the dataset

    :param m: M binary RCA matrix
    :type m: pandas.DataFrame
    :param df_complexity: Functional Complexity vector, returned by complexity
    :type df_complexity: pandas.DataFrame
    :return: Opportunity gain matrix with <function_name> as index and <dimension1> as columns
    :rtype: pandas.DataFrame
    """
    m = m.loc[~(m == 0).all(axis=1)]
    d = cmplx.function_proximity(m)
    col0 = df_complexity.columns.values[0]
    df_complexity = df_complexity[[col0, 'q']].set_index(col0)
    weigthed_m = (1 - m).multiply(df_complexity['q'])
    weigthed_d = d.div(d.sum(axis=0))
    gain = pd.DataFrame(np.dot(weigthed_d, weigthed_m.T).T, index=m.index, columns=m.columns)
    return gain