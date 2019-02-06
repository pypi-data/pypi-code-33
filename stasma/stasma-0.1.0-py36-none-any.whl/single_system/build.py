import numpy as np
from copy import copy


def build_mesh(self, return_mesh=False):
    """
    build points of surface for including spots
    """
    _a, _b, _c, _d = self.mesh(symmetry_output=True)

    self.star.points = _a
    self.star.point_symmetry_vector = _b
    self.star.base_symmetry_points_number = _c
    self.star.inverse_point_symmetry_matrix = _d

    self.evaluate_spots_mesh()
    self.star.incorporate_spots_mesh(component_com=0)

    if return_mesh:
        return self.star.return_all_points()


def build_surface_with_no_spots(self):
    """
    function is calling surface building function for single systems without spots and assigns star's surface to
    star object as its property
    :return:
    """
    points_length = np.shape(self.star.points[:self.star.base_symmetry_points_number, :])[0]
    # triangulating only one eighth of the star
    points_to_triangulate = np.append(self.star.points[:self.star.base_symmetry_points_number, :],
                                      [[0, 0, 0]], axis=0)
    triangles = self.single_surface(points=points_to_triangulate)
    # removing faces from triangulation, where origin point is included
    triangles = triangles[~(triangles >= points_length).any(1)]
    triangles = triangles[~((points_to_triangulate[triangles] == 0.).all(1)).any(1)]
    # setting number of base symmetry faces
    self.star.base_symmetry_faces_number = np.int(np.shape(triangles)[0])
    # lets exploit axial symmetry and fill the rest of the surface of the star
    all_triangles = [inv[triangles] for inv in self.star.inverse_point_symmetry_matrix]
    self.star.faces = np.concatenate(all_triangles, axis=0)

    base_face_symmetry_vector = np.arange(self.star.base_symmetry_faces_number)
    self.star.face_symmetry_vector = np.concatenate([base_face_symmetry_vector for _ in range(8)])


def build_surface_with_spots(self):
    """
    function for triangulation of surface with spots

    :type self: object
    :return:
    """
    points, vertices_map = self.star.return_all_points(return_vertices_map=True)
    faces = self.single_surface(points=points)
    model, spot_candidates = self.star.initialize_model_container(vertices_map)
    com = 0

    model = self.star.split_spots_and_component_faces(points, faces, model, spot_candidates, vertices_map, com)
    self.star.remove_overlaped_spots_by_vertex_map(vertices_map)
    self.star.remap_surface_elements(model, points)


def build_surface(self, return_surface=False):
    """
    function for building of general system component points and surfaces including spots

    :param self:
    :param return_surface: bool - if true, function returns arrays with all points and faces (surface + spots)
    :type: str
    :return:
    """

    # build surface if there is no spot specified
    if not self.star.spots:
        self.build_surface_with_no_spots()
        return (self.star.points, self.star.faces) if return_surface else (None, None)

    # saving one eighth of the star without spots to be used as reference for faces unaffected by spots
    # self.star.base_symmetry_points = copy(self.star.points[:self.star.base_symmetry_points_number])
    # self.star.base_symmetry_faces = copy(self.star.faces[:self.star.base_symmetry_faces_number])
    self.build_surface_with_spots()

    if return_surface:
        ret_points = copy(self.star.points)
        ret_faces = copy(self.star.faces)
        for spot_index, spot in self.star.spots.items():
            n_points = np.shape(ret_points)[0]
            ret_faces = np.append(ret_faces, spot.faces + n_points, axis=0)
            ret_points = np.append(ret_points, spot.points, axis=0)
        return ret_points, ret_faces


def build_color_map(self):
    if self.star.faces is None:
        raise ValueError("cannot build color map due to missing faces, it seems faces were not evaluated yet")
    return_map = [self.star.color] * len(self.star.faces)
    if self.star.spots:
        for spot_index, spot in self.star.spots.items():
            return_map = np.append(return_map, [spot.color] * len(spot.faces), axis=0)
    return np.array(return_map)
