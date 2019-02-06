from pointwise import GlyphClient
from pointwise.glyphapi import *
import dbutil as db
import conutil as cn
import apputil as ap
import testutil

import os, sys, unittest

class TestUnsDomain(testutil.TestBase):
    def testSPR16159(self):
        pw = self.pw
        ap.loadFile(pw, "SPR16159.pw", True)
        dom = pw.GridEntity.getByName("dom-9")
        dom.initialize()

        self.assertEqual(dom.getTRexFullLayerCount(), 6)
        self.assertEqual(dom.getTRexTotalLayerCount(), 10)
        self.assertInTol(dom.getTRexCellCount(), 970, "5%")

    def testSPR12450(self):
        pw = self.pw
        ap.loadDB(pw, "SPR12450.igs", True)
        pw.Connector.setCalculateDimensionMethod("Spacing")
        pw.Connector.setCalculateDimensionSpacing(0.01)

        models = pw.Database.getAll(type="pw::Model")
        model = pw.Model.assemble(models)

        quilts = pw.Database.getAll(type="pw::Quilt")
        quilts = pw.Quilt.assemble(quilts, maximumAngle=45.0)

        self.assertEqual(len(quilts), 8)

        doms = pw.DomainUnstructured.createOnDatabase(quilts,
                parametricConnectors="Aligned")

        self.assertEqual(len(quilts), len(doms))

    def testCreate(self):
        pw = self.pw
        line = db.makeCurve(pw, [(1, 1, 0), (1, 2, 0)])
        self.assertGlyphType(line, "pw::Curve")

if __name__ == '__main__':
    unittest.main()
