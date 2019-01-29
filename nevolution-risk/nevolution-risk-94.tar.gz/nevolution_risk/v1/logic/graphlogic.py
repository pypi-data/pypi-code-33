import networkx as nx
import numpy as np


class GraphLoader():

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
            list.append(line)
        return list


class TestData():
    def __init__(self, name, troops, color):
        self.name = name
        self.troops = troops
        self.color = color


if __name__ == '__main__':
    # creating a player 120 troops and a red color
    p1 = TestData('player_one', 120, 'red')
    # creating a graphloader
    loader = GraphLoader()
    # loading a source_graph from a specific path
    source_graph = loader.load_graph('../../res/small.txt')
    # creating own RiskGraph from source_graph
    risk_graph = RiskGraph(graph=source_graph[0], coord=source_graph[1])
    # setting attributes: Node ID, Attributename, Data
    risk_graph.set_attribute(0, 'player', p1)
    # calling an attribute from RiskGraph, Node ID:0, Attribute Player, name from TestData()
    print(risk_graph.get_attributes(0)['player'].name)
    # get an adjlist from RiskGraph
    print(risk_graph.get_adjlist())
