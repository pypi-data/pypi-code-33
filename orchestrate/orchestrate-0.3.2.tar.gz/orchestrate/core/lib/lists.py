"""
Common utility functions for working with lists
"""
from orchestrate.core.lib.types import (
  is_mapping,
  is_sequence,
  is_set,
)


def list_get(lis, index):
  """
  Gets the list item at the provided index, or None if that index is invalid
  """
  try:
    return lis[index]
  except IndexError:
    return None


def remove_nones(lis):
  """
  Returns a copy of this object with all `None` values removed.
  """
  if is_mapping(lis):
    return {k: v for k, v in lis.items() if v is not None}
  elif is_set(lis):
    return lis - {None}
  elif is_sequence(lis):
    return [l for l in lis if l is not None]


def coalesce(*args):
  """
  Returns the first non-None value, or None if no such value exists
  """
  return list_get(remove_nones(args), 0)
