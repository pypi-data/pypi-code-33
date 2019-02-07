from __future__ import division

from osem.general.enerapi.base.base import Base
from numpy import linspace, pi
from scipy.integrate import odeint

from osem.general.enerapi.common.Guard import *
from osem.general import conf


class HotWaterTank(Base):
    """
    Estimate isothermal cylindrical hot water tank dynamic behavior.
    """

    _default_parameter_value = {"rho": 1.0, "cp": 4184.0, "q_aux": [0], "t_step": 600, "nbr_of_values_for_step": 2}

    @staticmethod
    def help():
        return HotWaterTank.__doc__ + "\r\n" + HotWaterTank.calculate.__doc__

    @staticmethod
    def help_calculate():
        return HotWaterTank.__init__.__doc__.format(
            HotWaterTank._default_parameter_value["q_aux"][0],
            HotWaterTank._default_parameter_value["rho"],
            HotWaterTank._default_parameter_value["cp"],
            HotWaterTank._default_parameter_value["t_step"],
            HotWaterTank._default_parameter_value["nbr_of_values_for_step"]
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"height": 1, "diameter": 0.5, "u": 0.05, "t_cold": [12, 10],
        "flow_cons": [0.001, 0.001], "t_ext": [25, 22], "q_aux": [0, 500], "t_init": 65}}

        {{
            "height":           [m]
                (must be strictly positive)
            "diameter":         [m]
                (must be strictly positive)
            "u":                [W/m2/deg.K]
                (must be positive)
            "t_cold":           [deg.C]  (list)
                (must be the same length of other lists)
            "flow_cons":        [m3/s]   (list)
                (values must be positive, must be the same length of other lists)
            "t_ext":            [deg.C]  (list)
                (must be the same length of other lists)
            "q_aux":            [W]      (list)
                (if given, values must be positive, must be the same length of other lists, default values: {0})
            "t_init":           [deg.C]


            "rho":              [kg/m3]
                (must be strictly positive, default value: {1})
            "cp":               [J/kg/deg.K]
                (must be strictly positive, default value: {2})
            "t_step":           [s]
                (must be strictly positive, default value: {3})
            "nbr_of_values_for_step": [-]
                (must be higher than 2, default value: {4})
        }}

        """
        super(HotWaterTank, self).__init__(args)

        arg_list = ["height", "diameter", "u", "t_cold", "flow_cons", "t_ext", "q_aux", "t_init"]
        for val in arg_list:
            Guard.check_if_key_in_dict(val, args)

        Guard.check_for_same_list_lengths(l1=args["t_cold"], l2=args["flow_cons"], l3=args["t_ext"])

        if len(args["q_aux"]) != 1:
            Guard.check_for_same_list_lengths(l1=args["t_cold"], l2=args["q_aux"])
        else:
            args["q_aux"] = [0] * len(args["q_aux"])

        Guard.check_for_every_item_of_list(args["flow_cons"], Guard.check_is_higher, lower_limit=0)
        Guard.check_for_every_item_of_list(args["q_aux"], Guard.check_is_higher, lower_limit=0)

        Guard.check_is_higher(args["height"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["diameter"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["rho"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["cp"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["u"], lower_limit=0)

        Guard.check_is_higher(args["nbr_of_values_for_step"], lower_limit=2)
        Guard.check_is_higher(args["t_step"], lower_limit=0, strict=True)

        args["a"] = pi * args["diameter"] * (args["diameter"] / 2.0 + args["height"])
        args["m_fluid"] = args["rho"] * args["height"] * pi * (args["diameter"] / 2.0)**2

        self.args = args

    def calculate(self):
        """
        The returned object is of the form:
        {"t": [deg.C] (list)}

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        height                      [m]                 Height of the tank
        diameter                    [m]                 Diameter of the tank
        u                           [W/m2/deg.K]        Temperature loss coefficient
        t_cold                      [deg.C]  (list)     Inlet flow temperature
        flow_cons                   [m3/s]   (list)     Consumed flow
        t_ext                       [deg.C]  (list)     External temperature
        t_init                      [deg.C]             Initial temperature of the tank

        q_aux                       [W]      (list)     Power of electrical heating auxiliary (optional)
        rho                         [kg/m3]             Fluid density
        cp                          [J/kg/deg.K]        Fluid specific heat
        t_step                      [s]                 Time step duration
        nbr_of_values_for_step      [-]                 Number of values needed for each time step



        *********************************************************************
        Outputs:
        *********************************************************************
        t                           [deg.C]  (list)     Fluid temperature in the tank

        *********************************************************************
        Reference:
        *********************************************************************
        Rejane De Cesaro Oliveski, Arno Krenzinger, Horacio A. Vielmo,
        Comparison between models for the simulation of hot water storage tanks,
        Solar Energy, Volume 75, Issue 2, August 2003,
        Pages 121-134, ISSN 0038-092X, http://dx.doi.org/10.1016/j.solener.2003.07.009.
        (http://www.sciencedirect.com/science/article/pii/S0038092X03002603)

        """

        t_tank = [self.args["t_init"]]

        def eq_diff(y, t, *var):  # var -> (t_cold, flow_cons, t_ext, q_aux)
            p_loss = self.args["u"] * self.args["a"] * (var[2] - y)
            p_consumed = self.args["rho"] * self.args["cp"] * var[1] * (var[0] - y)
            p_app = var[3] * self.args["t_step"] / 3600

            dydt = p_consumed + p_loss + p_app
            dydt /= (self.args["m_fluid"] * self.args["cp"])
            return dydt

        t = linspace(0, self.args["t_step"], self.args["nbr_of_values_for_step"])
        for values in zip(self.args["t_cold"],
                          self.args["flow_cons"],
                          self.args["t_ext"],
                          self.args["q_aux"]):

            sol = odeint(eq_diff, t_tank[-1], t, args=values)
            t_tank.pop()
            for x in sol:
                t_tank.append(round(x[0], 2))

        return {
            "t": t_tank
        }

    def get_reference(self):
        """
        get the scientific reference for htis module
        :return:
        """
        return conf.ref_hot_water_tank