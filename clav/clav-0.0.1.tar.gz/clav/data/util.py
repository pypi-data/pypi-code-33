import types
from clav.data.attribute import attr
from collections import MutableMapping, MutableSequence
from distutils.util import strtobool

intrinsic_types = (
  type(None), bool, int, float, complex, str, tuple, list, set, dict,
)

def isexc(o):
  '''
  ``True`` if ``o`` is a tuple as returned by ``sys.exc_info()``, else
  ``False``.
  '''

  return isinstance(o, tuple) and len(o) == 3 and (
    isinstance(o[0], type) and
    isinstance(o[1], o[0]) and
    isinstance(o[2], types.TracebackType)
  )

def asbool(val):
  'Turn something (including strings via ``strtobool``) into a ``bool``.'

  if val == '':
    return False
  return bool(strtobool(val)) if isinstance(val, str) else bool(val)

def remap(src, cls=attr):
  '''
  Recursively convert all MutableMappings found in src to type cls. If
  src is a MutableMapping, then src will also be converted to type cls. This
  is used for mass-converting the mapping type used in a deeply-nested data
  structure, such as converting all dicts to attrs.

  :param [MutableSequence, MutableMapping] src: source collection
  :param type cls: target MutableMapping type
  :returns: a new collection
  :rtype MutableMapping:
  '''
  types = (MutableSequence, MutableMapping)
  if isinstance(src, MutableMapping):
    return cls((
      (k, remap(v, cls)) if isinstance(v, types) else (k, v)
      for (k, v) in src.items()
    ))
  elif isinstance(src, MutableSequence):
    return src.__class__(
      remap(_, cls) if isinstance(_, types) else _
      for _ in src
    )
  else:
    raise ValueError(f'src must be MutableSequence or MutableMapping: {src}')

def merge(a, b):
  'Merge two MutableMappings.'

  if not b:
    return a.copy()
  if not a:
    return b.copy()
  a = a.copy()
  b = b.copy()
  for k, v in a.items():
    if (
      k in b and
      all(isinstance(m, MutableMapping) for m in (v, b[k]))
    ):
      b[k] = merge(v, b[k])
  a.update(b)
  return a
