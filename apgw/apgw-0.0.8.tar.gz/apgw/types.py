'''Shared types.'''
from typing import (Any, List, Mapping, Optional, Tuple, Union)

ConnectionArgs = Union[Mapping[str, str], str]

InsertAssignments = Union[
    Mapping[str, Any],
    List[Tuple[str, Any]],
]

LimitOffset = Tuple[Optional[int], Optional[int]]

Record = Mapping[str, Any]

RecordsAndCount = Tuple[List[Record], int]

SQL = Tuple[Optional[str], List[Any]]
