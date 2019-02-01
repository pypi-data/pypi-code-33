import time

from anji_orm import Model, compute_field
from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1: int = 0

    @compute_field(expire_delay=1, cacheable=True)
    def test(self):
        self.c1 += 1
        return self.c1


class FieldComputeTest(BaseTestCase):

    def test_timed_compute(self):
        t1 = T1()
        first = t1.test
        time.sleep(2)
        second = t1.test
        self.assertEqual(first, 1)
        self.assertEqual(second, 2)
