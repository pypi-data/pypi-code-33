from nevolution_risk.constants import colors
from nevolution_risk.v1.logic.node import Node
from nevolution_risk.v1.logic.player import Player


class Graph(object):
    player1 = Player('joern', 0, colors.green)
    player2 = Player('heinrich', 0, colors.blue)

    def __init__(self, player_positions):
        self.nodes = []
        self.init_graph()
        self.nodes[player_positions[0]].player = self.player1
        self.nodes[player_positions[1]].player = self.player2

    def add_node(self, node):
        self.nodes.append(node)

    def init_graph(self):
        node0 = Node(0)
        node0.player.name = "void"
        node1 = Node(1)
        node2 = Node(2)
        node3 = Node(3)
        node4 = Node(4)
        node5 = Node(5)
        node6 = Node(6)
        node7 = Node(7)
        node8 = Node(8)
        node9 = Node(9)
        node10 = Node(10)

        self.add_node(node0)
        self.add_node(node1)
        self.add_node(node2)
        self.add_node(node3)
        self.add_node(node4)
        self.add_node(node5)
        self.add_node(node6)
        self.add_node(node7)
        self.add_node(node8)
        self.add_node(node9)
        self.add_node(node10)

        node1.add_node_to_list(node2)
        node1.add_node_to_list(node3)
        node1.add_node_to_list(node5)

        node2.add_node_to_list(node3)
        node2.add_node_to_list(node1)
        node2.add_node_to_list(node4)

        node3.add_node_to_list(node1)
        node3.add_node_to_list(node2)
        node3.add_node_to_list(node7)

        node4.add_node_to_list(node2)
        node4.add_node_to_list(node5)
        node4.add_node_to_list(node6)

        node5.add_node_to_list(node1)
        node5.add_node_to_list(node4)
        node5.add_node_to_list(node6)

        node6.add_node_to_list(node4)
        node6.add_node_to_list(node5)
        node6.add_node_to_list(node7)

        node7.add_node_to_list(node3)
        node7.add_node_to_list(node6)
        node7.add_node_to_list(node9)

        node8.add_node_to_list(node9)
        node8.add_node_to_list(node10)

        node9.add_node_to_list(node7)
        node9.add_node_to_list(node8)
        node9.add_node_to_list(node10)

        node10.add_node_to_list(node8)
        node10.add_node_to_list(node9)

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

# if __name__ == '__main__':
#     player1 = Player('joern', 0, colors.black)
#     graph1 = Graph()
#
#     print(graph1.nodes[4].player.name)
#     print(graph1.nodes[8].player.name)
#
#     print(graph1.attack(4, 5, player1))
#     print(graph1.attack(8, 9, player1))
#     print(graph1.is_conquered())
#
#     print(graph1.nodes[1].player.name)
