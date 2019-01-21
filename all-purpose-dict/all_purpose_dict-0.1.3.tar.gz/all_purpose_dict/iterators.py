class ApDictIterator:
    def __init__(self, apDictInst):
        self._inst = apDictInst
        self._orderedKeysIterator = iter(apDictInst._orderedKeys)

    def __iter__(self):
        return self

    def __next__(self):
        hashable, keyOrId = next(self._orderedKeysIterator)

        if hashable:
            key = keyOrId
            value = self._inst._hashableData[keyOrId]
        else:
            key = self._inst._nonHashableData[keyOrId][0]
            value = self._inst._nonHashableData[keyOrId][1]

        return (key, value)


class ApDictKeysIterator:
    def __init__(self, apDictInst):
        self._inst = apDictInst
        self._orderedKeysIterator = iter(apDictInst._orderedKeys)

    def __iter__(self):
        return self

    def __next__(self):
        hashable, keyOrId = next(self._orderedKeysIterator)

        if hashable:
            return keyOrId
        else:
            return self._inst._nonHashableData[keyOrId][0]


class ApDictValuesIterator:
    def __init__(self, apDictInst):
        self._inst = apDictInst
        self._orderedKeysIterator = iter(apDictInst._orderedKeys)

    def __iter__(self):
        return self

    def __next__(self):
        hashable, keyOrId = next(self._orderedKeysIterator)

        if hashable:
            return self._inst._hashableData[keyOrId]
        else:
            return self._inst._nonHashableData[keyOrId][1]
