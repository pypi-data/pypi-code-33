import numpy as np
import scipy
from astropy import units as u
from scipy.spatial.qhull import Delaunay

from stasma import utils, logger, units, const
from stasma.base.system import System
from stasma.single_system import static, build
from stasma.single_system.plot import Plot
from stasma.conf import config

config.set_up_logging()


class SingleSystem(System):
    MANDATORY_KWARGS = ['star', 'inclination', 'rotation_period']
    OPTIONAL_KWARGS = []
    ALL_KWARGS = MANDATORY_KWARGS + OPTIONAL_KWARGS

    def __init__(self, name=None, suppress_logger=False, **kwargs):
        utils.invalid_kwarg_checker(kwargs, SingleSystem.ALL_KWARGS, SingleSystem)
        utils.check_missing_kwargs(SingleSystem.KWARGS, kwargs, instance_of=SingleSystem)
        super(SingleSystem, self).__init__(name=name, **kwargs)

        # get logger
        self._logger = logger.getLogger(name=SingleSystem.__name__, suppress=suppress_logger)
        self._logger.info("initialising object {}".format(SingleSystem.__name__))

        self._logger.debug("setting property components of class instance {}".format(SingleSystem.__name__))

        self.star = kwargs['star']
        self.plot = Plot(self)
        self._rotation_period = None

        for kwarg in kwargs:
            self._logger.debug("setting property {} of class instance {} to {}"
                               "".format(kwarg, SingleSystem.__name__, kwargs[kwarg]))
            setattr(self, kwarg, kwargs[kwarg])

        # check if star object doesn't contain any meaningless parameters
        meaningless_params = {'synchronicity': self.star.synchronicity,
                              'backward radius': self.star.backward_radius,
                              'forward_radius': self.star.forward_radius,
                              'side_radius': self.star.side_radius}
        for parameter in meaningless_params:
            if meaningless_params[parameter] is not None:
                meaningless_params[parameter] = None
                self._logger.info('parameter `{0}` is meaningless in case of single star system, '
                                  'setting parameter `{0}` value to None'.format(parameter))

        # calculation of dependent parameters
        self._angular_velocity = static.angular_velocity(self.rotation_period)
        # this is also check if star surface is closed
        self.init_radii()

    @property
    def rotation_period(self):
        """
        returns rotation period of single system star in default period unit
        :return: float
        """
        return self._rotation_period

    @rotation_period.setter
    def rotation_period(self, rotation_period):
        """
        setter for rotational period of star in single star system, if unit is not specified, default period unit is
        assumed
        :param rotation_period:
        :return:
        """
        if isinstance(rotation_period, u.quantity.Quantity):
            self._rotation_period = np.float64(rotation_period.to(units.PERIOD_UNIT))
        elif isinstance(rotation_period, (int, np.int, float,
                                          np.float)):
            self._rotation_period = np.float64(rotation_period)
        else:
            raise TypeError('input of variable `rotation_period` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance')
        if self._rotation_period <= 0:
            raise ValueError('period of rotation must be non-zero positive value. Your value: {0}'
                             ''.format(rotation_period))

    def kwargs_serializer(self):
        """
        creating dictionary of keyword arguments of SingleSystem class in order to be able to reinitialize the class
        instance in init()

        :return: dict
        """
        serialized_kwargs = {}
        for kwarg in self.ALL_KWARGS:
            serialized_kwargs[kwarg] = getattr(self, kwarg)
        return serialized_kwargs

    def init(self):
        """
        function to reinitialize SingleSystem class instance after changing parameter(s) of binary system using setters

        :return:
        """
        self._logger.info('Reinitialising class instance {}'.format(SingleSystem.__name__))
        self.__init__(**self.kwargs_serializer())

    def calculate_polar_radius(self):
        """
        returns polar radius of the star in default units

        :return: float
        """
        polar_gravity_acceleration = np.power(10, self.star.polar_log_g)
        return np.power(const.G * self.star.mass / polar_gravity_acceleration, 0.5)

    def calculate_equatorial_radius(self):
        """
        returns equatorial radius of the star in default units

        :return: float
        """
        args, use = const.HALF_PI, False
        scipy_solver_init_value = np.array([1 / 1000.0])
        solution, _, ier, _ = scipy.optimize.fsolve(self.potential_fn, scipy_solver_init_value,
                                                    full_output=True, args=args)
        # check if star is closed
        if ier == 1 and not np.isnan(solution[0]):
            solution = solution[0]
            if solution <= 0:
                print(solution)
                raise ValueError('value of single star equatorial radius {} is not valid'.format(solution))
        else:
            raise ValueError('surface of the star is not closed, '
                             'check values of polar gravity and rotation period')

        return solution

    def init_radii(self):
        """
        auxiliary function for calculation of important radii
        :return:
        """
        self._logger.debug('calculating polar radius')
        self.star._polar_radius = self.calculate_polar_radius()
        self._logger.debug('calculating surface potential')
        args = 0,
        self.star._surface_potential = self.surface_potential(self.star.polar_radius, args)[0]
        self._logger.debug('calculating equatorial radius')
        self.star._equatorial_radius = self.calculate_equatorial_radius()

    def potential_fn(self, radius, *args):
        """
        implicit potential function

        :param radius: (np.)float; spherical variable
        :param args: ((np.)float, (np.)float, (np.)float); (component distance, azimutal angle, polar angle)
        :return:
        """
        return self.surface_potential(radius, *args) - self.star.surface_potential

    def surface_potential(self, radius, *args):
        """
        function calculates potential on the given point of the star

        :param radius: (np.)float; spherical variable
        :param args: ((np.)float, (np.)float, (np.)float); (component distance, azimutal angle, polar angle)
        :return: (np.)float
        """
        theta, = args  # latitude angle (0,180)
        return \
            - const.G * self.star.mass / radius - 0.5 * np.power(self._angular_velocity * radius * np.sin(theta), 2.0)

    def build_mesh(self, return_mesh=False):
        """
        build points of surface for including spots
        """
        return build.build_mesh(self, return_mesh)

    def build_surface(self, return_surface=False):
        """
        function for building of general binary star component surfaces including spots

        :param self:
        :param return_surface: bool - if true, function returns dictionary of arrays with all points and faces
                                      (surface + spots) for each component
        :return:
        """
        return build.build_surface(self, return_surface)

    def mesh(self, symmetry_output=False):
        """
        function for creating surface mesh of single star system

        :return: numpy.array([[x1 y1 z1],
                              [x2 y2 z2],
                                ...
                              [xN yN zN]]) - array of surface points if symmetry_output = False, else:
                 numpy.array([[x1 y1 z1],
                              [x2 y2 z2],
                                ...
                              [xN yN zN]]) - array of surface points,
                 numpy.array([indices_of_symmetrical_points]) - array which remapped surface points to symmetrical one
                                                                eighth of surface,
                 numpy.float - number of points included in symmetrical one eighth of surface,
                 numpy.array([octants[indexes_of_remapped_points_in_octants]) - matrix of eight sub matrices that mapped
                                                                                basic symmetry quadrant to all others
                                                                                octants

        """
        if self.star.discretization_factor > const.HALF_PI:
            raise ValueError("invalid value of alpha parameter, use value less than 90")

        alpha = self.star.discretization_factor
        N = int(const.HALF_PI // alpha)
        characterictic_angle = const.HALF_PI / N
        characterictic_distance = self.star.equatorial_radius * characterictic_angle

        # calculating equatorial part
        r_eq = np.array([self.star.equatorial_radius for ii in range(N)])
        phi_eq = np.array([characterictic_angle * ii for ii in range(N)])
        theta_eq = np.array([const.HALF_PI for ii in range(N)])
        # converting quarter of equator to cartesian
        equator = utils.spherical_to_cartesian(np.column_stack((r_eq, phi_eq, theta_eq)))
        x_eq, y_eq, z_eq = equator[:, 0], equator[:, 1], equator[:, 2]

        # calculating radii for each latitude and generating one eighth of surface of the star without poles and equator
        num = int((const.HALF_PI - 2 * characterictic_angle) // characterictic_angle)
        thetas = np.linspace(characterictic_angle, const.HALF_PI - characterictic_angle, num=num, endpoint=True)
        r_q, phi_q, theta_q = [], [], []
        # also generating meridian line
        r_mer, phi_mer, theta_mer = [], [], []
        for theta in thetas:
            args, use = theta, False
            scipy_solver_init_value = np.array([1 / 1000.0])
            solution, _, ier, _ = scipy.optimize.fsolve(self.potential_fn, scipy_solver_init_value,
                                                        full_output=True, args=args)
            radius = solution[0]
            num = int(const.HALF_PI * radius * np.sin(theta) // characterictic_distance)
            r_q += [radius for xx in range(1, num)]
            M = const.HALF_PI / num
            phi_q += [xx * M for xx in range(1, num)]
            theta_q += [theta for xx in range(1, num)]

            r_mer.append(radius)
            phi_mer.append(0)
            theta_mer.append(theta)

        r_q = np.array(r_q)
        phi_q = np.array(phi_q)
        theta_q = np.array(theta_q)
        r_mer = np.array(r_mer)
        phi_mer = np.array(phi_mer)
        theta_mer = np.array(theta_mer)

        # converting this eighth of surface to cartesian coordinates
        quarter = utils.spherical_to_cartesian(np.column_stack((r_q, phi_q, theta_q)))
        meridian = utils.spherical_to_cartesian(np.column_stack((r_mer, phi_mer, theta_mer)))
        x_q, y_q, z_q = quarter[:, 0], quarter[:, 1], quarter[:, 2]
        x_mer, y_mer, z_mer = meridian[:, 0], meridian[:, 1], meridian[:, 2]

        # stitching together equator and 8 sectors of stellar surface
        # in order: north hemisphere: north pole, x_meridian, xy_equator, xy_quarter, y_meridian, y-x_equator,
        #                             y-x_quarter, -x_meridian, -x-y_equator, -x-y_quarter, -y_meridian, -yx_equator,
        #                             -yx_quarter
        #           south hemisphere: south_pole, x_meridian, xy_quarter, y_meridian, y-x_quarter, -x_meridian,
        #                             -x-y_quarter, -y_meridian, -yx_quarter

        x = np.concatenate((np.array([0]), x_mer, x_eq, x_q, -y_mer, -y_eq, -y_q, -x_mer, -x_eq, -x_q, y_mer, y_eq,
                            y_q, np.array([0]), x_mer, x_q, -y_mer, -y_q, -x_mer, -x_q, y_mer, y_q))
        y = np.concatenate((np.array([0]), y_mer, y_eq, y_q, x_mer, x_eq, x_q, -y_mer, -y_eq, -y_q, -x_mer, -x_eq,
                            -x_q, np.array([0]), y_mer, y_q, x_mer, x_q, -y_mer, -y_q, -x_mer, -x_q))
        z = np.concatenate((np.array([self.star.polar_radius]), z_mer, z_eq, z_q, z_mer, z_eq, z_q, z_mer, z_eq,
                            z_q, z_mer, z_eq, z_q, np.array([-self.star.polar_radius]), -z_mer, -z_q, -z_mer, -z_q,
                            -z_mer, -z_q, -z_mer, -z_q))

        if symmetry_output:
            quarter_equator_length = len(x_eq)
            meridian_length = len(x_mer)
            quarter_length = len(x_q)
            base_symmetry_points_number = \
                1 + meridian_length + quarter_equator_length + quarter_length + meridian_length
            symmetry_vector = np.concatenate((np.arange(base_symmetry_points_number),  # 1st quadrant
                                              # stray point on equator
                                              [base_symmetry_points_number],
                                              # 2nd quadrant
                                              np.arange(2 + meridian_length, base_symmetry_points_number),
                                              # 3rd quadrant
                                              np.arange(1 + meridian_length, base_symmetry_points_number),
                                              # 4rd quadrant
                                              np.arange(1 + meridian_length, base_symmetry_points_number -
                                                        meridian_length),
                                              # south hemisphere
                                              np.arange(1 + meridian_length),
                                              np.arange(1 + meridian_length + quarter_equator_length,
                                                        base_symmetry_points_number),  # 1st quadrant
                                              np.arange(1 + meridian_length + quarter_equator_length,
                                                        base_symmetry_points_number),  # 2nd quadrant
                                              np.arange(1 + meridian_length + quarter_equator_length,
                                                        base_symmetry_points_number),  # 3nd quadrant
                                              np.arange(1 + meridian_length + quarter_equator_length,
                                                        base_symmetry_points_number - meridian_length)))

            south_pole_index = 4 * (base_symmetry_points_number - meridian_length) - 3
            reduced_bspn = base_symmetry_points_number - meridian_length  # auxiliary variable1
            reduced_bspn2 = base_symmetry_points_number - quarter_equator_length
            inverse_symmetry_matrix = \
                np.array([
                    np.arange(base_symmetry_points_number + 1),  # 1st quadrant (north hem)
                    # 2nd quadrant (north hem)
                    np.concatenate(([0], np.arange(reduced_bspn, 2 * base_symmetry_points_number - meridian_length))),
                    # 3rd quadrant (north hem)
                    np.concatenate(([0], np.arange(2 * reduced_bspn - 1, 3 * reduced_bspn + meridian_length - 1))),
                    # 4th quadrant (north hem)
                    np.concatenate(([0], np.arange(3 * reduced_bspn - 2, 4 * reduced_bspn - 3),
                                    np.arange(1, meridian_length + 2))),
                    # 1st quadrant (south hemisphere)
                    np.concatenate((np.arange(south_pole_index, meridian_length + 1 + south_pole_index),
                                    np.arange(1 + meridian_length, 1 + meridian_length + quarter_equator_length),
                                    np.arange(meridian_length + 1 + south_pole_index,
                                              base_symmetry_points_number - quarter_equator_length + south_pole_index),
                                    [base_symmetry_points_number])),
                    # 2nd quadrant (south hem)
                    np.concatenate(([south_pole_index],
                                    np.arange(reduced_bspn2 - meridian_length + south_pole_index,
                                              reduced_bspn2 + south_pole_index),
                                    np.arange(base_symmetry_points_number,
                                              base_symmetry_points_number + quarter_equator_length),
                                    np.arange(reduced_bspn2 + south_pole_index,
                                              2 * reduced_bspn2 - meridian_length - 1 +
                                              south_pole_index),
                                    [2 * base_symmetry_points_number - meridian_length - 1])),
                    # 3rd quadrant (south hem)
                    np.concatenate(([south_pole_index],
                                    np.arange(2 * reduced_bspn2 - 2 * meridian_length - 1 + south_pole_index,
                                              2 * reduced_bspn2 - meridian_length - 1 + south_pole_index),
                                    np.arange(2 * base_symmetry_points_number - meridian_length - 1,
                                              2 * base_symmetry_points_number - meridian_length + quarter_equator_length
                                              - 1),
                                    np.arange(2 * reduced_bspn2 - meridian_length - 1 + south_pole_index,
                                              3 * reduced_bspn2 - 2 * meridian_length - 2 + south_pole_index),
                                    [3 * reduced_bspn + meridian_length - 2])),
                    # 4th quadrant (south hem)
                    np.concatenate(([south_pole_index],
                                    np.arange(3 * reduced_bspn2 - 3 * meridian_length - 2 + south_pole_index,
                                              3 * reduced_bspn2 - 2 * meridian_length - 2 + south_pole_index),
                                    np.arange(3 * reduced_bspn + meridian_length - 2,
                                              3 * reduced_bspn + meridian_length - 2 +
                                              quarter_equator_length),
                                    np.arange(3 * reduced_bspn2 - 2 * meridian_length - 2 + south_pole_index, len(x)),
                                    np.arange(1 + south_pole_index, meridian_length + south_pole_index + 1),
                                    [1 + meridian_length]
                                    ))
                ])

            return np.column_stack((x, y, z)), symmetry_vector, base_symmetry_points_number + 1, inverse_symmetry_matrix
        else:
            return np.column_stack((x, y, z))

    def evaluate_spots_mesh(self):
        """
        compute points of each spots and assigns values to spot container instance

        :return:
        """

        def solver_condition(x, *_args, **_kwargs):
            return True

        if not self.star.spots:
            self._logger.info("no spots to evaluate.")
            return

        # iterate over spots
        for spot_index, spot_instance in list(self.star.spots.items()):
            self._logger.info("evaluating spots.")
            # lon -> phi, lat -> theta
            lon, lat = spot_instance.longitude, spot_instance.latitude
            self.star.setup_spot_instance_discretization_factor(spot_instance, spot_index)

            alpha, diameter = spot_instance.discretization_factor, spot_instance.angular_diameter

            # initial containers for current spot
            boundary_points, spot_points = [], []

            # initial radial vector
            radial_vector = np.array([1.0, lon, lat])  # unit radial vector to the center of current spot
            center_vector = utils.spherical_to_cartesian([1.0, lon, lat])

            args, use = (radial_vector[2],), False

            solution, use = self.solver(self.potential_fn, solver_condition, *args)

            if not use:
                # in case of spots, each point should be usefull, otherwise remove spot from
                # component spot list and skip current spot computation
                self._logger.info("center of spot {} doesn't satisfy reasonable "
                                  "conditions and entire spot will be omitted"
                                  "".format(spot_instance.kwargs_serializer()))

                self.star.remove_spot(spot_index=spot_index)
                continue

            spot_center_r = solution
            spot_center = utils.spherical_to_cartesian([spot_center_r, lon, lat])

            # compute euclidean distance of two points on spot (x0)
            # we have to obtain distance between center and 1st point in 1st ring of spot
            args, use = (lat + alpha,), False
            solution, use = self.solver(self.potential_fn, solver_condition, *args)
            if not use:
                # in case of spots, each point should be usefull, otherwise remove spot from
                # component spot list and skip current spot computation
                self._logger.info("first ring of spot {} doesn't satisfy reasonable conditions and "
                                  "entire spot will be omitted".format(spot_instance.kwargs_serializer()))

                self.star.remove_spot(spot_index=spot_index)
                continue

            x0 = np.sqrt(spot_center_r ** 2 + solution ** 2 - (2.0 * spot_center_r * solution * np.cos(alpha)))

            # number of points in latitudal direction
            num_radial = int(np.round((diameter * 0.5) / alpha)) + 1
            thetas = np.linspace(lat, lat + (diameter * 0.5), num=num_radial, endpoint=True)

            num_azimuthal = [1 if i == 0 else int(i * 2.0 * np.pi * x0 // x0) for i in range(0, len(thetas))]
            deltas = [np.linspace(0., const.FULL_ARC, num=num, endpoint=False) for num in num_azimuthal]

            # todo: add condition to die
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

                        args = (spherical_delta_vector[2],)
                        solution, use = self.solver(self.potential_fn, solver_condition, *args)

                        if not use:
                            self.star.remove_spot(spot_index=spot_index)
                            raise StopIteration

                        spot_point = utils.spherical_to_cartesian([solution, spherical_delta_vector[1],
                                                                   spherical_delta_vector[2]])
                        spot_points.append(spot_point)

                        if theta_index == len(thetas) - 1:
                            boundary_points.append(spot_point)

            except StopIteration:
                self._logger.info("at least 1 point of spot {} doesn't satisfy reasonable "
                                  "conditions and entire spot will be omitted"
                                  "".format(spot_instance.kwargs_serializer()))
                return
            # todo: make sure this value is correct = make an unittests for spots
            spot_instance.points = np.array(spot_points)
            spot_instance.boundary = np.array(boundary_points)
            spot_instance.boundary_center = spot_points[0]
            spot_instance.center = np.array(spot_center)

    def build_surface_with_no_spots(self):
        return build.build_surface_with_no_spots(self)

    def build_surface_with_spots(self):
        return build.build_surface_with_spots(self)

    def single_surface(self, points=None):
        """
        calculates triangulation of given set of points, if points are not given, star surface points are used. Returns
        set of triple indices of surface pints that make up given triangle

        :param points: np.array: numpy.array([[x1 y1 z1],
                                                [x2 y2 z2],
                                                  ...
                                                [xN yN zN]])
        :return: np.array(): numpy.array([[point_index1 point_index2 point_index3],
                                          [...],
                                            ...
                                          [...]])
        """
        if points is None:
            points = self.star.points
        triangulation = Delaunay(points)
        triangles_indices = triangulation.convex_hull
        return triangles_indices

    def calculate_equipotential_boundary(self):
        """
        calculates a equipotential boundary of star in zx(yz) plane

        :return: tuple (np.array, np.array)
        """
        points = []
        angles = np.linspace(0, const.FULL_ARC, 300, endpoint=True)
        for angle in angles:
            args, use = angle, False
            scipy_solver_init_value = np.array([1 / 1000.0])
            solution, _, ier, _ = scipy.optimize.fsolve(self.potential_fn, scipy_solver_init_value,
                                                        full_output=True, args=args)
            if ier == 1 and not np.isnan(solution[0]):
                solution = solution[0]
                if 30 >= solution >= 0:
                    use = True
            else:
                continue

            points.append([solution * np.sin(angle), solution * np.cos(angle)])
        return np.array(points)

    def build_color_map(self):
        return build.build_color_map(self)
