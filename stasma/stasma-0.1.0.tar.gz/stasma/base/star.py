import numpy as np

from stasma.base.body import Body
from stasma import logger, utils


class Star(Body):
    MANDATORY_KWARGS = ['mass']
    OPTIONAL_KWARGS = ['surface_potential', 'synchronicity',
                       'discretization_factor', 'spots', 'color', 'polar_log_g']
    ALL_KWARGS = MANDATORY_KWARGS + OPTIONAL_KWARGS

    def __init__(self, name=None, suppress_logger=False, **kwargs):
        """

        :param name: char
        :param suppress_logger: bool
        :param kwargs:
            :**kwargs options**:
                * **mass** * --  float or astropy.units.Quantity;
                        mass of Start object
                * **surface_potential** * --  float;
                        unit-less surface potential of Star
                * **synchronicity** * --  float;
                        synchornicity of Star defined in generalized Roche potential
                * **discretization_factor** * --  float;
                        average angular distance of two nearest points on Star surface
                * **spots** * --  list of dicts;
                        list of spots definition (see ``from stasma.base.Spot``)
                * **color** * --  float or astropy.units.Quantity;
                        mass of Start object
                * **polar_log_g** * --  float;
                        polar gravity acceleration in log10 of cgs units
                * **color** * -- list; [<0-255>, <0-255>, <0-255>]
                        color definition for plotting

        """
        utils.invalid_kwarg_checker(kwargs, Star.ALL_KWARGS, instance_of=Star)
        utils.check_missing_kwargs(Star.MANDATORY_KWARGS, kwargs, instance_of=Star)
        super(Star, self).__init__(name=name, **kwargs)

        # get logger
        self._logger = logger.getLogger(Star.__name__, suppress=suppress_logger)

        # default values of properties
        self._surface_potential = None
        self._backward_radius = None
        self._polar_radius = None
        self._synchronicity = None
        self._forward_radius = None
        self._side_radius = None
        self._equatorial_radius = None
        self._critical_surface_potential = None
        self._pulsations = None
        self._filling_factor = None

        # values of properties
        for kwarg in set(Star.ALL_KWARGS).difference(self.IGNORED_KWARGS):
            if kwarg in kwargs:
                self._logger.debug("setting property {} "
                                   "of class instance {} to {}".format(kwarg, Star.__name__, kwargs[kwarg]))
                setattr(self, kwarg, kwargs[kwarg])

    @property
    def equatorial_radius(self):
        """
        returns equatorial radius in default units

        :return: float
        """
        return self._equatorial_radius

    @property
    def surface_potential(self):
        """
        returns surface potential of Star
        usage: xy.Star

        :return: float64
        """
        return self._surface_potential

    @surface_potential.setter
    def surface_potential(self, potential):
        """
        setter for surface potential
        usage: xy.surface_potential = new_potential

        :param potential: float64
        """
        self._surface_potential = np.float64(potential)

    @property
    def critical_surface_potential(self):
        return self._critical_surface_potential

    @critical_surface_potential.setter
    def critical_surface_potential(self, potential):
        self._critical_surface_potential = potential

    @property
    def backward_radius(self):
        """
        returns value of backward radius of an object in default unit
        usage: xy.backward_radius

        :return: float64
        """
        return self._backward_radius

    @property
    def forward_radius(self):
        """
        returns value of forward radius of an object in default unit returns None if it doesn't exist
        usage: xy.forward_radius

        :return: float64
        """
        return self._forward_radius

    @property
    def polar_radius(self):
        """
        returns value of polar radius of an object in default unit returns None if it doesn't exist
        usage: xy.polar_radius

        :return: float64
        """
        return self._polar_radius

    @property
    def side_radius(self):
        """
        returns value of side radius of an object in default unit
        usage: xy.side_radius

        :return: float64
        """
        return self._side_radius

