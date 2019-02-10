from typing import Union, Tuple, List

from . import game_object as _game_object
from . import wrapper as _wrapper

from bge.types import KX_Camera

from bgez.stubs import mathutils

__all__ = [
    'CameraObject',
]

@_wrapper.register_wrapper(KX_Camera)
class CameraObject(_game_object.GameObject):

    _pyobject: KX_Camera

    @property
    def lens(self) -> float:
        return self._pyobject.lens

    @lens.setter
    def lens(self, value: float):
        self._pyobject.lens = value

    @property
    def lod_distance_factor(self) -> float:
        return self._pyobject.loadDistanceFactor

    @lod_distance_factor.setter
    def lod_distance_factor(self, value: float):
        self._pyobject.loadDistanceFactor = value

    @property
    def fov(self) -> float:
        return self._pyobject.fov

    @fov.setter
    def fov(self, value: float):
        self._pyobject.fov = value

    @property
    def orthographic_scale(self) -> float:
        return self._pyobject.ortho_scale

    @orthographic_scale.setter
    def orthographic_scale(self, value: float):
        self._pyobject.ortho_scale = value

    @property
    def near(self) -> float:
        return self._pyobject.near

    @near.setter
    def near(self, value: float):
        self._pyobject.near = value

    @property
    def far(self) -> float:
        return self._pyobject.far

    @far.setter
    def far(self, value: float):
        self._pyobject.far = value

    @property
    def shift_x(self) -> float:
        return self._pyobject.shift_x

    @shift_x.setter
    def shift_x(self, value: float):
        self._pyobject.shift_x = value

    @property
    def shift_y(self) -> float:
        return self._pyobject.shift_y

    @shift_y.setter
    def shift_y(self, value: float):
        self._pyobject.shift_y = value

    @property
    def perspective(self) -> bool:
        return self._pyobject.perspective

    @perspective.setter
    def perspective(self, value: bool):
        self._pyobject.perspective = value

    @property
    def frustum_culling(self) -> bool:
        return self._pyobject.frustum_culling

    @frustum_culling.setter
    def frustum_culling(self, value: bool):
        self._pyobject.frustum_culling = value

    @property
    def activity_culling(self) -> float:
        return self._pyobject.activityCulling

    @activity_culling.setter
    def activity_culling(self, value: float):
        self._pyobject.activityCulling = value

    @property
    def projection_matrix(self) -> mathutils.Matrix:
        return self._pyobject.projection_matrix

    @projection_matrix.setter
    def projection_matrix(self, value: mathutils.Matrix):
        self._pyobject.projection_matrix = value

    @property
    def modelview_matrix(self) -> mathutils.Matrix:
        return self._pyobject.modelview_matrix

    @property
    def camera_to_world(self) -> mathutils.Matrix:
        return self._pyobject.camera_to_world

    @property
    def world_to_camera(self) -> mathutils.Matrix:
        return self._pyobject.world_to_camera

    @property
    def use_viewport(self) -> bool:
        return self._pyobject.useViewport

    @use_viewport.setter
    def use_viewport(self, value: bool):
        self._pyobject.useViewport = value

    def use(self) -> _game_object.GameObject:
        '''
        Set the current camera as the scene active camera.\n
        Returns the old camera.
        '''
        old_camera, self.scene.camera = self.scene.camera, self
        return old_camera

    def sphere_inside_frustrum(self, centre: mathutils.Vector, radius: float) -> int:
        return self._pyobject.sphereInsideFrustrum(centre, radius)

    def box_inside_frustrum(self, box: List[List]) -> int:
        return self._pyobject.boxInsideFrustrum(box)

    def point_inside_frustrum(self, point: mathutils.Vector) -> int:
        return self._pyobject.pointInsideFrustrum(point)

    def set_on_top(self) -> None:
        '''
        Set this camera's viewport on top of all others.
        '''
        self._pyobject.setOnTop()

    def get_screen_position(self, position: Union[_game_object.GameObject, mathutils.Vector]) -> Tuple[float, float]:
        if isinstance(position, _game_object.GameObject):
            position = position._pyobject
        return self._pyobject.getScreenPosition(position)

    def get_screen_vector(self, x: float, y: float) -> mathutils.Vector:
        return self._pyobject.getScreenVect(x, y)

    def get_screen_ray(self, x: float, y: float, *, distance: float = 0, property: str = '') -> _game_object.GameObject:
        return self._pyobject.getScreenRay(x, y, distance, property)
