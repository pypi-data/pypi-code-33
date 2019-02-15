try:
    string_type = basestring
except NameError:
    string_type = str

class InvalidStateTransition(Exception):
    def __init__(self, current, unreachable):
        super().__init__("Invalid state transition from", current, "to", unreachable)

class AbortStateTransition(Exception):
    def __init__(self, message):
        super().__init__(message)

def wrap_with_tuple(what):
    if isinstance(what, (tuple, list)):
        return tuple(what)
    return (what,)

class State(object):
    def __init__(self, initial=False, **kwargs):
        self.initial = initial

    def __eq__(self,other):
        if isinstance(other, string_type):
            return self.name == other
        elif isinstance(other, State):
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        return not self == other


class Event(object):
    def __init__(self, **kwargs):
        self.to_state = kwargs.get('to_state', None)
        self.from_states = wrap_with_tuple(kwargs.get('from_states', tuple()))
        self.parameters = wrap_with_tuple(kwargs.get('parameters', tuple()))
        