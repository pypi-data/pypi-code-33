from typing import List

from . import game_object as _game_object
from . import wrapper as _wrapper

from bge.types import BL_ArmatureObject

__all__ = [
    'Armature',
]

@_wrapper.register_wrapper(BL_ArmatureObject)
class Armature(_game_object.GameObject):

    _pyobject: BL_ArmatureObject

    @property
    def constraints(self) -> List:
        return self._pyobject.constraints

    @property
    def channels(self) -> List:
        return self._pyobject.channels

    def update(self) -> None:
        self._pyobject.update()

    def draw(self) -> None:
        self._pyobject.draw()
