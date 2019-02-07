# this script contains the function used to support the simulation (i.e. all stuff used by run_simulation.py)

import numpy as np
import networkx as nx
from math import pi
from scipy.sparse.linalg import lsqr
from scipy.linalg import qr
import fluids.vectorized as fvec


def _scaled_loads(net, load_level0, level):
    """
    This function passes the loads from kW to kg/s using the LHV parameter and add the load linked
    to the station of the lower pressure network
    :param the pandangas network
    :param load_level0: the load from this level in a Dataframe
    :param lhv: param to pass from kW to kg/s
    :param level: the gas level (string)
    :return: load_level with a new column load
    """

    # pass from kWh to kg/sec
    load_level = load_level0.copy()  # avoid warning
    load_level.loc[:, 'load_kg_s'] = (load_level.loc[:, "scaling"] * load_level.loc[:, "p_kW"]) / net.lhv

    # add load from the stations
    for _, row in net.res_station.iterrows():
        bushigh = net.station.at[row.name, "bus_high"]
        if net.bus.loc[bushigh, "level"] == level:
            load_level.loc[bushigh, 'load_kg_s'] = abs(round(row[0], net.solver_option['round_num']))

    total_loads = sum(load_level["load_kg_s"])

    return load_level, total_loads


def _i_mat(graph):
    """
    the incidence matrix of the gas network for this pressure level
    :param graph: a networkx graphc
    """
    return np.asarray(nx.incidence_matrix(graph, oriented=True).todense())


def _i_mat_with_feeder(i_mat, ind_feeder):
    """
    This function modify i_mat so that all the unknown are on the left side of the equation.
    So at first we have Ax = b where b are the load. We known the loads apart from the loads in the feeder. Let separe
    b in to b0 (the usual load) and bf the load from the feeder. So we have Ax-bf = b0. Now, bf is in fact more unknown.
    So let's find a matrix B so that Bx'=b0 where x' is the concatenation of x and bf. B has len(bf) more column than
    A. The value at the added column i is the values bf[i].

    We than add one equation to ensure that the total loads is equal to the mass enterting the feeder

    :param i_mat: the incidence matrix
    :param ind_feeder: the index where a feeder is
    :return: the modified incidence matrix with the additional equation and its orginal size
    """

    # orginal size of incidence matrix
    row0 = i_mat.shape[0]
    col0 = i_mat.shape[1]

    # add extra empty column to B
    nb_feeder = len(ind_feeder)
    null_mat = np.zeros((row0, nb_feeder))
    i_mat = np.append(i_mat, null_mat, axis=1)

    # if a feeder is present at this line,  add a minus one to account fo rit
    for i, f in enumerate(ind_feeder):
        i_mat[f, col0+i] = -1

    return i_mat, row0, col0


def i_mat_for_pressure(i_mat, ind_feeder):
    """
    This function add to the matrix representing the equations of the pressure (saying that the pressure loss
    is equal to the pressure difference between two nodes) the "equations" saying that the feeder is at the nominal
    pressure
    :return:
    """
    mat_pres = i_mat.T

    # add equation saying that the pressure at the feeder is the nominal pressure (p_feeder0)

    np.set_printoptions(threshold=np.nan)

    feeder_equ = np.zeros((1, mat_pres.shape[1]))
    for i, f in enumerate(ind_feeder):
        feeder_equ2 = np.copy(feeder_equ)
        feeder_equ2[0, f] = 1
        mat_pres = np.append(mat_pres, feeder_equ2, axis=0)

    return mat_pres


def qr_null(A, tol=None):
    """Computes the null space of A using a rank-revealing QR decomposition. This is a ready made function
    from another project"""
    Q, R, P = qr(A.T, mode='full', pivoting=True)
    tol = np.finfo(R.dtype).eps if tol is None else tol
    rnk = min(A.shape) - np.abs(np.diag(R))[::-1].searchsorted(tol)
    return Q[:, rnk:].conj()


def _create_node_mass(netnx, bus_level, load_level):
    """
    This function create the mass for the node and add nan if the mass is to be found (feeder).
    It also return the index where the feeder/station is and the sum of the load
    :param netnx: the networkx graph for this pressure level
    :param bus_level: the bus ofr this level
    :param load_level: the load for this level
    :return:
    """

    m_dot_nodes = np.zeros(len(netnx.nodes))
    ind_feeder = []
    for i, b in enumerate(netnx.nodes):
        if b in bus_level.index:
            if bus_level.loc[b, "type"] == "SINK":
                m_dot_nodes[i] = load_level.loc[load_level['bus'] == b, 'load_kg_s'].values[0]
            elif bus_level.loc[b, "type"] == "NODE":
                m_dot_nodes[i] = 0
            elif bus_level.loc[b, "type"] == "SRCE":
                m_dot_nodes[i] = 0
                ind_feeder.append(i)

    return m_dot_nodes, np.array(ind_feeder)


def _v_from_m_dot(diameter, m_dot, fluid, v_max):
    """
    get the velocity and the load in the pipe (lod in %)
    :param diameter: the diamter of the pipe
    :param m_dot: the mass in the pipe
    :param fluid: the characterisitc of the fluid
    :return: the velocity and the load in the pipe
    """
    q = m_dot / fluid.rho
    a = pi * diameter ** 2 / 4
    v = q /a
    return v, abs(100 * v / v_max)


def _eq_mass_pipe(m_dot_nodes, i_mat, tol_mat_mass):
    """
    compute the mass in the pipes knowning the mass in the nodes assuming i_mat is sparse
    :param m_dot_nodes: the mass at the node (full, so with an hyopthesis on the mass at the feeder)
    :param i_mat: incidence matrix
    :param m_dot_pipes: np.array - the mass in the pipe
    """

    res = lsqr(i_mat, m_dot_nodes, atol=tol_mat_mass, btol=tol_mat_mass)
    m_dot_pipes = res[0]

    return m_dot_pipes


def _dp_from_m_dot_vec(m_dot, l, d, e, fluid):
    """
    Compute pressure loss using fluids library
    """
    a = pi * (d / 2) ** 2
    v = (m_dot / fluid.rho) / a
    v[v==0] = 1e-7
    re = fvec.core.Reynolds(v, d, fluid.rho, fluid.mu)
    fd = fvec.friction_factor(re, eD=e / d)
    k = fvec.K_from_f(fd=fd, L=l, D=d)
    return fvec.dP_from_K(k, rho=fluid.rho, V=v)


def _print_minimize_state(p_nodes, residual, iter):
    """
    This function print the current state of the minimization for the pressure equation
    :param p_nodes: the pressure in the nodes
    :param residual: the resiudal of the pressure equation
    :param iter: the current iteration
    """
    print('----------------------------------------------------------------------')
    print('Current State for the Minimization for Iteration ' + str(iter))
    print("The current pressure minimum: " + str(np.min(p_nodes)))
    print("The current pressure maximum: " + str(np.max(p_nodes)))
    print("The current pressure mean: " + str(np.mean(p_nodes)))
    print("The current residual is : " + str(residual))


