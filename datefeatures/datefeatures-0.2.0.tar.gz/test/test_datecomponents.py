import unittest
from datefeatures import DateComponents
from datetime import datetime
import numpy as np


class Test_DateComponents(unittest.TestCase):

    def test1(self):
        X = np.array(datetime(2016, 1, 1)).reshape(1, -1)
        cmp = DateComponents(
            year=True, month=False, day=False,
            hour=False, minute=False, second=False)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_year'].values[0], 2016)
        self.assertEquals(Z['0_leap'].values[0], True)

    def test2a(self):
        X = np.array(datetime(2016, 4, 30)).reshape(1, -1)
        cmp = DateComponents(
            year=False, month=True, day=False,
            hour=False, minute=False, second=False)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_quarter'].values[0], 2)
        self.assertEquals(Z['0_eoq'].values[0], False)
        self.assertEquals(Z['0_month'].values[0], 4)
        self.assertEquals(Z['0_eom'].values[0], True)

    def test2b(self):
        X = np.array(datetime(2016, 3, 31)).reshape(1, -1)
        cmp = DateComponents(
            year=False, month=True, day=False,
            hour=False, minute=False, second=False)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_quarter'].values[0], 1)
        self.assertEquals(Z['0_eoq'].values[0], True)
        self.assertEquals(Z['0_month'].values[0], 3)
        self.assertEquals(Z['0_eom'].values[0], True)

    def test2c(self):
        X = np.array(datetime(2016, 3, 1)).reshape(1, -1)
        cmp = DateComponents(
            year=False, month=True, day=False,
            hour=False, minute=False, second=False)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_quarter'].values[0], 1)
        self.assertEquals(Z['0_eoq'].values[0], False)
        self.assertEquals(Z['0_month'].values[0], 3)
        self.assertEquals(Z['0_eom'].values[0], False)

    def test3a(self):
        X = np.array(datetime(2016, 1, 3)).reshape(1, -1)
        cmp = DateComponents(
            year=False, month=False, day=True,
            hour=False, minute=False, second=False)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_day'].values[0], 3)
        self.assertEquals(Z['0_week'].values[0], 53)
        self.assertEquals(Z['0_dy'].values[0], 3)
        self.assertEquals(Z['0_dw'].values[0], 6)

    def test3b(self):
        X = np.array(datetime(2016, 1, 4)).reshape(1, -1)
        cmp = DateComponents(
            year=False, month=False, day=True,
            hour=False, minute=False, second=False)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_day'].values[0], 4)
        self.assertEquals(Z['0_week'].values[0], 1)
        self.assertEquals(Z['0_dy'].values[0], 4)
        self.assertEquals(Z['0_dw'].values[0], 0)

    def test4(self):
        X = np.array(datetime(2016, 1, 1, 23, 59, 58, 12345)).reshape(1, -1)
        cmp = DateComponents(
            year=False, month=False, day=False,
            hour=True, minute=True, second=True, microsecond=True)
        Z = cmp.fit_transform(X)
        self.assertEquals(Z['0_hour'].values[0], 23)
        self.assertEquals(Z['0_min'].values[0], 59)
        self.assertEquals(Z['0_sec'].values[0], 58)
        self.assertEquals(Z['0_ms'].values[0], 12345)


# run
if __name__ == '__main__':
    unittest.main()
