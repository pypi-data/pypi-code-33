import os

import networkx as nx

from nevolution_risk.constants.colors import green, blue, deepskyblue
from nevolution_risk.v2.logic.graphlogic import GraphLoader, RiskGraph
from nevolution_risk.v2.logic.node import Node
from nevolution_risk.v2.logic.player import Player


class Graph(object):

    def __init__(self, player_positions):

        loader = GraphLoader()
        dir_name = os.path.dirname(os.path.realpath(__file__))
        source_graph = loader.load_graph(os.path.join(dir_name, '../../res', 'small.txt'))
        self.graph = RiskGraph(graph=source_graph[0], coord=source_graph[1])
        self.nodes = []
        for n in range(0, self.graph.node_count):
            self.add_node(Node(n, self.graph.get_attributes(n)))

        for n in range(0, self.graph.node_count):
            for m in self.graph.get_adjlist()[n]:
                self.nodes[n].add_node_to_list(self.nodes[m])
                self.nodes[m].add_node_to_list(self.nodes[n])

        edges = []
        for line in nx.generate_edgelist(self.graph):
            edges.append(line)
        edge_count = len(edges)
        legal_actions = edge_count * 2

        self.player1 = Player('player_one', 120, green, legal_actions)
        self.player2 = Player("player_two", 120, deepskyblue, legal_actions)

        self.nodes[player_positions[0]].player = self.player1
        self.nodes[player_positions[1]].player = self.player2
        self.players = []
        self.players.append(self.player1)
        self.players.append(self.player2)

    def add_node(self, node):
        self.nodes.append(node)

    def attack(self, v0, v1, attacker):
        attack = self.nodes[v0]
        defend = self.nodes[v1]
        if defend in attack.adj_list:
            if attack.player == attacker:
                if defend.player.name == 'default':
                    defend.player = attacker
                    return True
        return False

    def is_conquered(self):
        for v in self.nodes:
            if v.player.name == 'default':
                return False
        return True


if __name__ == '__main__':
    graph = Graph((1, 8))
    for node in graph.nodes:
        print(node.x, node.y)
