# this script lists the pandasgas network used to test this module

import osem.networks.pandangas.network_creation as pg


def model_gas_test():
    """
    This function create a basic model to test pandangas - two level of pressure
    """

    net = pg.create_empty_network()

    busf = pg.create_bus(net, level="MP", name="BUSF")
    bus0 = pg.create_bus(net, level="MP", name="BUS0")

    bus1 = pg.create_bus(net, level="BP", name="BUS1")
    bus2 = pg.create_bus(net, level="BP", name="BUS2")
    bus3 = pg.create_bus(net, level="BP", name="BUS3")

    pg.create_load(net, bus2, p_kW=10.0, name="LOAD2")
    pg.create_load(net, bus3, p_kW=15.0, name="LOAD3")

    pg.create_pipe(net, busf, bus0, length_m=100, diameter_m=0.05, name="PIPE0")
    pg.create_pipe(net, bus1, bus2, length_m=400, diameter_m=0.05, name="PIPE1")
    pg.create_pipe(net, bus1, bus3, length_m=500, diameter_m=0.05, name="PIPE2")
    pg.create_pipe(net, bus2, bus3, length_m=500, diameter_m=0.05, name="PIPE3")

    pg.create_station(net, bus0, bus1, p_lim_kW=50, p_Pa=0.025E5, name="STATION")
    pg.create_feeder(net, busf, p_lim_kW=50, p_Pa=0.9E5, name="FEEDER")

    return net


def model_gas_test2():
    """
    This function create a basic model to test pandangas - one level of pressure
    """

    net = pg.create_empty_network()

    bus1 = pg.create_bus(net, level="BP", name="BUS1")
    bus2 = pg.create_bus(net, level="BP", name="BUS2")
    bus3 = pg.create_bus(net, level="BP", name="BUS3")

    pg.create_load(net, bus2, p_kW=10.0, name="LOAD2")
    pg.create_load(net, bus3, p_kW=10.0, name="LOAD3")

    pg.create_pipe(net, bus1, bus2, length_m=500, diameter_m=0.05, name="PIPE1")
    pg.create_pipe(net, bus1, bus3, length_m=500, diameter_m=0.05, name="PIPE2")
    pg.create_pipe(net, bus2, bus3, length_m=500, diameter_m=0.05, name="PIPE3")

    pg.create_feeder(net, bus1, p_lim_kW=50, p_Pa=0.9E5, name="FEEDER")

    return net


def model_with_four_bus():
    """
    Tis function create a network with four bus and three pipes - one level of pressure
    """
    nb_bus = 4
    dia = 0.05
    leng = [300, 100, 400]

    # create network
    net = pg.create_empty_network()

    # create bus and node
    all_bus = [None] * nb_bus
    for i in range(nb_bus):
        all_bus[i] = pg.create_bus(net, level="BP", name="BUS" + str(i))

    # create pipe
    # for i in range(0, nb_bus-1):
    #     pg.create_pipe(net, all_bus[i], all_bus[i+1], length_m=leng[i], diameter_m=dia, name="PIPE"+str(i))
    pg.create_pipe(net, "BUS0", "BUS1", length_m=leng[0], diameter_m=dia, name="PIPE" + str(0))
    pg.create_pipe(net, "BUS1", "BUS2", length_m=leng[1], diameter_m=dia, name="PIPE" + str(1))
    pg.create_pipe(net, "BUS2", "BUS3", length_m=leng[2], diameter_m=dia, name="PIPE" + str(2))

    # create loads
    pg.create_load(net, all_bus[3], p_kW=50.0, name="LOAD1")
    pg.create_load(net, all_bus[2], p_kW=50.0, name="LOAD2")
    pg.create_load(net, all_bus[1], p_kW=300.0, name="LOAD5")

    # create feeder
    pg.create_feeder(net, all_bus[0], p_lim_kW=50, p_Pa='BP', name="FEEDER")

    return net


def model_with_two_feeder():
    """
    This function create a simple pandangas model with 2 feeder
    :return: the pandangas network
    """

    # parameter
    nb_bus = 3
    dia = 0.05
    leng = 10

    # create network
    net = pg.create_empty_network()

    # create bus and node
    all_bus = [None] * nb_bus
    for i in range(nb_bus):
        all_bus[i] = pg.create_bus(net, level="BP", name="BUS"+str(i))

    for i in range(0, nb_bus-1):
        pg.create_pipe(net, all_bus[i], all_bus[i+1], length_m=leng, diameter_m=dia, name="PIPE"+str(i))


    # create loads
    pg.create_load(net, all_bus[1], p_kW=50.0, name="LOAD1")

    # create feeder
    pg.create_feeder(net, all_bus[0], p_lim_kW=50, p_Pa='BP', name="FEEDER")
    pg.create_feeder(net, all_bus[2], p_lim_kW=50, p_Pa='BP', name="FEEDER2")

    return net


def model_with_eight_bus(all_load_added=True):
    """
    This function create a simple model with 5 pipes, one feeder, two loads
          |
        F o-o-o
            |
    :param all_load_added: If True, no load missing
    :return: the pandangas network
    """

    # parameter
    nb_bus = 9
    dia = 0.05
    leng = 100

    # create network
    net = pg.create_empty_network()

    # create bus and node
    all_bus = [None] * nb_bus
    for i in range(nb_bus):
        all_bus[i] = pg.create_bus(net, level="BP", name="BUS"+str(i))

    for i in range(0, nb_bus-1):
        pg.create_pipe(net, all_bus[i], all_bus[i+1], length_m=leng, diameter_m=dia, name="PIPE"+str(i))

    # create loads
    if all_load_added:
        pg.create_load(net, all_bus[8], p_kW=50.0, name="LOAD1")
    pg.create_load(net, all_bus[4], p_kW=50.0, name="LOAD2")
    pg.create_load(net, all_bus[3], p_kW=300.0, name="LOAD5")

    # create feeder
    pg.create_feeder(net, all_bus[0], p_lim_kW=50, p_Pa='BP', name="FEEDER")

    return net