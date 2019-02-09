class Heading:
    def __init__(self, name="", title="", location="", via="", **kwargs):
        self.name = name
        self.title = title
        self.location = location
        self.via = "fa-" + via

    def serialize(self):
        return vars(self)
