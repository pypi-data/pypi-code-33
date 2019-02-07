class IntDescriptor:
    def __get__(self, instance, owner):
        return getattr(instance,self.name)

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __set__(self, instance, value):
        assert value>10
        setattr(instance,self.name,value)

class MetaDroid(type):
    def __new__(cls,name, bases,dct):
        new_dict = dict()
        for key, value in dct.items():
            if key.startwith ("_"):
                new_dict[key] = value
            elif key == "int_types":
                for int_type in value:
                    new_dict[int_type] = IntDescriptor()


        return type.__new__(cls,name,bases,new_dict)

class Droid(metaclass=MetaDroid):
    int_types= ["power","protection","height"]

    def __init__(self,power,protection,height):
        self.power = power
        self.protection = protection
        self.height = height