import unittest
from looqbox.utils.utils import *
import pandas as pd

class TestUtils(unittest.TestCase):

    def test_title_with_date(self):
        """
        Test title_with_date function
        """

        date_1 = ['2019-01-01', '2019-01-01']
        date_2 = ['2018-12-10', '2018-12-16']
        date_3 = ['2018-01-01', '2018-01-31']
        date_4 = ['2018-01-01', '2018-12-31']

        self.assertEqual('Período  dia  01/01/2019 (ter sem: 1/2019)',
                         title_with_date('Período', date_1))

        self.assertEqual('Período  de  10/12/2018 a 16/12/2018 (sem: 50 - 2018)',
                         title_with_date('Período', date_2))

        self.assertEqual('Período  de  01/01/2018 a 31/01/2018 (mês: 1/2018)',
                         title_with_date('Período', date_3))

        self.assertEqual('Período  de  01/01/2018 a 31/12/2018 (ano: 2018)',
                         title_with_date('Período', date_4))

    def test_format_cnpj(self):
        """
        Test format_cnpj function
        """

        self.assertEqual('00.100.000/0100-01',
                         format_cnpj('0100000010001'))

    def test_format_cpf(self):
        """
        Test format_cpf function
        """

        self.assertEqual('001.001.001-01',
                         format_cpf('00100100101'))

    def test_looq_format(self):
        """
        Test looq_format function
        """

        self.assertEqual('2.500,00', looq_format(2500, 'number:2'))
        self.assertEqual('2.500,0', looq_format(2500, 'number:1'))
        self.assertEqual('2.500', looq_format(2500, 'number:0'))
        self.assertEqual('85.53%', looq_format(0.8553, 'percent:2'))
        self.assertEqual('85.5%', looq_format(0.8553, 'percent:1'))
        self.assertEqual('86%', looq_format(0.8553, 'percent:0'))
        self.assertEqual('01/01/2018', looq_format(pd.to_datetime('2018-01-01'), 'date'))
        self.assertEqual('01/01/2018', looq_format(pd.to_datetime('2018-01-01'), 'Date'))
        self.assertEqual('01/01/2018 05:02:00', looq_format(pd.to_datetime('2018-01-01 05:02:00'), 'datetime'))
        self.assertEqual('01/01/2018 05:02:00', looq_format(pd.to_datetime('2018-01-01 05:02:00'), 'Datetime'))



