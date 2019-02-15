'''Contains the TransactionResult data structure.'''
from typing import (Any, Optional)
from ntier.messages import (Messages)
from ntier.paging import (Paging)
from ntier.policy_result import (PolicyResult)
from ntier.transaction_code import (TransactionCode)
from ntier.validation_result import (ValidationResult)

class TransactionResult:
  '''Represents a standard transaction result.'''
  def __init__(self, is_valid: bool, status_code: TransactionCode, payload: Any) -> None:
    self.is_valid: bool = is_valid
    self.status_code: TransactionCode = status_code
    self.payload: Any = payload
    self._paging: Optional[Paging] = None

  def __repr__(self):
    return '{}(is_valid={}, status_code={}, payload={}, paging={})'.format(
        self.__class__.__name__,
        self.is_valid,
        self.status_code,
        self.payload,
        self._paging,
    )

  @property
  def paging(self) -> Paging:
    if self._paging is None:
      raise Exception('Paging is not set.')
    return self._paging

  @property
  def has_paging(self) -> bool:
    return self._paging is not None

  def set_paging(self, page: int, per_page: int, total_records: int) -> 'TransactionResult':
    self._paging = Paging.build(page, per_page, total_records)
    return self

  @classmethod
  def success(cls, payload: Any = None) -> 'TransactionResult':
    return cls(True, TransactionCode.success, payload)

  @classmethod
  def found(cls, payload: Any = None) -> 'TransactionResult':
    return cls(True, TransactionCode.found, payload)

  @classmethod
  def created(cls, payload: Any = None) -> 'TransactionResult':
    return cls(True, TransactionCode.created, payload)

  @classmethod
  def updated(cls, payload: Any = None) -> 'TransactionResult':
    return cls(True, TransactionCode.updated, payload)

  @classmethod
  def not_changed(cls, payload: Any = None) -> 'TransactionResult':
    return cls(True, TransactionCode.not_changed, payload)

  @classmethod
  def deleted(cls, payload: Any = None) -> 'TransactionResult':
    return cls(True, TransactionCode.deleted, payload)

  @classmethod
  def failed(cls, payload: Any = None) -> 'TransactionResult':
    return cls(False, TransactionCode.failed, payload)

  @classmethod
  def not_found(cls, subject: str) -> 'TransactionResult':
    msg = Messages().add_general_message(f'{subject} not found')
    return cls(False, TransactionCode.not_found, msg.messages)

  @classmethod
  def not_authenticated(cls) -> 'TransactionResult':
    return cls(False, TransactionCode.not_authenticated, None)

  @classmethod
  def not_authorized(cls, policy_result: PolicyResult) -> 'TransactionResult':
    return cls(False, TransactionCode.not_authorized, policy_result.messages)

  @classmethod
  def not_valid(cls, validation_result: ValidationResult) -> 'TransactionResult':
    return cls(False, TransactionCode.not_valid, validation_result.messages)
