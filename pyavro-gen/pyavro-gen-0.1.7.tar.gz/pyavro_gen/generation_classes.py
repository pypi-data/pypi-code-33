"""
This module defines the class that specifies the types of generated classes
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from enum import Enum
from typing import Type, Dict, Any

from pyavro_gen.codewriters.core import ClassVarClassWriter, EnumClassWriter
from pyavro_gen.codewriters.extended import UndictifiableClassWriter, RpcWriter


class GenerationClassesType(Enum):
    """
    An enum for types of generation classes
    """
    RECORD_CLASS = 'RECORD_CLASS'
    RPC_CLASS = 'RPC_CLASS'
    CLASS_VARIABLE_CLASS = 'CLASS_VARIABLE_CLASS'
    ENUM_CLASS = 'ENUM_CLASS'


#: Container for types of generation classes. Values should be codewriters.
GENERATION_CLASSES: Dict[GenerationClassesType, Type[Any]] = {
    GenerationClassesType.RECORD_CLASS: UndictifiableClassWriter,
    GenerationClassesType.RPC_CLASS: RpcWriter,
    GenerationClassesType.CLASS_VARIABLE_CLASS: ClassVarClassWriter,
    GenerationClassesType.ENUM_CLASS: EnumClassWriter,
}
