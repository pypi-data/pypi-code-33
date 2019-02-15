'''Concrete base classes for transactions.'''
# pylint: disable=too-few-public-methods,invalid-name
from multidict import (MultiDict)
import ntier as N

InputData = MultiDict
TransactionData = N.TransactionData[InputData]

class APITransactionBase(N.APITransactionBase[InputData]):
  pass
