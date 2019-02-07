from enum import Enum
from typing import Optional

from anji_orm import Model, Field


class BaseEnum(Enum):

    first = 'first'
    second = 'second'
    magic = 'magic'


class BaseModel(Model):

    _table = 'not_base_table'

    test_field_3: Optional[str] = Field(secondary_index=True)
    test_field_1: Optional[str]
    test_field_2: Optional[str]


class BaseModelWithEnum(Model):

    _table = 'non_table'

    enum_field: BaseEnum = BaseEnum.first
    test_field: Optional[str]
