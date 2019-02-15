'''Contains the transaction Data class.'''
from dataclasses import (dataclass)
from typing import (Any, Generic, MutableMapping, TypeVar)

TransactionState = MutableMapping[str, Any]
InputData = TypeVar('InputData')

@dataclass(frozen=True)
class TransactionData(Generic[InputData]):
  '''Contains input and state data for an API Transaction.'''
  input: InputData
  state: TransactionState
