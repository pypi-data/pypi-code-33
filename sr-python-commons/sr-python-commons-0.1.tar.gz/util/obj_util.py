def props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']


def to_str(obj):
    return obj.__class__.__name__ + str(obj.__dict__)


def serialize(object):
    return json.dumps(object, default=lambda o: o.__dict__.values()[0])


class DataObject:
    def __str__(self):
        return to_str(self)

    def __repr__(self):
        return to_str(self)

    def dumps_json(self):
        return serialize(self)
