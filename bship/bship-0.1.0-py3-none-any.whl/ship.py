
class Ship(object):

    def __init__(self, name, sign, size):
        self.name = name
        self.sign = sign
        self.size = size
        self.hits = 0
        self.pos = []

    def __str__(self):
        """Prints like: Y Destroyer(3).
        """
        return "{} {}({})".format(self.sign, self.name, self.size)

    def empty(self):
        """Empties the POS for a new POS.
        """
        self.pos = []
