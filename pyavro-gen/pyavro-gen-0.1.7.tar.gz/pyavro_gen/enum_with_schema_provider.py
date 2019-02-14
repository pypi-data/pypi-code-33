"""
A provider for enums with schemas
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from enum import Enum
from typing import TypeVar, Type, List, Iterable, cast

from faker.providers import BaseProvider

TEnum = TypeVar("TEnum", bound=Enum)


class EnumWithSchemaProvider(BaseProvider):  # type: ignore
    """
    A Provider for enums with schemas.
    """

    def enum_with_schema(self, enum_cls: Type[TEnum]) -> TEnum:
        """
        Return a random element of this enum

        :param enum_cls: Enum class
        """
        members: List[TEnum] = list(m for m in cast(Iterable[TEnum], enum_cls)
                                    if not m.name.startswith('_'))
        return cast(TEnum, self.random_element(members))
