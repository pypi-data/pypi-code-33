import gc
import numpy as np
import scipy

from astropy import units as u
from copy import copy
from scipy.optimize import newton
from scipy.spatial.qhull import Delaunay

from stasma import utils, logger, units, const
from stasma.base.star import Star
from stasma.base.system import System
from stasma.binary_system import static, build
from stasma.binary_system.orbit import Orbit
from stasma.binary_system.plot import Plot
from stasma.conf import config

config.set_up_logging()


class BinarySystem(System):
    MANDATORY_KWARGS = ['period', 'eccentricity', 'inclination', 'argument_of_periastron']
    OPTIONAL_KWARGS = []
    ALL_KWARGS = MANDATORY_KWARGS + OPTIONAL_KWARGS

    def __init__(self, primary, secondary, name=None, suppress_logger=False, **kwargs):
        utils.invalid_kwarg_checker(kwargs, BinarySystem.ALL_KWARGS, BinarySystem)
        utils.check_missing_kwargs(BinarySystem.MANDATORY_KWARGS, kwargs, instance_of=BinarySystem)
        super(BinarySystem, self).__init__(name=name, suppress_logger=suppress_logger, **kwargs)

        # get logger
        self._logger = logger.getLogger(name=BinarySystem.__name__, suppress=suppress_logger)
        self._logger.info("initialising object {}".format(BinarySystem.__name__))
        self._logger.debug("setting property components of class instance {}".format(BinarySystem.__name__))
        self._suppress_logger = suppress_logger

        # assign components to binary system
        self._primary = primary
        self._secondary = secondary

        self._mass_ratio = self._secondary.mass / self._primary.mass

        # default values of properties
        self._period = None
        self._eccentricity = None
        self._argument_of_periastron = None
        self._orbit = None
        self._phase_shift = None
        self._semi_major_axis = None
        self._periastron_phase = None
        self._morphology = None
        self._inclination = None

        params = {
            "primary": self._primary,
            "secondary": self._secondary
        }
        params.update(**kwargs)
        self._star_params_validity_check(**params)

        for kwarg in kwargs:
            self._logger.debug("setting property {} of class instance {} to {}"
                               "".format(kwarg, BinarySystem.__name__, kwargs[kwarg]))
            setattr(self, kwarg, kwargs[kwarg])

        self.init_orbit()
        self._semi_major_axis = self.calculate_semi_major_axis()

        self._setup_critical_potential()
        self.setup_morphology()
        # todo: make distance depends on user input
        self.setup_components_radii(components_distance=self.orbit.periastron_distance)

        if not getattr(self._secondary, 'discretization_factor'):
            self._logger.info("setting discretization factor of secondary component "
                              "according discretization factor of primary component")
            self.secondary.discretization_factor = \
                self.primary.discretization_factor * self.primary.polar_radius / self.secondary.polar_radius * u.rad

        self.plot = Plot(self)

    @property
    def semi_major_axis(self):
        """
        returns semi major axis of the system in default distance unit

        :return: np.float
        """
        return self._semi_major_axis

    @semi_major_axis.setter
    def semi_major_axis(self, semi_major_axis):
        """
        returns semi major axis of the system in default distance unit

        :return: np.float
        """
        self._semi_major_axis = semi_major_axis

    def calculate_semi_major_axis(self):
        """
        calculates length semi major axis using 3rd kepler law

        :return: np.float
        """
        period = np.float64((self._period * units.PERIOD_UNIT).to(u.s))
        return (const.G * (self._primary.mass + self._secondary.mass) * period ** 2 / (4 * const.PI ** 2)) ** (1.0 / 3)

    @property
    def morphology(self):
        """
        morphology of binary star system

        :return: str; detached, semi-detached, over-contact, double-contact
        """
        return self._morphology

    @property
    def mass_ratio(self):
        """
        returns mass ratio m2/m1 of binary system components

        :return: numpy.float
        """
        return self._mass_ratio

    @mass_ratio.setter
    def mass_ratio(self, value):
        """
        disabled setter for binary system mass ratio

        :param value:
        :return:
        """
        raise Exception("property ``mass_ratio`` is read-only.")

    @property
    def primary(self):
        """
        encapsulation of primary component into binary system

        :return: class Star
        """
        return self._primary

    @property
    def secondary(self):
        """
        encapsulation of secondary component into binary system

        :return: class Star
        """
        return self._secondary

    @property
    def orbit(self):
        """
        encapsulation of orbit class into binary system

        :return: class Orbit
        """
        return self._orbit

    @property
    def period(self):
        """
        returns orbital period of binary system

        :return: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        """
        return self._period

    @period.setter
    def period(self, period):
        """
        set orbital period of binary star system, if unit is not specified, default period unit is assumed

        :param period: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(period, u.quantity.Quantity):
            self._period = np.float64(period.to(units.PERIOD_UNIT))
        elif isinstance(period, (int, np.int, float, np.float)):
            self._period = np.float64(period)
        else:
            raise TypeError('input of variable `period` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')
        self._logger.debug("setting property period of class instance {} to {}"
                           "".format(BinarySystem.__name__, self._period))

    @property
    def eccentricity(self):
        """
        eccentricity of orbit of binary star system

        :return: (np.)int, (np.)float
        """
        return self._eccentricity

    @eccentricity.setter
    def eccentricity(self, eccentricity):
        """
        set eccentricity

        :param eccentricity: (np.)int, (np.)float
        :return:
        """
        if eccentricity < 0 or eccentricity >= 1 or not isinstance(eccentricity, (int, np.int, float, np.float)):
            raise TypeError('input of variable `eccentricity` is not (np.)int or'
                            ' (np.)float or it is out of boundaries.')
        self._eccentricity = eccentricity
        self._logger.debug("setting property eccentricity of class instance {} to {}"
                           "".format(BinarySystem.__name__, self._eccentricity))

    @property
    def argument_of_periastron(self):
        """
        argument of periastron

        :return: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        """
        return self._argument_of_periastron

    @argument_of_periastron.setter
    def argument_of_periastron(self, argument_of_periastron):
        """
        setter for argument of periastron, if unit is not supplied, value in degrees is assumed

        :param argument_of_periastron: (np.)int, (np.)float, astropy.unit.quantity.Quantity
        :return:
        """
        if isinstance(argument_of_periastron, u.quantity.Quantity):
            self._argument_of_periastron = np.float64(argument_of_periastron.to(units.ARC_UNIT))
        elif isinstance(argument_of_periastron, (int, np.int, float, np.float)):
            self._argument_of_periastron = np.float64((argument_of_periastron * u.deg).to(units.ARC_UNIT))
        else:
            raise TypeError('input of variable `periastron` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')

        if not 0.0 <= self._argument_of_periastron <= const.FULL_ARC:
            self._argument_of_periastron %= const.FULL_ARC
        self._logger.debug("setting property argument of periastron of class instance {} to {}"
                           "".format(BinarySystem.__name__, self._argument_of_periastron))

    def _kwargs_serializer(self):
        """
        creating dictionary of keyword arguments of BinarySystem class in order to be able to reinitialize the class
        instance in init()

        :return: dict
        """
        serialized_kwargs = {}
        for kwarg in self.ALL_KWARGS:
            serialized_kwargs[kwarg] = getattr(self, kwarg)
        return serialized_kwargs

    def init(self):
        """
        function to reinitialize BinarySystem class instance after changing parameter(s) of binary system using setters

        :return:
        """
        self.__init__(primary=self._primary, secondary=self._secondary, **self._kwargs_serializer())

    def init_orbit(self):
        """
        encapsulating orbit class into binary system

        :return:
        """
        self._logger.debug("re/initializing orbit in class instance {} ".format(BinarySystem.__name__))
        orbit_kwargs = {key: getattr(self, key) for key in Orbit.MANDATORY_KWARGS}
        self._orbit = Orbit(suppress_logger=self._suppress_logger, **orbit_kwargs)

    def _star_params_validity_check(self, **kwargs):
        """
        checking if star instances have all additional atributes set properly

        :param kwargs: list
        :return:
        """

        if not isinstance(kwargs.get("primary"), Star):
            raise TypeError("primary component is not instance of class {}".format(Star.__name__))

        if not isinstance(kwargs.get("secondary"), Star):
            raise TypeError("secondary component is not instance of class {}".format(Star.__name__))

        # checking if stellar components have all mandatory parameters initialised
        # these parameters are not mandatory in single star system, so validity check cannot be provided
        # on whole set of MANDATORY_KWARGS in star object
        star_mandatory_kwargs = ['mass', 'surface_potential', 'synchronicity']
        missing_kwargs = []
        for component in [self._primary, self._secondary]:
            for kwarg in star_mandatory_kwargs:
                if getattr(component, kwarg) is None:
                    missing_kwargs.append("`{}`".format(kwarg))

            component_name = 'primary' if component == self._primary else 'secondary'
            if len(missing_kwargs) != 0:
                raise ValueError('mising argument(s): {} in {} component Star class'.format(
                    ', '.join(missing_kwargs), component_name))

    def _setup_critical_potential(self):
        """
        compute and set critical surface potential for both components

        :return:
        """
        self.primary.critical_surface_potential = self.critical_potential(
            component="primary", components_distance=1 - self.eccentricity
        )
        self.secondary.critical_surface_potential = self.critical_potential(
            component="secondary", components_distance=1 - self.eccentricity
        )

    def critical_potential(self, component, components_distance):
        """
        return a critical potential for target component

        :param component: str; define target component to compute critical potential; `primary` or `secondary`
        :param components_distance: np.float
        :return: np.float
        """
        args = components_distance,
        if component == "primary":
            solution = newton(self.primary_potential_derivative_x, 0.000001, args=args, tol=1e-12)
        elif component == "secondary":
            solution = newton(self.secondary_potential_derivative_x, 0.000001, args=args, tol=1e-12)
        else:
            raise ValueError("parameter `component` has incorrect value, "
                             "use `primary` or `secondary`")

        if not np.isnan(solution):
            args = components_distance, 0.0, const.HALF_PI
            if component == "primary":
                args = self.pre_calculate_for_potential_value_primary(*args)
                return abs(self.potential_value_primary(solution, *args))
            elif component == 'secondary':
                args = self.pre_calculate_for_potential_value_secondary(*args)
                return abs(self.potential_value_secondary(components_distance - solution, *args))
        else:
            raise ValueError("iteration process to solve critical potential seems to lead nowhere "
                             "(critical potential _solver has failed).")

    def pre_calculate_for_potential_value_secondary(self, *args):
        """
        function calculates auxiliary values for calculation of secondary component potential, and therefore they don't
        need to be wastefully recalculated every iteration in solver

        :param args: (component distance, azimut angle (0, 2pi), latitude angle (0, pi)
        :return: tuple: (b, c, d, e, f) such that: Psi2 = q/r + 1/sqrt(b+r^2+Cr) - d*r + e*x^2 + f
        """
        distance, phi, theta = args  # distance between components, azimut angle, latitude angle (0,180)

        cs = np.cos(phi) * np.sin(theta)

        b = np.power(distance, 2)
        c = 2 * distance * cs
        d = cs / b
        e = 0.5 * np.power(self.secondary.synchronicity, 2) * (1 + self.mass_ratio) * (1 - np.power(np.cos(theta), 2))
        f = 0.5 - 0.5 * self.mass_ratio

        if np.isscalar(phi):
            return b, c, d, e, f
        else:
            bb = b * np.ones(np.shape(phi))
            ff = f * np.ones(np.shape(phi))
            return np.column_stack((bb, c, d, e, ff))

    def primary_potential_derivative_x(self, x, *args):
        """
        derivative of potential function perspective of primary component along the x axis

        :param x: (np.)float
        :param args: tuple ((np.)float, (np.)float); (components distance, synchronicity of primary component)
        :return: (np.)float
        """
        d, = args
        r_sqr, rw_sqr = x ** 2, (d - x) ** 2
        return - (x / r_sqr ** (3.0 / 2.0)) + ((self.mass_ratio * (d - x)) / rw_sqr ** (
            3.0 / 2.0)) + self.primary.synchronicity ** 2 * (self.mass_ratio + 1) * x - self.mass_ratio / d ** 2

    def secondary_potential_derivative_x(self, x, *args):
        """
        derivative of potential function perspective of secondary component along the x axis

        :param x: (np.)float
        :param args: tuple ((np.)float, (np.)float); (components distance, synchronicity of secondary component)
        :return: (np.)float
        """
        d, = args
        r_sqr, rw_sqr = x ** 2, (d - x) ** 2
        return - (x / r_sqr ** (3.0 / 2.0)) + ((self.mass_ratio * (d - x)) / rw_sqr ** (
            3.0 / 2.0)) - self.secondary.synchronicity ** 2 * (self.mass_ratio + 1) * (d - x) + (1.0 / d ** 2)

    def potential_value_primary(self, radius, *args):
        """
        calculates modified kopal potential from point of view of primary component

        :param radius: (np.)float; spherical variable
        :param args: tuple: (B, C, D, E) such that: Psi1 = 1/r + A/sqrt(B+r^2+Cr) - D*r + E*x^2
        :return: (np.)float
        """

        b, c, d, e = args  # auxiliary values pre-calculated in pre_calculate_for_potential_value_primary()
        radius2 = np.power(radius, 2)

        return 1 / radius + self.mass_ratio / np.sqrt(b + radius2 - c * radius) - d * radius + e * radius2

    def potential_value_secondary(self, radius, *args):
        """
        calculates modified kopal potential from point of view of secondary component

        :param radius: np.float; spherical variable
        :param args: tuple: (b, c, d, e, f) such that: Psi2 = q/r + 1/sqrt(b+r^2-Cr) - d*r + e*x^2 + f
        :return: np.float
        """
        b, c, d, e, f = args
        radius2 = np.power(radius, 2)

        return self.mass_ratio / radius + 1. / np.sqrt(b + radius2 - c * radius) - d * radius + e * radius2 + f

    def pre_calculate_for_potential_value_primary(self, *args):
        """
        function calculates auxiliary values for calculation of primary component potential, and therefore they don't
        need to be wastefully recalculated every iteration in solver

        :param args: (component distance, azimut angle (0, 2pi), latitude angle (0, pi)
        :return: tuple: (b, c, d, e) such that: Psi1 = 1/r + a/sqrt(b+r^2+c*r) - d*r + e*x^2
        """
        distance, phi, theta = args  # distance between components, azimuth angle, latitude angle (0,180)

        cs = np.cos(phi) * np.sin(theta)

        b = np.power(distance, 2)
        c = 2 * distance * cs
        d = (self.mass_ratio * cs) / b
        e = 0.5 * np.power(self.primary.synchronicity, 2) * (1 + self.mass_ratio) * (1 - np.power(np.cos(theta), 2))

        if np.isscalar(phi):
            return b, c, d, e
        else:
            bb = b * np.ones(np.shape(phi))
            return np.column_stack((bb, c, d, e))

    def lagrangian_points(self):
        """

        :return: list; x-values of libration points [L3, L1, L2] respectively
        """

        def potential_dx(x, *args):
            """
            general potential in case of primary.synchornicity = secondary.synchronicity = 1.0 and eccentricity = 0.0

            :param x: (np.)float
            :param args: tuple; periastron distance of components
            :return: (np.)float
            """
            d, = args
            r_sqr, rw_sqr = x ** 2, (d - x) ** 2
            return - (x / r_sqr ** (3.0 / 2.0)) + ((self.mass_ratio * (d - x)) / rw_sqr ** (
                3.0 / 2.0)) + (self.mass_ratio + 1) * x - self.mass_ratio / d ** 2

        periastron_distance = self.orbit.periastron_distance
        xs = np.linspace(- periastron_distance * 3.0, periastron_distance * 3.0, 100)

        args_val = periastron_distance,
        round_to = 10
        points, lagrange = [], []

        for x_val in xs:
            try:
                # if there is no valid value (in case close to x=0.0, potential_dx diverge)
                np.seterr(divide='raise', invalid='raise')
                potential_dx(round(x_val, round_to), *args_val)
                np.seterr(divide='print', invalid='print')
            except Exception as e:
                self._logger.debug("invalid value passed to potential, exception: {0}".format(str(e)))
                continue

            try:
                solution, _, ier, _ = scipy.optimize.fsolve(potential_dx, x_val, full_output=True, args=args_val,
                                                            xtol=1e-12)
                if ier == 1:
                    if round(solution[0], 5) not in points:
                        try:
                            value_dx = abs(round(potential_dx(solution[0], *args_val), 4))
                            use = True if value_dx == 0 else False
                        except Exception as e:
                            self._logger.debug("skipping sollution for x: {0} due to exception: {1}"
                                               "".format(x_val, str(e)))
                            use = False

                        if use:
                            points.append(round(solution[0], 5))
                            lagrange.append(solution[0])
                            if len(lagrange) == 3:
                                break
            except Exception as e:
                self._logger.debug("solution for x: {0} lead to nowhere, exception: {1}".format(x_val, str(e)))
                continue

        return sorted(lagrange) if self.mass_ratio < 1.0 else sorted(lagrange, reverse=True)

    def libration_potentials(self):
        """
        return potentials in L3, L1, L2 respectively

        :return: list; [Omega(L3), Omega(L1), Omega(L2)]
        """

        def potential(radius):
            theta, d = const.HALF_PI, self.orbit.periastron_distance
            if isinstance(radius, (float, int, np.float, np.int)):
                radius = [radius]
            elif not isinstance(radius, (list, np.array)):
                raise ValueError("incorrect value of variable `radius`")

            p_values = []
            for r in radius:
                phi, r = (0.0, r) if r >= 0 else (const.PI, abs(r))

                block_a = 1.0 / r
                block_b = self.mass_ratio / (np.sqrt(np.power(d, 2) + np.power(r, 2) - (
                    2.0 * r * np.cos(phi) * np.sin(theta) * d)))
                block_c = (self.mass_ratio * r * np.cos(phi) * np.sin(theta)) / (np.power(d, 2))
                block_d = 0.5 * (1 + self.mass_ratio) * np.power(r, 2) * (
                    1 - np.power(np.cos(theta), 2))

                p_values.append(block_a + block_b - block_c + block_d)
            return p_values

        lagrangian_points = self.lagrangian_points()
        return potential(lagrangian_points)

    def setup_morphology(self):
        """
        Setup binary star class property `morphology`
        :return:
        """
        __PRECISSION__ = 1e-8
        __SETUP_VALUE__ = None
        if (self.primary.synchronicity == 1 and self.secondary.synchronicity == 1) and self.eccentricity == 0.0:
            lp = self.libration_potentials()

            self.primary.filling_factor = static.compute_filling_factor(self.primary.surface_potential, lp)
            self.secondary.filling_factor = static.compute_filling_factor(self.secondary.surface_potential, lp)

            if ((1 > self.secondary.filling_factor > 0) or (1 > self.primary.filling_factor > 0)) and \
                    (abs(self.primary.filling_factor - self.secondary.filling_factor) > __PRECISSION__):
                raise ValueError("detected over-contact binary system, but potentials of components are not the same")
            if self.primary.filling_factor > 1 or self.secondary.filling_factor > 1:
                raise ValueError("non-physical system: primary_filling_factor or "
                                 "secondary_filling_factor is greater then 1, "
                                 "filling factor is obtained as following:"
                                 "(Omega_{inner} - Omega) / (Omega_{inner} - Omega_{outter})")

            if (abs(self.primary.filling_factor) < __PRECISSION__ and self.secondary.filling_factor < 0) or (
                            self.primary.filling_factor < 0 and
                            abs(self.secondary.filling_factor) < __PRECISSION__) or (
                            abs(self.primary.filling_factor) < __PRECISSION__ and
                            abs(self.secondary.filling_factor) < __PRECISSION__):
                __SETUP_VALUE__ = "semi-detached"
            elif self.primary.filling_factor < 0 and self.secondary.filling_factor < 0:
                __SETUP_VALUE__ = "detached"
            elif 1 >= self.primary.filling_factor > 0:
                __SETUP_VALUE__ = "over-contact"
            elif self.primary.filling_factor > 1 or self.secondary.filling_factor > 1:
                raise ValueError("non-physical system: potential of components is to low")

        else:
            self.primary.filling_factor, self.secondary.filling_factor = None, None
            if (abs(self.primary.surface_potential - self.primary.critical_surface_potential) < __PRECISSION__) and \
                    (abs(
                            self.secondary.surface_potential - self.secondary.critical_surface_potential) < __PRECISSION__):
                __SETUP_VALUE__ = "double-contact"

            elif (not (not (abs(
                        self.primary.surface_potential - self.primary.critical_surface_potential) < __PRECISSION__) or not (
                        self.secondary.surface_potential > self.secondary.critical_surface_potential))) or \
                    ((abs(
                            self.secondary.surface_potential - self.secondary.critical_surface_potential) < __PRECISSION__)
                     and (self.primary.surface_potential > self.primary.critical_surface_potential)):
                __SETUP_VALUE__ = "semi-detached"

            elif (self.primary.surface_potential > self.primary.critical_surface_potential) and (
                        self.secondary.surface_potential > self.secondary.critical_surface_potential):
                __SETUP_VALUE__ = "detached"

            else:
                raise ValueError("non-physical system, "
                                 "change stellar parameters")
        self._morphology = __SETUP_VALUE__

    def setup_components_radii(self, components_distance):
        fns = [self.calculate_polar_radius, self.calculate_side_radius, self.calculate_backward_radius]
        components = ['primary', 'secondary']

        for component in components:
            component_instance = getattr(self, component)
            for fn in fns:
                self._logger.debug('initialising {} for {} component'.format(
                    ' '.join(str(fn.__name__).split('_')[1:]),
                    component
                ))
                param = '_{}'.format('_'.join(str(fn.__name__).split('_')[1:]))
                radius = fn(component, components_distance)
                setattr(component_instance, param, radius)
                if self.morphology != 'over-contact':
                    radius = self.calculate_forward_radius(component, components_distance)
                    setattr(component_instance, '_forward_radius', radius)

    def calculate_radius(self, *args):
        """
        function calculates radius of the star in given direction of arbitrary direction vector (in spherical
        coordinates) starting from the centre of the star

        :param args: tuple - (component: str - `primary` or `secondary`,
                              components_distance: float - distance between components in SMA units,
                              phi: float - longitudonal angle of direction vector measured from point under L_1 in
                                           positive direction (in radians)
                              omega: float - latitudonal angle of direction vector measured from north pole (in radians)
                              )
        :return: float - radius
        """
        if args[0] == 'primary':
            fn = self.potential_primary_fn
            precalc = self.pre_calculate_for_potential_value_primary
        elif args[0] == 'secondary':
            fn = self.potential_secondary_fn
            precalc = self.pre_calculate_for_potential_value_secondary
        else:
            raise ValueError('invalid value of `component` argument {}. Expecting `primary` or `secondary`'
                             .format(args[0]))

        scipy_solver_init_value = np.array([args[1] / 1e4])
        argss = precalc(*args[1:])
        solution, a, ier, b = scipy.optimize.fsolve(fn, scipy_solver_init_value,
                                                    full_output=True, args=argss, xtol=1e-10)

        # check for regular solution
        if ier == 1 and not np.isnan(solution[0]) and 30 >= solution[0] >= 0:
            return solution[0]
        else:
            if 0 < solution[0] < 1.0:
                return solution[0]
            else:
                raise ValueError('invalid value of radius {} was calculated'.format(solution))

    def calculate_polar_radius(self, component, components_distance):
        """
        calculates polar radius in the similar manner as in BinarySystem.compute_equipotential_boundary method

        :param component: str; `primary` or `secondary`
        :param components_distance: float
        :return: float; polar radius
        """
        args = (component, components_distance, 0.0, 0.0)
        return self.calculate_radius(*args)

    def calculate_side_radius(self, component, components_distance):
        """
        calculates side radius in the similar manner as in BinarySystem.compute_equipotential_boundary method

        :param component: str; `primary` or `secondary`
        :param components_distance: float
        :return: float; side radius
        """
        args = (component, components_distance, const.HALF_PI, const.HALF_PI)
        return self.calculate_radius(*args)

    def calculate_backward_radius(self, component, components_distance):
        """
        calculates backward radius in the similar manner as in BinarySystem.compute_equipotential_boundary method

        :param component: str; `primary` or `secondary`
        :param components_distance: float
        :return: float; polar radius
        """

        args = (component, components_distance, const.PI, const.HALF_PI)
        return self.calculate_radius(*args)

    def calculate_forward_radius(self, component, components_distance):
        """
        calculates forward radius in the similar manner as in BinarySystem.compute_equipotential_boundary method,
        NOT very usable in over-contact systems

        :param component:
        :param components_distance:
        :return:
        """
        args = (component, components_distance, 0.0, const.HALF_PI)
        return self.calculate_radius(*args)

    def potential_primary_fn(self, radius, *args):
        """
        implicit potential function from perspective of primary component

        :param radius: np.float; spherical variable
        :param args: (np.float, np.float, np.float); (component distance, azimutal angle, polar angle)
        :return:
        """
        return self.potential_value_primary(radius, *args) - self.primary.surface_potential

    def potential_secondary_fn(self, radius, *args):
        """
        implicit potential function from perspective of secondary component

        :param radius: np.float; spherical variable
        :param args: (np.float, np.float, np.float); (component distance, azimutal angle, polar angle)
        :return: np.float
        """
        return self.potential_value_secondary(radius, *args) - self.secondary.surface_potential

    def potential_primary_cylindrical_fn(self, radius, *args):
        """
        implicit potential function from perspective of primary component given in cylindrical coordinates

        :param radius: np.float
        :param args: tuple: (phi, z) - polar coordinates
        :return:
        """
        return self.potential_value_primary_cylindrical(radius, *args) - self.primary.surface_potential

    def potential_secondary_cylindrical_fn(self, radius, *args):
        """
        implicit potential function from perspective of secondary component given in cylindrical coordinates

        :param radius: np.float
        :param args: tuple: (phi, z) - polar coordinates
        :return: np.float
        """
        return self.potential_value_secondary_cylindrical(radius, *args) - self.secondary.surface_potential

    def potential_value_primary_cylindrical(self, radius, *args):
        """
        calculates modified kopal potential from point of view of primary component in cylindrical coordinates
        r_n, phi_n, z_n, where z_n = x and heads along z axis, this function is intended for generation of ``necks``
        of W UMa systems, therefore components distance = 1 an synchronicity = 1 is assumed

        :param radius: np.float
        :param args: tuple: (a, b, c, d, e, f) such that: Psi1 = 1/sqrt(a+r^2) + q/sqrt(b + r^2) - c + d*(e+f*r^2)
        :return:
        """
        a, b, c, d, e, f = args

        radius2 = np.power(radius, 2)
        return 1 / np.sqrt(a + radius2) + self.mass_ratio / np.sqrt(b + radius2) - c + d * (e + f * radius2)

    def potential_value_secondary_cylindrical(self, radius, *args):
        """
        calculates modified kopal potential from point of view of secondary component in cylindrical coordinates
        r_n, phi_n, z_n, where z_n = x and heads along z axis, this function is intended for generation of ``necks``
        of W UMa systems, therefore components distance = 1 an synchronicity = 1 is assumed

        :param radius: np.float
        :param args: tuple: (a, b, c, d, e, f, G) such that: Psi2 = q/sqrt(a+r^2) + 1/sqrt(b+r^2) - c + d*(e+f*r^2) + G
        :return:
        """
        a, b, c, d, e, f = args

        radius2 = np.power(radius, 2)
        return self.mass_ratio / np.sqrt(a + radius2) + 1. / np.sqrt(b + radius2) + c * (d + e * radius2) + f

    def pre_calculate_for_potential_value_primary_cylindrical(self, *args):
        """
        function calculates auxiliary values for calculation of primary component potential  in cylindrical symmetry,
        and therefore they don't need to be wastefully recalculated every iteration in solver

        :param args: (azimut angle (0, 2pi), z_n (cylindrical, identical with cartesian x))
        :return: tuple: (a, b, c, d, e, f) such that: Psi1 = 1/sqrt(a+r^2) + q/sqrt(b + r^2) - c + d*(e+f*r^2)
        """
        phi, z = args

        qq = self.mass_ratio / (1 + self.mass_ratio)

        a = np.power(z, 2)
        b = np.power(1 - z, 2)
        c = 0.5 * self.mass_ratio * qq
        d = 0.5 + 0.5 * self.mass_ratio
        e = np.power(qq - z, 2)
        f = np.power(np.sin(phi), 2)

        return a, b, c, d, e, f

    def pre_calculate_for_potential_value_secondary_cylindrical(self, *args):
        """
        function calculates auxiliary values for calculation of secondary component potential in cylindrical symmetry,
        and therefore they don't need to be wastefully recalculated every iteration in solver

        :param args: (azimut angle (0, 2pi), z_n (cylindrical, identical with cartesian x))
        :return: tuple: (a, b, c, d, e, f, G) such that: Psi2 = q/sqrt(a+r^2) + 1/sqrt(b + r^2) - c + d*(e+f*r^2) + G
        """
        phi, z = args

        qq = 1.0 / (1 + self.mass_ratio)

        a = np.power(z, 2)
        b = np.power(1 - z, 2)
        c = 0.5 / qq
        d = np.power(qq - z, 2)
        e = np.power(np.sin(phi), 2)
        f = 0.5 - 0.5 * self.mass_ratio - 0.5 * qq

        return a, b, c, d, e, f

    def build_mesh(self, component=None, components_distance=None, return_mesh=False):
        return build.build_mesh(self, component, components_distance, return_mesh)

    def build_surface(self, component=None, components_distance=None, return_surface=False):
        return build.build_surface(self, component, components_distance, return_surface)

    def build_surface_with_no_spots(self, component=None, components_distance=None):
        return build.build_surface_with_no_spots(self, component, components_distance)

    def build_surface_with_spots(self, component=None, components_distance=None):
        return build.build_surface_with_spots(self, component, components_distance)

    def build_color_map(self, component=None, components_distance=None):
        return build.build_color_map(self, component, components_distance)

    def detached_system_surface(self, component=None, components_distance=None, points=None):
        """
        calculates surface faces from the given component's points in case of detached or semi-contact system

        :param components_distance: float
        :param points:
        :param component: str
        :return: np.array - N x 3 array of vertices indices
        """
        component_instance = getattr(self, component)
        if points is None:
            points = component_instance.points

        if not np.any(points):
            raise ValueError("{} component, with class instance name {} do not contain any valid "
                             "surface point to triangulate".format(component, component_instance.name))
        # there is a problem with triangulation of near over-contact system, delaunay is not good with pointy surfaces
        critical_pot = self.primary.critical_surface_potential if component == 'primary' \
            else self.secondary.critical_surface_potential
        potential = self.primary.surface_potential if component == 'primary' \
            else self.secondary.surface_potential
        if potential - critical_pot > 0.01:
            self._logger.debug('triangulating surface of {} component using standard method.'.format(component))
            triangulation = Delaunay(points)
            triangles_indices = triangulation.convex_hull
        else:
            self._logger.debug('surface of {} component is near or at critical potential, '
                               'therefore custom triangulation method for (near)critical '
                               'potential surfaces will be used.'.format(component))
            # calculating closest point to the barycentre
            r_near = np.max(points[:, 0]) if component == 'primary' else np.min(points[:, 0])
            # projection of component's far side surface into ``sphere`` with radius r1

            points_to_transform = copy(points)
            if component == 'secondary':
                points_to_transform[:, 0] -= components_distance
            projected_points = \
                r_near * points_to_transform / np.linalg.norm(points_to_transform, axis=1)[:, None]
            if component == 'secondary':
                projected_points[:, 0] += components_distance

            triangulation = Delaunay(projected_points)
            triangles_indices = triangulation.convex_hull

        return triangles_indices

    def over_contact_system_surface(self, component=None, points=None, **kwargs):
        # do not remove kwargs, keep compatible interface w/ detached where components distance has to be provided
        # in this case,m components distance is sinked in kwargs and not used
        """
        calculates surface faces from the given component's points in case of over-contact system

        :param points: numpy.array - points to triangulate
        :param component: str - `primary` or `secondary`
        :return: np.array - N x 3 array of vertice indices
        """
        component_instance = getattr(self, component)
        if points is None:
            points = component_instance.points
        if np.isnan(points).any():
            raise ValueError("{} component, with class instance name {} contain any valid point to triangulate"
                             "".format(component, component_instance.name))
        # calculating position of the neck
        neck_x = np.max(points[:, 0]) if component == 'primary' else np.min(points[:, 0])
        # parameter k is used later to transform inner surface to quasi sphere (convex object) which will be then
        # triangulated
        k = neck_x / (neck_x + 0.01) if component == 'primary' else neck_x / ((1 - neck_x) + 0.01)

        # projection of component's far side surface into ``sphere`` with radius r1
        projected_points = np.empty(np.shape(points), dtype=float)

        # outside facing points are just inflated to match with transformed inner surface
        # condition to select outward facing points
        outside_points_test = points[:, 0] <= 0 if component == 'primary' else points[:, 0] >= 1
        outside_points = points[outside_points_test]
        if component == 'secondary':
            outside_points[:, 0] -= 1
        projected_points[outside_points_test] = \
            neck_x * outside_points / np.linalg.norm(outside_points, axis=1)[:, None]
        if component == 'secondary':
            projected_points[:, 0] += 1

        # condition to select outward facing points
        inside_points_test = (points[:, 0] > 0)[:-1] if component == 'primary' else (points[:, 0] < 1)[:-1]
        # if auxiliary point was used than  it is not appended to list of inner points to be transformed
        # (it would cause division by zero error)
        inside_points_test = np.append(inside_points_test, False) if \
            np.array_equal(points[-1], np.array([neck_x, 0, 0])) else np.append(inside_points_test, True)
        inside_points = points[inside_points_test]
        # scaling radii for each point in cylindrical coordinates
        r = (neck_x ** 2 - (k * inside_points[:, 0]) ** 2) ** 0.5 if component == 'primary' else \
            (neck_x ** 2 - (k * (1 - inside_points[:, 0])) ** 2) ** 0.5

        length = np.linalg.norm(inside_points[:, 1:], axis=1)
        projected_points[inside_points_test, 0] = inside_points[:, 0]
        projected_points[inside_points_test, 1:] = r[:, None] * inside_points[:, 1:] / length[:, None]
        # if auxiliary point was used, than it will be appended to list of transformed points
        if np.array_equal(points[-1], np.array([neck_x, 0, 0])):
            projected_points[-1] = points[-1]

        triangulation = Delaunay(projected_points)
        triangles_indices = triangulation.convex_hull

        # removal of faces on top of the neck
        neck_test = ~(np.equal(points[triangles_indices][:, :, 0], neck_x).all(-1))
        new_triangles_indices = triangles_indices[neck_test]

        return new_triangles_indices

    def evaluate_spots_mesh(self, components_distance, component=None):
        """
        compute points of each spots and assigns values to spot container instance

        :param component:
        :param components_distance: float
        :return:
        """

        def solver_condition(x, *_args):
            if isinstance(x, np.ndarray):
                x = x[0]
            point = utils.spherical_to_cartesian([x, _args[1], _args[2]])
            point[0] = point[0] if component == "primary" else components_distance - point[0]
            # ignore also spots where one of points is situated just on the neck
            if self.morphology == "over-contact":
                if (component == "primary" and point[0] >= neck_position) or \
                        (component == "secondary" and point[0] <= neck_position):
                    return False
            return True

        components = static.component_to_list(component)
        fns = {
            "primary": (self.potential_primary_fn, self.pre_calculate_for_potential_value_primary),
            "secondary": (self.potential_secondary_fn, self.pre_calculate_for_potential_value_secondary)
        }
        fns = {_component: fns[_component] for _component in components}

        # in case of wuma system, get separation and make additional test of location of each point (if primary
        # spot doesn't intersect with secondary, if does, then such spot will be skipped completly)
        neck_position = self.calculate_neck_position() if self.morphology == "over-contact" else 1e10

        for component, functions in fns.items():
            potential_fn, precalc_fn = functions
            self._logger.info("evaluating spots for {} component".format(component))
            component_instance = getattr(self, component)

            if not component_instance.spots:
                self._logger.info("no spots to evaluate for {} component -- continue.".format(component))
                continue

            # iterate over spots
            for spot_index, spot_instance in list(component_instance.spots.items()):
                # lon -> phi, lat -> theta
                lon, lat = spot_instance.longitude, spot_instance.latitude

                component_instance.setup_spot_instance_discretization_factor(spot_instance, spot_index)
                alpha = spot_instance.discretization_factor
                diameter = spot_instance.angular_diameter

                # initial containers for current spot
                boundary_points, spot_points = list(), list()

                # initial radial vector
                radial_vector = np.array([1.0, lon, lat])  # unit radial vector to the center of current spot
                center_vector = utils.spherical_to_cartesian([1.0, lon, lat])

                args1, use = (components_distance, radial_vector[1], radial_vector[2]), False
                args2 = precalc_fn(*args1)
                kwargs = {'solver_condition_args': args1}
                solution, use = self.solver(potential_fn, solver_condition, *args2, **kwargs)

                if not use:
                    # in case of spots, each point should be usefull, otherwise remove spot from
                    # component spot list and skip current spot computation
                    self._logger.warning("center of spot {} doesn't satisfy reasonable conditions and "
                                         "entire spot will be omitted."
                                         "".format(spot_instance.kwargs_serializer()))

                    component_instance.remove_spot(spot_index=spot_index)
                    continue

                spot_center_r = solution
                spot_center = utils.spherical_to_cartesian([spot_center_r, lon, lat])

                # compute euclidean distance of two points on spot (x0)
                # we have to obtain distance between center and 1st point in 1st inner ring of spot
                args1, use = (components_distance, lon, lat + alpha), False
                args2 = precalc_fn(*args1)
                kwargs = {'solver_condition_args': args1}
                solution, use = self.solver(potential_fn, solver_condition, *args2, **kwargs)

                if not use:
                    # in case of spots, each point should be usefull, otherwise remove spot from
                    # component spot list and skip current spot computation
                    self._logger.warning("first inner ring of spot {} doesn't satisfy reasonable conditions and "
                                         "entire spot will be omitted"
                                         "".format(spot_instance.kwargs_serializer()))

                    component_instance.remove_spot(spot_index=spot_index)
                    continue

                x0 = np.sqrt(spot_center_r ** 2 + solution ** 2 - (2.0 * spot_center_r * solution * np.cos(alpha)))

                # number of points in latitudal direction
                # + 1 to obtain same discretization as object itself
                num_radial = int(np.round((diameter * 0.5) / alpha)) + 1
                self._logger.debug('number of rings in spot {} is {}'
                                   ''.format(spot_instance.kwargs_serializer(), num_radial))
                thetas = np.linspace(lat, lat + (diameter * 0.5), num=num_radial, endpoint=True)

                num_azimuthal = [1 if i == 0 else int(i * 2.0 * np.pi * x0 // x0) for i in range(0, len(thetas))]
                deltas = [np.linspace(0., const.FULL_ARC, num=num, endpoint=False) for num in num_azimuthal]

                try:
                    for theta_index, theta in enumerate(thetas):
                        # first point of n-th ring of spot (counting start from center)
                        default_spherical_vector = [1.0, lon % const.FULL_ARC, theta]

                        for delta_index, delta in enumerate(deltas[theta_index]):
                            # rotating default spherical vector around spot center vector and thus generating concentric
                            # circle of points around centre of spot
                            delta_vector = utils.arbitrary_rotation(theta=delta, omega=center_vector,
                                                                    vector=utils.spherical_to_cartesian(
                                                                        default_spherical_vector),
                                                                    degrees=False)

                            spherical_delta_vector = utils.cartesian_to_spherical(delta_vector)

                            args1 = (components_distance, spherical_delta_vector[1], spherical_delta_vector[2])
                            args2 = precalc_fn(*args1)
                            kwargs = {'original_kwargs': args1}
                            solution, use = self.solver(potential_fn, solver_condition, *args2, **kwargs)

                            if not use:
                                component_instance.remove_spot(spot_index=spot_index)
                                raise StopIteration

                            spot_point = utils.spherical_to_cartesian([solution, spherical_delta_vector[1],
                                                                       spherical_delta_vector[2]])
                            spot_points.append(spot_point)

                            if theta_index == len(thetas) - 1:
                                boundary_points.append(spot_point)

                except StopIteration:
                    self._logger.warning("at least 1 point of spot {} doesn't satisfy reasonable "
                                         "conditions and entire spot will be omitted"
                                         "".format(spot_instance.kwargs_serializer()))
                    continue

                boundary_center = spot_points[0]

                # todo: max_size, check when triangulation
                # max size from barycenter of boundary to boundary
                spot_instance.max_size = max([np.linalg.norm(np.array(boundary_center) - np.array(b))
                                              for b in boundary_points])

                if component == "primary":
                    spot_instance.points = np.array(spot_points)
                    spot_instance.boundary = np.array(boundary_points)
                    spot_instance.center = np.array(spot_center)
                else:
                    spot_instance.points = np.array([np.array([components_distance - point[0], -point[1], point[2]])
                                                     for point in spot_points])

                    spot_instance.boundary = np.array([np.array([components_distance - point[0], -point[1], point[2]])
                                                       for point in boundary_points])

                    spot_instance.center = np.array([components_distance - spot_center[0], -spot_center[1],
                                                     spot_center[2]])
                gc.collect()

    def mesh_detached(self, component, components_distance, symmetry_output=False):
        """
        creates surface mesh of given binary star component in case of detached (semi-detached) system

        :param symmetry_output: bool - if true, besides surface points are returned also `symmetry_vector`,
                                       `base_symmetry_points_number`, `inverse_symmetry_matrix`
        :param component: str - `primary` or `secondary`
        :param components_distance: np.float
        :return: numpy.array([[x1 y1 z1],
                              [x2 y2 z2],
                                ...
                              [xN yN zN]]) - array of surface points if symmetry_output = False, else:
                 numpy.array([[x1 y1 z1],
                              [x2 y2 z2],
                                ...
                              [xN yN zN]]) - array of surface points,
                 numpy.array([indices_of_symmetrical_points]) - array which remapped surface points to symmetrical one
                                                                quarter of surface,
                 numpy.float - number of points included in symmetrical one quarter of surface,
                 numpy.array([quadrant[indexes_of_remapped_points_in_quadrant]) - matrix of four sub matrices that
                                                                                mapped basic symmetry quadrant to all
                                                                                others quadrants
        """
        component_instance = getattr(self, component)
        if component_instance.discretization_factor > const.HALF_PI:
            raise ValueError("invalid value of alpha parameter, "
                             "use value less than 90")

        alpha = component_instance.discretization_factor

        if component == 'primary':
            potential_fn = self.potential_primary_fn
            precalc_fn = self.pre_calculate_for_potential_value_primary
        elif component == 'secondary':
            potential_fn = self.potential_secondary_fn
            precalc_fn = self.pre_calculate_for_potential_value_secondary
        else:
            raise ValueError('invalid value of `component` argument: `{}`, '
                             'expecting `primary` or `secondary`.'.format(component))

        # pre calculating azimuths for surface points on quarter of the star surface
        phi, theta, separator = static.pre_calc_azimuths_for_detached_points(alpha)

        # calculating mesh in cartesian coordinates for quarter of the star
        args = phi, theta, components_distance, precalc_fn, potential_fn

        # todo: implement multiproc
        # points_q = static.get_surface_points(*args) if config.NUMBER_OF_THREADS == 1 or suppress_parallelism else \
        #     self.get_surface_points_multiproc(*args)
        points_q = static.get_surface_points(*args)

        equator = points_q[:separator[0], :]
        # assigning equator points and nearside and farside points A and B
        x_a, x_eq, x_b = equator[0, 0], equator[1: -1, 0], equator[-1, 0]
        y_a, y_eq, y_b = equator[0, 1], equator[1: -1, 1], equator[-1, 1]
        z_a, z_eq, z_b = equator[0, 2], equator[1: -1, 2], equator[-1, 2]

        # calculating points on phi = 0 meridian
        meridian = points_q[separator[0]: separator[1], :]
        x_meridian, y_meridian, z_meridian = meridian[:, 0], meridian[:, 1], meridian[:, 2]

        # the rest of the surface
        quarter = points_q[separator[1]:, :]
        x_q, y_q, z_q = quarter[:, 0], quarter[:, 1], quarter[:, 2]

        # stiching together 4 quarters of stellar surface in order:
        # north hemisphere: left_quadrant (from companion point of view):
        #                   nearside_point, farside_point, equator, quarter, meridian
        #                   right_quadrant:
        #                   quadrant, equator
        # south hemisphere: right_quadrant:
        #                   quadrant, meridian
        #                   left_quadrant:
        #                   quadrant
        x = np.array([x_a, x_b])
        y = np.array([y_a, y_b])
        z = np.array([z_a, z_b])
        x = np.concatenate((x, x_eq, x_q, x_meridian, x_q, x_eq, x_q, x_meridian, x_q))
        y = np.concatenate((y, y_eq, y_q, y_meridian, -y_q, -y_eq, -y_q, -y_meridian, y_q))
        z = np.concatenate((z, z_eq, z_q, z_meridian, z_q, z_eq, -z_q, -z_meridian, -z_q))

        x = -x + components_distance if component == 'secondary' else x
        points = np.column_stack((x, y, z))
        if symmetry_output:
            equator_length = np.shape(x_eq)[0]
            meridian_length = np.shape(x_meridian)[0]
            quarter_length = np.shape(x_q)[0]
            quadrant_start = 2 + equator_length
            base_symmetry_points_number = 2 + equator_length + quarter_length + meridian_length
            symmetry_vector = np.concatenate((np.arange(base_symmetry_points_number),  # 1st quadrant
                                              np.arange(quadrant_start, quadrant_start + quarter_length),
                                              np.arange(2, quadrant_start),  # 2nd quadrant
                                              np.arange(quadrant_start, base_symmetry_points_number),  # 3rd quadrant
                                              np.arange(quadrant_start, quadrant_start + quarter_length)
                                              ))

            points_length = np.shape(x)[0]
            inverse_symmetry_matrix = \
                np.array([np.arange(base_symmetry_points_number),  # 1st quadrant
                          np.concatenate(([0, 1],
                                          np.arange(base_symmetry_points_number + quarter_length,
                                                    base_symmetry_points_number + quarter_length + equator_length),
                                          np.arange(base_symmetry_points_number,
                                                    base_symmetry_points_number + quarter_length),
                                          np.arange(base_symmetry_points_number - meridian_length,
                                                    base_symmetry_points_number))),  # 2nd quadrant
                          np.concatenate(([0, 1],
                                          np.arange(base_symmetry_points_number + quarter_length,
                                                    base_symmetry_points_number + quarter_length + equator_length),
                                          np.arange(base_symmetry_points_number + quarter_length + equator_length,
                                                    base_symmetry_points_number + 2 * quarter_length + equator_length +
                                                    meridian_length))),  # 3rd quadrant
                          np.concatenate((np.arange(2 + equator_length),
                                          np.arange(points_length - quarter_length, points_length),
                                          np.arange(base_symmetry_points_number + 2 * quarter_length + equator_length,
                                                    base_symmetry_points_number + 2 * quarter_length + equator_length +
                                                    meridian_length)))  # 4th quadrant
                          ])

            return points, symmetry_vector, base_symmetry_points_number, inverse_symmetry_matrix
        else:
            return points

    def mesh_over_contact(self, component=None, symmetry_output=False):
        # todo: simplyfy this method
        """
        creates surface mesh of given binary star component in case of over-contact system

        :param symmetry_output: bool - if true, besides surface points are returned also `symmetry_vector`,
                                       `base_symmetry_points_number`, `inverse_symmetry_matrix`
        :param component: str - `primary` or `secondary`
        :return: numpy.array([[x1 y1 z1],
                              [x2 y2 z2],
                                ...
                              [xN yN zN]]) - array of surface points if symmetry_output = False, else:
                 numpy.array([[x1 y1 z1],
                              [x2 y2 z2],
                                ...
                              [xN yN zN]]) - array of surface points,
                 numpy.array([indices_of_symmetrical_points]) - array which remapped surface points to symmetrical one
                                                                quarter of surface,
                 numpy.float - number of points included in symmetrical one quarter of surface,
                 numpy.array([quadrant[indexes_of_remapped_points_in_quadrant]) - matrix of four sub matrices that
                                                                                mapped basic symmetry quadrant to all
                                                                                others quadrants
        """
        component_instance = getattr(self, component)
        if component_instance.discretization_factor > const.HALF_PI:
            raise ValueError("invalid value of alpha parameter, "
                             "use value less than 90")

        alpha = component_instance.discretization_factor
        scipy_solver_init_value = np.array([1. / 10000.])

        # calculating distance between components
        components_distance = self.orbit.orbital_motion(phase=0)[0][0]

        if component == 'primary':
            fn = self.potential_primary_fn
            fn_cylindrical = self.potential_primary_cylindrical_fn
            precalc = self.pre_calculate_for_potential_value_primary
            precal_cylindrical = self.pre_calculate_for_potential_value_primary_cylindrical
        elif component == 'secondary':
            fn = self.potential_secondary_fn
            fn_cylindrical = self.potential_secondary_cylindrical_fn
            precalc = self.pre_calculate_for_potential_value_secondary
            precal_cylindrical = self.pre_calculate_for_potential_value_secondary_cylindrical
        else:
            raise ValueError('invalid value of `component` argument: `{}`, '
                             'expecting `primary` or `secondary`.'.format(component))

        # generating the azimuths for neck
        neck_position, neck_polynomial = self.calculate_neck_position(return_polynomial=True)

        # calculating points on farside equator
        num = int(const.HALF_PI // alpha)
        r_eq1 = []
        phi_eq1 = np.linspace(const.HALF_PI, const.PI, num=num + 1)
        theta_eq1 = np.array([const.HALF_PI for _ in phi_eq1])
        for phi in phi_eq1:
            args = (components_distance, phi, const.HALF_PI)
            args = precalc(*args)
            solution, _, ier, _ = scipy.optimize.fsolve(fn, scipy_solver_init_value, full_output=True, args=args,
                                                        xtol=1e-12)
            r_eq1.append(solution[0])
        r_eq1 = np.array(r_eq1)
        equator1 = utils.spherical_to_cartesian(np.column_stack((r_eq1, phi_eq1, theta_eq1)))
        # assigning equator points and point A
        x_eq1, x_a = equator1[: -1, 0], equator1[-1, 0],
        y_eq1, y_a = equator1[: -1, 1], equator1[-1, 1],
        z_eq1, z_a = equator1[: -1, 2], equator1[-1, 2],

        # calculating points on phi = pi meridian
        r_meridian1 = []
        num = int(const.HALF_PI // alpha)
        phi_meridian1 = np.array([const.PI for _ in range(num)])
        theta_meridian1 = np.linspace(0., const.HALF_PI - alpha, num=num)
        for ii, theta in enumerate(theta_meridian1):
            args = (components_distance, phi_meridian1[ii], theta)
            args = precalc(*args)
            solution, _, ier, _ = scipy.optimize.fsolve(fn, scipy_solver_init_value, full_output=True, args=args,
                                                        xtol=1e-12)
            r_meridian1.append(solution[0])
        r_meridian1 = np.array(r_meridian1)
        meridian1 = utils.spherical_to_cartesian(np.column_stack((r_meridian1, phi_meridian1, theta_meridian1)))
        x_meridian1, y_meridian1, z_meridian1 = meridian1[:, 0], meridian1[:, 1], meridian1[:, 2]

        # calculating points on phi = pi/2 meridian, perpendicular to component`s distance vector
        r_meridian2 = []
        num = int(const.HALF_PI // alpha) - 1
        phi_meridian2 = np.array([const.HALF_PI for _ in range(num)])
        theta_meridian2 = np.linspace(alpha, const.HALF_PI, num=num, endpoint=False)
        for ii, theta in enumerate(theta_meridian2):
            args = (components_distance, phi_meridian2[ii], theta)
            args = precalc(*args)
            solution, _, ier, _ = scipy.optimize.fsolve(fn, scipy_solver_init_value, full_output=True, args=args,
                                                        xtol=1e-12)
            r_meridian2.append(solution[0])
        r_meridian2 = np.array(r_meridian2)
        meridian2 = utils.spherical_to_cartesian(np.column_stack((r_meridian2, phi_meridian2, theta_meridian2)))
        x_meridian2, y_meridian2, z_meridian2 = meridian2[:, 0], meridian2[:, 1], meridian2[:, 2]

        # calculating the rest of the surface on farside
        thetas = np.linspace(alpha, const.HALF_PI, num=num, endpoint=False)
        r_q1, phi_q1, theta_q1 = [], [], []
        for theta in thetas:
            alpha_corrected = alpha / np.sin(theta)
            num = int(const.HALF_PI // alpha_corrected)
            alpha_corrected = const.HALF_PI / (num + 1)
            phi_q_add = [const.HALF_PI + alpha_corrected * ii for ii in range(1, num + 1)]
            phi_q1 += phi_q_add
            for phi in phi_q_add:
                theta_q1.append(theta)
                args = (components_distance, phi, theta)
                args = precalc(*args)
                solution, _, ier, _ = scipy.optimize.fsolve(fn, scipy_solver_init_value, full_output=True, args=args,
                                                            xtol=1e-12)
                r_q1.append(solution[0])
        r_q1, phi_q1, theta_q1 = np.array(r_q1), np.array(phi_q1), np.array(theta_q1)
        quarter = utils.spherical_to_cartesian(np.column_stack((r_q1, phi_q1, theta_q1)))
        x_q1, y_q1, z_q1 = quarter[:, 0], quarter[:, 1], quarter[:, 2]

        # lets define cylindrical coordinate system r_n, phi_n, z_n for our neck where z_n = x, phi_n = 0 heads along
        # z axis
        delta_z = alpha * self.calculate_polar_radius(component=component, components_distance=1)
        if component == 'primary':
            num = 15 * int(
                neck_position // (component_instance.polar_radius * component_instance.discretization_factor))
            # position of z_n adapted to the slope of the neck, gives triangles with more similar areas
            x_curve = np.linspace(0., neck_position, num=num, endpoint=True)
            z_curve = np.polyval(neck_polynomial, x_curve)
            curve = np.column_stack((x_curve, z_curve))
            neck_lengths = np.sqrt(np.sum(np.diff(curve, axis=0) ** 2, axis=1))
            neck_length = np.sum(neck_lengths)
            segment = neck_length / (int(neck_length // delta_z) + 1)

            k = 1
            z_ns, line_sum = [], 0.0
            for ii in range(num - 2):
                line_sum += neck_lengths[ii]
                if line_sum > k * segment:
                    z_ns.append(x_curve[ii + 1])
                    k += 1
            z_ns.append(neck_position)
            z_ns = np.array(z_ns)
            # num = int(neck_position // delta_z) + 1
            # z_ns = np.linspace(delta_z, neck_position, num=num, endpoint=True)
        else:
            num = 15 * int(
                (1 - neck_position) // (component_instance.polar_radius * component_instance.discretization_factor))
            # position of z_n adapted to the slope of the neck, gives triangles with more similar areas
            x_curve = np.linspace(neck_position, 1, num=num, endpoint=True)
            z_curve = np.polyval(neck_polynomial, x_curve)
            curve = np.column_stack((x_curve, z_curve))
            neck_lengths = np.sqrt(np.sum(np.diff(curve, axis=0) ** 2, axis=1))
            neck_length = np.sum(neck_lengths)
            segment = neck_length / (int(neck_length // delta_z) + 1)

            k = 1
            z_ns, line_sum = [1 - neck_position], 0.0
            for ii in range(num - 2):
                line_sum += neck_lengths[ii]
                if line_sum > k * segment:
                    z_ns.append(1 - x_curve[ii + 1])
                    k += 1

            z_ns = np.array(z_ns)

        # generating equatorial, polar part and rest of the neck
        r_eqn, phi_eqn, z_eqn = [], [], []
        r_meridian_n, phi_meridian_n, z_meridian_n = [], [], []
        r_n, phi_n, z_n = [], [], []
        for z in z_ns:
            z_eqn.append(z)
            phi_eqn.append(const.HALF_PI)
            args = (const.HALF_PI, z)
            args = precal_cylindrical(*args)
            solution, _, ier, _ = scipy.optimize.fsolve(fn_cylindrical, scipy_solver_init_value, full_output=True,
                                                        args=args, xtol=1e-12)
            r_eqn.append(solution[0])

            z_meridian_n.append(z)
            phi_meridian_n.append(0.)
            args = (0., z)
            args = precal_cylindrical(*args)
            solution, _, ier, _ = scipy.optimize.fsolve(fn_cylindrical, scipy_solver_init_value, full_output=True,
                                                        args=args, xtol=1e-12)
            r_meridian_n.append(solution[0])

            num = int(const.HALF_PI * r_eqn[-1] // delta_z)
            num = 1 if num == 0 else num
            start_val = const.HALF_PI / num
            phis = np.linspace(start_val, const.HALF_PI, num=num - 1, endpoint=False)
            for phi in phis:
                z_n.append(z)
                phi_n.append(phi)
                args = (phi, z)
                args = precal_cylindrical(*args)
                solution, _, ier, _ = scipy.optimize.fsolve(fn_cylindrical, scipy_solver_init_value, full_output=True,
                                                            args=args, xtol=1e-12)
                r_n.append(solution[0])

        r_eqn = np.array(r_eqn)
        z_eqn = np.array(z_eqn)
        phi_eqn = np.array(phi_eqn)
        z_eqn, y_eqn, x_eqn = utils.cylindrical_to_cartesian(r_eqn, phi_eqn, z_eqn)

        r_meridian_n = np.array(r_meridian_n)
        z_meridian_n = np.array(z_meridian_n)
        phi_meridian_n = np.array(phi_meridian_n)
        z_meridian_n, y_meridian_n, x_meridian_n = \
            utils.cylindrical_to_cartesian(r_meridian_n, phi_meridian_n, z_meridian_n)

        r_n = np.array(r_n)
        z_n = np.array(z_n)
        phi_n = np.array(phi_n)
        z_n, y_n, x_n = utils.cylindrical_to_cartesian(r_n, phi_n, z_n)

        # building point blocks similar to those in detached system (equator pts, meridian pts and quarter pts)
        x_eq = np.concatenate((x_eqn, x_eq1), axis=0)
        y_eq = np.concatenate((y_eqn, y_eq1), axis=0)
        z_eq = np.concatenate((z_eqn, z_eq1), axis=0)
        x_q = np.concatenate((x_n, x_meridian2, x_q1), axis=0)
        y_q = np.concatenate((y_n, y_meridian2, y_q1), axis=0)
        z_q = np.concatenate((z_n, z_meridian2, z_q1), axis=0)
        x_meridian = np.concatenate((x_meridian_n, x_meridian1), axis=0)
        y_meridian = np.concatenate((y_meridian_n, y_meridian1), axis=0)
        z_meridian = np.concatenate((z_meridian_n, z_meridian1), axis=0)

        x = np.array([x_a])
        y = np.array([y_a])
        z = np.array([z_a])
        x = np.concatenate((x, x_eq, x_q, x_meridian, x_q, x_eq, x_q, x_meridian, x_q))
        y = np.concatenate((y, y_eq, y_q, y_meridian, -y_q, -y_eq, -y_q, -y_meridian, y_q))
        z = np.concatenate((z, z_eq, z_q, z_meridian, z_q, z_eq, -z_q, -z_meridian, -z_q))

        x = -x + components_distance if component == 'secondary' else x
        points = np.column_stack((x, y, z))
        if symmetry_output:
            equator_length = np.shape(x_eq)[0]
            meridian_length = np.shape(x_meridian)[0]
            quarter_length = np.shape(x_q)[0]
            quadrant_start = 1 + equator_length
            base_symmetry_points_number = 1 + equator_length + quarter_length + meridian_length
            symmetry_vector = np.concatenate((np.arange(base_symmetry_points_number),  # 1st quadrant
                                              np.arange(quadrant_start, quadrant_start + quarter_length),
                                              np.arange(1, quadrant_start),  # 2nd quadrant
                                              np.arange(quadrant_start, base_symmetry_points_number),  # 3rd quadrant
                                              np.arange(quadrant_start, quadrant_start + quarter_length)
                                              ))

            points_length = np.shape(x)[0]
            inverse_symmetry_matrix = \
                np.array([np.arange(base_symmetry_points_number),  # 1st quadrant
                          np.concatenate(([0],
                                          np.arange(base_symmetry_points_number + quarter_length,
                                                    base_symmetry_points_number + quarter_length + equator_length),
                                          np.arange(base_symmetry_points_number,
                                                    base_symmetry_points_number + quarter_length),
                                          np.arange(base_symmetry_points_number - meridian_length,
                                                    base_symmetry_points_number))),  # 2nd quadrant
                          np.concatenate(([0],
                                          np.arange(base_symmetry_points_number + quarter_length,
                                                    base_symmetry_points_number + quarter_length + equator_length),
                                          np.arange(base_symmetry_points_number + quarter_length + equator_length,
                                                    base_symmetry_points_number + 2 * quarter_length + equator_length +
                                                    meridian_length))),  # 3rd quadrant
                          np.concatenate((np.arange(1 + equator_length),
                                          np.arange(points_length - quarter_length, points_length),
                                          np.arange(base_symmetry_points_number + 2 * quarter_length + equator_length,
                                                    base_symmetry_points_number + 2 * quarter_length + equator_length +
                                                    meridian_length)))  # 4th quadrant
                          ])

            return points, symmetry_vector, base_symmetry_points_number, inverse_symmetry_matrix
        else:
            return points

    def calculate_neck_position(self, return_polynomial=False):
        """
        function calculates x-coordinate of the `neck` (the narrowest place) of an over-contact system
        :return: np.float (0.1)
        """
        neck_position = None
        components_distance = 1.0
        components = ['primary', 'secondary']
        points_primary, points_secondary = [], []
        fn_map = {'primary': (self.potential_primary_fn, self.pre_calculate_for_potential_value_primary),
                  'secondary': (self.potential_secondary_fn, self.pre_calculate_for_potential_value_secondary)}

        # generating only part of the surface that I'm interested in (neck in xy plane for x between 0 and 1)
        angles = np.linspace(0., const.HALF_PI, 100, endpoint=True)
        for component in components:
            for angle in angles:
                args, use = (components_distance, angle, const.HALF_PI), False

                scipy_solver_init_value = np.array([components_distance / 10000.0])
                args = fn_map[component][1](*args)
                solution, _, ier, _ = scipy.optimize.fsolve(fn_map[component][0], scipy_solver_init_value,
                                                            full_output=True, args=args, xtol=1e-12)

                # check for regular solution
                if ier == 1 and not np.isnan(solution[0]):
                    solution = solution[0]
                    if 30 >= solution >= 0:
                        use = True
                else:
                    continue

                if use:
                    if component == 'primary':
                        points_primary.append([solution * np.cos(angle), solution * np.sin(angle)])
                    elif component == 'secondary':
                        points_secondary.append([- (solution * np.cos(angle) - components_distance),
                                                 solution * np.sin(angle)])

        neck_points = np.array(points_secondary + points_primary)
        # fitting of the neck with polynomial in order to find minimum
        polynomial_fit = np.polyfit(neck_points[:, 0], neck_points[:, 1], deg=15)
        polynomial_fit_differentiation = np.polyder(polynomial_fit)
        roots = np.roots(polynomial_fit_differentiation)
        roots = [np.real(xx) for xx in roots if np.imag(xx) == 0]
        # choosing root that is closest to the middle of the system, should work...
        # idea is to rule out roots near 0 or 1
        comparision_value = 1
        for root in roots:
            new_value = abs(0.5 - root)
            if new_value < comparision_value:
                comparision_value = new_value
                neck_position = root
        if return_polynomial:
            return neck_position, polynomial_fit
        else:
            return neck_position

    def compute_equipotential_boundary(self, components_distance, plane):
        """
        compute a equipotential boundary of components (crossection of Hill plane)

        :param components_distance: (np.)float
        :param plane: str; xy, yz, zx
        :return: tuple (np.array, np.array)
        """

        components = ['primary', 'secondary']
        points_primary, points_secondary = [], []
        fn_map = {'primary': (self.potential_primary_fn, self.pre_calculate_for_potential_value_primary),
                  'secondary': (self.potential_secondary_fn, self.pre_calculate_for_potential_value_secondary)}

        angles = np.linspace(-3 * const.HALF_PI, const.HALF_PI, 300, endpoint=True)
        for component in components:
            for angle in angles:
                if utils.is_plane(plane, 'xy'):
                    args, use = (components_distance, angle, const.HALF_PI), False
                elif utils.is_plane(plane, 'yz'):
                    args, use = (components_distance, const.HALF_PI, angle), False
                elif utils.is_plane(plane, 'zx'):
                    args, use = (components_distance, 0.0, angle), False
                else:
                    raise ValueError('Invalid choice of crossection plane, use only: `xy`, `yz`, `zx`.')

                scipy_solver_init_value = np.array([components_distance / 10000.0])
                args = fn_map[component][1](*args)
                solution, _, ier, _ = scipy.optimize.fsolve(fn_map[component][0], scipy_solver_init_value,
                                                            full_output=True, args=args, xtol=1e-12)

                # check for regular solution
                if ier == 1 and not np.isnan(solution[0]):
                    solution = solution[0]
                    if 30 >= solution >= 0:
                        use = True
                else:
                    continue

                if use:
                    if utils.is_plane(plane, 'yz'):
                        if component == 'primary':
                            points_primary.append([solution * np.sin(angle), solution * np.cos(angle)])
                        elif component == 'secondary':
                            points_secondary.append([solution * np.sin(angle), solution * np.cos(angle)])
                    elif utils.is_plane(plane, 'xz'):
                        if component == 'primary':
                            points_primary.append([solution * np.sin(angle), solution * np.cos(angle)])
                        elif component == 'secondary':
                            points_secondary.append([- (solution * np.sin(angle) - components_distance),
                                                     solution * np.cos(angle)])
                    else:
                        if component == 'primary':
                            points_primary.append([solution * np.cos(angle), solution * np.sin(angle)])
                        elif component == 'secondary':
                            points_secondary.append([- (solution * np.cos(angle) - components_distance),
                                                     solution * np.sin(angle)])

        return np.array(points_primary), np.array(points_secondary)

    def _get_surface_builder_fn(self):
        """
        returns suitable triangulation function depending on morphology
        :return: function instance that performs generation surface faces
        """
        return self.over_contact_system_surface if self.morphology == "over-contact" else self.detached_system_surface
