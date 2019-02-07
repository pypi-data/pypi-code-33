

"""
This script calls the gas simulation for the different pressure levels. It starts with the lower levels and
run through each level. It also manage the output from the simulation.
"""

import fluids
from thermo.chemical import Chemical
from scipy.optimize import minimize
from scipy.sparse.linalg import lsqr
from numpy.linalg import pinv
import operator
import numpy as np

import osem.networks.pandangas.utilities as uti
import osem.networks.pandangas.network_creation as net_create
import osem.networks.pandangas.simulation_tool as simtool

# initial conditions for the minimisation, need to be global to be stopped during the run
global sol0


def runpg(net, solver_option=None):
    """
    This is the main function used to run a pandangas simulation
    :param net: A pandangas network
    :param solver_option: the option for the solver
    :return:
    """

    # prepare simulation
    net = uti.erase_results(net)
    net = uti._create_empty_result(net)
    net_create.set_solver_option(net, solver_option)

    # check
    uti.check_duplicates(net)

    # order level
    sorted_levels = sorted(net.levels.items(), key=operator.itemgetter(1))

    # pass through each level
    for level, value in sorted_levels:
        if level in net.bus["level"].unique():

            # run simulation for one pressure level
            print("Compute level {}".format(level))
            net = _run_sim_by_level(net, level)

    return net


def _run_sim_by_level(net, level):
    """
    This function computes the gas simulation for one level
    :param net: the pangandgas network
    :param level: the considered pressure level
    :return: a pandasgas network
    """

    # gas parameter
    level_value = net.levels[level]
    fluid_type = Chemical("natural gas", T=net.temperature, P=level_value * net.corr_pnom + net.p_atm)

    # select data for this pressure level
    netnx = uti.create_nxgraph(net, level=level)
    bus_level = net.bus.loc[net.bus['level'] == level, :]
    feeder_level = net.feeder.loc[net.feeder["bus"].isin(bus_level.index), :]
    station_level = net.station.loc[net.station["bus_low"].isin(bus_level.index), :]
    load_level = net.load.loc[net.load["bus"].isin(bus_level.index), :]

    # get the data by edge for this level
    p_names = uti._get_data_by_edge(netnx, 'name')
    materials = uti._get_data_by_edge(netnx, "mat")
    roughness = np.array([fluids.material_roughness(m) for m in materials])
    leng = uti._get_data_by_edge(netnx, "L_m")
    diam = uti._get_data_by_edge(netnx, "D_m")

    # add load (with the load linked to a station of a lower pressure level) and give these masses to the nodes
    load_level, total_loads = simtool._scaled_loads(net, load_level, level)
    m_dot_nodes, ind_feeder = simtool._create_node_mass(netnx, bus_level, load_level)

    # incidence matrix (so a matrix which says which node are connected to which edge)
    i_mat = simtool._i_mat(netnx)
    if net.solver_option['disp']:
        print('incidence matrix: done.')

    # modify i_mat so that the unknown linked with the solver are on the left side of the "equation"
    mat_all, row0, col0 = simtool._i_mat_with_feeder(i_mat, ind_feeder)

    # get null space for the mass (so that the space with all possible solutions form the matrix)
    z_i_mat = simtool.qr_null(mat_all)
    nullity_mass = z_i_mat.shape[1]  # how many freedom degrees

    # get one solution to the equation representing mass conservation
    res = lsqr(mat_all, m_dot_nodes, atol=net.solver_option['tol_mat_mass'], btol=net.solver_option['tol_mat_mass'])
    sol0 = res[0]
    if net.solver_option['disp']:
        print('find null space for the mass equation: done.')

    # obtain the pseudo inverse matrix for the pressure equation (so the matrix which find the closest solution)
    mat_pres = simtool.i_mat_for_pressure(i_mat, ind_feeder)
    pinv_pres = pinv(mat_pres)
    p_noms = [level_value]*len(ind_feeder)
    if net.solver_option['disp']:
        print('find pseudo-inverse matrix for the pressure equation: done.')

    # if we have more than one possibility as solution, minimize
    if nullity_mass > 0:
        m0 = np.random.rand(nullity_mass)
        args_mass = (z_i_mat, sol0, net.v_max, diam, row0, col0, leng, roughness, fluid_type,
                     net.solver_option, pinv_pres, p_noms, mat_pres, mat_all, m_dot_nodes)
        options = {'maxiter': net.solver_option['maxiter'], 'gtol': net.solver_option['gtol'],
                   'disp': net.solver_option['disp']}
        _compute_mass_and_pres.niter = 0  # attach a variable to a function

        try:
            # As we have more than on solution, we test many of them to find the one which fits the pressure equ.
            res = minimize(_compute_mass_and_pres, m0, method='BFGS', args=args_mass, options=options)
            # all solution are the  "basic" solution + residual, cf. linear algebra.
            print(res)
            sol = sol0 + z_i_mat.dot(res.x)
        except SmallEnoughGoodException:
            sol = sol0 + z_i_mat.dot(res.x)
    else:
        sol = sol0

    # separate the result
    m_dot_pipes = sol[:col0]
    m_dot_nodes[ind_feeder] = sol[col0:]

    # compute load and velocity
    v, load_pipes = simtool._v_from_m_dot(diam, m_dot_pipes, fluid_type, net.v_max)

    # copmute pressure
    print(m_dot_pipes)
    p_loss = simtool._dp_from_m_dot_vec(m_dot_pipes, leng, diam, roughness, fluid_type)*(-1)
    p_loss = np.append(p_loss, p_noms)
    p_nodes = pinv_pres.dot(p_loss)
    if nullity_mass > 0 and net.solver_option['disp']:
        simtool._print_minimize_state(p_nodes, res.fun, _compute_mass_and_pres.niter)

    # output bus
    r_num = net.solver_option['round_num']
    netnx_node = list(netnx.node)
    net.res_bus.loc[netnx_node, "p_Pa"] = np.round(p_nodes,r_num)
    net.res_bus.loc[netnx_node, "p_bar"] = np.round(p_nodes * 1e-5, r_num)
    net.res_bus.loc[netnx_node, "m_dot_kg/s"] = np.round(m_dot_nodes, r_num)
    net.res_bus.loc[netnx_node, "p_kW"] = np.round(m_dot_nodes * net.lhv, r_num)

    # output pipe
    net.res_pipe.loc[p_names, "m_dot_kg/s"] = np.round(m_dot_pipes, r_num)
    net.res_pipe.loc[p_names, "p_kW"] = np.round(m_dot_pipes * net.lhv, r_num)
    net.res_pipe.loc[p_names, "v_m/s"] = np.round(v, r_num)
    net.res_pipe.loc[p_names, "loading_%"] = np.round(load_pipes,r_num)

    # output feeder
    f_names = feeder_level.index
    net.res_feeder.loc[f_names, "m_dot_kg/s"] = net.res_bus.loc[feeder_level["bus"].values, "m_dot_kg/s"].values
    net.res_feeder.loc[f_names, "p_kW"] = net.res_bus.loc[feeder_level["bus"].values,"p_kW"].values
    loading_feeder = np.abs(100 * net.res_feeder.loc[f_names, "p_kW"] / net.feeder.loc[f_names, "p_lim_kW"])
    loading_feeder = loading_feeder.astype(float)
    net.res_feeder.loc[f_names, "loading_%"] = np.round(loading_feeder.values, r_num)

    # output station
    s_names = station_level.index
    net.res_station.loc[s_names, "m_dot_kg/s"] = net.res_bus.loc[station_level["bus_low"].values, "m_dot_kg/s"].values
    net.res_station.loc[s_names, "p_kW"] = net.res_bus.loc[station_level["bus_low"].values, "p_kW"].values
    loading_station = np.abs(100 * net.res_station.loc[s_names, "p_kW"] / net.station.loc[station_level.index, "p_lim_kW"])
    loading_station = loading_station.astype(float)
    net.res_station.loc[s_names, "loading_%"] = np.round(loading_station.values, r_num)

    return net


def _compute_mass_and_pres(m0, *args):
    """
    This function compute the mass, knowning a first solution to the equation and the null of the modified incidence
    maxtrix. It return the man of the pressure loss which is minimized.
    :return:
    """
    z_i_mat, sol1, v_max, diam, row0, col0, leng, roughness, fluid_type, solver_option, pinv_pres, p_noms, \
    mat_pres,mat_all, m_dot_nodes= args

    # get new solution from "basic" solution
    m_here = sol1 + z_i_mat.dot(m0)
    m_here = m_here[:col0]

    # loss of pressure in each pipes
    p_loss = simtool._dp_from_m_dot_vec(m_here, leng, diam, roughness, fluid_type)* (-1)
    p_loss = np.append(p_loss, p_noms)

    # equations for the pressure (should be zero, so minize residual)
    p_nodes = pinv_pres.dot(p_loss)
    residual = np.sum(np.abs(mat_pres.dot(p_nodes) - p_loss))

    if solver_option['disp'] and _compute_mass_and_pres.niter%solver_option['iter_print'] == 0:
        simtool._print_minimize_state(p_nodes, residual, _compute_mass_and_pres.niter)
    _compute_mass_and_pres.niter+=1

    if abs(residual) < solver_option['min_residual']:
        # raise SmallEnoughGoodException
        return residual
    else:
        return residual


class SmallEnoughGoodException(Warning):
    """
    The scipy.minimize function cannot be stopped if the function value reach a certain level considered small enough
    (like 100% load for example). So this is a hack to be able to do this anyway. So this class is not an exception, it
    is a way to stop the function.
    """
    pass

