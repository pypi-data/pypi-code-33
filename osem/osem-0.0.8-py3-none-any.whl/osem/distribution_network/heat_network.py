from math import sqrt, pi

from osem.general import conf
from osem.general.enerapi.base.base import Base
from sympy import symbols
from sympy.solvers import solve

from osem.general.enerapi.common.Guard import *


class HeatNetwork(Base):
    """
    Estimate constant heat losses in pipes for steady state conditions.
    """

    _default_parameter_value = {"ground_temp": 10, "th_loss_coef": 0.203, "rho_fluid": 1000, "cp_mass_fluid": 4185, "v_max": 2.0}

    @staticmethod
    def help():
        return HeatNetwork.__doc__ + "\r\n" + HeatNetwork.calculate.__doc__

    @staticmethod
    def help_calculate():
        return HeatNetwork.__init__.__doc__.format(
            HeatNetwork._default_parameter_value["ground_temp"],
            HeatNetwork._default_parameter_value["th_loss_coef"],
            HeatNetwork._default_parameter_value["v_max"]
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"len_tot": 10000, "t_cons_max": 90, "p_cons_tot": 5000,
            "t_return_fixed": 60}}

        {{
            len_tot             [m]         (must be a positive integer)
            t_cons_max          [deg.]
            p_cons_tot          [kW]        (must be positive)
            t_return_fixed      [deg.]

            ground_temp         [deg.]      (must be between -10 and
                    30 deg., default value: {0})
            th_loss_coef        [W/m/K]     (must be between 0 and
                    1 W/m/K, default value: {1})
            rho_fluid           [kg/m3]
            cp_mass_fluid       [J/kg/K]
            v_max               [m/s]       (must be strictly positive,
                    default value: {2})
        }}
        """

        super(HeatNetwork, self).__init__(args)

        Guard.check_if_key_in_dict("len_tot", args)
        Guard.check_if_key_in_dict("t_cons_max", args)
        Guard.check_if_key_in_dict("p_cons_tot", args)
        Guard.check_if_key_in_dict("t_return_fixed", args)

        Guard.check_is_higher(args["len_tot"], lower_limit=0)
        Guard.check_is_higher(args["t_cons_max"], lower_limit=0)
        Guard.check_is_higher(args["p_cons_tot"], lower_limit=0)
        Guard.check_is_higher(args["t_return_fixed"], lower_limit=0)
        Guard.check_is_higher(args["th_loss_coef"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["rho_fluid"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["cp_mass_fluid"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["v_max"], lower_limit=0, strict=True)

        Guard.check_value_in_between(args["ground_temp"], min=-10, max=30)
        Guard.check_value_in_between(args["th_loss_coef"], min=0, max=1)

        # Convert cp_mass_fluid [J/kg/K] -> kWh/kg/K and th_loss_coef [W/m/K] -> kW/m/K
        args["th_loss_coef"] /= 1000.0
        args["cp_mass_fluid"] *= 2.78 * 10**(-7)

        self.args = args

    def calculate(self):
        """
        Perform estimation of steady state network heat losses.
        The returned object is of the form:

        ```
        {
            p_supply            [kW]
            p_th_supply         [kW]
            p_th_return         [kW]
            ratio_th_loss       [ratio]
            t_supply            [deg.]
            t_reject            [deg.]
            fluid_flow          [m3/h]
            inner_diameter_min  [m]
        }
        ```

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        len_tot                 [m]             Network supply length
        t_cons_max              [deg.]          Higher consumption temperatures needed
        p_cons_tot              [kW]            Consumed power
        t_return_fixed          [deg.]          Set point temperature for return flow
        ground_temp             [deg.]          Ground temperature
        th_loss_coef            [W/m/K]         Thermal loss coefficient for heat pipe
        rho_fluid               [kg/m3]         Fluid's density
        cp_mass_fluid           [J/kg/K]        Fluid's thermal capacity
        v_max                   [m/s]           Maximum accepted fluid velocity

        *********************************************************************
        Outputs:
        *********************************************************************
        p_supply                [kW]            Supplied power
        p_th_supply             [kW]            Thermal loss power for supply network
        p_th_return             [kW]            Thermal loss power for return network
        ratio_th_loss           [ratio]         Ratio of thermal loss, 1 - consumed power divided by supplied power
        t_supply                [deg.]          Supplied temperature at the beginning of the supply network
        t_reject                [deg.]          Rejected temperature at the start of return network
        fluid_flow              [m3/h]          Fluid's flow through network
        inner_diameter_min      [m]             Minimal pipe inner diameter considered maximum accepted fluid velocity

        Every estimation is based on parameters and coefficients found in [1].

        *********************************************************************
        Reference:
        *********************************************************************
        [1] C. Weber. "Multi-Objective Design and Optimization of District Energy Systems Including Polygeneration
        Energy Conversion Technologies", PhD thesis, Lausanne, 2008

        http://infoscience.epfl.ch/record/114786/files/EPFL_TH4018.pdf

        """

        p_supply, p_th_supply, p_th_return = symbols('p_supply, p_th_supply, p_th_return')
        q, t_supply, t_reject = symbols('q, t_supply, t_reject')

        f1 = p_supply - self.args["p_cons_tot"] - p_th_supply - p_th_return

        f2 = p_supply - self.args["rho_fluid"] * self.args["cp_mass_fluid"] * q * (
            t_supply - self.args["t_return_fixed"])

        f3 = p_th_supply - self.args["rho_fluid"] * self.args["cp_mass_fluid"] * q * (
            t_supply - self.args["t_cons_max"])

        f4 = p_th_return - self.args["rho_fluid"] * self.args["cp_mass_fluid"] * q * (
            t_reject - self.args["t_return_fixed"])

        f5 = self.args["p_cons_tot"] - self.args["rho_fluid"] * self.args["cp_mass_fluid"] * q * (
            self.args["t_cons_max"] - t_reject)

        f6 = p_th_supply - self.args["th_loss_coef"] * self.args["len_tot"] * (
            (t_supply + self.args["t_cons_max"]) / 2.0 - self.args["ground_temp"])

        f7 = p_th_return - self.args["th_loss_coef"] * self.args["len_tot"] * (
            (t_reject + self.args["t_return_fixed"]) / 2.0 - self.args["ground_temp"])

        res = solve((f1, f2, f3, f4, f5, f6, f7), (p_supply, p_th_supply, p_th_return, q, t_supply, t_reject),
                    dict=True)

        try:
            p_sup = res[1][p_supply]
            p_th_sup = res[1][p_th_supply]
            p_th_ret = res[1][p_th_return]
            flow = res[1][q]
            t_sup = res[1][t_supply]
            t_rej = res[1][t_reject]

            a = float(flow) / (self.args["v_max"] * 3600)
            a = a / pi
            diam = 2 * sqrt(a)

            ratio_th_loss = 1 - self.args["p_cons_tot"] / float(p_sup)

            return {
                "p_supply": round(p_sup, 3),
                "p_th_supply": round(p_th_sup, 3),
                "p_th_return": round(p_th_ret, 3),
                "ratio_th_loss": round(ratio_th_loss, 3),
                "t_supply": round(t_sup, 3),
                "t_reject": round(t_rej, 3),
                "fluid_flow": round(flow, 3),
                "inner_diameter_min": round(diam, 3)
            }
        except KeyError:
            print ("System solved with only one root...")

            return {
                "p_supply": None,
                "p_th_supply": None,
                "p_th_return": None,
                "ratio_th_loss": None,
                "t_supply": None,
                "t_reject": None,
                "fluid_flow": None,
                "inner_diameter_min": None
            }


    def get_reference(self):
        """
        get the reference for this module
        """
        return conf.ref_heat_network