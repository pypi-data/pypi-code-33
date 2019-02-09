#!/usr/local/bin/python
# coding: utf-8


import networkx as nx
import pygraphviz as pgv

from graph import Graph


class GraphAdapter(Graph):
    """
    This class uses the graph structure of the networkx library.

    See more: https://networkx.github.io
    """

    def __init__(self):
        """
        Initializes a GraphAdapter instance and assign None to
        graph variable.
        """
        self.graph = nx.DiGraph()

    def set_graph(self, graph):
        """
        Set 'graph' to instance variable 'graph'.

        Parameters
        ----------
        graph: DiGraph object
        """
        self.graph = graph

    def load_dot(self, file_path):
        """
        Return a DiGraph instance from dot file 'file_path'.

        Parameters
        ----------
        file_path: path file
            Dot file containing the proof graph.

        Raises
        ------
        FileError
            'file_path' not exists
            'file_path' is empty

        Returns
        -------
        digraph:
            A DiGraph instance from networkx library
        """
        try:
            agraph = nx.nx_agraph.read_dot(file_path)
            self.graph = nx.DiGraph(agraph)
        except pgv.DotError:
            message = "is poorly formulated"
            raise FileError(file_path, message)
        except IOError:
            message = "not exists"
            raise FileError(file_path, message)

    def save_dot(self, file_path):
        nx.nx_agraph.write_dot(self.graph, file_path)

    def to_agraph(self):
        """
        Return a Agraph (from pygraphviz library) instance from graph
        variable.

        Returns
        -------
        agraph:
            An Agraph instance from pygraphviz library
        """
        agraph = nx.nx_agraph.to_agraph(self.graph)
        return agraph

    def add_node(self, node):
        """
        Add node to graph

        Parameters
        ----------
        node: hashable type
            Node to be added to the graph.
        """
        self.graph.add_node(node)

    def get_nodes(self):
        """
        Return a list of all nodes in the graph.

        Returns
        -------
        nodes: list
            List of all nodes in the graph
        """
        nodes = list(self.graph.nodes)
        return nodes

    def set_node_attribute(self, node, attribute, value):
        """
        Assign value to node attribute.

        Parameters
        ----------
        node: hashable type
            Node in the graph

        attribute: hashable type
            Node attribute

        value: int, string or boolean
            Value of node attribute

        Raises
        ------
        AttributeError
            'attribute' is not hashable type.

        NodeGraphError
            'node' is not in the graph.
        """
        try:
            if self.graph.has_node(node):
                self.graph.nodes[node][attribute] = value
            else:
                message = "is not in the graph"
                raise NodeGraphError(node, message)
        except TypeError:
            message = "is not hashable"
            raise NodeAttributeGraphError(attribute, message)

    def get_node_attribute(self, node, attribute):
        """
        Return the node attribute.

        Parameters
        ----------
        node: hashable type
            Node in the graph

        attribute: hashable type
            Node attribute

        Raises
        ------
        NodeAttributeGraphError
            'node' does not have 'attribute'.

        NodeGraphError
            'node' is not in the graph.

        Returns
        -------
        attribute: object
            Value of node attribute.
        """
        try:
            if self.graph.has_node(node):
                node_attribute = self.graph.nodes[node][attribute]
                return node_attribute
            else:
                message = "is not in the graph"
                raise NodeGraphError(node, message)
        except TypeError:
            message = "is not hashable"
            raise NodeAttributeGraphError(attribute, message)
        except KeyError:
            message = "not exists"
            raise NodeAttributeGraphError(attribute, message)

    def get_all_node_attributes(self, node):
        """
        Return a dictionary-like object with all node attributes

        Parameters
        ----------
        node: hashable type
            Node in the graph

        Raises
        ------
        NodeGraphError
            'node' is not in the graph.

        Returns
        -------
        attributes: dictionary-like object
            Dictionary with all node attributes
        """
        if self.graph.has_node(node):
            attributes = self.graph.nodes[node]
            return attributes
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def get_in_neighbors(self, node):
        """
        Returns a list of nodes that are source of edges that pointing
        to the node.

        Parameters
        ----------
        node: hashable type
            Node in the graph

        Raises
        ------
        NodeGraphError
            'node' is not in the graph.

        Returns
        -------
        in_neighbors: list
            List with all in neighbors of 'node'
        """
        if self.graph.has_node(node):
            in_neighbors = list(self.graph.predecessors(node))
            return in_neighbors
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def get_out_neighbors(self, node):
        """
        Returns a list of nodes that are target of edges that pointing
        out of the node.

        Parameters
        ----------
        node: hashable type
            Node in the graph

        Raises
        ------
        NodeGraphError
            'node' is not in the graph.

        Returns
        -------
        out_neighbors: list
            List with all out neighbors of 'node'
        """
        if self.graph.has_node(node):
            out_neighbors = list(self.graph.successors(node))
            return out_neighbors
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def get_in_edges(self, node):
        """
        Return the edges that pointing to the node.

        Parameters
        ----------
        node: hashable type
            Node in the graph

        Raises
        ------
        NodeGraphError
            'node' is not in the graph.

        Returns
        -------
        in_edges: list
            List of edges (source, node) that pointing to the node.
        """
        if self.graph.has_node(node):
            in_edges = self.graph.in_edges(node, data=False)
            return in_edges
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def get_out_edges(self, node):
        """
        Return the edges that pointing out of the node.

        Parameters
        ----------
        node: hashable type
            Node in the graph

        Raises
        ------
        NodeGraphError
            'node' is not in the graph

        Returns
        -------
        out_edges: list
            List of edges (node, target) that pointing out of the
            node.
        """
        if self.graph.has_node(node):
            out_edges = list(self.graph.out_edges(node, data=False))
            return out_edges
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def get_in_degree(self, node):
        """
        Return the number of edges that pointing to the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        GraphError
            'node' is not in the graph

        Returns
        -------
        in_degree: int
            Number of edges that pointing to the node.
        """
        if self.graph.has_node(node):
            in_degree = self.graph.in_degree(node)
            return in_degree

        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def get_out_degree(self, node):
        """
        Return the number of edges that pointing out of the node.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        GraphError
            'node' is not in the graph

        Returns
        -------
        out_degree: int
            Number of edges that pointing out of the node.
        """
        if self.graph.has_node(node):
            out_degree = self.graph.out_degree(node)
            return out_degree
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def remove_node(self, node):
        """
        Remove node from the graph.

        Parameters
        ----------
        node: node
            Node in the graph

        Raises
        ------
        GraphError
            'node' is not in the graph
        """
        if self.graph.has_node(node):
            self.graph.remove_node(node)
        else:
            message = "is not in the graph"
            raise NodeGraphError(node, message)

    def has_node(self, node):
        """
        Return True if node exists in graph. Return False if node not
        exists.

        Parameters
        ----------
        node: node
            Node in the graph
        """
        return self.graph.has_node(node)

    def get_edges(self):
        """
        Return a list with all edges in the graph.

        Returns
        -------
        edges: list
            List with all edges in the graph
        """
        edges = list(self.graph.edges)
        return edges

    def add_edge(self, source, target, **kwargs):
        """
        Add the edge (source, target) in the graph.

        Parameters
        ----------
        source, target: hashable types
            Nodes in the graph

        kwargs: keywords arguments, optional
            Attributes of edge.

        Raises
        ------
        NodeGraphError
            'source' or 'target' is not in the graph.

        AttributeError
            Some attribute in 'kwargs' is not hashable.
        """
        if self.graph.has_node(source):
            if self.graph.has_node(target):
                if self.graph.has_edge(source, target):
                    message = "already exists"
                    raise EdgeGraphError(source, target, message)
                self.graph.add_edge(source, target)
                if kwargs:
                    for attribute, value in kwargs.items():
                        try:
                            self.graph.edges[source, target][attribute] = value
                        except TypeError:
                            message = "is not hashable"
                            raise EdgeAttributeGraphError(attribute, message)
            else:
                message = "is not in the graph"
                raise NodeGraphError(target, message)
        else:
            message = "is not in the graph"
            raise NodeGraphError(source, message)

    def has_edge(self, source, target):
        """
        Return True if edge exists in the graph, False if not exists

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph
        """
        return self.graph.has_edge(source, target)

    def set_edge_attribute(self, source, target, attribute, value):
        """
        Assign value to edge attribute.

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph

        attribute: hashable type
            Node attribute

        value: int, string or boolean
            Value of edge attribute

        Raises
        ------
        EdgeGraphError
            The edge (source, target) is not in the graph

        EdgeAttributeGraphError
            'attribute' is not hashable type.
        """
        try:
            if self.graph.has_edge(source, target):
                self.graph.edges[source, target][attribute] = value
            else:
                message = "is not in the graph"
                raise EdgeGraphError(source, target, message)
        except TypeError:
            message = "is not hashable"
            raise EdgeAttributeGraphError(attribute, message)
        except KeyError:
            message = "not exists"
            raise EdgeAttributeGraphError(attribute, message)

    def get_edge_attribute(self, source, target, attribute):
        """
        Return the edge attribute.

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph

        attribute: hashable type
            Node attribute

        Raises
        ------
        EdgeAttributeGraphError
            'attribute' is not hashable type.

        EdgeGraphError
            The edge (source, target) is not in the graph

        Returns
        -------
        attribute: object
            Value of edge attribute.
        """
        if self.graph.has_edge(source, target):
            try:
                edge_attribute = self.graph.edges[source, target][attribute]
                return edge_attribute
            except TypeError:
                message = "is not hashable"
                raise EdgeAttributeGraphError(attribute, message)
            except KeyError:
                message = "not exists"
                raise EdgeAttributeGraphError(attribute, message)
        else:
            message = "is not in the graph"
            raise EdgeGraphError(source, target, message)

    def get_all_edge_attributes(self, source, target):
        """
        Return a dictionary-like object with all edge attributes

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph

        Raises
        ------
        EdgeGraphError
            The edge (source, target) is not in the graph.

        Returns
        -------
        attributes: dictionary-like object
            Dictionary with all edge attributes
        """
        if self.graph.has_edge(source, target):
            return self.graph.edges[source, target]
        else:
            message = "not exists"
            raise EdgeGraphError(source, target, message)

    def remove_edge(self, source, target):
        """
        Remove edge from the graph.

        Parameters
        ----------
        source, target: hashable type
            Nodes in the graph

        Raises
        ------
        EdgeGraphError
            The edge (source, target) is not in the graph.
        """
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
        else:
            message = "not exists"
            raise EdgeGraphError(source, target, message)

    def remove_edges(self, edges):
        """
        Remove edges from the graph.

        Parameters
        ----------
        edges: list of (source, target)
            Edges in the graph
        """
        self.graph.remove_edges_from(edges)

    def get_all_shortest_paths(self, source, target):
        return nx.all_shortest_paths(self.graph, source, target)


class FileError(Exception):

    def __init__(self, path, message):
        self.message = message
        self.path = path

    def __str__(self):
        message = "The file {0} {1}".format(self.path, self.message)
        return message


class GraphError(Exception):
    """
    Base class for exceptions raised in GraphAdapter object.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NodeGraphError(GraphError):
    """
    Exception raised if an error occurs in node of GraphAdapter object.
    """

    def __init__(self, node, message):
        GraphError.__init__(self, message)
        self.node = node

    def __str__(self):
        message = "The node {0} {1}".format(self.node, self.message)
        return message


class EdgeGraphError(GraphError):
    """
    Exception raised if an error occurs in edge of GraphAdapter object.
    """

    def __init__(self, source, target, message):
        GraphError.__init__(self, message)
        self.source = source
        self.target = target

    def __str__(self):
        message = "The edge ({0}, {1}) {2}".format(self.source,
                                                   self.target,
                                                   self.message)
        return message


class NodeAttributeGraphError(GraphError):
    """
    Exception raised if an error occurs in node attribute of
    GraphAdapter object.
    """

    def __init__(self, attribute, message):
        GraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message


class EdgeAttributeGraphError(GraphError):
    """
    Exception raised if an error occurs in edge attribute of
    GraphAdapter object.
    """

    def __init__(self, attribute, message):
        GraphError.__init__(self, message)
        self.attribute = attribute

    def __str__(self):
        message = "The attribute {0} {1}".format(self.attribute, self.message)
        return message
