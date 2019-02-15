'''Contains the TransactionCode Enum.'''
from enum import Enum

class TransactionCode(Enum):
  '''This enum represents all the status codes that can be returned in a TransactionResult.'''
  success = 100
  found = 101
  created = 102
  updated = 103
  not_changed = 104
  deleted = 105
  failed = 200
  not_found = 201
  not_authenticated = 202
  not_authorized = 203
  not_valid = 204
