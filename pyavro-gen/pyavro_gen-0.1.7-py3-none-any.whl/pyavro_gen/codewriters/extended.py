"""
Extended codewriters.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from typing import Optional

from pyavro_gen.codewriters.core import ClassWriter, Decorator, \
    Extension


class UndictifiableClassWriter(ClassWriter):
    """
    Codewriter to produce classes that can be "undictified".
    https://github.com/Dobiasd/undictify
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.decorators = [
            Decorator('@type_checked_constructor()',
                      ClassWriter('undictify.type_checked_constructor')),
            Decorator('@dataclass', ClassWriter('dataclasses.dataclass'))
        ]


class DataClassWriter(ClassWriter):
    """
    Codewriter to write dataclasses.
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.decorators = [
            Decorator('@dataclass', ClassWriter('dataclasses.dataclass'))
        ]


class RpcWriter(ClassWriter):
    """
    Codewriter to write RPC protocols.
    """

    def __init__(self,
                 fully_qualified_name: str,
                 doc: Optional[str] = None,
                 prefix: Optional[str] = None):
        super().__init__(fully_qualified_name, doc, prefix)

        self.extensions = [
            Extension('abc.ABC')
        ]
