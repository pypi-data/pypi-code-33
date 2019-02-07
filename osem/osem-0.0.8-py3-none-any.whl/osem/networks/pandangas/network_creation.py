#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This script contains the class definition of a gas network and the function used to create this network
    and its components.

    Usage:

    import osef.pandangas as pg

    net = pg.create_empty_network()

    busf = pg.create_bus(net, level="MP", name="BUSF")
    bus0 = pg.create_bus(net, level="MP", name="BUS0")

    bus1 = pg.create_bus(net, level="BP", name="BUS1")
    bus2 = pg.create_bus(net, level="BP", name="BUS2")
    bus3 = pg.create_bus(net, level="BP", name="BUS3")

    pg.create_load(net, bus2, p_kW=10.0, name="LOAD2")
    pg.create_load(net, bus3, p_kW=13.0, name="LOAD3")

    pg.create_pipe(net, busf, bus0, length_m=100, diameter_m=0.05, name="PIPE0")
    pg.create_pipe(net, bus1, bus2, length_m=400, diameter_m=0.05, name="PIPE1")
    pg.create_pipe(net, bus1, bus3, length_m=500, diameter_m=0.05, name="PIPE2")
    pg.create_pipe(net, bus2, bus3, length_m=500, diameter_m=0.05, name="PIPE3")

    pg.create_station(net, bus0, bus1, p_lim_kW=50, p_Pa=0.025E5, name="STATION")
    pg.create_feeder(net, busf, p_lim_kW=50, p_Pa=0.9E5, name="FEEDER")

"""
import pandas as pd
import os
import json
import osem.general.conf as conf


class _Network:
    """"
    A class which define a pandangas network
    """
    def __init__(self):

        # data
        self._data_folder = conf.data_folder

        # default value
        self.levels = conf.default_levels  # Pa
        self.lhv = conf.lhv
        self.v_max = conf.v_max
        self.solver_option = conf.default_solver_option
        self.solver_info = self._load_solver_info()
        self.temperature = conf.temperature  # K
        self.p_atm = conf.p_atm  # Pa
        self.corr_pnom = conf.corr_pnom

        # component of the network
        self.bus = pd.DataFrame(columns=["level", "zone", "type"])
        self.pipe = pd.DataFrame(columns=["from_bus", "to_bus", "length_m", "diameter_m", "material", "in_service"])
        self.load = pd.DataFrame(columns=["bus", "p_kW", "min_p_Pa", "scaling"])
        self.feeder = pd.DataFrame(columns=["bus", "p_lim_kW", "p_Pa"])
        self.station = pd.DataFrame(columns=["bus_high", "bus_low", "p_lim_kW", "p_Pa"])

        # resultat of the simulation by components
        self.res_bus = pd.DataFrame(columns=["p_Pa", "p_bar", "m_dot_kg/s","p_kW"])
        self.res_pipe = pd.DataFrame(columns=["m_dot_kg/s", "v_m/s", "p_kW", "loading_%"])
        self.res_feeder = pd.DataFrame(columns=["m_dot_kg/s", "p_kW", "loading_%"])
        self.res_station = pd.DataFrame(columns=["m_dot_kg/s", "p_kW", "loading_%"])

        self.keys = ["bus", "pipe", "load", "feeder", "station", "res_bus", "res_pipe", "res_feeder", "res_station"]

    def _load_solver_info(self):
        """
        This function load a json file which details the information realted to the solver option
        :return: the info in a string
        """

        with open(os.path.join(self._data_folder, conf.filename_info_solver), 'r') as f:
            solver_explanation = json.load(f)
        return solver_explanation

    def __repr__(self):
        """
        implementation of the print function
        """
        r = "This pandangas network includes the following parameter tables:"
        par = []
        res = []
        for tb in self.keys:
            if len(getattr(self, tb)) > 0:
                if "res_" in tb:
                    res.append(tb)
                else:
                    par.append(tb)
        for tb in par:
            length = len(getattr(self, tb))
            r += "\n   - %s (%s %s)" % (
                tb,
                length,
                "elements" if length > 1 else "element",
            )
        if res:
            r += "\n and the following results tables:"
            for tb in res:
                length = len(getattr(self, tb))
                r += "\n   - %s (%s %s)" % (
                    tb,
                    length,
                    "elements" if length > 1 else "element",
                )

        return r


def _change_bus_type(net, bus, bus_type):
    """
    Bus can have three type: NODE, SRCE and LOAD. This function allows to change between these different type.

    :param net: a pandangas network
    :param bus: the bus whoses type should be changed
    :param bus_type: the bus type
    :return: none
    """

    old_type = net.bus.loc[bus, "type"]
    try:
        assert old_type == "NODE"
    except AssertionError:
        msg = "The buses {} is already a {} !".format(bus, old_type)
        raise ValueError(msg)

    net.bus.loc[bus, "type"] = bus_type


def _try_existing_bus(net, bus):
    """
    Check if a bus exist on a given network, raise ValueError and log an error if not

    :param net: the given network
    :param bus: the bus to check existence
    :return:
    """
    try:
        assert bus in net.bus.index
    except AssertionError:
        msg = "The bus {} does not exist !".format(bus)
        raise ValueError(msg)


def _check_level(net, bus_a, bus_b, same=True):
    """
    Check the pressure level of two buses on a given network, raise ValueError and log an error depending on parameter

    :param net: the given network
    :param bus_a: the first bus
    :param bus_b: the second bus
    :param same: if True, the method will check if the node have the same pressure level
    if False, the method will check if the node have different pressure levels (default: True)
    :return:
    """
    lev_a = net.bus.loc[bus_a, "level"]
    lev_b = net.bus.loc[bus_b, "level"]

    if same:
        try:
            assert lev_a == lev_b
        except AssertionError:
            msg = "The buses {} and {} have a different pressure level !".format(bus_a, bus_b)
            raise ValueError(msg)
    else:
        try:
            assert lev_a != lev_b
        except AssertionError:
            msg = "The buses {} and {} have the same pressure level !".format(bus_a, bus_b)
            raise ValueError(msg)


def create_empty_network():
    """
    Create an empty network

    :return: a Network object that will later contain all the buses, pipes, etc.
    """
    return _Network()


def create_bus(net, level, name, zone=None, check=True):
    """
    Create a bus on a given network

    :param net: the given network
    :param level: nominal pressure level of the bus
    :param name: name of the bus
    :param zone: zone of the bus (default: None)
    :param check: If True, check the integrity of the input
    :return: name of the bus
    """
    if check:
        if level not in net.levels:
            msg = "The pressure level of the bus {} is not in {}".format(name, net.levels)
            raise ValueError(msg)
        if name in net.bus.index:
            msg = "The bus {} already exists".format(name)
            raise ValueError(msg)

    net.bus.loc[name] = [level, zone, "NODE"]
    return name


def create_pipe(net, from_bus, to_bus, length_m, diameter_m, name, material=conf.mat_default, in_service=True, check=True):

    """
    Create a pipe between two existing buses on a given network

    :param net: the given network
    :param from_bus: the name of the already existing bus where the pipe starts
    :param to_bus: the name of the already existing bus where the pipe ends
    :param length_m: length of the pipe (in [m])
    :param diameter_m: inner diameter of the pipe (in [m])
    :param name: name of the pipe
    :param material: material of the pipe
    :param in_service: if False, the simulation will not take this pipe into account (default: True)
    :param check: If True, check the integrity of the input
    :return: name of the pipe
    """
    if check:
        _try_existing_bus(net, from_bus)
        _try_existing_bus(net, to_bus)
        _check_level(net, from_bus, to_bus)
        if name in net.pipe.index:
            msg = "The pipe {} already exists".format(name)
            raise ValueError(msg)

    net.pipe.loc[name] = [from_bus, to_bus, length_m, diameter_m, material, in_service]
    return name


def create_load(net, bus, p_kW, name, min_p_pa=conf.min_p_pa, scaling=conf.scaling):
    """
    Create a load attached to an existing bus in a given network

    :param net: the given network
    :param bus: the existing bus
    :param p_kW: power consumed by the load (in [kW])
    :param name: name of the load
    :param min_p_pa: minimum acceptable pressure
    :param scaling: scaling factor for the load (default: 1.0)
    :return: name of the load
    """

    _try_existing_bus(net, bus)
    net.load.loc[name] = [bus, p_kW, min_p_pa, scaling]
    _change_bus_type(net, bus, "SINK")
    return name


def change_load(net, name_load_bus, p_kW, add=False, bybusname=False):
    """
    this function add a load to an existing load. For example, it
    can be used if more than one house is connected to a network end.
    If add is True, the load is added to the old load and not directly changed.

    :param net: the given pandangas network
    :param name_load_bus: the name of the bus or the load
    :param p_kW: float - power consumed by the load (in [kW])
    :param add: a boolean indicating if the new load is added to the old one (add=True) or directly changed (add=False)
    :param bybusname: If True, the load is identified by its bus name, not the name of the load
    :return: name of the load
    """
    if bybusname:
        _try_existing_bus(net, name_load_bus)
        name_load = net.load.loc[net.load["bus"] == name_load_bus].index[0]
    else:
        name_load = name_load_bus

    if add:
        net.load.loc[name_load, 'p_kW'] += p_kW
    else:
        net.load.loc[name_load, 'p_kW'] = p_kW


def create_feeder(net, bus, p_lim_kW, p_Pa, name):
    """
    Create a feeder attached to an existing bus in a given network

    :param net: the given network
    :param bus: the existing bus
    :param p_lim_kW: maximum power flowing through the feeder
    :param p_Pa: operating pressure level at the output of the feeder
    :param name: name of the feeder
    :return: name of the feeder
    """
    _try_existing_bus(net, bus)

    net.feeder.loc[name] = [bus, p_lim_kW, p_Pa]
    _change_bus_type(net, bus, "SRCE")
    return name


def create_station(net, bus_high, bus_low, p_lim_kW, p_Pa, name):
    """
    Create a pressure station between two existing buses on different pressure level in a given network

    :param net: the given network
    :param bus_high: the existing bus with higher nominal pressure
    :param bus_low: the existing bus with lower nominal pressure
    :param p_lim_kW: maximum power flowing through the feeder
    :param p_Pa: operating pressure level at the output of the feeder
    :param name: name of the station
    :return: name of the station
    """

    _try_existing_bus(net, bus_high)
    _try_existing_bus(net, bus_low)
    _check_level(net, bus_high, bus_low, same=False)

    net.station.loc[name] = [bus_high, bus_low, p_lim_kW, p_Pa]
    create_load(net, bus_high, 0, "STALOAD" + str(name))
    _change_bus_type(net, bus_low, "SRCE")

    return name


def set_pressure_level(net, levels):
    """
    This function set the pressure levels of pandangas network. The pressure levels are in Pascal.
    :param net: a pandangas network
    :param levels: a dictionnary where the keys are the name of the pressure level and the keys the value.
           default_level = {"HP": 5.0E5, "MP": 1.0E5, "BP+": 0.1E5, "BP": 0.025E5}
    """

    net.levels = levels


def set_temperature(net, temp, celsius=True):
    """
    This function set the exterior temperature of the network
    :param net: a pandangas network
    :param temp: the tempeature in Celsius or Kelvin
    :param celsius: if True, the temperature is in Celsius otherwise in Kelvin
    """
    if celsius:
        net.temperature = temp + 273.15
    else:
        net.temperature = temp


def set_pressure(net, p_atm):
    """
    This function set the exterior pressure of the network in Pascal
    :param net: a pandangas network
    :param p_atm:
    """
    net.p_atm = p_atm


def set_solver_option(net, solver_option=None):
    """
    The function to set the solver option used to solve the equations
    :param net: the pandasgaz network
    :param solver_option: the dict given by the user with custom options or none
    """

    if solver_option:
        for k in solver_option.keys():
            net.solver_option[k] = solver_option[k]


def get_solver_info(net):
    """
    This function print the information related to the solver option
    :param net:
    """
    print('Here are the current solver options: ')
    print(net.solver_option)

    print('\nHere are definition of the current solver options: ')
    print(net.solver_info)

