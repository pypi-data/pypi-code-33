from datetime import datetime


class Descriptor:
    counter = 0

    def __init_subclass__(cls, **kwargs):
        cls.counter += 1

    def __init__(self):
        self.__class__.__bases__[0].counter += 1

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)


class IntDescriptor(Descriptor):
    # def __set_name__(self, owner, name):
    #     self.name = "_" + name
    #
    # def __get__(self, instance, owner):
    #     return getattr(instance, self.name)
    def __init__(self):
        super()
        self.counter += 1

    def __set__(self, instance, value):
        assert isinstance(value, int) or isinstance(value, float)
        assert value > 10 , f"Int could not be less then 10, {value} was provided"
        setattr(instance, self.name, value)


class StringDesciptor(Descriptor):
    # def __set_name__(self, owner, name):
    #     self.name = "_"+name
    #
    # def __get__(self, instance, owner):
    #     return getattr(instance, self.name)
    def __init__(self):
        super()
        self.counter += 1

    def __set__(self, instance, value):
        value = value.strip()
        assert isinstance(value, str)
        assert len(value) > 2, f"Length of String could not be less then 2, {len(value)} was provided"
        setattr(instance, self.name, value)


class BoolDescriptor(Descriptor):
    def __init__(self):
        super()
        self.counter += 1

    def __set__(self, instance, value):
        assert isinstance(value, bool), f"{self.name} should be Boolean, {value, type(value)} was provided"
        setattr(instance, self.name, value)


class DateTimeDescriptor(Descriptor):
    # def __set_name__(self, owner, name):
    #     self.name = "_"+name
    #
    # def __get__(self, instance, owner):
    #     return getattr(instance, self.name)
    def __init__(self):
        super()
        self.counter += 1

    def __set__(self, instance, value):
        date = datetime.strptime(value, "")
        # assert value > 10, f"Value could not be lower then 10, {value} was provided"
        setattr(instance, self.name, value)
