from typing import Any, Dict, Awaitable

from bgez.core import CallbackList, undefined
from bgez.asyn import Deferred, sleep

from ..process import logic_process as _logic_process
from . import camera_object as _camera_object
from . import game_object as _game_object
from . import wrapper as _wrapper

from bge.types import KX_Scene

__all__ = [
    'Scene',
]

@_wrapper.register_wrapper(KX_Scene)
class Scene(_wrapper.PyObjectPlus, _logic_process.LogicProcess):
    '''
    This is a wrapper around `KX_Scene` objects.
    Acts as an emitter for most events triggered by a BGE Scene.
    `KX_Scene` objects should be wrapped only once.
    '''

    _pyobject: KX_Scene

    def __init__(self, kx_scene: KX_Scene, master: bool = False):
        super().__init__(kx_scene)
        self.__frame_deferred: Dict[int, Deferred] = {}
        self.__master: bool = master
        self.frame: int = 0
        self.__hook()

    def __check_master(self):
        if self.__master:
            raise RuntimeError(f'cannot end master scene {self.name}')

    def __hook(self):
        kx_scene = self._pyobject

        self.pre_draw_setup = CallbackList()
        self.pre_draw = CallbackList()
        self.post_draw = CallbackList()
        self.removal = CallbackList()

        kx_scene.pre_draw_setup.append(self.pre_draw_setup.__call__)
        kx_scene.pre_draw.append(self.pre_draw.__call__)
        kx_scene.post_draw.append(self.post_draw.__call__)
        kx_scene.onRemove.append(self.removal.__call__)

    def __get_frame_deferred(self, frame: int) -> Deferred:
        if frame not in self.__frame_deferred:
            self.__frame_deferred[frame] = Deferred()
        return self.__frame_deferred[frame]

    def __resolve_frame_deferred(self, frame: int) -> None:
        self.__frame_deferred.pop(frame - 1, None)
        deferred = self.__frame_deferred.get(frame, None)
        if deferred is not None: deferred.resolve(frame)

    def __str__(self):
        return f'{self.__class__.__qualname__}({self.name})'

    def on_pre_logic(self):
        self.frame += 1
        self.__resolve_frame_deferred(self.frame)

    @property
    def name(self) -> str:
        return self._pyobject.name

    @name.setter
    def name(self, value):
        self._pyobject.name = value

    @property
    def objects(self) -> '_wrapper.ListValue[_game_object.GameObject]':
        return _wrapper.wrap(self._pyobject.objects)

    @property
    def inactives(self) -> '_wrapper.ListValue[_game_object.GameObject]':
        return _wrapper.wrap(self._pyobject.objectsInactive)

    @property
    def camera(self) -> '_camera_object.CameraObject':
        return _wrapper.wrap(self._pyobject.active_camera)

    @camera.setter
    def camera(self, camera: '_game_object.GameObject'):
        if isinstance(camera, _game_object.GameObject):
            camera = camera._pyobject
        self._pyobject.active_camera = camera

    @property
    def cameras(self) -> '_wrapper.ListValue[_camera_object.CameraObject]':
        return _wrapper.wrap(self._pyobject.cameras)

    @property
    def lights(self) -> list:
        return _wrapper.wrap(self._pyobject.lights)

    @property
    def texts(self) -> list:
        return _wrapper.wrap(self._pyobject.texts)

    @property
    def world(self):
        return _wrapper.wrap(self._pyobject.world)

    @property
    def filters(self):
        return self._pyobject.filterManager

    def add_object(self, object: '_game_object.GameObject', reference: '_game_object.GameObject' = None, life: float = 0.):
        if isinstance(object, _game_object.GameObject):
            object = object._pyobject
        if isinstance(reference, _game_object.GameObject):
            reference = reference._pyobject
        return _wrapper.wrap(self._pyobject.addObject(object, reference, life))

    def skip(self, offset: int = 1, *, value: Any = undefined) -> Awaitable[int]:
        if offset < 1:
            if value is undefined:
                value = self.frame
            return sleep(0, value)
        frame = self.frame + offset
        promise = self.__get_frame_deferred(frame).promise
        if value is undefined:
            return promise
        return promise.then(lambda _: value)

    def end(self) -> None:
        self.__check_master()
        self._pyobject.end()

    def replace(self, scene: 'Scene') -> None:
        self.__check_master()
        if isinstance(scene, Scene):
            scene = scene._pyobject
        self._pyobject.replace(scene)

    def suspend(self) -> None:
        self._pyobject.suspend()

    def resume(self) -> None:
        self._pyobject.resume()
