from __future__ import division

from System import System
from osem.general.enerapi.base.base import Base
from osem.general import conf
from osem.general.enerapi.common.Guard import *


class StratifiedDynamic(Base):
    """
    Simulate dynamic behavior of a stratified thermal storage tank.
    """

    _default_parameter_value = {"inlet_water_temp": 12, "rho_fluid": 985, "cp_mass_fluid": 4185, "lambda_fluid": 0.62,
                                "time_step": 150, "nb_points_by_step": 11, "U_tot": 0.5, "env_temp": 15,
                                "wall_thick": 0.006, "lambda_wall": 50.2}

    ARGS_LIST = ["rho_fluid", "cp_mass_fluid", "inlet_water_temp", "lambda_fluid", "time_step", "nb_points_by_step",
                 "U_tot", "env_temp", "diameter", "height", "nb_of_layers", "temp_init_max", "temp_init_min",
                 "ports_in", "ports_out", "wall_thick", "lambda_wall"]

    @staticmethod
    def help():
        return StratifiedDynamic.__doc__ + "\r\n" + StratifiedDynamic.calculate.__doc__

    @staticmethod
    def help_calculate():
        return StratifiedDynamic.__init__.__doc__.format(
            StratifiedDynamic._default_parameter_value["inlet_water_temp"],
            StratifiedDynamic._default_parameter_value["rho_fluid"],
            StratifiedDynamic._default_parameter_value["cp_mass_fluid"],
            StratifiedDynamic._default_parameter_value["lambda_fluid"],
            StratifiedDynamic._default_parameter_value["time_step"],
            StratifiedDynamic._default_parameter_value["nb_points_by_step"],
            StratifiedDynamic._default_parameter_value["U_tot"],
            StratifiedDynamic._default_parameter_value["env_temp"],
            StratifiedDynamic._default_parameter_value["wall_thick"],
            StratifiedDynamic._default_parameter_value["lambda_wall"])

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{
        "diameter": 0.5762, "height": 1.1524, "nb_of_layers": 10,
        "temp_init_max": 70, "temp_init_min": 35,
        "ports_in": {{"port_1": {{"height": 1.0, "temp_in": [72, 70, 70],
                      "flow_in": [0.07, 0.07, 0.035]}},
                     "port_2": {{"height": 0.1, "temp_in": [25, 25, 25],
                                 "flow_in": [0.035, 0.07, 0.035]}}
                     }},
        "ports_out": {{"port_1": {{"height": 0.9,
                                   "flow_out": [0.035, 0.07, 0.035]}},
                      "port_2": {{"height": 0.1,
                                  "flow_out": [0.07, 0.07, 0.035]}}
                      }}
        }}

        {{
            diameter            [m]         (must be strictly positive)
            height              [m]         (must be strictly positive)
            nb_of_layers        [-]         (must be an integer strictly
                                             higher than 2)
            temp_init_max       [deg.C]      (must be strictly positive and
                                             greater than temp_init_min)
            temp_init_min       [deg.C]     (must be strictly positive)
            ports_in            [-]         (must be a dict of dicts with
                                             keys: "height", "temp_in",
                                             "flow_in")
                height          [%]         (must be strictly positive
                                            and less than 1)
                temp_in         [deg.C]     (must be strictly positive)
                flow_in         [m3/h]      (must be strictly positive)

            ports_out           [-]         (must be a dict of dicts with
                                             keys: "height", "flow_out")
                height          [%]         (must be strictly positive
                                            and less than 1)
                flow_in         [m3/h]      (must be strictly positive)

            inlet_water_temp    [deg.C]     (default value: {0})
            rho_fluid           [kg/m3]     (must be strictly positive,
                                             default value: {1})
            cp_mass_fluid       [J/kg/K]    (must be strictly positive,
                                             default value: {2})
            lambda_fluid        [W/m/K]     (must be strictly positive,
                                             default value: {3})
            time_step           [s]         (must be strictly positive,
                                             default value: {4})
            nb_points_by_step   [-]         (must be greater than 2,
                                             default value: {5})
            U_tot               [W/m2/K]    (must be positive, '0' means
                                             no convection losses,
                                             default value: {6})
            env_temp            [deg.]      (default value: {7})
            wall_thick          [m]         (must be strictly positive,
                                             default value: {8})
            lambda_wall         [W/m/K]     (must be positive,
                                             default value: {9})
        }}
        """

        super(StratifiedDynamic, self).__init__(args)

        for key in self.ARGS_LIST:
            Guard.check_if_key_in_dict(key, args)

        args["nb_of_layers"] = int(args["nb_of_layers"])

        Guard.check_is_higher(args["rho_fluid"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["diameter"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["height"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["cp_mass_fluid"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["lambda_fluid"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["inlet_water_temp"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["wall_thick"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["lambda_wall"], lower_limit=0)
        Guard.check_is_higher(args["time_step"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["U_tot"], lower_limit=0)
        Guard.check_is_higher(args["nb_points_by_step"], lower_limit=2)
        Guard.check_is_higher(args["nb_of_layers"], lower_limit=2, strict=True)
        Guard.check_is_higher(args["temp_init_min"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["temp_init_max"], lower_limit=args["temp_init_min"])

        # Checks for ports_in
        for key in args["ports_in"]:
            Guard.check_if_key_in_dict("height", args["ports_in"][key])
            Guard.check_if_key_in_dict("temp_in", args["ports_in"][key])
            Guard.check_if_key_in_dict("flow_in", args["ports_in"][key])
            Guard.check_for_every_item_of_list(args["ports_in"][key]["temp_in"], Guard.check_is_higher, lower_limit=0,
                                               strict=True)
            Guard.check_for_every_item_of_list(args["ports_in"][key]["flow_in"], Guard.check_is_higher, lower_limit=0)

            l_t_in = len(args["ports_in"][key]["temp_in"])
            l_f_in = len(args["ports_in"][key]["flow_in"])
            Guard.check_value_in_between(l_t_in, min=(l_t_in + l_f_in) / 2.0, max=(l_t_in + l_f_in) / 2.0)
            Guard.check_value_in_between(l_f_in, min=(l_t_in + l_f_in) / 2.0, max=(l_t_in + l_f_in) / 2.0)
        Guard.check_for_every_item_of_list([args["ports_in"][key]["height"] for key in args["ports_in"]],
                                           Guard.check_is_higher, lower_limit=0, strict=True)
        Guard.check_for_every_item_of_list([args["ports_in"][key]["height"] for key in args["ports_in"]],
                                           Guard.check_value_in_between, min=0, max=1)

        # Checks for ports_out
        for key in args["ports_out"]:
            Guard.check_if_key_in_dict("height", args["ports_out"][key])
            Guard.check_if_key_in_dict("flow_out", args["ports_out"][key])
            Guard.check_for_every_item_of_list(args["ports_out"][key]["flow_out"], Guard.check_is_higher, lower_limit=0)

            l_f_out = len(args["ports_out"][key]["flow_out"])
            l_f_in = len(args["ports_in"]["port_1"]["flow_in"])
            Guard.check_value_in_between(l_f_out, min=(l_f_out + l_f_in) / 2.0, max=(l_f_out + l_f_in) / 2.0)
        Guard.check_for_every_item_of_list([args["ports_out"][key]["height"] for key in args["ports_out"]],
                                           Guard.check_is_higher, lower_limit=0, strict=True)
        Guard.check_for_every_item_of_list([args["ports_out"][key]["height"] for key in args["ports_out"]],
                                           Guard.check_value_in_between, min=0, max=1)

        # Convert flows [m3/h] --> [m3/s]
        for key in args["ports_in"]:
            for idx, flow in enumerate(args["ports_in"][key]["flow_in"]):
                conv_flow = flow / 3600
                args["ports_in"][key]["flow_in"][idx] = conv_flow

        for key in args["ports_out"]:
            for idx, flow in enumerate(args["ports_out"][key]["flow_out"]):
                conv_flow = flow / 3600
                args["ports_out"][key]["flow_out"][idx] = conv_flow

        self.args = args

    def calculate(self):
        """
        Simulate the behavior of a stratified thermal storage. The tank is divided in fictional layers of
        homogeneous temperature. Temperatures variations are due to losses to the environment, conduction between
        layers, ports flows and flows circulating between layers.The tank is assumed to be a vertical cylinder
        insulated the same on each side. Ports can either correspond to an inlet or an outlet of water. There are
        physical entities described by a height and a flow (and a temperature for inlet ports). Heights are specified
        as the ratio between port height and tank height (between 0 and 1).
        All specified flows are volumetric flows (unit: m3/h).
        The returned object is of the form:

        ```
        {
            temperatures_layer      [deg.C]     (list of lists)
            temperatures_step       [deg.C]     (list of lists)
        }
        ```

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        diameter                [m]             Storage diameter
        height                  [m]             Storage height
        nb_of_layers            [-]             Desired number of layers
        temp_init_max           [deg.C]         Maximum initial temperature
        temp_init_min           [deg.C]         Minimum initial temperature
        ports_in                [dict]          Inlet ports parameters dictionary
            height              [%]                 Inlet ports height
            temp_in             [deg.C]             Inlet temperatures (list)k
            flow_in             [m3/h]              Inlet flows (list)
        ports_out               [dict]          Outlet ports parameters dictionary
            height              [%]                 Outlet ports height
            flow_in             [m3/h]              Outlet flows (list)

        inlet_water_temp        [deg.C]         Mainstream water temperature
        rho_fluid               [kg/m3]         Fluid density
        cp_mass_fluid           [J/kg/K]        Fluid mass heat capacity
        lambda_fluid            [W/m/K]         Fluid thermal conductivity
        time_step               [s]             Length of a time step
        nb_points_by_step       [-]             Number of points by time step
        U_tot                   [W/m2/K]        External convective heat transfer coefficient
        env_temp                [deg.]          Environment temperature
        wall_thick              [m]             Tank wall thickness
        lambda_wall             [W/m/K]         Tank wall thermal conductivity

        *********************************************************************
        Outputs:
        *********************************************************************
        temperatures_layer      [deg.C]         Temperatures ordered by layer (list of lists)
        temperatures_step       [deg.C]         Temperatures ordered by time step (list of lists)


        Every estimation is based on the model and hypothesis found in [1] and [2].

        *********************************************************************
        References:
        *********************************************************************
        [1] I. Dincer, M. Rosen: "Thermal Energy Storage : Systems and Applications",
            Wiley and Sons Inc, 2002, pp. 276 - 287

        [2] W.A. Beckman, J.A. Duffie: "Solar Engineering of Thermal Processes",
            second edition, Wiley and Sons Inc, 1991, pp. 379-384

        """

        system = System(self.args)

        system.create_storage()
        system.simulate_storage()
        system.layer_to_step()

        return {"temperatures_layer": system.results, "temperatures_step": system.results_step}


    def get_reference(self):
        """
        obtain the scientific reference for this module
        :return:
        """

        conf.ref_statified_dyn