from nevolution_risk.v3.logic import node


class Continent(object):

    def __init__(self, id, nodes):
        self.capital = None
        self.reward_level = 0
        self.nodes = nodes
        self.id = id

        for node in nodes:
            node.continent = self

        if self.id == 0:
            self.init(2, 4)
        elif self.id == 1:
            self.init(1, 10)
        elif self.id == 2:
            self.init(2, 17)
        elif self.id == 3:
            self.init(1, 25)
        elif self.id == 4:
            self.init(3, 30)
        elif self.id == 5:
            self.init(1, 41)

    def reward(self):
        reward = self.reward_level
        if self.capital is not None:
            for node in self.nodes:
                if node.capital:
                    while node.troops <= 4 and reward >= 1:
                        node.troops = node.troops + 1
                        reward = reward - 1

    def init(self, lvl, capital):
        self.reward_level = lvl
        self.capital = capital
        for node in self.nodes:
            if self.capital == node.id:
                node.capital = True
