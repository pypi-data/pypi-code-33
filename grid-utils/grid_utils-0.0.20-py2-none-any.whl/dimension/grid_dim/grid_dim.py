import six

__all__ = ['GridDim']


class GridDim(object):
    """
    Notice: subclasses should provide attr "name".
    """
    @property
    def ndim(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError

    @property
    def values(self):
        raise NotImplementedError

    @values.setter
    def values(self, new_vals):
        raise NotImplementedError

    def __getitem__(self, key):
        return self.get_index(key)

    def get_index(self, key, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return "<{} {}, size: {}>".format(self.__class__.__name__, self.name, self.size)
