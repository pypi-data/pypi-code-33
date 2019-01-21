# ------- #
# Imports #
# ------- #

from ordered_set import OrderedSet
from .fns import forEach, raise_


# ---- #
# Main #
# ---- #


class ApSet:
    def __init__(self, aList=[]):
        validateInput(aList)

        #
        # _orderedElements holds a set of tuples
        #   (hashable: boolean, idOrElement) where idOrElement is the id of the
        #   element when hashable is false.  Likewise when hashable is true,
        #   idOrElement is the actual element.
        #
        self._orderedElements = OrderedSet()

        self._hashableElements = set()

        #
        # because this holds non-hashable elements, it needs to be a dict of
        #   id(element) -> element
        #
        self._nonHashableElements = {}
        forEach(self._addElement)(aList)

    def _addElement(self, element):
        try:
            self._hashableElements.add(element)
            self._orderedElements.add((True, element))
        except:
            self._nonHashableElements[id(element)] = element
            self._orderedElements.add((False, id(element)))

        return self

    def __contains__(self, element):
        return self.has(element)

    def __iter__(self):
        return ApSetIterator(self)

    def __len__(self):
        return len(self._orderedElements)

    def add(self, element):
        return self._addElement(element)

    def clear(self):
        self._hashableElements.clear()
        self._nonHashableElements.clear()
        self._orderedElements.clear()
        return self

    def has(self, element):
        try:
            return element in self._hashableElements
        except:
            return id(element) in self._nonHashableElements

    def remove(self, element):
        elementRemoved = False
        try:
            if element in self._hashableElements:
                elementRemoved = True
                self._orderedElements.discard((True, element))
                self._hashableElements.remove(element)
        except:
            if id(element) in self._nonHashableElements:
                elementRemoved = True
                self._orderedElements.discard((False, id(element)))
                del self._nonHashableElements[id(element)]

        if not elementRemoved:
            raise KeyError(
                f"the element '{str(element)}' does not exist in ApSet"
            )

        return self


class ApSetIterator:
    def __init__(self, apSetInst):
        self._inst = apSetInst
        self._orderedElementsIterator = iter(apSetInst._orderedElements)

    def __next__(self):
        hashable, elementOrId = next(self._orderedElementsIterator)

        if hashable:
            return elementOrId
        else:
            return self._inst._nonHashableElements[elementOrId]


# ------- #
# Helpers #
# ------- #


def validateInput(aList):
    if not isinstance(aList, list):
        raise_(
            ValueError,
            f"""
            aList is not an instance of list
            type given: {type(aList)}
            """,
        )
