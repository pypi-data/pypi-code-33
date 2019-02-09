#!/usr/local/bin/python
# coding: utf-8

from util import constants
from visualize import visual_graph_adapter as vga
from graph import proof_graph as pgr


class VisualProofGraph:
    """
    Base class for visualize proof graphs.

    This class uses a VisualProofGraph instance for generate
    visualizations of proof graphs.

    This class generates visualizations of the entire graph. The
    generation takes place before and after the compression of the
    proof.
    """

    # File names
    INPUT = constants.INPUT
    FINAL = constants.FINAL

    def __init__(self, graph):
        """
        Initializes a VisualProofGraph instance.

        Set GraphAdapter object to instance variable 'graph'.

        Initializes instance variable 'vgraph' (VisualGraphAdapter)
        with None.
        """
        self.graph = graph
        self.vgraph = None

    def draw_input(self):
        """
        Generates the visualization of the graph in 'graph' variable.

        The file generated is "pdf/input.pdf"
        """
        self.vgraph = vga.VisualGraphAdapter(self.graph)
        self.__draw(VisualProofGraph.INPUT)

    def draw_final(self, file_path=None):
        """
        Generates the visualization of the graph in 'graph' variable.

        The file generated is "pdf/final.pdf"
        """
        self.vgraph = vga.VisualGraphAdapter(self.graph)
        self.__draw(VisualProofGraph.FINAL, file_path)

    def draw_collapse(self, name, nodes, before=False, after=False,
                      premisses_1=None, premisses_2=None, a_edges=None):
        if before:
            node1, node2 = nodes

            ancestor_edges = self.__get_ancestor_in_edges(node1, node2)

            collapse_graph, select_nodes = self.__init_collapse_graph(nodes)
            self.vgraph = vga.VisualGraphAdapter(collapse_graph)

            in_n = select_nodes[node1]["in_n"] + select_nodes[node2]["in_n"]
            out_n = select_nodes[node1]["out_n"] + select_nodes[node2]["out_n"]

            self.__set_nodes_orientation(nodes, in_n, out_n)

            self.__set_nodes_color(nodes, select_nodes[node1]["in_n"],
                                   select_nodes[node2]["in_n"])

            self.__draw(name)

            return select_nodes[node1]["in_n"], select_nodes[node2][
                "in_n"], ancestor_edges
        elif after:
            node, = nodes
            collapse_graph, select_nodes = \
                self.__init_collapse_graph(nodes, a_edges=a_edges)
            self.vgraph = vga.VisualGraphAdapter(collapse_graph)

            self.__set_nodes_orientation(nodes, select_nodes[node]["in_n"],
                                         select_nodes[node]["out_n"])

            self.__set_nodes_color(nodes, premisses_1, premisses_2)

            self.__draw(name)
        else:
            raise Exception('before or after must be True')

    def set_node_color_collapse(self, red_nodes, green_nodes, blue_nodes):
        for node in red_nodes:
            self.vgraph.set_node_attribute(node, "color", "grey")
            self.vgraph.set_node_attribute(node, "style", "filled")

        for node in green_nodes:
            self.vgraph.set_node_attribute(node, "color", "green")
            self.vgraph.set_node_attribute(node, "style", "filled")

        for node in blue_nodes:
            self.vgraph.set_node_attribute(node, "color", "blue")
            self.vgraph.set_node_attribute(node, "style", "filled")

    def __draw(self, name, file_path=None):
        """
        Generate file visualization from 'vgraph' variable.

        Set nodes and edges layout.
        """
        self.vgraph.set_name(name)
        self.__set_nodes_layout()
        self.__set_edges_layout()
        self.vgraph.draw_pdf(file_path)

    def __set_nodes_layout(self):
        """
        Set nodes layout from VisualGraphAdapter 'vgraph'.

        Assigns new values to node attributes:
        - label = formula

        - If hypothesis attribute is True:
            - xlabel = "h"
            - color = "red"
        """
        for node in self.vgraph.get_nodes():
            formula = self.vgraph.get_node_attribute(node, constants.FORMULA)
            self.vgraph.set_node_attribute(node, vga.VisualGraphAdapter.LABEL,
                                           formula)

            is_hypothesis = self.vgraph.get_node_attribute(
                node, constants.HYPOTHESIS)
            if is_hypothesis:
                self.vgraph.set_node_attribute(
                    node, vga.VisualGraphAdapter.XLABEL, "h")
                self.vgraph.set_node_attribute(node,
                                               vga.VisualGraphAdapter.COLOR,
                                               vga.VisualGraphAdapter.RED)

            del node.attr[constants.FORMULA], node.attr[constants.HYPOTHESIS]

    def __set_edges_layout(self):
        """
        Set edges layout from VisualGraphAdapter 'vgraph'.

        Assigns new values to edge attributes:
        - If ancestor attribute is True:
            - color = "blue"
            - fontcolor = "red"
            - xlabel = path

        - If collapsed attribute is True:
            - label = greek letter lambda

        - If edge is deductive:
            - xlabel = color
        """
        for (u, v) in self.vgraph.get_edges():
            edge = self.vgraph.get_edge(u, v)
            if edge.attr[constants.ANCESTOR] == constants.TRUE:
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.COLOR,
                                               vga.VisualGraphAdapter.BLUE)
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.FONTCOLOR,
                                               vga.VisualGraphAdapter.RED)
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.XLABEL,
                                               str(edge.attr[constants.PATH]))
                del edge.attr[constants.PATH]
            elif edge.attr[constants.COLLAPSED] == constants.TRUE:
                xlabel = constants.LAMBDA + edge.attr[constants.LAMBDA_COLORS]
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.XLABEL,
                                               xlabel)
            else:
                self.vgraph.set_edge_attribute(u, v,
                                               vga.VisualGraphAdapter.XLABEL,
                                               str(edge.attr[constants.COLOR]))
                del edge.attr[constants.COLOR]

    def __set_nodes_orientation(self, nodes, in_n, out_n):
        self.vgraph.set_nodes_orientation(nodes, constants.SAME)
        self.vgraph.set_nodes_orientation(in_n, constants.SAME)
        self.vgraph.set_nodes_orientation(in_n, constants.UPPER)
        self.vgraph.set_nodes_orientation(out_n, constants.SAME)

    def __set_nodes_color(self, nodes, premisses_1, premisses_2):
        if len(nodes) == 2:
            self.vgraph.set_node_attribute(nodes[0], "color", "#c1c1c1")
            self.vgraph.set_node_attribute(nodes[0], "style", "filled")
            self.vgraph.set_node_attribute(nodes[1], "color", "#424242")
            self.vgraph.set_node_attribute(nodes[1], "style", "filled")
        elif len(nodes) == 1:
            self.vgraph.set_node_attribute(nodes[0], "color", "#828282")
            self.vgraph.set_node_attribute(nodes[0], "style", "filled")

        for node in premisses_1:
            self.vgraph.set_node_attribute(node, "color", "#25e000")
            self.vgraph.set_node_attribute(node, "style", "filled")

        for node in premisses_2:
            self.vgraph.set_node_attribute(node, "color", "#127200")
            self.vgraph.set_node_attribute(node, "style", "filled")

    def __init_collapse_graph(self, nodes, a_edges=None):
        collapse_graph = pgr.ProofGraph()
        select_nodes = {}
        for node in nodes:
            select_nodes[node] = {"in_n": [], "out_n": [],
                                  "ancestor_sources": []}

            # Add node and node attributes
            self.__add_copy_node(collapse_graph, node)

            # Add ancestors and edges between them
            in_edges = self.graph.get_deductive_in_edges(node)
            for (source, target) in in_edges:
                self.__add_copy_node(collapse_graph, source)
                self.__add_copy_edge(collapse_graph, source, target)
                select_nodes[node]["in_n"].append(source)

            # Add ancestors and edges between them
            out_edges = self.graph.get_deductive_out_edges(node)
            for (source, target) in out_edges:
                self.__add_copy_node(collapse_graph, target)
                self.__add_copy_edge(collapse_graph, source, target)
                select_nodes[node]["out_n"].append(target)

            in_neighbors = [node]

            while in_neighbors:
                in_node = in_neighbors.pop(0)
                ancestor_target = self.graph.get_node_attribute(
                    in_node, constants.ANCESTOR_TARGET)
                if ancestor_target:

                    self.__add_copy_node(collapse_graph, in_node)
                    in_edges = self.graph.get_ancestor_in_edges(in_node)
                    for (s, t) in in_edges:
                        self.__add_copy_node(collapse_graph, s)
                        self.__add_copy_edge(collapse_graph, s, t)
                        select_nodes[node]["ancestor_sources"].append(s)
                in_in_neighbors = self.graph.get_deductive_in_neighbors(in_node)
                in_neighbors += in_in_neighbors

            if a_edges:
                for (s, t) in a_edges:
                    self.__add_copy_node(collapse_graph, s)
                    select_nodes[node]["ancestor_sources"].append(s)
                    if self.graph.has_edge(s, t):
                        self.__add_copy_edge(collapse_graph, s, t)

            for ancestor in select_nodes[node]["ancestor_sources"]:
                paths = self.graph.get_deductive_paths(node, ancestor)
                for path in paths:
                    self.__add_copy_path(collapse_graph, path)

        return collapse_graph, select_nodes

    def __add_copy_path(self, collapse_graph, path):
        for node in path:
            if node != path[-1]:
                index = path.index(node)
                self.__add_copy_node(collapse_graph, node)
                self.__add_copy_node(collapse_graph, path[index + 1])
                self.__add_copy_edge(collapse_graph, node, path[index + 1])

    def __add_copy_node(self, collapse_graph, node):
        if not collapse_graph.has_node(node):
            # Add node
            collapse_graph.add_node(node)

            # Add node attributes
            attr_node = self.graph.get_all_node_attributes(node)
            for attr, value in attr_node.items():
                collapse_graph.set_node_attribute(node, attr, value)

    def __add_copy_edge(self, collapse_graph, source, target):
        if not collapse_graph.has_edge(source, target):
            # Add node
            collapse_graph.add_edge(source, target)

            # Add node attributes
            attr_edge = self.graph.get_all_edge_attributes(source, target)
            for attr, value in attr_edge.items():
                collapse_graph.set_edge_attribute(source, target, attr, value)

    def __get_ancestor_in_edges(self, node1, node2):
        common_neighbor = self.__check_common_neighbor(node1, node2)
        if self.__check_common_neighbor(node1, node2):
            successor_1 = successor_2 = common_neighbor

            ancestor_1 = \
                self.__get_ancestor_edges_redirect(node1, successor=successor_1)
        else:
            successors_1 = self.graph.get_deductive_out_neighbors(node1)
            successor_2, = self.graph.get_deductive_out_neighbors(node2)

            ancestor_1 = []
            for s1 in successors_1:
                ancestor_1 += \
                    self.__get_ancestor_edges_redirect(node1, successor=s1)

        ancestor_2 = self.__get_ancestor_edges_redirect(node2,
                                                        successor=successor_2)

        return ancestor_1 + ancestor_2

    def __check_common_neighbor(self, node1, node2):
        out_edges_1 = self.graph.get_deductive_out_neighbors(node1)
        out_edges_2 = self.graph.get_deductive_out_neighbors(node2)

        common_neighbor = None

        for n1 in out_edges_1:
            for n2 in out_edges_2:
                if n1 == n2:
                    common_neighbor = n1

        return common_neighbor

    def __get_ancestor_edges_redirect(self, node, successor=None):
        ancestor_edges = []

        in_degree = self.graph.get_deductive_in_degree(node)
        a_target = self.graph.get_node_attribute(node,
                                                 constants.ANCESTOR_TARGET)

        if in_degree == 0 and a_target:
            a_edges_node = self.graph.get_ancestor_in_edges(node)
            for (s, t) in a_edges_node:
                ancestor_edges.append((s, successor))

        return ancestor_edges
