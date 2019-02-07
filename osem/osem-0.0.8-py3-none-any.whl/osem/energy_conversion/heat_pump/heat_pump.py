from osem.general.enerapi.base.base import Base
from osem.general import conf
from osem.general.enerapi.common.Guard import *


class HeatPump(Base):
    """
    Estimate heat pump real and Carnot based COP from hot and cold sources temperatures.
    """

    _default_parameter_value = {"reversible": [False], "n": 0.43, "r": 0.80}

    n_max = 0.48
    n_min = 0.38

    t_hot_max = 100
    t_hot_min = 0
    t_cold_min = -15

    @staticmethod
    def help():
        return HeatPump.__doc__ + "\r\n" + HeatPump.calculate.__doc__

    @staticmethod
    def help_calculate():
        return HeatPump.__init__.__doc__.format(
            HeatPump.t_hot_min,
            HeatPump.t_hot_max,
            HeatPump.t_cold_min,
            HeatPump._default_parameter_value["reversible"],
            HeatPump.n_min,
            HeatPump.n_max,
            HeatPump._default_parameter_value["n"],
            HeatPump._default_parameter_value["r"])

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"t_hot": [50, 51, 52], "t_cold": [8, 10, 12]}}

        {{
            "t_hot":        [deg.C] (list)
                (must be between {0} and {1})
            "t_cold":       [deg.C] (list)
                (must be between {2} and t_hot)

            "reversible":   [bool.] (list)
                (true or false, default value: {3})
            "n":            [ratio]
                (must be between {4} and {5}, default value: {6})
            "r":            [ratio]
                (must be between 0 and 1, default value: {7})
        }}
        """

        super(HeatPump, self).__init__(args)

        Guard.check_if_key_in_dict("t_hot", args)
        Guard.check_if_key_in_dict("t_cold", args)

        Guard.check_for_same_list_lengths(l1=args["t_hot"], l2=args["t_cold"])

        Guard.check_for_every_item_of_list(args["t_hot"], Guard.check_value_in_between, min=HeatPump.t_hot_min,
                                           max=HeatPump.t_hot_max)
        Guard.check_for_every_item_of_list(args["t_cold"], Guard.check_value_in_between, min=HeatPump.t_cold_min,
                                           max=min(args["t_hot"]))

        Guard.check_for_every_item_of_list(args["reversible"], Guard.check_if_value_in_list, values=[True, False])

        if len(args["reversible"]) != 1:
            Guard.check_for_same_list_lengths(l1=args["t_hot"], l2=args["reversible"])

        Guard.check_value_in_between(args["n"], min=HeatPump.n_min, max=HeatPump.n_max)
        Guard.check_value_in_between(args["r"], min=0, max=1, min_in=False)

        self.args = args

    def calculate(self):
        """
        The returned object is of the form:
        {
            "cop_carnot":   [ratio] (list)
            "cop_real":     [ratio] (list)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        t_hot           [deg.C] (list)      Hot source temperature
        t_cold          [deg.C] (list)      Cold source temperature
        reversible      [bool.] (list)      Set to True if the heat pump is reversible and in cold production
        n               [ratio]             Ratio between Carnot based and real COP (default at 0.43 from [1])
        r               [ratio]             Ratio between real COP in reversible or normal behaviour (default at 0.80 from [1])

        *********************************************************************
        Outputs:
        *********************************************************************
        cop_carnot      [ratio] (list)      Carnot based COP as defined in [1]
        cop_real        [ratio] (list)      Real COP as defined in [1]

        *********************************************************************
        Reference:
        *********************************************************************
        [1] L. Girardin. "A GIS-based Methodology for the Evaluation of Integrated Energy Systems in Urban Area".
        PhD thesis, STI, Lausanne, 2012

        """

        if len(self.args["reversible"]) == 1:
            self.args["reversible"] *= len(self.args["t_hot"])

        cop_carnot = []
        cop_real = []

        for t_hot, t_cold, rev in zip(self.args["t_hot"], self.args['t_cold'], self.args["reversible"]):
            t_hot += 273.15
            t_cold += 273.15

            if rev is False:
                cop_c = float(t_hot) / (t_hot - t_cold)
                cop_r = float(t_hot) / (t_hot - t_cold) * self.args["n"]

            else:
                cop_c = float(t_cold) / (t_hot - t_cold)
                cop_r = float(t_cold) / (t_hot - t_cold) * self.args["n"] * self.args["r"]

            cop_carnot.append(round(cop_c, 2))
            cop_real.append(round(cop_r, 2))

        return {
            "cop_carnot": cop_carnot,
            "cop_real": cop_real
        }


    def get_reference(self):
        """
        return the scientific reference for this module
        """
        return conf.ref_girardin
