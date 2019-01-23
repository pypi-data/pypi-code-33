import os

import networkx as nx
import numpy as np

from nevolution_risk.constants.colors import green, blue
from nevolution_risk.v3.logic.player import Player


class GraphLoader(object):

    def __init__(self):
        pass

    def convert_to_adjm(self, adress):
        file = open(adress, 'r')
        adjm = file.read()
        file.close()
        adjm = adjm.split('\n')
        del adjm[-1]
        for x in range(0, len(adjm)):
            adjm[x] = adjm[x].split(',')
            del adjm[x][-1]
            for y in range(0, len(adjm[x])):
                adjm[x][y] = int(adjm[x][y])

        return adjm[0:-2], adjm[-2:]

    def load_graph(self, path):
        my_tuple = self.convert_to_adjm(path)
        my_graph = my_tuple[0]
        my_graph = np.array(my_graph)
        return nx.from_numpy_matrix(my_graph), my_tuple[1]


class RiskGraph(nx.Graph):
    def __init__(self, graph=None, coord=None):
        super().__init__(incoming_graph_data=graph)

        self.set_coord(coord)
        self.node_count = len(coord[0])
        self.x_coordinates = coord[0]
        self.y_coordinates = coord[1]

    def set_attribute(self, node_id, attr_name, data):
        self.nodes[node_id][attr_name] = data

    def set_coord(self, coord):
        for id in range(0, len(coord[0])):
            self.set_attribute(id, 'x', coord[0][id])
            self.set_attribute(id, 'y', coord[1][id])

    def get_attributes(self, node_id):
        return self.nodes[node_id]

    def get_adjlist(self):
        list = []

        for line in nx.generate_adjlist(self):
            line = line.split()
            adjacent = []
            for node in line:
                adjacent.append(int(float(node)))
            list.append(adjacent)
        return list


if __name__ == '__main__':
    # creating a player 120 troops and a red color
    p1 = Player('player_one', 120, green)
    p2 = Player("player_two", 120, blue)
    # creating a graphloader
    loader = GraphLoader()
    # loading a source_graph from a specific path
    dir_name = os.path.dirname(os.path.realpath(__file__))
    source_graph = loader.load_graph(os.path.join(dir_name, '../../res', 'small.txt'))
    # creating own RiskGraph from source_graph
    risk_graph = RiskGraph(graph=source_graph[0], coord=source_graph[1])
    # setting attributes: Node ID, Attributename, Data
    risk_graph.set_attribute(0, 'player', p1)
    # calling an attribute from RiskGraph, Node ID:0, Attribute Player, name from TestData()
    print(risk_graph.get_attributes(0)['player'].name)
    # get an adjlist from RiskGraph
    print(risk_graph.get_adjlist())
    print(risk_graph.get_attributes(0))
    print()
    print()
    print()
    print()
    list1 = [64, 188, 292, 64, 188, 292, 64, 188, 64, 64, 64, 188, 64, 400, 400, 524, 400, 524, 630, 630, 292, 524, 400,
             524, 400, 524, 742, 864, 961, 1061, 742, 864, 961, 961, 1061, 630, 742, 864, 864, 961, 864, 961]
    list2 = [40, 89, 89, 158, 158, 158, 246, 246, 319, 381, 477, 477, 627, 89, 158, 89, 246, 158, 89, 246, 281, 381,
             477, 477, 627, 564, 89, 89, 89, 40, 246, 381, 319, 158, 158, 381, 381, 477, 564, 564, 627, 627]
    print(list(zip(list1, list2)))
