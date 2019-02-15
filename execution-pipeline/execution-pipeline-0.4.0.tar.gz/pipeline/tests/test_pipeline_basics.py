import unittest


from pipeline.tests.helpers import base_helpers as helpers


class TestPipelineBasics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPipelineBasics, cls).setUpClass()
        cls.caches = [helpers.MC(), helpers.RC(), helpers.MMC()]

    def test_pre_execution_pipeline(self):
        a = helpers.A('sup')
        self.assertFalse(a.stored == 'sup')
        self.assertTrue(a.stored == 'this argument is always changed')

    def test_post_execution_pipeline(self):
        a = helpers.A()
        self.assertTrue(a.fun_boys(1, 2, 3, 4, 5)['added'] == 'yup')
        # print(a.fun_boys1(1, 2, 3, 4, 5))
        self.assertTrue(a.fun_boys1(1, 2, 3, 4, 5)['also_added'] == 'also yup')

    def test_error_pipeline(self):
        a = helpers.A()
        self.assertEqual(a.fun_boys2(), "Don't worry, we handled a TypeError.")  # handles TypeError
        self.assertEqual(a.fun_boys2(1, 2, 3, 4, 5), "Don't worry, we handled MyException.")  # handles FailedTestError

    def test_cache_pipeline(self):
        # pipeline will return the last value of the function call instead of the current return value.
        # (such is the nature of caching :( )

        for cache in self.caches:
            cache.changed_value = 500
            self.assertEqual(cache.fun_boys3(1, 2, 3, 4, 5), 500)
            cache.changed_value = 200
            self.assertEqual(cache.fun_boys3(1, 2, 3, 4, 5), 500)

    def test_no_cache_collision(self):
        # we have to ensure that methods across distinct classes are identified uniquely by key in a shared cache
        class1 = helpers.DistinctClass1()
        class2 = helpers.DistinctClass2()
        self.assertNotEqual(class1.avoid_collision(1), class2.avoid_collision(1))

    def test_ugly_cache_hit(self):
        ugly_arg1 = {i: i for i in range(100000)}
        ugly_arg2 = {i: i for i in range(100000)}
        for cache in self.caches:
            cache.changed_value = 500
            self.assertEqual(cache.fun_boys3(ugly_arg1, 2, 3, 4, 5), 500)
            cache.changed_value = 200  # should get cached value even with ugly_args that match
            self.assertEqual(cache.fun_boys3(ugly_arg2, 2, 3, 4, 5), 500)

    def test_ugly_cache_miss(self):
        # making sure that ugly arguments still result in correct cache miss
        ugly_arg1 = {i: i for i in range(100000)}
        ugly_arg2 = {i: i for i in range(100001)}
        for cache in self.caches:
            cache.changed_value = 500
            self.assertEqual(cache.fun_boys3(ugly_arg1, 2, 3, 4, 5), 500)
            cache.changed_value = 200  # should miss cached value even with ugly_args that don't match
            self.assertEqual(cache.fun_boys3(ugly_arg2, 2, 3, 4, 5), 200)


if __name__ == '__main__':
    unittest.main()
