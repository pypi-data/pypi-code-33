import numpy as np

from copy import copy
from scipy.optimize import fsolve
from stasma.binary_system import static


def build_mesh(self, component=None, components_distance=None, return_mesh=False):
    """
    build points of surface for primary or/and secondary component !!! w/o spots yet !!!

    :param return_mesh:
    :param self:
    :param component: str or empty
    :param components_distance: float
    :return:
    """
    if components_distance is None:
        raise ValueError('Argument `component_distance` was not supplied.')
    component = static.component_to_list(component)
    ret_points = dict()

    component_x_center = {'primary': 0.0, 'secondary': components_distance}
    for _component in component:
        component_instance = getattr(self, _component)
        # in case of spoted surface, symmetry is not used
        if self.morphology == 'over-contact':
            _a, _b, _c, _d = self.mesh_over_contact(component=_component, symmetry_output=True)
        else:
            _a, _b, _c, _d = self.mesh_detached(component=_component, components_distance=components_distance,
                                                symmetry_output=True)
        component_instance.points = _a
        component_instance.point_symmetry_vector = _b
        component_instance.base_symmetry_points_number = _c
        component_instance.inverse_point_symmetry_matrix = _d

        component_instance = getattr(self, _component)

        self.evaluate_spots_mesh(components_distance=components_distance, component=_component)
        # if self.morphology not in ['over-contact']:
        #     component_instance.incorporate_spots_mesh(component_com=component_x_center[_component])
        component_instance.incorporate_spots_mesh(component_com=component_x_center[_component])

        if return_mesh:
            ret_points[_component] = component_instance.return_all_points()
    return ret_points if return_mesh else None


def build_surface(self, component=None, components_distance=None, return_surface=False):
    """
    function for building of general binary star component surfaces including spots

    :param self:
    :param return_surface: bool - if true, function returns dictionary of arrays with all points and faces
                                  (surface + spots) for each component
    :param components_distance: distance between components
    :param component: specify component, use `primary` or `secondary`
    :return:
    """

    if not components_distance:
        raise ValueError('components_distance value was not provided')

    component = static.component_to_list(component)
    ret_points, ret_faces = {}, {}

    for _component in component:
        component_instance = getattr(self, _component)

        if not component_instance.spots:
            self.build_surface_with_no_spots(_component, components_distance=components_distance)
            if return_surface:
                ret_points[_component] = copy(component_instance.points)
                ret_faces[_component] = copy(component_instance.faces)
            continue
        else:
            self.build_surface_with_spots(_component, components_distance=components_distance)

        if return_surface:
            ret_points[_component], ret_faces[_component] = component_instance.return_whole_surface()

    return (ret_points, ret_faces) if return_surface else None


def build_surface_with_no_spots(self, component=None, components_distance=None):
    """
    function for building binary star component surfaces without spots

    :param self:
    :param components_distance: float
    :param component:
    :return:
    """

    component = static.component_to_list(component)

    for _component in component:
        component_instance = getattr(self, _component)
        # triangulating only one quarter of the star

        if self.morphology != 'over-contact':
            points_to_triangulate = component_instance.points[:component_instance.base_symmetry_points_number, :]
            triangles = self.detached_system_surface(component=_component, points=points_to_triangulate,
                                                     components_distance=components_distance)
        else:
            neck = np.max(component_instance.points[:, 0]) if component[0] == 'primary' \
                else np.min(component_instance.points[:, 0])
            points_to_triangulate = \
                np.append(component_instance.points[:component_instance.base_symmetry_points_number, :],
                          np.array([[neck, 0, 0]]), axis=0)
            triangles = self.over_contact_system_surface(component=_component, points=points_to_triangulate)
            # filtering out triangles containing last point in `points_to_triangulate`
            triangles = triangles[(triangles < component_instance.base_symmetry_points_number).all(1)]

        # filtering out faces on xy an xz planes
        y0_test = ~np.isclose(points_to_triangulate[triangles][:, :, 1], 0).all(1)
        z0_test = ~np.isclose(points_to_triangulate[triangles][:, :, 2], 0).all(1)
        triangles = triangles[np.logical_and(y0_test, z0_test)]

        component_instance.base_symmetry_faces_number = np.int(np.shape(triangles)[0])
        # lets exploit axial symmetry and fill the rest of the surface of the star
        all_triangles = [inv[triangles] for inv in component_instance.inverse_point_symmetry_matrix]
        component_instance.base_symmetry_faces = triangles
        component_instance.faces = np.concatenate(all_triangles, axis=0)

        base_face_symmetry_vector = np.arange(component_instance.base_symmetry_faces_number)
        component_instance.face_symmetry_vector = np.concatenate([base_face_symmetry_vector for _ in range(4)])


def build_surface_with_spots(self, component=None, components_distance=None):
    """
    function capable of triangulation of spotty stellar surfaces, it merges all surface points, triangulates them
    and then sorts the resulting surface faces under star or spot
    :param self:
    :param components_distance: float
    :param component: str `primary` or `secondary`
    :return:
    """
    component = static.component_to_list(component)
    component_com = {'primary': 0.0, 'secondary': components_distance}
    for _component in component:
        component_instance = getattr(self, _component)
        points, vertices_map = component_instance.return_all_points(return_vertices_map=True)

        surface_fn = self._get_surface_builder_fn()
        faces = surface_fn(component=_component, points=points, components_distance=components_distance)
        model, spot_candidates = component_instance.initialize_model_container(vertices_map)
        model = component_instance.split_spots_and_component_faces(
            points, faces, model, spot_candidates, vertices_map, component_com=component_com[_component]
        )
        component_instance.remove_overlaped_spots_by_vertex_map(vertices_map)
        component_instance.remap_surface_elements(model, points)


def build_color_map(self, component=None, components_distance=None):
    if components_distance is None:
        raise ValueError('component distance value was not supplied')
    component = static.component_to_list(component)

    return_map = dict()
    for _component in component:
        component_instance = getattr(self, _component)

        if component_instance.faces is None:
            raise ValueError("cannot build color map due to missing faces, it seems faces were not evaluated yet")

        return_map[_component] = [component_instance.color] * len(component_instance.faces)
        if component_instance.spots:
            for spot_index, spot in component_instance.spots.items():
                return_map[_component] = np.append(return_map[_component], [spot.color] * len(spot.faces), axis=0)

    return {key: np.array(value) for key, value in return_map.items()}
