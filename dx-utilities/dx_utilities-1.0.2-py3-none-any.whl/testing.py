# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
from unittest import TestCase


class DXTestCase(TestCase):
    """Extend assertion methods of the parent class"""

    def assertTupleAlmostEqual(self, tuple1, tuple2, msg=None, *args, **kwargs):
        """Compare tuples containing float numbers for equality within
        some tolerance prescribed in the `assertAlmostEqual` method
        of the parent class.

        :param tuple tuple1:
        :param tuple tuple2:
        :param str msg:
        :param \*args: See positional arguments in
            `TestCase.assertAlmostEqual`.
        :param \*\*kwargs: See keyword-arguments in
            `TestCase.assertAlmostEqual`.
        """
        self.assertEqual(len(tuple1), len(tuple2))
        for i in range(len(tuple1)):
            self.assertAlmostEqual(tuple1[i], tuple2[i], msg=msg, *args,
                                   **kwargs)
