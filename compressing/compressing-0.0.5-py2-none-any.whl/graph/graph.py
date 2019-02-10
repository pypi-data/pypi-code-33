#!/usr/local/bin/python
# coding: utf-8

from abc import ABCMeta, abstractmethod


class Graph:
    """
    Interface for the Networkx library.

    Implemented by GraphAdapter class.

    See graph_adapter.py.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def set_graph(self, graph): pass

    @abstractmethod
    def load_dot(self, file_path): pass

    @abstractmethod
    def save_dot(self, file_path): pass

    @abstractmethod
    def to_agraph(self): pass

    @abstractmethod
    def add_node(self, node): pass

    @abstractmethod
    def get_nodes(self): pass

    @abstractmethod
    def set_node_attribute(self, node, attribute, value): pass

    @abstractmethod
    def get_node_attribute(self, node, attribute): pass

    @abstractmethod
    def get_all_node_attributes(self, node): pass

    @abstractmethod
    def get_in_neighbors(self, node): pass

    @abstractmethod
    def get_out_neighbors(self, node): pass

    @abstractmethod
    def get_in_edges(self, node): pass

    @abstractmethod
    def get_out_edges(self, node): pass

    @abstractmethod
    def get_in_degree(self, node): pass

    @abstractmethod
    def get_out_degree(self, node): pass

    @abstractmethod
    def remove_node(self, node): pass

    @abstractmethod
    def has_node(self, node): pass

    @abstractmethod
    def get_edges(self): pass

    @abstractmethod
    def add_edge(self, source, target, **kwargs): pass

    @abstractmethod
    def set_edge_attribute(self, source, target, attribute, value): pass

    @abstractmethod
    def get_edge_attribute(self, source, target, attribute): pass

    @abstractmethod
    def get_all_edge_attributes(self, source, target): pass

    @abstractmethod
    def remove_edge(self, source, target): pass

    @abstractmethod
    def remove_edges(self, edges): pass

    @abstractmethod
    def has_edge(self, source, target): pass

    @abstractmethod
    def get_all_shortest_paths(self, source, target): pass
