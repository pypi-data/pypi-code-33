from osem.general.enerapi.base.base import Base
from osem.general import conf
from osem.general.enerapi.common.Guard import Guard

__author__ = 'tbernhard'


class GeoThermal(Base):
    """
    Estimate geothermal power and annual energy production for a given site.
    """

    _default_parameter_value = {"ground_conductivity": 2.0, "maximum_depth": 400.0}

    @staticmethod
    def help():
        return GeoThermal.__doc__ + "\r\n" + GeoThermal.calculate.__doc__

    @staticmethod
    def help_calculate():
        return GeoThermal.__init__.__doc__.format(
                GeoThermal._default_parameter_value["ground_conductivity"],
                GeoThermal._default_parameter_value["maximum_depth"]
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"altitude": 400,  "available_area": 625}}

        {{
            "ground_conductivity": [W/(m.K)]
                    (must be positive, default value: {0})
            "altitude": [m]      (must be a positive integer)
            "maximum_depth": [m]     (float must be bigger or equal to
                    0 and smaller than 400, default value: {1})
            "available_area": [m2]     (float positive)
        }}
        """

        super(GeoThermal, self).__init__(args)

        Guard.check_if_key_in_dict("altitude", args)
        Guard.check_if_key_in_dict("available_area", args)

        Guard.check_is_higher(args["available_area"], lower_limit=0, strict=False)

        Guard.check_value_in_between(args["ground_conductivity"], min=0, max=6)
        Guard.check_value_in_between(args["altitude"], min=0, max=2000)
        Guard.check_value_in_between(args["maximum_depth"], min=0, max=400)

        self.args = args

    def calculate(self):
        """
        The returned object is of the form:
        {
            "Geothermal specific Power available":   [W/m]
            "Geothermal Power extracted":   [kW]
            "Geothermal Energy extracted":    [kWh/an]
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        ground_conductivity [W/(m.K)]        Ground conductivity
        altitude             [m]  Altitude of the site
        maximum.depth    [m]     Maximum depth authorized by the legislation
        available_area [m2]     Available area of the site

        *********************************************************************
        Outputs:
        *********************************************************************
        Geothermal specific power [W/m]         Specific power extracted from the ground
        Geothermal Power          [kW]          Geothermal power extracted from the ground
        Geothermal Energy         [MWh/an]      Annual energy extract from the ground

        *********************************************************************
        Reference:
        *********************************************************************
        Agence Qualite Construction. Maugard, Alain. Pompes a chaleur geothermiques - Les operations de forage et
        limite de prestations. Paris, France. Programme d'action pour la qualite de la construction et la
        transition energetique. 2014-07.
        http://www.programmepacte.fr/sites/default/files/pdf/
        rapport-rage-pac-geothermiques-operations-forage-limites-prestations-2014-07.pdf

        """
        # Geothermal specific power (at 400m). Polynomial extrapolation from reference :
        geothermal_sp_power_400m = -0.75 * self.args["ground_conductivity"] ** 2 \
                                   + 12.9 * self.args["ground_conductivity"] + 17.6

        # Geothermal specific power (at the defined altitude)
        ground_response_function = 7
        ground_thermal_gradient = 0.006  # [K/m]
        geothermal_sp_power = geothermal_sp_power_400m \
                              - (2 * 3.14 * self.args["ground_conductivity"] / ground_response_function
                                 * (ground_thermal_gradient * (self.args["altitude"] - 400)))

        # Geothermal power provided by the probes
        depth = self.args["maximum_depth"]
        probe_distance = 25.0
        probes_number = self.args["available_area"] / (probe_distance ** 2)
        geothermal_power = depth * geothermal_sp_power * probes_number / 1000  # kW

        # Geothermal energy provided by the probes, during one year
        h_full = 2200  # full charge hours per year [h/an]
        geothermal_energy = geothermal_power * h_full / 1000  # MWh

        return {
            "Geothermal specific power": round(geothermal_sp_power, 0),
            "Geothermal power": round(geothermal_power, 0),
            "Geothermal energy": round(geothermal_energy, 0)
        }

    def get_reference(self):

        return conf.ref_geothermal
