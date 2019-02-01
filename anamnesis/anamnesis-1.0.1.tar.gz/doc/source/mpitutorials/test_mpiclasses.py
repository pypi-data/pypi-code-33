#!/usr/bin/python3

from anamnesis import AbstractAnam, register_class


class ComplexPerson(AbstractAnam):

    hdf5_outputs = ['name', 'age']

    hdf5_defaultgroup = 'person'

    def __init__(self, name='Unknown', age=0):
        AbstractAnam.__init__(self)

        self.name = name
        self.age = age


register_class(ComplexPerson)


class ComplexPlace(AbstractAnam):

    hdf5_outputs = ['location']

    hdf5_defaultgroup = 'place'

    def __init__(self, location='Somewhere'):
        AbstractAnam.__init__(self)

        self.location = location


register_class(ComplexPlace)


class ComplexTrain(AbstractAnam):

    hdf5_outputs = ['destination']

    hdf5_defaultgroup = 'train'

    def __init__(self, destination='Edinburgh'):
        AbstractAnam.__init__(self)

        self.destination = destination

    def init_from_hdf5(self):
        print("ComplexTrain.init_from_hdf5")
        print("We have already set destination: {}".format(self.destination))


register_class(ComplexTrain)
