import unittest


from pipeline.tests.helpers import base_helpers as helpers

pandas_installed = False
try:
    import pandas
    pandas_installed = True
except ModuleNotFoundError:
    pass


class TestDataFramesCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestDataFramesCache, cls).setUpClass()
        cls.caches = [helpers.MC(), helpers.RC(), helpers.MMC()]

    @unittest.skipUnless(pandas_installed, 'Pandas is not installed so we cannot use it for testing.')
    def test_dataframe_cache_hits(self):
        df1 = pandas.DataFrame({i: [j for j in range(1000)] for i in range(10)})
        df2 = pandas.DataFrame({i: [j for j in range(1000)] for i in range(10)})
        for cache in self.caches:
            cache.changed_value = 500
            self.assertEqual(cache.fun_boys3(df1, 2, 3, 4, 5), 500)
            cache.changed_value = 200  # should get cached value even with dataframes that match
            self.assertEqual(cache.fun_boys3(df2, 2, 3, 4, 5), 500)

    @unittest.skipUnless(pandas_installed, 'Pandas is not installed so we cannot use it for testing.')
    def test_dataframe_cache_misses(self):
        df1 = pandas.DataFrame({i: [j for j in range(1000)] for i in range(10)})
        df2 = pandas.DataFrame({i: [j for j in range(1001)] for i in range(10)})
        for cache in self.caches:
            cache.changed_value = 500
            self.assertEqual(cache.fun_boys3(df1, 2, 3, 4, 5), 500)
            cache.changed_value = 200  # should get cached value even with dataframes that match
            self.assertEqual(cache.fun_boys3(df2, 2, 3, 4, 5), 200)
        df1 = pandas.DataFrame({i: [j for j in range(1000)] for i in range(10)})
        df2 = pandas.DataFrame({i: [j for j in list(range(500, -1, -1)) + list(range(500, -1, -1))] for i in range(10)})
        for cache in self.caches:
            cache.changed_value = 500
            self.assertEqual(cache.fun_boys3(df1, 2, 3, 4, 5), 500)
            cache.changed_value = 200  # should get cached value even with dataframes that match
            self.assertEqual(cache.fun_boys3(df2, 2, 3, 4, 5), 200)
