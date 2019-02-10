"""
Test for src/graph/graph_adapter.py
"""

from graph.graph_adapter import GraphAdapter, FileError, \
    NodeGraphError, EdgeGraphError, NodeAttributeGraphError, \
    EdgeAttributeGraphError
import networkx as nx
import unittest as unt
import pygraphviz as pgv


class GraphAdapterTest(unt.TestCase):

    def setUp(self):
        self.graph_adapter = GraphAdapter()
        self.success_file = "input_test/input_success.dot"

    def test_load_dot(self):
        # Test return type
        self.graph_adapter.load_dot(self.success_file)
        self.assertIsInstance(self.graph_adapter.graph, nx.DiGraph)

        # Test raising exception if file is empty
        empty_file = "input_test/input_empty.dot"
        self.assertRaises(FileError,
                          self.graph_adapter.load_dot,
                          empty_file)

        # Test raising exception if file not exists
        success_file = "input_test/input_not_exists.dot"
        self.assertRaises(FileError,
                          self.graph_adapter.load_dot,
                          success_file)

        # Test raising exception if format files is incorrect
        incorrect_format_file = "input_test/input_incorrect_format.pdf"
        self.assertRaises(FileError,
                          self.graph_adapter.load_dot,
                          incorrect_format_file)

    def test_to_agraph(self):
        # Test return type
        self.graph_adapter.load_dot(self.success_file)
        self.assertIsInstance(self.graph_adapter.to_agraph(), pgv.AGraph)

    def test_add_node(self):
        graph = nx.DiGraph()
        self.graph_adapter.set_graph(graph)

        # Test node in the graph
        self.graph_adapter.add_node('1')
        self.assertTrue(self.graph_adapter.graph.has_node('1'))

    def test_get_nodes(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        self.graph_adapter.set_graph(graph)

        # Test return type
        self.assertIs(type(self.graph_adapter.get_nodes()), list)

        # Test return result
        self.assertEqual(set(self.graph_adapter.get_nodes()), {'1', '2'})

    def test_set_node_attribute(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph (node
        # 10000 not exists)
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.set_node_attribute,
            node='2', attribute=3, value=0)

        # Test raising exception if attribute is not hashable (node '1' exists)
        self.assertRaises(
            NodeAttributeGraphError,
            self.graph_adapter.set_node_attribute,
            node='1', attribute=[], value=0)

        # Test node attribute value
        self.graph_adapter.set_node_attribute('1', "test_attr", True)
        self.assertEqual(graph.nodes['1']["test_attr"], True)

    def test_get_node_attribute(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.nodes['1']["test_attr"] = True
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_node_attribute,
            node='2', attribute="test_attr")

        # Test raising exception if attribute is not hashable
        self.assertRaises(
            NodeAttributeGraphError,
            self.graph_adapter.get_node_attribute,
            node='1', attribute=[])

        # Test raising exception if attribute not exists
        self.assertRaises(
            NodeAttributeGraphError,
            self.graph_adapter.get_node_attribute,
            node='1', attribute="not_exists")

        # Test return result
        self.assertEqual(
            self.graph_adapter.get_node_attribute('1', 'test_attr'),
            True)

    def test_get_all_node_attributes(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.nodes['1']["attr1"] = 1
        graph.nodes['1']["attr2"] = 2
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_all_node_attributes,
            node='2')

        # Test return result
        self.assertEqual(
            self.graph_adapter.get_all_node_attributes('1'),
            {"attr1": 1, "attr2": 2})

    def test_get_in_neighbors(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_in_neighbors,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.graph_adapter.get_in_neighbors('1')),
            {'2', '3'})

    def test_get_out_neighbors(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_out_neighbors,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.graph_adapter.get_out_neighbors('1')),
            {'2', '3'})

    def test_get_in_edges(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_in_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.graph_adapter.get_in_edges('1')),
            {('2', '1'), ('3', '1')})

    def test_get_out_edges(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_out_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.graph_adapter.get_out_edges('1')),
            {('1', '2'), ('1', '3')})

    def test_get_in_degree(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_in_degree,
            node='4')

        # Test return result
        self.assertEqual(self.graph_adapter.get_in_degree('1'), 2)

    def test_get_out_degree(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.get_out_degree,
            node='4')

        # Test return result
        self.assertEqual(self.graph_adapter.get_out_degree('1'), 2)

    def test_remove_node(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.remove_node,
            node='2')

        # Test node in graph
        self.graph_adapter.remove_node('1')
        self.assertFalse(graph.has_node('1'))

    def test_has_node(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        self.graph_adapter.set_graph(graph)

        # Test if node Not exists
        self.assertFalse(self.graph_adapter.has_node('2'))

        # Test if node exists
        self.assertTrue(self.graph_adapter.has_node('1'))

    def test_get_edges(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.graph_adapter.set_graph(graph)

        # Test return result
        self.assertEqual(
            set(self.graph_adapter.get_edges()),
            {('1', '2'), ('1', '3')})

    def test_add_edge(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        self.graph_adapter.set_graph(graph)

        # Test raising exception if source is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.add_edge,
            source='4', target='3')

        # Test if target is not in the graph
        self.assertRaises(
            NodeGraphError,
            self.graph_adapter.add_edge,
            source='3', target='4')

        # Test edge in graph
        self.graph_adapter.add_edge('1', '2')
        self.assertTrue(self.graph_adapter.graph.has_edge('1', '2'))

        # Test edge attribute in graph
        self.graph_adapter.add_edge('1', '3', test_attribute=1)
        self.assertEqual(
            self.graph_adapter.graph.edges['1', '3']["test_attribute"],
            1)

    def test_has_edge(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.graph_adapter.set_graph(graph)

        # Test if graph has edge
        self.assertTrue(self.graph_adapter.has_edge('1', '2'))

        # Test if graph does not have
        self.assertFalse(self.graph_adapter.has_edge('2', '1'))

    def test_set_edge_attribute(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.graph_adapter.set_graph(graph)

        # Test if edge is not in the graph
        self.assertRaises(
            EdgeGraphError,
            self.graph_adapter.set_edge_attribute,
            source='2', target='1', attribute="test_attribute", value=True)

        # Test if attribute is not hashable
        self.assertRaises(
            EdgeAttributeGraphError,
            self.graph_adapter.set_edge_attribute,
            source='1', target='2', attribute=[], value=True)

        # Test edge attribute in the graph
        self.graph_adapter.set_edge_attribute('1', '2', "test_attribute", 0)
        self.assertEqual(
            self.graph_adapter.graph.edges['1', '2']["test_attribute"],
            0)

    def test_get_edge_attribute(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        graph.edges['1', '2']["test_attribute"] = 0
        self.graph_adapter.set_graph(graph)

        # Test if edge not exists in the graph
        self.assertRaises(
            EdgeGraphError,
            self.graph_adapter.get_edge_attribute,
            source='2', target='1', attribute="test_attribute")

        # Test if attribute is not hashable
        self.assertRaises(
            EdgeAttributeGraphError,
            self.graph_adapter.get_edge_attribute,
            source='1', target='2', attribute=[])

        # Test return result
        self.assertEqual(
            self.graph_adapter.get_edge_attribute('1', '2', "test_attribute"),
            0)

    def test_get_all_edge_attributes(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        graph.edges['1', '2']["test_attribute1"] = 1
        graph.edges['1', '2']["test_attribute2"] = 2
        self.graph_adapter.set_graph(graph)

        # Test if edge is not in the graph
        self.assertRaises(
            EdgeGraphError,
            self.graph_adapter.get_all_edge_attributes,
            source='2', target='1')

        # Test return result
        self.assertEqual(
            self.graph_adapter.get_all_edge_attributes('1', '2'),
            {"test_attribute1": 1, "test_attribute2": 2})

    def test_remove_edge(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.graph_adapter.set_graph(graph)

        # Test if edge is not in the graph
        self.assertRaises(
            EdgeGraphError,
            self.graph_adapter.remove_edge,
            source='2', target='1')

        # Test edge in the graph
        self.graph_adapter.remove_edge('1', '2')
        self.assertFalse(self.graph_adapter.graph.has_edge('1', '2'))

    def test_remove_edges(self):
        graph = nx.DiGraph()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        graph.add_edge('2', '1')
        self.graph_adapter.set_graph(graph)

        # Test edges in the graph
        self.graph_adapter.remove_edges([('1', '2'), ('2', '1')])
        self.assertFalse(self.graph_adapter.graph.has_edge('1', '2'))
        self.assertFalse(self.graph_adapter.graph.has_edge('2', '1'))


if __name__ == '__main__':
    unt.main(verbosity=2)
