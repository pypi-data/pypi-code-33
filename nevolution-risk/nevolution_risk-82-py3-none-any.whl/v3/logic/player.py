from nevolution_risk.constants.colors import white


class Player(object):
    def __init__(self, name, troops=0, color=white):
        self.name = name
        self.troops = troops
        self.color = color
