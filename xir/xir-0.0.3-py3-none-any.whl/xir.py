# pylint: disable=fixme, missing-docstring, protected-access
import json
import uuid as UUID


class Xir:
    def __init__(self):
        self.structure = Network(props=None)
        self.behavior = Behavior()

    def xir(self):
        return json.dumps(self.xir_dict(), indent=2)

    def xir_dict(self):
        return {
            'structure': self.structure.xir_dict(),
            'behavior': self.behavior.xir_dict()
        }


class Behavior:  # pylint: disable=too-few-public-methods
    # TODO
    def __init__(self):
        pass

    # TODO
    def xir_dict(self):  # pylint: disable=no-self-use
        return {}


class Network:
    def __init__(self, props):
        self.uuid = str(UUID.uuid4())
        self.props = props
        self.nets = []
        self.nodes = []
        self.links = []
        self._parent = None

    def net(self, props):
        n = Network(props)
        n._parent = self
        self.nets.append(n)
        return n

    def add_net(self, net):
        net._parent = self
        self.nets.append(net)
        return net

    def node(self, props=None, endpoints=None):
        n = Node(props, endpoints)
        n._parent = self
        self.nodes.append(n)
        return n

    def add_node(self, node):
        node._parent = self
        self.nodes.append(node)
        return node

    def add_nodes(self, nodes):
        for n in nodes:
            self.add_node(n)

    def link(self, endpoints, props=None):
        if props is None:
            props = {}

        l = Link(endpoints, props)
        self.links.append(l)
        l._parent = self
        create_neighborhood(l, endpoints)
        return l

    # same as link, but magically creates the required endpoints
    def connect(self, nodes, props=None):
        if props is None:
            props = {}
        endpoints = list(map(lambda x: x.endpoint(props), nodes))
        l = Link(endpoints, props)
        self.links.append(l)
        l._parent = self
        create_neighborhood(l, endpoints)
        return l

    def xir(self):
        return json.dumps(self.xir_dict(), indent=2)

    def xir_dict(self):
        return {
            'id': self.uuid,
            'props': self.props,
            'nets': [x.xir_dict() for x in self.nets],
            'nodes': [x.xir_dict() for x in self.nodes],
            'links': [x.xir_dict() for x in self.links]
        }

def pretty(net, indent=""):

    def iprint(a_super_long_annoying_python_linter_compliant_name):
        print(indent + a_super_long_annoying_python_linter_compliant_name)

    iprint(label(net))

    indent += "  "
    for n in net.nodes:
        iprint(label(n))
        indent += "  "
        for i, e in enumerate(n.endpoints):
            for b in e._neighbors:
                iprint("%2d: "%i + label(b.endpoint._parent))
        indent = indent[:-2]

    for subnet in net.nets:
        pretty(subnet, indent)

def label(thing):
    if 'name' in thing.props:
        return thing.props['name']
    return thing.uuid


def create_neighborhood(link, endpoints):
    for i, x in enumerate(endpoints):
        for y in endpoints[i:]:
            if x._parent.uuid != y._parent.uuid:
                x._neighbors.append(Neighbor(link, y))
                y._neighbors.append(Neighbor(link, x))


def prop_dict(data):

    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = prop_dict(v)

    if isinstance(data, list):
        for i, v in enumerate(data):
            data[i] = prop_dict(v)

    try:
        data = data.xir_dict()
    except:  # noqa: E722 pylint: disable=bare-except
        pass

    return data


class Node:
    def __init__(self, props=None, endpoints=None):
        if endpoints is None:
            self.endpoints = []
        else:
            for child in endpoints:
                child._parent = self
            self.endpoints = endpoints

        if props is None:
            self.props = {}
        else:
            self.props = props

        self.uuid = str(UUID.uuid4())
        self.props = props
        self.config = {}
        self._parent = None

    def configure(self, conf):
        self.config = conf
        return self

    def endpoint(self, props=None):
        if props is None:
            props = {}

        e = Endpoint(props)
        e._parent = self
        self.endpoints.append(e)
        return e

    def select(self, tag):
        result = []
        for e in self.endpoints:
            p = e.props.get('tag')
            if p is not None and p == tag:
                result.append(e)

        return result

    def neighbors(self, details=False):
        if details:
            return self.neighbors_detailed()
        return self.neighbors_brief()

    def neighbors_brief(self):
        result = []
        for e in self.endpoints:
            for n in e._neighbors:
                result.append(label(n.endpoint._parent))
        return result

    def neighbors_detailed(self):
        result = []
        for e in self.endpoints:
            for n in e._neighbors:
                result.append({label(n.endpoint._parent): n.link.props})
        return result

    def xir_dict(self):
        return {
            'id': self.uuid,
            'props': prop_dict(self.props),
            'config': prop_dict(self.config),
            'endpoints': [x.xir_dict() for x in self.endpoints]
        }


class Endpoint:
    def __init__(self, props, uuid=None):
        if uuid is None:
            self.uuid = str(UUID.uuid4())
        else:
            self.uuid = uuid

        self.props = props
        self._neighbors = []
        self._parent = None

    def xir_dict(self):
        return {
            'id': self.uuid,
            'props': self.props
        }

    def empty(self):
        return len(self._neighbors) == 0


class Link:  # pylint: disable=too-few-public-methods
    def __init__(self, endpoints, props):
        self.uuid = str(UUID.uuid4())
        self.props = props
        self._parent = None
        # self.endpoints = list(map(lambda x: Endpoint({}, x), nodes))
        self.endpoints = endpoints

    def xir_dict(self):
        return {
            'id': self.uuid,
            'props': self.props,
            'endpoints': [x.xir_dict() for x in self.endpoints]
        }


class Neighbor:  # pylint: disable=too-few-public-methods
    def __init__(self, link, endpoint):
        self.link = link
        self.endpoint = endpoint
        self._parent = None


def uid():
    return str(UUID.uuid4())


def protoFilter(x, proto):  # pylint: disable=invalid-name
    return list(filter(lambda e: e.props['protocol'] == proto, x.endpoints))
