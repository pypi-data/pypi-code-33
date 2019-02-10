from typing import Any, Dict, List, cast

from itertools import chain

from bgez.asyn import Deferred, Promise

from ..process import logic_process as _logic_process
from ..types import wrapper as _wrapper
from ..types import scene as _scene

from bge import logic # pylint: disable=E0401

__all__ = [
    'SceneManager',
]

class SceneManager(_logic_process.LogicProcess):
    '''
    Manages Scenes.
    - Keeps a track of all alive scenes and wraps them on the go.
    - Responsible for dispatching the logic ticks to callbacks for that event.
    '''

    def __init__(self):
        self.__waiting: Dict[str, Any] = dict()
        self.__mark_objects()

    def __mark_objects(self):
        scene = self.current
        for object in chain(scene.objects, scene.inactives):
            object.properties.setdefault('__library__', '__main__')

    def __str__(self):
        scenes = [scene.name for scene in self.list]
        return f'{self.__class__.__name__} {scenes}'

    def __getitem__(self, item) -> '_scene.Scene':
        return cast(_scene.Scene, self.list[item])

    def on_pre_logic(self):
        waiting = self.__waiting
        for scene in self.list:
            name = scene.name
            if name in waiting:
                waiting.pop(name).resolve(scene)
        scene.on_pre_logic()

    def __check_inactive(self, name):
        inactives = self.inactives
        if name not in inactives:
            raise KeyError(f'{name} is not in {inactives}')

    def __add_scene(self, name: str, overlay: int) -> Promise:
        self.__check_inactive(name)
        queue = self.__waiting
        if name in queue:
            return queue[name].promise

        deferredScene: Deferred = Deferred()
        queue[name] = deferredScene
        logic.addScene(name, overlay) # actual scene adding
        return deferredScene.promise

    @property
    def current(self) -> '_scene.Scene':
        '''Returns the current scene.'''
        return _wrapper.wrap(logic.getCurrentScene())

    @property
    def list(self) -> '_wrapper.ListValue':
        return _wrapper.wrap(logic.getSceneList())

    @property
    def inactives(self) -> List[str]:
        '''Returns the names of the inactive scenes'''
        return logic.getInactiveSceneList()

    def overlay(self, name: str) -> Promise:
        return self.__add_scene(name, 1)

    def underlay(self, name: str) -> Promise:
        return self.__add_scene(name, 0)
