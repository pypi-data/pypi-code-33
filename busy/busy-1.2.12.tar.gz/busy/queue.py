# General-purpose queue of items
# Method calls on queue use indices that start at 1

from .selector import Selector
from .item import Item
import busy


class Queue:

    itemclass = Item
    default_key = 'default'

    def __init__(self, manager=None):
        self._items = []
        self.manager = manager

    def all(self):
        return self._items

    def count(self):
        return len(self._items)

    # Add new items. Always makes them the right class. Also does inserts.

    def add(self, *items, index=None):
        newitems = [self.itemclass.create(i) for i in items if i]
        index = len(self._items) if index is None else index
        self._items[index:index] = newitems

    # Replace existing items at the indices provided. Also inserts if the
    # indices run out. Does not create items. Would be good to combine this
    # with the add method.

    def replace(self, indices, newvalues):
        while newvalues and indices:
            self._items[indices.pop(0)] = newvalues.pop(0)
        while indices:
            del self._items[indices.pop()]
        self._items.extend(newvalues)

    def get(self, index=1):
        return self._items[index-1] if self._items else None

    def select(self, *criteria):
        selector = Selector(criteria)
        return selector.indices(self._items)

    def _split(self, *criteria):
        return self._split_by_indices(*self.select(*criteria))

    def _split_by_indices(self, *indices):
        inlist = [t for i, t in enumerate(self._items) if i in indices]
        outlist = [t for i, t in enumerate(self._items) if i not in indices]
        return (inlist, outlist)

    def pop(self, *criteria):
        hilist, lolist = self._split(*criteria or [len(self._items)])
        self._items = hilist + lolist

    def drop(self, *criteria):
        lolist, hilist = self._split(*criteria or [1])
        self._items = hilist + lolist

    def delete(self, *criteria):
        killlist, keeplist = self._split(*criteria)
        self._items = keeplist

    def delete_by_indices(self, *indices):
        killlist, keeplist = self._split_by_indices(*indices)
        self._items = keeplist

    def list(self, *criteria):
        return [(i+1, self._items[i]) for i in self.select(*criteria)]

    @property
    def strings(self):
        return [str(i) for i in self._items]

    def manage(self, *criteria):
        itemlist = self.list(*criteria)
        indices = [i[0]-1 for i in itemlist]
        before = ''.join([str(i[1])+'\n' for i in itemlist])
        after = busy.editor(before).split('\n')
        new_items = [self.itemclass(i) for i in after if i]
        self.replace(indices, new_items)

    @classmethod
    def register(self, queueclass, default=False):
        if not hasattr(self, '_classes'):
            self._classes = {}
        self._classes[queueclass.key] = queueclass
        if default:
            self.default_key = queueclass.key

    @classmethod
    def subclass(self, key):
        # if not hasattr(self, '_classes'):
        #     self._classes = {}
        return self._classes.get(key) or self
