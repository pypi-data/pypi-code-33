from abc import ABC, abstractmethod

from rada_vaskiv.utils import load_rada, save_rada


class Console(ABC):
    
    def __init__(self, rada_class, fraction_class, deputat_class):
        self.rada_class = rada_class
        self.fraction_class = fraction_class
        self.deputat_class = deputat_class

    @abstractmethod
    def run(self):
        pass


class UkraineConsole(Console):
    db_name = 'ukraine_db.pickle'

    def run(self):
        help_text = """
              Введіть 1, щоб додати фракцію
              Введіть 2, щоб видалити фракцію
              Введіть 3, щоб очистити фракцію
              Введіть 4, щоб вивести фракції
              Введіть 5, щоб додати депутата у фракцію
              Введіть 6, щоб видалити депутата із фракції
              Введіть 7, щоб вивести список хабарників у фракції
              Введіть 8, щоб вивести список  хабарників у раді
              Введіть 9, щоб вивести найбільшого хабарника у раді
              Введіть 10, щоб вивести найбільшого хабарника у фракції.
              Введіть 11, щоб перевірити чи є дупутат у фракції
              Введіть 12, щоб перевірити чи є депутат у раді
              Введіть 13, щоб дати хабаря депутату.
              Введіть 14, щоб вивести всіх депутатів із ради.
              Введіть 0, щоб вийти із програми. 

            """
        rada = load_rada(self.db_name)
        if not rada:
            rada = self.rada_class(self.fraction_class)
        while True:
            print(help_text)
            user_input = int(input().strip())
            if user_input == 1:
                rada.add_fraction()
            elif user_input == 2:
                rada.remove_fraction()
            elif user_input == 3:
                fraction_name = input("Enter fraction name\n")
                fr = self.fraction_class(fraction_name)
                for fraction in rada.fractions:
                    if fraction.name == fr.name:
                        fraction.clear()
            elif user_input == 4:
                rada.print_all_fractions()
            elif user_input == 5:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            deputat = self.fraction_class.get_deputat()
                            fraction.add_deputat(deputat)
            elif user_input == 6:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            deputat = self.fraction_class.get_deputat()
                            fraction.remove_deputat(deputat)
            elif user_input == 7:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            fraction.print_all_bribe_takers()
            elif user_input == 8:
                rada.show_all_bribe_takers()
            elif user_input == 9:
                rada.show_biggest_bribe_taker()
            elif user_input == 10:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            print(fraction.get_biggest_bribe_taker())
            elif user_input == 11:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            deputat = self.fraction_class.get_deputat()
                            print(deputat in fraction)
            elif user_input == 12:
                deputat = self.fraction_class.get_deputat()
                print(deputat in rada)
            elif user_input == 14:
                # for fr in rada.fractions:
                #     for dep in fr.deputats:
                #         print(dep)
                for dep in rada:
                    print(dep)
            elif user_input == 0:
                save_rada(rada, self.db_name)
                break


class PolandConsole(Console):
    db_name = 'poland_db.pickle'

    def run(self):
        help_text = """
              Введіть 1, щоб додати фракцію
              Введіть 2, щоб видалити фракцію
              Введіть 3, щоб очистити фракцію
              Введіть 4, щоб вивести фракції
              Введіть 5, щоб додати депутата у фракцію
              Введіть 6, щоб видалити депутата із фракції
              Введіть 11, щоб перевірити чи є дупутат у фракції
              Введіть 12, щоб перевірити чи є депутат у раді
              Введіть 14, щоб вивести всіх депутатів із ради.
              Введіть 0, щоб вийти із програми. 

            """
        rada = load_rada(self.db_name)
        if not rada:
            rada = self.rada_class(self.fraction_class)
        while True:
            print(help_text)
            user_input = int(input().strip())
            if user_input == 1:
                rada.add_fraction()
            elif user_input == 2:
                rada.remove_fraction()
            elif user_input == 3:
                fraction_name = input("Enter fraction name\n")
                fr = self.fraction_class(fraction_name)
                for fraction in rada.fractions:
                    if fraction.name == fr.name:
                        fraction.clear()
            elif user_input == 4:
                rada.print_all_fractions()
            elif user_input == 5:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            deputat = self.fraction_class.get_deputat()
                            fraction.add_deputat(deputat)
            elif user_input == 6:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            deputat = self.fraction_class.get_deputat()
                            fraction.remove_deputat(deputat)
            elif user_input == 7:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            fraction.print_all_bribe_takers()
            elif user_input == 8:
                rada.show_all_bribe_takers()
            elif user_input == 9:
                rada.show_biggest_bribe_taker()
            elif user_input == 10:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            print(fraction.get_biggest_bribe_taker())
            elif user_input == 11:
                fraction_name = input('Enter fraction name\n')
                fr = self.fraction_class(fraction_name)
                if not fr in rada:
                    print('No such fraction in rada')
                else:
                    for fraction in rada.fractions:
                        if fraction == fr:
                            deputat = self.fraction_class.get_deputat()
                            print(deputat in fraction)
            elif user_input == 12:
                deputat = self.fraction_class.get_deputat()
                print(deputat in rada)
            elif user_input == 14:
                # for fr in rada.fractions:
                #     for dep in fr.deputats:
                #         print(dep)
                for dep in rada:
                    print(dep)
            elif user_input == 0:
                save_rada(rada, self.db_name)
                break
