import keyword


class Namespace:

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if not _valid_attr_name(name):
                raise ValueError(f'Invalid attr name: {name!r}')

            setattr(self, name, value)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__.items())

    def __repr__(self):
        return '{' + ', '.join(f'{k!r}: {v!r}' for k, v in self) + '}'

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


def _valid_attr_name(name):
    return name.isidentifier() and not keyword.iskeyword(name)
