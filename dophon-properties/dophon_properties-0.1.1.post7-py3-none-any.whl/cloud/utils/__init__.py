class DictObject:
    def __init__(self, d: dict):
        for k, v in d.items():
            self[k] = v

    def __setitem__(self, key, value):
        setattr(self, key, value)