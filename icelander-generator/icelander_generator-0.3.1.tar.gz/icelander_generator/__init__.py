"""Generator for random Icelanders"""
from __future__ import unicode_literals
from builtins import object

import random
import datetime
import json
import os

from kennitala import Kennitala

from .name_scraper import NameScraper
from .address import Address

__author__ = "7oi"
__version__ = "0.3.1"
__license__ = 'MIT'


class Icelander(object):
    """The Icelander generator
    Class that contains methods to generate random icelanders and even dump them to a file
    """

    genders = ['female', 'male']
    names = {
        'female': [],
        'male': [],
    }
    address_generator = Address()

    def __init__(self):
        file_path = os.path.dirname(__file__)
        with open(os.path.join(file_path, NameScraper.DATA_FOLDER, NameScraper.NAMES_FILE), 'r') as names_file:
            self.names = json.loads(names_file.read())

    def get_first_name(self, gender='female'):
        """Generate first name for person

        Keyword Arguments:
            gender {str} -- Gender of person (default: {'female'})

        Returns:
            str -- First name for person
        """

        return random.choice(self.names[gender])[0]

    def get_last_name(self, gender='female', parent=None):
        """Generate last name for person

        Keyword Arguments:
            gender {str} -- Gender of person. (default: {'female'})
            parent {dict} -- Parent dict to derive last name from. If None a random parent name is chosen. (default: {None})

        Returns:
            str -- Last name for person
        """
        if parent is None:
            parent_name = random.choice(self.names[random.choice(self.genders)])[1]
        else:
            parent_name = [
                name
                for _nm, name in self.names[parent.get('gender')]
                if _nm == parent.get('firstname')
            ][0]
        if gender == 'male':
            return '{}son'.format(parent_name)
        return '{}dóttir'.format(parent_name)

    def get_random_person(self, gender=None, year=None, parent=None, address=None):
        """Get random person as a dict

        Keyword Arguments:
            gender {str} -- Gender of person. If None a random gender is selected. (default: {None})
            year {int} -- Birth year of person. If None a random year is selected. (default: {None})
            parent {dict} -- Parent to derive last name from. If None a random last name is selected. (default: {None})
            address {dict} -- An address to associate person with. If None a random address is selected. (default: {None})

        Returns:
            dict -- A dict with attributes for person {gender, firstname, lastname, ssn}
        """

        if year is not None:
            # Select random date in given year
            start_date = datetime.date(year, 1, 1).toordinal()
            end_date = datetime.date(year, 12, 31).toordinal()
            random_date = datetime.date.fromordinal(random.randint(start_date, end_date))
            ssn = Kennitala.generate(random_date)
        else:
            ssn = Kennitala.random()

        if gender is None:
            gender = random.choice(self.genders)

        if address is None:
            address = self.address_generator.get_random_address()
        return {
            'gender': gender,
            'firstname': self.get_first_name(gender),
            'lastname': self.get_last_name(gender, parent=parent),
            'ssn': ssn,
            'address': address
        }

    def get_random_people(self, num_people=1, gender=None, year=None, address=None):
        """Gets a list of random people

        Keyword Arguments:
            num_people {int} -- Number of people to generate. (default: {1})
            gender {str} -- Gender for people. If None a random gender is selected for each person (default: {None})
            year {int} -- Birth year for people. If None a random year is selected for each person (default: {None})

        Returns:
            list -- List of person dicts
        """

        return [
            self.get_random_person(gender=gender, year=year, address=address)
            for _i in range(num_people)
        ]

    def get_random_household(self, size=5, parents=2, place=None, po_code=None):
        """Gets random household

        Keyword Arguments:
            size {int} -- Size of household. (default: {5})
            parents {int} -- Number of parents (default: {2})
            place {str} -- Name of city/town to place them in. If None then selected randomly. (default: {None})
            po_code {str} -- Post code to place them in. If None then selected randomly. (default: {None})

        Returns:
            list -- List of household members
        """
        address = self.address_generator.get_random_address(place=place, po_code=po_code)
        curr_year = datetime.date.today().year
        ret = []
        parent = None
        parent_years_range = range(curr_year - 60, curr_year - 20)
        if parents > 0:
            parent_years = [random.choice(parent_years_range) for _i in range(parents)]
            ret.extend([
                self.get_random_person(year=year, address=address)
                for year in parent_years
            ])
            parent = ret[0] if ret else None
        else:
            # If no parents, give some random years anyway
            parent_years = [random.choice(parent_years_range) for _i in range(3)]

        num_kids = size - parents
        if num_kids > 0:
            kids_years = [
                random.choice(range(random.choice(parent_years) + 18, curr_year))
                for _i in range(num_kids)
            ]

            ret.extend([
                self.get_random_person(year=year, address=address, parent=parent)
                for year in kids_years
            ])
        return ret

    def dump_random_people_to_file(self, filename='random_people_dump.json', num_people=1, gender=None, year=None):
        """Dumps generated people to a json file

        Arguments:
            filename {str} -- Filename to dump to (default: {'random_people_dump.json'})
        """
        with open(filename, 'w') as outfile:
            json.dump(self.get_random_people(num_people, gender, year), outfile, indent=2)
