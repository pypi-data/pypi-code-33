from collections import OrderedDict
from .format import formatter


class ConfigDict(OrderedDict):
    '''
    ConfigDict is an override of standard dictionary
    to allow dot-named access to nested dictionary
    values.

    The standard nested call:

        config['parent']['child']

    can also be accessed as:

        config['parent.child']

    '''
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        if '.' not in key:
            return super(ConfigDict, self).__getitem__(key)
        segments = key.split('.')
        end = self
        for seg in segments:
            end = super(ConfigDict, end).__getitem__(seg)
        return end

    def __contains__(self, key):
        if '.' not in key:
            return super(ConfigDict, self).__contains__(key)
        segments = key.split('.')
        end = self
        contains = False
        for seg in segments:
            contains = super(ConfigDict, end).__contains__(seg)
            if not contains:
                return contains
            end = super(ConfigDict, end).__getitem__(seg)
        return contains

    def walk_values(self):
        _values = []

        def _recurse(section, v):
            for val in super(ConfigDict, section).values():
                if isinstance(val, ConfigDict):
                    _recurse(val, v)
                if isinstance(val, ConfigValue):
                    v.append(val)

        _recurse(self, _values)

        return _values

    def copy(self):
        'od.copy() -> a shallow copy of od'
        return self.__class__(self)

    def __str__(self):
        return formatter(self)


class ConfigValue(object):

    def __init__(self, initial_value):
        self.raw_value = [initial_value]
        self.end_value = None

    def add(self, value):
        self.raw_value.append(value)

    @property
    def multiline(self):
        return len(self.raw_value) > 1

    @property
    def value(self):
        if self.multiline:
            return '\n'.join(self.raw_value)
        # if self.raw_value:
        return str(self.raw_value[0])

    def __deepcopy__(self, memo):
        return self.end_value


class ListNode(object):

    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.previous = None
        self.next = None

    def __repr__(self):
        return '<ListNode "{}">'.format(self.name)

    @property
    def is_root(self):
        return self.previous is None \
            and self.next is not None

    @property
    def is_tail(self):
        return self.next is None \
            and self.previous is not None

    @property
    def unlinked(self):
        return self.previous is None and self.next is None

    def append(self, node):
        _next = self.next
        if _next:
            _next.previous = node
        self.next = node
        self.next.previous = self
        self.next.next = _next
        return node

    def prepend(self, node):
        _previous = self.previous
        if _previous:
            _previous.next = node
        self.previous = node
        self.previous.next = self
        self.previous.previous = _previous
        return node

    def replace(self, node):
        self.name = node.name
        self.content = node.content
        return self

    def remove(self):
        if self.is_root:
            self.next.previous = None
        elif self.is_tail:
            self.previous.next = None
        elif not self.unlinked:
            self.next.previous = self.previous
            self.previous.next = self.next
        self.previous = None
        self.next = None

    def __eq__(self, node):
        return self.name == node.name \
            and self.content == node.content


class DoubleLinkedDict(object):

    def __init__(self, *args):
        self.current = None
        self.root = None
        self.tail = None
        self._dict = {}
        for name, content in args:
            self.append(name, content)

    def __len__(self):
        return len(self._dict)

    def __getitem__(self, index):
        return self._dict[index]

    def __setitem__(self, name, value):
        self.append(name, value)

    def __contains__(self, name):
        return name in self._dict

    def replace(self, node_name, content):
        node = ListNode(node_name, content)
        self._dict[node_name].replace(node)

    def append(self, name, content):
        node = ListNode(name, content)
        self._dict[name] = node
        if self.tail:
            self.tail.append(node)
        else:
            self.root = node
        self.tail = node

    def prepend(self, name, content):
        node = ListNode(name, content)
        self._dict[name] = node
        if self.root:
            self.root.prepend(node)
        else:
            self.tail = node
        self.root = node

    def insert_before(self, node_name, name, content):
        node = self._dict[node_name]
        new_node = ListNode(name, content)
        self._dict[name] = new_node
        node.prepend(new_node)
        if self.root is node:
            self.root = new_node

    def insert_after(self, node_name, name, content):
        node = self._dict[node_name]
        new_node = ListNode(name, content)
        self._dict[name] = new_node
        node.append(new_node)
        if self.tail is node:
            self.tail = new_node

    def __iter__(self):
        node = self.root
        yield node
        while not node.is_tail:
            node = node.next
            yield node

    def iter_names(self):
        for node in self:
            yield node.name

    def iter_values(self):
        for node in self:
            yield node.content
