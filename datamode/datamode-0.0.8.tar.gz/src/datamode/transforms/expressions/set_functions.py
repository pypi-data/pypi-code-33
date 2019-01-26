import pandas as pd

##
## Set functions
##
def _sum(items):
  total = 0
  for item in items:
    if item is not None:
      total += item

  return total

# Todo: should we count only non-nulls?
def count(items):
  return len(items)

def average(items):
  return _sum(items) / count(items)

def first(items):
  if isinstance(items, pd.Series):
    return items.iloc[0]
  else:
    return items[0]


FUNC_NAME_MAP = {
  'sum': _sum,
  'count': count,
  'average': average,
  'first': first,
}

def get_func_by_name(name):
  return FUNC_NAME_MAP[name]
