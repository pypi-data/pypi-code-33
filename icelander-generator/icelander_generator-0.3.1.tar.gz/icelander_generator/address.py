"""Generator for Icelandic addresses"""
from __future__ import unicode_literals
from builtins import object

import csv
import random
from os import path


class Address(object):
    """Generate icelandic addresses
    Generates random icelandic addresses from existing street names and po codes.
    House numbers are randomly generated, so they can be non-existent.
    """
    DATA_FOLDER = 'data'
    PO_CODES_FILE = 'po_codes.tsv'
    STREETS_FILE = 'streets.tsv'
    streets = []

    def __init__(self):
        self.import_streets()

    def import_streets(self):
        """Imports streets with correct place names and postcodes from tsv files
        """

        curr_dir = path.dirname(__file__)
        # Read postal codes from tsv file
        with open(path.join(curr_dir, self.DATA_FOLDER, self.PO_CODES_FILE), 'rt', encoding='utf-8') as poc_file:
            postal_codes = {
                po_code: place
                for po_code, place in csv.reader(poc_file, delimiter='\t')
            }

        # Read street names from csv file
        with open(path.join(curr_dir, self.DATA_FOLDER, self.STREETS_FILE), 'rt', encoding='utf-8') as streets:
            for po_code, street in csv.reader(streets, delimiter='\t'):
                place = postal_codes.get(po_code)
                self.streets.append((street, po_code, place))

    def get_random_address(self, place=None, po_code=None, max_num=99):
        """Generates a random street address

        Keyword Arguments:
            place {str} -- Place where to restrict address to. If None no restrictions apply. (default: {None})
            po_code {str} -- Postal code to restrict address to. If None no restrictions apply. (default: {None})
            max_num {int} -- Maximum house numbers on street. (default: {99})

        Returns:
            dict -- {nr, street, po_code, place}
        """

        house_nr = random.randint(1, max_num)
        choice = None

        if po_code is not None:
            try:
                choice = random.choice([street for street in self.streets if street[1] == po_code])
            except IndexError:
                pass
        if place is not None and choice is None:
            try:
                choice = random.choice([street for street in self.streets if street[2] == place])
            except IndexError:
                pass
        if choice is None:
            choice = random.choice(self.streets)
        return {
            'nr': house_nr,
            'street': choice[0],
            'po_code': choice[1],
            'place': choice[2]
        }
