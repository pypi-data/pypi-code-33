import pickle

def goodhash(*args):
  h = ''
  for t in args:
    if isinstance(t, dict):
      h += 'd<>'
      for k, v in sorted(t.items()):
        h += goodhash(k) + '<>' + goodhash(v) + '<>'
      continue
    if isinstance(t, list):
      h += 'l<>'
      for i in t:
        h += goodhash(i) + '<>'
      continue
    if isinstance(t, set):
      h += str(hash(frozenset(t))) + '<>'
      continue
    h += str(hash(pickle.dumps(t))) + '<>'
  return str(hash(h))

class RamCacheWrapper(object):
  ram_cache = {}

  def __init__(self, fn, name=''):
    self._fn = fn
    self._name = name

  def __call__(self, *args, **kwargs):
      context = {
          'kwargs': kwargs,
          'args': args
      }
      try:
          return self.check_cache(self._fn.__name__ + self._name, context)
      except:
          rval = self._fn(*args, **kwargs)
          self.save_cache(self._fn.__name__ + self._name, context, rval)
          return rval

  def check_cache(self, key, context):
    cacheKey = goodhash(key, context)
    if cacheKey not in self.ram_cache:
      raise Exception('no_cache')

    return self.ram_cache[cacheKey]

  def save_cache(self, key, context, value):
    cacheKey = goodhash(key, context)
    self.ram_cache[cacheKey] = value
