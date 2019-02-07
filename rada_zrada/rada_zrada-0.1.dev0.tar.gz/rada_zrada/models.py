"""
  1 )  Моделюємо верховну раду. (мінімізувати використання типу list у цьому завданні).
   Створити клас Human описати наступними полями: вага, зріст  додати джентельментський набір ( __eq__, __hash__, __str__).
   Створити клас Deputat, унаслідувати його від Human, описати його наст. полями:
        прізвище, ім’я, вік, хабарник ( boolean), розмір хабаря ( не передавати в конструктор) .
   Додати джент. набір Deputat.
  1.1) Закодити метод give_tribute (дати хабар) депутату,  в якому передбачити наступне,
    якщо поле хабарник False, то надрукувати, що депутат не бере хабарів.
    Якщо True, то ввести із консолі суму хабаря.  Якщо сума більше 10000 то надрувати, “Міліція ув’язнить депутата”, якщо сума менша= 10000, то занести поле інстансу цю суму.
  1.2) Створити клас Fraction (фракція) в якому описати наст методи:
   додати депутата (вводимо із консолі),
   видалити депутата( вводимо із консолі),
   вивести всіх хабарників у фракці, ( відсортувати за хабарем - використати functor)
   вивести найбільшого хабарника у фракції,
   вивести усіх депутатів у фракції, (відсортувати за імям, прізвищем - викорисстати functor)
   очистити всю фракцію від депутатів,
   чи є депутат у фракції.
  1.3) Створити клас Верховна рада, реалізувати в ньому наст. методи:
   додати фракцію,
   видалити фракцію,
   вивести всі фракції,
   вивести конкретну фракцію,
   додати депутата до конкретної фракції,
   видалити депутата,
"""
import copy

from abc import ABC, abstractmethod
from abc import ABCMeta
from rada_zrada.utils import Sorting
from rada_zrada.utils import singleton
from rada_zrada.descriptors import IntDescriptor, StringDesciptor, BoolDescriptor


class RadaMetaClass(type):
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
                    new_dict[el] = StringDesciptor()
                    cls.counter += 1
            elif attr == 'bool_types':
                for el in dct[attr]:
                    new_dict[el] = BoolDescriptor()
                    cls.counter += 1
            else:
                new_dict[attr] = value

        return type.__new__(cls, name, bases, new_dict)


class AbstractMetaClass(ABCMeta, RadaMetaClass):
    pass


class Human(metaclass=RadaMetaClass):
    int_types = ['weight', 'height']

    def __init__(self, weight, height):
        self.weight = weight
        self.height = height

    def __str__(self):
        return f"{self.weight} {self.height}"

    def __hash__(self):
        return hash(self.weight) + hash(self.height)

    def __eq__(self, other):
        return self.weight == other.weight and self.height == other.height


class AbstractDeputy(ABC, metaclass=AbstractMetaClass):
    int_types = ["weight", "height"]
    str_types = ["first_name", "last_name", "date_of_birth"]

    @abstractmethod
    def __init__(self, first_name, last_name, date_of_birth, weight, height):
        self.weight = weight
        self.height = height
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.date_of_birth})"

    def __hash__(self):
        return hash(self.first_name) + \
               hash(self.last_name) + \
               hash(self.date_of_birth)

    def __eq__(self, other):
        return self.first_name == other.first_name and \
               self.last_name == other.last_name and \
               self.date_of_birth == other.date_of_birth

    @abstractmethod
    def sing_anthem(self):pass


class UkraineDeputy(AbstractDeputy):
    bool_types = ["bribe_taker"]

    def __init__(self, first_name, last_name, date_of_birth, weight, height, bribe_taker):
        super().__init__(first_name, last_name, date_of_birth, weight, height)
        self.bribe_taker = bribe_taker
        self.bribes_amount = 0

    # def sing_anthem(self):
    #     print("Ще не вмерла Україна")

    def give_tribute(self, bribe_amount=None):
        if self.bribe_taker:
            if not bribe_amount:
                bribe_amount = int(input("Bribe amount?\n"))
            if bribe_amount > 10000:
                print(f"Міліція ув’язнить депутата : {self}")
            else:
                self.bribes_amount += bribe_amount
        else:
            print(f"{self} doesn't take any tributes or bribes")

# class PolandDeputy(AbstractDeputy, metaclass=Rada)

class Fraction(metaclass=RadaMetaClass):
    """
        додати депутата (вводимо із консолі),
        видалити депутата( вводимо із консолі),
        вивести всіх хабарників у фракці, ( відсортувати за хабарем - використати functor)
        вивести найбільшого хабарника у фракції,
        вивести усіх депутатів у фракції, (відсортувати за імям, прізвищем - викорисстати functor)
        очистити всю фракцію від депутатів,
        чи є депутат у фракції.
    """
    str_types = ["name"]

    def __init__(self, name):
        self.name = name
        self.deputies_set = set()

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __contains__(self, item):
        if item in self.deputies_set:
            return True
        return False

    def __iter__(self):
        return iter(self.deputies_set)

    def _add_deputy(self, new_deputy):
        self.deputies_set.add(new_deputy)

    def _remove_deputy(self, deputy_to_remove):
        self.deputies_set.remove(deputy_to_remove)

    def add_deputy(self, new_deputy=None):
        if not new_deputy or not isinstance(new_deputy, Deputy):
            first_name = input()
            last_name = input()
            date_of_birth = input()
            weight = float(input())
            height = float(input())
            bribe_taker = bool(input())
            new_deputy = Deputy(first_name, last_name, date_of_birth, weight, height, bribe_taker)

        if new_deputy in self.deputies_set:
            print(f"{new_deputy} already in Fraction {self}")
        else:
            self._add_deputy(new_deputy)

    def remove_deputy(self, deputy=None):
        deputies_dict = {}
        i = 1
        if deputy:
            if isinstance(deputy, Deputy):
                if deputy in self.deputies_set:
                    self._remove_deputy(deputy)
                else:
                    print(f"{self} doesn't contain {deputy}")
            else:
                print(f"{deputy} is not instance of class Deputy")
        else:
            for deputy in self.deputies_set:
                deputies_dict[i] = deputy
                print(f"{i:3}{deputy.first_name} {deputy.last_name} ({deputy.date_of_birth})")
                i += 1
            deputy_num = input()
            if deputy_num > i:
                print("No such deputy")
                return
            self._remove_deputy(deputies_dict[deputy_num])

    def _sort_all_deputies(self, key):
        for _dep in sorted(list(self.deputies_set), key=key):
            # if _dep.bribe_taker:
            yield _dep

    def print_all_deputies(self):
        i = 1
        for _dep in self._sort_all_deputies(key=Sorting("first_name", "last_name")):
            print(f"{self} {i:2} {_dep.first_name} {_dep.last_name} ({_dep.date_of_birth})")
            i += 1

    def print_all_bribe_takers(self):
        for _dep in self._sort_all_deputies(key=Sorting("first_name", "bribes_amount")):
            if _dep.bribe_taker:
                print(_dep)

    def print_bribe_taker_with_max_bribes_amount(self):
        for _dep in self._sort_all_deputies(key=Sorting(bribes_amount=lambda x: x*-1)):
            if _dep.bribe_taker:
                print(f"bribe_taker_with_max_bribes_amount : {_dep} {_dep.bribes_amount}")

                break

    def clear(self):
        self.deputies_set = set()


@singleton
class VerhovnaRada:

    def __init__(self):
        self.fractions = set()

    def __iter__(self):
        return copy.copy(self)

    def add_fraction(self):
        fraction_name = input('Enter fraction name\n')
        self.fractions.add(Fraction(fraction_name))

    def remove_fraction(self):
        fraction_name = input('Enter fraction name\n')
        self.fractions.discard(Fraction(fraction_name))

    def print_all_fractions(self):
        for fraction in self.fractions:
            print(fraction)
            fraction.print_all_deputats()

    def add_deputat_to_fraction(self, fraction, deputat):
        fraction.add_deputat(deputat)

    def remove_deputat_fromm_fraction(self, fraction, deputat):
        fraction.remove_deputat(deputat)

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

    def show_all_deputats(self):
        for fraction in self.fractions:
            fraction.print_all_deputats()

    def __contains__(self, fraction):
        if fraction in self.fractions:
            return True
        return False

if __name__ == '__main__':
    oleg_laschko = UkraineDeputy(first_name="Oleg", last_name="L'ashko", date_of_birth="01.01.1980", weight=90, height=170, bribe_taker=True)
    julia_tymoshenko = UkraineDeputy(first_name="Julia", last_name="Tymoshenko", date_of_birth="01.01.1970", weight=90, height=170, bribe_taker=True)
    petro_poroshenko = UkraineDeputy(first_name="Petro", last_name="Poroshenko", date_of_birth="01.01.1970", weight=110, height=170, bribe_taker=True)
    semen_semenchenko = UkraineDeputy(first_name="Semen", last_name="Semenchenko", date_of_birth="01.01.1980", weight=90, height=170, bribe_taker=True)
    fraction = Fraction(name="Bribe Fraction")
    fraction.add_deputy(oleg_laschko)
    fraction.add_deputy(julia_tymoshenko)
    fraction.add_deputy(petro_poroshenko)
    fraction.add_deputy(semen_semenchenko)
    julia_tymoshenko.give_tribute(9999)
    julia_tymoshenko.give_tribute(5000)
    fraction.print_all_deputies()
    # for dep in fraction:
    #     print(f"{dep} ({dep.bribes_amount})")
    # print("bribe_taker_with_max_bribes_amount", end="")
    fraction.print_bribe_taker_with_max_bribes_amount()
    fraction.print_all_bribe_takers()
    # print(oleg_laschko in fraction)
    # print(julia_tymoshenko in fraction)
    # print("oleg" in fraction)

    # print(dir(Deputy))
    # print(Deputy.__dict__)