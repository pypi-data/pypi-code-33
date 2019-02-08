
# Copyright (C) 2019 Frank Sauerburger

import unittest
import numpy as np
from math import log

import pyveu
import pyveu.si as si
from pyveu import Quantity, UnitSystem
from pyveu import DifferentUnitSystem, UncertaintyIllDefined

class QuantityTestCase(unittest.TestCase):
    """
    This class implements all tests for non-arithmetic methods of the Quantity
    class. The tests assume that the SI units have been implemented correctly.
    """

    ############################################################
    # __init__
    def test_init_type(self):
        """
        Check the type of the quantity object. It should be a Quantity, a
        Named, a ModifiableNamed and a SystemAffiliated.
        """
        quantity = Quantity(9.18, 0.37, si.metre)
        self.assertIsInstance(quantity, Quantity)
        self.assertIsInstance(quantity, pyveu.Named)
        self.assertIsInstance(quantity, pyveu.ModifiableNamedMixin)
        self.assertIsInstance(quantity, pyveu.SystemAffiliatedMixin)

    def test_init_internal_variables(self):
        """
        Check that the constructor creates all internal variables.
        """
        quantity = Quantity(42.042)

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 0)
        self.assertEqual(quantity._value, 42.042)
        self.assertEqual(list(quantity._unit_vector), [0, 0, 0, 0, 0, 0, 0, 0])


    def test_init_storage_args(self):
        """
        Check that the constructor stores the given positional arguments. This
        includes: value, error, unit, label, symbol and latex symbol.
        """
        quantity = Quantity(1.776, 0.008, si.metre, "Height", "h", r"h_{\phi}")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

        self.assertEqual(quantity.label(), "Height")
        self.assertEqual(quantity.symbol(), "h")
        self.assertEqual(quantity.latex(), "h_{\\phi}")

    def test_init_storage_negative_error(self):
        """
        Check that __init__() throws an exception if the error is negative.
        """
        self.assertRaises(ValueError, Quantity, 1.776, -0.008)

    def test_init_storage_kwds(self):
        """
        Check that the constructor stores the given keyword arguments. This
        includes: value, error, unit, label, symbol and latex symbol.
        """
        quantity = Quantity(value=1.776, error=0.008, unit=si.metre,
                            label="Height", symbol="h", latex=r"h_{\phi}")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

        self.assertEqual(quantity.label(), "Height")
        self.assertEqual(quantity.symbol(), "h")
        self.assertEqual(quantity.latex(), "h_{\\phi}")

    def test_init_mandatory_args(self):
        """
        Check that only the first argument, the value argument is mandatory.
        """
        try:
            quantity = Quantity(1.776)
        except TypeError as e:
            self.fail(e)

    def test_init_string_definition_value(self):
        """
        Check that a quantity can be initialized with a string consisting only
        of a value.
        """
        quantity = Quantity("1.776")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 0)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [0, 0, 0, 0, 0, 0, 0, 0])

    def test_init_string_definition_value_error(self):
        """
        Check that a quantity can be initialized with a string consisting of a
        value and error.
        """
        quantity = Quantity("1.776 +- 0.008")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [0, 0, 0, 0, 0, 0, 0, 0])

    def test_init_string_definition_value_unit(self):
        """
        Check that a quantity can be initialized with a string consisting of a
        value and unit.
        """
        quantity = Quantity("1776 mm")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 0)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

    def test_init_string_definition_value_error_unit(self):
        """
        Check that a quantity can be initialized with a string consisting of a
        value, error and unit.
        """
        quantity = Quantity("1.776 +- 0.008 m")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])
    
    def test_init_string_with_error_arg(self):
        """
        Check initialization with a string fails if the error arguments is
        given.
        """
        self.assertRaises(ValueError, Quantity, "1.776 m", error=0.02)
    
    def test_init_string_with_unit_arg(self):
        """
        Check initialization with a string fails if the unit arguments is
        given.
        """
        self.assertRaises(ValueError, Quantity, "1.776", unit=si.metre)
    
    def test_init_string_with_names(self):
        """
        Check initialization with a string and names succeeds.
        """
        quantity = Quantity("1.776 +- 0.008 m", label="Height", symbol="h",
                            latex="h_{\\phi}")

        self.assertEqual(quantity._derivatives, {})
        self.assertEqual(quantity._variances, {})

        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

        self.assertEqual(quantity.label(), "Height")
        self.assertEqual(quantity.symbol(), "h")
        self.assertEqual(quantity.latex(), "h_{\\phi}")

    def test_init_unit_object(self):
        """
        Check that initialization with a unit object succeeds. The test is
        repeated with different units, prefixed units, fractions of units and
        powers of units.
        """
        quantity = Quantity(1.776, 0.008, si.metre)
        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

        quantity = Quantity(1776, 8, si.milli * si.metre )
        self.assertEqual(quantity._variance, 64e-6)
        self.assertEqual(quantity._value, 1.776)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

        quantity = Quantity(9810, 23, si.milli * si.metre / si.second**2)
        self.assertEqual(quantity._variance, 0.023**2)
        self.assertEqual(quantity._value, 9.81)
        self.assertEqual(list(quantity._unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_init_unit_vector(self):
        """
        Check that initialization with a unit vector succeeds. The test is
        repeated with different units, prefixed units, fractions of units and
        powers of units.
        """
        quantity = Quantity(9810, 23, [1, 0, -2, 0, 0, 0, 0, 0])
        self.assertEqual(quantity._variance, 23**2)
        self.assertEqual(quantity._value, 9810)
        self.assertEqual(list(quantity._unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
        self.assertIsInstance(quantity._unit_vector, np.ndarray)

        unit_vector = np.array([1, 0, -2, 0, 0, 0, 0, 0])
        quantity = Quantity(9810, 23, unit_vector)
        self.assertEqual(quantity._variance, 23**2)
        self.assertEqual(quantity._value, 9810)
        self.assertEqual(list(quantity._unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
        self.assertIsInstance(quantity._unit_vector, np.ndarray)

    def test_init_default_unit_system(self):
        """
        Check that the quantity is tied to the default unit system, when the
        unit_system argument is omitted.
        """
        quantity = Quantity("1.776 +- 0.008 m")

        self.assertIs(quantity.unit_system(), pyveu.get_default_unit_system())

    def test_init_custom_unit_system(self):
        """
        Check that the quantity can be assigned to a custom unit system passed
        to the unit_system argument.
        """
        us = UnitSystem("alternative US", 3)
        us.create_base_unit(0, "Inch", "in", register=True)

        quantity = Quantity("65 +- 2 in", unit_system=us)
        self.assertIs(quantity.unit_system(), us)
        self.assertEqual(list(quantity._unit_vector), [1, 0, 0])

    def test_unit_system_from_unit(self):
        """
        Check that if the unit_system parameter is omitted, the unit system of
        the unit object is used.
        """
        us = UnitSystem("alternative US", 3)
        inch = us.create_base_unit(0, "Inch", "in", register=True)

        quantity = Quantity(65, 2, inch)
        self.assertIs(quantity.unit_system(), us)

    def test_unit_system_mismatch(self):
        """
        Check that the unit system of the unit object must match a custom unit
        system.
        """
        us = UnitSystem("alternative US", 3)
        self.assertRaises(pyveu.DifferentUnitSystem, Quantity, 125, 18,
                          si.metre, unit_system=us)

    ############################################################
    # value
    def test_value_base(self):
        """
        Check that value() returns the value in base units by default.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertEqual(quantity.value(), 7670)

    def test_value_unit_system(self):
        """
        Check that value() check the unit system of the unit object.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)

        us = UnitSystem("other", 2)
        base = us.create_base_unit(0, "Base", "b")
        self.assertRaises(pyveu.DifferentUnitSystem, quantity.value, base)

    def test_value_pure_prefix(self):
        """
        Check that value() returns the value in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is cm.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertEqual(quantity.value(to="mm / s"), 7.67e6)
        self.assertEqual(quantity.value(to=si.milli * si.metre / si.second),
                         7.67e6)

    def test_value_non_base(self):
        """
        Check that value() returns the value in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is inch.
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")

        quantity = Quantity(1.78, 0.02, metre, unit_system=us)
        self.assertAlmostEqual(quantity.value(inch), 1.78 / 0.0254)
        self.assertAlmostEqual(quantity.value("in"), 1.78 / 0.0254)

    def test_value_non_base_prefixed(self):
        """
        Check that value() returns the value in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is kilo
        inch (kin).
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(1.78, 0.02, metre, unit_system=us)
        self.assertAlmostEqual(quantity.value(kilo * inch), 1.78 / 25.4)
        self.assertAlmostEqual(quantity.value("kin"), 1.78 / 25.4)

    def test_value_non_base_fraction(self):
        """
        Check that value() returns the value in a custom unit specified by the
        'to' argument. The quantity is in m/s and the custom type is km/h.
        """
        us = UnitSystem("alternative US", 2)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        second = us.create_base_unit(1, "Second", "s", register=True)
        hour = second * 3600
        us.register_unit(hour, "Hour", "hr")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(64.9, 0.2, metre / second, unit_system=us)
        self.assertAlmostEqual(quantity.value(kilo * metre / hour), 64.9 * 3.6)
        self.assertAlmostEqual(quantity.value("km / hr"), 64.9 * 3.6)

    def test_value_non_base_power(self):
        """
        Check that value() returns the value in a custom unit specified by the
        'to' argument. The quantity is in metre^2 and the custom type is mm^2.
        """
        quantity = Quantity(1284e-6, 23e-6, si.metre**2)
        self.assertAlmostEqual(quantity.value((si.milli * si.metre)**2), 1284)
        self.assertAlmostEqual(quantity.value("mm^2"), 1284)

    def test_value_non_scalar(self):
        """
        Check that an exception is raised if the unit is in metre and value is
        called with 'km/h'.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertRaises(ValueError, quantity.value, "km")
        self.assertRaises(ValueError, quantity.value, si.kilo * si.metre)

    def test_value_non_scalar_dimensionless(self):
        """
        Check that an exception is raised if the unit is 'rad' and value is
        called with 'm'.
        """
        quantity = Quantity(7.67, 0.01, si.radian)
        self.assertRaises(ValueError, quantity.value, "m")
        self.assertRaises(ValueError, quantity.value, si.metre)

    ############################################################
    # error
    def test_error_base(self):
        """
        Check that error() returns the error in base units by default.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertEqual(quantity.error(), 10)

    def test_error_unit_system(self):
        """
        Check that error() check the unit system of the unit object.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)

        us = UnitSystem("other", 2)
        base = us.create_base_unit(0, "Base", "b")
        self.assertRaises(pyveu.DifferentUnitSystem, quantity.error, base)

    def test_error_pure_prefix(self):
        """
        Check that error() returns the error in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is cm.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertEqual(quantity.error(to="mm / s"), 0.01e6)
        self.assertEqual(quantity.error(to=si.milli * si.metre / si.second),
                         0.01e6)

    def test_error_non_base(self):
        """
        Check that error() returns the error in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is inch.
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")

        quantity = Quantity(1.78, 0.02, metre, unit_system=us)
        self.assertAlmostEqual(quantity.error(inch), 0.02 / 0.0254)
        self.assertAlmostEqual(quantity.error("in"), 0.02 / 0.0254)

    def test_error_non_base_prefixed(self):
        """
        Check that error() returns the error in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is kilo
        inch (kin).
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(1.78, 0.02, metre, unit_system=us)
        self.assertAlmostEqual(quantity.error(kilo * inch), 0.02 / 25.4)
        self.assertAlmostEqual(quantity.error("kin"), 0.02 / 25.4)

    def test_error_non_base_fraction(self):
        """
        Check that error() returns the error in a custom unit specified by the
        'to' argument. The quantity is in m/s and the custom type is km/h.
        """
        us = UnitSystem("alternative US", 2)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        second = us.create_base_unit(1, "Second", "s", register=True)
        hour = second * 3600
        us.register_unit(hour, "Hour", "hr")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(64.9, 0.2, metre / second, unit_system=us)
        self.assertAlmostEqual(quantity.error(kilo * metre / hour), 0.2 * 3.6)
        self.assertAlmostEqual(quantity.error("km / hr"), 0.2 * 3.6)

    def test_error_non_base_power(self):
        """
        Check that error() returns the error in a custom unit specified by the
        'to' argument. The quantity is in metre^2 and the custom type is mm^2.
        """
        quantity = Quantity(1284e-6, 23e-6, si.metre**2)
        self.assertAlmostEqual(quantity.error((si.milli * si.metre)**2), 23)
        self.assertAlmostEqual(quantity.error("mm^2"), 23)

    def test_error_non_scalar(self):
        """
        Check that an exception is raised if the unit is in metre and error is
        called with 'km/h'.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertRaises(ValueError, quantity.error, "km")
        self.assertRaises(ValueError, quantity.error, si.kilo * si.metre)

    def test_error_non_scalar_dimensionless(self):
        """
        Check that an exception is raised if the unit is 'rad' and error is
        called with 'm'.
        """
        quantity = Quantity(7.67, 0.01, si.radian)
        self.assertRaises(ValueError, quantity.error, "m")
        self.assertRaises(ValueError, quantity.error, si.metre)

    ############################################################
    # variance
    def test_variance_base(self):
        """
        Check that variance() returns the variance in base units by default.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertEqual(quantity.variance(), 10**2)

    def test_variance_unit_system(self):
        """
        Check that variance() check the unit system of the unit object.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)

        us = UnitSystem("other", 2)
        base = us.create_base_unit(0, "Base", "b")
        self.assertRaises(pyveu.DifferentUnitSystem, quantity.variance, base)

    def test_variance_pure_prefix(self):
        """
        Check that variance() returns the variance in a custom unit specified
        by the 'to' argument. The quantity is in metre and the custom type is
        cm.
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertEqual(quantity.variance(to="mm / s"), 1e8)
        self.assertEqual(quantity.variance(to=si.milli * si.metre / si.second),
                         1e8)

    def test_variance_non_base(self):
        """
        Check that variance() returns the variance in a custom unit specified
        by the 'to' argument. The quantity is in metre and the custom type is
        inch.
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")

        quantity = Quantity(1.78, 0.02, metre, unit_system=us)
        self.assertAlmostEqual(quantity.variance(inch), (0.02 / 0.0254)**2)
        self.assertAlmostEqual(quantity.variance("in"), (0.02 / 0.0254)**2)

    def test_variance_non_base_prefixed(self):
        """
        Check that variance() returns the variance in a custom unit specified
        by the 'to' argument. The quantity is in metre and the custom type is
        kilo inch (kin).
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(1.78, 0.02, metre, unit_system=us)
        self.assertAlmostEqual(quantity.variance(kilo * inch),
                               (0.02 / 25.4)**2)
        self.assertAlmostEqual(quantity.variance("kin"), (0.02 / 25.4)**2)

    def test_variance_non_base_fraction(self):
        """
        Check that variance() returns the variance in a custom unit specified
        by the 'to' argument. The quantity is in m/s and the custom type is
        km/h.
        """
        us = UnitSystem("alternative US", 2)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        second = us.create_base_unit(1, "Second", "s", register=True)
        hour = second * 3600
        us.register_unit(hour, "Hour", "hr")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(64.9, 0.2, metre / second, unit_system=us)
        self.assertAlmostEqual(quantity.variance(kilo * metre / hour),
                               (0.2 * 3.6)**2)
        self.assertAlmostEqual(quantity.variance("km / hr"), (0.2 * 3.6)**2)

    def test_variance_non_base_power(self):
        """
        Check that variance() returns the variance in a custom unit specified
        by the 'to' argument. The quantity is in metre^2 and the custom type
        is mm^2.
        """
        quantity = Quantity(1284e-6, 23e-6, si.metre**2)
        self.assertAlmostEqual(quantity.variance((si.milli * si.metre)**2),
                               23**2)
        self.assertAlmostEqual(quantity.variance("mm^2"), 23**2)

    def test_variance_non_scalar(self):
        """
        Check that an exception is raised if the unit is in metre and variance
        is called with 'km/h'..
        """
        quantity = Quantity(7.67, 0.01, si.kilo * si.metre / si.second)
        self.assertRaises(ValueError, quantity.variance, "km")
        self.assertRaises(ValueError, quantity.variance, si.kilo * si.metre)

    def test_variance_non_scalar_dimensionless(self):
        """
        Check that an exception is raised if the unit is 'rad' and variance is
        called with 'm'.
        """
        quantity = Quantity(7.67, 0.01, si.radian)
        self.assertRaises(ValueError, quantity.variance, "m")
        self.assertRaises(ValueError, quantity.variance, si.metre)

    ############################################################
    ## unit_vector

    def test_unit_vector(self):
        """
        Check that unit_vector() returns the correct vector.
        """
        quantity = Quantity("1.776 +- 0.008 kg m / s^2")
        self.assertEqual(list(quantity.unit_vector()),
                         [1, 1, -2, 0, 0, 0, 0, 0])


    def test_unit_vector_type(self):
        """
        Check that unit_vector() returns the unit vector as a numpy array.
        """
        quantity = Quantity("1.776 +- 0.008 kg m / s^2")
        self.assertIsInstance(quantity.unit_vector(), np.ndarray)

    def test_unit_vector_copy(self):
        """
        Check that unit_vector() returns a copy of the internal unit vector.
        """
        quantity = Quantity("1.776 +- 0.008 kg m / s^2")
        unit_vector = quantity.unit_vector()
        unit_vector *= 2
        self.assertEqual(list(quantity.unit_vector()),
                         [1, 1, -2, 0, 0, 0, 0, 0])

    ############################################################
    #  Dimensionless
    def test_dimensionless_dl_base(self):
        """
        Check that a quantity with a dimensionless unit is dimensionless.
        """
        quantity = Quantity("6.2 +- 0.4 rad")
        self.assertTrue(quantity.dimensionless())

    def test_dimensionless_ndl_base(self):
        """
        Check that a quantity with a non-dimensionless base unit is not
        dimensionless.
        """
        quantity = Quantity("6.2 +- 0.4 m")
        self.assertFalse(quantity.dimensionless())

    def test_dimensionless_dl_combination(self):
        """
        Check that a quantity with a dimensionless linear combination is
        dimensionless.
        """
        us = UnitSystem("other", 3, 2)
        us.create_base_unit(-1, "Radian", "rad", register=True)
        us.create_base_unit(-2, "Unity", "unity", register=True)

        quantity = Quantity("6.2 +- 0.4 rad unity^2", unit_system=us)
        self.assertTrue(quantity.dimensionless())

    def test_dimensionless_pndl_combination(self):
        """
        Check that a quantity with a pure non-dimensionless linear combination
        is not dimensionless.
        """
        quantity = Quantity("6.2 +- 0.4 m /s")
        self.assertFalse(quantity.dimensionless())

    def test_dimensionless_mndl_combination(self):
        """
        Check that a quantity with a mix non-dimensionless linear combination
        is not dimensionless.
        """
        us = UnitSystem("other", 3, 2)
        us.create_base_unit(0, "Meter", "m", register=True)
        us.create_base_unit(-1, "Radian", "rad", register=True)
        us.create_base_unit(-2, "Unity", "unity", register=True)

        quantity = Quantity("6.2 +- 0.4 m / rad unity^2", unit_system=us)
        self.assertFalse(quantity.dimensionless())

    ############################################################
    # round
    def test_round_base(self):
        """
        Check that round() returns the round in base units by default. This
        should check the 'to' part of the method. Since this is extensively
        tested for error() and value(), the tests here are rather basic.
        """
        quantity = Quantity("7.67323e3 +- 43.232 m / s")
        self.assertEqual(quantity.round(), ("7670", "40", 0))

    def test_round_return_type(self):
        """
        Check that round returns a tuple with two strings and an integer.
        """
        quantity = Quantity("7.67323e3 +- 43.232 m / s")

        retval = quantity.round()
        self.assertIsInstance(retval, tuple)
        self.assertEqual(len(retval), 3)

        value, error, common_factor = retval
        self.assertIsInstance(value, str)
        self.assertIsInstance(error, str)
        self.assertIsInstance(common_factor, int)

    def test_round_non_base(self):
        """
        Check that round() returns the round in a custom unit specified by the
        'to' argument. The quantity is in metre and the custom type is inch.
        This should check the 'to' part of the method. Since this is
        extensively tested for error() and value(), the tests here are rather
        basic.
        """
        us = UnitSystem("alternative US", 1)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        inch = metre * 0.0254
        us.register_unit(inch, "Inch", "in")

        quantity = Quantity("7.67323e3 +- 43.232 m", unit_system=us)
        self.assertEqual(quantity.round(inch), ("302100", "1700", 0))
        self.assertEqual(quantity.round("in"), ("302100", "1700", 0))

    def test_round_non_scalar(self):
        """
        Check that an exception is raised if the unit is in metre and round is
        called with 'km/h'. This should check the 'to' part of the method.
        Since this is extensively tested for error() and value(), the tests
        here are rather basic.
        """
        quantity = Quantity("7.67323e3 +- 43.232 m")
        self.assertRaises(ValueError, quantity.round, "s")
        self.assertRaises(ValueError, quantity.round, si.second)

    def test_round_significant_digits_integer(self):
        """
        Check that round() rounds to the given number of significant_digits.
        The parameter significant_digits is a integer in this test case.
        """
        quantity = Quantity("7.67323e3 +- 43.232 m")
        self.assertEqual(quantity.round(significant_digits=1),
                              ("7670", "40", 0))
        self.assertEqual(quantity.round(significant_digits=2),
                              ("7673", "43", 0))
        self.assertEqual(quantity.round(significant_digits=3),
                              ("7673.2", "43.2", 0))

    def test_round_significant_digits_less_than_one(self):
        """
        Check that round() raises an exception if significant_digits is
        less than one.
        """
        quantity = Quantity("7.67323e3 +- 43.232 m")
        self.assertRaises(ValueError, quantity.round, significant_digits=0.5)
        self.assertRaises(ValueError, quantity.round, significant_digits=0)
        self.assertRaises(ValueError, quantity.round, significant_digits=-0.5)
        self.assertRaises(ValueError, quantity.round, significant_digits=-1)
        self.assertRaises(ValueError, quantity.round, significant_digits=-3)

    def test_round_significant_digits_float(self):
        """
        Check that round() rounds to the given number of significant_digits.
        The parameter significant_digits is float in this test case.
        """
        quantity = Quantity("7.67323e3 +- 43.232 m")
        self.assertEqual(quantity.round(significant_digits=2.1),
                              ("7673", "43", 0))
        self.assertEqual(quantity.round(significant_digits=2.4),
                              ("7673", "43", 0))
        self.assertEqual(quantity.round(significant_digits=2.5),
                              ("7673.2", "43.2", 0))
        self.assertEqual(quantity.round(significant_digits=2.9),
                              ("7673.2", "43.2", 0))

    def test_round_significant_digits_defautl(self):
        """
        Check that round() uses significant_digits=1.2 as default.
        """
        quantity = Quantity("1.77659 +- 0.00832 m")
        self.assertEqual(quantity.round(), ("1.777", "0.008", 0))
        quantity = Quantity("1.77659 +- 0.00212 m")
        self.assertEqual(quantity.round(), ("1.777", "0.002", 0))
        quantity = Quantity("1.77659 +- 0.00192 m")
        self.assertEqual(quantity.round(), ("1.7766", "0.0019", 0))
        quantity = Quantity("1.77659 +- 0.00102 m")
        self.assertEqual(quantity.round(), ("1.7766", "0.0010", 0))
        quantity = Quantity("1.77659 +- 0.00092 m")
        self.assertEqual(quantity.round(), ("1.7766", "0.0009", 0))

    def test_round_common_factor_small(self):   
        """
        Check that the common exponent is extracted if value and error are
        small.
        """
        quantity = Quantity("1.77659 +- 0.2123 mm^2")
        self.assertEqual(quantity.round(), ("1.8", "0.2", -6))

    def test_round_common_factor_large(self):   
        """
        Check that the common exponent is extracted if value and error are
        large.
        """
        quantity = Quantity("1.77659 +- 0.2123 km^2")
        self.assertEqual(quantity.round(), ("1800", "200", 3))

    def test_round_common_factor_large_difference(self):   
        """
        Check that the common exponent is not extracted if the value and error
        differ by many orders of magnitude .
        """
        quantity = Quantity("1.23456789012345e6 +- 754e-6 s")
        self.assertEqual(quantity.round(), ("1234567.8901", "0.0008", 0))

    def test_round_without_error(self):   
        """
        Check that the full value is returned if the error is zero.
        """
        quantity = Quantity("1.234567890123456  s")
        value, error, common = quantity.round()
        self.assertTrue(value.startswith("1.23456789012"))
        self.assertEqual(error, "0")
        self.assertEqual(common, 0)

        quantity = Quantity("1.234567890123456e6  s")
        value, error, common = quantity.round()
        self.assertTrue(value.startswith("1234567.89012"))
        self.assertEqual(error, "0")
        self.assertEqual(common, 0)

    def test_round_both_zero(self):   
        """
        Check that the ("0", "0", 0) is returned when the value and error are
        zero.
        """
        quantity = Quantity("0  s")
        self.assertEqual(quantity.round(),
                               ("0", "0", 0))


    def test_round_next_regime_int(self):
        """
        Check what happens if an error of 0.96 is rounded upwards, when 
        significant_digits is an integer.
        """
        quantity = Quantity("1776.59 +- 9.678 m")
        self.assertEqual(quantity.round(significant_digits=1),
                               ("1780", "10", 0))
        quantity = Quantity("1776.59 +- 9.978 m")
        self.assertEqual(quantity.round(significant_digits=2),
                               ("1777", "10", 0))
        quantity = Quantity("1776.59 +- 9.998 m")
        self.assertEqual(quantity.round(significant_digits=3),
                               ("1776.6", "10.0", 0))

    def test_round_next_regime_float(self):
        """
        Check what happens if an error of 0.96 is rounded upwards, when 
        significant_digits is a float.
        """
        quantity = Quantity("1776.59 +- 9.678 m")
        self.assertEqual(quantity.round(significant_digits=1.1),
                               ("1777", "10", 0))
        quantity = Quantity("1776.59 +- 9.978 m")
        self.assertEqual(quantity.round(significant_digits=2.1),
                               ("1776.6", "10.0", 0))
        quantity = Quantity("1776.59 +- 9.998 m")
        self.assertEqual(quantity.round(significant_digits=3.1),
                               ("1776.59", "10.00", 0))

    ############################################################
    # str
    def test_str_with_common_factor(self):
        """
        Check that the common factor is included in the string.
        """
        quantity = Quantity("1.77659 +- 0.2123 mm^2")
        self.assertEqual(quantity.str(), "(1.8 +- 0.2) * 10^-6 m^2")

    def test_str_without_common_factor(self):
        """
        Check that common factor 10^0 is omitted.
        """
        quantity = Quantity("1.77659 +- 0.2123 m")
        self.assertEqual(quantity.str(), "(1.8 +- 0.2) m")

    def test_str_without_unit(self):
        """
        Check that the unit part is omitted if the unit vector is (0, 0, ...,
        0).
        """
        quantity = Quantity("1.77659 +- 0.2123")
        self.assertEqual(quantity.str(), "1.8 +- 0.2")

    def test_str_custom_unit(self):
        """
        Check that the unit can be changed from 'm/s' to 'km/h'.
        """
        us = UnitSystem("alternative US", 2)
        metre = us.create_base_unit(0, "Metre", "m", register=True)
        second = us.create_base_unit(1, "Second", "s", register=True)
        hour = second * 3600
        us.register_unit(hour, "Hour", "hr")
        kilo = us.create_prefix(1000, "Kilo", "k")

        quantity = Quantity(1.77659, 0.2123, si.metre / si.second)
        self.assertEqual(quantity.str("km / hr"), "(6.4 +- 0.8) km / hr")

    def test_str_custom_unit_non_scalar(self):
        """
        Check that all non-scalar multiples of the unit are append to the
        units string.
        """
        quantity = Quantity(1.77659, 0.2123, si.metre / si.second)
        self.assertEqual(quantity.str("hr^-1"), "(6400 +- 800) 1 / hr * m")

    def test_str_without_error(self):
        """
        Check that '+- 0' is omitted if the error is zero.
        """
        quantity = Quantity("1.77659 m")
        self.assertEqual(quantity.str(), "1.77659 m")

    def test_str_custom_signficance_digits(self):
        """
        Check that the significant_digits parameter is passed on to value()
        and error.
        """
        quantity = Quantity("1.77659 +- 0.2123 m")
        self.assertEqual(quantity.str(significant_digits=3),
                         "(1.777 +- 0.212) m")

    def test_str_with_symbol(self):
        """
        Check that the string contains "<symbol> = " if the quantity has a
        symbol.
        """
        quantity = Quantity("1.77659 +- 0.2123 m", symbol="h")
        self.assertEqual(quantity.str(), "h = (1.8 +- 0.2) m")

        quantity = Quantity("1.77659 +- 0.2123 m", symbol="h",
                            latex="h_{\\phi}")
        self.assertEqual(quantity.str(), "h = (1.8 +- 0.2) m")

    ############################################################
    # lors
#     def test_lors_with_common_factor(self):
#         """
#         Check that the common factor is included in the string.
#         """
#         quantity = Quantity("1.77659 +- 0.2123 mm^2")
#         self.assertEqual(quantity.lors(),
#                          r"(1.8 \pm 0.2) \cdot 10^{-6} \mathrm{m}^2")
# 
#     def test_lors_without_common_factor(self):
#         """
#         Check that common factor 10^0 is omitted.
#         """
#         quantity = Quantity("1.77659 +- 0.2123 m")
#         self.assertEqual(quantity.lors(),
#                          r"(1.8 \pm 0.2) \mathrm{m}^2")
# 
#     def test_lors_without_unit(self):
#         """
#         Check that the unit part is omitted if the unit vector is (0, 0, ...,
#         0).
#         """
#         quantity = Quantity("1.77659 +- 0.2123")
#         self.assertEqual(quantity.str(), "1.8 \\pm  0.2")
# 
#     def test_lors_custom_unit(self):
#         """
#         Check that the unit can be changed from 'm/s' to 'km/h'.
#         """
#         us = UnitSystem("alternative US", 2)
#         metre = us.create_base_unit(0, "Metre", "m", register=True)
#         second = us.create_base_unit(1, "Second", "s", register=True)
#         hour = second * 3600
#         us.register_unit(hour, "Hour", "hr")
#         kilo = us.create_prefix(1000, "Kilo", "k")
# 
#         quantity = Quantity(1.77659, 0.2123, metre / second)
#         self.assertEqual(quantity.str("km / hr"),
#                          r"(6.4 \pm 0.8) \frac{\mathrm{km}}{\mathrm{hr}}")
# 
#     def test_lors_custom_unit_non_scalar(self):
#         """
#         Check that all non-scalar multiples of the unit are append to the
#         units string.
#         """
#         quantity = Quantity(1.77659, 0.2123, metre / second)
#         self.assertEqual(quantity.str("hr^-1"),
#                          r"(6400 \pm 800) \frac{\mathrm{m}}{\mathrm{hr}}")
# 
#     def test_lors_without_error(self):
#         """
#         Check that '\\pm 0' is omitted if the error is zero.
#         """
#         quantity = Quantity("1.77659 m")
#         self.assertEqual(quantity.str(), "1.77659 \\mathrm{m}")
# 
#     def test_lors_custom_signficance_digits(self):
#         """
#         Check that the significant_digits parameter is passed on to value()
#         and error.
#         """
#         quantity = Quantity("1.77659 +- 0.2123 m")
#         self.assertEqual(quantity.str(significant_digits=3),
#                          r"(1.777 \pm 0.212) \mathrm{m}")
# 
#     def test_lors_with_lors(self):
#         """
#         Check that the string contains "<lors> = " if the quantity has a
#         symbol latex symbol.
#         """
#         quantity = Quantity("1.77659 +- 0.2123 m", symbol="h")
#         self.assertEqual(quantity.lors(), r"h = (1.777 \pm 0.212) \mathrm{m}")
# 
#         quantity = Quantity("1.77659 +- 0.2123 m", symbol="h",
#                             latex="h_{\\phi}")
#         self.assertEqual(quantity.lors(),
#                          r"h_{\phi} = (1.777 \pm 0.212) \mathrm{m}")

    ############################################################
    # __str__

    def test_str(self):
        """
        Check that __str__ calls str().
        """
        quantity = Quantity("1.77659 +- 0.2123 m")
        self.assertEqual(str(quantity), "(1.8 +- 0.2) m")

    ############################################################
    # repr
    def test_repr(self):
        """
        Check that all parts of an independent unit are present.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")

        self.assertEqual(repr(quantity),
                         "<Quantity Speed: v = (1.77659 +- 0.20923) m s^(-1)>")

    def test_repr_no_error(self):
        """
        Check that the error part is omitted, if the error is zero.
        """
        quantity = Quantity("1.77659 m / s", label="Speed",
                            symbol="v", latex="\\nu")

        self.assertEqual(repr(quantity),
                         "<Quantity Speed: v = 1.77659 m s^(-1)>")

    def test_repr_no_label(self):
        """
        Check that the label part is omitted, if the label is not set.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", symbol="v",
                            latex="\\nu")

        self.assertEqual(repr(quantity),
                         "<Quantity: v = (1.77659 +- 0.20923) m s^(-1)>")

    def test_repr_no_symbol(self):
        """
        Check that the '<symbol> = ' part is omitted, if the symbol is not
        set.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            latex="\\nu")
        self.assertEqual(repr(quantity),
                         "<Quantity Speed: (1.77659 +- 0.20923) m s^(-1)>")

    def test_repr_anonymous(self):
        """
        Check that all name parts are omitted if the quantity is anonymous.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s")

        self.assertEqual(repr(quantity),
                         "<Quantity: (1.77659 +- 0.20923) m s^(-1)>")

    def test_repr_no_unit(self):
        """
        Check that the unit is not included in the string if the unit vector
        id (0, 0, ..., 0).
        """
        quantity = Quantity("1.77659 +- 0.20923")

        self.assertEqual(repr(quantity),
                         "<Quantity: 1.77659 +- 0.20923>")

    def test_repr_dependent(self):
        """
        Check that list of dependencies include the id() of the quantities it
        depends on.
        """
        quantity = Quantity("1.77659 +- 0.20923 m")
        quantity._derivatives = {1234: 0.21}
        quantity._variances = {1234: 2930.2}

        self.assertEqual(repr(quantity),
                         "<Quantity: (1.77659 +- 0.20923) m | depends=[1234]>")

    ############################################################
    # Modifiable Named
    def test_label_modify(self):
        """
        Check that the label can be modified.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")
        self.assertEqual(quantity.label(), "Speed")
        quantity.label("Speed 2")
        self.assertEqual(quantity.label(), "Speed 2")

        quantity = Quantity("1.77659 +- 0.20923 m / s")
        self.assertEqual(quantity.label(), None)
        quantity.label("Speed 2")
        self.assertEqual(quantity.label(), "Speed 2")

    def test_label_modify_id(self):
        """
        Check that the id() is not changed, when the label is modified.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")
        previous_id = id(quantity)
        quantity.label("Speed 2")
        self.assertEqual(id(quantity), previous_id)

    def test_symbol_modify(self):
        """
        Check that the symbol can be modified.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")
        self.assertEqual(quantity.symbol(), "v")
        quantity.symbol("v_2")
        self.assertEqual(quantity.symbol(), "v_2")

        quantity = Quantity("1.77659 +- 0.20923 m / s")
        self.assertEqual(quantity.symbol(), None)
        quantity.symbol("v_2")
        self.assertEqual(quantity.symbol(), "v_2")

    def test_symbol_modify_id(self):
        """
        Check that the id() is not changed, when the symbol is modified.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")
        previous_id = id(quantity)
        quantity.symbol("v_2")
        self.assertEqual(id(quantity), previous_id)

    def test_latex_modify(self):
        """
        Check that the latex can be modified.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")
        self.assertEqual(quantity.latex(), "\\nu")
        quantity.latex("\\nu_2")
        self.assertEqual(quantity.latex(), "\\nu_2")

        quantity = Quantity("1.77659 +- 0.20923 m / s")
        self.assertEqual(quantity.latex(), None)
        quantity.latex("\\nu_2")
        self.assertEqual(quantity.latex(), "\\nu_2")

    def test_latex_modify_id(self):
        """
        Check that the id() is not changed, when the latex is modified.
        """
        quantity = Quantity("1.77659 +- 0.20923 m / s", label="Speed",
                            symbol="v", latex="\\nu")
        previous_id = id(quantity)
        quantity.latex("\\nu_2")
        self.assertEqual(id(quantity), previous_id)

    ############################################################
    # Round helper
    def test_get_digit_pos(self):
        """
        Check that _get_digit() returns the requested digit.
        """
        self.assertEqual(Quantity._get_digit(345676.54321, 7), 0)
        self.assertEqual(Quantity._get_digit(345676.54321, 6), 0)
        self.assertEqual(Quantity._get_digit(345676.54321, 5), 3)
        self.assertEqual(Quantity._get_digit(345676.54321, 4), 4)
        self.assertEqual(Quantity._get_digit(345676.54321, 3), 5)
        self.assertEqual(Quantity._get_digit(345676.54321, 2), 6)
        self.assertEqual(Quantity._get_digit(345676.54321, 1), 7)
        self.assertEqual(Quantity._get_digit(345676.54321, 0), 6)
        self.assertEqual(Quantity._get_digit(345676.54321, -1), 5)
        self.assertEqual(Quantity._get_digit(345676.54321, -2), 4)
        self.assertEqual(Quantity._get_digit(345676.54321, -3), 3)
        self.assertEqual(Quantity._get_digit(345676.54321, -4), 2)
        self.assertEqual(Quantity._get_digit(345676.54321, -5), 1)
        self.assertEqual(Quantity._get_digit(345676.54321, -6), 0)

    def test_get_digit_neg(self):
        """
        Check that _get_digit() returns the requested digit when the number is
        negative.
        """
        self.assertEqual(Quantity._get_digit(-345676.54321, 7), 0)
        self.assertEqual(Quantity._get_digit(-345676.54321, 6), 0)
        self.assertEqual(Quantity._get_digit(-345676.54321, 5), 3)
        self.assertEqual(Quantity._get_digit(-345676.54321, 4), 4)
        self.assertEqual(Quantity._get_digit(-345676.54321, 3), 5)
        self.assertEqual(Quantity._get_digit(-345676.54321, 2), 6)
        self.assertEqual(Quantity._get_digit(-345676.54321, 1), 7)
        self.assertEqual(Quantity._get_digit(-345676.54321, 0), 6)
        self.assertEqual(Quantity._get_digit(-345676.54321, -1), 5)
        self.assertEqual(Quantity._get_digit(-345676.54321, -2), 4)
        self.assertEqual(Quantity._get_digit(-345676.54321, -3), 3)
        self.assertEqual(Quantity._get_digit(-345676.54321, -4), 2)
        self.assertEqual(Quantity._get_digit(-345676.54321, -5), 1)
        self.assertEqual(Quantity._get_digit(-345676.54321, -6), 0)

    def test_msd_position_pos(self):
        """
        Check the return value of _msd_position() for positive numbers.
        """
        self.assertEqual(Quantity._msd_position(0.0021), -3)
        self.assertEqual(Quantity._msd_position(0.0321), -2)
        self.assertEqual(Quantity._msd_position(0.4321), -1)
        self.assertEqual(Quantity._msd_position(5.0321), 0)
        self.assertEqual(Quantity._msd_position(65.0021), 1)
        self.assertEqual(Quantity._msd_position(790.0021), 2)
        self.assertEqual(Quantity._msd_position(1002.0021), 3)
        self.assertEqual(Quantity._msd_position(10021), 4)
        self.assertEqual(Quantity._msd_position(230021), 5)

    def test_msd_position_neg(self):
        """
        Check the return value of _msd_position() for negative numbers.
        """
        self.assertEqual(Quantity._msd_position(-0.0021), -3)
        self.assertEqual(Quantity._msd_position(-0.0321), -2)
        self.assertEqual(Quantity._msd_position(-0.4321), -1)
        self.assertEqual(Quantity._msd_position(-5.0321), 0)
        self.assertEqual(Quantity._msd_position(-65.0021), 1)
        self.assertEqual(Quantity._msd_position(-790.0021), 2)
        self.assertEqual(Quantity._msd_position(-1002.0021), 3)
        self.assertEqual(Quantity._msd_position(-10021), 4)
        self.assertEqual(Quantity._msd_position(-230021), 5)

class QuantityParseTestCase(unittest.TestCase):
    """
    This class implements all tests Quantity.parse_unit(). The tests have been put
    into its own class to avoid prefixing them with 'test_parse_'. This test
    case does not test prefix parsing since the UnitSystem has already been
    tested.
    """
    def test_default_unit_system(self):
        """
        Check that parse_unit() uses the default unit system.
        """
        value, error, unit_vector = Quantity.parse("1 +- 1 m")
        self.assertEqual(list(unit_vector), [1, 0, 0, 0, 0, 0, 0, 0]) 

    def test_custom_unit_system(self):
        """
        Check that parse_unit() uses a custom unit system when given.
        """
        us = UnitSystem("Test System", 2)
        us.create_base_unit(0, "Meter", "m", register=True)
        us.create_base_unit(1, "Second", "s", register=True)

        value, error, unit_vector = Quantity.parse("1 +- 1 m", us)
        self.assertEqual(list(unit_vector), [1, 0])

    def test_empty(self):
        """
        Check that an empty string fails because the value part is missing.
        """
        self.assertRaises(ValueError, Quantity.parse, "")

    def test_value_only(self):
        """
        Check that a value only string is parsed. The error and unit vector
        should be zero.
        """
        value, error, unit_vector = Quantity.parse("42.3")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 0)
        self.assertEqual(list(unit_vector), [0, 0, 0, 0, 0, 0, 0, 0])

    def test_value_error(self):
        """
        Check that a string with a value and error part is parsed. The unit
        vector should be zero.
        """
        value, error, unit_vector = Quantity.parse("42.3 +- 2.8")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 2.8)
        self.assertEqual(list(unit_vector), [0, 0, 0, 0, 0, 0, 0, 0])

    def test_value_unit(self):
        """
        Check that a string with a value and unit part is parsed. The error
        should be zero.
        """
        value, error, unit_vector = Quantity.parse("42.3 s")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 0)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])

    def test_value_error_unit(self):
        """
        Check that a string with a value, error and unit part is parsed.
        """
        value, error, unit_vector = Quantity.parse("42.3 +- 2.9 s")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 2.9)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])

    def test_value_error_unit_spaces(self):
        """
        Check that a string with all three parts is parsed regardless of
        white spaces.
        """
        value, error, unit_vector = Quantity.parse("42.3+-2.9s")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 2.9)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])
    
        value, error, unit_vector = Quantity.parse("42.3+-2.9 s")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 2.9)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])
    
        value, error, unit_vector = Quantity.parse("42.3 +- 2.9s")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 2.9)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])

        value, error, unit_vector = Quantity.parse("  42.3 +- 2.9 s  ")
        self.assertEqual(value, 42.3)
        self.assertEqual(error, 2.9)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])
    
    def test_value_int(self):
        """
        Check that an integer value is parsed.
        """
        value, error, unit_vector = Quantity.parse("10 +- 0.12 m / s^2")
        self.assertEqual(value, 10)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_int_e(self):
        """
        Check that an integer value with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("9e3 +- 0.12 m / s^2")
        self.assertEqual(value, 9000)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_int_neg_e(self):
        """
        Check that an integer value with negative exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("9e-3 +- 0.12 m / s^2")
        self.assertEqual(value, 0.009)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_float(self):
        """
        Check that a float value is parsed.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 0.12 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_float_e(self):
        """
        Check that a float value with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("9.81e1 +- 0.12 m / s^2")
        self.assertEqual(value, 98.1)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

        value, error, unit_vector = Quantity.parse("9.81e0 +- 0.12 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_float_neg_e(self):
        """
        Check that a float value with negative exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("9.81e-2 +- 0.12 m / s^2")
        self.assertEqual(value, 0.0981)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
        value, error, unit_vector = Quantity.parse("9.81e-0 +- 0.12 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_value_neg_int(self):
        """
        Check that a negative integer value is parsed.
        """
        value, error, unit_vector = Quantity.parse("-10 +- 0.12 m / s^2")
        self.assertEqual(value, -10)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_neg_int_e(self):
        """
        Check that a negative integer value with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("-10e2 +- 0.12 m / s^2")
        self.assertEqual(value, -1000)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_neg_int_neg_e(self):
        """
        Check that a negative integer value with negative exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("-82e-2 +- 0.12 m / s^2")
        self.assertEqual(value, -0.82)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_value_neg_float(self):
        """
        Check that a negative float value is parsed.
        """
        value, error, unit_vector = Quantity.parse("-9.81 +- 0.12 m / s^2")
        self.assertEqual(value, -9.81)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_neg_float_e(self):
        """
        Check that a negative float value with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("-9.81e9 +- 0.12 m / s^2")
        self.assertEqual(value, -9.81e9)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_value_neg_float_neg_e(self):
        """
        Check that a negative float value with negative exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("-9.81e-4 +- 0.12 m / s^2")
        self.assertEqual(value, -9.81e-4)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_value_plus_int(self):
        """
        Check that a integer value with a leading plus is parsed.
        """
        value, error, unit_vector = Quantity.parse("+9 +- 0.12 m / s^2")
        self.assertEqual(value, 9)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_value_plus_float_plus_e(self):
        """
        Check that a float value with exponent, both with leading plus is parsed.
        """
        value, error, unit_vector = Quantity.parse("+9.18e+1 +- 0.12 m / s^2")
        self.assertEqual(value, 91.8)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_error_int(self):
        """
        Check that an integer error is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- 1 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 1)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_error_int_e(self):
        """
        Check that an integer error with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- 2e1 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 20)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_error_int_neg_e(self):
        """
        Check that an integer error with negative exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- 9e-1 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.9)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_error_float(self):
        """
        Check that a float error is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- 0.12 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_error_float_e(self):
        """
        Check that a float error with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- 0.127e1 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 1.27)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])

    def test_error_float_neg_e(self):
        """
        Check that a float error with negative exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- 12.7e-1 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 1.27)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_error_neg_int(self):
        """
        Check that a negative integer error raises an exception.
        """
        self.assertRaises(ValueError, Quantity.parse, "0.981e1 +- -2 m / s^2")

    def test_error_neg_int_e(self):
        """
        Check that a negative integer error with exponent raises an exception.
        """
        self.assertRaises(ValueError, Quantity.parse, "0.981e1 +- -2e3 m / s^2")

    def test_error_neg_int_neg_e(self):
        """
        Check that a negative integer error with negative exponent raises an
        exception.
        """
        self.assertRaises(ValueError, Quantity.parse, "0.981e1 +- -2e-8 m / s^2")
    
    def test_error_neg_float(self):
        """
        Check that a negative float error raises an exception.
        """
        self.assertRaises(ValueError, Quantity.parse, "0.981e1 +- -2.82 m / s^2")

    def test_error_neg_float_e(self):
        """
        Check that a negative float error with exponent raises an exception.
        """
        self.assertRaises(ValueError, Quantity.parse, "0.981e1 +- -2.82e12 m / s^2")

    def test_error_neg_float_neg_e(self):
        """
        Check that a negative float error with negative exponent raises an
        exception.
        """
        self.assertRaises(ValueError, Quantity.parse, "0.981e1 +- -2.82e-12 m / s^2")
    
    def test_error_plus_int(self):
        """
        Check that a integer error with a leading plus is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- +12 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 12)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])
    
    def test_error_plus_float_plus_e(self):
        """
        Check that a float error with exponent, both with leading plus is parsed.
        """
        value, error, unit_vector = Quantity.parse("0.981e1 +- +12.7e+1 m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 127)
        self.assertEqual(list(unit_vector), [1, 0, -2, 0, 0, 0, 0, 0])


    def test_unit(self):
        """
        Check that a unit is translated into a unit vector.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 m kg s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 1, 1, 0, 0, 0, 0, 0])

    def test_unit_prefix(self):
        """
        Check that a prefixed unit is translated into a unit vector and that
        the value and errors are scaled..
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 ms")
        self.assertAlmostEqual(value, 9.81e-3)
        self.assertAlmostEqual(error, 0.32e-3)
        self.assertEqual(list(unit_vector), [0, 0, 1, 0, 0, 0, 0, 0])

    def test_unit_exponent(self):
        """
        Check that a unit with exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 m kg^3 s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 3, 1, 0, 0, 0, 0, 0])

    def test_unit_exponent_prefix(self):
        """
        Check that a prefixed unit with exponent is translated into a unit
        vector and that the value and errors are scaled..
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 kg / mm^3")
        self.assertEqual(value, 9.81e9)
        self.assertAlmostEqual(error, 0.32e9, places=5)
        self.assertEqual(list(unit_vector), [-3, 1, 0, 0, 0, 0, 0, 0])

    def test_unit_float_exponent(self):
        """
        Check that a unit with float exponent is parsed.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 m kg^0.5 s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 0.5, 1, 0, 0, 0, 0, 0])

    def test_unit_neg_exponent(self):
        """
        Check that a unit with a negative exponent is parsed. This should be
        tested for unit in the numerator and denominator.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 m kg^3 s^-1")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 3, -1, 0, 0, 0, 0, 0])

    def test_unit_fraction(self):
        """
        Check that the unit part can be a fraction.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 m / s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 0, -1, 0, 0, 0, 0, 0])

    def test_unit_fraction_prefix(self):
        """
        Check that a prefixed unit in a fraction is translated into a unit
        vector and that the value and errors are scaled.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 m / ms")
        self.assertEqual(value, 9.81e3)
        self.assertEqual(error, 0.32e3)
        self.assertEqual(list(unit_vector), [1, 0, -1, 0, 0, 0, 0, 0])

    def test_unit_missing_numerator(self):
        """
        Check that the first token of the unit can be a slash without any
        other parts in the numerator.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 / s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [0, 0, -1, 0, 0, 0, 0, 0])

        value, error, unit_vector = \
            Quantity.parse("9.81 +- 3.2e-1 m / s^-2")
        self.assertEqual(list(unit_vector), [1, 0, 2, 0, 0, 0, 0, 0])

    def test_unit_leading_slash(self):
        """
        Check that the first token of the unit can be a slash with other parts
        in the numerator.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 / s * m")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 0, -1, 0, 0, 0, 0, 0])

    def test_unit_leading_star(self):
        """
        Check that the first token of the unit can be a star.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 * m")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 0, 0, 0, 0, 0, 0, 0])

        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 * m / s")
        self.assertEqual(list(unit_vector), [1, 0, -1, 0, 0, 0, 0, 0])

    def test_unit_continued_fraction(self):
        """
        Check that any space-separated unit right of a slash is in the
        denominator.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 kg / m s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [-1, 1, -1, 0, 0, 0, 0, 0])

    def test_unit_continued_slash(self):
        """
        Check that a slash continues a previously initialized denominator.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 kg / m / s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [-1, 1, -1, 0, 0, 0, 0, 0])
        
    def test_unit_slash_star(self):
        """
        Check that a star breaks a denominator and appends to the numerator.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 kg / m * s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [-1, 1, 1, 0, 0, 0, 0, 0])

    def test_unit_product(self):
        """
        Check that a star multiplies the numerators.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 kg * s * s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [0, 1, 2, 0, 0, 0, 0, 0])

    def test_unit_product_before_fraction(self):
        """
        Check that a star multiplies the numerators before a fraction.
        """
        value, error, unit_vector = Quantity.parse("9.81 +- 3.2e-1 kg * m / s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 1, -1, 0, 0, 0, 0, 0])

    def test_unit_product_after_fraction(self):
        """
        Check that a star multiplies the numerators after a fraction.
        """
        value, error, unit_vector = \
            Quantity.parse("9.81 +- 3.2e-1 kg / m  *s * s")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [-1, 1, 2, 0, 0, 0, 0, 0])

    def test_unit_complex_example(self):
        """
        Check that a complex example is parsed as intended.
        """
        value, error, unit_vector = \
            Quantity.parse("9.81 +- 3.2e-1 kg * m / s^2")
        self.assertEqual(value, 9.81)
        self.assertEqual(error, 0.32)
        self.assertEqual(list(unit_vector), [1, 1, -2, 0, 0, 0, 0, 0])


    def test_unit_double_star(self):
        """
        Check that two directly following stars fail.
        """
        self.assertRaises(ValueError, Quantity.parse, "9.81 +- 3.2e-1 m * * s")

    def test_unit_double_slash(self):
        """
        Check that two directly following slashs fail.
        """
        self.assertRaises(ValueError, Quantity.parse, "9.81 +- 3.2e-1 m // s")

    def test_unit_direct_star_slash(self):
        """
        Check that a slash directly following a stars fails.
        """
        self.assertRaises(ValueError, Quantity.parse, "9.81 +- 3.2e-1 m /* s")

    def test_unit_trailing_slash(self):
        """
        Check that a trailing slash fails.
        """
        self.assertRaises(ValueError, Quantity.parse, "9.81 +- 3.2e-1 m / s /")

    def test_unit_trailing_star(self):
        """
        Check that a trailing star fails.
        """
        self.assertRaises(ValueError, Quantity.parse, "9.81 +- 3.2e-1 m / s *")
    
class QuantityPraseUnitTestCase(unittest.TestCase):
    """
    This class implements all tests Quantity.parse_unit(). The tests have been put
    into its own class to avoid prefixing them with 'test_parse_'. This test
    focuses on the history of the generated units.
    """

    def test_default_unit_system(self):
        """
        Check that parse_unit() uses the default unit system.
        """
        unit = Quantity.parse_unit("m")
        self.assertEqual(repr(unit), "<Unit Metre: 1 m = 1 m>")
        self.assertEqual(str(unit), "m")
        
    def test_custom_unit_system(self):
        """
        Check that parse_unit() uses a custom unit system when given.
        """
        us = UnitSystem("Test System", 2)
        us.create_base_unit(0, "METRE", "M", register=True)
        us.create_base_unit(1, "SECOND", "S", register=True)

        unit = Quantity.parse_unit("M", us)
        self.assertEqual(repr(unit), "<Unit METRE: 1 M = 1 M>")
        self.assertEqual(str(unit), "M")

    def test_empty(self):
        """
        Check that parsing an empty string returns a dimensionless object
        (history should be m^0).
        """
        unit = Quantity.parse_unit("")
        self.assertEqual(repr(unit), "<Unit: 1 >")
        self.assertEqual(str(unit), "m^0")

    def test_unit(self):
        """
        Check that a unit is translated into a unit vector.
        """
        unit = Quantity.parse_unit("m kg s")
        self.assertEqual(repr(unit), "<Unit: 1 m kg s>")
        self.assertEqual(str(unit), "m * kg * s")

    def test_unit_prefix(self):
        """
        Check that a prefixed unit is translated into a unit vector and that
        the value and errors are scaled..
        """
        unit = Quantity.parse_unit("ms")
        self.assertEqual(repr(unit), "<Unit MilliSecond: 1 ms = 0.001 s>")
        self.assertEqual(str(unit), "ms")

    def test_unit_exponent(self):
        """
        Check that a unit with exponent is parsed.
        """
        unit = Quantity.parse_unit("m kg^3 s")
        self.assertEqual(repr(unit), "<Unit: 1 m kg^3 s>")
        self.assertEqual(str(unit), "m * kg^3 * s")

    def test_unit_exponent_prefix(self):
        """
        Check that a prefixed unit with exponent is translated into a unit
        vector and that the value and errors are scaled..
        """
        unit = Quantity.parse_unit("kg / mm^3")
        self.assertEqual(repr(unit), "<Unit: 1e+09 m^(-3) kg>")
        self.assertEqual(str(unit), "kg / mm^3")

    def test_unit_float_exponent(self):
        """
        Check that a unit with float exponent is parsed.
        """
        unit = Quantity.parse_unit("m kg^0.5 s")
        self.assertEqual(repr(unit), "<Unit: 1 m kg^0.5 s>")
        self.assertEqual(str(unit), "m * kg^0.5 * s")

    def test_unit_neg_exponent(self):
        """
        Check that a unit with a negative exponent is parsed. This should be
        tested for unit in the numerator and denominator.
        """
        unit = Quantity.parse_unit("m kg^3 s^-1")
        self.assertEqual(repr(unit), "<Unit: 1 m kg^3 s^(-1)>")
        self.assertEqual(str(unit), "m * kg^3 / s")

    def test_unit_fraction(self):
        """
        Check that the unit part can be a fraction.
        """
        unit = Quantity.parse_unit("m / s")
        self.assertEqual(repr(unit), "<Unit: 1 m s^(-1)>")
        self.assertEqual(str(unit), "m / s")

    def test_unit_fraction_prefix(self):
        """
        Check that a prefixed unit in a fraction is translated into a unit
        vector and that the value and errors are scaled.
        """
        unit = Quantity.parse_unit("m / ms")
        self.assertEqual(repr(unit), "<Unit: 1000 m s^(-1)>")
        self.assertEqual(str(unit), "m / ms")

    def test_unit_missing_numerator(self):
        """
        Check that the first token of the unit can be a slash without any
        other parts in the numerator.
        """
        unit = Quantity.parse_unit(" / s")
        self.assertEqual(repr(unit), "<Unit: 1 s^(-1)>")
        self.assertEqual(str(unit), "1 / s")

    def test_unit_leading_slash(self):
        """
        Check that the first token of the unit can be a slash with other parts
        in the numerator.
        """
        unit = Quantity.parse_unit(" / s * m")
        self.assertEqual(repr(unit), "<Unit: 1 m s^(-1)>")
        self.assertEqual(str(unit), "m / s")

    def test_unit_leading_star(self):
        """
        Check that the first token of the unit can be a star.
        """
        unit = Quantity.parse_unit(" * m")
        self.assertEqual(repr(unit), "<Unit Metre: 1 m = 1 m>")
        self.assertEqual(str(unit), "m")

    def test_unit_continued_fraction(self):
        """
        Check that any space-separated unit right of a slash is in the
        denominator.
        """
        unit = Quantity.parse_unit("kg / m s")
        self.assertEqual(repr(unit), "<Unit: 1 m^(-1) kg s^(-1)>")
        self.assertEqual(str(unit), "kg / (m * s)")

    def test_unit_continued_slash(self):
        """
        Check that a slash continues a previously initialized denominator.
        """
        unit = Quantity.parse_unit("kg / m / s")
        self.assertEqual(repr(unit), "<Unit: 1 m^(-1) kg s^(-1)>")
        self.assertEqual(str(unit), "kg / (m * s)")
        
    def test_unit_slash_star(self):
        """
        Check that a star breaks a denominator and appends to the numerator.
        """
        unit = Quantity.parse_unit("kg / m * s")
        self.assertEqual(repr(unit), "<Unit: 1 m^(-1) kg s>")
        self.assertEqual(str(unit), "kg * s / m")

    def test_unit_product(self):
        """
        Check that a star multiplies the numerators.
        """
        unit = Quantity.parse_unit("kg * s * s")
        self.assertEqual(repr(unit), "<Unit: 1 kg s^2>")
        self.assertEqual(str(unit), "kg * s * s")

    def test_unit_product_before_fraction(self):
        """
        Check that a star multiplies the numerators before a fraction.
        """
        unit = Quantity.parse_unit("kg * m / s")
        self.assertEqual(repr(unit), "<Unit: 1 m kg s^(-1)>")
        self.assertEqual(str(unit), "kg * m / s")

    def test_unit_product_after_fraction(self):
        """
        Check that a star multiplies the numerators after a fraction.
        """
        unit = Quantity.parse_unit("kg / m * s * s")
        self.assertEqual(repr(unit), "<Unit: 1 m^(-1) kg s^2>")
        self.assertEqual(str(unit), "kg * s * s / m")

    def test_unit_complex_example(self):
        """
        Check that a complex example is parsed as intended.
        """
        unit = Quantity.parse_unit("kg * m / s^2")
        self.assertEqual(repr(unit), "<Unit: 1 m kg s^(-2)>")
        self.assertEqual(str(unit), "kg * m / s^2")


    def test_unit_double_star(self):
        """
        Check that two directly following stars fail.
        """
        self.assertRaises(ValueError, Quantity.parse_unit, "m * * s")

    def test_unit_double_slash(self):
        """
        Check that two directly following slashs fail.
        """
        self.assertRaises(ValueError, Quantity.parse_unit, "m // s")

    def test_unit_direct_star_slash(self):
        """
        Check that a slash directly following a stars fails.
        """
        self.assertRaises(ValueError, Quantity.parse_unit, "m /* s")

    def test_unit_trailing_slash(self):
        """
        Check that a trailing slash fails.
        """
        self.assertRaises(ValueError, Quantity.parse_unit, "m / s /")

    def test_unit_trailing_star(self):
        """
        Check that a trailing star fails.
        """
        self.assertRaises(ValueError, Quantity.parse_unit, "m / s *")

    def test_qid_type(self):
        """
        Check that the quantity identifier is an integer.
        """
        self.assertIsInstance(Quantity("1.3 kg").qid(), int)

    def test_qid_unique(self):
        """
        Check that newly created quantities have unique qids.
        """
        a = Quantity("83.5 +- 2 cm")
        b = Quantity("83.5 +- 2 cm")

        qid_a = a.qid()
        qid_b = b.qid()

        del b
        b = Quantity("83.5 +- 2 cm")
        qid_c = b.qid()

        self.assertNotEqual(qid_a, qid_b)
        self.assertNotEqual(qid_a, qid_c)
        self.assertNotEqual(qid_b, qid_c)


class QuantityArithmeticsHelper:
    """
    Test case to test multiplications involving quantities.
    """

    def assertDictAlmostEqual(self, a, b, *args, **kwds):
        """
        Check that the items of the two dicts are almost equal.
        """
        self.assertEqual(a.keys(), b.keys())

        for key in a.keys():
            self.assertAlmostEqual(a[key], b[key], *args, **kwds)

    def test_assertDictAlmostEqual_small(self):
        """
        Check that helper method assertDictAlmostEqual succeeds if the
        difference between items is small.
        """
        try:
            self.assertDictAlmostEqual(
                {"hello": 3.0000000001, "world": 4.0000000001},
                {"hello": 3.0000000002, "world": 4.0000000001})
        except AssertionError:
            self.fail("assertDictAlmostEqual failed even though the difference "
                      "is small.")

    def test_assertDictAlmostEqual_large(self):
        """
        Check that helper method assertDictAlmostEqual fails if the
        difference between items is large.
        """
        self.assertRaises(AssertionError, self.assertDictAlmostEqual,
                {"hello": 3.0000000001, "world": 4.0000000001},
                {"hello": 3.0040000002, "world": 4.0000000002})

    def test_assertDictAlmostEqual_keys(self):
        """
        Check that helper method assertDictAlmostEqual fails if the
        keys differ.
        """
        self.assertRaises(AssertionError, self.assertDictAlmostEqual,
                {"hello": 3.0000000001, "world": 4.0000000001},
                {"hihi": 3.0000000002, "world": 4.0000000002})

class QuantityMulTestCase(QuantityArithmeticsHelper, unittest.TestCase):
    """
    Test case to test the multiplications involving quantities.
    """

    def test_mul_type(self):
        """
        Check that multiplying a quantity returns a quantity.
        """
        quantity = Quantity("17 +- 3 m") * 1.23
        self.assertIsInstance(quantity, Quantity)

    def test_mul_new(self):
        """
        Check that multiplying a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity * 1.23, quantity)

    def test_mul_int(self):
        """
        Check that multiplying a quantity with an integer, returns a quantity
        with a scaled value and error. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * 5

        self.assertEqual(repr(product),
                         "<Quantity: (85 +- 15) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 5})

    def test_mul_float(self):
        """
        Check that multiplying a quantity with an float, returns a quantity
        with a scaled value and error. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * 0.5

        self.assertEqual(repr(product),
                         "<Quantity: (8.5 +- 1.5) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 0.5})

    def test_mul_negative(self):
        """
        Check that multiplying a quantity with a negative number, returns a
        quantity with a scaled value and error. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * -1.1

        self.assertEqual(repr(product),
                         "<Quantity: (-18.7 +- 3.3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: -1.1})

    def test_mul_prefix(self):
        """
        Check that multiplying a quantity with a prefix, returns a
        quantity with a scaled value and error. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * si.kilo

        self.assertEqual(repr(product),
                         "<Quantity: (17000 +- 3000) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1000})

    def test_mul_unit(self):
        """
        Check that multiplying a quantity with a unit, returns a
        quantity with a scaled value and error and the product of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * si.newton

        self.assertEqual(repr(product),
                         "<Quantity: (17 +- 3) m^2 kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1})


    def test_mul_unit_w_history(self):
        """
        Check that multiplying a quantity with a derived unit, returns a
        quantity with a scaled value and error and the product of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * (si.newton * 2)

        self.assertEqual(repr(product),
                         "<Quantity: (34 +- 6) m^2 kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 2})

    def test_mul_scaled_unit(self):
        """
        Check that multiplying a quantity with a scaled unit, returns a
        quantity with a scaled value and error and the product of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * si.minute

        self.assertEqual(repr(product),
                         "<Quantity: (1020 +- 180) m s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 60})

    def test_mul_quantity_no_units(self):
        """
        Check that multiplying a dimensionless quantity with another
        dimensionless quantity, returns a quantity with a product of the value
        and the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: 20 +- 10 | depends=[%d, %d]>" % 
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_mul_quantity_self_unit(self):
        """
        Check that multiplying a quantity with another, dimensionless quantity,
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m N")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_mul_quantity_other_unit(self):
        """
        Check that multiplying a dimensionless quantity with another quantity,
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8 m N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_mul_quantity_both_units(self):
        """
        Check that multiplying a quantity with another quantity, returns a
        quantity with a product of the value and the propagated errors and the
        product of the two units. The new quantity must store the derivatives
        and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})


    def test_mul_quantity_no_errors(self):
        """
        Check that multiplying a error-less quantity with another
        error-less quantity, returns a quantity with a product of the value
        and the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product), "<Quantity: 20 m^2 kg s^(-2)>")
        self.assertEqual(product._variances, {})
        self.assertEqual(product._derivatives, {})

    def test_mul_quantity_self_error(self):
        """
        Check that multiplying a quantity with another
        error-less quantity, returns a quantity with a product of the value
        and the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 6) m^2 kg s^(-2) | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2})

    def test_mul_quantity_other_error(self):
        """
        Check that multiplying a error-less quantity with another quantity,
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 8) m^2 kg s^(-2) | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(product._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_b: 10})

    def test_mul_quantity_both_errors(self):
        """
        Check that multiplying a quantity with another quantity, returns a
        quantity with a product of the value and the propagated errors and the
        product of the two units. The new quantity must store the derivatives
        and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_mul_quantity_dep_error_number(self):
        """
        Check that multiplying a dependent quantity with a number
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_b * 1.5

        self.assertEqual(repr(product),
                         "<Quantity: (60 +- 18) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 6})

    def test_mul_quantity_dep_error_prefix(self):
        """
        Check that multiplying a dependent quantity with a prefix
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_b * si.kilo

        self.assertEqual(repr(product),
                         "<Quantity: (40000 +- 12000) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 4000})

    def test_mul_quantity_dep_error_unit(self):
        """
        Check that multiplying a dependent quantity with a unit
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_b * si.minute

        self.assertEqual(repr(product),
                         "<Quantity: (2400 +- 720) m s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 240})

    def test_mul_quantity_self_dep_error(self):
        """
        Check that multiplying a dependent quantity with another quantity,
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("8 +- 3.2 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        product = quantity_b * quantity_c

        self.assertEqual(repr(product),
                         "<Quantity: (320 +- 160) m s | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_c: 10.24})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 32, qid_c: 40})

    def test_mul_quantity_other_dep_error(self):
        """
        Check that multiplying a quantity with another dependent quantity,
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        product = quantity_a * quantity_c

        self.assertEqual(repr(product),
                         "<Quantity: (320 +- 160) m s | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 10.24})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 32, qid_b: 40})


    def test_mul_quantity_both_dep_errors(self):
        """
        Check that multiplying a dependent quantity with another dependent
        quantity, returns a quantity with a product of the value and the
        propagated errors and the product of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("5 +- 1.5 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 4
        quantity_d = quantity_a * 2
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        product = quantity_d * quantity_c

        self.assertEqual(repr(product),
                         "<Quantity: (320 +- 160) m s | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 2.25, qid_b: 10.24})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 64, qid_b: 40})

    def test_mul_quantity_two_numbers(self):
        """
        Check that multiplying a number quantity with another quantity,
        returns a quantity with a product of the value if both quantities are
        dimensionless and error-less . The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        product = quantity_a * quantity_b

        self.assertEqual(repr(product), "<Quantity: 40>")
        self.assertEqual(product._variances, {})
        self.assertEqual(product._derivatives, {})

    def test_mul_quantity_correation(self):
        """
        Check that the multiplication of a quantity with itself honors the
        correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        product = quantity * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (100 +- 80) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 16})
        self.assertDictAlmostEqual(product._derivatives, {qid: 20})

    def test_mul_quantity_correation_diamond(self):
        """
        Check that the multiplication of a quantity which depend on the same
        quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        product = (quantity * 2) * (quantity * 4)

        self.assertEqual(repr(product),
                         "<Quantity: (800 +- 640) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 16})
        self.assertDictAlmostEqual(product._derivatives, {qid: 160})

    def test_rmul_type(self):
        """
        Check that multiplying (from the left) a quantity returns a quantity.
        """
        quantity = 1.23 * Quantity("17 +- 3 m") 
        self.assertIsInstance(quantity, Quantity)

    def test_rmul_new(self):
        """
        Check that multiplying a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity * 1.23, quantity)

    def test_rmul_int(self):
        """
        Check that multiplying (from the left) a quantity with an integer,
        returns a quantity with a scaled value and error. The new quantity
        must store the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = 5 * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (85 +- 15) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 5})

    def test_rmul_float(self):
        """
        Check that multiplying (from the left) a quantity with an float,
        returns a quantity with a scaled value and error. The new quantity
        must store the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity * 0.5

        self.assertEqual(repr(product),
                         "<Quantity: (8.5 +- 1.5) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 0.5})

    def test_rmul_negative(self):
        """
        Check that multiplying (from the left) a quantity with a negative
        number, returns a quantity with a scaled value and error. The new
        quantity must store the derivative and the original variance of the
        quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = -1.1 * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (-18.7 +- 3.3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: -1.1})

    def test_rmul_prefix(self):
        """
        Check that multiplying (from the left) a quantity with a prefix,
        returns a quantity with a scaled value and error. The new quantity
        must store the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = si.kilo * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (17000 +- 3000) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1000})

    def test_rmul_unit(self):
        """
        Check that multiplying (from the left) a quantity with a unit, returns
        a quantity with a scaled value and error and the product of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = si.newton * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (17 +- 3) m^2 kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1})


    def test_rmul_unit_w_history(self):
        """
        Check that multiplying (from the left) a quantity with a derived unit,
        returns a quantity with a scaled value and error and the product of
        the two units. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = (si.newton * 2) * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (34 +- 6) m^2 kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 2})

    def test_rmul_scaled_unit(self):
        """
        Check that multiplying (form the left) a quantity with a scaled unit,
        returns a quantity with a scaled value and error and the product of
        the two units. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = si.minute * quantity

        self.assertEqual(repr(product),
                         "<Quantity: (1020 +- 180) m s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 60})

    def test_rmul_quantity_no_units(self):
        """
        Check that multiplying (from the left) a dimensionless quantity with
        another dimensionless quantity, returns a quantity with a product of
        the value and the propagated errors and the product of the two units.
        The new quantity must store the derivatives and the original variances
        of the quantities.

        This multiplication from the left occurs when the left object is a
        subclass.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: 20 +- 10 | depends=[%d, %d]>" % 
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_rmul_quantity_self_unit(self):
        """
        Check that multiplying (from the left) a quantity with another,
        dimensionless quantity, returns a quantity with a product of the value
        and the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m N")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_rmul_quantity_other_unit(self):
        """
        Check that multiplying (form the left) a dimensionless quantity with another quantity,
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8 m N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_rmul_quantity_both_units(self):
        """
        Check that multiplying (form the left) a quantity with another
        quantity, returns a quantity with a product of the value and the
        propagated errors and the product of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})


    def test_rmul_quantity_no_errors(self):
        """
        Check that multiplying (from the left) a error-less quantity with
        another error-less quantity, returns a quantity with a product of the
        value and the propagated errors and the product of the two units. The
        new quantity must store the derivatives and the original variances of
        the quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product), "<Quantity: 20 m^2 kg s^(-2)>")
        self.assertEqual(product._variances, {})
        self.assertEqual(product._derivatives, {})

    def test_rmul_quantity_self_error(self):
        """
        Check that multiplying (from the left) a quantity with another
        error-less quantity, returns a quantity with a product of the value
        and the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 6) m^2 kg s^(-2) | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2})

    def test_rmul_quantity_other_error(self):
        """
        Check that multiplying (from the left) a error-less quantity with
        another quantity, returns a quantity with a product of the value and
        the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 8) m^2 kg s^(-2) | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(product._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_b: 10})

    def test_rmul_quantity_both_errors(self):
        """
        Check that multiplying (from the left) a quantity with another
        quantity, returns a quantity with a product of the value and the
        propagated errors and the product of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product),
                         "<Quantity: (20 +- 10) m^2 kg s^(-2) | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 2, qid_b: 10})

    def test_rmul_quantity_dep_error_number(self):
        """
        Check that multiplying (from the left) a dependent quantity with a
        number returns a quantity with a product of the value and the
        propagated errors and the product of the two units. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = 1.5 * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (60 +- 18) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 6})

    def test_rmul_quantity_dep_error_prefix(self):
        """
        Check that multiplying (from the left) a dependent quantity with a
        prefix returns a quantity with a product of the value and the
        propagated errors and the product of the two units. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = si.kilo * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (40000 +- 12000) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 4000})

    def test_rmul_quantity_dep_error_unit(self):
        """
        Check that multiplying (from the left) a dependent quantity with a unit
        returns a quantity with a product of the value and the propagated
        errors and the product of the two units. The new quantity must store
        the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        product = si.minute * quantity_b

        self.assertEqual(repr(product),
                         "<Quantity: (2400 +- 720) m s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(product._variances, {qid_a: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 240})

    def test_rmul_quantity_self_dep_error(self):
        """
        Check that multiplying (form the left) a dependent quantity with
        another quantity, returns a quantity with a product of the value and
        the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("8 +- 3.2 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        product = quantity_b.__rmul__(quantity_c)

        self.assertEqual(repr(product),
                         "<Quantity: (320 +- 160) m s | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_c: 10.24})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 32, qid_c: 40})

    def test_rmul_quantity_other_dep_error(self):
        """
        Check that multiplying (from the left) a quantity with another
        dependent quantity, returns a quantity with a product of the value and
        the propagated errors and the product of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        product = quantity_a.__rmul__(quantity_c)

        self.assertEqual(repr(product),
                         "<Quantity: (320 +- 160) m s | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 9, qid_b: 10.24})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 32, qid_b: 40})


    def test_rmul_quantity_both_dep_errors(self):
        """
        Check that multiplying (from the left) a dependent quantity with
        another dependent quantity, returns a quantity with a product of the
        value and the propagated errors and the product of the two units. The
        new quantity must store the derivatives and the original variances of
        the quantities.
        """
        quantity_a = Quantity("5 +- 1.5 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 4
        quantity_d = quantity_a * 2
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        product = quantity_d.__rmul__(quantity_c)

        self.assertEqual(repr(product),
                         "<Quantity: (320 +- 160) m s | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(product._variances, {qid_a: 2.25, qid_b: 10.24})
        self.assertDictAlmostEqual(product._derivatives, {qid_a: 64, qid_b: 40})

    def test_rmul_quantity_two_numbers(self):
        """
        Check that multiplying (from the left) a number quantity with another
        quantity, returns a quantity with a product of the value if both
        quantities are dimensionless and error-less . The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        product = quantity_a.__rmul__(quantity_b)

        self.assertEqual(repr(product), "<Quantity: 40>")
        self.assertEqual(product._variances, {})
        self.assertEqual(product._derivatives, {})

    def test_rmul_quantity_correation(self):
        """
        Check that the multiplication (from the left) of a quantity with
        itself honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        product = quantity.__rmul__(quantity)

        self.assertEqual(repr(product),
                         "<Quantity: (100 +- 80) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 16})
        self.assertDictAlmostEqual(product._derivatives, {qid: 20})

    def test_rmul_quantity_correation_diamond(self):
        """
        Check that the multiplication (from the left) of a quantity which
        depend on the same quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        product = (quantity * 2).__rmul__(quantity * 4)

        self.assertEqual(repr(product),
                         "<Quantity: (800 +- 640) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 16})
        self.assertDictAlmostEqual(product._derivatives, {qid: 160})

    def test_imul_negative(self):
        """
        Check that multiplying (in-place) a quantity with a negative number,
        returns a quantity with a scaled value and error. The new quantity
        must store the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity
        product *= -1.1

        self.assertEqual(repr(product),
                         "<Quantity: (-18.7 +- 3.3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: -1.1})

    def test_imul_prefix(self):
        """
        Check that multiplying (in-place) a quantity with a prefix, returns a
        quantity with a scaled value and error. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity
        product *= si.kilo

        self.assertEqual(repr(product),
                         "<Quantity: (17000 +- 3000) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1000})

    def test_imul_unit(self):
        """
        Check that multiplying (in-place) a quantity with a unit, returns a
        quantity with a scaled value and error and the product of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity
        product *= si.newton

        self.assertEqual(repr(product),
                         "<Quantity: (17 +- 3) m^2 kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1})

    def test_imul_quantity_correation_diamond(self):
        """
        Check that the multiplication (in-place) of a quantity which depend on
        the same quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        product = (quantity * 2)
        product *= (quantity * 4)

        self.assertEqual(repr(product),
                         "<Quantity: (800 +- 640) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 16})
        self.assertDictAlmostEqual(product._derivatives, {qid: 160})

    def test_mul_unit_system(self):
        """
        Check that the multiplication check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a * b,
                          quantity_a, quantity_b)

    def test_rmul_unit_system(self):
        """
        Check that the multiplication check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a.__rmul__(b),
                          quantity_a, quantity_b)

class QuantityDivTestCase(QuantityArithmeticsHelper, unittest.TestCase):
    """
    Test case to test divisions involving quantities.
    """

    def test_div_type(self):
        """
        Check that dividing a quantity returns a quantity.
        """
        quantity = Quantity("17 +- 3 m") / 1.23
        self.assertIsInstance(quantity, Quantity)

    def test_div_new(self):
        """
        Check that dividing a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity / 1.23, quantity)

    def test_div_int(self):
        """
        Check that dividing a quantity by an integer, returns a quantity
        with a scaled value and error. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("15 +- 3 m")
        qid = quantity.qid()

        ratio = quantity / 5

        self.assertEqual(repr(ratio),
                         "<Quantity: (3 +- 0.6) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 0.2})

    def test_div_int_auto_true_div(self):
        """
        Check that dividing an integer quantity by an integer, returns a quantity
        with a scaled, float value and error. Python 2.7 compatibility check.
        Dividing should always convert to floats.
        """
        quantity = Quantity("10 m")
        qid = quantity.qid()

        ratio = quantity / 4

        self.assertEqual(repr(ratio),
                         "<Quantity: 2.5 m>")
        self.assertDictAlmostEqual(ratio._variances, {})
        self.assertDictAlmostEqual(ratio._derivatives, {})

    def test_div_float(self):
        """
        Check that dividing a quantity by a float, returns a quantity
        with a scaled value and error. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("15 +- 3 m")
        qid = quantity.qid()

        ratio = quantity / 0.5

        self.assertEqual(repr(ratio),
                         "<Quantity: (30 +- 6) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 2})

    def test_div_negative(self):
        """
        Check that dividing a quantity by a negative number, returns a
        quantity with a scaled value and error. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        ratio = quantity / -0.25

        self.assertEqual(repr(ratio),
                         "<Quantity: (-68 +- 12) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -4})

    def test_div_prefix(self):
        """
        Check that dividing a quantity by a prefix, returns a quantity with a
        scaled value and error. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        ratio = quantity / si.kilo

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.017 +- 0.003) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 0.001})

    def test_div_unit(self):
        """
        Check that dividing a quantity by a unit, returns a quantity with a
        scaled value and error and the ratio of the two units. The new
        quantity must store the derivative and the original variance of the
        quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        ratio = quantity / si.newton

        self.assertEqual(repr(ratio),
                         "<Quantity: (17 +- 3) kg^(-1) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 1})


    def test_div_unit_w_history(self):
        """
        Check that dividing a quantity with a derived unit, returns a quantity
        with a scaled value and error and the ratio of the two units. The
        new quantity must store the derivative and the original variance of
        the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        ratio = quantity / (si.newton * 2)

        self.assertEqual(repr(ratio),
                         "<Quantity: (8.5 +- 1.5) kg^(-1) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 0.5})

    def test_div_scaled_unit(self):
        """
        Check that dividing a quantity by a scaled unit, returns a
        quantity with a scaled value and error and the ratio of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("330 +- 99 m")
        qid = quantity.qid()

        ratio = quantity / si.minute

        self.assertEqual(repr(ratio),
                         "<Quantity: (5.5 +- 1.65) m s^(-1) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 9801})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 1. / 60})

    def test_div_quantity_no_units(self):
        """
        Check that dividing a dimensionless quantity by another dimensionless
        quantity, returns a quantity with a ratio of the value and the
        propagated errors and the ratio of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: 5 +- 2.5 | depends=[%d, %d]>" % 
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_div_quantity_self_unit(self):
        """
        Check that dividing a quantity by another, dimensionless quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m N")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_div_quantity_other_unit(self):
        """
        Check that dividing a dimensionless quantity by another quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8 m N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m^(-2) kg^(-1) s^2 | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_div_quantity_both_units(self):
        """
        Check that dividing a quantity by another quantity, returns a
        quantity with a ratio of the value and the propagated errors and the
        ratio of the two units. The new quantity must store the derivatives
        and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) kg^(-1) s^2 | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})


    def test_div_quantity_no_errors(self):
        """
        Check that dividing a error-less quantity by another error-less
        quantity, returns a quantity with a ratio of the value and the
        propagated errors and the ratio of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio), "<Quantity: 5 kg^(-1) s^2>")
        self.assertEqual(ratio._variances, {})
        self.assertEqual(ratio._derivatives, {})

    def test_div_quantity_self_error(self):
        """
        Check that dividing a quantity with another
        error-less quantity, returns a quantity with a ratio of the value
        and the propagated errors and the ratio of the two units. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 1.5) kg^(-1) s^2 | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5})

    def test_div_quantity_other_error(self):
        """
        Check that dividing a error-less quantity by another quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2) kg^(-1) s^2 | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(ratio._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_b: -2.5})

    def test_div_quantity_both_errors(self):
        """
        Check that dividing a quantity by another quantity, returns a quantity
        with a ratio of the value and the propagated errors and the ratio
        of the two units. The new quantity must store the derivatives and the
        original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) kg^(-1) s^2 | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_div_quantity_dep_error_number(self):
        """
        Check that dividing a dependent quantity by a number returns a
        quantity with a ratio of the value and the propagated errors and the
        ratio of the two units. The new quantity must store the propagate
        its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b / 1.6

        self.assertEqual(repr(ratio),
                         "<Quantity: (25 +- 7.5) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 2.5})

    def test_div_quantity_dep_error_prefix(self):
        """
        Check that dividing a dependent quantity by a prefix returns a
        quantity with a ratio of the value and the propagated errors and the
        ratio of the two units. The new quantity must store the propagate
        its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b / si.kilo

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.04 +- 0.012) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.004})

    def test_div_quantity_dep_error_unit(self):
        """
        Check that dividing a dependent quantity by a unit returns a quantity
        with a ratio of the value and the propagated errors and the ratio
        of the two units. The new quantity must store the propagate its
        derivatives and variances.
        """
        quantity_a = Quantity("30 +- 9 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b / si.minute

        self.assertEqual(repr(ratio),
                         "<Quantity: (2 +- 0.6) m s^(-1) | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 81})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 4. / 60})

    def test_div_quantity_self_dep_error(self):
        """
        Check that dividing a dependent quantity by another quantity, returns
        a quantity with a ratio of the value and the propagated errors and
        the ratio of the two units. The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("8 +- 3.2 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        ratio = quantity_b / quantity_c

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m s^(-1) | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_c: 10.24})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_c: -40./64})

    def test_div_quantity_other_dep_error(self):
        """
        Check that dividing a quantity by another dependent quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("160 +- 48 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        ratio = quantity_a / quantity_c

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m s^(-1) | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 2304, qid_b: 10.24})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 1./32, qid_b: -40./64})

    def test_div_quantity_both_dep_errors(self):
        """
        Check that dividing a dependent quantity by another dependent
        quantity, returns a quantity with a ratio of the value and the
        propagated errors and the ratio of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("5 +- 1.5 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 2
        quantity_d = quantity_a * 16
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        ratio = quantity_d / quantity_c

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m s^(-1) | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 2.25, qid_b: 10.24})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 1, qid_b: -0.625})

    def test_div_quantity_two_numbers(self):
        """
        Check that dividing a number quantity by another quantity,
        returns a quantity with a ratio of the value if both quantities are
        dimensionless and error-less . The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        ratio = quantity_a / quantity_b

        self.assertEqual(repr(ratio), "<Quantity: 0.625>")
        self.assertEqual(ratio._variances, {})
        self.assertEqual(ratio._derivatives, {})

    def test_div_quantity_correation(self):
        """
        Check that the division of a quantity with itself honors the
        correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        ratio = quantity / quantity

        self.assertEqual(repr(ratio), "<Quantity: 1>")
        self.assertDictAlmostEqual(ratio._variances, {})
        self.assertDictAlmostEqual(ratio._derivatives, {})

    def test_div_quantity_correation_diamond(self):
        """
        Check that the division of a quantity which depend on the same
        quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        ratio = (quantity * 2) / (quantity * 4)

        self.assertEqual(repr(ratio), "<Quantity: 0.5>")
        self.assertDictAlmostEqual(ratio._variances, {})
        self.assertDictAlmostEqual(ratio._derivatives, {})

    def test_rdiv_type(self):
        """
        Check that dividing by a quantity returns a quantity.
        """
        quantity = 1.23 / Quantity("17 +- 3 m")
        self.assertIsInstance(quantity, Quantity)

    def test_rdiv_new(self):
        """
        Check that dividing by a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(1.23 / quantity, quantity)

    def test_rdiv_int(self):
        """
        Check that dividing an integer by a quantity, returns a quantity
        with a scaled value and error. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("5 +- 1 m")
        qid = quantity.qid()

        ratio = 15 / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (3 +- 0.6) m^(-1) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 1})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -0.6})

    def test_rdiv_int_auto_true_div(self):
        """
        Check that dividing an integer by an integer quantity, returns a quantity
        with a scaled, float value and error. Python 2.7 compatibility check.
        Dividing should always convert to floats.
        """
        quantity = Quantity("10 m")
        qid = quantity.qid()

        ratio = 4 / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: 0.4 m^(-1)>")
        self.assertDictAlmostEqual(ratio._variances, {})
        self.assertDictAlmostEqual(ratio._derivatives, {})

    def test_rdiv_float(self):
        """
        Check that dividing a quantity by a float, returns a quantity
        with a scaled value and error. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("0.5 +- 0.1 m")
        qid = quantity.qid()

        ratio = 15 / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (30 +- 6) m^(-1) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 0.01})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -60})

    def test_rdiv_negative(self):
        """
        Check that dividing a negative number by a quantity, returns a
        quantity with a scaled value and error. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("0.25 +- 2.5 m")
        qid = quantity.qid()

        ratio = -17 / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (-68 +- 680) m^(-1) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 6.25})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: 272})

    def test_rdiv_prefix(self):
        """
        Check that dividing a prefix by a quantity, returns a quantity with a
        scaled value and error. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("40 +- 4 m")
        qid = quantity.qid()

        ratio = si.kilo / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (25 +- 2.5) m^(-1) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 16})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -1/1.6})

    def test_rdiv_unit(self):
        """
        Check that dividing a unit by a quantity, returns a quantity with a
        scaled value and error and the ratio of the two units. The new
        quantity must store the derivative and the original variance of the
        quantity.
        """
        quantity = Quantity("20 +- 4 m")
        qid = quantity.qid()

        ratio = si.newton / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.05 +- 0.01) kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 16})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -0.0025})


    def test_rdiv_unit_w_history(self):
        """
        Check that dividing a derived unit by a quantity, returns a quantity
        with a scaled value and error and the ratio of the two units. The
        new quantity must store the derivative and the original variance of
        the quantity.
        """
        quantity = Quantity("20 +- 4 m")
        qid = quantity.qid()

        ratio = (si.newton * 2) / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.1 +- 0.02) kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 16})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -0.005})

    def test_rdiv_scaled_unit(self):
        """
        Check that dividing a scaled unit by a quantity, returns a
        quantity with a scaled value and error and the ratio of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("1200 +- 240 m")
        qid = quantity.qid()

        ratio = si.minute / quantity

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.05 +- 0.01) m^(-1) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(ratio._variances, {qid: 57600})
        self.assertDictAlmostEqual(ratio._derivatives, {qid: -1. / 24000})

    def test_rdiv_quantity_no_units(self):
        """
        Check that dividing a dimensionless quantity by another dimensionless
        quantity, returns a quantity with a ratio of the value and the
        propagated errors and the ratio of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: 5 +- 2.5 | depends=[%d, %d]>" % 
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_rdiv_quantity_self_unit(self):
        """
        Check that dividing a dimensionless quantity by another quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m N")
        quantity_b = Quantity("2 +- 0.8")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m^2 kg s^(-2) | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_rdiv_quantity_other_unit(self):
        """
        Check that dividing a quantity by another dimensionless quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = Quantity("2 +- 0.8 m N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m^(-2) kg^(-1) s^2 | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_rdiv_quantity_both_units(self):
        """
        Check that dividing a quantity by another quantity, returns a
        quantity with a ratio of the value and the propagated errors and the
        ratio of the two units. The new quantity must store the derivatives
        and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) kg^(-1) s^2 | depends=[%d, %d]>"
                         % (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})


    def test_rdiv_quantity_no_errors(self):
        """
        Check that dividing a error-less quantity by another error-less
        quantity, returns a quantity with a ratio of the value and the
        propagated errors and the ratio of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio), "<Quantity: 5 kg^(-1) s^2>")
        self.assertEqual(ratio._variances, {})
        self.assertEqual(ratio._derivatives, {})

    def test_rdiv_quantity_self_error(self):
        """
        Check that dividing a error-less quantity with another quantity,
        returns a quantity with a ratio of the value and the propagated errors
        and the ratio of the two units. The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 1.5) kg^(-1) s^2 | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5})

    def test_rdiv_quantity_other_error(self):
        """
        Check that dividing a quantity by another error-less quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2) kg^(-1) s^2 | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(ratio._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_b: -2.5})

    def test_rdiv_quantity_both_errors(self):
        """
        Check that dividing a quantity by another quantity, returns a quantity
        with a ratio of the value and the propagated errors and the ratio
        of the two units. The new quantity must store the derivatives and the
        original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 +- 0.8 N")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) kg^(-1) s^2 | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_b: 0.64})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_b: -2.5})

    def test_rdiv_quantity_dep_error_number(self):
        """
        Check that dividing a number by a dependent quantity returns a
        quantity with a ratio of the value and the propagated errors and the
        ratio of the two units. The new quantity must store the propagate
        its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = 1.6 / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.04 +- 0.012) m^(-1) | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: -0.004})

    def test_rdiv_quantity_dep_error_prefix(self):
        """
        Check that dividing a prefix by a dependent quantity by returns a
        quantity with a ratio of the value and the propagated errors and the
        ratio of the two units. The new quantity must store the propagate
        its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = si.kilo / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (25 +- 7.5) m^(-1) | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: -2.5})

    def test_rdiv_quantity_dep_error_unit(self):
        """
        Check that dividing a unit by a dependent quantity returns a quantity
        with a ratio of the value and the propagated errors and the ratio
        of the two units. The new quantity must store the propagate its
        derivatives and variances.
        """
        quantity_a = Quantity("30 +- 9 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        ratio = si.minute / quantity_b

        self.assertEqual(repr(ratio),
                         "<Quantity: (0.5 +- 0.15) m^(-1) s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 81})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: -1 / 60.})

    def test_rdiv_quantity_self_dep_error(self):
        """
        Check that dividing a quantity by another, dependent quantity, returns
        a quantity with a ratio of the value and the propagated errors and
        the ratio of the two units. The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("8 +- 3.2 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        ratio = quantity_c.__rtruediv__(quantity_b)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m s^(-1) | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 9, qid_c: 10.24})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 0.5, qid_c: -40./64})

    def test_rdiv_quantity_other_dep_error(self):
        """
        Check that dividing a dependent quantity by another quantity,
        returns a quantity with a ratio of the value and the propagated
        errors and the ratio of the two units. The new quantity must store
        the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("160 +- 48 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        ratio = quantity_c.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m s^(-1) | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 2304, qid_b: 10.24})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 1./32, qid_b: -40./64})

    def test_rdiv_quantity_both_dep_errors(self):
        """
        Check that dividing a dependent quantity by another dependent
        quantity, returns a quantity with a ratio of the value and the
        propagated errors and the ratio of the two units. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("5 +- 1.5 m")
        quantity_b = Quantity("8 +- 3.2 s")
        quantity_c = quantity_b * 2
        quantity_d = quantity_a * 16
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        ratio = quantity_c.__rtruediv__(quantity_d)

        self.assertEqual(repr(ratio),
                         "<Quantity: (5 +- 2.5) m s^(-1) | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(ratio._variances, {qid_a: 2.25, qid_b: 10.24})
        self.assertDictAlmostEqual(ratio._derivatives, {qid_a: 1, qid_b: -0.625})

    def test_rdiv_quantity_two_numbers(self):
        """
        Check that dividing a number quantity by another quantity,
        returns a quantity with a ratio of the value if both quantities are
        dimensionless and error-less . The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        ratio = quantity_b.__rtruediv__(quantity_a)

        self.assertEqual(repr(ratio), "<Quantity: 0.625>")
        self.assertEqual(ratio._variances, {})
        self.assertEqual(ratio._derivatives, {})

    def test_rdiv_quantity_correation(self):
        """
        Check that the division of a quantity with itself honors the
        correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        ratio = quantity.__rtruediv__(quantity)

        self.assertEqual(repr(ratio), "<Quantity: 1>")
        self.assertDictAlmostEqual(ratio._variances, {})
        self.assertDictAlmostEqual(ratio._derivatives, {})

    def test_rdiv_quantity_correation_diamond(self):
        """
        Check that the division of a quantity which depend on the same
        quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        ratio = (quantity * 4).__rtruediv__(quantity * 2)

        self.assertEqual(repr(ratio), "<Quantity: 0.5>")
        self.assertDictAlmostEqual(ratio._variances, {})
        self.assertDictAlmostEqual(ratio._derivatives, {})

    def test_idiv_negative(self):
        """
        Check that dividing (in-place) a quantity with a negative number,
        returns a quantity with a scaled value and error. The new quantity
        must store the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity
        product /= -0.25

        self.assertEqual(repr(product),
                         "<Quantity: (-68 +- 12) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: -4})

    def test_idiv_prefix(self):
        """
        Check that dividing (in-place) a quantity with a prefix, returns a
        quantity with a scaled value and error. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity
        product /= si.kilo

        self.assertEqual(repr(product),
                         "<Quantity: (0.017 +- 0.003) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 0.001})

    def test_idiv_unit(self):
        """
        Check that dividing (in-place) a quantity with a unit, returns a
        quantity with a scaled value and error and the product of the two
        units. The new quantity must store the derivative and the original
        variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        product = quantity
        product /= si.newton

        self.assertEqual(repr(product),
                         "<Quantity: (17 +- 3) kg^(-1) s^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(product._variances, {qid: 9})
        self.assertDictAlmostEqual(product._derivatives, {qid: 1})

    def test_idiv_quantity_correation_diamond(self):
        """
        Check that the multiplication (in-place) of a quantity which depend on
        the same quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        product = (quantity * 2)
        product /= (quantity * 4)

        self.assertEqual(repr(product), "<Quantity: 0.5>")
        self.assertDictAlmostEqual(product._variances, {})
        self.assertDictAlmostEqual(product._derivatives, {})

    def test_div_unit_system(self):
        """
        Check that the divisions check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a / b,
                          quantity_a, quantity_b)

    def test_rdiv_unit_system(self):
        """
        Check that the divisions check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a.__rtruediv__(b),
                          quantity_a, quantity_b)

class QuantityAddTestCase(QuantityArithmeticsHelper, unittest.TestCase):
    """
    Test case to test additions involving quantities.
    """

    def test_add_type(self):
        """
        Check that adding two a quantity returns a quantity.
        """
        quantity = Quantity("17 +- 3 m") + Quantity("1.3 +- 0.02 m")
        self.assertIsInstance(quantity, Quantity)

    def test_add_new(self):
        """
        Check that adding a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity + Quantity("1 m"), quantity)

    def test_add_int(self):
        """
        Check that adding a quantity and an integer, returns a quantity with a
        added values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = quantity + 5

        self.assertEqual(repr(sum),
                         "<Quantity: 20 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_add_float(self):
        """
        Check that adding a quantity and a float, returns a quantity with a
        added values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = quantity + 0.5

        self.assertEqual(repr(sum),
                         "<Quantity: 15.5 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_add_negative(self):
        """
        Check that adding a quantity and a negative number, returns a
        quantity with a summed value. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = quantity + (-0.25)

        self.assertEqual(repr(sum),
                         "<Quantity: 16.75 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_add_prefix(self):
        """
        Check that adding a quantity and a prefix, returns a quantity with a
        summed values. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = quantity + si.kilo

        self.assertEqual(repr(sum),
                         "<Quantity: 1017 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_add_unit(self):
        """
        Check that adding a quantity and a unit, returns a quantity with
        summed values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        sum = quantity + si.metre

        self.assertEqual(repr(sum),
                         "<Quantity: (18 +- 3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})


    def test_add_unit_w_history(self):
        """
        Check that adding a quantity and a derived unit, returns a quantity
        with a summed value. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 N")
        qid = quantity.qid()

        sum = quantity + (si.newton * 2)

        self.assertEqual(repr(sum),
                         "<Quantity: (19 +- 3) m kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_add_scaled_unit(self):
        """
        Check that adding a quantity and a scaled unit, returns a quantity
        with a summed values. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("330 +- 99 s")
        qid = quantity.qid()

        sum = quantity + si.minute

        self.assertEqual(repr(sum),
                         "<Quantity: (390 +- 99) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9801})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_add_quantity_no_errors(self):
        """
        Check that adding a error-less quantity and another error-less
        quantity, returns the summed of the values. The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10")
        quantity_b = Quantity("2")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a + quantity_b

        self.assertEqual(repr(sum), "<Quantity: 12>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_add_quantity_self_error(self):
        """
        Check that adding a quantity and another error-less quantity, returns
        a quantity with a sum of the values and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a + quantity_b

        self.assertEqual(repr(sum),
                         "<Quantity: (12 +- 3) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1})

    def test_add_quantity_other_error(self):
        """
        Check that adding a error-less quantity and another quantity, returns
        a quantity with a sum of the values and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 s")
        quantity_b = Quantity("2 +- 0.8 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a + quantity_b

        self.assertEqual(repr(sum),
                         "<Quantity: (12 +- 0.8) s | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(sum._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(sum._derivatives, {qid_b: 1})

    def test_add_quantity_both_errors(self):
        """
        Check that adding a quantity by another quantity, returns a quantity
        with a sum of the values and the propagated errors. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 kg")
        quantity_b = Quantity("29 +- 4 kg")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a + quantity_b

        self.assertEqual(repr(sum),
                         "<Quantity: (39 +- 5) kg | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_b: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1, qid_b: 1})

    def test_add_quantity_dep_error_number(self):
        """
        Check that adding a dependent quantity and a number returns a quantity
        with a sum of the value and the propagated errors. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b + Quantity("7 m")

        self.assertEqual(repr(sum),
                         "<Quantity: (47 +- 12) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_add_quantity_dep_error_prefix(self):
        """
        Check that adding a dependent quantity and a prefix returns a quantity
        with a sum of the value and the propagated errors. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b + si.kilo

        self.assertEqual(repr(sum),
                         "<Quantity: 1040 +- 12 | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_add_quantity_dep_error_unit(self):
        """
        Check that adding a dependent quantity and a unit returns a quantity
        with a sum of the value and the propagated errors. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("30 +- 9 s")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b + si.minute

        self.assertEqual(repr(sum),
                         "<Quantity: (180 +- 36) s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 81})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_add_quantity_self_dep_error(self):
        """
        Check that adding a dependent quantity and another quantity, returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("80 +- 16 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_b + quantity_c

        self.assertEqual(repr(sum),
                         "<Quantity: (120 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_c: 256})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4, qid_c: 1})

    def test_add_quantity_other_dep_error(self):
        """
        Check that adding a quantity and another dependent quantity, returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("80 +- 16 m")
        quantity_b = Quantity("10 +- 3 m")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_a + quantity_c

        self.assertEqual(repr(sum),
                         "<Quantity: (120 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 256, qid_b: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1, qid_b: 4})

    def test_add_quantity_both_dep_errors(self):
        """
        Check that adding a dependent quantity by another dependent quantity,
        returns a quantity with a sum of the value. The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("54 +- 12 m")
        quantity_b = Quantity("20 +- 6 m")
        quantity_c = quantity_b * 3
        quantity_d = quantity_a * 2
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_d + quantity_c

        self.assertEqual(repr(sum),
                         "<Quantity: (168 +- 30) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 144, qid_b: 36})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 2, qid_b: 3})

    def test_add_quantity_two_numbers(self):
        """
        Check that adding a number quantity by another quantity,
        returns a quantity with a sum of the value if both quantities are
        dimensionless and error-less. The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        sum = quantity_a + quantity_b

        self.assertEqual(repr(sum), "<Quantity: 13>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_add_quantity_correation(self):
        """
        Check that the sum of a quantities and itself honors the
        correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = quantity + quantity

        self.assertEqual(repr(sum),
            "<Quantity: (20 +- 8) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 2})

    def test_add_quantity_correation_diamond(self):
        """
        Check that the sum of quantities which depend on the same
        quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = (quantity * 2) + (quantity * 4)

        self.assertEqual(repr(sum),
            "<Quantity: (60 +- 24) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 6})

    def test_add_quantity_dimensionless_dimensionless(self):
        """
        Check that adding a two dimensionless quantity return the sum of the
        values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = quantity + Quantity("3 rad")

        self.assertEqual(repr(sum), "<Quantity: 18 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_add_quantity_unit_scalar(self):
        """
        Check that adding a quantity with a unit and a scalar raises an
        exception.
        """
        self.assertRaises(ValueError, lambda a, b: a + b,
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: a + b,
                         Quantity("3 m"), Quantity("1"))

    def test_add_quantity_unit_otherunit(self):
        """
        Check that adding a quantity with a unit and a quantity with a
        different unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a + b,
                         Quantity("3 m"), Quantity("1 s"))

    def test_add_quantity_unit_dimensionless(self):
        """
        Check that adding a quantity with a unit and a quantity with a
        dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a + b,
                         Quantity("3 m"), Quantity("1 rad"))

    def test_add_quantity_dimensionless_scalar(self):
        """
        Check that adding a quantity with a dimensionless unit and a scalar
        raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()


        sum = quantity + 5

        self.assertEqual(repr(sum),
                         "<Quantity: 20 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})


        sum = quantity + Quantity("1")

        self.assertEqual(repr(sum), "<Quantity: 16 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_add_quantity_scalar_unit(self):
        """
        Check that adding a quantity with a unit and a scalar raises an
        exception.
        """
        self.assertRaises(ValueError, lambda a, b: b + a,
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: b + a,
                         Quantity("3 m"), Quantity("1"))

    def test_add_quantity_dimensionless_unit(self):
        """
        Check that adding a quantity with a unit and a quantity with a
        dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: b + a,
                         Quantity("3 m"), Quantity("1 rad"))

    def test_add_quantity_scalar_dimensionless(self):
        """
        Check that adding a quantity with a dimensionless unit and a scalar
        raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = Quantity("1") + quantity

        self.assertEqual(repr(sum), "<Quantity: 16 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})


    def test_radd_type(self):
        """
        Check that adding (form the left) two a quantity returns a quantity.
        """
        quantity = Quantity("17 +- 3 m").__radd__(Quantity("1.3 +- 0.02 m"))
        self.assertIsInstance(quantity, Quantity)

    def test_radd_new(self):
        """
        Check that adding (form the left) a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity.__radd__(Quantity("1 m")), quantity)

    def test_radd_int(self):
        """
        Check that adding (form the left) a quantity and an integer, returns a quantity with a
        added values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = 5 + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: 20 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_radd_float(self):
        """
        Check that adding (form the left) a quantity and a float, returns a quantity with a
        added values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = 0.5 + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: 15.5 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_radd_negative(self):
        """
        Check that adding (form the left) a quantity and a negative number, returns a
        quantity with a summed value. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = (-0.25) + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: 16.75 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_radd_prefix(self):
        """
        Check that adding (form the left) a quantity and a prefix, returns a quantity with a
        summed values. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = si.kilo + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: 1017 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_radd_unit(self):
        """
        Check that adding (form the left) a quantity and a unit, returns a quantity with
        summed values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        sum = si.metre + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: (18 +- 3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})


    def test_radd_unit_w_history(self):
        """
        Check that adding (form the left) a quantity and a derived unit, returns a quantity
        with a summed value. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 N")
        qid = quantity.qid()

        sum = (si.newton * 2) + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: (19 +- 3) m kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_radd_scaled_unit(self):
        """
        Check that adding (form the left) a quantity and a scaled unit, returns a quantity
        with a summed values. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("330 +- 99 s")
        qid = quantity.qid()

        sum = si.minute + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: (390 +- 99) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9801})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_radd_quantity_no_errors(self):
        """
        Check that adding (form the left) a error-less quantity and another error-less
        quantity, returns the summed of the values. The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10")
        quantity_b = Quantity("2")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__radd__(quantity_b)

        self.assertEqual(repr(sum), "<Quantity: 12>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_radd_quantity_self_error(self):
        """
        Check that adding (form the left) a quantity and another error-less quantity, returns
        a quantity with a sum of the values and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__radd__(quantity_b)

        self.assertEqual(repr(sum),
                         "<Quantity: (12 +- 3) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1})

    def test_radd_quantity_other_error(self):
        """
        Check that adding (form the left) a error-less quantity and another quantity, returns
        a quantity with a sum of the values and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 s")
        quantity_b = Quantity("2 +- 0.8 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__radd__(quantity_b)

        self.assertEqual(repr(sum),
                         "<Quantity: (12 +- 0.8) s | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(sum._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(sum._derivatives, {qid_b: 1})

    def test_radd_quantity_both_errors(self):
        """
        Check that adding (form the left) a quantity by another quantity, returns a quantity
        with a sum of the values and the propagated errors. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 kg")
        quantity_b = Quantity("29 +- 4 kg")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__radd__(quantity_b)

        self.assertEqual(repr(sum),
                         "<Quantity: (39 +- 5) kg | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_b: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1, qid_b: 1})

    def test_radd_quantity_dep_error_number(self):
        """
        Check that adding (form the left) a dependent quantity and a number returns a quantity
        with a sum of the value and the propagated errors. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b.__radd__(Quantity("7 m"))

        self.assertEqual(repr(sum),
                         "<Quantity: (47 +- 12) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_radd_quantity_dep_error_prefix(self):
        """
        Check that adding (form the left) a dependent quantity and a prefix returns a quantity
        with a sum of the value and the propagated errors. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b.__radd__(si.kilo)

        self.assertEqual(repr(sum),
                         "<Quantity: 1040 +- 12 | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_radd_quantity_dep_error_unit(self):
        """
        Check that adding (form the left) a dependent quantity and a unit returns a quantity
        with a sum of the value and the propagated errors. The new quantity
        must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("30 +- 9 s")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b.__radd__(si.minute)

        self.assertEqual(repr(sum),
                         "<Quantity: (180 +- 36) s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 81})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_radd_quantity_self_dep_error(self):
        """
        Check that adding (form the left) a dependent quantity and another quantity, returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("80 +- 16 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_b.__radd__(quantity_c)

        self.assertEqual(repr(sum),
                         "<Quantity: (120 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_c: 256})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4, qid_c: 1})

    def test_radd_quantity_other_dep_error(self):
        """
        Check that adding (form the left) a quantity and another dependent quantity, returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("80 +- 16 m")
        quantity_b = Quantity("10 +- 3 m")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_a.__radd__(quantity_c)

        self.assertEqual(repr(sum),
                         "<Quantity: (120 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 256, qid_b: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1, qid_b: 4})

    def test_radd_quantity_both_dep_errors(self):
        """
        Check that adding (form the left) a dependent quantity by another dependent quantity,
        returns a quantity with a sum of the value. The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("54 +- 12 m")
        quantity_b = Quantity("20 +- 6 m")
        quantity_c = quantity_b * 3
        quantity_d = quantity_a * 2
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_d.__radd__(quantity_c)

        self.assertEqual(repr(sum),
                         "<Quantity: (168 +- 30) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 144, qid_b: 36})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 2, qid_b: 3})

    def test_radd_quantity_two_numbers(self):
        """
        Check that adding (form the left) a number quantity by another quantity,
        returns a quantity with a sum of the value if both quantities are
        dimensionless and error-less. The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        sum = quantity_a.__radd__(quantity_b)

        self.assertEqual(repr(sum), "<Quantity: 13>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_radd_quantity_correation(self):
        """
        Check that the sum of a quantities and itself honors the
        correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = quantity.__radd__(quantity)

        self.assertEqual(repr(sum),
            "<Quantity: (20 +- 8) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 2})

    def test_radd_quantity_correation_diamond(self):
        """
        Check that the sum of quantities which depend on the same
        quantity honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = (quantity * 2) + (quantity * 4)

        self.assertEqual(repr(sum),
            "<Quantity: (60 +- 24) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 6})

    def test_radd_quantity_dimensionless_dimensionless(self):
        """
        Check that adding (form the left) a two dimensionless quantity return the sum of the
        values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = quantity.__radd__(Quantity("3 rad"))

        self.assertEqual(repr(sum), "<Quantity: 18 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_radd_quantity_unit_scalar(self):
        """
        Check that adding (form the left) a quantity with a unit and a scalar raises an
        exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__radd__(b),
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: a.__radd__(b),
                         Quantity("3 m"), Quantity("1"))

    def test_radd_quantity_unit_otherunit(self):
        """
        Check that adding (form the left) a quantity with a unit and a quantity with a
        different unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__radd__(b),
                         Quantity("3 m"), Quantity("1 s"))

    def test_radd_quantity_unit_dimensionless(self):
        """
        Check that adding (form the left) a quantity with a unit and a quantity with a
        dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__radd__(b),
                         Quantity("3 m"), Quantity("1 rad"))

    def test_radd_quantity_dimensionless_scalar(self):
        """
        Check that adding (form the left) a quantity with a dimensionless unit and a scalar
        raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()


        sum = 5 + quantity

        self.assertEqual(repr(sum),
                         "<Quantity: 20 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})


        sum = quantity.__radd__(Quantity("1"))

        self.assertEqual(repr(sum), "<Quantity: 16 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_radd_quantity_scalar_unit(self):
        """
        Check that adding (form the left) a quantity with a unit and a scalar raises an
        exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__radd__(b),
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: a.__radd__(b),
                         Quantity("3 m"), Quantity("1"))

    def test_radd_quantity_dimensionless_unit(self):
        """
        Check that adding (form the left) a quantity with a unit and a quantity with a
        dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: b.__radd__(a),
                         Quantity("3 m"), Quantity("1 rad"))

    def test_radd_quantity_scalar_dimensionless(self):
        """
        Check that adding (form the left) a quantity with a dimensionless unit and a scalar
        raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = Quantity("1") + quantity

        self.assertEqual(repr(sum), "<Quantity: 16 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_add_unit_system(self):
        """
        Check that the additions check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a + b,
                          quantity_a, quantity_b)

    def test_radd_unit_system(self):
        """
        Check that the additions check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a.__radd__(b),
                          quantity_a, quantity_b)

class QuantitySubTestCase(QuantityArithmeticsHelper, unittest.TestCase):
    """
    Test case to test subtractions involving quantities.
    """

    def test_sub_type(self):
        """
        Check that subtracting two quantities returns a quantity.
        """
        quantity = Quantity("17 +- 3 m") - Quantity("1.3 +- 0.02 m")
        self.assertIsInstance(quantity, Quantity)

    def test_sub_new(self):
        """
        Check that subtracting a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity - Quantity("1 m"), quantity)

    def test_sub_int(self):
        """
        Check that subtracting a quantity and an integer, returns a quantity
        with a added values. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = quantity - 5

        self.assertEqual(repr(sum),
                         "<Quantity: 10 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_sub_float(self):
        """
        Check that subtracting a quantity and a float, returns a quantity with
        a added values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = quantity - 0.5

        self.assertEqual(repr(sum),
                         "<Quantity: 14.5 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_sub_negative(self):
        """
        Check that subtracting a quantity and a negative number, returns a
        quantity with a summed value. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = quantity - (-0.25)

        self.assertEqual(repr(sum),
                         "<Quantity: 17.25 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_sub_prefix(self):
        """
        Check that subtracting a quantity and a prefix, returns a quantity
        with a summed values. The new quantity must store the derivative and
        the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = quantity - si.kilo

        self.assertEqual(repr(sum),
                         "<Quantity: -983 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_sub_unit(self):
        """
        Check that subtracting a quantity and a unit, returns a quantity with
        summed values. The new quantity must store the derivative and the
        original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        sum = quantity - si.metre

        self.assertEqual(repr(sum),
                         "<Quantity: (16 +- 3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})


    def test_sub_unit_w_history(self):
        """
        Check that subtracting a quantity and a derived unit, returns a
        quantity with a summed value. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 N")
        qid = quantity.qid()

        sum = quantity - (si.newton * 2)

        self.assertEqual(repr(sum),
                         "<Quantity: (15 +- 3) m kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_sub_scaled_unit(self):
        """
        Check that subtracting a quantity and a scaled unit, returns a
        quantity with a summed values. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("330 +- 99 s")
        qid = quantity.qid()

        sum = quantity - si.minute

        self.assertEqual(repr(sum),
                         "<Quantity: (270 +- 99) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9801})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 1})

    def test_sub_quantity_no_errors(self):
        """
        Check that subtracting a error-less quantity and another error-less
        quantity, returns the summed of the values. The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("10")
        quantity_b = Quantity("2")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a - quantity_b

        self.assertEqual(repr(sum), "<Quantity: 8>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_sub_quantity_self_error(self):
        """
        Check that subtracting a quantity and another error-less quantity,
        returns a quantity with a sum of the values and the propagated errors.
        The new quantity must store the derivatives and the original variances
        of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a - quantity_b

        self.assertEqual(repr(sum),
                         "<Quantity: (8 +- 3) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1})

    def test_sub_quantity_other_error(self):
        """
        Check that subtracting a error-less quantity and another quantity,
        returns a quantity with a sum of the values and the propagated errors.
        The new quantity must store the derivatives and the original variances
        of the quantities.
        """
        quantity_a = Quantity("10 s")
        quantity_b = Quantity("2 +- 0.8 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a - quantity_b

        self.assertEqual(repr(sum),
                         "<Quantity: (8 +- 0.8) s | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(sum._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(sum._derivatives, {qid_b: -1})

    def test_sub_quantity_both_errors(self):
        """
        Check that subtracting a quantity by another quantity, returns a
        quantity with a sum of the values and the propagated errors. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10 +- 3 kg")
        quantity_b = Quantity("29 +- 4 kg")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a - quantity_b

        self.assertEqual(repr(sum),
                         "<Quantity: (-19 +- 5) kg | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_b: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1, qid_b: -1})

    def test_sub_quantity_dep_error_number(self):
        """
        Check that subtracting a dependent quantity and a number returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b - Quantity("7 m")

        self.assertEqual(repr(sum),
                         "<Quantity: (33 +- 12) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_sub_quantity_dep_error_prefix(self):
        """
        Check that subtracting a dependent quantity and a prefix returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b - si.kilo

        self.assertEqual(repr(sum),
                         "<Quantity: -960 +- 12 | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_sub_quantity_dep_error_unit(self):
        """
        Check that subtracting a dependent quantity and a unit returns a
        quantity with a sum of the value and the propagated errors. The new
        quantity must store the propagate its derivatives and variances.
        """
        quantity_a = Quantity("30 +- 9 s")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b - si.minute

        self.assertEqual(repr(sum),
                         "<Quantity: (60 +- 36) s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 81})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4})

    def test_sub_quantity_self_dep_error(self):
        """
        Check that subtracting a dependent quantity and another quantity,
        returns a quantity with a sum of the value and the propagated errors.
        The new quantity must store the derivatives and the original variances
        of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("80 +- 16 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_b - quantity_c

        self.assertEqual(repr(sum),
                         "<Quantity: (-40 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_c: 256})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 4, qid_c: -1})

    def test_sub_quantity_other_dep_error(self):
        """
        Check that subtracting a quantity and another dependent quantity,
        returns a quantity with a sum of the value and the propagated errors.
        The new quantity must store the derivatives and the original variances
        of the quantities.
        """
        quantity_a = Quantity("80 +- 16 m")
        quantity_b = Quantity("10 +- 3 m")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_a - quantity_c

        self.assertEqual(repr(sum),
                         "<Quantity: (40 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 256, qid_b: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 1, qid_b: -4})

    def test_sub_quantity_both_dep_errors(self):
        """
        Check that subtracting a dependent quantity by another dependent
        quantity, returns a quantity with a sum of the value. The new quantity
        must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("54 +- 12 m")
        quantity_b = Quantity("20 +- 6 m")
        quantity_c = quantity_b * 3
        quantity_d = quantity_a * 2
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_d - quantity_c

        self.assertEqual(repr(sum),
                         "<Quantity: (48 +- 30) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 144, qid_b: 36})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: 2, qid_b: -3})

    def test_sub_quantity_two_numbers(self):
        """
        Check that subtracting a number quantity by another quantity, returns
        a quantity with a sum of the value if both quantities are
        dimensionless and error-less. The new quantity must store the
        derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        sum = quantity_a - quantity_b

        self.assertEqual(repr(sum), "<Quantity: -3>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_sub_quantity_correation(self):
        """
        Check that the sum of a quantities and itself honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = quantity - quantity

        self.assertEqual(repr(sum), "<Quantity: 0 s>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_sub_quantity_correation_diamond(self):
        """
        Check that the sum of quantities which depend on the same quantity
        honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = (quantity * 2) - (quantity * 4)

        self.assertEqual(repr(sum),
            "<Quantity: (-20 +- 8) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -2})

    def test_sub_quantity_dimensionless_dimensionless(self):
        """
        Check that subtracting a two dimensionless quantity return the sum of
        the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = quantity - Quantity("3 rad")

        self.assertEqual(repr(sum), "<Quantity: 12 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_sub_quantity_unit_scalar(self):
        """
        Check that subtracting a quantity with a unit and a scalar raises an
        exception.
        """
        self.assertRaises(ValueError, lambda a, b: a - b,
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: a - b,
                         Quantity("3 m"), Quantity("1"))

    def test_sub_quantity_unit_otherunit(self):
        """
        Check that subtracting a quantity with a unit and a quantity with a
        different unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a - b,
                         Quantity("3 m"), Quantity("1 s"))

    def test_sub_quantity_unit_dimensionless(self):
        """
        Check that subtracting a quantity with a unit and a quantity with a
        dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a - b,
                         Quantity("3 m"), Quantity("1 rad"))

    def test_sub_quantity_dimensionless_scalar(self):
        """
        Check that subtracting a quantity with a dimensionless unit and a
        scalar raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()


        sum = quantity - 5

        self.assertEqual(repr(sum),
                         "<Quantity: 10 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})


        sum = quantity - Quantity("1")

        self.assertEqual(repr(sum), "<Quantity: 14 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_sub_quantity_scalar_unit(self):
        """
        Check that subtracting a quantity with a unit and a scalar raises an
        exception.
        """
        self.assertRaises(ValueError, lambda a, b: b - a,
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: b - a,
                         Quantity("3 m"), Quantity("1"))

    def test_sub_quantity_dimensionless_unit(self):
        """
        Check that subtracting a quantity with a unit and a quantity with a
        dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: b - a,
                         Quantity("3 m"), Quantity("1 rad"))

    def test_sub_quantity_scalar_dimensionless(self):
        """
        Check that subtracting a quantity with a dimensionless unit and a
        scalar raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = Quantity("1") - quantity

        self.assertEqual(repr(sum), "<Quantity: -14 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})


    def test_rsub_type(self):
        """
        Check that subtracting (form the left) two a quantity returns a quantity.
        """
        quantity = Quantity("17 +- 3 m").__rsub__(Quantity("1.3 +- 0.02 m"))
        self.assertIsInstance(quantity, Quantity)

    def test_rsub_new(self):
        """
        Check that subtracting (form the left) a quantity returns a new object.
        """
        quantity = Quantity("17 +- 3 m")
        self.assertIsNot(quantity.__rsub__(Quantity("1 m")), quantity)

    def test_rsub_int(self):
        """
        Check that subtracting (form the left) a quantity and an integer,
        returns a quantity with a added values. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = 5 - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: -10 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})

    def test_rsub_float(self):
        """
        Check that subtracting (form the left) a quantity and a float, returns
        a quantity with a added values. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        sum = 0.5 - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: -14.5 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})

    def test_rsub_negative(self):
        """
        Check that subtracting (form the left) a quantity and a negative
        number, returns a quantity with a summed value. The new quantity must
        store the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = (-0.25) - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: -17.25 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})

    def test_rsub_prefix(self):
        """
        Check that subtracting (form the left) a quantity and a prefix,
        returns a quantity with a summed values. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3")
        qid = quantity.qid()

        sum = si.kilo - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: 983 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})

    def test_rsub_unit(self):
        """
        Check that subtracting (form the left) a quantity and a unit, returns
        a quantity with summed values. The new quantity must store the
        derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 m")
        qid = quantity.qid()

        sum = si.metre - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: (-16 +- 3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})


    def test_rsub_unit_w_history(self):
        """
        Check that subtracting (form the left) a quantity and a derived unit,
        returns a quantity with a summed value. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("17 +- 3 N")
        qid = quantity.qid()

        sum = (si.newton * 2) - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: (-15 +- 3) m kg s^(-2) | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})

    def test_rsub_scaled_unit(self):
        """
        Check that subtracting (form the left) a quantity and a scaled unit,
        returns a quantity with a summed values. The new quantity must store
        the derivative and the original variance of the quantity.
        """
        quantity = Quantity("330 +- 99 s")
        qid = quantity.qid()

        sum = si.minute - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: (-270 +- 99) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 9801})
        self.assertDictAlmostEqual(sum._derivatives, {qid: -1})

    def test_rsub_quantity_no_errors(self):
        """
        Check that subtracting (form the left) a error-less quantity and
        another error-less quantity, returns the summed of the values. The new
        quantity must store the derivatives and the original variances of the
        quantities.
        """
        quantity_a = Quantity("10")
        quantity_b = Quantity("2")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__rsub__(quantity_b)

        self.assertEqual(repr(sum), "<Quantity: -8>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_rsub_quantity_self_error(self):
        """
        Check that subtracting (form the left) a quantity and another
        error-less quantity, returns a quantity with a sum of the values and
        the propagated errors. The new quantity must store the derivatives and
        the original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = Quantity("2 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__rsub__(quantity_b)

        self.assertEqual(repr(sum),
                         "<Quantity: (-8 +- 3) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -1})

    def test_rsub_quantity_other_error(self):
        """
        Check that subtracting (form the left) a error-less quantity and
        another quantity, returns a quantity with a sum of the values and the
        propagated errors. The new quantity must store the derivatives and the
        original variances of the quantities.
        """
        quantity_a = Quantity("10 s")
        quantity_b = Quantity("2 +- 0.8 s")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__rsub__(quantity_b)

        self.assertEqual(repr(sum),
                         "<Quantity: (-8 +- 0.8) s | depends=[%d]>" % qid_b)
        self.assertDictAlmostEqual(sum._variances, {qid_b: 0.64})
        self.assertDictAlmostEqual(sum._derivatives, {qid_b: 1})

    def test_rsub_quantity_both_errors(self):
        """
        Check that subtracting (form the left) a quantity by another quantity,
        returns a quantity with a sum of the values and the propagated errors.
        The new quantity must store the derivatives and the original variances
        of the quantities.
        """
        quantity_a = Quantity("10 +- 3 kg")
        quantity_b = Quantity("29 +- 4 kg")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_a.__rsub__(quantity_b)

        self.assertEqual(repr(sum),
                         "<Quantity: (19 +- 5) kg | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_b: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -1, qid_b: 1})

    def test_rsub_quantity_dep_error_number(self):
        """
        Check that subtracting (form the left) a dependent quantity and a
        number returns a quantity with a sum of the value and the propagated
        errors. The new quantity must store the propagate its derivatives and
        variances.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b.__rsub__(Quantity("7 m"))

        self.assertEqual(repr(sum),
                         "<Quantity: (-33 +- 12) m | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -4})

    def test_rsub_quantity_dep_error_prefix(self):
        """
        Check that subtracting (form the left) a dependent quantity and a
        prefix returns a quantity with a sum of the value and the propagated
        errors. The new quantity must store the propagate its derivatives and
        variances.
        """
        quantity_a = Quantity("10 +- 3")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b.__rsub__(si.kilo)

        self.assertEqual(repr(sum),
                         "<Quantity: 960 +- 12 | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -4})

    def test_rsub_quantity_dep_error_unit(self):
        """
        Check that subtracting (form the left) a dependent quantity and a unit
        returns a quantity with a sum of the value and the propagated errors.
        The new quantity must store the propagate its derivatives and
        variances.
        """
        quantity_a = Quantity("30 +- 9 s")
        quantity_b = quantity_a * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()

        sum = quantity_b.__rsub__(si.minute)

        self.assertEqual(repr(sum),
                         "<Quantity: (-60 +- 36) s | depends=[%d]>" % qid_a)
        self.assertDictAlmostEqual(sum._variances, {qid_a: 81})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -4})

    def test_rsub_quantity_self_dep_error(self):
        """
        Check that subtracting (form the left) a dependent quantity and
        another quantity, returns a quantity with a sum of the value and the
        propagated errors. The new quantity must store the derivatives and the
        original variances of the quantities.
        """
        quantity_a = Quantity("10 +- 3 m")
        quantity_b = quantity_a * 4
        quantity_c = Quantity("80 +- 16 m")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_b.__rsub__(quantity_c)

        self.assertEqual(repr(sum),
                         "<Quantity: (40 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_c))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 9, qid_c: 256})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -4, qid_c: 1})

    def test_rsub_quantity_other_dep_error(self):
        """
        Check that subtracting (form the left) a quantity and another
        dependent quantity, returns a quantity with a sum of the value and the
        propagated errors. The new quantity must store the derivatives and the
        original variances of the quantities.
        """
        quantity_a = Quantity("80 +- 16 m")
        quantity_b = Quantity("10 +- 3 m")
        quantity_c = quantity_b * 4
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_a.__rsub__(quantity_c)

        self.assertEqual(repr(sum),
                         "<Quantity: (-40 +- 20) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 256, qid_b: 9})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -1, qid_b: 4})

    def test_rsub_quantity_both_dep_errors(self):
        """
        Check that subtracting (form the left) a dependent quantity by another
        dependent quantity, returns a quantity with a sum of the value. The
        new quantity must store the derivatives and the original variances of
        the quantities.
        """
        quantity_a = Quantity("54 +- 12 m")
        quantity_b = Quantity("20 +- 6 m")
        quantity_c = quantity_b * 3
        quantity_d = quantity_a * 2
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        qid_c = quantity_c.qid()

        sum = quantity_d.__rsub__(quantity_c)

        self.assertEqual(repr(sum),
                         "<Quantity: (-48 +- 30) m | depends=[%d, %d]>" %
                         (qid_a, qid_b))
        self.assertDictAlmostEqual(sum._variances, {qid_a: 144, qid_b: 36})
        self.assertDictAlmostEqual(sum._derivatives, {qid_a: -2, qid_b: 3})

    def test_rsub_quantity_two_numbers(self):
        """
        Check that subtracting (form the left) a number quantity by another
        quantity, returns a quantity with a sum of the value if both
        quantities are dimensionless and error-less. The new quantity must
        store the derivatives and the original variances of the quantities.
        """
        quantity_a = Quantity("5")
        quantity_b = Quantity("8")

        sum = quantity_a.__rsub__(quantity_b)

        self.assertEqual(repr(sum), "<Quantity: 3>")
        self.assertEqual(sum._variances, {})
        self.assertEqual(sum._derivatives, {})

    def test_rsub_quantity_correation(self):
        """
        Check that the sum of a quantities and itself honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = quantity.__rsub__(quantity)

        self.assertEqual(repr(sum), "<Quantity: 0 s>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_rsub_quantity_correation_diamond(self):
        """
        Check that the sum of quantities which depend on the same quantity
        honors the correlation.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        sum = (quantity * 2).__rsub__(quantity * 4)

        self.assertEqual(repr(sum),
            "<Quantity: (20 +- 8) s | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(sum._variances, {qid: 16})
        self.assertDictAlmostEqual(sum._derivatives, {qid: 2})

    def test_rsub_quantity_dimensionless_dimensionless(self):
        """
        Check that subtracting (form the left) a two dimensionless quantity
        return the sum of the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = quantity.__rsub__(Quantity("3 rad"))

        self.assertEqual(repr(sum), "<Quantity: -12 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_rsub_quantity_unit_scalar(self):
        """
        Check that subtracting (form the left) a quantity with a unit and a
        scalar raises an exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__rsub__(b),
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: a.__rsub__(b),
                         Quantity("3 m"), Quantity("1"))

    def test_rsub_quantity_unit_otherunit(self):
        """
        Check that subtracting (form the left) a quantity with a unit and a
        quantity with a different unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__rsub__(b),
                         Quantity("3 m"), Quantity("1 s"))

    def test_rsub_quantity_unit_dimensionless(self):
        """
        Check that subtracting (form the left) a quantity with a unit and a
        quantity with a dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__rsub__(b),
                         Quantity("3 m"), Quantity("1 rad"))

    def test_rsub_quantity_dimensionless_scalar(self):
        """
        Check that subtracting (form the left) a quantity with a dimensionless
        unit and a scalar raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()


        sum = 5 - quantity

        self.assertEqual(repr(sum),
                         "<Quantity: -10 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})


        sum = quantity.__rsub__(Quantity("1"))

        self.assertEqual(repr(sum), "<Quantity: -14 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_rsub_quantity_scalar_unit(self):
        """
        Check that subtracting (form the left) a quantity with a unit and a
        scalar raises an exception.
        """
        self.assertRaises(ValueError, lambda a, b: a.__rsub__(b),
                         Quantity("3 m"), 1)
        self.assertRaises(ValueError, lambda a, b: a.__rsub__(b),
                         Quantity("3 m"), Quantity("1"))

    def test_rsub_quantity_dimensionless_unit(self):
        """
        Check that subtracting (form the left) a quantity with a unit and a
        quantity with a dimensionless unit raises exception.
        """
        self.assertRaises(ValueError, lambda a, b: b.__rsub__(a),
                         Quantity("3 m"), Quantity("1 rad"))

    def test_rsub_quantity_scalar_dimensionless(self):
        """
        Check that subtracting (form the left) a quantity with a dimensionless
        unit and a scalar raises sums the values.
        """
        quantity = Quantity("15 rad")
        qid = quantity.qid()

        sum = Quantity("1").__rsub__(quantity)

        self.assertEqual(repr(sum), "<Quantity: 14 rad>")
        self.assertDictAlmostEqual(sum._variances, {})
        self.assertDictAlmostEqual(sum._derivatives, {})

    def test_sub_unit_system(self):
        """
        Check that the subtractions check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a - b,
                          quantity_a, quantity_b)

    def test_rsub_unit_system(self):
        """
        Check that the subtractions check the unit system.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4 s")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a.__rsub__(b),
                          quantity_a, quantity_b)


class QuantityNegTestCase(QuantityArithmeticsHelper, unittest.TestCase):
    """
    Test the negation of a quantity.
    """

    def test_neg_type(self):
        """
        Check that negating a quantity returns a quantity.
        """
        quantity = Quantity("15 +- 3 m")

        negative = -quantity
        self.assertIsInstance(negative, Quantity)

    def test_neg_new(self):
        """
        Check that negating a quantity returns a different quantity.
        """
        quantity = Quantity("15 +- 3 m")
        qid = quantity.qid()

        negative = -quantity
        self.assertNotEqual(negative.qid(), qid)

    def test_neg_scalar_quantity(self):
        """
        Check that negating a scalar quantity negates its value.
        """
        quantity = Quantity("15")
        qid = quantity.qid()

        negative = -quantity

        self.assertEqual(repr(negative), "<Quantity: -15>")
        self.assertDictAlmostEqual(negative._variances, {})
        self.assertDictAlmostEqual(negative._derivatives, {})

    def test_neg_quantity_w_unit(self):
        """
        Check that negating a quantity with a unit negates its value.
        """
        quantity = Quantity("15 m")
        qid = quantity.qid()

        negative = -quantity

        self.assertEqual(repr(negative), "<Quantity: -15 m>")
        self.assertDictAlmostEqual(negative._variances, {})
        self.assertDictAlmostEqual(negative._derivatives, {})

    def test_neg_quantity_w_error(self):
        """
        Check that negating a quantity with an error negates its value.
        """
        quantity = Quantity("15 +- 3")
        qid = quantity.qid()

        negative = -quantity

        self.assertEqual(repr(negative),
                         "<Quantity: -15 +- 3 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(negative._variances, {qid: 9})
        self.assertDictAlmostEqual(negative._derivatives, {qid: -1})

    def test_neg_quantity_w_unit_error(self):
        """
        Check that negating a quantity with a unit and an error negates its
        value.
        """
        quantity = Quantity("15 +- 3 m")
        qid = quantity.qid()

        negative = -quantity

        self.assertEqual(repr(negative),
                         "<Quantity: (-15 +- 3) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(negative._variances, {qid: 9})
        self.assertDictAlmostEqual(negative._derivatives, {qid: -1})

    def test_neg_dependent_quantity(self):
        """
        Check that negating a dependent quantity negates its value.
        """
        quantity_a = Quantity("15 +- 3 m")
        qid = quantity_a.qid()
        quantity_b = quantity_a * 6

        negative = -quantity_b

        self.assertEqual(repr(negative),
                         "<Quantity: (-90 +- 18) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(negative._variances, {qid: 9})
        self.assertDictAlmostEqual(negative._derivatives, {qid: -6})

class QuantityPowTestCase(QuantityArithmeticsHelper, unittest.TestCase):
    """
    Test the exponentiation of a quantity.
    """

    #######################################################
    # Basic tests
    def test_pow_type(self):
        """
        Check that pow() returns a quantity.
        """
        quantity = Quantity("15 m")

        square = quantity**2

        self.assertIsInstance(square, Quantity)


    def test_pow_new(self):
        """
        Check that pow returns a different quantity.
        """
        quantity = Quantity("15 m")
        qid = quantity.qid()

        square = quantity**2

        self.assertIsNot(square, quantity)

    #######################################################
    # Different types in the exponent, all dimensionless
    def test_pow_int(self):
        """
        Check exponentiating a quantity by an integer exponentiates the value
        and the unit and propagates the error.
        """
        quantity = Quantity("15 +- 3 m")
        qid = quantity.qid()

        square = quantity**2

        self.assertEqual(repr(square),
                         "<Quantity: (225 +- 90) m^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(square._variances, {qid: 9})
        self.assertDictAlmostEqual(square._derivatives, {qid: 30})

    def test_pow_float (self):
        """
        Check exponentiating a quantity by an float exponentiates the value
        and the unit and propagates the error.
        """
        quantity = Quantity("16 +- 2 m")
        qid = quantity.qid()

        power = quantity**0.5

        self.assertEqual(repr(power),
                         "<Quantity: (4 +- 0.25) m^0.5 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 4})
        self.assertDictAlmostEqual(power._derivatives, {qid: 0.125})

    def test_pow_prefix(self):
        """
        Check exponentiating a quantity by a prefix exponentiates the value
        and the unit and propagates the error.
        """
        quantity = Quantity("16 +- 2 m")
        qid = quantity.qid()

        power = quantity**si.deca

        self.assertEqual(repr(power),
                         "<Quantity: (1.09951e+12 +- 1.37439e+12) m^10 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 4})
        self.assertDictAlmostEqual(power._derivatives, {qid: 687194767360})

    def test_pow_unit(self):
        """
        Check exponentiating a quantity by a unit exponentiates the value
        and the unit and propagates the error. The unit is dimensionless.
        """
        quantity = Quantity("16 +- 2 m")
        qid = quantity.qid()

        power = quantity**si.radian

        self.assertEqual(repr(power),
                         "<Quantity: (16 +- 2) m | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 4})
        self.assertDictAlmostEqual(power._derivatives, {qid: 1})

    def test_pow_quantity(self):
        """
        Check exponentiating a quantity by a quantity exponentiates the value
        and the unit and propagates the error. The quantity is dimensionless.
        """
        base = Quantity("16 +- 2 m")
        exponent = Quantity("2")
        qid = base.qid()

        square = base**exponent

        self.assertEqual(repr(square),
                         "<Quantity: (256 +- 64) m^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(square._variances, {qid: 4})
        self.assertDictAlmostEqual(square._derivatives, {qid: 32})

    #######################################################
    # Check units in base and exponent, 
    def test_pow_nounit_pow_nounit(self):
        """
        Check that exponentiating a quantity by another quantity works if both
        quantities are unit-less.
        """
        base = Quantity("5 +- 0.1")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: 125 +- 12.5472 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_pow_nounit_pow_dimensionless(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base quantity is unit-less and the exponent dimensionless.
        """
        base = Quantity("5 +- 0.1")
        exponent = Quantity("3 +- 0.05 rad")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: 125 +- 12.5472 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_pow_nounit_pow_unit(self):
        """
        Check that exponentiating a quantity by another quantity raises an
        exception if the base quantity is unit-less and the exponent not
        dimensionless.
        """
        base = Quantity("5 +- 0.1")
        exponent = Quantity("3 +- 0.05 m")

        self.assertRaises(ValueError, lambda b, e: b**e, base, exponent)

    def test_pow_dimensionless_pow_nounit(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base is dimensionless and the exponent unit-less.
        """
        base = Quantity("5 +- 0.1 rad")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) rad^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_pow_dimensionless_pow_dimensionless(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base quantity is dimensionless and the exponent dimensionless.
        """
        base = Quantity("5 +- 0.1 rad")
        exponent = Quantity("3 +- 0.05 rad")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) rad^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_pow_dimensionless_pow_unit(self):
        """
        Check that exponentiating a quantity by another quantity raises an
        exception if the base quantity is dimensionless and the exponent not
        dimensionless.
        """
        base = Quantity("5 +- 0.1 rad")
        exponent = Quantity("3 +- 0.05 m")

        self.assertRaises(ValueError, lambda b, e: b**e, base, exponent)

    def test_pow_unit_pow_nounit(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base is not dimensionless and the exponent is unit-less.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_pow_unit_pow_dimensionless(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base quantity is not dimensionless but the exponent is dimensionless.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3 +- 0.05 rad")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_pow_unit_pow_unit(self):
        """
        Check that exponentiating a quantity by another quantity raises an
        exception if both quantities are not dimensionless.
        """
        base = Quantity("5 +- 0.1 s")
        exponent = Quantity("3 +- 0.05 m")

        self.assertRaises(ValueError, lambda b, e: b**e, base, exponent)


    def test_pow_unit_pow_unit_object(self):
        """
        Check that exponentiating a quantity by a non-dimensionless unit
        object raises an exception.
        """
        base = Quantity("5 +- 0.1 s")
        exponent = si.metre

        self.assertRaises(ValueError, lambda b, e: b**e, base, exponent)

    #######################################################
    # Simple error propagation with independent quantities
    def test_pow_noerror_pow_noerror(self):
        """
        Check that exponentiating an error-less quantities by another
        error-less quantities does not propagate any errors.
        """
        base = Quantity("5 m")
        exponent = Quantity("3")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power), "<Quantity: 125 m^3>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})
    def test_pow_noerror_pow_error(self):
        """
        Check that exponentiating an error-less quantities by another
        quantities with error does propagate the error.
        """
        base = Quantity("5 m")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 10.059) m^3 | "
                         "depends=[%d]>" % (exp_qid))
        self.assertDictAlmostEqual(power._variances, {exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives, {exp_qid: 125 * log(5)})
    def test_pow_error_pow_noerror(self):
        """
        Check that exponentiating a quantities with an error by an error-less
        quantities does propagate the error.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power), "<Quantity: (125 +- 7.5) m^3 | "
                                      "depends=[%d]>" % base_qid)
        self.assertDictAlmostEqual(power._variances, {base_qid: 0.01})
        self.assertDictAlmostEqual(power._derivatives, {base_qid: 75})
    def test_pow_error_pow_error(self):
        """
        Check that exponentiating a quantities with an error by an quantities
        with an error does propagate both errors.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    #######################################################
    # Error propagation with dependent quantities
    def test_pow_dependent(self):
        """
        Check that exponentiating a quantity by another quantity honors
        dependencies.
        """
        quantity_a = Quantity("2.5 +- 0.05 m")
        quantity_b = Quantity("9 +- 0.15")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        base = quantity_a * 2
        exponent = quantity_b / 3

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (qid_a, qid_b))
        self.assertDictAlmostEqual(power._variances,
                                   {qid_a: 0.0025, qid_b: 0.0225})
        self.assertDictAlmostEqual(power._derivatives,
                                   {qid_a: 150, qid_b: 125 * log(5) / 3})

    def test_pow_dependent_diamond(self):
        """
        Check that exponentiating a quantity by another quantity honors
        correlations between the quantities.
        """
        quantity = Quantity("10 +- 0.1")
        base = quantity / 2
        exponent = quantity / 5

        qid = quantity.qid()

        power = base**exponent

        self.assertEqual(repr(power),
                         "<Quantity: 25 +- 1.30472 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 0.01})
        self.assertDictAlmostEqual(power._derivatives,
                                   {qid: 5 + log(5) * 5})

    #######################################################
    # Unit System
    def test_pow_unit_system(self):
        """
        Check that exponentiating a quantity by another quantity from a
        different unit system raises an error.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: a**b,
                          quantity_a, quantity_b)


      
    #######################################################
    # Mathematical edge cases
    def test_pow_x_pow_0(self):
        """
        Check that exponentiating x (non-zero) by 0 returns 0 without error or
        unit.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        power = quantity**0
        self.assertEqual(repr(power), "<Quantity: 1>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_pow_0_pow_x(self):
        """
        Check that exponentiating 0 by x (non-zero) returns 0 without error
        but with unit.
        """
        quantity = Quantity("0 +- 4 s")
        qid = quantity.qid()

        power = quantity**2
        self.assertEqual(repr(power), "<Quantity: 0 s^2>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_pow_0_pow_neg_1(self):
        """
        Check that exponentiating 0 by -1 raises an exception.
        """
        quantity = Quantity("0 +- 4 s")
        qid = quantity.qid()

        self.assertRaises(ZeroDivisionError, lambda a: a**-1, quantity)

    def test_pow_0_pow_0_w_error(self):
        """
        Check that exponentiating 0 by 0 raises an exception if any of the
        quantities has an error involved.
        """
        quantity = Quantity("0 +- 4 s")
        self.assertRaises(UncertaintyIllDefined, lambda a: a**0, quantity)

        quantity = Quantity("0 +- 4")
        self.assertRaises(UncertaintyIllDefined, lambda a: a.__rpow__(a), quantity)

    def test_pow_0_pow_0_wo_error(self):
        """
        Check that exponentiating 0 by 0 returns 0**0 with unit if neither
        quantities has an error.
        """
        base = Quantity("0 s")
        exponent = Quantity("0")

        power = base**exponent

        self.assertEqual(repr(power), "<Quantity: 1>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_pow_neg_2_pow_non_int(self):
        """
        Check that exponentiating a negative quantity by an non-int exponent
        error raises an exception.
        """
        base = Quantity("-2 s")

        self.assertRaises(ValueError, lambda a, b: a**b, base, 1.34)
        self.assertRaises(ValueError, lambda a, b: a**b, base, 0.34)

    def test_pow_neg_2_pow_error(self):
        """
        Check that exponentiating a negative quantity by an integer exponent
        without error exponentiates the value, propagates the error and
        multiples the unit.
        """
        base = Quantity("-2 s")
        exponent = Quantity("2 +- 0.01")

        self.assertRaises(UncertaintyIllDefined, lambda a, b: a**b,
                          base, exponent)


    def test_pow_neg_15_pow_int(self):
        """
        Check that exponentiating a negative quantity by an integer exponent
        without error exponentiates the value, propagates the error and
        multiples the unit.
        """
        base = Quantity("-15 +- 3 m")
        exponent = Quantity("2.0")
        qid = base.qid()

        power = base**exponent

        self.assertEqual(repr(power), "<Quantity: (225 +- 90) m^2 | "
                                      "depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 9})
        self.assertDictAlmostEqual(power._derivatives, {qid: -30})

    ###########################################################################
    # rpow

    #######################################################
    # Basic tests
    def test_rpow_type(self):
        """
        Check that rpow() returns a quantity.
        """
        quantity = Quantity("15")

        power = 2**quantity

        self.assertIsInstance(power, Quantity)


    def test_rpow_new(self):
        """
        Check that rpow returns a different quantity.
        """
        quantity = Quantity("15")
        qid = quantity.qid()

        power = 2**quantity

        self.assertIsNot(power, quantity)

    #######################################################
    # Different types in the exponent, all dimensionless
    def test_rpow_int(self):
        """
        Check exponentiating a quantity by an integer exponentiates the value
        and the unit and propagates the error.
        """
        quantity = Quantity("2 +- 0.1")
        qid = quantity.qid()

        power = 15**quantity

        self.assertEqual(repr(power),
                         "<Quantity: 225 +- 60.9311 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 0.01})
        self.assertDictAlmostEqual(power._derivatives, {qid: log(15) * 225})

    def test_rpow_float (self):
        """
        Check exponentiating a quantity by an float exponentiates the value
        and the unit and propagates the error.
        """
        quantity = Quantity("0.5 +- 0.01")
        qid = quantity.qid()

        power = 16**quantity

        self.assertEqual(repr(power),
                         "<Quantity: 4 +- 0.110904 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 0.0001})
        self.assertDictAlmostEqual(power._derivatives, {qid: log(16) * 4})

    def test_rpow_prefix(self):
        """
        Check exponentiating a quantity by a prefix exponentiates the value
        and the unit and propagates the error.
        """
        quantity = Quantity("3 +- 0.01")
        qid = quantity.qid()

        power = si.deca**quantity

        self.assertEqual(repr(power),
                         "<Quantity: 1000 +- 23.0259 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 0.0001})
        self.assertDictAlmostEqual(power._derivatives, {qid: log(10) * 1000})

    def test_rpow_unit(self):
        """
        Check exponentiating a quantity by a unit exponentiates the value
        and the unit and propagates the error. The unit is dimensionless.
        """
        quantity = Quantity("2 +- 0.1")
        qid = quantity.qid()

        power = (2 * si.radian)**quantity

        self.assertEqual(repr(power), "<Quantity: (4 +- 0.277259) rad^2 | "
                                      "depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 0.01})
        self.assertDictAlmostEqual(power._derivatives, {qid: log(2) * 4})

    def test_rpow_quantity(self):
        """
        Check exponentiating a quantity by a quantity exponentiates the value
        and the unit and propagates the error. The quantity is dimensionless.
        """
        base = Quantity("16 +- 2 m")
        exponent = Quantity("2")
        qid = base.qid()

        square = exponent.__rpow__(base)

        self.assertEqual(repr(square),
                         "<Quantity: (256 +- 64) m^2 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(square._variances, {qid: 4})
        self.assertDictAlmostEqual(square._derivatives, {qid: 32})

    #######################################################
    # Check units in base and exponent, 
    def test_rpow_nounit_pow_nounit(self):
        """
        Check that exponentiating a quantity by another quantity works if both
        quantities are unit-less.
        """
        base = Quantity("5 +- 0.1")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: 125 +- 12.5472 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_rpow_nounit_pow_dimensionless(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base quantity is unit-less and the exponent dimensionless.
        """
        base = Quantity("5 +- 0.1")
        exponent = Quantity("3 +- 0.05 rad")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: 125 +- 12.5472 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_rpow_nounit_pow_unit(self):
        """
        Check that exponentiating a quantity by another quantity raises an
        exception if the base quantity is unit-less and the exponent not
        dimensionless.
        """
        base = Quantity("5 +- 0.1")
        exponent = Quantity("3 +- 0.05 m")

        self.assertRaises(ValueError, lambda b, e: e.__rpow__(b), base, exponent)

    def test_rpow_dimensionless_pow_nounit(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base is dimensionless and the exponent unit-less.
        """
        base = Quantity("5 +- 0.1 rad")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) rad^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_rpow_dimensionless_pow_dimensionless(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base quantity is dimensionless and the exponent dimensionless.
        """
        base = Quantity("5 +- 0.1 rad")
        exponent = Quantity("3 +- 0.05 rad")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) rad^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_rpow_dimensionless_pow_unit(self):
        """
        Check that exponentiating a quantity by another quantity raises an
        exception if the base quantity is dimensionless and the exponent not
        dimensionless.
        """
        base = Quantity("5 +- 0.1 rad")
        exponent = Quantity("3 +- 0.05 m")

        self.assertRaises(ValueError, lambda b, e: b**e, base, exponent)

    def test_rpow_unit_pow_nounit(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base is not dimensionless and the exponent is unit-less.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_rpow_unit_pow_dimensionless(self):
        """
        Check that exponentiating a quantity by another quantity works if the
        base quantity is not dimensionless but the exponent is dimensionless.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3 +- 0.05 rad")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    def test_rpow_unit_pow_unit(self):
        """
        Check that exponentiating a quantity by another quantity raises an
        exception if both quantities are not dimensionless.
        """
        base = Quantity("5 +- 0.1 s")
        exponent = Quantity("3 +- 0.05 m")

        self.assertRaises(ValueError, lambda b, e: e.__rpow__(b), base, exponent)

    #######################################################
    # Simple error propagation with independent quantities
    def test_rpow_noerror_pow_noerror(self):
        """
        Check that exponentiating an error-less quantities by another
        error-less quantities does not propagate any errors.
        """
        base = Quantity("5 m")
        exponent = Quantity("3")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power), "<Quantity: 125 m^3>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_rpow_noerror_pow_error(self):
        """
        Check that exponentiating an error-less quantities by another
        quantities with error does propagate the error.
        """
        base = Quantity("5 m")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 10.059) m^3 | "
                         "depends=[%d]>" % (exp_qid))
        self.assertDictAlmostEqual(power._variances, {exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives, {exp_qid: 125 * log(5)})
    def test_rpow_error_pow_noerror(self):
        """
        Check that exponentiating a quantities with an error by an error-less
        quantities does propagate the error.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power), "<Quantity: (125 +- 7.5) m^3 | "
                                      "depends=[%d]>" % base_qid)
        self.assertDictAlmostEqual(power._variances, {base_qid: 0.01})
        self.assertDictAlmostEqual(power._derivatives, {base_qid: 75})
    def test_rpow_error_pow_error(self):
        """
        Check that exponentiating a quantities with an error by an quantities
        with an error does propagate both errors.
        """
        base = Quantity("5 +- 0.1 m")
        exponent = Quantity("3 +- 0.05")
        base_qid = base.qid()
        exp_qid = exponent.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (base_qid, exp_qid))
        self.assertDictAlmostEqual(power._variances,
                                   {base_qid: 0.01, exp_qid: 0.0025})
        self.assertDictAlmostEqual(power._derivatives,
                                   {base_qid: 75, exp_qid: 125 * log(5)})

    #######################################################
    # Error propagation with dependent quantities
    def test_rpow_dependent(self):
        """
        Check that exponentiating a quantity by another quantity honors
        dependencies.
        """
        quantity_a = Quantity("2.5 +- 0.05 m")
        quantity_b = Quantity("9 +- 0.15")
        qid_a = quantity_a.qid()
        qid_b = quantity_b.qid()
        base = quantity_a * 2
        exponent = quantity_b / 3

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: (125 +- 12.5472) m^3 | "
                         "depends=[%d, %d]>" % (qid_a, qid_b))
        self.assertDictAlmostEqual(power._variances,
                                   {qid_a: 0.0025, qid_b: 0.0225})
        self.assertDictAlmostEqual(power._derivatives,
                                   {qid_a: 150, qid_b: 125 * log(5) / 3})

    def test_rpow_dependent_diamond(self):
        """
        Check that exponentiating a quantity by another quantity honors
        correlations between the quantities.
        """
        quantity = Quantity("10 +- 0.1")
        base = quantity / 2
        exponent = quantity / 5

        qid = quantity.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power),
                         "<Quantity: 25 +- 1.30472 | depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 0.01})
        self.assertDictAlmostEqual(power._derivatives,
                                   {qid: 5 + log(5) * 5})

    #######################################################
    # Unit System
    def test_rpow_unit_system(self):
        """
        Check that exponentiating a quantity by another quantity from a
        different unit system raises an error.
        """
        quantity_a = Quantity("10 +- 4 s")
        quantity_b = Quantity("10 +- 4")

        quantity_b._unit_system = "systeme a moi"

        self.assertRaises(DifferentUnitSystem, lambda a, b: b.__rpow__(a),
                          quantity_a, quantity_b)


      
    #######################################################
    # Mathematical edge cases
    def test_rpow_x_pow_0(self):
        """
        Check that exponentiating x (non-zero) by 0 returns 0 without error or
        unit.
        """
        quantity = Quantity("10 +- 4 s")
        qid = quantity.qid()

        power = quantity**0
        self.assertEqual(repr(power), "<Quantity: 1>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_rpow_0_pow_x(self):
        """
        Check that exponentiating 0 by x (non-zero) returns 0 without error
        but with unit.
        """
        quantity = Quantity("2")
        qid = quantity.qid()

        power = 0**quantity
        self.assertEqual(repr(power), "<Quantity: 0>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_rpow_0_pow_neg_1(self):
        """
        Check that exponentiating 0 by -1 raises an exception.
        """
        quantity = Quantity("-1")
        qid = quantity.qid()

        self.assertRaises(ZeroDivisionError, lambda a: 0**a, quantity)

    def test_rpow_0_pow_0_w_error(self):
        """
        Check that exponentiating 0 by 0 raises an exception if any of the
        quantities has an error involved.
        """
        quantity = Quantity("0 +- 4")
        qid = quantity.qid()

        self.assertRaises(UncertaintyIllDefined, lambda a: 0**a, quantity)
        self.assertRaises(UncertaintyIllDefined, lambda a: a.__rpow__(a), quantity)

    def test_rpow_0_pow_0_wo_error(self):
        """
        Check that exponentiating 0 by 0 returns 0**0 with unit if neither
        quantities has an error.
        """
        base = Quantity("0 s")
        exponent = Quantity("0")

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power), "<Quantity: 1>")
        self.assertDictAlmostEqual(power._variances, {})
        self.assertDictAlmostEqual(power._derivatives, {})

    def test_rpow_neg_2_pow_non_int(self):
        """
        Check that exponentiating a negative quantity by an non-int exponent
        error raises an exception.
        """
        exp_a = Quantity("1.34")
        exp_b = Quantity("0.34")

        self.assertRaises(ValueError, lambda b, e: e.__rpow__(b), -2, exp_a)
        self.assertRaises(ValueError, lambda b, e: e.__rpow__(b), -2, exp_b)

    def test_rpow_neg_2_pow_error(self):
        """
        Check that exponentiating a negative quantity by an integer exponent
        without error exponentiates the value, propagates the error and
        multiples the unit.
        """
        base = Quantity("-2 s")
        exponent = Quantity("2 +- 0.01")

        self.assertRaises(UncertaintyIllDefined, lambda a, b: b.__rpow__(a),
                          base, exponent)


    def test_rpow_neg_15_pow_int(self):
        """
        Check that exponentiating a negative quantity by an integer exponent
        without error exponentiates the value, propagates the error and
        multiples the unit.
        """
        base = Quantity("-15 +- 3 m")
        exponent = Quantity("2.0")
        qid = base.qid()

        power = exponent.__rpow__(base)

        self.assertEqual(repr(power), "<Quantity: (225 +- 90) m^2 | "
                                      "depends=[%d]>" % qid)
        self.assertDictAlmostEqual(power._variances, {qid: 9})
        self.assertDictAlmostEqual(power._derivatives, {qid: -30})
