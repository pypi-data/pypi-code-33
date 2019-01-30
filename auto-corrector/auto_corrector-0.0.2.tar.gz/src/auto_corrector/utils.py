import re, os
from itertools import chain

PATH = os.path.abspath(os.path.dirname(__file__))
RE = '[A-Za-z0-9]+'

Localdict_file = open(os.path.join(PATH, "en_US_GB_CA_lower.txt"), 'r')
local_dict = Localdict_file.read().splitlines()
Global_dict_file = open(os.path.join(PATH, "Global_dict.txt"), 'r')
Global_dict = Global_dict_file.read().splitlines()
alphanumeric = re.compile('([0-9]+[a-z]+)|([0-9]+[A-Z]+)|([a-z]+[0-9]+)|([A-Z]+[0-9]+)')
symbols = re.compile('[^A-Za-z0-9\']')

def words_from_archive(filename, include_dups=False, map_case=False):
    with open(os.path.join(PATH,filename)) as f:
        words = re.findall(RE, f.read())
    if include_dups:
        return words
    elif map_case:
        return {w.lower():w for w in words}
    else:
        return set(words)

def concat(*args):
    """reversed('th'), 'e' => 'hte'"""
    try:
        return ''.join(args)
    except TypeError:
        return ''.join(chain.from_iterable(args))

class Zero(dict):
    """dict with a zero default"""

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        try:
            return super(Zero, self).__getitem__(key)
        except KeyError:
            return 0

zero_default_dict = Zero
