def modes(data, count=6):
  'Return the count most common values found in list data.'

  _ = sorted(set(data), key=data.count, reverse=True)
  return _[:min(len(_), count)]

def mode(data):
  return modes(data, count=1)[0]
