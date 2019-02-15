from collections import deque
from hippodamia.enums import Health
from hippodamia.enums import ViewDetails
from hippodamia.enums import Necessity
import threading


"""
[ROOT]
  ├─ [ANode]
  │    ├─ [BNode]
  │    ├─ [CNode]
  │    │    ├─ [DNode]
  │    │    │    ├─ [ENode]
  │    │    │    └─ [FNode]  
  │    │    └─ [GNode]
  │    └─ [HNode]
  └─ [INode]
       ├─ [JNode]
       ├─ [KNode]
       │    ├─ [LNode]
       │    └─ [MNode]       
       └─ [NNode]
    
  
Root-ANode - prefix_first_line =  "  ├─ "
Root-ANode - prefix_next_lines =  "  │  "
ANode-CNode - prefix_first_line = "  │    ├─ "
ANode-CNode - prefix_next_lines = "  │    │  "
CNode-DNode - prefix_first_line = "  │    │    ├─ "
CNode-DNode - prefix_next_lines = "  │    │    │  "
INode-KNode - prefix_first_line = "       ├─ "
INode-KNode - prefix_next_lines = "       │  "

TYPE_A = "  ├─ "
TYPE_B = "  │  "
TYPE_C = "  └─ "
TYPE_D = "     "
"""


class Entry:
    MAX_NAME_LEN = 15
    INDENT = 2

    HORIZONTAL = "│"
    HORIZONTAL_CONNECTOR = "├"
    VERTICAL = "─"
    VERTICAL_CONNECTOR = "┬"
    EDGE = "└"
    SPACE = " "

    TYPE_A = SPACE + SPACE + HORIZONTAL_CONNECTOR + VERTICAL + SPACE
    TYPE_B = SPACE + SPACE + HORIZONTAL + SPACE + SPACE
    TYPE_C = SPACE + SPACE + EDGE + VERTICAL + SPACE
    TYPE_D = SPACE + SPACE + SPACE + SPACE + SPACE

    visited = None
    health = None
    name = None

    def update(self):
        raise NotImplementedError

    def reset_visited(self):
        raise NotImplementedError

    def _name2str(self):
        result = self.name
        if len(result) > self.MAX_NAME_LEN:
            result = result[:12]
        result = "[{}]".format(result)
        return result


class Branch(Entry):
    children = None

    def __init__(self, name):
        Entry.__init__(self)
        self.children = {}
        self.name = name
        self.update()

    def update(self, children=None):
        if not self.visited:
            if children is None:
                children = self.children

            self.health = Health.GREEN
            for gid, leaf in children.items():
                leaf_health = leaf.update()
                self.health = max(self.health, leaf_health)

            self.visited = True
        return self.health

    def reset_visited(self):
        for gid, leaf in self.children.items():
            leaf.reset_visited()
        self.visited = False

    def add_leaf(self, leaf, breadcrumbs, children=None):
        if children is None:
            children = self.children

        if len(breadcrumbs) == 0:
            children[leaf.gid] = leaf
        else:
            branch_name = breadcrumbs.popleft()
            if branch_name is None or branch_name == "":
                branch_name = "_"

            if branch_name not in children:
                children[branch_name] = Branch(branch_name)
            children[branch_name].add_leaf(leaf, breadcrumbs)

    def pformat(self, details=ViewDetails.NONE, filters=None):
        if filters is None:
            filters = deque()
        lines = self.tree_view("", "", details, filters)
        result = "\n".join(lines)
        return  result

    @staticmethod
    def _filter_match(name, entry_filter):
        if entry_filter is not None:
            name = name.lower()
            entry_filter = entry_filter.lower()
            return name.startswith(entry_filter)
        return True

    def tree_view(self, prefix_first_line, prefix_next_lines, details, filters):
        filters = filters.copy()
        try:
            entry_filter = filters.popleft()
        except IndexError:
            entry_filter = None

        first_line = prefix_first_line + self._pprint_details(details)
        lines = [first_line]
        prefix_a = prefix_next_lines + self.TYPE_A
        prefix_b = prefix_next_lines + self.TYPE_B
        prefix_c = prefix_next_lines + self.TYPE_C
        prefix_d = prefix_next_lines + self.TYPE_D

        counter = 0
        for name, entry in self.children.items():
            counter += 1
            if self._filter_match(name, entry_filter):
                if counter == len(self.children):
                    # last entry
                    prefix_first = prefix_c
                    prefix_next = prefix_d
                else:
                    prefix_first = prefix_a
                    prefix_next = prefix_b

                if type(entry) is Leaf:
                    line = prefix_first + entry.pformat(details)
                    lines.append(line)
                elif type(entry) is Branch:
                    sub_lines = entry.tree_view(prefix_first, prefix_next, details, filters)
                    lines += sub_lines
                else:
                    raise TypeError

        return lines

    def _pprint_details(self, details):
        result = [self._name2str()]
        if details & ViewDetails.HEALTH == ViewDetails.HEALTH:
            result.append(self.health.name)
        if details & ViewDetails.STATE == ViewDetails.STATE:
            pass
        if details & ViewDetails.GID == ViewDetails.GID:
            pass
        result = " ".join(result)
        return result


class Root(Branch):
    def __init__(self):
        Branch.__init__(self, name="__root__")

    def build_tree(self, leafs):
        new_children = {}

        for gid, leaf in leafs.items():
            breadcrumbs = leaf.breadcrumbs.copy()
            self.add_leaf(leaf, breadcrumbs, new_children)

        self.children = new_children
        self.update()


class Leaf(Entry):
    gid = None
    shadow = None
    breadcrumbs = None

    def __init__(self, shadow):
        Entry.__init__(self)
        self.shadow = shadow
        self.gid = self.shadow.properties.gid
        self.breadcrumbs = deque()
        self.update()

    def update(self):
        self.visited = True
        self.health = self.shadow.properties.health
        self.name = self.shadow.properties.name
        self.breadcrumbs = deque([self.shadow.properties.location, self.shadow.properties.room,
                                  self.shadow.properties.device])
        result = self.health
        if self.shadow.properties.necessity != Necessity.REQUIRED:
            result = min(result, Health.YELLOW)

        return result

    def reset_visited(self):
        self.visited = False

    def pformat(self, details=ViewDetails.NONE):
        result = [self._name2str()]

        if details & ViewDetails.HEALTH == ViewDetails.HEALTH:
            result.append(self.health.name)
        if details & ViewDetails.STATE == ViewDetails.STATE:
            result.append(self.shadow.get_state_id().name)
        if details & ViewDetails.GID == ViewDetails.GID:
            result.append("gid:")
            result.append(self.gid)

        result = " ".join(result)
        return result


class HierarchicalView:
    _logger = None
    _agentshadows = None
    _enforcement = None

    _tree = None
    _leafs = None

    _updateavailable = None
    _update_observer_thread = None
    _stop_observer = None

    def __init__(self, enforcement, agentshadows, updateavailable, logger):
        self._enforcement = enforcement
        self._logger = logger
        self._agentshadows = agentshadows
        self._updateavailable = updateavailable

        self._tree = Root()
        self._leafs = {}

        self._update_observer_thread = threading.Thread(target=self._update_observer)
        self._stop_observer = False

    def _process_update(self):
        self._tree.reset_visited()
        rebuild = self._add_new_shadows()
        rebuild = rebuild or self._purge_unvisited_leafs()
        if rebuild:
            self._tree.build_tree(self._leafs)
        self._tree.update()

    def pformat(self, details=ViewDetails.HEALTH, filters=None):
        if filters is None:
            filters = deque([None, None, None, None])
        else:
            filters = deque([filters["LOCATION"], filters["ROOM"], filters["DEVICE"], filters["SERVICE"]])
        return self._tree.pformat(details, filters)

    def _purge_unvisited_leafs(self):
        gids = []
        for gid, leaf in self._leafs.items():
            if not leaf.visited:
                gids.append(gid)
        rebuild = len(gids) > 0

        for gid in gids:
            del self._leafs[gid]

        return rebuild

    def _add_new_shadows(self):
        rebuild_tree = False
        for gid, shadow in self._agentshadows.items():
            if gid not in self._leafs:
                leaf = Leaf(shadow)
                self._leafs[gid] = leaf
                rebuild_tree = True
            else:
                self._leafs[gid].visited = True

        return rebuild_tree

    def _update_observer(self):
        while not self._stop_observer:
            self._updateavailable.wait()
            if not self._stop_observer:
                self._process_update()
            self._updateavailable.clear()

    def start(self):
        self._stop_observer = False
        self._update_observer_thread.start()
        self._updateavailable.set()

    def stop(self):
        self._stop_observer = True
        self._updateavailable.set()
        self._update_observer_thread.join()
