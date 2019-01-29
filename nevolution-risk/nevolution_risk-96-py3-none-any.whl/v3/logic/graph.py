import os

import networkx as nx

from nevolution_risk.constants.colors import green, blue, deepskyblue
from nevolution_risk.v3.logic.continent import Continent
from nevolution_risk.v3.logic.continent_loader import ContinentLoader
from nevolution_risk.v3.logic.graphlogic import GraphLoader, RiskGraph
from nevolution_risk.v3.logic.node import Node
from nevolution_risk.v3.logic.player import Player


class Graph(object):

    def __init__(self, player_positions, player_count):
        self.player_count = player_count
        self.current_player = 0
        loader = GraphLoader()
        dir_name = os.path.dirname(os.path.realpath(__file__))
        source_graph = loader.load_graph(os.path.join(dir_name, '../../res', 'small.txt'))
        self.graph = RiskGraph(graph=source_graph[0], coord=source_graph[1])
        self.nodes = []
        self.conq_list = []
        for n in range(0, self.graph.node_count):
            self.add_node(Node(n, self.graph.get_attributes(n)))

        for n in range(0, self.graph.node_count):
            for m in self.graph.get_adjlist()[n]:
                self.nodes[n].add_node_to_list(self.nodes[m])
                self.nodes[m].add_node_to_list(self.nodes[n])

        continents = ContinentLoader().load_continents(os.path.join(dir_name, '../../res', 'continents.txt'))
        self.continents = []
        n = 0
        countries = []
        for continent in continents:
            for country in continent:
                countries.append(self.nodes[country])
            Continent(n, countries)
            self.continents.append(Continent(n, countries)
                                   )
            countries = []
            n = n + 1

        edges = []
        for line in nx.generate_edgelist(self.graph):
            edges.append(line)
        edge_count = len(edges)
        action_len = edge_count * 4 + 1

        self.players = []
        self.players.append(Player('player_one', 120, green, action_len))
        self.players.append(Player("player_two", 120, deepskyblue, action_len))

        self.set_player_start(player_positions[0], 0)
        self.set_player_start(player_positions[1], 1)

    def add_node(self, node):
        self.nodes.append(node)

    def set_player_start(self, node, player):
        if player == 0:
            self.nodes[node].player = self.players[0]
            self.nodes[node].troops = 5
            self.nodes[node].start_position = True
            self.nodes[node].start_player = self.players[0]
        elif player == 1:
            self.nodes[node].player = self.players[1]
            self.nodes[node].troops = 1
            self.nodes[node].start_position = True
            self.nodes[node].start_player = self.players[1]

    def next_player(self):
        if self.current_player + 1 >= self.player_count:
            self.add_troops()

        self.current_player = (self.current_player + 1) % self.player_count

    def add_troops(self):
        for node in self.nodes:
            if node.start_position:
                if node.troops < 5:
                    node.troops = node.troops + 1

        for continent in self.continents:
            var = 0
            current_player = continent.nodes[0].player
            for node in continent.nodes:
                if node.player == current_player:
                    var = var + 1
            if var == len(continent.nodes):
                continent.reward()

    def is_conquered(self):
        self.conq_list.clear()
        for node in self.nodes:
            if node.player.name == 'default':
                self.conq_list.append('default')
            elif node.player == self.players[0]:
                self.conq_list.append(self.players[0])
            elif node.player == self.players[1]:
                self.conq_list.append(self.players[1])

        if self.players[0] not in self.conq_list:
            # print("Player", self.players[0].name, "got conquered!")
            return True
        elif self.players[1] not in self.conq_list:
            # print("Player", self.players[1].name, "got conquered!")
            return True
        elif 'default' in self.conq_list:
            return False

        return True

    def move(self, v1, v2, troop_count, attacker):
        start = self.nodes[v1]
        finish = self.nodes[v2]

        if (start.troops - troop_count) < 1:
            return False
        elif attacker != start.player:
            return False
        elif attacker == finish.player:
            return self.fortify(start, finish, troop_count)
        elif attacker != finish.player:
            return self.attack(start, finish, troop_count)

        return False

    def fortify(self, start, finish, troop_count):
        if not (troop_count >= 1 and finish.troops <= 4 and start.troops >= 1):
            return False

        while troop_count >= 1 and finish.troops <= 4 and start.troops >= 1:
            finish.troops = finish.troops + 1
            troop_count = troop_count - 1
            start.troops = start.troops - 1

        return True

    def attack(self, start, finish, troop_count):
        if finish.troops == 0:
            start.troops = start.troops - troop_count
            finish.troops = troop_count
            finish.player = start.player
            return True

        if troop_count == 1 and finish.troops >= 3:
            start.troops = start.troops - 1
            finish.troops = finish.troops - 1
            return True

        if troop_count == 1 and finish.troops == 2:
            start.troops = start.troops - 1
            finish.troops = finish.troops - 1
            return True

        if troop_count == 1 and start.troops >= 2 and finish.troops == 1:
            start.troops = start.troops - 1
            return True

        if troop_count == 2 and finish.troops >= 3:
            start.troops = start.troops - 2
            finish.troops = finish.troops - 2
            return True

        if troop_count == 2 and finish.troops == 1:
            start.troops = start.troops - 2
            finish.player = start.player
            return True

        if troop_count == 2 and finish.troops == 2:
            start.troops = start.troops - 2
            finish.troops = finish.troops - 1
            return True

        return False


if __name__ == '__main__':
    graph = Graph((1, 8), 2)
    for node in graph.nodes:
        print(node.x, node.y)
