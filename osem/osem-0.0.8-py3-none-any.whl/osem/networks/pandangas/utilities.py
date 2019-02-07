
# this script contains helper function for the pandansgas network
import pandas as pd
import numpy as np
import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import operator
import fluids
from thermo.chemical import Chemical

import osem.networks.pandangas.network_creation as net_create
import osem.networks.pandangas.simulation_tool as simtool


def check_network_result(net, lim_mass=1e-4, lim_pres=2):
    """
    This functions check if the result of a simulation makes sens. to this end, mass conservation and
    pressure conservation are computed
    :param net: A pandagas network which have been simulated (so net.res_bus exists)
    :param lim_mass: An accecptable error on the mass
    :return: True if network satisfy the conditions of mass and pressure conservation , False otherwise
    """

    # check conservation of mass
    if abs(net.res_bus["m_dot_kg/s"].sum()) > lim_mass:
        return False

    # check for pressure conservation for each level
    sorted_levels = sorted(net.levels.items(), key=operator.itemgetter(1))
    for level, value in sorted_levels:
        if level in net.bus["level"].unique():

            # get network
            netnx = create_nxgraph(net, level=level)
            i_mat = simtool._i_mat(netnx)

            # get ind feeder
            bus_level = net.bus.loc[net.bus['level'] == level, :]
            load_level = net.load.loc[net.load["bus"].isin(bus_level.index), :]
            load_level, total_loads = simtool._scaled_loads(net, load_level, level)
            m_dot_nodes, ind_feeder = simtool._create_node_mass(netnx, bus_level, load_level)

            # get data for this level
            level_value = net.levels[level]
            fluid_type = Chemical("natural gas", T=net.temperature, P=level_value + net.p_atm)
            materials = _get_data_by_edge(netnx, "mat")
            roughness = np.array([fluids.material_roughness(m) for m in materials])
            leng = _get_data_by_edge(netnx, "L_m")
            diam = _get_data_by_edge(netnx, "D_m")
            name_pipe = _get_data_by_edge(netnx, "name")
            m_dot_pipes = net.res_pipe.loc[name_pipe,"m_dot_kg/s"].values
            p_nodes = net.res_bus.loc[np.array(netnx.nodes),"p_Pa"].values

            # make the matrix multiplication (should be null)
            mat_pres = simtool.i_mat_for_pressure(i_mat, ind_feeder)
            p_loss = simtool._dp_from_m_dot_vec(m_dot_pipes, leng, diam, roughness, fluid_type) * (-1)
            p_loss = np.append(p_loss, [level_value] * len(ind_feeder))
            res = mat_pres.dot(p_nodes) - p_loss
            if abs(sum(res)) > lim_pres:
                return False

    return True


def check_for_empty_load(net, default_load=0):
    """
    Pandangas do not function if there are pipe which are at the network end without a load. This function
    check that all end pipes have a load. If not, it changes these end pipes to a loaf of the default_load values.
    :param net: a pandangaz network
    :param default_load: the load to add to "alone" pipe
    :return: net: an updated pandangas network with no end pipe without a load
    """
    # get all pipe at the end of the network
    once_in_to_bus = net.pipe.loc[net.pipe.groupby('to_bus').to_bus.transform(len) == 1, :]
    load_all = once_in_to_bus.loc[~once_in_to_bus.to_bus.isin(net.pipe['from_bus']), 'to_bus']
    # get what type is the end nodes
    type_bus_end = net.bus.loc[net.bus.index.isin(load_all), ['name', 'type']]
    if 'NODE' in type_bus_end.values:
        load_to_be_corrected = type_bus_end.loc[type_bus_end['type'] == 'NODE', :]
    else:
        return net

    # correct load
    for i, li in enumerate(load_to_be_corrected.index):
        net_create.create_load(net, li, p_kW=default_load, name='ADDED_LOAD' + str(i))
    return net


def check_duplicates(net):
    """
    This function check for duplicate names in a pandasgas network. It raise an error if there is duplcate names
    :param net: a pandasgas network
    :return: None
    """
    if np.any(net.bus.index.duplicated()):
        raise KeyError('Duplicated name in the network bus are not supported.')
    if np.any(net.bus.index.duplicated()):
        raise KeyError('Duplicated name in the network pipes are not supported.')
    if np.any(net.bus.index.duplicated()):
        raise KeyError('Duplicated name in the network stations are not supported.')
    if np.any(net.bus.index.duplicated()):
        raise KeyError('Duplicated name in the network feeders are not supported.')


def erase_results(net):
    """
    This function erase the result of a simulation. Automatically done at a start of a new simulation.
    :param net: a pandangas network
    :return the same network with empty result
    """
    net.res_bus.drop(net.res_bus.index, inplace=True)
    net.res_pipe.drop(net.res_pipe.index, inplace=True)
    net.res_feeder.drop(net.res_feeder.index, inplace=True)
    net.res_station.drop(net.res_station.index, inplace=True)

    return net


def create_nxgraph(net, level=None, only_in_service=True, directed=True):
    """
    Convert a given network into a NetworkX MultiGraph for particular level or for all level if level is set to None.

    :param net: the given network
    :param level: the name of pressure level of interest (string)
    :param only_in_service: if True, convert only the pipes that are in service (default: True)
    :param directed: If true, create a directed graph, otherwise undirected
    :return: a MultiGraph
    """

    if directed:
        g = nx.MultiDiGraph()
    else:
        g = nx.Graph()

    # create node
    if level is None:
        for idx, row in net.bus.iterrows():
                g.add_node(row.name)
    else:
        for idx, row in net.bus.iterrows():
            if row[0] == level:
                g.add_node(row.name)

    # create edge
    pipes = net.pipe
    if only_in_service:
        pipes = pipes.loc[pipes["in_service"]]
    for idx, row in pipes.iterrows():
        if row[0] in g.nodes() or row[1] in g.nodes():
            g.add_edge(row[0], row[1], name=row.name, type="PIPE", L_m=row[2], D_m=row[3], mat=row[4])

    # create edge at station if multi-level network
    if level is None:
        for idx, row in net.station.iterrows():
            g.add_edge(row[0], row[1], name=row.name, type="STATION")

    return g


def _get_data_by_edge(netnx, data_type):
    """
    This function return the data ordered as the edge of the network
    :param netnx: the graph
    :param data_type: the type of data need
    :return: an np.array iwht the data ordered as in the edge
    """
    data_by_edge = np.array([data[data_type] for _, _, data in netnx.edges(data=True)])

    return data_by_edge


def _create_empty_result(net):
    """
    This function creates a list of dataframe with all result value set to zeros
    :param net:
    :return: a net with res_bus, res_pipe, res_feeder and res_station at a value of zeros
    """

    net.res_bus = pd.DataFrame(0, index=net.bus.index, columns=net.res_bus.columns)
    net.res_pipe = pd.DataFrame(0, index=net.pipe.index, columns=net.res_pipe.columns)
    net.res_feeder = pd.DataFrame(0, index=net.feeder.index, columns=net.res_feeder.columns)
    net.res_station = pd.DataFrame(0, index=net.station.index, columns=net.res_station.columns)

    return net


def draw_network_gas(net, pos=None, show=True):
    """
    This function plot a gas network created by pandangaz.
    :param net: A network created by pandangaz
    :param pos: The coordinates of the node (optional)
    :param show: If True, it will show the figure now
    """
    # prepare a network for plotting
    net_draw = create_nxgraph(net, directed=False)
    bus_load = net.bus.loc[net.bus['type'] == 'SINK', :].index.tolist()
    bus_feeder = net.bus.loc[net.bus['type'] == 'SRCE', :].index.tolist()
    name_feeder_sta = {k:v for (k,v) in zip(bus_feeder, bus_feeder)}

    # position of the nodes
    if not pos:
        pos = nx.spring_layout(net_draw)

    # plot
    plt.figure()
    try:
        nx.draw(net_draw, pos, node_size=2, node_color='black', label='Node', with_labels=False, font_size=12)
    except ValueError:
        print('ValueError: you might have pipes with NULL position.')
    nx.draw_networkx_nodes(net_draw, pos,
                           nodelist=bus_load,
                           node_color='r',
                           node_size=10,
                           label='Load')
    nx.draw_networkx_nodes(net_draw, pos,
                           nodelist=bus_feeder,
                           node_color='g',
                           node_size=10,
                           label='Feeders and Stations')
    nx.draw_networkx_labels(net_draw, pos, labels=name_feeder_sta)
    plt.legend()

    if show:
        plt.show()


def draw_results(net, pos=None, show=True, maxloading=300):
    """
    This function plot the output from a pandas gaz models. No plt.show() in the function.
    :param net: A network created by pandangaz
    :param pos: The coordinates of the node (optional)
    :param show: If Tue, the result are shown
    :param maxloading: for the colorbar, the max of the load (sometimes there are short pipe with high load)
    """
    # prepare a network for plotting
    net_draw = create_nxgraph(net, directed=False)

    # order output
    res_bus_ordered = net.res_bus
    res_bus_ordered = res_bus_ordered.reindex(net_draw.nodes())
    order_edge = [data['name'] for (u, v, data) in net_draw.edges(data=True)]
    res_pipe_ordered = net.res_pipe
    res_pipe_ordered = res_pipe_ordered.reindex(order_edge)

    # get the result for mass and pressure
    mass_res = res_pipe_ordered['m_dot_kg/s'].values
    loading = res_pipe_ordered['loading_%'].values
    pressure_nodes = res_bus_ordered['p_Pa'].values
    mass_nodes = np.abs(res_bus_ordered["m_dot_kg/s"].values)

    # position of the nodes
    if not pos:
        pos = nx.spring_layout(net_draw)
    cmap = plt.cm.get_cmap('jet')

    # plot the network
    draw_network_gas(net, pos=pos, show=False)

    # plot the loads
    plt.figure()
    vmin = min(loading)
    vmax = maxloading
    plt.title('Pipe Loading')
    try:
        nx.draw(net_draw, pos, node_size=1, node_color='black', edge_color=loading,
                    edge_cmap=cmap, width=3, with_labels=False, font_size=12,edge_vmin=vmin,edge_vmax=vmax)
    except ValueError:
        print('ValueError: you might have pipes with NULL position.')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, shrink=.6)
    cbar.set_label('Load [%]', rotation=270, labelpad=15)
    plt.legend()

    # plot the mass in the pipe
    plt.figure()
    vmin = min(mass_res)
    vmax = max(mass_res)
    plt.title('Mass in pipe')
    try:
        nx.draw(net_draw, pos, node_size=1, node_color='black', edge_color=mass_res,
                edge_cmap=cmap, width=3, with_labels=False, font_size=12, edge_vmin=vmin, edge_vmax=vmax)
    except ValueError:
        print('ValueError: you might have pipes with NULL position.')
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, shrink=.6)
    cbar.set_label('Discharge mass [kg/sec]', rotation=270, labelpad=15)
    plt.legend()

    # plot the pressure in the nodes
    plt.figure()
    vmin = min(pressure_nodes)
    vmax = max(pressure_nodes)+1
    plt.title('Pressure - Gas Nodes')
    nx.draw_networkx(net_draw, pos, node_size=30, node_color=pressure_nodes, cmap=cmap, with_labels=False, font_size=12,
            vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, shrink=.6)
    cbar.set_label('Pressure [Pa]', rotation=270, labelpad=15)
    plt.legend()

    # plot the mass in the nodes
    vmin = min(mass_nodes)
    vmax = max(mass_nodes)
    cmap = plt.cm.get_cmap('bwr')
    plt.figure()
    plt.title('Discharge Mass Nodes')
    nx.draw_networkx(net_draw, pos, node_size=10, node_color=mass_nodes, cmap=cmap, with_labels=False, font_size=12,
                     vmin=vmin, vmax=vmax)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, shrink=.6)
    cbar.set_label('Discharge mass [kg/sec]', rotation=270, labelpad=15)
    plt.legend()

    if show:
        plt.show()


def save_pandangas_net(net, netname, pathdir=None, save_result=False):
    """
    This function save a pandangaz network to csv files (one csv by dataframe in a folder)
    :param net: the pandasgas network
    :param netname: the name of thei network (string)
    :param pathdir: the path where to save the file (by default current path)
    :param save_result: If True, save the model result also
    """

    # get path and save directory
    if pathdir is None:
        pathdir = os.path.join(os.getcwd(), netname)
    else:
        pathdir = os.path.join(pathdir, netname)
    if not os.path.isdir(pathdir):
        os.makedirs(pathdir)

    # save data
    dataframe_name = ['pipe.csv', 'bus.csv', 'load.csv', 'feeder.csv', 'station.csv']
    dataframe_val = [net.pipe, net.bus, net.load, net.feeder, net.station]
    for id, d in enumerate(dataframe_name):
        dataframe_val[id].to_csv(os.path.join(pathdir, d))

    # save result
    if save_result:
        dataframe_name = ['pipe_res.csv', 'bus_res.csv', 'feeder_res.csv', 'station_res.csv']
        dataframe_val = [net.res_pipe, net.res_bus, net.res_feeder, net.res_station]
        for id, d in enumerate(dataframe_name):
            dataframe_val[id].to_csv(os.path.join(pathdir, d))

# this function is commented as it would need two additional library which is a lot for OSEF
# import geopandas as gpd
# from shapely.geometry import Point, LineString
#
# def save_panandgas_as_shp(net, pos, netname, pathdir=None, crs=None):
#     """
#     This function save a pandagas as a shapefile
#     :param net: the pandas gas .net
#     :param pos: A dict with bus name as key and coordinate as value
#     :param netname: the name of the netpwork
#     :param path_dir: the path where to save the file (by default current path)
#     :param crs: the coordinate system of the file to save
#     """
#
#     # get path and save directory
#     if pathdir is None:
#         pathdir = os.path.join(os.getcwd(), netname)
#     else:
#         pathdir = os.path.join(pathdir, netname)
#     if not os.path.isdir(pathdir):
#         os.makedirs(pathdir)
#
#     # get the geometry for the bus
#     net.res_bus['geometry'] = None
#     for n in net.res_bus.index:
#         net.res_bus.loc[n, 'geometry'] = Point(pos[n])
#
#     # get the geometry for pipe
#     net.res_pipe['geometry'] = None
#     for n in net.res_pipe.index:
#         bus1 = net.pipe.loc[n, 'from_bus']
#         bus2 = net.pipe.loc[n, 'to_bus']
#         net.res_pipe.loc[n, 'geometry'] = LineString([pos[bus1], pos[bus2]])
#
#     # save bus
#     filebus = os.path.join(pathdir, netname + '_bus.shp')
#     net.res_bus = gpd.GeoDataFrame(net.res_bus, geometry='geometry')
#     if crs is not None:
#         net.res_bus.crs = crs
#     net.res_bus.to_file(filebus, driver='ESRI Shapefile')
#
#     # save pipes
#     filepipe = os.path.join(pathdir, netname + '_pipe.shp')
#     net.res_pipe = gpd.GeoDataFrame(net.res_pipe, geometry='geometry')
#     if crs is not None:
#         net.res_pipe.crs = crs
#     net.res_pipe.to_file(filepipe, driver='ESRI Shapefile')


def load_pandangaz_net(pathdir, get_initial_cond=False):
    """
    Load a pandasngas network which was created though the save_pandangas_net() function.
    :param pathdir: the path to the folder
    :return: a pandasgas network and the initial condition (if get_initial cond is True)
    """

    net = net_create.create_empty_network()
    net.pipe = pd.read_csv(os.path.join(pathdir, 'pipe.csv'), index_col=0)
    net.bus = pd.read_csv(os.path.join(pathdir, 'bus.csv'), index_col=0)
    net.load = pd.read_csv(os.path.join(pathdir, 'load.csv'), index_col=0)
    net.feeder = pd.read_csv(os.path.join(pathdir, 'feeder.csv'), index_col=0)
    net.station = pd.read_csv(os.path.join(pathdir, 'station.csv'), index_col=0)

    if get_initial_cond:
        net.res_pipe = pd.read_csv(os.path.join(pathdir, 'pipe_res.csv'), index_col=0)
        net.res_bus = pd.read_csv(os.path.join(pathdir, 'bus_res.csv'), index_col=0)
        net.res_feeder = pd.read_csv(os.path.join(pathdir, 'feeder_res.csv'), index_col=0)
        net.res_station = pd.read_csv(os.path.join(pathdir, 'station_res.csv'), index_col=0)

        power_ini = {'bus':net.res_bus["p_kW"], 'pipe':net.res_pipe["p_kW"],'feeder':net.res_feeder["p_kW"],
                    'station':net.res_station["p_kW"]}

        return net, power_ini
    else:
        return net


def check_for_connectivity(net, pos=None, show=True):
    """
    This function check if all the nodes of a pandangaz network are connected. No check for pressure.
    :param net: A pandangas network
    :param show: If True, show an image with the different network when more than one network.
    :return: True if all connectec, False otherwise
    """
    net_nx = create_nxgraph(net, directed=False)
    sub_graphs = list(nx.connected_component_subgraphs(net_nx))
    nb_net = len(sub_graphs)
    if nb_net > 1:

        # plot the different networj (optional)
        if show:
            if not pos:
                pos = nx.spring_layout(net_nx)
            colors = list(mcolors.cnames)[9:] * 100  # avoid very light color at the start
            plt.figure()
            plt.title('Sub-networks')
            for iss, s in enumerate(sub_graphs):
                nx.draw(s, pos, node_size=1)
                if s.number_of_nodes() > 200:
                    label = 'Number of nodes: ' + str(s.number_of_nodes())
                    nx.draw_networkx_nodes(s, pos, node_size=10, node_color=colors[iss], label=label)
                else:
                    nx.draw_networkx_nodes(s, pos, node_size=10, node_color=colors[iss])
            plt.xlabel('x-coordinate [m]')
            plt.ylabel('y-coordinate [m]')
            plt.show()

        return False

    elif nb_net == 1:
        return True

    else:
        return False


