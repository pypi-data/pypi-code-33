from collections import MutableMapping, MutableSequence


class PathAccessorKeyError (KeyError):
    """This path overrides KeyError.__str__ for more precise error messages."""
    def __str__(self):
        return self.args[0]


class PathAccessorBase (object):
    def __init__(self, value, path):
        assert isinstance(path, str), (value, path)
        self._value = value
        self._path = path
        self._mappingaccessor = type(self)

    def __repr__(self):
        return '<{0.__name__} {1._path} {1._value!r}>'.format(type(self), self)

    def __len__(self):
        return len(self._value)

    def __delitem__(self, key):
        del self._value[key]

    def __setitem__(self, key, value):
        self._value[key] = value

    def __getitem__(self, key):
        return self._get(key, PathAccessorKeyError, '{}[{!r}]')

    # A private utility method for subclasses:
    def _get(self, key, exctype, pathfmt):
        v = self._value
        try:
            thing = v[key]
        except (KeyError, IndexError, AttributeError):
            raise exctype('{!r} has no member {!r}'.format(self, key))

        return wrap(
            thing,
            pathfmt.format(self._path, key),
            mappingaccessor=self._mappingaccessor,
        )


class MappingPathAccessor (PathAccessorBase, MutableMapping):
    @classmethod
    def fromMappedAttrs(cls, inst):
        assert isinstance(inst, MappedAttrsPathAccessor), inst
        return cls(inst._value, inst._path)

    def __init__(self, d, path):
        assert isinstance(d, MutableMapping), (d, path)
        PathAccessorBase.__init__(self, d, path)

    def __iter__(self):
        return iter(self._value)


class MappedAttrsPathAccessor (PathAccessorBase):
    def __getattr__(self, key):
        return self._get(key, AttributeError, '{}.{}')

    def __setattr__(self, key, value):
        """
        Caution/Gotcha: if key begins w/ '_' this sets private internal
        member state. Otherwise it sets value state.
        """
        if key.startswith('_'):
            PathAccessorBase.__setattr__(self, key, value)
        else:
            self[key] = value


class SequencePathAccessor (PathAccessorBase, MutableSequence):
    def __init__(self, s, path, mappingaccessor=MappingPathAccessor):
        assert isinstance(s, MutableSequence), (s, path)
        PathAccessorBase.__init__(self, s, path)
        self._mappingaccessor = mappingaccessor

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get(key, IndexError, '{}[{!r}]')
        else:
            raise TypeError(
                'Index {!r} of {!r} not an integer'.format(
                    key,
                    self,
                ),
            )

    def insert(self, key, value):
        self._value.insert(key, value)


def wrap(thing, path, mappingaccessor=MappingPathAccessor):
    if isinstance(thing, basestring):
        # This case avoids the Sequence case below:
        return thing
    elif isinstance(thing, MutableMapping):
        return mappingaccessor(thing, path)
    elif isinstance(thing, MutableSequence):
        return SequencePathAccessor(thing, path, mappingaccessor)
    else:
        return thing
