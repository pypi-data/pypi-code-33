

__all__ = ()


def update_value(value, data):

    existing = set(value.__dict__.keys())

    incoming = set(data.keys())

    outgoing = existing - incoming

    for key in outgoing:

        delattr(value, key)

    for key in incoming:

        setattr(value, key, data[key])
