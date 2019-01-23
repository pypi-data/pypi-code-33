from unittest import TestCase
from reliabilly.components.data import get_query
from reliabilly.settings import Constants


class TestDataClient(TestCase):
    def test_arg_processing(self):
        offset, limit, query = get_query(offset=1, limit=4, test='jjb')
        self.assertEqual(offset, 1)
        self.assertEqual(limit, 4)
        self.assertEqual(query, {'test': 'jjb'})
        offset, limit, query = get_query(offset=1, limit=44444)
        self.assertEqual(offset, 1)
        self.assertEqual(limit, Constants.MAX_PAGE_SIZE)
