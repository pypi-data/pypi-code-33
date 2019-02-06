import numpy as np
import logging

from astropy import units as u
from matplotlib.colors import rgb_to_hsv

from stasma import units, utils


class Spot(object):
    """
    Spot data container
    """
    MANDATORY_KWARGS = ["longitude", "latitude", "angular_diameter"]
    OPTIONAL_KWARGS = ["discretization_factor", "color"]
    IGNORED_KWARGS = ['color']
    ALL_KWARGS = MANDATORY_KWARGS + OPTIONAL_KWARGS

    def __init__(self, **kwargs):
        utils.invalid_kwarg_checker(kwargs=kwargs, kwarglist=Spot.ALL_KWARGS, instance_of=Spot)
        utils.check_missing_kwargs(Spot.MANDATORY_KWARGS, kwargs, instance_of=Spot)

        self._logger = logging.getLogger(Spot.__name__)

        self._discretization_factor = None
        self._latitude = None
        self._longitude = None
        self._angular_diameter = None

        self.boundary = None
        self.boundary_center = None
        self.center = None

        self.points = None
        self.faces = None

        self.color = [1 - (255 - c) / 255.0 for c in kwargs.pop('color')] if kwargs.get('color') \
            else np.random.random_sample(3)

        for key in kwargs:
            if key not in self.IGNORED_KWARGS:
                set_val = kwargs.get(key)
                self._logger.debug("setting property {} of class instance {} to {}"
                                   "".format(key, Spot.__name__, kwargs[key]))
                setattr(self, key, set_val)

    def kwargs_serializer(self):
        return {kwarg: getattr(self, kwarg) for kwarg in self.ALL_KWARGS if getattr(self, kwarg) is not None}

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        """
        setter for spot longitude
        expecting value in degrees or as astropy units instance

        :param longitude: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(longitude, u.quantity.Quantity):
            self._longitude = np.float64(longitude.to(units.ARC_UNIT))
        elif isinstance(longitude, (int, np.int, float, np.float)):
            self._longitude = np.radians(np.float64(longitude))
        else:
            raise TypeError('input of variable `longitude` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance')

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        """
        setter for spot latitude
        expecting value in degrees or as astropy units instance

        :param latitude: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(latitude, u.quantity.Quantity):
            self._latitude = np.float64(latitude.to(units.ARC_UNIT))
        elif isinstance(latitude, (int, np.int, float, np.float)):
            self._latitude = np.radians(np.float64(latitude))
        else:
            raise TypeError('input of variable `latitude` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance')

    @property
    def angular_diameter(self):
        return self._angular_diameter

    @angular_diameter.setter
    def angular_diameter(self, angular_diameter):
        """
        setter for spot angular_diamter
        expecting value in degrees or as astropy units instance

        :param angular_diameter: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(angular_diameter, u.quantity.Quantity):
            self._angular_diameter = np.float64(angular_diameter.to(units.ARC_UNIT))
        elif isinstance(angular_diameter, (int, np.int, float, np.float)):
            self._angular_diameter = np.radians(np.float64(angular_diameter))
        else:
            raise TypeError('input of variable `angular_diamter` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')

    @property
    def discretization_factor(self):
        return self._discretization_factor

    @discretization_factor.setter
    def discretization_factor(self, discretization_factor):
        """
        setter for spot discretization_factor (mean angular size of spot face)
        expecting value in degrees or as astropy units instance

        :param discretization_factor: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(discretization_factor, u.quantity.Quantity):
            self._discretization_factor = np.float64(discretization_factor.to(units.ARC_UNIT))
        elif isinstance(discretization_factor, (int, np.int, float, np.float)):
            self._discretization_factor = np.radians(np.float64(discretization_factor))
        else:
            raise TypeError('input of variable `angular_density` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance')
