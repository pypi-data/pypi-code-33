from osem.general import conf
from osem.general.enerapi.base.base import Base
from mpmath import exp
from sympy import Symbol
from sympy.solvers import solve

from osem.general.enerapi.common.Guard import *


class HeatExchanger(Base):
    """
    Estimate hot and cold outlet flows temperatures for a heat exchanger with Effectiveness-NTU method.
    The Effectiveness-NTU method takes a different approach to solving heat exchange analysis by using 
    three dimensionless parameters: Heat Capacity Rate Ratio, Effectiveness, and Number of Transfer Units.
    The relationship between these three parameters depends on the type of heat exchanger and the internal
    flow pattern and allow to avoid solving a system of two non-linear equations in order to get oulet temperatures
    """

    _default_parameter_value = {"rho": 1000, "cp": 4185, "type": "1-2n"}

    TYPE_LIST = ["1-2n"]
    ARG_LIST = ["u", "area", "flow_hot", "t_in_hot", "flow_cold", "t_in_cold"]

    @staticmethod
    def help():
        return HeatExchanger.__doc__ + "\r\n" + HeatExchanger.calculate.__doc__

    @staticmethod
    def help_calculate():
        return HeatExchanger.__init__.__doc__.format(
            HeatExchanger._default_parameter_value["rho"],
            HeatExchanger._default_parameter_value["cp"],
            HeatExchanger._default_parameter_value["type"],
            ", ".join("{0}".format(n) for n in HeatExchanger.TYPE_LIST)
        )

    def __init__(self, args):
        """
        Arguments should be of the form:

        {{"u": 10, "area": 1,"flow_hot": [0.001, 0.001],"t_in_hot": [80, 100],"flow_cold": [0.002, 0.0005],"t_in_cold": [20, 50]}}

        {{
            "u"             [W/m2/deg.K]
                (must be strictly positive)
            "area"          [m2]
                (must be strictly positive)
            "flow_hot"      [m3/s]  (list)
                (values must be positive)
            "t_in_hot"      [deg.C] (list)
            "flow_cold"     [m3/s]  (list)
                (values must be positive)
            "t_in_cold"     [deg.C] (list)
                (values must be lower than *t_in_hot*)

            "rho"           [kg/m3]
                (must be strictly positive, default value: {0} kg/m3)
            "cp"            [J/kg/deg.K]
                (must be strictly positive, default value: {1} J/kg/deg.K)
            "type"          [-]
                (must be one of {3}, default value: {2}, cf. [?] for more information)
        }}
        """

        super(HeatExchanger, self).__init__(args)

        for value in HeatExchanger.ARG_LIST:
            Guard.check_if_key_in_dict(value, args)

        Guard.check_is_higher(args["u"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["area"], lower_limit=0, strict=True)

        Guard.check_is_higher(args["rho"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["cp"], lower_limit=0, strict=True)
        Guard.check_if_value_in_list(args["type"], values=HeatExchanger.TYPE_LIST)

        Guard.check_for_same_list_lengths(l1=args["flow_hot"], l2=args["t_in_hot"],
                                          l3=args["flow_cold"], l4=args["t_in_cold"])

        Guard.check_for_every_item_of_list(args["flow_hot"], Guard.check_is_higher, lower_limit=0)
        Guard.check_for_every_item_of_list(args["flow_cold"], Guard.check_is_higher, lower_limit=0)

        for t in zip(args["t_in_hot"], args["t_in_cold"]):
            Guard.check_is_higher(t[0], lower_limit=t[1])

        self.args = args

    def calculate(self):
        """
        Estimate outlet temperatures for cold and hot flows.
        The returned object is of the form:

        ```
        {
            t_out_hot       [deg.C]   (list)
            t_out_cold      [deg.C]   (list)
        }
        ```

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        u               [W/m2/deg.K]        Heat transfer Coefficient
        area            [m2]                Exchange area
        flow_hot        [m3/s]  (list)      Inlet flows for hot flow
        t_in_hot        [deg.C] (list)      Inlet temperatures for hot flow
        flow_cold       [m3/s]  (list)      Inlet flows for cold flow
        t_in_cold       [deg.C] (list)      Inlet temperatures for cold flow

        *********************************************************************
        Outputs:
        *********************************************************************
        t_out_hot       [deg.C] (list)      Outlet temperatures for hot flow
        t_out_cold      [deg.C] (list)      Outlet temperatures for cold flow

        *********************************************************************
        References:
        *********************************************************************
        [1] F.P. Incropera and D.P. DeWitt, 1990, Fundamentals of Heat and Mass Tranfert,
        3rd edition, pp. 658-660, Wiley, New York
        """

        u = self.args["u"]
        a = self.args["area"]

        rho = self.args["rho"]
        cp = self.args["cp"]

        t_out_hot = []
        t_out_cold = []

        for (q1, t1_in, q2, t2_in) in zip(self.args["flow_hot"], self.args["t_in_hot"],
                                          self.args["flow_cold"], self.args["t_in_cold"]):

            if q1 == 0 or q2 == 0:
                t1 = t1_in
                t2 = t2_in

            else:
                ntu = u * a / (min(q1, q2) * rho * cp)
                if q1 == q2:
                    hcrr = 0.99  # in fact hcrr = 1
                else:
                    hcrr = min(q1, q2) / max(q1, q2)
                phi_max = min(q1, q2) * rho * cp * (t1_in - t2_in)

                e = Symbol('e')

                def f(x):
                    return {
                        '1-2n': exp(ntu * (hcrr - 1)) - (e - 1) / (hcrr * e - 1)
                    }.get(x, e - 1)

                eff = solve(f(self.args["type"]), e)[0]

                phi = eff * phi_max

                t1 = t1_in - phi / (q1 * rho * cp)
                t2 = t2_in + phi / (q2 * rho * cp)

            t_out_hot.append(round(t1, 2))
            t_out_cold.append(round(t2, 2))

        return {
            "t_out_hot": t_out_hot,
            "t_out_cold": t_out_cold
        }


    def get_reference(self):

        return conf.ref_heat_exchanger
