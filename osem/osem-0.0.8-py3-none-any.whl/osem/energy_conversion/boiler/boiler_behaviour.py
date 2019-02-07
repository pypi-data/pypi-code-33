import json
import os
from osem.general import conf
from osem.general.enerapi.base.base import Base
from osem.general.enerapi.common.DomainException import *
from osem.general.enerapi.common.IoC import *

from osem.general.enerapi.common.Guard import *


class BoilerBehaviour(Base):
    """
    Estimate boiler behaviour with efficiency (consumed power from supplied power or supplied power from consumed power)
    """

    TECHNO_IDS = [7201, 7203, 7205]

    @staticmethod
    def help():
        return BoilerBehaviour.__doc__ + "\r\n" + BoilerBehaviour.calculate.__doc__

    @staticmethod
    def help_calculate():
        return BoilerBehaviour.__init__.__doc__.format(
            ", ".join("{0}".format(n) for n in BoilerBehaviour.TECHNO_IDS))

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"p_supplied": 100, "techno_id": 7203}}
        OR
        {{"p_consumed": 120, "techno_id": 7203}}

        {{
            "p_consumed" OR "p_supplied"    [int.]
                (must be a positive value)
            "techno_id"                     [int.]
                (must be a REGBL ID, either {0})
        }}
        """
        
        super(BoilerBehaviour, self).__init__(args)
        self._data_folder_enerapi = conf.data_folder_enerapi


        with open(os.path.join(self._data_folder_enerapi, conf.file_boiler_techno)) as data_file:
            techno_data  = json.load(data_file)


        Guard.check_if_key_in_dict("techno_id", args)
        Guard.check_if_value_in_list(args["techno_id"], values=BoilerBehaviour.TECHNO_IDS)

        calc_consumed = True

        if "p_consumed" in args:
            calc_consumed = False
            Guard.check_is_higher(args["p_consumed"], lower_limit=0)
            if "p_supplied" in args:
                raise DomainException("Both p_consumed and p_supplied are defined!")
        else:
            if "p_supplied" not in args:
                raise DomainException("Neither p_consumed or p_supplied are defined!")
            else:
                Guard.check_is_higher(args["p_supplied"], lower_limit=0)

        args["calc_consumed"] = calc_consumed

        args["techno_data"] = techno_data

        self.args = args
        
    def calculate(self):
        """
        Perform estimation of boiler supplied heating power from consumed heating power.
        Or perform estimation of boiler consumed heating power from supplied heating power.
        The returned object is of the form:

        ```
        {
            p_supplied  OR  p_consumed      [kW]
            techno_id                       [int.]
        }
        ```

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        p_supplied      [kW]        Supplied heating power
        p_consumed      [kW]        Consumed heating power
        techno_id       [int.]      Building's energy source

        *********************************************************************
        Outputs:
        *********************************************************************
        p_supplied      [kW]        Supplied heating power
        p_consumed      [kW]        Consumed heating power

        Every estimation is based on parameters and coefficients found in [1].

        *********************************************************************
        Reference:
        *********************************************************************
        [1] L. Girardin. "A GIS-based Methodology for the Evaluation of Integrated Energy Systems in Urban Area".
        PhD thesis, STI, Lausanne, 2012

        http://infoscience.epfl.ch/record/170535/files/EPFL_TH5287.pdf

        """

        efficiency = 1  # init

        for key in self.args["techno_data"]["data"]:
            if self.args["techno_id"] == self.args["techno_data"]["data"][key]["GENHZ-WW"]:
                efficiency = self.args["techno_data"]["data"][key]["efficiency"]

        if self.args["calc_consumed"]:
            p_supp = self.args["p_supplied"]
            p_cons = float(self.args["p_supplied"]) / efficiency

        else:
            p_cons = self.args["p_consumed"]
            p_supp = self.args["p_consumed"] * efficiency
        
        return {
            "p_supplied": round(p_supp, 2),
            "p_consumed": round(p_cons, 2)
        }

    def get_reference(self):
        """
        get the reference for this module
        """
        return conf.ref_girardin