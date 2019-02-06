from pointwise import GlyphClient
from pointwise.glyphapi import *

import os, sys, unittest

def dump(line):
    print(line)

class TestBase(unittest.TestCase):
    port_ = 0
    auth_ = None
    host_ = 'localhost'

    @classmethod
    def setUpClass(cls):
        cls.glf = GlyphClient(port=TestBase.port_, auth=TestBase.auth_, \
                host=TestBase.host_, callback=dump)
        cls.pw = cls.glf.get_glyphapi()

    @classmethod
    def tearDownClass(cls):
        cls.glf.close()

    def assertGlyphType(self, obj, gtype):
        self.assertTrue(isinstance(obj, GlyphObj))
        self.assertEqual(obj.glyphType, gtype)

    def assertEqual(self, v1, v2):
        if not isinstance(v1, (list, tuple, Vector2, Vector3)):
            super(TestBase, self).assertEqual(v1, v2)
        else:
            for i,j in zip(tuple(v1), tuple(v2)): super(TestBase, self).assertEqual(i, j)

    def assertAlmostEqual(self, v1, v2):
        if not isinstance(v1, (list, tuple, Vector2, Vector3)):
            super(TestBase, self).assertAlmostEqual(v1, v2)
        else:
            for i,j in zip(tuple(v1), tuple(v2)): super(TestBase, self).assertAlmostEqual(i, j)

    def assertInRange(self, value, minval, maxval):
        if not isinstance(value, (list, tuple)):
            value = (value,)
        if not isinstance(minval, (list, tuple)):
            minval = (minval,)
        if not isinstance(maxval, (list, tuple)):
            maxval = (maxval,)

        for i,j in zip(value,minval): self.assertGreaterEqual(i, j)
        for i,j in zip(value,maxval): self.assertLessEqual(i, j)

    def assertInTol(self, value, other, tol=None):
        if isinstance(value, (Vector2, Vector3)):
            value = tuple(value)
        elif not isinstance(value, (list, tuple)):
            value = (value,)

        if isinstance(other, (Vector2, Vector3)):
            other = tuple(other)
        elif not isinstance(other, (list, tuple)):
            other = (other,)

        if tol is None:
            tol = self.pw.Database.getSamePointTolerance()

        if isinstance(tol, float) and tol == 0.0:
            self.assertEqual(value, other)
        elif isinstance(tol, str) and tol.endswith("%"):
            tol = float(tol[0:-1]) / 100.0
            minval = tuple(map(lambda v: v - tol*v, other))
            maxval = tuple(map(lambda v: v + tol*v, other))
            self.assertInRange(value, minval, maxval)
        else:
            minval = tuple(map(lambda v: v - tol, other))
            maxval = tuple(map(lambda v: v + tol, other))
            self.assertInRange(value, minval, maxval)

