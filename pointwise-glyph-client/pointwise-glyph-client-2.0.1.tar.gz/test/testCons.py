from pointwise import GlyphClient
from pointwise.glyphapi import *
import dbutil as db
import conutil as cn
import testutil

import os, sys, unittest

class TestUtilities(testutil.TestBase):
    def testCon1(self):
        pw = self.pw
        pw.Application.reset()

        self.assertEqual(pw.Connector.setCalculateDimensionMethod("Spacing"), [])
        self.assertEqual(pw.Connector.setCalculateDimensionSpacing(.3), [])
        conic1 = pw.SegmentConic()
        self.assertIsInstance(conic1, GlyphObj)
        self.assertGlyphType(conic1, "pw::SegmentConic")
        conic1.addPoint((-25,8,0))
        conic1.addPoint((-8,8,0))
        conic1.setIntersectPoint((-20,20,0))
        conic2 = pw.SegmentConic()
        conic2.addPoint(conic1.getPoint(conic1.getPointCount()))
        conic2.addPoint((10,16,0))
        conic2.setShoulderPoint((8,8,0))
        con = pw.Connector()
        con.addSegment(conic1)
        con.addSegment(conic2)
        con.calculateDimension()

        self.assertEqual(con.getDimension(), 159)

        with pw.Examine("ConnectorLengthI") as ex:
            ex.addEntity(pw.Grid.getAll(type="pw::Connector"))
            ex.examine()
            self.assertAlmostEqual(ex.getAverage(), 0.29936418)

    def testCreateOnDb1(self):
        pw = self.pw
        c1 = pw.Curve()
        self.assertIsInstance(c1, GlyphObj)
        self.assertGlyphType(c1, "pw::Curve")
        c1.addSegment(pw.SegmentSpline())
        c1.getSegment(1).addPoint((0,0,0))
        c1.getSegment(1).addPoint((0,1,0))

        c2 = pw.Curve()
        c2.addSegment(pw.SegmentSpline())
        c2.getSegment(1).addPoint((1,0,0))
        c2.getSegment(1).addPoint((1,1,0))

        surf = pw.Surface()
        surf.interpolate(c1, c2)
        c1.delete()
        c2.delete()

        con = pw.Connector()
        con.addSegment(pw.SegmentSurfaceSpline())
        coord = [0.0, 0.0, surf]
        con.getSegment(1).addPoint(coord)
        con.getSegment(1).addPoint([0.5, 1.0, surf])
        con.getSegment(1).addPoint((1.0, 0.0, surf))
        con.getSegment(1).setSlope("Akima")
        con.getSegment(1).setSlopeOut(1, (0.0, 1.0))
        con.getSegment(1).setSlopeIn(3, [0.0, 1.0])
        con.setDimension(31)

    def testInitCons(self):
        pw = self.pw
        pw.Application.reset()

        line1 = db.makeCurve(pw, [(0, 0, 0), (0, 1, 0)])
        line2 = db.makeCurve(pw, [(1, 1, 0), (1, 0, 0)])
        line3 = db.makeCurve(pw, [(2, 0, 0), (2, 1, 0)])
        line4 = db.makeCurve(pw, [(3, 0, 0), (3, 1, 0)])
        cir1 = db.makeCircularArc(pw, (-5, 0, 0), (6, 0, 0), angle=180, axis=(0, 0, 1))
        cir2 = db.makeCircularArc(pw, (7, 0, 0), (10, 0, 0), angle=180, axis=(0, 0, 1))

        self.assertGlyphType(line1, "pw::Curve")

        ruled = pw.Surface()
        ruled.interpolate(line1, line2, orient="Opposite")

        swept = pw.Surface()
        swept.sweep(line1, (0, 0, 1))

        quarter_cyl = pw.Surface()
        quarter_cyl.revolve(line3, (3, 0, 0), (0, 1, 0), angle=90)

        cyl1 = pw.Surface()
        cyl1.revolve(line4, (4, 0, 0), (0, 1, 0), angle=360)

        cyl2 = pw.Surface()
        cyl2.revolve(line4, (4, 0, 0), (0, 1, 0), angle=360)
        with pw.Application.begin("Modify", [cyl2]) as modify:
            ents = modify.getEntities()
            pw.Entity.transform(Transform.rotation(axis=(1, 0, 0), angle=90, anchor=(2, 0, 0)), ents)
            modify.end()
        cyl2.setOrientation(1, 4)

        hemisphere = pw.Surface()
        hemisphere.revolve(cir1, pw.Application.getXYZ((0, 0, cir1)), (1, 0, 0), angle=180)

        sphere = pw.Surface()
        sphere.revolve(cir2, pw.Application.getXYZ((0, 0, cir2)), (1, 0, 0), angle=360)

        solid = { }
        solid['surf1'] = db.makeSquareSurface(self.pw, (0, 0, 1), (10, 10, 1))
        solid['surf2'] = db.makeSquareSurface(self.pw, (10, 0, 1), (20, 10, 1))
        solid['surf3'] = db.makeSquareSurface(self.pw, (0, 10, 1), (10, 20, 3))
        solid['surf4'] = db.makeSquareSurface(self.pw, (10, 10, 1), (20, 20, 3))
        self.assertGlyphType(solid['surf1'], "pw::Surface")

        tsurfs = pw.SurfaceTrim.createFromSurfaces(solid.values())
        solid['tsurf1'] = tsurfs[0]
        solid['tsurf2'] = tsurfs[1]
        solid['tsurf3'] = tsurfs[2]
        solid['tsurf4'] = tsurfs[3]
        self.assertGlyphType(solid['tsurf1'], "pw::SurfaceTrim")

        solid['quilt1'] = solid['tsurf1'].getQuilt()
        solid['quilt2'] = solid['tsurf2'].getQuilt()
        solid['quilt3'] = solid['tsurf3'].getQuilt()
        solid['quilt4'] = solid['tsurf4'].getQuilt()
        self.assertGlyphType(solid['quilt1'], "pw::Quilt")

        pw.Model.assemble([solid['tsurf2'].getModel(), solid['tsurf3'].getModel(), solid['tsurf4'].getModel()])
        solid['model1'] = solid['tsurf1'].getModel()
        solid['model234'] = solid['tsurf2'].getModel()
        self.assertGlyphType(solid['model1'], "pw::Model")

    def testSetPoint1(self):
        pw = self.pw
        pw.Application.reset()
        c = cn.makeCon(pw, [(0, 0, 0), (0, 1, 0), (1, 0, 0)], dim=21)
        self.assertGlyphType(c, "pw::Connector")

        details = c.getSegment(1)._dump()
       
        xyz0 = c.getXYZ(5)
        xyz1 = c.getXYZ(6)
        xyz2 = c.getXYZ(7)
        xyzn = Vector3(xyz0) + (Vector3(xyz2)-Vector3(xyz0)).scale(0.25)
        c.setPoint(6, xyzn)
        self.assertAlmostEqual(c.getPoint(5), xyz0)
        self.assertAlmostEqual(c.getPoint(6), xyzn)
        self.assertAlmostEqual(c.getPoint(7), xyz2)
        self.assertEqual(c.getSubConnectorCount(), 1)
        self.assertGlyphType(c.getDistribution(1), "pw::DistributionGeneral")
        self.assertEqual(c.getSegment(1)._dump(), details)

if __name__ == '__main__':
    unittest.main()
