from datetime import datetime
from iso8601 import parse_date


class Counter:
    counter = 0
    def __init__(self):
        Counter.counter += 1


class IntDescriptor(Counter):
    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        assert value > 0
        assert type(value) in (int, float)
        setattr(instance, self.name, value)


class StringDescriptor(Counter):
    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        value = value.strip()
        assert len(value) > 1
        assert isinstance(value, str)
        setattr(instance, self.name, value)

class DateDescriptor (Counter):
    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        value = parse_date(value)
        assert isinstance(value, datetime)
        setattr(instance, self.name, value)





class MetaRada(type):
    counter = 0

    def __new__(cls, name, bases,dct):
        new_dict = dict()

        for key, value in dct.items():

            if key == "int_types":
                for int_type in value:
                    new_dict[int_type] = IntDescriptor()
                    cls.counter += 1
            elif key == "str_types":
                for str_type in value:
                    new_dict[str_type] = IntDescriptor()
                    cls.counter += 1
            else:
                new_dict[key] = value
        return type.__new__(cls,name,bases,new_dict)


def singleton(cls):
    instance = {}     # why not list?

    def get_instance(*args,**kwargs):
        if cls not in instance:
            instance[cls] = cls(*args,**kwargs)
        return instance[cls]
    return get_instance



# ipdb - debuger, ipdb.settrace()