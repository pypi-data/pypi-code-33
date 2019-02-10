from typing import Awaitable

from bgez.core.resource import Resource

from .types import blend_library as _blend_library

from bgez.game import logic

class BlendFile(Resource[_blend_library.BlendLibrary]):

    def __init__(self, path: str):
        super().__init__()
        self.path = path

    def _load(self) -> Awaitable[_blend_library.BlendLibrary]:
        return logic.load(self.path)

    def _unload(self) -> None:
        logic.unload(self.path)
