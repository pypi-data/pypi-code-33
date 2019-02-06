import gc

from abc import ABCMeta
from copy import copy

import numpy as np
from astropy import units as u

from stasma import logger
from stasma import units
from stasma.base.spot import Spot


class Body(metaclass=ABCMeta):
    """
    Abstract class that defines bodies that can be modelled by this software
    see https://docs.python.org/3.5/library/abc.html for more informations
    units are imported from astropy.units module
    see documentation http://docs.astropy.org/en/stable/units/
    """

    ID = 1
    IGNORED_KWARGS = ['color']

    def __init__(self, name=None, suppress_logger=False, **kwargs):
        self._logger = logger.getLogger(Body.__name__, suppress=suppress_logger)

        if name is None:
            self._name = str(Body.ID)
            self._logger.debug("name of class instance {} set to {}".format(Body.__name__, self._name))
            Body.ID += 1
        else:
            self._name = str(name)

        self._mass = None
        self._polar_radius = None
        self._discretization_factor = np.radians(3)
        self._points = None
        self._faces = None
        self._spots = None
        self._synchronicity = None

        self._point_symmetry_vector = None
        self.inverse_point_symmetry_matrix = None
        self.base_symmetry_points_number = None
        self._face_symmetry_vector = None
        self.base_symmetry_faces_number = None
        # those are used only if case of spots are used
        self.base_symmetry_points = None
        self.base_symmetry_faces = None

        self._polar_log_g = None

        self.color = [1 - (255 - c) / 255.0 for c in kwargs.pop('color')] if kwargs.get('color') \
            else np.random.random_sample(3)

    @property
    def synchronicity(self):
        """
        returns synchronicity parameter F = omega_rot/omega_orb
        usage: xy.synchronicity

        :return: numpy.float64
        """
        return self._synchronicity

    @synchronicity.setter
    def synchronicity(self, synchronicity):
        """
        object synchronicity (F = omega_rot/omega_orb) setter, expects number input convertible to numpy float64
        usage: xy.synchronicity = new_synchronicity

        :param synchronicity: numpy.float64
        """
        if synchronicity is not None:
            self._synchronicity = np.float64(synchronicity)
        else:
            self._synchronicity = None

    @property
    def name(self):
        """
        name getter
        usage: xy.name

        :return: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        name setter
        usage: xy.name = new_name

        :param name: str
        """
        self._name = str(name)

    @property
    def polar_log_g(self):
        """
        returns logarithm of polar surface gravity in SI

        :return: float
        """
        return self._polar_log_g

    @polar_log_g.setter
    def polar_log_g(self, polar_log_g):
        """
        setter for polar surface gravity, if unit is not specified in astropy.units format, value in m/s^2 is assumed

        :param log_g:
        :return:
        """
        if isinstance(polar_log_g, u.quantity.Quantity):
            self._polar_log_g = np.float64(polar_log_g.to(units.LOG_ACCELERATION_UNIT))
        elif isinstance(polar_log_g, (int, np.int, float, np.float)):
            self._polar_log_g = np.float64(polar_log_g)
        else:
            raise TypeError('input of variable `polar_log_g` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance')
        self._logger.debug("setting property polar_log_g "
                           "of class instance {} to {}".format(Body.__name__, self._polar_log_g))

    @property
    def mass(self):
        """
        mass getter, returns mass of object in default mass unit
        usage: by xy.mass

        :return: np.float64
        """
        return self._mass

    @mass.setter
    def mass(self, mass):
        """
        mass setter
        usage: xy.mass = new_mass
        if mass is int, np.int, float, np.float, program assumes solar mass as it's unit
        if mass astropy.unit.quantity.Quantity instance, program converts it to default units and stores it's value in
        attribute _mass

        :param mass: int, np.int, float, np.float, astropy.unit.quantity.Quantity
        """
        if isinstance(mass, u.quantity.Quantity):
            self._mass = np.float64(mass.to(units.MASS_UNIT))
        elif isinstance(mass, (int, np.int, float, np.float)):
            self._mass = np.float64(mass * u.solMass.to(units.MASS_UNIT))
        else:
            raise TypeError('Your input is not (np.)int or (np.)float nor astropy.unit.quantity.Quantity instance.')

    @property
    def polar_radius(self):
        """
        returns value polar radius of an object in default unit
        usage: xy.polar_radius

        :return: float64
        """
        return self._polar_radius

    @polar_radius.setter
    def polar_radius(self, polar_radius):
        """
        setter for polar radius of body
        expected type is astropy.units.quantity.Quantity, numpy.float or numpy.int othervise TypeError will be raised
        if quantity is not specified, default distance unit is assumed

        :param polar_radius:
        :return:
        """
        if isinstance(polar_radius, u.quantity.Quantity):
            self._polar_radius = np.float64(polar_radius.to(units.DISTANCE_UNIT))
        elif isinstance(polar_radius, (int, np.int, float, np.float)):
            self._polar_radius = np.float64(polar_radius)
        else:
            raise TypeError('Value of variable `polar radius` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')

    @property
    def discretization_factor(self):
        """
        returns mean angular distance between surface points

        :return: float
        """
        return self._discretization_factor

    @discretization_factor.setter
    def discretization_factor(self, discretization_factor):
        """
        setter for discretization factor

        :param :float or int
        :return:
        """
        if isinstance(discretization_factor, u.quantity.Quantity):
            self._discretization_factor = np.float64(discretization_factor.to(units.ARC_UNIT))
        elif isinstance(discretization_factor, (int, np.int, float, np.float)):
            self._discretization_factor = np.radians(np.float64(discretization_factor))
        else:
            raise TypeError('Input of variable `discretization_factor` is not (np.)int or (np.)float '
                            'nor astropy.unit.quantity.Quantity instance.')

    @property
    def points(self):
        """
        points getter
        usage: xy.points
        returns dictionary of points that forms surface of Body

        :return: dict
        """
        return self._points

    @points.setter
    def points(self, points):
        """
        points setter
        usage: xy.points = new_points
        setting numpy array of points that form surface of Body
        input dictionary has to be in shape:
        points = numpy.array([[x1 y1 z1],
                                [x2 y2 z2],
                                ...
                                [xN yN zN]])
        where xi, yi, zi are cartesian coordinates of vertice i

        :param points: numpy.array
        xi, yi, zi: float64
        """
        self._points = np.array(points)

    @property
    def faces(self):
        """
        returns dictionary of triangles that will create surface of body
        triangles are stored as list of indices of points
        usage: xy.faces

        :return: numpy.array
        shape: points = numpy.array([[vertice_index_k, vertice_index_l, vertice_index_m]),
                                  [...]),
                                   ...
                                  [...]])
        """
        return self._faces

    @faces.setter
    def faces(self, faces):
        """
        faces setter
        usage: xy.faces = new_faces
        faces dictionary has to be in shape:
        points = np.array([vertice_index_k, vertice_index_l, vertice_index_m],
                          [...],
                           ...
                          [...]]

        :param faces: numpy.array
        """
        self._faces = faces

    @property
    def face_symmetry_vector(self):
        """
        vector of indices with the same length as body`s faces, n-th value of face_symmetry_matrix indicates position
        of base symmetry face for given n-th point
        :return:
        """
        return self._face_symmetry_vector

    @face_symmetry_vector.setter
    def face_symmetry_vector(self, symmetry_vector):
        """
        setter for vector of indices with the same length as body`s faces, n-th value of face_symmetry_matrix
        indicates position of base symmetry face for given n-th point

        :param symmetry_vector: np.array([index_of_symmetry_face1, ..., index_of_symmetry_faceN])
        :return:
        """
        if np.shape(self.faces)[0] != np.shape(symmetry_vector)[0]:
            raise ValueError('length of symmetry vector {} is not the same as number of surface faces {}'
                             ''.format(np.shape(symmetry_vector)[0], np.shape(self.faces)[0]))
        self._face_symmetry_vector = symmetry_vector

    @property
    def spots(self):
        return self._spots

    @spots.setter
    def spots(self, spots):
        # initialize spots dataframes
        if spots:
            self._spots = {idx: Spot(**spot_meta) for idx, spot_meta in enumerate(spots)}

    def calculate_surface_centres(self, points=None, faces=None):
        """
        returns centers of every surface face

        :return: numpy_array([[center_x1, center_y1, center_z1],
                              [center_x2, center_y2, center_z2],
                               ...
                              [center_xn, center_yn, center_zn]])
        """
        if points is None:
            points = self.points
            faces = self.faces
        return np.average(points[faces], axis=1)

    def calculate_normals(self, points=None, faces=None, centres=None, com=None):
        """
        returns outward facing normal unit vector for each face of stellar surface

        :return: numpy_array([[normal_x1, normal_y1, normal_z1],
                              [normal_x2, normal_y2, normal_z2],
                               ...
                              [normal_xn, normal_yn, normal_zn]])
        """
        normals = np.array([np.cross(points[xx[1]] - points[xx[0]], points[xx[2]]
                                     - points[xx[0]]) for xx in faces])
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        cntr = self.calculate_surface_centres(points, faces) if centres is None else copy(centres)

        corr_centres = cntr - np.array([com, 0, 0])[None, :]

        # making sure that normals are properly oriented near the axial planes
        sgn = np.sign(np.sum(np.multiply(normals, corr_centres), axis=1))

        return normals * sgn[:, None]

    def remove_spot(self, spot_index):
        del (self._spots[spot_index])

    def incorporate_spots_mesh(self, component_com=None):
        if not self.spots:
            self._logger.debug("not spots found, skipping incorporating spots to mesh".format(self.name))
            return
        self._logger.info("incorporating spot points to component {} mesh".format(self.name))

        if component_com is None:
            raise ValueError('object centre of mass was not given')

        vertices_map = [{"enum": -1} for _ in self.points]
        # `all_component_points` do not contain points of any spot
        all_component_points = copy(self.points)
        neck = np.min(all_component_points[:self.base_symmetry_points_number, 0])

        for spot_index, spot in self.spots.items():
            # average spacing in spot points
            vertices_to_remove, vertices_test = [], []
            cos_max_angle_point = np.cos(0.5 * spot.angular_diameter + 0.30 * spot.discretization_factor)
            spot_center = spot.center - np.array([component_com, 0., 0.])

            # removing star points in spot
            # for dist, ix in zip(distances, indices):
            for ix, pt in enumerate(all_component_points):
                surface_point = all_component_points[ix] - np.array([component_com, 0., 0.])
                cos_angle = \
                    np.inner(spot_center, surface_point) / (np.linalg.norm(spot_center) * np.linalg.norm(surface_point))

                if cos_angle < cos_max_angle_point or pt[0] == neck:
                    continue
                vertices_to_remove.append(ix)

            # simplices of target object for testing whether point lying inside or not of spot boundary, removing
            # duplicate points on the spot border
            # kedze vo vertice_map nie su body skvrny tak toto tu je zbytocne viac menej
            vertices_to_remove = list(set(vertices_to_remove))

            # points and vertices_map update
            if vertices_to_remove:
                _points, _vertices_map = list(), list()

                for ix, vertex in list(zip(range(0, len(all_component_points)), all_component_points)):
                    if ix in vertices_to_remove:
                        # skip point if is marked for removal
                        continue

                    # append only points of currrent object that do not intervent to spot
                    # [current, since there should be already spot from previous iteration step]
                    _points.append(vertex)
                    _vertices_map.append({"enum": vertices_map[ix]["enum"]})

                for vertex in spot.points:
                    _points.append(vertex)
                    _vertices_map.append({"enum": spot_index})

                all_component_points = copy(_points)
                vertices_map = copy(_vertices_map)

        separated_points = self.split_points_of_spots_and_component(all_component_points, vertices_map)
        self.setup_body_points(separated_points)

    def split_points_of_spots_and_component(self, points, vertices_map):
        points = np.array(points)
        component_points = {
            "object": points[np.where(np.array(vertices_map) == {'enum': -1})[0]]
        }
        self.remove_overlaped_spots_by_spot_index(
            spot_indices=set([int(val["enum"]) for val in vertices_map if val["enum"] > -1]))
        spots_points = {
            "{}".format(i): points[np.where(np.array(vertices_map) == {'enum': i})[0]]
            for i in range(len(self.spots))
            if len(np.where(np.array(vertices_map) == {'enum': i})[0]) > 0
        }
        return {**component_points, **spots_points}

    def remove_overlaped_spots_by_spot_index(self, spot_indices):
        all_spot_indices = set([int(val) for val in self.spots.keys()])
        spot_indices_to_remove = all_spot_indices.difference(spot_indices)

        for spot_index in spot_indices_to_remove:
            self._logger.debug("spot {} of component {} is overlaped and will be removed"
                               "".format(spot_index, self.name))
            self.remove_spot(spot_index)

    def remove_overlaped_spots_by_vertex_map(self, vertices_map):
        # remove spots that are totaly overlaped
        spots_instance_indices = list(set([vertices_map[ix]["enum"] for ix, _ in enumerate(vertices_map)
                                           if vertices_map[ix]["enum"] >= 0]))
        for spot_index, _ in list(self.spots.items()):
            if spot_index not in spots_instance_indices:
                self._logger.warning("spot with index {} doesn't contain any face "
                                     "and will be removed from component {} spot list"
                                     "".format(spot_index, self.name))
                self.remove_spot(spot_index=spot_index)
        gc.collect()

    def setup_body_points(self, points):
        self.points = points.pop("object")
        for spot_index, spot_points in points.items():
            self.spots[int(spot_index)].points = points[spot_index]

    def remap_surface_elements(self, model, points_to_remap):
        """
        function remaps all surface points (`points_to_remap`) and faces (star and spots) according to the `model`

        :param model: dict - list of indices of points in `points_to_remap` divided into star and spots sublists
        :param self: Star object
        :param points_to_remap: array of all surface points (star + points used in
        `BinarySystem._split_spots_and_component_faces`)
        :return:
        """
        # remapping points and faces of star
        self._logger.debug("changing value of parameter points of component {}"
                           "".format(self.name))
        indices = np.unique(model["object"])
        self.points = points_to_remap[indices]

        self._logger.debug("changing value of parameter faces component {}"
                           "".format(self.name))

        points_length = np.shape(points_to_remap)[0]
        remap_list = np.empty(points_length, dtype=int)
        remap_list[indices] = np.arange(np.shape(indices)[0])
        self.faces = remap_list[model["object"]]

        # remapping points and faces of spots
        for spot_index, _ in list(self.spots.items()):
            self._logger.debug("changing value of parameter points of spot {} / component {}"
                               "".format(spot_index, self.name))
            # get points currently belong to the given spot
            indices = np.unique(model["spots"][spot_index])
            self.spots[spot_index].points = points_to_remap[indices]

            self._logger.debug("changing value of parameter faces of spot {} / component {}"
                               "".format(spot_index, self.name))

            remap_list = np.empty(points_length, dtype=int)
            remap_list[indices] = np.arange(np.shape(indices)[0])
            self.spots[spot_index].faces = remap_list[model["spots"][spot_index]]
        gc.collect()

    def return_all_points(self, return_vertices_map=False):
        """
        function returns all surface point and faces optionally with corresponding map of vertices
        :param return_vertices_map:
        :param self: Star object
        :return: array - all surface points including star and surface points
        """
        points = copy(self.points)
        if self.spots:
            for spot_index, spot_instance in self.spots.items():
                points = np.concatenate([points, spot_instance.points])

        if return_vertices_map:
            vertices_map = [{"type": "object", "enum": -1}] * len(self.points)
            for spot_index, spot_instance in self.spots.items():
                vertices_map = np.concatenate(
                    [vertices_map, [{"type": "spot", "enum": spot_index}] * len(spot_instance.points)]
                )
            return points, vertices_map
        return points

    def return_whole_surface(self):
        """
        returns all points and faces of the whole star
        :return:
        """
        ret_points = copy(self.points)
        ret_faces = copy(self.faces)
        if self.spots:
            for spot_index, spot in self.spots.items():
                n_points = np.shape(ret_points)[0]
                ret_points = np.append(ret_points, spot.points, axis=0)
                ret_faces = np.append(ret_faces, spot.faces + n_points, axis=0)

        return ret_points, ret_faces

    def setup_spot_instance_discretization_factor(self, spot_instance, spot_index):
        # component_instance = getattr(self, component)
        if spot_instance.discretization_factor is None:
            self._logger.debug('angular density of the spot {0} on {2} component was not supplied '
                               'and discretization factor of star {1} was used.'
                               ''.format(spot_index, self.discretization_factor, self.name))
            spot_instance.discretization_factor = 0.9 * self.discretization_factor * units.ARC_UNIT
        if spot_instance.discretization_factor > 0.5 * spot_instance.angular_diameter:
            self._logger.debug('angular density {1} of the spot {0} on {2} component was larger than its '
                               'angular radius. Therefore value of angular density was set to be equal to '
                               '0.5 * angular diameter'
                               ''.format(spot_index, self.discretization_factor, self.name))
            spot_instance.discretization_factor = 0.5 * spot_instance.angular_diameter * units.ARC_UNIT

    @classmethod
    def _resolve_obvious_spots(cls, points, faces, model, spot_candidates, vmap):
        for simplex, face_points, ix in list(zip(faces, points[faces], range(faces.shape[0]))):
            # if each point belongs to the same spot, then it is for sure face of that spot
            condition1 = vmap[simplex[0]]["enum"] == vmap[simplex[1]]["enum"] == vmap[simplex[2]]["enum"]
            if condition1:
                if 'spot' == vmap[simplex[0]]["type"]:
                    model["spots"][vmap[simplex[0]]["enum"]].append(np.array(simplex))
                else:
                    model["object"].append(np.array(simplex))
            else:
                spot_candidates["com"].append(np.average(face_points, axis=0))
                spot_candidates["ix"].append(ix)

        gc.collect()
        return model, spot_candidates

    def split_spots_and_component_faces(self, points, faces, model, spot_candidates, vmap, component_com):
        """
        function that sorts faces to model data structure by distinguishing if it belongs to star or spots

        :param component_com:
        :param points: array (N_points * 3) - all points of surface
        :param faces: array (N_faces * 3) - all faces of the surface
        :param model: dict - data structure for faces sorting
        :param spot_candidates: initialised data structure for spot candidates
        :param vmap: vertice map
        :return:
        """
        model, spot_candidates = \
            self._resolve_obvious_spots(points, faces, model, spot_candidates, vmap)
        model = self._resolve_spot_candidates(model, spot_candidates, faces, component_com)
        # converting lists in model to numpy arrays
        model['object'] = np.array(model['object'])
        for spot_ix in self.spots:
            model['spots'][spot_ix] = np.array(model['spots'][spot_ix])

        return model

    @staticmethod
    def initialize_model_container(vertices_map):
        """
        initializes basic data structure `model` objects that will contain faces divided by its origin (star or spots)
        and data structure containing spot candidates with its index, centre,
        :param vertices_map:
        :return:
        """
        model = {"object": [], "spots": {}}
        spot_candidates = {"simplex": {}, "com": [], "ix": []}
        spots_instance_indices = list(set([vertices_map[ix]["enum"] for ix, _ in enumerate(vertices_map)
                                           if vertices_map[ix]["enum"] >= 0]))
        for spot_index in spots_instance_indices:
            model["spots"][spot_index] = []
        return model, spot_candidates

    def _resolve_spot_candidates(self, model, spot_candidates, faces, component_com):
        """
        resolves spot face candidates by comparing angular distances of face cantres and spot centres, in case of
        multiple layered spots, face is assigned to the top layer

        :param model:
        :param spot_candidates:
        :param faces:
        :param component_com:
        :return:
        """
        # checking each candidate one at a time trough all spots
        com = np.array(spot_candidates["com"]) - np.array([component_com, 0.0, 0.0])
        cos_max_angle = {idx: np.cos(0.5 * spot.angular_diameter) for idx, spot in self.spots.items()}
        center = {idx: spot.center - np.array([component_com, 0.0, 0.0])
                  for idx, spot in self.spots.items()}
        for idx, _ in enumerate(spot_candidates["com"]):
            spot_idx_to_assign = -1
            simplex_ix = spot_candidates["ix"][idx]
            for spot_ix in self.spots:
                cos_angle_com = np.inner(center[spot_ix], com[idx]) / \
                                (np.linalg.norm(center[spot_ix]) * np.linalg.norm(com[idx]))
                if cos_angle_com > cos_max_angle[spot_ix]:
                    spot_idx_to_assign = spot_ix

            if spot_idx_to_assign == -1:
                model["object"].append(np.array(faces[simplex_ix]))
            else:
                model["spots"][spot_idx_to_assign].append(np.array(faces[simplex_ix]))

        gc.collect()
        return model
