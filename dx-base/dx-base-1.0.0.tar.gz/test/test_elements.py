import numbers
import unittest

from math import pi
from mathutils import Vector

from dx_base.elements import (RCSlab, RCColumn2D, ColumnDropPanel,
                              SteelReinforcement, PlanarElement)


class TestSteelReinforcement(unittest.TestCase):

    def test_area_per_unit_breadth(self):
        phi = 30.
        d = 45.
        s = 100.
        asx = SteelReinforcement.from_dimensions(phi, d, spacing=s)
        self.assertAlmostEqual(pi*phi**2/4/s, asx.Asbr)

    def test_addition(self):
        d1 = 45.
        phi1 = 30.
        s1 = 100.
        as1 = SteelReinforcement.from_dimensions(phi1, d1, spacing=s1)
        As1 = pi*phi1**2/4
        Asbr1 = As1 / s1
        d2 = 45.
        phi2 = 30.
        s2 = 100.
        as2 = SteelReinforcement.from_dimensions(phi2, d2, spacing=s2)
        As2 = pi*phi2**2/4
        Asbr2 = As2 / s2

        as12 = as1 + as2
        As12 = As1 + As2
        Asbr12 = Asbr1 + Asbr2
        self.assertAlmostEqual(as12.As, As12)
        self.assertAlmostEqual(as12.Asbr, Asbr12)
        d12 = (d1*Asbr1 + d2*Asbr2)/(Asbr1 + Asbr2)
        self.assertAlmostEqual(as12.d, d12)

        d3 = 42.
        phi3 = 30.
        s3 = 100.
        as3 = SteelReinforcement.from_dimensions(phi3, d3, spacing=s3)
        As3 = pi*phi3**2/4
        Asbr3 = As3 / s3

        as123 = as12 + as3
        As123 = As12 + As3
        Asbr123 = Asbr12 + Asbr3
        self.assertAlmostEqual(as123.As, As123)
        d123 = Asbr12*d12/Asbr123 + d3*Asbr3/Asbr123
        self.assertAlmostEqual(as123.d, d123)

        asother = as123 + 0.
        self.assertAlmostEqual(asother.As, As123)
        self.assertAlmostEqual(asother.Asbr, Asbr123)
        self.assertAlmostEqual(asother.d, d123)

    def test_raddition(self):
        d1 = 45.
        phi1 = 30.
        s1 = 100.
        as1 = SteelReinforcement.from_dimensions(phi1,  d1, spacing=s1)
        As1 = pi*phi1**2/4
        Asbr1 = As1 / s1

        asother = 0. + as1
        self.assertAlmostEqual(asother.As, As1)
        self.assertAlmostEqual(asother.Asbr, Asbr1)
        self.assertAlmostEqual(asother.d, d1)

    def test_phi(self):
        As = [314e-06, 380e-06, 28.3e-06, 804e-06]
        phi = [.020, .022, .006, .032]
        for i, Asi in enumerate(As):
            rebar = SteelReinforcement(As[i], 0.)
            with self.subTest(i=i):
                self.assertAlmostEqual(rebar.phi, phi[i])

        nbars = 4
        As = nbars * 380e-06
        rebar = SteelReinforcement(As, 0., nbars=nbars)
        self.assertEqual(rebar.phi, .022)


class TestPlanarElement(unittest.TestCase):

    def setUp(self):
        self.element = PlanarElement(thickness=10.)

    def test_thickness(self):
        self.assertAlmostEqual(self.element.thickness, 10.)

        self.element.thickness = 20.
        self.assertAlmostEqual(self.element.thickness, 20.)

    def test_material(self):
        self.assertIsNone(self.element.material)


class TestColumnDropPanel(unittest.TestCase):

    def setUp(self):
        self.column = RCColumn2D.create_rectangle_by_dimensions(1., 1.)
        self.lx = 0.5
        self.ly = 1.
        self.hH = 0.3
        self.drop_panel = ColumnDropPanel.create_as_column_offset(
                self.column, self.lx, self.hH, self.ly
                )

    def test_create_as_column_offset(self):
        self.assertIsInstance(self.drop_panel, ColumnDropPanel)
        self.assertEqual(self.drop_panel.centroid, self.column.centroid)
        self.assertAlmostEqual(self.drop_panel.height, self.hH)
        self.assertAlmostEqual(self.drop_panel.area, 6.)
        self.assertAlmostEqual(self.drop_panel.bx, 2.)
        self.assertAlmostEqual(self.drop_panel.by, 3.)

    def test_derived_properties(self):
        self.assertAlmostEqual(self.drop_panel.lx, self.lx)
        self.assertAlmostEqual(self.drop_panel.ly, self.ly)


class TestRCSlab(unittest.TestCase):

    def test_instantiation_by_factory(self):
        slab = RCSlab.create_rectangle_by_box(xymin=(0.0, 0.), xymax=(1., 1.),
                                              thickness=0.3)
        self.assertIsInstance(slab, RCSlab)
        self.assertAlmostEquals(slab.area, 1.)

    def test_add_agent(self):
        slab = RCSlab.create_rectangle_by_box(xymin=(0.0, 0.), xymax=(1., 1.),
                                              thickness=0.3)

        slab.add_agent(label='columns', agent_type=RCColumn2D, bx=0.3, by=0.3,
                       position='lower-left', origin=(0., 0.), thickness=0.4)
        slab.add_agent(label='columns', agent_type=RCColumn2D, bx=0.3, by=0.3,
                       position='lower-left', origin=(0., 0.), thickness=0.4)
        slab.add_agent(label='columns', agent_type=RCColumn2D, bx=0.3, by=0.3,
                       position='lower-left', origin=(0., 0.), thickness=0.4)

        self.assertEqual(len(slab.agents['columns']), 3)

        c = slab.agents['columns'][0]
        self.assertIsInstance(c, RCColumn2D)
        self.assertAlmostEquals(c.area, 0.09)

    def test_add_tension_bar_raw(self):
        slab = RCSlab.create_rectangle_by_box(xymin=(0.0, 0.), xymax=(1., 1.),
                                              thickness=0.3)
        # Set tension re-bar
        slab.add_tension_rebar_raw(phi=12., s=120., d=280.)
        slab.add_tension_rebar_raw(phi=16., s=120., d=295., axes='y', index=0)
        t_rebar = slab.t_rebar[0]
        self.assertAlmostEqual(t_rebar.value[0].As, pi*12.**2/4)
        self.assertAlmostEqual(t_rebar.value[1].As, pi*16.**2/4)
        self.assertAlmostEqual(t_rebar.value[0].Asbr, pi*12.**2/4/120.)
        self.assertAlmostEqual(t_rebar.value[1].Asbr, pi*16.**2/4/120.)
        self.assertAlmostEqual(t_rebar.value[0].d, 280.)
        self.assertAlmostEqual(t_rebar.value[1].d, 295.)

        # Replace tension re-bar
        slab.add_tension_rebar_raw(phi=16., s=120., d=295., axes='y', index=0,
                                   replace=True)
        self.assertAlmostEqual(t_rebar.value[0], 0.)
        self.assertAlmostEqual(t_rebar.value[1].As, pi*16.**2/4)
        self.assertAlmostEqual(t_rebar.value[1].Asbr, pi*16.**2/4/120.)
        self.assertAlmostEqual(t_rebar.value[1].d, 295.)

    def test_add_partial_rebar_raises(self):
        slab = RCSlab.create_rectangle_by_box(xymin=(0.0, 0.), xymax=(1., 1.),
                                              thickness=0.3)
        with self.assertRaises(ValueError):
            slab.add_partial_rebar(10., 100., 28., bx=10., by=1.)

    def test_add_partial_rebar(self):
        slab = RCSlab.create_rectangle_by_dimensions(
            bx=10., by=10, thickness=0.3, origin=(5., 5.)
            )
        slab.add_partial_rebar(10., 100., 28., bx=1., by=10., origin=(0.5, 5.))
        rebar = slab.rebar[0]
        self.assertAlmostEqual(rebar.geometry.area, 10.)

    def test_add_soil_pressure(self):
        slab = RCSlab.create_rectangle_by_box(xymin=(0., 0.), xymax=(1., 1.),
                                              thickness=0.)
        slab.add_soil_pressure(10.)
        self.assertAlmostEqual(slab.soil_pressure[0].value, 10.)
