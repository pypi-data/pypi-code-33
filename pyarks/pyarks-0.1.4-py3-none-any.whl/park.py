class Park(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name.encode("utf-8")

    def getRides(self):
        print("This method should never be called. It serves as a base for park instances to override")
        return []