"""
Implementation of the Economic Complexity algorithm introduced by Hidalgo and Hausmann


References
----------
See Hidalgo, "The Product Space Conditions the Development of Nations."
    https://arxiv.org/pdf/0708.2090.pdf

See Economic complexity glossary,
    http://atlas.cid.harvard.edu/learn/glossary

See algorithm applied to Locus framework,
    https://drive.google.com/open?id=1jotoaZgVFKd8Il-qzDMP3EBu9NQuRWgR

"""

import pandas as pd
import numpy as np
import pandas.api.types as ptypes
import networkx as nx
import os
import pickle
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import locuscomplexity.color_code as cc

dirname, filename = os.path.split(os.path.abspath(__file__))


def validate_input(df_data, dimension1, year):
    """
    Make sure the input data has a column dimension1, a column YEAR (that contains at least one
    occurrence of year and other columns that contains functions

    :param df_data: (Dataframe) input data to validate
    :param dimension1: (str) first dimension of the problem (name of the column in df_data)
    :param year: (int) year of interest, we want to make sure it appears in the dataset
    :return: throw error if not valid, nothing otherwise
    """
    cols = df_data.columns.values
    assert dimension1 in cols, f"Make sure the input data has a column {dimension1} " \
                           "that contains the code or name of each communities"
    assert ptypes.is_string_dtype(df_data[dimension1]), f"Make sure the column {dimension1} " \
                           "is of type string. If it contains integers starting with zeros, use str.zfill(n) to " \
                           "keep the zeros at the beginning."
    assert 'YEAR' in cols, "Make sure the input data has a column 'YEAR' " \
                           "that contains the year of the recorded data in each row"
    YEAR = df_data['YEAR'].astype(int).values
    assert year in YEAR, "Make sure the input data contains data on the year you are interested in. " \
                         "{} doesn't appear in the dataset".format(year)


def build_m(df_data, dimension1, binary=True, filter_col=None, filter_val=None):
    """
    Build matrix binary M by computing the RCA of every instance of dimension 1

    :param df_data: (Dataframe) each row is a instance of dimension1 in a YEAR, other columns are functions.
    :param dimension1: (string) first dimension of the problem (name of the column in df_data)
    :param year: (int) year of interest
    :param binary : (bool) True to get M matrix, False to get RCA matrix
    :return: (Dataframe) Matrix M
    """
    #validate_input(df_data, dimension1, year)
    if filter_col:
        df_nat = df_data[df_data[filter_col] == filter_val]
        df_cp = df_nat.groupby(by=[dimension1, filter_col]).sum()
    else:
        df_nat = df_data
        df_cp = df_nat.groupby(by=[dimension1]).sum()

    #Compute num and denom for RCA
    df_nat = df_cp.sum(axis=1)
    df_num = df_cp.astype(float).div(df_nat, axis=0).astype(float)

    df_prod = df_cp.sum(axis=0)
    df_tot = df_prod.sum()
    df_denum = df_prod / df_tot

    #Compute RCA
    if filter_col:
        df = df_num.div(df_denum).reset_index().drop(filter_col, 1).set_index(dimension1)
    else:
        df = df_num.div(df_denum).reset_index().set_index(dimension1)
    #Make matrix binary or keep raw RCA values
    if binary:
        df = df.apply(lambda x: x > 1).astype(int)
    return df


def diversity(m):
    """
    Compute Diversity vector for all instance of dimension1 in the dataset

    :param m: (Dataframe) M RCA, binary matrix
    :return: (Series) d = Diversity vector
    """
    #Taking the sum of each row of the binary M matrix
    return m.sum(axis=1)


def ubiquity(m):
    """
    Compute Ubiquity vector for all functions in the dataset

    :param m: (Dataframe) M RCA, binary matrix
    :return: (Series) Ubiquity vector
    """
    #Taking the sum of each column of the binary M matrix
    return m.sum(axis=0)


def m_dn_un(m):
    """
    From M matrix build both M tilde matrices, first is for Community Complexity Index
    second is for Function Complexity Index

    :param m: (Dataframe) M binary RCA matrix
    :return: (Df, Df) M_tilde for dimension1, M_tilde for functions
    """
    m_dn = m.div(diversity(m), axis='index').replace(np.nan,0)
    mT_un = (m.T).div(ubiquity(m), axis='index').replace(np.nan,0)
    m_tilde_community = pd.DataFrame(np.dot(m_dn, mT_un),
                                     index=m_dn.index, columns=m_dn.index)
    m_tilde_function = pd.DataFrame(np.dot(mT_un, m_dn),
                                    index=m_dn.columns, columns=m_dn.columns)

    return m_tilde_community, m_tilde_function


def complexity_indices(df_data, dimension1, filter_col=None, filter_val=None):
    """
    Computes Community Complexity Indices and Functional Complexity Indices
    
    :param df_data: (Dataframe) each row is a instance of dimension1 in a YEAR, other columns are functions.
    :param dimension1: (str) first dimension of the problem (name of the column in df_data)
    :param year: (int) Year of interest
    :return: (Dataframe) Community complexity vector,
             (Dataframe) Functional complexity vector
    """
    m = build_m(df_data, dimension1, filter_col, filter_val)
    Mc, Mp = m_dn_un(m)

    #Computes second largest eigenvector of M_tilde for dimension1
    val, vect = np.linalg.eig(Mc)
    K = vect[:, 1].real
    cci = (K - np.mean(K)) / np.std(K)
    d = diversity(m)
    corr = np.corrcoef(np.squeeze(d.values), np.squeeze(cci))
    if (corr[0, 1] < 0):
        cci = -cci

    #Computes second largest eigenvector of M_tilde for dimension2
    val, vect = np.linalg.eig(Mp)
    K = vect[:, 1].real
    fci = -(np.mean(K) - K) / np.std(K)
    u = ubiquity(m)
    corr = np.corrcoef(np.squeeze(u.values), np.squeeze(fci))
    if (corr[0, 1] > 0):
        fci = -fci

    return pd.DataFrame(cci, index=Mc.index, columns=['q1']).reset_index(), \
           pd.DataFrame(fci, index=Mp.index, columns=['q2']).reset_index()


def function_proximity(m):
    """
    Compute the proximity between each pair of function in the dataset, defined by how
    likely they are to be competitively exported together.

    :param m: (Dataframe)  M binary RCA matrix
    :return: (Dataframe) Proximity matrix where [i,j] is the proximity metric between function fi and fj
    """

    sim = pd.DataFrame(np.dot(m.T, m), index=m.columns, columns=m.columns)
    u = ubiquity(m).to_dict()
    denom = [[np.max([u[fi], u[fj]]) for fi in m.columns] for fj in m.columns]
    sim = sim.divide(pd.DataFrame(denom, index=m.columns, columns=m.columns))
    return sim


def distance_to_function(m):
    """
    Compute the distance of each instance of dimension1 to each function

    :param m: (Dataframe) M binary RCA matrix
    :return: D (Dataframe) Matrix of distances where [c,f] is the distance to
            function f of c
    """
    P = function_proximity(m)
    sum_prox = P.sum(axis=0)
    D = pd.DataFrame(np.dot(1 - m, P), index=m.index, columns=m.columns).div(sum_prox, axis='columns')
    return D



def have_developed(df_data, dimension1, y1, y2, binary=True):
    """
    Identifies which instance of dimension1 have developed (Y), their RCA to >1 which function on a specified period
    and which have not (N)

    :param df_data: (Dataframe) each row is an instance of dimension1 in a YEAR, other columns are functions.
    :param dimension1: (str) first dimension of the problem (name of the column in df_data)
    :param y1: Year 1
    :param y2: Year 2
    :return: Y (Dataframe) matrix with 1 in [c,f] if c has developed function f between y1 and y2 (not before)
            N (Dataframe) matrix with 1 in [c,f] if c has not developed function f between y1 and y2
    """
    m1 = build_m(df_data, dimension1, y1, binary)
    m2 = build_m(df_data, dimension1, y2, binary)
    inter = m1.index.intersection(m2.index)
    m1 = m1.loc[inter]
    m2 = m2.loc[inter]
    # Get differences of matrices m at time y1 and y2
    if binary :
        # Test if gone from 0 to 1
        Y = ((m1 == 0) & (m2 == 1)).replace(np.nan, False).astype(int)
        N = ((m2 == 0) & (m1 == 0)).replace(np.nan, False).astype(int)
    else :
        # Test if gone from <0.5 to >1
        Y = ((m1 < 0.5) & (m2 > 1)).replace(np.nan, False).astype(int)
        N = ((m1 < 0.5) & (m2 < 0.5)).replace(np.nan, False).astype(int)
    return Y, N


def distance_before_dev(df_data, dimension1, y1, y2):
    """
    Compute the comparison of the average distance of communities
    to functions that were developed and functions that weren't.

    :param df_data: (Dataframe) each row is an instance of dimension1 in a YEAR, other columns are functions.
    :param dimension1: (str) first dimension of the problem (name of the column in df_data)
    :param y1: (int) Year 1, beginning of period of interest
    :param y2: (int) Year 2, end of period of interest
    :return: (Series) For each function in the dataset, ratio of the average distance of dimension1 that developed that
                    function over average distance of dimension1 that did not develop that function
    """
    Y, N = have_developed(df_data,dimension1,y1, y2)
    D = distance_to_function(build_m(df_data, dimension1, y1))
    y = Y.sum(axis=0)
    n = N.sum(axis=0)
    H1 = pd.Series(np.diag(np.dot((D.transpose()), Y)), index=Y.columns).div(y, axis='index')
    H2 = pd.Series(np.diag(np.dot((D.transpose()), N)), index=Y.columns).div(n, axis='index')
    H = H1.div(H2, axis='index')
    return H


def proba_to_develop(df_data, dimension1, phi, y1, y2):
    """
    Generate the probability of developing a new RCA in a function if the proximity of the closest connected
    function is lower than a threshold.

    :param phi: (float) threshold
    :param dimension1: (str) first dimension of the problem (name of the column in df_data)
    :param y1: (int) Year 1, beginning of period of interest
    :param y2: (int) Year 2, end of period of interest
    :return: (Series) For each function, proba of developing an RCA if the proximity of the closest connected
                function is lower than phi, based on the evolution between y1 and y2
    """
    T, N = have_developed(df_data, dimension1, y1, y2)
    m = build_m(df_data, dimension1, y1)
    prox = function_proximity(m)
    prox_close = (prox > phi).astype(int)
    ready = pd.DataFrame(np.dot(m, prox_close), index=m.index, columns=m.columns)
    inter = (ready & T).astype(int).sum()
    prob = inter.div(ready.sum(), axis='index')
    return prob



def plot_product_space(m, functional_comp, instance1=None, thresh=0.3,
                       savepath=None, title=None):
    """
    Plot the general functional space
    If an instance of dimension1 is specified, greys out functions for which this instance of dimension1
    has an RCA<1

    :param m: (Dataframe) Matrix M
    :param functional_comp: (Series) Functional complexity series, whose index values are locus codes
    :param instance1: (int) instance of dimension1 to draw the functional space for
                    if function M[c,f]=0 the node of f is grey in c's functional space
    :param thresh: (float) threshold on proximity between two functions,
                    if sim(fi,fj)>threshold : draw an edge between the nodes of fi and fj
    :param savepath: (str) path of the saved figure
    :param title: (str) title of the figure
    :return: None
    """
    dimension1_bipart = m

    prox = function_proximity(m).values

    # Build similarity graph
    graph = nx.Graph()
    for r in range(prox.shape[0]):
        for c in range(prox.shape[1]):
            graph.add_edge(r, c, weight=1 - prox[r, c] + 0.00001)

    # Generate maximum spanning tree
    mst = nx.minimum_spanning_tree(graph)
    for u, v in mst.edges():  # Reweight edges uniformly for visual
        mst[u][v]['weight'] = 1

    # Add other strong edges
    while (np.max(prox) > thresh):
        (r, c) = np.unravel_index(np.argmax(prox), prox.shape)
        if ((r, c) not in mst.edges()):
            mst.add_edge(r, c, weight=1)
        prox[r, c] = 0

    # Plot
    plt.figure(figsize=(12, 12))

    if (title):
        plt.title(title)

    labels = {i: val for i, val in enumerate(list(functional_comp.index.values))}
    colors = [cc.color(val) for key, val in enumerate(list(functional_comp.index.values))]
    layout = nx.kamada_kawai_layout(mst)

    if (instance1 is not None):
        presence = dimension1_bipart.loc[instance1]
        for ind, code in enumerate(list(functional_comp.index.values)):
            if ((code not in presence.index) or (presence[code] == 0)):
                colors[ind] = cc.LIGHT_GRAY

    nx.draw_networkx(mst, pos=layout, labels=labels,
                     node_size=500 * np.exp(functional_comp.iloc[:,0]) + 100, node_color=colors,
                     edge_color=cc.BLUE_GRAY,
                     sfont_size=10)

    graph.clear()
    if (savepath is not None):
        savepath = os.path.join(dirname, '../results/' + savepath)
        plt.savefig(savepath)
    plt.interactive(False)
    plt.show()
    plt.gcf().clear()

