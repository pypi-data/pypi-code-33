from abc import ABC, ABCMeta, abstractmethod
from itertools import chain

from rada_vaskiv.utils import Sorting
from rada_vaskiv.descriptors import IntDescriptor, StrDescriptor, DateDescriptor


class RadaMetaClass(ABCMeta):
    counter = 0

    def __new__(cls, name, bases, dct):
        new_dict = dict()
        for attr, value in dct.items():
            if attr == 'int_types':
                for el in dct[attr]:
                    new_dict[el] = IntDescriptor()
                    cls.counter += 1
            elif attr == 'str_types':
                for el in dct[attr]:
                    new_dict[el] = StrDescriptor()
                    cls.counter += 1
            else:
                new_dict[attr] = value

        return type.__new__(cls, name, bases, new_dict)


class Human(metaclass=RadaMetaClass):
    """This is doc"""
    int_types = ['weight', 'height']

    def __init__(self, weight, height):
        self.weight = weight
        self.height = height

    def __hash__(self):
        return hash(self.weight) + hash(self.height)

    def __eq__(self, other):
        if self.weight == other.weight and \
                self.height == other.height:
            return True
        return False


class Deputat(Human, ABC, metaclass=RadaMetaClass):
    str_types = ['surname', 'name']

    date_of_birth = DateDescriptor()

    @abstractmethod
    def __init__(self, surname, name, date_of_birth, weight, height):
        super().__init__(weight, height)
        self.surname = surname
        self.name = name
        self.date_of_birth = date_of_birth

    def __hash__(self):
        return hash(self.surname) + \
               hash(self.name) + \
               hash(self.date_of_birth)

    def __eq__(self, other):
        if self.surname == other.surname and \
                self.name == other.name and \
                self.date_of_birth == other.date_of_birth:
            return True
        return False

    def __str__(self):
        return f'{self.name} {self.surname}'


class UkraineDeputat(Deputat):
    language = 'ukrainian'

    def __init__(self, surname, name, date_of_birth, weight, height, bribe_taker):
        super().__init__(surname, name, date_of_birth, weight, height)
        self.bribe_taker = bribe_taker
        self.bribes_amount = 0

    def give_tribute(self):
        if not self.bribe_taker:
            print(f'{self} doesnt take bribes')
        else:
            bribe_amount = int(input("Entre bribe amount\n"))
            if bribe_amount > 10000:
                print("Міліція ув’язнить депутата")
            else:
                self.bribes_amount += bribe_amount


class PolandDeputat(Deputat):
    language = 'polish'

    def __init__(self, surname, name, date_of_birth, weight, height):
        super().__init__(surname, name, date_of_birth, weight, height)


class Fraction(ABC):
    name = StrDescriptor()

    @abstractmethod
    def __init__(self, name):
        self.name = name
        self.deputats = set()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __str__(self):
        return f'Name: {self.name}. Deputats: {len(self.deputats)}'

    @classmethod
    def get_deputat(cls, input_data):
        deputat = cls.deputat_class(*input_data)
        return deputat

    def add_deputat(self, deputat):
        if deputat in self.deputats:
            print(f'{deputat} already in fraction')
        else:
            self.deputats.add(deputat)

    def remove_deputat(self, deputat):
        if deputat in self.deputats:
            self.deputats.remove(deputat)
            print(f'{deputat} was removed')
        else:
            print(f'{deputat} is not in {self}')

    def print_all_deputats(self):
        sorted_list = list(self.deputats)
        sorted_list.sort(key=Sorting('name', 'surname'))
        for dep in sorted_list:
            print(dep)

    def clear(self):
        self.deputats = set()
        print(f'{self} is empty')

    def __contains__(self, deputat):
        if deputat in self.deputats:
            return True
        return False

    def __iter__(self):
        self.counter = -1
        return self

    def __next__(self):
        self.counter += 1
        if self.counter >= len(self.deputats):
            raise StopIteration()
        else:
            return list(self.deputats)[self.counter]


class UkraineFraction(Fraction):
    deputat_class = UkraineDeputat

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_all_bribe_takers(self):
        sorted_list = list(self.deputats)
        sorted_list.sort(key=Sorting('bribes_amount'))
        for dep in sorted_list:
            if dep.bribe_taker:
                print(dep)

    def get_biggest_bribe_taker(self):
        sorted_list = list(self.deputats)
        sorted_list.sort(key=Sorting('bribes_amount'))
        max_bribe_amount = sorted_list[0]
        if max_bribe_amount.bribe_taker:
            return max_bribe_amount

    @classmethod
    def get_deputat(cls):
        input_data = input('Enter surname name data_f_birth weight height bribe_taker\n'
                           'Liashko Oleh 2019-01-01 60 180 1\n')
        input_data = input_data.split()
        return super().get_deputat(input_data)


class PolandFraction(Fraction):
    """Poland Fraction"""
    deputat_class = PolandDeputat

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_deputat(cls):
        input_data = input('Enter surname name data_f_birth weight height\n'
                           'Liashko Oleh 2019-01-01 60 180\n')
        input_data = input_data.split()
        return super().get_deputat(input_data)


class VerhovnaRada(ABC):

    @abstractmethod
    def __init__(self, fraction_class):
        self.fraction_class = fraction_class
        self.fractions = set()

    def add_fraction(self):
        fraction_name = input('Enter fraction name\n')
        self.fractions.add(self.fraction_class(fraction_name))

    def remove_fraction(self):
        fraction_name = input('Enter fraction name\n')
        self.fractions.discard(self.fraction_class(fraction_name))

    def print_all_fractions(self):
        for fraction in self.fractions:
            print(fraction)
            fraction.print_all_deputats()

    def add_deputat_to_fraction(self, fraction, deputat):
        fraction.add_deputat(deputat)

    def remove_deputat_from_fraction(self, fraction, deputat):
        fraction.remove_deputat(deputat)

    def show_all_deputats(self):
        for fraction in self.fractions:
            fraction.print_all_deputats()

    def __contains__(self, fraction):
        if fraction in self.fractions:
            return True
        return False

    def __iter__(self):
        fr_iterators = [iter(fr) for fr in self.fractions]
        return chain(*fr_iterators)


class UkraineRada(VerhovnaRada):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def show_all_bribe_takers(self):
        for fraction in self.fractions:
            fraction.print_all_bribe_takers()

    def show_biggest_bribe_taker(self):
        all_deputats = set()
        for fraction in self.fractions:
            all_deputats.union(fraction.deputats)

        sorted_list = list(all_deputats)
        sorted_list.sort(key=Sorting('bribes_amount'))
        max_bribe_amount = sorted_list[0]
        if max_bribe_amount.bribe_taker:
            print(max_bribe_amount)


class PolandRada(VerhovnaRada):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)






