# ------- #
# Imports #
# ------- #

from all_purpose_set import ApSet
from types import SimpleNamespace as o
from .fns import isEmpty, isLaden, raise_


# ---- #
# Init #
# ---- #

nodeAttrs = ["element", "next_", "previous"]


# ---- #
# Main #
# ---- #


class LinkedList:
    def __init__(self, aList=[]):
        validateInput(aList)

        self._setOfNodes = ApSet()

        if isLaden(aList):
            self._populateData(aList)
        else:
            self.firstNode = None
            self.lastNode = None

    def _populateData(self, aList):
        self.firstNode = self.lastNode = tmpNode = node(aList[0])
        self._setOfNodes.add(self.firstNode)

        for element in aList[1:]:
            tmpNode = self.lastNode
            self.lastNode = node(element, previous=tmpNode)
            self._setOfNodes.add(self.lastNode)
            tmpNode.next_ = self.lastNode

    def _addInitialNode(self, element):
        initialNode = node(element)
        self._setOfNodes.add(initialNode)
        self.firstNode = initialNode
        self.lastNode = initialNode
        return self

    def __copy__(self):
        result = LinkedList()
        for el in self:
            result.append(el)

        return result

    def __iter__(self):
        return LinkedListIterator(self.firstNode)

    def __len__(self):
        return len(self._setOfNodes)

    def __reversed__(self):
        return LinkedListReverseIterator(self.lastNode)

    def append(self, element):
        if isEmpty(self._setOfNodes):
            return self._addInitialNode(element)

        newLastNode = node(element, previous=self.lastNode)
        self._setOfNodes.add(newLastNode)
        self.lastNode.next_ = newLastNode
        self.lastNode = newLastNode
        return self

    copy = __copy__

    def appendAll(self, aList):
        validateList(aList)

        for el in aList:
            self.append(el)

        return self

    def findFirstNode(self, element):
        tmpNode = self.firstNode
        while tmpNode:
            if tmpNode.element == element:
                return tmpNode

            tmpNode = tmpNode.next_

        raise_(
            ValueError,
            f"""
            The element passed does not exist in this linked list
            element: {element}
            """,
        )

    def insertAfter(self, aNode, element):
        validateNode(self, aNode)
        tmpNode = node(element, next_=aNode.next_, previous=aNode)
        self._setOfNodes.add(tmpNode)
        if aNode.next_:
            aNode.next_.previous = tmpNode
        else:
            self.lastNode = tmpNode
        aNode.next_ = tmpNode
        return self

    def insertAllAfter(self, aNode, aList):
        validateNode(self, aNode)
        validateList(aList)

        nextNode = aNode.next_
        if nextNode is None:
            return self.appendAll(aList)

        curNode = aNode
        for el in aList:
            nodeToInsert = node(el, previous=curNode)
            self._setOfNodes.add(nodeToInsert)
            curNode.next_ = nodeToInsert
            curNode = nodeToInsert

        curNode.next_ = nextNode
        nextNode.previous = curNode
        return self

    def insertAllBefore(self, aNode, aList):
        validateNode(self, aNode)
        validateList(aList)

        previousNode = aNode.previous
        if previousNode is None:
            return self.prependAll(aList)

        curNode = aNode
        for el in reversed(aList):
            nodeToInsert = node(el, next_=curNode)
            self._setOfNodes.add(nodeToInsert)
            curNode.previous = nodeToInsert
            curNode = nodeToInsert

        curNode.previous = previousNode
        previousNode.next_ = curNode
        return self

    def insertBefore(self, aNode, element):
        validateNode(self, aNode)
        tmpNode = node(element, next_=aNode, previous=aNode.previous)
        self._setOfNodes.add(tmpNode)
        if aNode.previous:
            aNode.previous.next_ = tmpNode
        else:
            self.firstNode = tmpNode
        aNode.previous = tmpNode
        return self

    def prepend(self, element):
        if isEmpty(self._setOfNodes):
            return self._addInitialNode(element)

        newFirstNode = node(element, next_=self.firstNode)
        self._setOfNodes.add(newFirstNode)
        self.firstNode.previous = newFirstNode
        self.firstNode = newFirstNode
        return self

    def prependAll(self, aList):
        validateList(aList)

        for el in reversed(aList):
            self.prepend(el)

        return self

    def removeFirstElement(self, element):
        self.removeNode(self.findFirstNode(element))
        return self

    def removeNode(self, aNode):
        validateNode(self, aNode)
        self._setOfNodes.remove(aNode)
        prev = aNode.previous
        next_ = aNode.next_
        if prev:
            prev.next_ = next_
        if next_:
            next_.previous = prev
        return self


class LinkedListIterator:
    def __init__(self, firstNode):
        self._curNode = firstNode

    def __iter__(self):
        return self

    def __next__(self):
        if self._curNode is None:
            raise StopIteration

        result = self._curNode.element
        self._curNode = self._curNode.next_
        return result


class LinkedListReverseIterator:
    def __init__(self, lastNode):
        self._curNode = lastNode

    def __iter__(self):
        return self

    def __next__(self):
        if self._curNode is None:
            raise StopIteration

        result = self._curNode.element
        self._curNode = self._curNode.previous
        return result


def node(element, *, next_=None, previous=None):
    return o(element=element, next_=next_, previous=previous)


# ------- #
# Helpers #
# ------- #


def validateList(aList):
    if not (isinstance(aList, LinkedList) or isinstance(aList, list)):
        raise_(
            ValueError,
            f"""
            aList must be either a LinkedList or a list
            type given: {type(aList).__name__}
            """,
        )


def validateNode(self, aNode):
    for attr in nodeAttrs:
        validateNodeAttr(attr, aNode)

    if aNode not in self._setOfNodes:
        raise_(
            ValueError,
            """
            The node given is not in this linked list, thus you cannot operate
            on it.
            """,
        )


def validateNodeAttr(attr, aNode):
    if not hasattr(aNode, attr):
        raise_(
            ValueError,
            f"""
            The node given is not valid which means it's been mutated outside
            this class!

            node has no attribute '{attr}'
            """,
        )


def validateInput(aList):
    if not isinstance(aList, list):
        raise_(
            ValueError,
            f"""
            aList is not an instance of list
            type given: {type(aList).__name__}
            """,
        )
