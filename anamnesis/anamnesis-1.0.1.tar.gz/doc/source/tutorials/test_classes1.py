#!/usr/bin/python3

from anamnesis import AbstractAnam, register_class


class SimplePerson(AbstractAnam):

    hdf5_outputs = ['name', 'age']

    def __init__(self, name='Unknown', age=0):
        AbstractAnam.__init__(self)

        self.name = name
        self.age = age


register_class(SimplePerson)
