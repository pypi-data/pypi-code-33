import pi._requires.six


class DictType(dict):
    def __init__(self, init):
        for k, v in pi._requires.six.iteritems(init):
            self[k] = v
