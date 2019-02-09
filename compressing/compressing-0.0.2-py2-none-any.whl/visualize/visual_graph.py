#!/usr/local/bin/python
# coding: utf-8

from abc import ABCMeta, abstractmethod


class VisualGraph:
    """
    Interface for the PyGraphviz library.

    Implemented by VisualGraphAdapter class.

    See visual_graph_adapter.py.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def draw_pdf(self): pass

    @abstractmethod
    def get_nodes(self): pass

    @abstractmethod
    def get_edges(self): pass

    @abstractmethod
    def get_node(self, node): pass

    @abstractmethod
    def get_edge(self, u, v): pass

    @abstractmethod
    def set_edge_attribute(self, u, v, attribute, value): pass

    @abstractmethod
    def get_edge_attribute(self, u, v, attribute): pass

    @abstractmethod
    def set_node_attribute(self, node, attribute, value): pass

    @abstractmethod
    def get_node_attribute(self, node, attribute): pass

    @abstractmethod
    def set_nodes_orientation(self, nodes, orientation): pass
