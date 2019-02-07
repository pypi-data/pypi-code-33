import json
import unittest

import requests

from wordpy import Word


try:
    with open('./data.json') as data_file:
        data = json.loads(data_file.read())
except FileNotFoundError:
    raw = requests.get('https://pastebin.com/raw/C904cJLK').text
    data = json.loads(raw)


class DefinitionTest(unittest.TestCase):

    def setUp(self):
        self.car = Word('car')
        self.happy = Word('happy')

    def test_definitions(self):
        self.assertEqual(data['car']['definition'], self.car.definition)
        self.assertEqual(data['happy']['definition'], self.happy.definition)
