import abc

class Placeholder(object):

    is_placeholder_object = True

    @abc.abstractmethod
    # All Placeholders must set attribute _pb
    def initialize_pb(self):
        pass

    def __init__(self):
        self.initialize_pb()

    def set_app(self, app):
        self._app = app

    def to_pb(self):
        return self._pb

    def from_pb(self, pb):
        self._pb = pb
        return self
