'''Contains the TransactionBase class.'''
from typing import (Optional, Tuple)
from ntier.transaction_result import TransactionResult
from ntier.constants import (
    PAGE_DEFAULT,
    PER_PAGE_DEFAULT,
    PER_PAGE_MAX,
)

class TransactionBase:
  '''Base class for transactions.'''
  def __init__(self):
    self.paging: Optional[Tuple[int, int]] = None

  def set_paging(self, page: int, per_page: int) -> 'TransactionBase':
    '''Sets paging values for the transaction.'''
    if page < 1:
      page = 1
    if per_page < 1:
      per_page = 1
    if per_page > PER_PAGE_MAX:
      per_page = PER_PAGE_MAX

    self.paging = (page, per_page)
    return self

  @property
  def offset(self):
    '''Returns the offset based on the paging.'''
    if self.paging is None:
      (page, per_page) = (PAGE_DEFAULT, PER_PAGE_DEFAULT)
    else:
      (page, per_page) = self.paging
    return (page - 1) * per_page

  @property
  def limit(self):
    '''Returns the limit based on the paging.'''
    if self.paging is None:
      return PER_PAGE_DEFAULT
    (_, per_page) = self.paging
    return per_page

  def set_output_paging(self, result: TransactionResult, total_records: int) -> TransactionResult:
    '''Assign paging to a TransactionResult.'''
    if self.paging is None:
      (page, per_page) = (PAGE_DEFAULT, PER_PAGE_DEFAULT)
    else:
      (page, per_page) = self.paging
    result.set_paging(page, per_page, total_records)
    return result
