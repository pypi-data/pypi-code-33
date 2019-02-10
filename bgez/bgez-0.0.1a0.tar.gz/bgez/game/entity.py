from typing import Optional, List

from .process import logic_process as _logic_process
from .types import blend_library as _blend_library
from .types import game_object as _game_object
from .types import scene as _scene

from bgez.core.resource import Resource

__all__ = [
    'Entity',
]

class Entity(_logic_process.LogicProcess):

    dependencies: List[Resource] = []
    library: Optional[_blend_library.BlendLibrary] = None

    @classmethod
    def ready(cls):
        return all(resource.loaded for resource in cls.dependencies)

    @classmethod
    async def spawn(cls, *, scene: _scene.Scene = None) -> _game_object.GameObject:
        from bgez.game import scenes
        if scene is None:
            scene = scenes.current
        for resource in cls.dependencies:
            if not resource.loaded:
                await resource.load()
        return None

    def __init__(self, object: _game_object.GameObject):
        self.object = object
