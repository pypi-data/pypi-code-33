from pointwise import GlyphClient
from pointwise.glyphapi import *
import testutil

import os, sys, unittest

class TestUtilities(testutil.TestBase):
    def testArraysAndLists(self):
        self.assertEqual(self.glf.eval("set a(x) 1; set a(y) 2; array get a"), "x 1 y 2")
        gc = GlyphObj("None", self.glf)
        self.assertEqual(gc._evalTclVar('a'), {'x': [1], 'y': [2]})
        self.assertEqual(self.glf.eval("set b [list 10 11 12]"), "10 11 12")
        self.assertEqual(gc._evalTclVar('b'), [10, 11, 12])
        self.assertEqual(self.glf.eval("set c [list 20]"), "20")
        self.assertEqual(gc._evalTclVar('c'), 20)
        self.assertEqual(self.glf.eval("set c { 20 }"), " 20 ")
        self.assertEqual(gc._evalTclVar('c'), 20)
        self.assertEqual(self.glf.eval("set c \"{ 20 }\""), "{ 20 }")
        self.assertEqual(gc._evalTclVar('c'), [20])

    def testVec2(self):
        with self.assertRaises(ValueError):
            v0 = Vector2((1))
        with self.assertRaises(ValueError):
            v0 = Vector2(1)
        with self.assertRaises(ValueError):
            v0 = Vector2((1, 1, 1))
        v0 = Vector2()
        self.assertEqual(tuple(v0), (0, 0))
        v1 = Vector2((1, 1))
        self.assertEqual(tuple(v1), (1, 1))
        v1 = Vector2(1, 1)
        self.assertEqual(tuple(v1), (1, 1))
        self.assertEqual(str(v1), "(1.0, 1.0)")
        v2 = Vector2((2, 4))
        self.assertEqual(tuple(v2), (2, 4))
        self.assertEqual(tuple(v2 * v1), tuple(v2))
        v3 = v1 / 2.0
        self.assertEqual(tuple(v3), (0.5, 0.5))
        v3 *= 2.0
        self.assertEqual(tuple(v3), tuple(v1))
        v3 -= v1
        self.assertEqual(tuple(v3), tuple(Vector2()))
        self.assertEqual(v3.index(0), 0.0)
        self.assertEqual(v3.index(1), 0.0)
        self.assertEqual(v3.x, 0.0)
        self.assertEqual(v3.y, 0.0)
        v3.x = 1.0
        v3.y = 1.0
        self.assertEqual(tuple(v3), tuple(Vector2((1.0, 1.0))))
        self.assertTrue(v3.equal(Vector2((1.0, 1.0))))
        self.assertTrue(v3.notEqual(v2))
        self.assertEqual(v3.add(v2), (3, 5))
        self.assertEqual(v3.add((6, 8)), (7, 9))
        self.assertEqual(v3.subtract((2, 2)), (-1, -1))
        self.assertEqual(v3.negate(), (-1, -1))
        self.assertEqual(v3.scale(2), (2, 2))
        self.assertEqual(v3.divide(2), (0.5, 0.5))
        self.assertEqual(v3.multiply((3, 3)), (3, 3))
        self.assertEqual(v3.dot(v2), 6.0)
        for c in v3.normalize(): self.assertAlmostEqual(c, 1/math.sqrt(2))
        self.assertAlmostEqual(v3.length(), math.sqrt(2))
        self.assertEqual(Vector2.minimum(v3, v2), v3)
        self.assertEqual(Vector2.maximum(v3, v2), v2)

    def testVec3(self):
        with self.assertRaises(ValueError):
            v0 = Vector3((1))
        with self.assertRaises(ValueError):
            v0 = Vector3(1)
        with self.assertRaises(ValueError):
            v0 = Vector3((1, 1))
        with self.assertRaises(ValueError):
            v0 = Vector3(1, 1)
        with self.assertRaises(ValueError):
            v0 = Vector3((1, 1, 1, 1))
        with self.assertRaises(ValueError):
            v0 = Vector3(1, 1, 1, 1)
        v1 = Vector3((1, 1, 1))
        self.assertEqual(tuple(v1), (1, 1, 1))
        v1 = Vector3(1, 1, 1)
        self.assertEqual(tuple(v1), (1, 1, 1))
        self.assertEqual(str(v1), "(1.0, 1.0, 1.0)")
        v2 = Vector3((2, 4, 6))
        self.assertEqual(tuple(v2), (2, 4, 6))
        self.assertEqual(tuple(v2 * v1), tuple(v2))
        v3 = v1 / 2.0
        self.assertEqual(tuple(v3), (0.5, 0.5, 0.5))
        v3 *= 2.0
        self.assertEqual(tuple(v3), tuple(v1))
        v3 -= v1
        self.assertEqual(tuple(v3), tuple(Vector3()))
        self.assertEqual(v3.index(0), 0.0)
        self.assertEqual(v3.index(1), 0.0)
        self.assertEqual(v3.index(2), 0.0)
        self.assertEqual(v3.x, 0.0)
        self.assertEqual(v3.y, 0.0)
        self.assertEqual(v3.z, 0.0)
        v3.x = 1.0
        v3.y = 1.0
        v3.z = 1.0
        self.assertEqual(v3, Vector3((1.0, 1.0, 1.0)))
        self.assertTrue(v3.equal(Vector3((1.0, 1.0, 1.0))))
        self.assertTrue(v3.notEqual(v2))
        self.assertEqual(v3.add(v2), (3, 5, 7))
        self.assertEqual(v3.add((6, 8, 10)), (7, 9, 11))
        self.assertEqual(v3.subtract((2, 2, 2)), (-1, -1, -1))
        self.assertEqual(v3.negate(), (-1, -1, -1))
        self.assertEqual(v3.scale(2), (2, 2, 2))
        self.assertEqual(v3.divide(2), (0.5, 0.5, 0.5))
        self.assertEqual(v3.multiply((3, 3, 3)), (3, 3, 3))
        self.assertEqual(v3.dot(v2), 12.0)
        for c in v3.normalize(): self.assertAlmostEqual(c, 1/math.sqrt(3))
        self.assertAlmostEqual(v3.length(), math.sqrt(3))
        self.assertEqual(Vector3.minimum(v3, v2), v3)
        self.assertEqual(Vector3.maximum(v3, v2), v2)
        self.assertEqual(Vector3((1, 0, 0)).cross((Vector3((0, 1, 0)))), (0, 0, 1))
        self.assertEqual(Vector3((0, 1, 0)).cross((Vector3((1, 0, 0)))), (0, 0, -1))
        self.assertEqual(Vector3((1, 0, 0)).cross((Vector3((0, 0, 1)))), (0, -1, 0))
        self.assertEqual(Vector3((0, 0, 1)).cross((Vector3((1, 0, 0)))), (0, 1, 0))
        self.assertEqual(Vector3((0, 1, 0)).cross((Vector3((0, 0, 1)))), (1, 0, 0))
        self.assertEqual(Vector3((0, 0, 1)).cross((Vector3((0, 1, 0)))), (-1, 0, 0))
        self.assertEqual(tuple(v3.cross(v2)), (2, -4, 2))
        self.assertEqual(v3.distanceToLine((0, 0, 0), (0, 0, 1)), math.sqrt(2))
        self.assertEqual(Vector3.affine(0.5, (1, 0, 0), (2, 0, 0)), (1.5, 0, 0))
        self.assertAlmostEqual(Vector3.barycentric((0.25,0.25,0.5), (2,0,0), (0,2,0), (0,0,2)), (.375,.375,.25))

    def testPlane(self):
        p = Plane(normal=(0, 0, 1), origin=(0, 0, 0))
        self.assertEqual(tuple(p), (0, 0, 1, 0))
        self.assertEqual(p.A, 0)
        self.assertEqual(p.B, 0)
        self.assertEqual(p.C, 1)
        self.assertEqual(p.D, 0)
        self.assertEqual(p.constant(), 0)
        self.assertEqual(p.equation(), (0, 0, 1, 0))
        p = Plane(normal=(0, 1, 1), origin=(-5, -5, -5))
        self.assertEqual(p.equation(), (0, 1.0/math.sqrt(2), 1.0/math.sqrt(2), -10/math.sqrt(2)))
        self.assertEqual(p.normal(), (0, 1/math.sqrt(2), 1/math.sqrt(2)))
        self.assertEqual(p.constant(), -10/math.sqrt(2))
        p = Plane(p1=(0, 0, 2), p2=(1, 0, 2), p3=(0, 1, 2))
        self.assertEqual(p.equation(), (0, 0, 1, 2))
        self.assertTrue(p.inHalfSpace((10, 10, 10)))
        self.assertFalse(p.inHalfSpace((10, 10, -10)))
        self.assertEqual(p.line((10, 10, 10), (0, 0, 1)), (10, 10, 2))
        self.assertEqual(p.segment((10, 10, 10), (10, 10, -11)), (10, 10, 2))

        with self.assertRaises(ValueError):
            p.line((10, 10, 10), (1, 0, 0))
        with self.assertRaises(ValueError):
            p.segment((10, 10, 10), (0, 0, 10))

        p = Plane(A=1, B=0, C=0, D=10)
        self.assertEqual(p.equation(), (1, 0, 0, 10))
        self.assertEqual(p.project((0, 0, 0)), (10, 0, 0))

    def testQuat(self):
        self.assertEqual(tuple(Quaternion()), (0, 0, 0, 0))
        self.assertEqual(tuple(Quaternion((0, 0, 0), 0)), (0, 0, 0, 0))
        q = Quaternion((0, 0, 1), 90)
        for k1,k2 in zip(tuple(q),(0,0,1,90)): self.assertAlmostEqual(k1, k2)
        self.assertAlmostEqual(q.axis, (0, 0, 1))
        self.assertAlmostEqual(q.angle, 90.0)
        self.assertTrue(q.equal(Quaternion(_quat=q.quat_)))
        self.assertTrue(q.notEquals(Quaternion()))
        qr = q.rotate(Quaternion((0, 0, 1), 90))
        self.assertAlmostEqual(q.norm(), 1.0)
        for k1,k2 in zip(tuple(qr),(0,0,1,180)): self.assertAlmostEqual(k1, k2)
        qr = q.rotate(Quaternion((1, 0, 0), 90))
        for k1,k2 in zip(tuple(qr),(0.577350269,-0.577350269,0.577350269,120)): self.assertAlmostEqual(k1, k2)
        qr = qr.inverse()
        for k1,k2 in zip(tuple(qr),(-0.577350269,0.577350269,-0.577350269,120)): self.assertAlmostEqual(k1, k2)
        for k1,k2 in zip(tuple(qr),tuple(qr.normalize())): self.assertAlmostEqual(k1, k2)

    def testXform(self):
        eye = Transform.identity()
        self.assertEqual(eye, (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
        self.assertEqual(eye, tuple(Transform()))

        t1 = eye.translate((1, 2, 3))
        self.assertEqual(tuple(t1), ((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 3, 1)))
        self.assertEqual(tuple(t1), tuple(Transform.translation((1, 2, 3))))

        t1 = t1.translate((-1, -1, -1))
        self.assertEqual(tuple(t1), ((1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 2, 1)))
        self.assertEqual(tuple(t1.apply((2, 2, 2))), (2, 3, 4))
        self.assertEqual(tuple(t1.applyToDirection((0, 1, 0))), (0, 1, 0))
        self.assertEqual(tuple(t1.applyToNormal((0, 1, 0))), (0, 1, 0))

        t2 = eye.rotate((0, 0, 1), 90.0)
        self.assertEqual(tuple(t2), (0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
        self.assertEqual(tuple(t2), tuple(Transform.rotation((0, 0, 1), 90)))
        self.assertEqual(tuple(t2.apply((10, 10, 0))), (-10, 10, 0))
        self.assertEqual(tuple(t2.applyToDirection((1, 0, 0))), (0, 1, 0))
        self.assertEqual(tuple(t2.applyToNormal((1, 0, 0))), (0, 1, 0))

        t3 = eye.rotate((0, 0, 1), 90.0, (5, 5, 0))
        self.assertEqual(tuple(t3), (0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1, 0, 10, 0, 0, 1))
        self.assertEqual(tuple(t3), tuple(Transform.rotation((0, 0, 1), 90, (5, 5, 0))))
        self.assertEqual(tuple(t3.apply((10, 10, 0))), (0, 10, 0))
        self.assertEqual(tuple(t3.applyToDirection((1, 0, 0))), (0, 1, 0))
        self.assertEqual(tuple(t3.applyToNormal((1, 0, 0))), (0, 1, 0))
        self.assertEqual(tuple(t3.applyToPlane(Plane(origin=(10, 0, 0), normal=(1, 0, 0)))), (0, 1, 0, 10))

        self.assertEqual(tuple(Transform.identity().scale((2, 4, 6))), tuple(Transform.scaling((2, 4, 6))))

        t4 = t3.scale((2, 2, 4))
        self.assertEqual(tuple(t4), (0, 2, 0, 0, -2, 0, 0, 0, 0, 0, 4, 0, 10, 0, 0, 1))
        t5 = t4.scale((1, 1, 0.5), anchor=(10, 10, 10))
        self.assertEqual(tuple(t5), (0, 2, 0, 0, -2, 0, 0, 0, 0, 0, 2, 0, 10, 0, 20, 1))
        t6 = t5.mirror((0, 1, 0), 10)
        self.assertEqual(tuple(t6), (0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, -30, 0, 20, 1))
        self.assertEqual(tuple(t6.apply((1, 1, 1))), (-28, 2, 22))

        t7 = Transform.calculatedScaling((0, 0, 0), (2, 2, 2), (4, 4, 4))
        self.assertEqual(tuple(t7), (2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1))
        t7 = Transform.calculatedScaling((10, -10, 4), (2, 2, 2), (4, 4, 4))
        for i,j in zip(tuple(t7), (0.75, 0, -0, 0, 0, 1.16666667, -0, 0, 0, 0, -0, 0, 2.5, 1.6666667, 4, 1)):
            self.assertAlmostEqual(i, j)

        t8 = Transform.ortho(1, 2, 3, 4, 5, 6)
        self.assertEqual(tuple(t8), (2, 0, 0, 0, 0, 2, 0, 0, 0, 0, -2, 0, -3, -7, -11, 1))
        t8 = Transform.perspective(1, 2, 3, 4, 5, 6)
        self.assertEqual(tuple(t8), (10, 0, 0, 0, 0, 10, 0, 0, 3, 7, -11, -1, 0, 0, -60, 0))

        self.assertEqual(tuple(Transform.identity().mirror((0, 1, 0), 5)),
                tuple(Transform.mirroring((0, 1, 0), 5)))
        tm = Transform.mirrorPlane(Plane(origin=(0, 10, 0), normal=(0, 1, 0)))
        self.assertEqual(tuple(tm), (1, -0, -0, 0, -0, -1, -0, 0, -0, -0, 1, 0, 0, 20, 0, 1))

        ts = Transform.stretching((0, 0, 0), (1, 0, 0), (3, 0, 0))
        self.assertEqual(tuple(ts), (3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
        ts = tm.stretch((2, 2, 0), (1, 0, 0), (5, 0, 0))
        self.assertEqual(tuple(ts), (-3, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 8, 20, 0, 1))
        self.assertEqual(ts.apply((7, -7, 14)), (-13, 27, 14))
        self.assertEqual(tuple(ts.apply(Vector3((7, -7, 14)))), (-13, 27, 14))
        self.assertEqual(ts.apply(Vector3(7, -7, 14)), Vector3(-13, 27, 14))

    def testBBox(self):
        bbox = Extents()
        self.assertTrue(bbox.isEmpty())
        with self.assertRaises(TypeError):
            bbox.minimum()
        with self.assertRaises(TypeError):
            bbox.maximum()
        with self.assertRaises(ValueError):
            bbox = Extents(1)
        with self.assertRaises(ValueError):
            bbox = Extents(1, 2)
        bbox = Extents(0, 0, 0)
        self.assertEqual(tuple(bbox.minimum()), (0, 0, 0))
        self.assertEqual(tuple(bbox.maximum()), (0, 0, 0))
        bbox = Extents(0, 0, 0, 1, 1, 1)
        self.assertEqual(tuple(bbox.minimum()), (0, 0, 0))
        self.assertEqual(tuple(bbox.maximum()), (1, 1, 1))
        bbox = Extents(Vector3(0, 0, 0), Vector3(1, 1, 1))
        self.assertEqual(tuple(bbox.minimum()), (0, 0, 0))
        self.assertEqual(tuple(bbox.maximum()), (1, 1, 1))
        with self.assertRaises(ValueError):
            bbox = Extents(0, 0, 0, -1, 0, 0)
        bbox = Extents().enclose(Vector3(0, 0, 0))
        self.assertEqual(tuple(bbox.minimum()), (0, 0, 0))
        self.assertEqual(tuple(bbox.maximum()), (0, 0, 0))
        bbox = bbox.enclose((1, 1, 1)).enclose((-1, -2, -3))
        self.assertEqual(tuple(bbox.minimum()), (-1, -2, -3))
        self.assertEqual(tuple(bbox.maximum()), (1, 1, 1))
        self.assertAlmostEqual(bbox.diagonal(), 5.385164807134504)
        bbox = bbox.expand(1)
        self.assertEqual(tuple(bbox.minimum()), (-2, -3, -4))
        self.assertEqual(tuple(bbox.maximum()), (2, 2, 2))
        bbox2 = Extents(-10, -10, -10, -2, -3, -4)
        self.assertTrue(bbox.isIntersecting(bbox2))
        self.assertTrue(bbox.isInside((0, 0, 0)))
        self.assertFalse(bbox2.isInside((0, 0, 0)))
        self.assertFalse(bbox2.isInside((-10, -10, -10.0000001)))
        bbox3 = bbox2.translate((9, 9, 9))
        self.assertEqual(tuple(bbox3.minimum()), (-1, -1, -1))
        self.assertEqual(tuple(bbox3.maximum()), (7, 6, 5))
        bbox3 = bbox3.rotate(Quaternion((0, 0, 1), 90))
        self.assertEqual(tuple(bbox3.minimum()), (-6, -1, -1))
        self.assertEqual(tuple(bbox3.maximum()), (1, 7, 5))

if __name__ == '__main__':
    unittest.main()
