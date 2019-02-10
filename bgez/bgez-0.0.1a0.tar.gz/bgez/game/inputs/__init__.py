from bgez.core.inputs import Keymap as CoreKeymap, ButtonType, AxisType

from bge.logic import expandPath # pylint: disable=E0401

from .bge_inputs import *
from .bge_registry import *

class Keymap(CoreKeymap):

    def __init__(self, registry = BGE_INPUT_REGISTRY):
        super().__init__(registry)

    def _resolve_path(self, path: str) -> str:
        return expandPath(path)
