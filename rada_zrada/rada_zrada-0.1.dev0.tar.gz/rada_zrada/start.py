class IntDescriptor:

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        assert value > 10
        setattr(instance, self.name, value)


class DroidMeta(type):
    def __new__(typ, name, bases, dct):
        new_dict = dict()
        for key, val in dct.items():
            print(key, val)

            if key == "int_types":
                for elem in val:
                    new_dict[elem] = IntDescriptor()
            else:
                new_dict[key] = val

        return type.__new__(typ, name, bases, new_dict)


class Droid(metaclass=DroidMeta):
    int_types = ["a", "b", "c"]

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


if __name__ == '__main__':
    d1 = Droid(1, 2, 3)
