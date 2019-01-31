class ListLookup(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indexes = dict()  #
        self._unique_indexes = set()

    def index(self, name, callback, unique=False):
        """
        Create index with given name. Callback must return value for future lookups
        """
        if name in self._indexes:
            raise ValueError("Index %s already exists" % name)
        if name == 'preserve_order':
            raise ValueError("%s cannot be used as index name" % name)

        if unique is True:
            self._indexes[name] = self._unique_index(callback)
            self._unique_indexes.add(name)
            return

        pointers = {}
        for i, it in enumerate(self):
            val = callback(it)
            # store pointers in lists
            pointers.setdefault(val, set())
            pointers[val].add(i)
        self._indexes[name] = pointers

    def _unique_index(self, callback):
        """
        Unique index contains only one pointer per value
        """
        return {
            callback(it): i
            for i, it in enumerate(self)
        }

    def lookup(self, preserve_order=True, **kwargs):
        pointers = None
        for index_name, value in kwargs.items():
            res = self._lookup_index(index_name, value)
            if pointers is None:
                pointers = res
            else:
                pointers &= res

        if preserve_order:
            pointers = sorted(pointers)
        for i in pointers:
            yield self[i]

    def _lookup_index(self, index_name, value):
        try:
            index = self._indexes[index_name]
        except KeyError:
            raise RuntimeError("Index %s does not exist" % index_name)

        try:
            pointers = index[value]
        except KeyError:
            return None

        unique = (index_name in self._unique_indexes)
        if unique:
            return set([pointers])
        return pointers
