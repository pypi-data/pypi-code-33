from .rekey import rekey

__all__ = [
  'Rekeyable',
  'RekeyableList',
  'RekeyableDict',
  'RekeyableSet',
  'RekeyableTuple',
]


class Rekeyable():
    def rekey(self, key_handle=None, value_handle=None):
        return rekey(self, key_handle, value_handle)


class RekeyableList(list, Rekeyable): pass
class RekeyableDict(dict, Rekeyable): pass
class RekeyableSet(set, Rekeyable): pass
class RekeyableTuple(tuple, Rekeyable): pass
