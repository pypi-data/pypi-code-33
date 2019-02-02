# -*- coding: utf-8 -*-
import random
import datetime
import json
import os

from kennitala import Kennitala

from .name_scraper import NameScraper


class IcelanderGenerator(object):
    genders = ['female', 'male']
    names = {
        'female': [],
        'male': [],
    }

    def __init__(self, *args, **kwargs):
        super(IcelanderGenerator, self).__init__(*args, **kwargs)
        file_path = os.path.dirname(__file__)
        with open(os.path.join(file_path, NameScraper.NAMES_FILE), 'r') as names_file:
            self.names = json.loads(names_file.read())

    def get_first_name(self, gender='female'):
        """Generate first name for person

        Keyword Arguments:
            gender {str} -- Gender of person (default: {'female'})

        Returns:
            str -- First name for person
        """

        return random.choice(self.names[gender])[0]

    def get_last_name(self, gender='female', parent_name=None):
        """Generate last name for person

        Keyword Arguments:
            gender {str} -- Gender of person. (default: {'female'})
            parent_name {str} -- Parent's name. If None a random parent name is chosen. (default: {None})

        Returns:
            str -- Last name for person
        """
        if parent_name is None:
            parent_name = random.choice(self.names[random.choice(self.genders)])[1]
        if gender == 'male':
            return u'{}son'.format(parent_name)
        else:
            return u'{}dóttir'.format(parent_name)

    def get_random_person(self, gender=None, year=None):
        """Get random person as a dict

        Keyword Arguments:
            gender {str} -- Gender of person. If None a random gender is selected. (default: {None})
            year {int} -- Birth year of person. If None a random year is selected. (default: {None})

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
        return {
            'gender': gender,
            'firstname': self.get_first_name(gender),
            'lastname': self.get_last_name(gender),
            'ssn': ssn
        }

    def get_random_people(self, num_people=1, gender=None, year=None):
        """Gets a list of random people

        Keyword Arguments:
            num_people {int} -- Number of people to generate. (default: {1})
            gender {str} -- Gender for people. If None a random gender is selected for each person (default: {None})
            year {int} -- Birth year for people. If None a random year is selected for each person (default: {None})

        Returns:
            list -- List of person dicts
        """

        return [self.get_random_person(gender, year) for i in range(num_people)]

    def dump_random_people_to_file(self, filename='random_people_dump.json', num_people=1, gender=None, year=None):
        """Dumps generated people to a json file

        Arguments:
            filename {str} -- Filename to dump to (default: {'random_people_dump.json'})
        """
        with open(filename, 'w') as outfile:
            json.dump(self.get_random_people(num_people, gender, year), outfile, indent=2)
