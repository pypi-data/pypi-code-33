from iso8601 import parse_date


class Counter:
    counter = 0

    def __init__(self):
        Counter.counter += 1


class IntDescriptor(Counter):

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        value = float(value)
        assert value > 0
        setattr(instance, self.name, value)


class StrDescriptor(Counter):

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        assert isinstance(value, str)
        assert len(value.strip()) > 1
        setattr(instance, self.name, value.strip())


class DateDescriptor(Counter):

    def __set_name__(self, owner, name):
        self.name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        """
        2019-01-01 19-00-01
        """
        da = parse_date(value)
        setattr(instance, self.name, da)
