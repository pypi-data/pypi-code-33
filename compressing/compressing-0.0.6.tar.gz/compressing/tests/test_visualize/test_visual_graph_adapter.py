"""
Test for src/visualize/visual_graph_adapter.py
"""

import unittest as unt
from graph.graph_adapter import GraphAdapter
from visualize.visual_graph_adapter import VisualGraphAdapter

import networkx as nx


class TestVisualGraphAdapter(unt.TestCase):

    def setUp(self):
        graph = GraphAdapter()
        graph.set_graph(nx.DiGraph())
        self.vgraph = VisualGraphAdapter(graph)

    def test_set_name(self):
        self.vgraph.set_name("test_name")

        # Test set name
        self.assertEqual(self.vgraph.name, "test_name")

    def test_get_nodes(self):
        self.vgraph.agraph.add_node(1)
        self.vgraph.agraph.add_node(2)

        # Test get nodes
        self.assertEqual(set(self.vgraph.get_nodes()), {u'1', u'2'})

    def test_get_edges(self):
        self.vgraph.agraph.add_edge(1, 2)
        self.vgraph.agraph.add_edge(2, 3)
        self.vgraph.agraph.add_edge(3, 1)

        # Test get edges
        self.assertEqual(set(self.vgraph.get_edges()),
                         {(u'1', u'2'), (u'2', u'3'), (u'3', u'1')})

    def test_get_edge(self):
        self.vgraph.agraph.add_edge(1, 2)

        # Test get edge
        self.assertEqual(self.vgraph.get_edge(1, 2), (u'1', u'2'))

    def test_get_node(self):
        self.vgraph.agraph.add_node(1)

        # Test get edge
        self.assertEqual(self.vgraph.get_node(1), u'1')

    def test_set_edge_attribute(self):
        self.vgraph.agraph.add_edge(1, 2)

        # Test set edge attribute
        self.vgraph.set_edge_attribute(1, 2, "test_attribute", [1, 2])

        edge = self.vgraph.agraph.get_edge(1, 2)
        self.assertEqual(edge.attr, {u"test_attribute": u'[1, 2]'})

    def test_get_edge_attribute(self):
        self.vgraph.agraph.add_edge(1, 2)
        edge = self.vgraph.agraph.get_edge(1, 2)
        edge.attr["test_attribute"] = "123"

        # Test get edge attribute
        self.assertEqual(self.vgraph.get_edge_attribute(1, 2, "test_attribute"),
                         u"123")

    def test_set_node_attribute(self):
        self.vgraph.agraph.add_node(1)

        # Test set edge attribute
        self.vgraph.set_node_attribute(1, "test_attribute", [1, 2])

        node = self.vgraph.agraph.get_node(1)
        self.assertEqual(node.attr, {u"test_attribute": u'[1, 2]'})

    def test_get_node_attribute(self):
        self.vgraph.agraph.add_node(1)
        node = self.vgraph.agraph.get_node(1)
        node.attr["test_attribute"] = "123"

        # Test get edge attribute
        self.assertEqual(self.vgraph.get_node_attribute(1, "test_attribute"),
                         u"123")


if __name__ == '__main__':
    unt.main(verbosity=2)
