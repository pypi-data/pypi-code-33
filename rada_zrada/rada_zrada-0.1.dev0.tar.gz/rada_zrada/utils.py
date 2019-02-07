from rada_zrad.descriptors import Descriptor, IntDescriptor, StringDesciptor, BoolDescriptor


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


class Sorting:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, instance):
        values = []
        if self.args:
            for attr in self.args:
                values.append(getattr(instance, attr))
        if self.kwargs:
            for attr, func in self.kwargs.items():
                values.append(func(getattr(instance, attr)))
        return values


class DroidMeta(type):
    def __new__(typ, name, bases, dct):
        new_dict = dict()
        for key, val in dct.items():
            # print(key, val)

            if key == "int_types":
                for elem in val:
                    new_dict[elem] = IntDescriptor()
            if key == "str_types":
                for elem in val:
                    new_dict[elem] = StringDesciptor()
            else:
                new_dict[key] = val

        return type.__new__(typ, name, bases, new_dict)


class Droid(metaclass=DroidMeta):
    int_types = ["a", "b", "c"]
    str_types = ["name"]

    def __init__(self, name, a, b, c):
        self.name = name
        self.a = a
        self.b = b
        self.c = c


if __name__ == '__main__':
    d1 = Droid("r2d2", 11, 12, 13)
    print(Descriptor.counter)
