'''Contains constraint data structures and types.'''
from typing import (Any, List, Union)
from collections import (OrderedDict)
from dataclasses import dataclass

@dataclass(frozen=True)
class BinaryConstraint:
  column: str
  value: Any
  operator: str = '='

@dataclass(frozen=True)
class TextConstraint:
  sql: str
  params: List[Any]

class DictConstraint(OrderedDict):
  '''An alias for OrderedDict.'''

@dataclass(frozen=True)
class Literal:
  value: str

Constraints = Union[
    BinaryConstraint,
    DictConstraint,
    List[BinaryConstraint],
    TextConstraint,
]
