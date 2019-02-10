from typing import Dict

from . import game_object as _game_object
from . import scene as _scene

from bgez.stubs import bge_types

__all__ = [
    'BlendLibrary',
]

class BlendLibrary:
    '''
    Wraps a LibLoad resolution.\n
    '''

    def __init__(self, scene: _scene.Scene, status: bge_types.LibLoadStatus):
        self.__status = status
        self.scene = scene
        self.inactives: Dict[str, _game_object.GameObject] = {}
        self.active: Dict[str, _game_object.GameObject] = {}

        if status.finished:
            self._on_finish(status)
        else:
            status.onFinish = self._on_finish

    def _on_finish(self, status: bge_types.LibLoadStatus):

        for object in self.scene.objects:
            if (object.library is None) and (object.name not in self.active):
                object.library = status.libraryName
                self.active[object.name] = object

        for object in self.scene.inactives:
            if (object.library is None) and (object.name not in self.inactives):
                object.library = status.libraryName
                self.inactives[object.name] = object

    @property
    def finished(self) -> bool:
        return self.__status.finished

    @property
    def time_taken(self) -> float:
        return self.__status.timeTaken

    @property
    def progress(self) -> float:
        return self.__status.progress

    @property
    def name(self) -> str:
        return self.__status.libraryName
