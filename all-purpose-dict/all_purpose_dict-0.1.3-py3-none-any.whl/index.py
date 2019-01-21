# ------- #
# Imports #
# ------- #

from ordered_set import OrderedSet
from .fns import discardWhen, isLaden, raise_
from . import iterators


# ---- #
# Main #
# ---- #


class ApDict:
    def __init__(self, listOfPairs=[]):
        validateListOfPairs(listOfPairs)

        #
        # _orderedKeys holds a set of tuples (hashable: boolean, key)
        #   where key is the id of the key when hashable is false
        #
        self._orderedKeys = OrderedSet()

        self._hashableData = {}
        self._nonHashableData = {}
        self._populateData(listOfPairs)

    def _populateData(self, listOfPairs):
        for key, value in listOfPairs:
            self._set(key, value)

    def _set(self, key, value):
        try:
            self._hashableData[key] = value
            self._orderedKeys.add((True, key))
        except:
            self._nonHashableData[id(key)] = (key, value)
            self._orderedKeys.add((False, id(key)))

        return self

    def __contains__(self, key):
        return self.has(key)

    def __delitem__(self, key):
        return self.delete(key)

    def __getitem__(self, key):
        return self.get(key)

    def __iter__(self):
        return iterators.ApDictIterator(self)

    def __len__(self):
        return len(self._orderedKeys)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def clear(self):
        self._hashableData.clear()
        self._nonHashableData.clear()
        self._orderedKeys.clear()
        return self

    def delete(self, key):
        keyRemoved = False
        try:
            if key in self._hashableData:
                keyRemoved = True
                self._orderedKeys.discard((True, key))
                del self._hashableData[key]
        except:
            if id(key) in self._nonHashableData:
                keyRemoved = True
                self._orderedKeys.discard((False, id(key)))
                del self._nonHashableData[id(key)]

        if not keyRemoved:
            raise KeyError(f"the key '{str(key)}' does not exist in ApDict")

        return self

    def get(self, key):
        try:
            if key in self._hashableData:
                return self._hashableData[key]
        except:
            if id(key) in self._nonHashableData:
                return self._nonHashableData[id(key)][1]

        raise KeyError(f"the key '{str(key)}' does not exist in ApDict")

    def has(self, key):
        try:
            return key in self._hashableData
        except:
            return id(key) in self._nonHashableData

    def keysIterator(self):
        return iterators.ApDictKeysIterator(self)

    def set(self, key, value):
        return self._set(key, value)

    def valuesIterator(self):
        return iterators.ApDictValuesIterator(self)


# ------- #
# Helpers #
# ------- #


def validateListOfPairs(listOfPairs):
    if not isinstance(listOfPairs, list):
        raise_(
            ValueError,
            f"""
            listOfpairs is not an instance of list
            type given: {type(listOfPairs)}
            """,
        )

    invalidElements = discardWhen(isListOrTupleOfLen2)(listOfPairs)
    if isLaden(invalidElements):
        n = len(invalidElements)
        if n == 1:
            singleOrPlural = "element which isn't"
        else:
            singleOrPlural = "elements which aren't"
        raise_(
            ValueError,
            f"""
            listOfPairs has {n} {singleOrPlural} a list or tuple of length 2

            first invalid element: {str(invalidElements[0])}
            """,
        )


def isListOrTupleOfLen2(something):
    return (
        isinstance(something, list) or isinstance(something, tuple)
    ) and len(something) == 2
