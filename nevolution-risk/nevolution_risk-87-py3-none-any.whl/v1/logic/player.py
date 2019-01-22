from nevolution_risk.constants import colors


class Player(object):
    troops = 0
    color = colors.white

    def __init__(self, name, troops, color):
        self.name = name
        self.troops = troops
        self.color = color
