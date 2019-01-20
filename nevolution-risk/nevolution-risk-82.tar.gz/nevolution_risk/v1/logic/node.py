from nevolution_risk.constants import colors
# from nevolution_risk.v1.logic import Graph
from nevolution_risk.v1.logic.player import Player


class Node(object):
    def __init__(self, ids):
        self.adj_list = []
        self.id = ids
        self.player = Player('default', 0, colors.white)

    def add_node_to_list(self, node):
        self.adj_list.append(node)


# if __name__ == '__main__':
#     test_list = []
#     test_player = Player('joern', 0, colors.white)
#     test_node = Node(1)
#     test_node.player = test_player
#
#     node1 = Node(1)
#     node4 = Node(4)
#     node5 = Node(5)
#     node5.add_node_to_list(node1)
#     node5.add_node_to_list(node4)
#
#     graph1 = Graph()
#     n = 1
#
#     print()
#     print(graph1.nodes[n].adj_list[0].id)
#     print(graph1.nodes[n].adj_list[1].id)
#     print(graph1.nodes[n].adj_list[2].id)
#     print()
