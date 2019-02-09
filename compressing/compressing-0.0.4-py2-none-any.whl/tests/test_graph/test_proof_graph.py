"""
Test for src/graph/proof_graph.py
"""

import unittest as unt
import pygraphviz as pgv
from graph.proof_graph import ProofGraph, NodeProofGraphError, \
    EdgeProofGraphError, NodeAttributeProofGraphError, ProofGraphError, \
    EdgeAttributeProofGraphError, WrongSettingGraphError
from graph.graph_adapter import GraphAdapter


class ProofGraphTest(unt.TestCase):

    def setUp(self):
        self.proof_graph = ProofGraph()

    def test_set_root(self):
        # Test graph with no root
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        graph.add_edge('2', '1')
        self.proof_graph.set_graph(graph)
        self.assertRaises(ProofGraphError, self.proof_graph.set_root)

        # Test graph with more than one root
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        self.proof_graph.set_graph(graph)
        self.assertRaises(ProofGraphError, self.proof_graph.set_root)

        # Test set root
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.proof_graph.set_graph(graph)
        self.assertEqual(self.proof_graph.root, '1')

    def test_set_graph(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')

        # Test graph type
        self.proof_graph.set_graph(graph)
        self.assertIsInstance(self.proof_graph.graph, GraphAdapter)

    def test_set_node_attribute(self):
        graph = GraphAdapter()
        graph.add_node('1')
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.set_node_attribute,
            node='2', attribute=ProofGraph.ANCESTOR_TARGET, value=True)

        # Test if attribute is invalid
        self.assertRaises(
            NodeAttributeProofGraphError,
            self.proof_graph.set_node_attribute,
            node='1', attribute="invalid_attribute", value=True)

        # Test node attribute
        self.proof_graph.set_node_attribute(
            '1',
            ProofGraph.LABEL,
            "test_label")
        self.assertEqual(
            self.proof_graph.graph.get_node_attribute('1', ProofGraph.LABEL),
            "test_label")

    def test_get_node_attribute(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.set_node_attribute('1', ProofGraph.LABEL, "test_label")
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_node_attribute,
            node='2', attribute=ProofGraph.LABEL)

        # Test if attribute is invalid
        self.assertRaises(
            NodeAttributeProofGraphError,
            self.proof_graph.get_node_attribute,
            node='1', attribute="invalid_attribute")

        # Test return result
        self.assertEqual(
            self.proof_graph.get_node_attribute('1', ProofGraph.LABEL),
            "test_label")

    def test_get_all_node_attributes(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.set_node_attribute('1', ProofGraph.LABEL, "test_label")
        graph.set_node_attribute('1', ProofGraph.ANCESTOR_TARGET, True)
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_all_node_attributes,
            node='2')

        # Test return result
        self.assertEqual(
            self.proof_graph.get_all_node_attributes('1'),
            {ProofGraph.LABEL: "test_label", ProofGraph.ANCESTOR_TARGET: True})

    def test_get_in_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_in_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_in_edges('1')),
            {('2', '1'), ('3', '1')})

    def test_get_out_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_out_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_out_edges('1')),
            {('1', '2'), ('1', '3')})

    def test_get_deductive_in_degree(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        graph.set_edge_attribute('2', '1', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('3', '1', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_deductive_in_degree,
            node='4')

        # Test return result
        self.assertEqual(self.proof_graph.get_deductive_in_degree('1'), 1)

    def test_get_deductive_out_degree(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        graph.set_edge_attribute('1', '2', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('1', '3', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_deductive_out_degree,
            node='4')

        # Test return result
        self.assertEqual(self.proof_graph.get_deductive_out_degree('1'), 1)

    def test_get_deductive_in_neighbors(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        graph.set_edge_attribute('2', '1', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('3', '1', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_deductive_in_neighbors,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_deductive_in_neighbors('1')),
            {'3'})

    def test_get_deductive_out_neighbors(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        graph.set_edge_attribute('1', '2', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('1', '3', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_deductive_out_neighbors,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_deductive_out_neighbors('1')),
            {'3'})

    def test_get_deductive_in_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        graph.set_edge_attribute('2', '1', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('3', '1', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_deductive_in_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_deductive_in_edges('1')),
            {('3', '1')})

    def test_get_deductive_out_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        graph.set_edge_attribute('1', '2', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('1', '3', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_deductive_out_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_deductive_out_edges('1')),
            {('1', '3')})

    def test_get_ancestor_in_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('2', '1')
        graph.add_edge('3', '1')
        graph.set_edge_attribute('2', '1', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('3', '1', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_ancestor_in_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_ancestor_in_edges('1')),
            {('2', '1')})

    def test_get_ancestor_out_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        graph.set_edge_attribute('1', '2', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('1', '3', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.get_ancestor_out_edges,
            node='4')

        # Test return result
        self.assertEqual(
            set(self.proof_graph.get_ancestor_out_edges('1')),
            {('1', '2')})

    def test_redirect_in_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_node('4')
        graph.add_edge('3', '1')
        graph.add_edge('4', '1')
        graph.set_edge_attribute('3', '1', ProofGraph.ANCESTOR, True)
        graph.set_edge_attribute('4', '1', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if some node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.redirect_in_edges,
            node_u='5', node_v='1')

        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.redirect_in_edges,
            node_u='1', node_v='5')

        # Test redirect edges without ancestor_edges
        self.proof_graph.redirect_in_edges('1', '2')

        self.assertTrue(self.proof_graph.graph.has_edge('3', '1'))
        self.assertFalse(self.proof_graph.graph.has_edge('4', '1'))

        self.assertTrue(self.proof_graph.graph.has_edge('4', '2'))

        # Test redirect edges with ancestor_edges
        self.proof_graph.redirect_in_edges('1', '2', ancestor_edges=True)

        self.assertFalse(self.proof_graph.graph.has_edge('3', '1'))

        self.assertTrue(self.proof_graph.graph.has_edge('3', '2'))

    def test_redirect_out_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_node('4')
        graph.add_edge('1', '3')
        graph.add_edge('1', '4')
        graph.set_edge_attribute('1', '3', ProofGraph.ANCESTOR, False)
        graph.set_edge_attribute('1', '4', ProofGraph.ANCESTOR, False)
        self.proof_graph.set_graph(graph)

        # Test raising exception if some node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.redirect_out_edges,
            node_u='5', node_v='1')

        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.redirect_out_edges,
            node_u='1', node_v='5')

        # Test redirect edges
        self.proof_graph.redirect_out_edges('1', '2')

        self.assertFalse(self.proof_graph.graph.has_edge('1', '3'))
        self.assertFalse(self.proof_graph.graph.has_edge('1', '4'))

        self.assertTrue(self.proof_graph.graph.has_edge('2', '3'))
        self.assertTrue(self.proof_graph.graph.has_edge('2', '4'))

    def test_remove_node(self):
        graph = GraphAdapter()
        graph.add_node('1')
        self.proof_graph.set_graph(graph)

        # Test raising exception if node is not in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.remove_node,
            node='3')

        # Test remove node
        self.proof_graph.remove_node('1')
        self.assertFalse(self.proof_graph.graph.has_node('1'))

    def test_add_ancestor_edge(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        self.proof_graph.set_graph(graph)

        # Test raising exception if node not exists in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.add_ancestor_edge,
            source='3', target='1')

        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.add_ancestor_edge,
            source='1', target='3')

        # Test raising exception with wrong setting
        self.assertRaises(
            WrongSettingGraphError,
            self.proof_graph.add_ancestor_edge,
            source='1', target='2')

        # Test ancestor edge with 'path' and 'new_color'
        self.proof_graph.add_ancestor_edge('1', '2', path=[1, 2], new_color=3)
        self.assertTrue(self.proof_graph.graph.has_edge('1', '2'))
        self.assertEqual(
            self.proof_graph.graph.get_edge_attribute('1', '2',
                                                      ProofGraph.PATH),
            [3, 1, 2])

        # Test ancestor edge with 'path'
        self.proof_graph.add_ancestor_edge('1', '2', path=[1, 2])
        self.assertTrue(self.proof_graph.graph.has_edge('1', '2'))
        self.assertEqual(
            self.proof_graph.graph.get_edge_attribute('1', '2',
                                                      ProofGraph.PATH),
            [1, 2])

        # Test ancestor edge with 'new_color'
        self.proof_graph.add_ancestor_edge('1', '2', new_color=1)
        self.assertTrue(self.proof_graph.graph.has_edge('1', '2'))
        self.assertEqual(
            self.proof_graph.graph.get_edge_attribute('1', '2',
                                                      ProofGraph.PATH),
            [1])

    def test_collapse_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        self.proof_graph.set_graph(graph)

        # Test raising exception if node not exists in the graph
        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.collapse_edges,
            node_u='4', node_v='1', target='2')

        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.collapse_edges,
            node_u='1', node_v='4', target='2')

        self.assertRaises(
            NodeProofGraphError,
            self.proof_graph.collapse_edges,
            node_u='1', node_v='2', target='4')

        # Test raising exception if edge not exists in the graph
        self.proof_graph.graph.add_edge('1', '3')

        self.assertRaises(
            EdgeProofGraphError,
            self.proof_graph.collapse_edges,
            node_u='1', node_v='2', target='3')

        # Test collapse edges
        self.proof_graph.graph.add_edge('2', '3')
        self.proof_graph.collapse_edges('1', '2', '3')

        self.assertFalse(self.proof_graph.graph.has_edge('2', '3'))
        self.assertTrue(self.proof_graph.graph.has_edge('1', '3'))
        self.assertTrue(
            self.proof_graph.graph.get_edge_attribute('1',
                                                      '3',
                                                      ProofGraph.COLLAPSED))

    def test_set_edge_attribute(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.proof_graph.set_graph(graph)

        # Test raising exception if edge not exists
        self.assertRaises(
            EdgeProofGraphError,
            self.proof_graph.set_edge_attribute,
            source='2', target='1', attribute="test_attribute", value=True)

        # Test raising exceptions if attribute is invalid
        self.assertRaises(
            EdgeAttributeProofGraphError,
            self.proof_graph.set_edge_attribute,
            source='1', target='2', attribute="test_attribute", value=True)

        # Test edge attribute
        self.proof_graph.set_edge_attribute('1', '2', ProofGraph.ANCESTOR, True)
        self.assertTrue(
            self.proof_graph.graph.get_edge_attribute('1',
                                                      '2',
                                                      ProofGraph.ANCESTOR))

    def test_get_edge_attribute(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.proof_graph.set_graph(graph)

        # Test raising exception if edge not exists
        self.assertRaises(
            EdgeProofGraphError,
            self.proof_graph.get_edge_attribute,
            source='2', target='1', attribute="test_attribute")

        # Test raising exceptions if attribute is invalid
        self.assertRaises(
            EdgeAttributeProofGraphError,
            self.proof_graph.get_edge_attribute,
            source='1', target='2', attribute="test_attribute")

        # Test edge attribute
        self.proof_graph.graph.set_edge_attribute('1',
                                                  '2',
                                                  ProofGraph.ANCESTOR,
                                                  True)
        self.assertTrue(
            self.proof_graph.get_edge_attribute('1',
                                                '2',
                                                ProofGraph.ANCESTOR))

    def test_get_all_edge_attributes(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.proof_graph.set_graph(graph)

        # Test raising exception if edge not exists
        self.assertRaises(
            EdgeProofGraphError,
            self.proof_graph.get_all_edge_attributes,
            source='2', target='1')

        # Test edge attributes
        self.proof_graph.graph.set_edge_attribute('1',
                                                  '2',
                                                  ProofGraph.PATH,
                                                  [1, 2])
        self.proof_graph.graph.set_edge_attribute('1',
                                                  '2',
                                                  ProofGraph.ANCESTOR,
                                                  False)

        self.assertEqual(
            self.proof_graph.get_all_edge_attributes('1', '2'),
            {ProofGraph.PATH: [1, 2], ProofGraph.ANCESTOR: False})

    def test_remove_edge(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_edge('1', '2')
        self.proof_graph.set_graph(graph)

        # Test raising exception if edge not exists
        self.assertRaises(
            EdgeProofGraphError,
            self.proof_graph.remove_edge,
            source='2', target='1')

        # Test remove edge
        self.proof_graph.remove_edge('1', '2')
        self.assertFalse(self.proof_graph.graph.has_edge('1', '2'))

    def test_remove_edges(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.proof_graph.set_graph(graph)

        # Test raising exception if edge not exists
        self.assertRaises(
            EdgeProofGraphError,
            self.proof_graph.remove_edge,
            source='2', target='1')

        # Test remove edge
        self.proof_graph.remove_edges([('1', '2'), ('1', '3')])
        self.assertFalse(self.proof_graph.graph.has_edge('1', '2'))
        self.assertFalse(self.proof_graph.graph.has_edge('1', '3'))

    def test_to_agraph(self):
        graph = GraphAdapter()
        graph.add_node('1')
        graph.add_node('2')
        graph.add_node('3')
        graph.add_edge('1', '2')
        graph.add_edge('1', '3')
        self.proof_graph.set_graph(graph)

        # Test return result
        self.assertIsInstance(self.proof_graph.to_agraph(), pgv.AGraph)


if __name__ == '__main__':
    unt.main()
