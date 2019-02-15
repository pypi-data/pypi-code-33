'''Contains the Paging data structure.'''
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Paging:
  '''Contains paging information.'''
  page: int
  per_page: int
  total_records: int
  total_pages: int

  @classmethod
  def build(cls, page: int, per_page: int, total_records: int) -> 'Paging':
    return cls(page, per_page, total_records, math.ceil(total_records / per_page))
