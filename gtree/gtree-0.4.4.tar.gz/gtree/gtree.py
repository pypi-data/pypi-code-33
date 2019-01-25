from collections import defaultdict


class Node:
    def __init__(self, data, parent=None):
        """Creates a new Node instance.
        :param data: the data that the node should consist of, can be any type.
        :param parent: a reference to any existing node, None by default (i.e. the node will be a root node.)
        """
        self._data = data
        self._parent = parent
        self._children = []

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if new_parent is None:
            self._parent.remove(self)
            self._parent = None
            return
        if not isinstance(new_parent, Node):
            raise ValueError("invalid parent type")
        if new_parent == self:
            raise ValueError("invalid parent")
        if new_parent == self.parent:
            return
        if self._parent:
            self._parent.remove(self)

        new_parent.add(self)
        self._parent = new_parent

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        raise Exception("invalid operation")

    def size(self) -> int:
        if not self._children:
            return 1
        else:
            return self.rec_size()

    def rec_size(self) -> int:
        if not self._children:
            return 1
        s = 1
        for child in self._children:
            s += child.rec_size()
        return s

    def add(self, n):
        """Adds the node containing data to this node.
        :param n: the node to add, can be an existing Node or new data.
        :return: the node created.
        """
        if not isinstance(n, Node):
            n = Node(n, self)
        self._children.append(n)
        return n

    def remove(self, n):
        """Tries to remove the given node from this tree.
        :param n: the node to remove.
        """
        if not isinstance(n, Node):
            raise ValueError("illegal type: {} is not of type {}".format(type(n), type(Node)))
        elif self == n:
            raise ValueError("node cannot remove itself")
        self.rec_remove(n)

    def rec_remove(self, n):
        if self._children:
            if n in self._children:
                self._children.remove(n)
            else:
                for child in self._children:
                    child.rec_remove(n)

    def leave(self):
        """Remove itself from the tree it belongs to."""
        if self._parent:
            self._parent.remove(self)
            self._parent = None

    def foreach_breadth_first(self, callback, *argv, **kwargs):
        """Run callback for each node in the tree top to bottom.
        :param callback: the callable to run for each node.
        :param argv: variable length variables to pass on to callback.
        :param kwargs: keyword arguments to pass on to callback.
        """
        for node in self.collect_breadth_first():
            callback(node, *argv, **kwargs)

    def foreach_depth_first(self, callback, *argv, **kwargs):
        """Run callback for each node in the tree bottom up.
        :param callback: the callable to run for each node.
        :param argv: variable length variables to pass on to callback.
        :param kwargs: keyword arguments to pass on to callback.
        """
        for node in self.collect_depth_first():
            callback(node, *argv, **kwargs)

    def collect_breadth_first(self):
        """Returns a list of the nodes traversed each level using breadth first search.
        :return: a list consisting of the nodes in this tree ordered breadth first.
        """
        level_map = self.__collect_levels()
        levels = [level for level in level_map.keys()]
        levels.sort()
        nodes = []
        for level in levels:
            [nodes.append(l) for l in level_map[level]]
        return nodes

    def __collect_bfs(self, level, nodes):
        nodes[level].append(self)
        for child in self.children:
            child.__collect_bfs(level + 1, nodes)

    def collect_depth_first(self):
        """Returns a list of the nodes traversed each level using depth first search.
        :return: a list consisting of the nodes in this tree ordered depth first.
        """
        nodes = self.collect_breadth_first()
        nodes.reverse()
        return nodes

    def find(self, predicate):
        """Searches the tree for node return true for the predicate function.
        :param predicate: the predicate to pass the node to evaluate.
        :return:
        """
        if not callable(predicate):
            raise TypeError("expected callable but got {}".format(type(predicate)))
        nodes = []
        self.rec_find(predicate, nodes)
        return nodes

    def rec_find(self, predicate, nodes):
        if predicate(self):
            nodes.append(self)
        for child in self._children:
            child.rec_find(predicate, nodes)

    def level(self, level: int):
        if level < 0:
            raise ValueError("invalid level")
        level_map = self.__collect_levels()
        levels = [level for level in level_map.keys()]
        if level in levels:
            return level_map[level]
        return []

    def __collect_levels(self):
        level_map = defaultdict(list)
        self.__collect_bfs(0, level_map)
        return level_map

    @staticmethod
    def build_tree(dictionary):
        """Builds a new tree given a dictionary.
        :param dictionary: a dictionary defining the tree.
            The data types of the constituting the dictionary should only be simple types.
        :return:
        """
        nodes = []
        if isinstance(dictionary, dict):
            for k, v in dictionary.items():
                root_node = Node(k)
                root_node.rec_build_tree(v)
                nodes.append(root_node)
        else:
            raise ValueError("invalid data: no tree structure")

        if len(nodes) == 1:
            return nodes[0]
        else:
            return nodes

    def rec_build_tree(self, d):
        if isinstance(d, dict):
            for k, v in d.items():
                node = self.add(k)
                node.rec_build_tree(v)
        elif isinstance(d, list):
            for v in d:
                self.rec_build_tree(v)
        elif isinstance(d, str):
            self.add(d)

    def __str__(self):
        if self._data:
            return str(self._data)
        else:
            return ""

    def __getitem__(self, key):
        """Allows index nodes looking for nodes.

        If key is an integer or a slice, it only index the children of the node.
        If another data type is given, it searches for a node that has data matching key.

        Params:
            key (Any): the index to search for.
        """
        if isinstance(key, int) or isinstance(key, slice):
            return self.children[key]
        return self.find(lambda node: node.data == key)

    def __iter__(self):
        self._nodes = self.collect_depth_first()
        return self

    def __next__(self):
        try:
            n = self._nodes.pop(0)
            return n
        except IndexError:
            raise StopIteration
