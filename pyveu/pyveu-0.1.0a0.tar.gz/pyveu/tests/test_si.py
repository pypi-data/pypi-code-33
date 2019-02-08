# coding=utf-8

# Copyright (C) 2018 Frank Sauerburger

import unittest
import math
import pyveu
import pyveu.si as si

class SiTestCase(unittest.TestCase):
    """
    This class implements tests for the si module. The main focus of these
    tests is physical correctness of the defined units. When the units are not
    powers-of-ten multiples of base units a reference independent from CODATA
    is used. The actual values in the package are based on scipy.constants and
    therefore CODATA.
    """

    def test_return_value(self):
        """
        Check that method create_systeme_international() returns a unit
        system, the units and the prefixes. This test does not test the
        individual returned units.
        """
        retval = si.create_systeme_international()
        self.assertEqual(len(retval), 3)

        us, prefixes, units = retval

        self.assertIsInstance(us, pyveu.UnitSystem)
        self.assertEqual(len(prefixes), 20)
        self.assertEqual(len(units), 59)

    def test_new(self):
        """
        Check that the method create_systeme_international() actually creates
        a new unit system.
        """
        us_1, units, prefixes = si.create_systeme_international()
        us_2, units, prefixes = si.create_systeme_international()

        self.assertIsNot(us_1, us_2)

    def test_metre(self):
        """
        Check the definition of the metre unit.
        """
        self.assertEqual(si.metre.label(), "Metre")
        self.assertEqual(si.metre.symbol(), "m")
        self.assertEqual(si.metre.latex(), None)
        self.assertEqual(si.metre.factor(), 1)
        self.assertEqual(list(si.metre.unit_vector()),
                         [1, 0, 0, 0, 0, 0, 0, 0])

    def test_meter(self):
        """
        Check the definition of the meter alias.
        """
        self.assertEqual(si.meter.label(), "Metre")
        self.assertEqual(si.meter.symbol(), "m")
        self.assertEqual(si.meter.latex(), None)
        self.assertEqual(si.meter.factor(), 1)
        self.assertEqual(list(si.meter.unit_vector()),
                         [1, 0, 0, 0, 0, 0, 0, 0])

    def test_kilogram(self):
        """
        Check the definition of the kilogram unit.
        """
        self.assertEqual(si.kilogram.label(), "Kilogram")
        self.assertEqual(si.kilogram.symbol(), "kg")
        self.assertEqual(si.kilogram.latex(), None)
        self.assertEqual(si.kilogram.factor(), 1)
        self.assertEqual(list(si.kilogram.unit_vector()),
                         [0, 1, 0, 0, 0, 0, 0, 0])

    def test_second(self):
        """
        Check the definition of the second unit.
        """
        self.assertEqual(si.second.label(), "Second")
        self.assertEqual(si.second.symbol(), "s")
        self.assertEqual(si.second.latex(), None)
        self.assertEqual(si.second.factor(), 1)
        self.assertEqual(list(si.second.unit_vector()),
                         [0, 0, 1, 0, 0, 0, 0, 0])

    def test_ampere(self):
        """
        Check the definition of the ampere unit.
        """
        self.assertEqual(si.ampere.label(), "Ampere")
        self.assertEqual(si.ampere.symbol(), "A")
        self.assertEqual(si.ampere.latex(), None)
        self.assertEqual(si.ampere.factor(), 1)
        self.assertEqual(list(si.ampere.unit_vector()),
                         [0, 0, 0, 1, 0, 0, 0, 0])

    def test_kelvin(self):
        """
        Check the definition of the kelvin unit.
        """
        self.assertEqual(si.kelvin.label(), "Kelvin")
        self.assertEqual(si.kelvin.symbol(), "K")
        self.assertEqual(si.kelvin.latex(), None)
        self.assertEqual(si.kelvin.factor(), 1)
        self.assertEqual(list(si.kelvin.unit_vector()),
                         [0, 0, 0, 0, 1, 0, 0, 0])

    def test_mole(self):
        """
        Check the definition of the mole unit.
        """
        self.assertEqual(si.mole.label(), "Mole")
        self.assertEqual(si.mole.symbol(), "mol")
        self.assertEqual(si.mole.latex(), None)
        self.assertEqual(si.mole.factor(), 1)
        self.assertEqual(list(si.mole.unit_vector()),
                         [0, 0, 0, 0, 0, 1, 0, 0])

    def test_candela(self):
        """
        Check the definition of the candela unit.
        """
        self.assertEqual(si.candela.label(), "Candela")
        self.assertEqual(si.candela.symbol(), "cd")
        self.assertEqual(si.candela.latex(), None)
        self.assertEqual(si.candela.factor(), 1)
        self.assertEqual(list(si.candela.unit_vector()),
                         [0, 0, 0, 0, 0, 0, 1, 0])

    def test_radian(self):
        """
        Check the definition of the radian unit.
        """
        self.assertEqual(si.radian.label(), "Radian")
        self.assertEqual(si.radian.symbol(), "rad")
        self.assertEqual(si.radian.latex(), None)
        self.assertEqual(si.radian.factor(), 1)
        self.assertEqual(list(si.radian.unit_vector()),
                         [0, 0, 0, 0, 0, 0, 0, 1])

    def assertUvEqual(self, unit_a, unit_b):
        """
        Assert that the unit vectors are equal.
        """
        self.assertEqual(list(unit_a.unit_vector()),
                         list(unit_b.unit_vector()))

    def test_gram(self):
        """
        Check the definition of the gram unit.
        """
        self.assertEqual(si.gram.label(), "Gram")
        self.assertEqual(si.gram.symbol(), "g")
        self.assertEqual(si.gram.latex(), None)
        self.assertEqual(si.gram.factor(), 0.001)
        self.assertUvEqual(si.gram, si.kilogram)

    def test_minute(self):
        """
        Check the definition of the minute unit.
        """
        self.assertEqual(si.minute.label(), "Minute")
        self.assertEqual(si.minute.symbol(), "min")
        self.assertEqual(si.minute.latex(), None)
        self.assertEqual(si.minute.factor(), 60)
        self.assertUvEqual(si.minute, si.second)

    def test_hour(self):
        """
        Check the definition of the hour unit.
        """
        self.assertEqual(si.hour.label(), "Hour")
        self.assertEqual(si.hour.symbol(), "hr")
        self.assertEqual(si.hour.latex(), None)
        self.assertEqual(si.hour.factor(), 3600)
        self.assertUvEqual(si.hour, si.second)

    def test_newton(self):
        """
        Check the definition of the newton unit.
        """
        self.assertEqual(si.newton.label(), "Newton")
        self.assertEqual(si.newton.symbol(), "N")
        self.assertEqual(si.newton.latex(), None)
        self.assertEqual(si.newton.factor(), 1)
        self.assertUvEqual(si.newton, si.kilogram * si.metre / si.second**2)

    def test_joule(self):
        """
        Check the definition of the joule unit.
        """
        self.assertEqual(si.joule.label(), "Joule")
        self.assertEqual(si.joule.symbol(), "J")
        self.assertEqual(si.joule.latex(), None)
        self.assertEqual(si.joule.factor(), 1)
        self.assertUvEqual(si.joule, si.kilogram * si.metre**2 / si.second**2)

    def test_watt(self):
        """
        Check the definition of the watt unit.
        """
        self.assertEqual(si.watt.label(), "Watt")
        self.assertEqual(si.watt.symbol(), "W")
        self.assertEqual(si.watt.latex(), None)
        self.assertEqual(si.watt.factor(), 1)
        self.assertUvEqual(si.watt, si.kilogram * si.metre**2 / si.second**3)

    def test_volt(self):
        """
        Check the definition of the volt unit.
        """
        self.assertEqual(si.volt.label(), "Volt")
        self.assertEqual(si.volt.symbol(), "V")
        self.assertEqual(si.volt.latex(), None)
        self.assertEqual(si.volt.factor(), 1)
        self.assertUvEqual(si.volt, si.kilogram * si.metre**2 / si.second**3 \
                           / si.ampere)

    def test_coulomb(self):
        """
        Check the definition of the coulomb unit.
        """
        self.assertEqual(si.coulomb.label(), "Coulomb")
        self.assertEqual(si.coulomb.symbol(), "C")
        self.assertEqual(si.coulomb.latex(), None)
        self.assertEqual(si.coulomb.factor(), 1)
        self.assertUvEqual(si.coulomb, si.ampere * si.second)

    def test_ohm(self):
        """
        Check the definition of the ohm unit.
        """
        self.assertEqual(si.ohm.label(), "Ohm")
        self.assertEqual(si.ohm.symbol(), "ohm")
        self.assertEqual(si.ohm.latex(), "\\Omega")
        self.assertEqual(si.ohm.factor(), 1)
        self.assertUvEqual(si.ohm, si.kilogram * si.metre**2 / si.second**3 \
                           / si.ampere**2)

    def test_farad(self):
        """
        Check the definition of the farad unit.
        """
        self.assertEqual(si.farad.label(), "Farad")
        self.assertEqual(si.farad.symbol(), "F")
        self.assertEqual(si.farad.latex(), None)
        self.assertEqual(si.farad.factor(), 1)
        self.assertUvEqual(si.farad, si.second**4 * si.ampere**2 \
                           / (si.metre**2 * si.kilogram**1))

    def test_henry(self):
        """
        Check the definition of the henry unit.
        """
        self.assertEqual(si.henry.label(), "Henry")
        self.assertEqual(si.henry.symbol(), "H")
        self.assertEqual(si.henry.latex(), None)
        self.assertEqual(si.henry.factor(), 1)
        self.assertUvEqual(si.henry, si.kilogram * si.metre**2 / si.second**2 \
                           / si.ampere**2)

    def test_tesla(self):
        """
        Check the definition of the tesla unit.
        """
        self.assertEqual(si.tesla.label(), "Tesla")
        self.assertEqual(si.tesla.symbol(), "T")
        self.assertEqual(si.tesla.latex(), None)
        self.assertEqual(si.tesla.factor(), 1)
        self.assertUvEqual(si.tesla, si.volt * si.second / si.metre**2)

    def test_weber(self):
        """
        Check the definition of the weber unit.
        """
        self.assertEqual(si.weber.label(), "Weber")
        self.assertEqual(si.weber.symbol(), "Wb")
        self.assertEqual(si.weber.latex(), None)
        self.assertEqual(si.weber.factor(), 1)
        self.assertUvEqual(si.weber, si.kilogram * si.metre**2 \
                           / (si.second**2 * si.ampere))

    def test_hertz(self):
        """
        Check the definition of the hertz unit.
        """
        self.assertEqual(si.hertz.label(), "Hertz")
        self.assertEqual(si.hertz.symbol(), "Hz")
        self.assertEqual(si.hertz.latex(), None)
        self.assertEqual(si.hertz.factor(), 1)
        self.assertUvEqual(si.hertz, 1 / si.second)

    def test_becquerel(self):
        """
        Check the definition of the becquerel unit.
        """
        self.assertEqual(si.becquerel.label(), "Becquerel")
        self.assertEqual(si.becquerel.symbol(), "Bq")
        self.assertEqual(si.becquerel.latex(), None)
        self.assertEqual(si.becquerel.factor(), 1)
        self.assertUvEqual(si.becquerel, 1 / si.second)

    def test_sievert(self):
        """
        Check the definition of the sievert unit.
        """
        self.assertEqual(si.sievert.label(), "Sievert")
        self.assertEqual(si.sievert.symbol(), "Sv")
        self.assertEqual(si.sievert.latex(), None)
        self.assertEqual(si.sievert.factor(), 1)
        self.assertUvEqual(si.sievert, si.joule / si.kilogram)

    def test_gray(self):
        """
        Check the definition of the gray unit.
        """
        self.assertEqual(si.gray.label(), "Gray")
        self.assertEqual(si.gray.symbol(), "Gy")
        self.assertEqual(si.gray.latex(), None)
        self.assertEqual(si.gray.factor(), 1)
        self.assertUvEqual(si.gray, si.joule / si.kilogram)

    def test_electron_volt(self):
        """
        Check the definition of the electron volt unit.
        """
        self.assertEqual(si.electron_volt.label(), "Electronvolt")
        self.assertEqual(si.electron_volt.symbol(), "eV")
        self.assertEqual(si.electron_volt.latex(), None)
        self.assertAlmostEqual(si.electron_volt.factor(),
                               1.6021766208e-19)  # [1], see references.txt
        self.assertUvEqual(si.electron_volt, si.kilogram * si.metre**2 / si.second**2)

    def test_speed_of_light(self):
        """
        Check the definition of the speed of light.
        """
        self.assertEqual(si.speed_of_light.label(), "Speed of light")
        self.assertEqual(si.speed_of_light.symbol(), "c")
        self.assertEqual(si.speed_of_light.latex(), None)
        self.assertAlmostEqual(si.speed_of_light.factor(),
                               299792458)  # [1], see references.txt
        self.assertUvEqual(si.speed_of_light, si.metre / si.second)

    def test_c(self):
        """
        Check the definition of abbreviated speed of light.
        """
        self.assertEqual(si.c.label(), "Speed of light")
        self.assertEqual(si.c.symbol(), "c")
        self.assertEqual(si.c.latex(), None)
        self.assertAlmostEqual(si.c.factor(),
                               299792458)  # [1], see references.txt
        self.assertUvEqual(si.c, si.metre / si.second)

    def test_planck_constant(self):
        """
        Check the definition of the Planck constant.
        """
        self.assertEqual(si.planck_constant.label(), "Planck constant")
        self.assertEqual(si.planck_constant.symbol(), "h")
        self.assertEqual(si.planck_constant.latex(), None)
        self.assertAlmostEqual(si.planck_constant.factor(),
                               6.626070040e-34)  # [1], see references.txt
        self.assertUvEqual(si.planck_constant, si.kilogram * si.metre**2 / si.second)

    def test_h(self):
        """
        Check the definition of abbreviated Planck constant.
        """
        self.assertEqual(si.h.label(), "Planck constant")
        self.assertEqual(si.h.symbol(), "h")
        self.assertEqual(si.h.latex(), None)
        self.assertAlmostEqual(si.h.factor(),
                               6.626070040e-34)  # [1], see references.txt
        self.assertUvEqual(si.h, si.kilogram * si.metre**2 / si.second)

    def test_h_bar(self):
        """
        Check the definition of the reduced Planck constant.
        """
        self.assertEqual(si.hbar.label(), "Reduced Planck constant")
        self.assertEqual(si.hbar.symbol(), "h_bar")
        self.assertEqual(si.hbar.latex(), "\\hbar")
        self.assertAlmostEqual(si.hbar.factor(),
                               1.054571800e-34)  # [1], see references.txt
        self.assertUvEqual(si.hbar, si.kilogram * si.metre**2 / si.second)

    def test_pascal(self):
        """
        Check the definition of the pascal unit.
        """
        self.assertEqual(si.pascal.label(), "Pascal")
        self.assertEqual(si.pascal.symbol(), "Pa")
        self.assertEqual(si.pascal.latex(), None)
        self.assertEqual(si.pascal.factor(), 1)
        self.assertUvEqual(si.pascal, si.kilogram / (si.metre * si.second**2))

    def test_steradian(self):
        """
        Check the definition of the steradian unit.
        """
        self.assertEqual(si.steradian.label(), "Steradian")
        self.assertEqual(si.steradian.symbol(), "sr")
        self.assertEqual(si.steradian.latex(), None)
        self.assertEqual(si.steradian.factor(), 1)
        self.assertUvEqual(si.steradian, si.radian**2)

    def test_siemens(self):
        """
        Check the definition of the siemens unit.
        """
        self.assertEqual(si.siemens.label(), "Siemens")
        self.assertEqual(si.siemens.symbol(), "S")
        self.assertEqual(si.siemens.latex(), None)
        self.assertEqual(si.siemens.factor(), 1)
        self.assertUvEqual(si.siemens, si.second**3 * si.ampere**2 / \
                           (si.kilogram * si.metre**2))

    def test_lumen(self):
        """
        Check the definition of the lumen unit.
        """
        self.assertEqual(si.lumen.label(), "Lumen")
        self.assertEqual(si.lumen.symbol(), "lm")
        self.assertEqual(si.lumen.latex(), None)
        self.assertEqual(si.lumen.factor(), 1)
        self.assertUvEqual(si.lumen, si.candela * si.radian**2)

    def test_lux(self):
        """
        Check the definition of the lux unit.
        """
        self.assertEqual(si.lux.label(), "Lux")
        self.assertEqual(si.lux.symbol(), "lx")
        self.assertEqual(si.lux.latex(), None)
        self.assertEqual(si.lux.factor(), 1)
        self.assertUvEqual(si.lux, si.candela * si.radian**2 / si.metre**2)

    def test_kat(self):
        """
        Check the definition of the kat unit.
        """
        self.assertEqual(si.kat.label(), "Katal")
        self.assertEqual(si.kat.symbol(), "kat")
        self.assertEqual(si.kat.latex(), None)
        self.assertEqual(si.kat.factor(), 1)
        self.assertUvEqual(si.kat, si.mole / si.second)

    # def test_day(self):
    #     """
    #     Check the definition of the day unit.
    #     """
    #     self.assertEqual(si.day.label(), "Day")
    #     self.assertEqual(si.day.symbol(), "d")
    #     self.assertEqual(si.day.latex(), None)
    #     self.assertEqual(si.day.factor(), 3600 * 24)
    #     self.assertUvEqual(si.day, si.second)

    def test_julian_year(self):
        """
        Check the definition of the julian year unit.
        """
        self.assertEqual(si.julian_year.label(), "Julian year")
        self.assertEqual(si.julian_year.symbol(), "yr")
        self.assertEqual(si.julian_year.latex(), None)
        self.assertEqual(si.julian_year.factor(), 365.25 * 3600 * 24)
        self.assertUvEqual(si.julian_year, si.second)

    # def test_year(self):
    #     """
    #     Check the definition of the year unit.
    #     """
    #     self.assertEqual(si.year.label(), "Year")
    #     self.assertEqual(si.year.symbol(), "a")
    #     self.assertEqual(si.year.latex(), None)
    #     self.assertEqual(si.year.factor(), 365 * 3600 * 24)
    #     self.assertUvEqual(si.year, si.second)

    def test_degree(self):
        """
        Check the definition of the degree unit.
        """
        self.assertEqual(si.degree.label(), "Degree")
        self.assertEqual(si.degree.symbol(), "°")
        self.assertEqual(si.degree.latex(), "{}^{\\circ}")
        self.assertEqual(si.degree.factor(), math.pi / 180)
        self.assertUvEqual(si.degree, si.radian)

    def test_arc_minute(self):
        """
        Check the definition of the arc minute unit.
        """
        self.assertEqual(si.arc_minute.label(), "Arc minute")
        self.assertEqual(si.arc_minute.symbol(), "'")
        self.assertEqual(si.arc_minute.latex(), None)
        self.assertEqual(si.arc_minute.factor(), math.pi / 60 / 180)
        self.assertUvEqual(si.arc_minute, si.radian)

    def test_arc_second(self):
        """
        Check the definition of the arc second unit.
        """
        self.assertEqual(si.arc_second.label(), "Arc second")
        self.assertEqual(si.arc_second.symbol(), "''")
        self.assertEqual(si.arc_second.latex(), None)
        self.assertEqual(si.arc_second.factor(), math.pi / 3600 / 180)
        self.assertUvEqual(si.arc_second, si.radian)

    def test_litre(self):
        """
        Check the definition of the litre unit.
        """
        self.assertEqual(si.litre.label(), "Litre")
        self.assertEqual(si.litre.symbol(), "l")
        self.assertEqual(si.litre.latex(), None)
        self.assertEqual(si.litre.factor(), 0.001)
        self.assertUvEqual(si.litre, si.metre**3)

    def test_liter(self):
        """
        Check the definition of the liter unit.
        """
        self.assertEqual(si.liter.label(), "Litre")
        self.assertEqual(si.liter.symbol(), "l")
        self.assertEqual(si.liter.latex(), None)
        self.assertEqual(si.liter.factor(), 0.001)
        self.assertUvEqual(si.liter, si.metre**3)

    def test_astronomical_unit(self):
        """
        Check the definition of the astronomical unit.
        """
        self.assertEqual(si.astronomical_unit.label(), "Astronomical unit")
        self.assertEqual(si.astronomical_unit.symbol(), "au")
        self.assertEqual(si.astronomical_unit.latex(), None)
        self.assertAlmostEqual(si.astronomical_unit.factor(),
                         1.49597870700e11, delta=10)  # [2], see references.txt
        self.assertUvEqual(si.astronomical_unit, si.metre)

    # def test_parsec(self):
    #     """
    #     Check the definition of the parsec unit.
    #     """
    #     self.assertEqual(si.parsec.label(), "Parsec")
    #     self.assertEqual(si.parsec.symbol(), "au")
    #     self.assertEqual(si.parsec.latex(), None)
    #     self.assertAlmostEqual(si.parsec.factor(),
    #                      3.085677581e16)  # [3], see references.txt
    #    self.assertUvEqual(si.parsec, si.metre)

    def test_light_year(self):
        """
        Check the definition of a light year.
        """
        self.assertEqual(si.light_year.label(), "Light year")
        self.assertEqual(si.light_year.symbol(), "ly")
        self.assertEqual(si.light_year.latex(), None)
        self.assertAlmostEqual(si.light_year.factor(),
                         365.25 * 299792458 * 3600 * 24)  # [4], see references.txt
        self.assertUvEqual(si.light_year, si.metre)

    def test_hectare(self):
        """
        Check the definition of the hectare unit.
        """
        self.assertEqual(si.hectare.label(), "Hectare")
        self.assertEqual(si.hectare.symbol(), "ha")
        self.assertEqual(si.hectare.latex(), None)
        self.assertEqual(si.hectare.factor(), 1e4)
        self.assertUvEqual(si.hectare, si.metre**2)

    def test_are(self):
        """
        Check the definition of the 'are' unit.
        """
        self.assertEqual(si.are.label(), "Are")
        self.assertEqual(si.are.symbol(), "ar")
        self.assertEqual(si.are.latex(), None)
        self.assertEqual(si.are.factor(), 100)
        self.assertUvEqual(si.are, si.metre**2)

    def test_dalton(self):
        """
        Check the definition of the dalton unit.
        """
        self.assertEqual(si.dalton.label(), "Dalton")
        self.assertEqual(si.dalton.symbol(), "Da")
        self.assertEqual(si.dalton.latex(), None)
        self.assertAlmostEqual(si.dalton.factor(),
                         1.66053886e-27, delta=1e-33)  # [5], see references.txt
        self.assertUvEqual(si.dalton, si.kilogram)

    # def test_unit(self):
    #     """
    #     Check the definition of the atomic mass unit.
    #     """
    #     self.assertEqual(si.unit.label(), "Atomic mass unit")
    #     self.assertEqual(si.unit.symbol(), "Da")
    #     self.assertEqual(si.unit.latex(), None)
    #     self.assertAlmostEqual(si.unit.factor(),
    #                      1.66053886e-27, delta=1e-33)  # [5], see references.txt
    #     self.assertUvEqual(si.unit, si.kilogram)

    def test_angstrom(self):
        u"""
        Check the definition of the ångström unit.
        """
        self.assertEqual(si.angstrom.label(), u"Ångström")
        self.assertEqual(si.angstrom.symbol(), u"Å")
        self.assertEqual(si.angstrom.latex(), "\\AA")
        self.assertEqual(si.angstrom.factor(), 1e-10)
        self.assertUvEqual(si.angstrom, si.metre)

    def test_barn(self):
        """
        Check the definition of the barn unit.
        """
        self.assertEqual(si.barn.label(), "Barn")
        self.assertEqual(si.barn.symbol(), "b")
        self.assertEqual(si.barn.latex(), None)
        self.assertEqual(si.barn.factor(), 1e-28)
        self.assertUvEqual(si.barn, si.metre**2)

    def test_bar(self):
        """
        Check the definition of the bar unit.
        """
        self.assertEqual(si.bar.label(), "Bar")
        self.assertEqual(si.bar.symbol(), "bar")
        self.assertEqual(si.bar.latex(), None)
        self.assertEqual(si.bar.factor(), 1e5)
        self.assertUvEqual(si.bar, si.kilogram / si.metre / si.second**2)

    def test_atmosphere(self):
        """
        Check the definition of the atmosphere unit.
        """
        self.assertEqual(si.atmosphere.label(), "Atmosphere")
        self.assertEqual(si.atmosphere.symbol(), "atm")
        self.assertEqual(si.atmosphere.latex(), None)
        self.assertEqual(si.atmosphere.factor(),
                         101325)  # [5], see references.txt
        self.assertUvEqual(si.atmosphere, si.kilogram / si.metre / si.second**2)

    def test_gauss(self):
        """
        Check the definition of the gauss unit.
        """
        self.assertEqual(si.gauss.label(), "Gauss")
        self.assertEqual(si.gauss.symbol(), "G")
        self.assertEqual(si.gauss.latex(), None)
        self.assertEqual(si.gauss.factor(), 1e-4)
        self.assertUvEqual(si.gauss, si.kilogram / si.ampere / si.second**2)

    # def test_inch(self):
    #     """
    #     Check the definition of the inch unit.
    #     """
    #     self.assertEqual(si.inch.label(), "Inch")
    #     self.assertEqual(si.inch.symbol(), "in")
    #     self.assertEqual(si.inch.latex(), None)
    #     self.assertEqual(si.inch.factor(), 0.0254)
    #     self.assertUvEqual(si.inch, si.metre)

    def test_foot(self):
        """
        Check the definition of the foot unit.
        """
        self.assertEqual(si.foot.label(), "Foot")
        self.assertEqual(si.foot.symbol(), "ft")
        self.assertEqual(si.foot.latex(), None)
        self.assertEqual(si.foot.factor(), 0.0254 * 12)
        self.assertUvEqual(si.foot, si.metre)

    def test_yard(self):
        """
        Check the definition of the yard unit.
        """
        self.assertEqual(si.yard.label(), "Yard")
        self.assertEqual(si.yard.symbol(), "yd")
        self.assertEqual(si.yard.latex(), None)
        self.assertEqual(si.yard.factor(), 0.0254 * 12 * 3)
        self.assertUvEqual(si.yard, si.metre)

    def test_mil(self):
        """
        Check the definition of the mil unit.
        """
        self.assertEqual(si.mil.label(), "Mil")
        self.assertEqual(si.mil.symbol(), "mil")
        self.assertEqual(si.mil.latex(), None)
        self.assertEqual(si.mil.factor(), 0.0254 / 1000)
        self.assertUvEqual(si.mil, si.metre)

    def test_mile(self):
        """
        Check the definition of the mile unit.
        """
        self.assertEqual(si.mile.label(), "Mile")
        self.assertEqual(si.mile.symbol(), "mi")
        self.assertEqual(si.mile.latex(), None)
        self.assertEqual(si.mile.factor(), 0.0254 * 12 * 5280)
        self.assertUvEqual(si.mile, si.metre)

    def test_erg(self):
        """
        Check the definition of the erg unit.
        """
        self.assertEqual(si.erg.label(), "Erg")
        self.assertEqual(si.erg.symbol(), "erg")
        self.assertEqual(si.erg.latex(), None)
        self.assertEqual(si.erg.factor(), 1e-7)
        self.assertUvEqual(si.erg, si.kilogram * si.metre**2 /si.second**2)

    def test_deca(self):
        """
        Check the definition of the deca prefix.
        """
        self.assertEqual(si.deca.label(), "Deca")
        self.assertEqual(si.deca.symbol(), "da")
        self.assertEqual(si.deca.latex(), None)
        self.assertEqual(si.deca.factor(), 1e1)
        self.assertIsInstance(si.deca, pyveu.Prefix)

    def test_hecto(self):
        """
        Check the definition of the hecto prefix.
        """
        self.assertEqual(si.hecto.label(), "Hecto")
        self.assertEqual(si.hecto.symbol(), "h")
        self.assertEqual(si.hecto.latex(), None)
        self.assertEqual(si.hecto.factor(), 1e2)
        self.assertIsInstance(si.hecto, pyveu.Prefix)

    def test_kilo(self):
        """
        Check the definition of the kilo prefix.
        """
        self.assertEqual(si.kilo.label(), "Kilo")
        self.assertEqual(si.kilo.symbol(), "k")
        self.assertEqual(si.kilo.latex(), None)
        self.assertEqual(si.kilo.factor(), 1e3)
        self.assertIsInstance(si.kilo, pyveu.Prefix)

    def test_mega(self):
        """
        Check the definition of the mega prefix.
        """
        self.assertEqual(si.mega.label(), "Mega")
        self.assertEqual(si.mega.symbol(), "M")
        self.assertEqual(si.mega.latex(), None)
        self.assertEqual(si.mega.factor(), 1e6)
        self.assertIsInstance(si.mega, pyveu.Prefix)

    def test_giga(self):
        """
        Check the definition of the giga prefix.
        """
        self.assertEqual(si.giga.label(), "Giga")
        self.assertEqual(si.giga.symbol(), "G")
        self.assertEqual(si.giga.latex(), None)
        self.assertEqual(si.giga.factor(), 1e9)
        self.assertIsInstance(si.giga, pyveu.Prefix)

    def test_tera(self):
        """
        Check the definition of the tera prefix.
        """
        self.assertEqual(si.tera.label(), "Tera")
        self.assertEqual(si.tera.symbol(), "T")
        self.assertEqual(si.tera.latex(), None)
        self.assertEqual(si.tera.factor(), 1e12)
        self.assertIsInstance(si.tera, pyveu.Prefix)

    def test_peta(self):
        """
        Check the definition of the peta prefix.
        """
        self.assertEqual(si.peta.label(), "Peta")
        self.assertEqual(si.peta.symbol(), "P")
        self.assertEqual(si.peta.latex(), None)
        self.assertEqual(si.peta.factor(), 1e15)
        self.assertIsInstance(si.peta, pyveu.Prefix)

    def test_exa(self):
        """
        Check the definition of the exa prefix.
        """
        self.assertEqual(si.exa.label(), "Exa")
        self.assertEqual(si.exa.symbol(), "E")
        self.assertEqual(si.exa.latex(), None)
        self.assertEqual(si.exa.factor(), 1e18)
        self.assertIsInstance(si.exa, pyveu.Prefix)

    def test_zetta(self):
        """
        Check the definition of the zetta prefix.
        """
        self.assertEqual(si.zetta.label(), "Zetta")
        self.assertEqual(si.zetta.symbol(), "Z")
        self.assertEqual(si.zetta.latex(), None)
        self.assertEqual(si.zetta.factor(), 1e21)
        self.assertIsInstance(si.zetta, pyveu.Prefix)

    def test_yotta(self):
        """
        Check the definition of the yotta prefix.
        """
        self.assertEqual(si.yotta.label(), "Yotta")
        self.assertEqual(si.yotta.symbol(), "Y")
        self.assertEqual(si.yotta.latex(), None)
        self.assertEqual(si.yotta.factor(), 1e24)
        self.assertIsInstance(si.yotta, pyveu.Prefix)

    def test_deci(self):
        """
        Check the definition of the deci prefix.
        """
        self.assertEqual(si.deci.label(), "Deci")
        self.assertEqual(si.deci.symbol(), "d")
        self.assertEqual(si.deci.latex(), None)
        self.assertEqual(si.deci.factor(), 1e-1)
        self.assertIsInstance(si.deci, pyveu.Prefix)

    def test_centi(self):
        """
        Check the definition of the centi prefix.
        """
        self.assertEqual(si.centi.label(), "Centi")
        self.assertEqual(si.centi.symbol(), "c")
        self.assertEqual(si.centi.latex(), None)
        self.assertEqual(si.centi.factor(), 1e-2)
        self.assertIsInstance(si.centi, pyveu.Prefix)

    def test_milli(self):
        """
        Check the definition of the milli prefix.
        """
        self.assertEqual(si.milli.label(), "Milli")
        self.assertEqual(si.milli.symbol(), "m")
        self.assertEqual(si.milli.latex(), None)
        self.assertEqual(si.milli.factor(), 1e-3)
        self.assertIsInstance(si.milli, pyveu.Prefix)

    def test_micro(self):
        """
        Check the definition of the micro prefix.
        """
        self.assertEqual(si.micro.label(), "Micro")
        self.assertEqual(si.micro.symbol(), "u")
        self.assertEqual(si.micro.latex(), u"\\mu")
        self.assertEqual(si.micro.factor(), 1e-6)
        self.assertIsInstance(si.micro, pyveu.Prefix)

    def test_nano(self):
        """
        Check the definition of the nano prefix.
        """
        self.assertEqual(si.nano.label(), "Nano")
        self.assertEqual(si.nano.symbol(), "n")
        self.assertEqual(si.nano.latex(), None)
        self.assertEqual(si.nano.factor(), 1e-9)
        self.assertIsInstance(si.nano, pyveu.Prefix)

    def test_pico(self):
        """
        Check the definition of the pico prefix.
        """
        self.assertEqual(si.pico.label(), "Pico")
        self.assertEqual(si.pico.symbol(), "p")
        self.assertEqual(si.pico.latex(), None)
        self.assertEqual(si.pico.factor(), 1e-12)
        self.assertIsInstance(si.pico, pyveu.Prefix)

    def test_femto(self):
        """
        Check the definition of the femto prefix.
        """
        self.assertEqual(si.femto.label(), "Femto")
        self.assertEqual(si.femto.symbol(), "f")
        self.assertEqual(si.femto.latex(), None)
        self.assertEqual(si.femto.factor(), 1e-15)
        self.assertIsInstance(si.femto, pyveu.Prefix)

    def test_atto(self):
        """
        Check the definition of the atto prefix.
        """
        self.assertEqual(si.atto.label(), "Atto")
        self.assertEqual(si.atto.symbol(), "a")
        self.assertEqual(si.atto.latex(), None)
        self.assertEqual(si.atto.factor(), 1e-18)
        self.assertIsInstance(si.atto, pyveu.Prefix)

    def test_zepto(self):
        """
        Check the definition of the zepto prefix.
        """
        self.assertEqual(si.zepto.label(), "Zepto")
        self.assertEqual(si.zepto.symbol(), "z")
        self.assertEqual(si.zepto.latex(), None)
        self.assertEqual(si.zepto.factor(), 1e-21)
        self.assertIsInstance(si.zepto, pyveu.Prefix)

    def test_yocto(self):
        """
        Check the definition of the yocto prefix.
        """
        self.assertEqual(si.yocto.label(), "Yocto")
        self.assertEqual(si.yocto.symbol(), "y")
        self.assertEqual(si.yocto.latex(), None)
        self.assertEqual(si.yocto.factor(), 1e-24)
        self.assertIsInstance(si.yocto, pyveu.Prefix)

    # unit
