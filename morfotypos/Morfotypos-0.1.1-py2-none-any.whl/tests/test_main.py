# -*- coding: utf-8 -*-
# Copyright 2019 bitwise.solutions <https://bitwise.solutions>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randrange
from morfotypos.morfotypos import get_fds
import unittest

RANDOM_VALS = ['123', 'asdas', 'ασφ', '']


class TestMain(unittest.TestCase):

    def _get_fields(self, start, end):
        fields = {}
        for x in range(start, end + 1):
            fields[x] = RANDOM_VALS[randrange(0, len(RANDOM_VALS))]
        return fields

    def test_generate(self):
        headers = self._get_fields(1, 288)
        details = self._get_fields(288, 350)
        extra = self._get_fields(350, 360)
        fds = get_fds(headers, details, extra).encode('iso8859_7')
        # 288 is the number of the header fields
        # 62 is the number of the detail fields
        # 10 is the number of the extra fields
        # - 3 because of the header, details, extra delimeters instead of #
        self.assertEquals(fds.count('#'), 360 - 3)
        self.assertTrue('h$' in fds)
        self.assertTrue('d$' in fds)
        self.assertTrue('a$' in fds)
        self.assertEquals(fds[:fds.index('d$')].count('#'), 287)
        self.assertEquals(fds[fds.index('d$'):fds.index('a$')].count('#'), 61)
        self.assertEquals(fds[fds.index('a$'):].count('#'), 9)
