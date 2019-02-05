
def deep_merge(base,overlay):

    # If we have reached the end of either of the
    # base or the overlay we are done
    if overlay is None: return base
    if base is None: return overlay

    # Ensure the types are the same
    if not isinstance(base,type(overlay)):
        raise Exception('Data structures cannot be combined.')

    if isinstance(base,dict):
        for k,v in overlay.items():
            base[k] = deep_merge(base.get(k),v)
        return base

    if isinstance(base,list):
        # FIXME: how to deal with lists?
        # Do we add the lists together
        return overlay
    else:
        return overlay

class DictObj(object):
    def __init__(self,config,data):
        self._config = config
        self._data = data

    def dict(self):
        return self._data

    def get(self,*args,**kwargs):
        return self._data.get(*args,**kwargs)

    def __getattr__(self,k):
        v = self._data[k]
        if isinstance(v,dict):
            return DictObj(self._config,v)
        return v

    def __getitem__(self,k):
        return self.__getattr__(k)

    def __str__(self):
        return str(self._data)

    def __call__(self):
        return self._data

