
# Copyright (C) 2018 Frank Sauerburger

import unittest
import mock
import numpy as np

import pyveu
from pyveu import Named, SystemAffiliatedMixin, Prefix, Unit, UnitSystem

class Unknown(object):
    """
    This helper class is used to check that arithmetic operations return
    NotImplemented if they operate on a unknown object.
    """
    pass

class ToyUnitSystem(object):
    """
    This class implement mimics a unit system. The method has all the units
    hard coded and is only used for unit tests.
    """
    def base_representation(self, unit_vector):
        assert len(unit_vector) == 3

        base_units = ["kg", "s", "m"]
        factors = []

        for base, power in zip(base_units, unit_vector):
            if power == 1:
                factors.append(base)
            elif power > 0:
                factors.append("%s^%g" % (base, power))
            elif power < 0:
                factors.append("%s^(%g)" % (base, power))

        return " ".join(factors)

class ToyUnitSystemTest(unittest.TestCase):
    """
    This method tests the toy unit system used here for unit tests.
    """
    def test_all(self):
        """
        Check that units all base units are included in the base
        representation.
        """
        tus = ToyUnitSystem()

        self.assertEqual(tus.base_representation([4, 3, 2]), "kg^4 s^3 m^2")

    def test_zero(self):
        """
        Check that units with vanishing exponents are removed from the
        representation.
        """
        tus = ToyUnitSystem()

        self.assertEqual(tus.base_representation([0, 3, 2]), "s^3 m^2")
        self.assertEqual(tus.base_representation([4, 0, 2]), "kg^4 m^2")
        self.assertEqual(tus.base_representation([4, 3, 0]), "kg^4 s^3")

        self.assertEqual(tus.base_representation([4, 0, 0]), "kg^4")
        self.assertEqual(tus.base_representation([0, 3, 0]), "s^3")
        self.assertEqual(tus.base_representation([0, 0, 2]), "m^2")

        self.assertEqual(tus.base_representation([0, 0, 0]), "")

    def test_half(self):
        """
        Check that units with 1/2 exponents are printed with the exponent.
        """
        tus = ToyUnitSystem()

        self.assertEqual(tus.base_representation([0, 0.5, 2]), "s^0.5 m^2")

    def test_one(self):
        """
        Check that units with unit exponents are printed without exponent.
        """
        tus = ToyUnitSystem()

        self.assertEqual(tus.base_representation([1, 3, 2]), "kg s^3 m^2")
        self.assertEqual(tus.base_representation([4, 1, 2]), "kg^4 s m^2")
        self.assertEqual(tus.base_representation([4, 3, 1]), "kg^4 s^3 m")

        self.assertEqual(tus.base_representation([4, 1, 1]), "kg^4 s m")
        self.assertEqual(tus.base_representation([1, 3, 1]), "kg s^3 m")
        self.assertEqual(tus.base_representation([1, 1, 2]), "kg s m^2")

        self.assertEqual(tus.base_representation([1, 1, 1]), "kg s m")

    def test_negative(self):
        """
        Check that negative exponents are in parenthesis.
        """

        tus = ToyUnitSystem()

        self.assertEqual(tus.base_representation([-1, 3, 2]), "kg^(-1) s^3 m^2")
        self.assertEqual(tus.base_representation([4, -3, 2]), "kg^4 s^(-3) m^2")
        self.assertEqual(tus.base_representation([4, 3, -2]), "kg^4 s^3 m^(-2)")

    def test_length(self):
        """
        Check that an assertion error is raised if the length of the unit
        vector is not three.
        """

        tus = ToyUnitSystem()

        self.assertRaises(AssertionError, tus.base_representation, [-1, 3])
        self.assertRaises(AssertionError, tus.base_representation, [])
        self.assertRaises(AssertionError, tus.base_representation,
                          [-1, 3, 2, 0])

class UnitTest(unittest.TestCase):
    """
    This class implements test cases for the unit class.
    """

    def test_init_store(self):
        """
        Check that all the values passed to the constructor are saved
        internally.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        self.assertEqual(micrometer._factor, 1e-6)
        self.assertEqual(list(micrometer._unit_vector), [0, 0, 1])
        self.assertEqual(micrometer._label, "Micrometer")
        self.assertEqual(micrometer._symbol, "um")
        self.assertEqual(micrometer._latex, r"\mu m")
        self.assertEqual(micrometer._unit_system, tos)

    def test_init_type(self):
        """
        Check that a unit inherits from Named and ModifiableNamedMixin.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        self.assertIsInstance(micrometer, Unit)
        self.assertIsInstance(micrometer, Named)
        self.assertIsInstance(micrometer, SystemAffiliatedMixin)


    def test_create_w_history_type(self):
        """
        Check that create_with_history() creates a new unit.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        kilometer = Unit.create_with_history(1000, [1, 0, 0, 0, 0], sam)

        self.assertIsInstance(kilometer, Unit)
        

    def test_create_w_history_store(self):
        """
        Check that create_with_history() creates a new unit and stores the
        factor and the unit system.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        kilometer = Unit.create_with_history(1000, [1, 0, 0, 0, 0], sam)

        self.assertEqual(kilometer.factor(), 1000)
        self.assertEqual(kilometer.unit_system(), sam)

    def test_create_w_history_dimensionless_factor(self):
        """
        Check that the units history is the factor.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        two = Unit.create_with_history(2, [0, 0, 0, 0, 0], sam)

        self.assertEqual(repr(two), "<Unit: 2 >")
        self.assertEqual(repr(two._history), "2 * (<Unit Meter: 1 m = 1 m>^0)")

    def test_create_w_history_dimensionless(self):
        """
        Check that the units history is the factor.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        one = Unit.create_with_history(1, [0, 0, 0, 0, 0], sam)

        self.assertEqual(repr(one), "<Unit: 1 >")
        self.assertEqual(repr(one._history), "1 * (<Unit Meter: 1 m = 1 m>^0)")

    def test_create_w_history_single_positive(self):
        """
        Check that the units history is a product of the factor and the base
        unit when there is a single positive entry in the unit vector.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        kilometer = Unit.create_with_history(1000, [1, 0, 0, 0, 0], sam)

        self.assertEqual(repr(kilometer), "<Unit: 1000 m>")
        self.assertEqual(repr(kilometer._history), "1000 * <Unit Meter: 1 m = 1 m>")

    def test_create_w_history_single_negative(self):
        """
        Check that the units history is a product of the factor and the base
        unit when there is a single negative entry in the unit vector.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        resolution = Unit.create_with_history(1000, [-1, 0, 0, 0, 0], sam)

        self.assertEqual(repr(resolution), "<Unit: 1000 m^(-1)>")
        self.assertEqual(repr(resolution._history), "1000 / <Unit Meter: 1 m = 1 m>")

    def test_create_w_history_multiple_positive(self):
        """
        Check that the units history is a product of the factor and the base
        unit when there is a multiple positive entry in the unit vector.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        micro_farad = Unit.create_with_history(1e-6, [0, 1, 0, 1, 0], sam)

        self.assertEqual(repr(micro_farad), "<Unit: 1e-06 A s>")
        self.assertEqual(repr(micro_farad._history), "1e-06 * "
                         "<Unit Ampere: 1 A = 1 A> * <Unit Second: 1 s = 1 s>")

    def test_create_w_history_multiple_negative(self):
        """
        Check that the units history is a product of the factor and the base
        unit when there is a multiple negative entry in the unit vector.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        milli_flux = Unit.create_with_history(1e-3, [-2, 0, 0, -1, 0], sam)

        self.assertEqual(repr(milli_flux), "<Unit: 0.001 m^(-2) s^(-1)>")
        self.assertEqual(repr(milli_flux._history), "0.001 / "
                         "((<Unit Meter: 1 m = 1 m>^2) * "
                         "<Unit Second: 1 s = 1 s>)")

    def test_create_w_history_multiple_mixed(self):
        """
        Check that the units history is a product of the factor and the base
        unit when there is a multiple negative and positive entry in the unit vector.
        """
        sam = UnitSystem("systeme a moi", 5)
        sam.create_base_unit(0, "Meter", "m")
        sam.create_base_unit(1, "Ampere", "A")
        sam.create_base_unit(2, "Kelvin", "K")
        sam.create_base_unit(3, "Second", "s")
        sam.create_base_unit(4, "Kilogram", "kg")

        kilo_newton = Unit.create_with_history(1000, [1, 0, 0, -2, 1], sam)

        self.assertEqual(repr(kilo_newton), "<Unit: 1000 m s^(-2) kg>")
        self.assertEqual(repr(kilo_newton._history), "(1000 * "
                         "<Unit Meter: 1 m = 1 m> * "
                         "<Unit Kilogram: 1 kg = 1 kg>) / "
                         "(<Unit Second: 1 s = 1 s>^2)")
    
    def test_get_factor(self):
        """
        Check that factor() returns the internal factor.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        self.assertEqual(micrometer.factor(), 1e-6)

    def test_get_unit_vector(self):
        """
        Check that unit_vector() returns the internal unit vector.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        self.assertEqual(list(micrometer.unit_vector()), [0, 0, 1])

    def test_get_unit_vector_copy(self):
        """
        Check that unit_vector() returns a copy of the internal unit vector.
        This is tested by retrieving the vector, modifying it and then
        compare it to the internal vector.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        unit_vector = micrometer.unit_vector()
        unit_vector *= 2    # in-place modification
        self.assertNotEqual(list(unit_vector), list(micrometer.unit_vector()))

    def test_get_unit_vector_type(self):
        """
        Check that unit_vector() returns a numpy array.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        self.assertIsInstance(micrometer.unit_vector(), np.ndarray)

    ############################################################
    # Representation
    def test_repr_named(self):
        """
        Check the representation of a named unit. The presentation should
        contain the label, symbol and factor.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        self.assertEqual(repr(micrometer), "<Unit Micrometer: 1 um = 1e-06 m>")

    def test_repr_named_decimal(self):
        """
        Check the representation of a named Unit. The presentation should
        contain the label, symbol and factor. The factor should be displayed
        as a decimal, if it is close to 1.
        """
        tos = ToyUnitSystem()
        circle = Unit(3.14, [0, 0, 1], "Circle", "crc", None, tos)

        self.assertEqual(repr(circle), "<Unit Circle: 1 crc = 3.14 m>")

    def test_repr_no_label(self):
        """
        If a label is None but symbol is non-None, the label should be
        omitted in the representation.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], None, "um", r"\mu m", tos)

        self.assertEqual(repr(micrometer), "<Unit: 1 um = 1e-06 m>")


    def test_repr_no_symbol(self):
        """
        If a label is None but symbol is non-None, the label should be
        omitted in the representation.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", None, r"\mu m", tos)

        self.assertEqual(repr(micrometer), "<Unit Micrometer: 1e-06 m>")

    def test_repr_anonymous(self):
        """
        If the unit is anonymous (even if it has a latex symbol) the string
        representation should only contain the factor and base_representation
        of the unit vector.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], None,  None, r"\mu", tos)
        self.assertEqual(repr(micrometer), "<Unit: 1e-06 m>")

        micrometer = Unit(1e-6, [0, 0, 1], None,  None, None, tos)
        self.assertEqual(repr(micrometer), "<Unit: 1e-06 m>")


    ############################################################
    # Multiplication
    def test_mul_number_new(self):
        """
        Check that multiplying a unit with a scalar creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = micrometer * 1e-3

        self.assertIsNot(micrometer, nanometer)

    def test_mul_number_us(self):
        """
        Check that multiplying a unit with a scalar propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = micrometer * 1e-3

        self.assertEqual(nanometer.unit_system(), tos)
        
    def test_mul_float(self):
        """
        Check that multiplying a unit with a float scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = micrometer * 1e-3
        self.assertEqual(repr(nanometer), "<Unit: 1e-09 m>")
        
    def test_mul_int(self):
        """
        Check that multiplying a unit with an integer scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        millimeter = micrometer * 1000
        self.assertEqual(repr(millimeter), "<Unit: 0.001 m>")

    def test_mul_Prefix(self):
        """
        Check that multiplying a unit with a Prefix scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        millimeter = micrometer * kilo
        self.assertEqual(repr(millimeter), "<Unit: 0.001 m>")

    def test_mul_Prefix_new(self):
        """
        Check that multiplying a unit with a Prefix creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        millimeter = micrometer * kilo
        self.assertIsNot(micrometer, millimeter)

    def test_mul_Prefix_us(self):
        """
        Check that multiplying a unit with a Prefix propagates the unit system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        millimeter = micrometer * kilo
        self.assertEqual(millimeter.unit_system(), tos)

    def test_mul_Prefix_diff_us(self):
        """
        Check that multiplying a unit with a Prefix assigned to a different unit
        system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a * b,
                          micrometer, kilo)

    def test_mul_Unit(self):
        """
        Check that multiplying a unit with another unit scales the factor and
        add the unit vectors. The scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, tos)

        speed = micrometer * hertz
        self.assertEqual(repr(speed), "<Unit: 1e-06 s^(-1) m>")

    def test_mul_Unit_new(self):
        """
        Check that multiplying a unit with another unit creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, tos)

        speed = micrometer * hertz

        self.assertIsNot(speed, micrometer)
        self.assertIsNot(speed, hertz)

    def test_mul_Unit_diff_us(self):
        """
        Check that multiplying a unit with another unit assigned to a different
        unit system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a * b,
                          micrometer, hertz)

    def test_mul_Unit_us(self):
        """
        Check that multiplying a unit with another unit propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, tos)

        speed = micrometer * hertz

        self.assertEqual(speed.unit_system(), tos)

    def test_mul_unknown(self):
        """
        Check that multiplication with an unknown class returns
        NotImplemented.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a * b, micrometer, unknown)

    def test_mul_long(self):
        """
        Check that multiplication works with Python 2 long integers.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        try:
            some_what_large = micrometer * 1000000000000000000000
        except TypeError:
            self.fail("Multiplication of a Unit with a long int failed.")

    ############################################################
    # Right-Multiplication
    def test_rmul_number_new(self):
        """
        Check that right-multiplying a unit with a scalar creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = 1e-3 * micrometer

        self.assertIsNot(micrometer, nanometer)

    def test_rmul_number_us(self):
        """
        Check that right-multiplying a unit with a scalar propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = 1e-3 * micrometer

        self.assertEqual(nanometer.unit_system(), tos)
        
    def test_rmul_float(self):
        """
        Check that right-multiplying a unit with a float scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = 1e-3 * micrometer
        self.assertEqual(repr(nanometer), "<Unit: 1e-09 m>")
        
    def test_rmul_int(self):
        """
        Check that right-multiplying a unit with an integer scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        millimeter = 1000 * micrometer
        self.assertEqual(repr(millimeter), "<Unit: 0.001 m>")

    def test_rmul_Prefix(self):
        """
        Check that right-multiplying a unit with a Prefix scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        millimeter = kilo * micrometer 
        self.assertEqual(repr(millimeter), "<Unit: 0.001 m>")

    def test_rmul_Prefix_new(self):
        """
        Check that right-multiplying a unit with a Prefix creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        millimeter = kilo * micrometer
        self.assertIsNot(micrometer, millimeter)

    def test_rmul_Prefix_us(self):
        """
        Check that right-multiplying a unit with a Prefix propagates the unit
        system
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        millimeter = kilo * micrometer
        self.assertEqual(millimeter.unit_system(), tos)

    def test_rmul_Prefix_diff_us(self):
        """
        Check that right-multiplying a unit with a Prefix assigned to a different
        unit system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a * b,
                          kilo, micrometer)

    def test_rmul_Unit(self):
        """
        Check that right-multiplying a unit by another unit scales the factor
        and add the unit vectors. The scaled unit should be anonymous.

        This this type of operator might be called, when the right object is a
        subclass of the left one.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, tos)

        speed = micrometer.__rmul__(hertz)
        self.assertEqual(repr(speed), "<Unit: 1e-06 s^(-1) m>")

    def test_rmul_Unit_new(self):
        """
        Check that right-multiplying a unit with a Prefix creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, tos)

        speed = micrometer.__rmul__(hertz)
        self.assertIsNot(speed, micrometer)
        self.assertIsNot(speed, hertz)

    def test_rmul_Unit_us(self):
        """
        Check that right-multiplying a unit with another unit propagates the
        unit system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, tos)

        speed = micrometer.__rmul__(hertz)
        self.assertEqual(speed.unit_system(), tos)

    def test_rmul_Unit_diff_us(self):
        """
        Check that right-multiplying a unit with another Unit assigned to a
        different unit system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        hertz = Unit(1, [0, -1, 0], "Hertz", "Hz", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem,
                          lambda a, b: b.__rmul__(a),
                          hertz, micrometer)

    def test_rmul_unknown(self):
        """
        Check that right-multiplication with an unknown class returns
        NotImplemented.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a * b, unknown, micrometer)

    def test_rmul_long(self):
        """
        Check that right-multiplication works with Python 2 long integers.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        try:
            some_what_large = 1000000000000000000000 * micrometer
        except TypeError:
            self.fail("Multiplication of a Unit with a long int failed.")

    ############################################################
    # Division
    def test_div_number_new(self):
        """
        Check that dividing a unit by a scalar creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        millimeter = micrometer / 1e-3

        self.assertIsNot(micrometer, millimeter)

    def test_div_number_us(self):
        """
        Check that dividing a unit by a scalar propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        millimeter = micrometer / 1e-3

        self.assertEqual(millimeter.unit_system(), tos)
        
    def test_div_float(self):
        """
        Check that dividing a unit by a float scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        millimeter = micrometer / 1e-3
        self.assertEqual(repr(millimeter), "<Unit: 0.001 m>")
        
    def test_div_int(self):
        """
        Check that dividing a unit by an integer scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        nanometer = micrometer / 1000
        self.assertEqual(repr(nanometer), "<Unit: 1e-09 m>")

    def test_div_Prefix(self):
        """
        Check that dividing a unit by a Prefix scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        nanometer = micrometer / kilo
        self.assertEqual(repr(nanometer), "<Unit: 1e-09 m>")

    def test_div_Prefix_new(self):
        """
        Check that dividing a unit by a Prefix creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        nanometer = micrometer / kilo
        self.assertIsNot(micrometer, nanometer)

    def test_div_Prefix_us(self):
        """
        Check that dividing a unit by a Prefix propagates the unit system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        nanometer = micrometer / kilo
        self.assertEqual(nanometer.unit_system(), tos)

    def test_div_Prefix_diff_us(self):
        """
        Check that dividing a unit by a Prefix assigned to a different unit
        system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a / b,
                          micrometer, kilo)

    def test_div_Unit(self):
        """
        Check that dividing a unit by another unit scales the factor and
        subtracts the unit vectors. The scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, tos)

        speed = micrometer / second
        self.assertEqual(repr(speed), "<Unit: 1e-06 s^(-1) m>")

    def test_div_Unit_new(self):
        """
        Check that dividing a unit by another unit creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, tos)

        speed = micrometer / second
        self.assertIsNot(speed, micrometer)
        self.assertIsNot(speed, second)

    def test_div_Unit_diff_us(self):
        """
        Check that dividing a unit by another unit assigned to a different
        unit system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a / b,
                          micrometer, second)

    def test_div_Unit_us(self):
        """
        Check that dividing a unit by another unit propagates the unit system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, tos)

        speed = micrometer / second
        self.assertEqual(speed.unit_system(), tos)

    def test_div_unknown(self):
        """
        Check that division by an unknown class returns NotImplemented.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a / b, micrometer, unknown)

    def test_div_long(self):
        """
        Check that division works by Python 2 long integers.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        try:
            some_what_large = micrometer / 1000000000000000000000
        except TypeError:
            self.fail("Division of a Unit by a long int failed.")

    ############################################################
    # True division / Python 2 division compatibility
    def test_trudiv_py2(self):
        """
        Check that dividing an integer Unit performs a true-division.
        """
        tos = ToyUnitSystem()
        kilometer = Unit(1000, [0, 0, 1], "Kilometer", "km", None, tos)

        millimeter = kilometer.__div__(1000000)

        self.assertEqual(repr(millimeter), "<Unit: 0.001 m>")

    ############################################################
    # Right-division
    def test_rdiv_number_new(self):
        """
        Check that right-dividing a unit by a scalar creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        per_millimeter = 1e-3 / micrometer

        self.assertIsNot(micrometer, per_millimeter)

    def test_rdiv_number_us(self):
        """
        Check that right-dividing a unit by a scalar propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        per_millimeter = 1e-3 / micrometer

        self.assertEqual(per_millimeter.unit_system(), tos)
        
    def test_rdiv_float(self):
        """
        Check that right-dividing a unit by a float scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        per_millimeter = 1e-3 / micrometer
        self.assertEqual(repr(per_millimeter), "<Unit: 1000 m^(-1)>")
        
    def test_rdiv_int(self):
        """
        Check that right-dividing a unit by an integer scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        per_nanometer = 1000 / micrometer
        self.assertEqual(repr(per_nanometer), "<Unit: 1e+09 m^(-1)>")

    def test_rdiv_Prefix(self):
        """
        Check that right-dividing a unit by a Prefix scales the factor. The
        scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        per_nanometer = kilo / micrometer
        self.assertEqual(repr(per_nanometer), "<Unit: 1e+09 m^(-1)>")

    def test_rdiv_Prefix_new(self):
        """
        Check that right-dividing a unit by a Prefix creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        per_nanometer = kilo / micrometer
        self.assertIsNot(micrometer, per_nanometer)

    def test_rdiv_Prefix_us(self):
        """
        Check that right-dividing a unit by a Prefix propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, tos)

        per_nanometer = kilo / micrometer
        self.assertEqual(per_nanometer.unit_system(), tos)

    def test_rdiv_Prefix_diff_us(self):
        """
        Check that right-dividing a unit by a Prefix assigned to a different
        unit system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        kilo = Prefix(1000, "Kilo", "k", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a / b, kilo,
                          micrometer)

    def test_rdiv_Unit(self):
        """
        Check that right-dividing a unit by another scales the factor and
        subtracts the unit vectors. The scaled unit should be anonymous.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, tos)

        speed = second.__rtruediv__(micrometer)
        self.assertEqual(repr(speed), "<Unit: 1e-06 s^(-1) m>")

    def test_rdiv_Unit_new(self):
        """
        Check that right-dividing a unit by another unit creates a new unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, tos)

        speed = second.__rtruediv__(micrometer)
        self.assertIsNot(micrometer, speed)
        self.assertIsNot(second, speed)

    def test_rdiv_Unit_us(self):
        """
        Check that right-dividing a unit by another Unit propagates the unit
        system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, tos)

        speed = second.__rtruediv__(micrometer)
        self.assertEqual(speed.unit_system(), tos)

    def test_rdiv_Unit_diff_us(self):
        """
        Check that right-dividing a unit by another unit assigned to a different
        unit system fails.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        second = Unit(1, [0, 1, 0], "Second", "s", None, ToyUnitSystem())

        self.assertRaises(pyveu.DifferentUnitSystem,
                          lambda a, b: b.__rtruediv__(a),
                          micrometer, second)

    def test_rdiv_unknown(self):
        """
        Check that right-division by an unknown class returns NotImplemented.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a / b, unknown, micrometer)

    def test_rdiv_long(self):
        """
        Check that right-division works by Python 2 long integers.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        try:
            some_what_large = 1000000000000000000000 / micrometer
        except TypeError:
            self.fail("Division of a Unit by a long int failed.")

    ############################################################
    # True right-division / Python 2 division compatibility
    def test_rtrudiv_py2(self):
        """
        Check that right-dividing an integer Unit performs a true-division.
        """
        tos = ToyUnitSystem()
        kilometer = Unit(1000000, [0, 0, 1], "Kilometer", "km", None, tos)

        millimeter = kilometer.__rdiv__(1000)

        self.assertEqual(repr(millimeter), "<Unit: 0.001 m^(-1)>")

    ############################################################
    # Power
    def test_pow_number_new(self):
        """
        Check that raising a unit to a power returns a new, anonymous unit.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        square_micrometer = micrometer**2
        self.assertIsNot(square_micrometer, micrometer)

    def test_pow_number_us(self):
        """
        Check that raising a unit to a power propagates the unit system.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        square_micrometer = micrometer**2
        self.assertEqual(square_micrometer.unit_system(), tos)

    def test_pow_int(self):
        """
        Check that raising a unit to an integer power raises the factor to the
        same power and multiplies the unit vector by the power.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        square_micrometer = micrometer**2
        self.assertEqual(repr(square_micrometer), "<Unit: 1e-12 m^2>")

    def test_pow_float(self):
        """
        Check that raising a unit to an integer power raises the factor to the
        same power and multiplies the unit vector by the power.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        square_micrometer = micrometer**0.5
        self.assertEqual(repr(square_micrometer), "<Unit: 0.001 m^0.5>")

    def test_pow_unknown(self):
        """
        Check that raising a unit to power of an unknown class returns NotImplemented.
        """
        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)
        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a**b, micrometer, unknown)

    def test_pow_long(self):
        """
        Check that the power can be a Python 2 long type.
        """

        tos = ToyUnitSystem()
        micrometer = Unit(1e-6, [0, 0, 1], "Micrometer", "um", r"\mu m", tos)

        long_two = 2000000000000000000000 / 1000000000000000000000
        square_micrometer = micrometer**long_two

        self.assertEqual(repr(square_micrometer), "<Unit: 1e-12 m^2>")

    ############################################################
    #  Dimensionless
    def test_dimensionless_dl_base(self):
        """
        Check that a dimensionless base unit is dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        radian = us.create_unit(1, [0, 0, 0, 1, 0], "Radian", "rad")
        self.assertTrue(radian.dimensionless())

        steradian = us.create_unit(1, [0, 0, 0, 0, 1], "Steradian", "sr")
        self.assertTrue(steradian.dimensionless())

    def test_dimensionless_ndl_base(self):
        """
        Check that a non-dimensionless base unit is not dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        meter = us.create_unit(1, [0, 0, 1, 0, 0], "Meter", "m")
        self.assertFalse(meter.dimensionless())

    def test_dimensionless_dl_combination(self):
        """
        Check that a dimensionless linear combination is dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        comb = us.create_unit(2, [0, 0, 0, 1, 2], "comb", "c")
        self.assertTrue(comb.dimensionless())

    def test_dimensionless_pndl_combination(self):
        """
        Check that a pure non-dimensionless linear combination is not
        dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        comb = us.create_unit(2, [1, 0, 1, 0, 0], "comb", "c")
        self.assertFalse(comb.dimensionless())

    def test_dimensionless_mndl_combination(self):
        """
        Check that a mix non-dimensionless linear combination is not
        dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        comb = us.create_unit(2, [1, 0, 1, 0, 1], "comb", "c")
        self.assertFalse(comb.dimensionless())

    ############################################################
    # Arithmetic history
    def test_history_init(self):
        """
        Check that the initial history is None.
        """
        sam = UnitSystem("systeme a moi", 1)
        ampere = sam.create_base_unit(0, "Amp", "A")

        self.assertIsNone(ampere._history)

    ############################################################
    # Arithmetic history: Multiplication
    def test_history_mul_storage(self):
        """
        Check that multiplying two units stores a product.
        """
        sam = UnitSystem("systeme a moi", 2)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")

        coulomb = ampere * second
        self.assertEqual(repr(coulomb._history),
                         "<Unit Amp: 1 A = 1 A> * <Unit Sec: 1 s = 1 s>")
        
    def test_history_mul_storage_number(self):
        """
        Check that multiplying a units with a number not store this operation.
        """
        sam = UnitSystem("systeme a moi", 2)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")

        current_rating = ampere * 3
        self.assertEqual(repr(current_rating._history),
                         "<Unit Amp: 1 A = 1 A> * 3")

        charge_rating = current_rating * second
        self.assertEqual(repr(charge_rating._history),
                         "<Unit Amp: 1 A = 1 A> * 3 * " 
                         "<Unit Sec: 1 s = 1 s>")


    def test_history_mul_product(self):
        """
        Check that multiplying a unit with a product of units appends the unit
        to the product.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")
        volt = sam.create_base_unit(2, "Volt", "V")

        coulomb = ampere * second
        joule = volt * coulomb
        self.assertEqual(repr(joule._history), "<Unit Volt: 1 V = 1 V> * "
                         "<Unit Amp: 1 A = 1 A> * <Unit Sec: 1 s = 1 s>")

    def test_history_mul_fraction(self):
        """
        Check that multiplying a unit with a fraction of units creates a new
        product.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilo", "kg")

        speed = metre / second
        momentum = kilogram * speed
        self.assertEqual(repr(momentum._history), "<Unit Kilo: 1 kg = 1 kg> * "
                         "(<Unit Metre: 1 m = 1 m> / <Unit Sec: 1 s = 1 s>)")

    def test_history_mul_power(self):
        """
        Check that multiplying a unit with a power of units creates a new
        product.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        hertz_2 = second**-2
        acceleration = metre * hertz_2
        self.assertEqual(repr(acceleration._history),
                         "<Unit Metre: 1 m = 1 m> * "
                         "(<Unit Sec: 1 s = 1 s>^-2)")

    def test_history_mul_named_product(self):
        """
        Check that multiplying a unit with a named product of units does not
        copy the whole history of the named product.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")
        volt = sam.create_base_unit(2, "Volt", "V")

        coulomb = sam.register_unit(ampere * second, "Coulomb", "C")
        joule = volt * coulomb
        self.assertEqual(repr(joule._history), "<Unit Volt: 1 V = 1 V> * "
                         "<Unit Coulomb: 1 C = 1 A s>")
        
    def test_history_mul_named_fraction(self):
        """
        Check that multiplying a unit with a named fraction of units does not
        copy the whole history of the named fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        joule = sam.create_base_unit(0, "Joule", "J")
        second = sam.create_base_unit(1, "Sec", "s")
        hour = sam.create_base_unit(2, "Hour", "h")

        watt = sam.register_unit(joule / second, "Watt", "W")
        watt_hour = hour * watt
        self.assertEqual(repr(watt_hour._history), "<Unit Hour: 1 h = 1 h> * "
                         "<Unit Watt: 1 W = 1 J s^(-1)>")

    def test_history_mul_named_power(self):
        """
        Check that multiplying a unit with a named power of units does
        not copy the whole history of the named power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        hertz_2 = sam.register_unit(second**-2, "Hertz2", "h2")
        acceleration = metre * hertz_2
        self.assertEqual(repr(acceleration._history),
                         "<Unit Metre: 1 m = 1 m> * "
                         "<Unit Hertz2: 1 h2 = 1 s^(-2)>")

    def test_history_mul_named_prefix_named_unit(self):
        """
        Check that multiplying a named unit with a named prefix from the right
        creates a product of the two factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        kilo_amp = ampere * kilo
        self.assertEqual(repr(kilo_amp._history), "<Unit Amp: 1 A = 1 A> * "
                         "<Prefix Kilo: k = 1000>")

    def test_history_mul_unnamed_prefix_named_unit(self):
        """
        Check that multiplying a named unit with an unnamed prefix from the
        right creates a product of the three factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        fuse_amp = ampere * (0.016 * kilo)
        self.assertEqual(repr(fuse_amp._history), "<Unit Amp: 1 A = 1 A> * "
                         "0.016 * <Prefix Kilo: k = 1000>")

    def test_history_mul_named_prefix_unnamed_unit(self):
        """
        Check that multiplying a unnamed unit with a named prefix from the
        right creates a product of the three factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        kilo_amp = watt * kilo
        self.assertEqual(repr(kilo_amp._history), "<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V> * "
                         "<Prefix Kilo: k = 1000>")

    def test_history_mul_unnamed_prefix_unnamed_unit(self):
        """
        Check that multiplying a named ununit with an unnamed prefix from the
        right creates a product of the four factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        power_rating = watt * (0.25 * kilo)
        self.assertEqual(repr(power_rating._history), "<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V> * "
                         "0.25 * <Prefix Kilo: k = 1000>")

    def test_history_rmul_storage_number(self):
        """
        Check that right-multiplying a units with a number does store this
        operation.
        """
        sam = UnitSystem("systeme a moi", 2)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")

        current_rating = 3 * ampere 
        self.assertEqual(repr(current_rating._history),
                         "3 * <Unit Amp: 1 A = 1 A>")

    def test_history_rmul_product(self):
        """
        Check that right-multiplying a unit with a product of units appends
        the unit to the product.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")
        volt = sam.create_base_unit(2, "Volt", "V")

        coulomb = ampere * second
        joule = coulomb * volt
        self.assertEqual(repr(joule._history), "<Unit Amp: 1 A = 1 A> * "
                         "<Unit Sec: 1 s = 1 s> * <Unit Volt: 1 V = 1 V>")

    def test_history_rmul_fraction(self):
        """
        Check that right-multiplying a unit with a fraction of units creates a
        new product.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilo", "kg")

        speed = metre / second
        momentum = speed * kilogram
        self.assertEqual(repr(momentum._history), 
                         "(<Unit Metre: 1 m = 1 m> / <Unit Sec: 1 s = 1 s>) * "
                         "<Unit Kilo: 1 kg = 1 kg>")

    def test_history_rmul_power(self):
        """
        Check that right-multiplying a unit with a power of units creates a new
        product.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        hertz_2 = second**-2
        acceleration = hertz_2 * metre
        self.assertEqual(repr(acceleration._history),
                         "(<Unit Sec: 1 s = 1 s>^-2) * "
                         "<Unit Metre: 1 m = 1 m>")

    def test_history_rmul_named_product(self):
        """
        Check that right-multiplying a unit with a named product of units does
        not copy the whole history of the named product.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")
        volt = sam.create_base_unit(2, "Volt", "V")

        coulomb = sam.register_unit(ampere * second, "Coulomb", "C")
        joule = coulomb * volt
        self.assertEqual(repr(joule._history), "<Unit Coulomb: 1 C = 1 A s> * "
                         "<Unit Volt: 1 V = 1 V>")

    def test_history_rmul_named_fraction(self):
        """
        Check that right-multiplying a unit with a named fraction of units
        does not copy the whole history of the named fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        joule = sam.create_base_unit(0, "Joule", "J")
        second = sam.create_base_unit(1, "Sec", "s")
        hour = sam.create_base_unit(2, "Hour", "h")

        watt = sam.register_unit(joule / second, "Watt", "W")
        watt_hour = watt * hour
        self.assertEqual(repr(watt_hour._history),
                         "<Unit Watt: 1 W = 1 J s^(-1)> * "
                         "<Unit Hour: 1 h = 1 h>")

    def test_history_rmul_named_power(self):
        """
        Check that right-multiplying a unit with a named power of units
        creates does not copy the whole history of the named power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        hertz_2 = sam.register_unit(second**-2, "Hertz2", "h2")
        acceleration = hertz_2 * metre
        self.assertEqual(repr(acceleration._history),
                         "<Unit Hertz2: 1 h2 = 1 s^(-2)> * "
                         "<Unit Metre: 1 m = 1 m>")

    def test_history_rmul_named_prefix_named_unit(self):
        """
        Check that multiplying a named unit with a named prefix from the left
        creates a product of the two factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        kilo_amp = kilo * ampere
        self.assertEqual(repr(kilo_amp._history), "<Prefix Kilo: k = 1000> * "
                         "<Unit Amp: 1 A = 1 A>")

    def test_history_rmul_unnamed_prefix_named_unit(self):
        """
        Check that multiplying a named unit with an unnamed prefix from the
        left creates a product of the three factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        fuse_amp = (0.016 * kilo) * ampere
        self.assertEqual(repr(fuse_amp._history), "0.016 * <Prefix Kilo: k = 1000> * "
                         "<Unit Amp: 1 A = 1 A>")

    def test_history_rmul_named_prefix_unnamed_unit(self):
        """
        Check that multiplying a unnamed unit with a named prefix from the
        left creates a product of the three factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        kilo_amp = kilo * watt
        self.assertEqual(repr(kilo_amp._history), "<Prefix Kilo: k = 1000> * "
                         "<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V>")

    def test_history_rmul_unnamed_prefix_unnamed_unit(self):
        """
        Check that multiplying a named ununit with an unnamed prefix from the
        left creates a product of the four factors.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        power_rating = (0.25 * kilo) * watt
        self.assertEqual(repr(power_rating._history), "0.25 * <Prefix Kilo: k = 1000> * "
                         "<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V>")

    def test_history_mul_products(self):
        """
        Check that multiplying a two products adds all factors to the same
        product.
        """
        sam = UnitSystem("systeme a moi", 4)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilo", "kg")
        kelvin = sam.create_base_unit(3, "Kelvin", "K")

        prod_a = metre * second
        prod_b = kilogram * kelvin

        prod = prod_a * prod_b

        self.assertEqual(repr(prod._history),
                         "<Unit Metre: 1 m = 1 m> * "
                         "<Unit Sec: 1 s = 1 s> * "
                         "<Unit Kilo: 1 kg = 1 kg> * "
                         "<Unit Kelvin: 1 K = 1 K>")

    def test_history_mul_named_products(self):
        """
        Check that multiplying a two named products does not copy any history.
        """
        sam = UnitSystem("systeme a moi", 4)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilo", "kg")
        kelvin = sam.create_base_unit(3, "Kelvin", "K")

        prod_a = sam.register_unit(metre * second, "Prod A", "A")
        prod_b = sam.register_unit(kilogram * kelvin, "Prod B", "B")

        prod = prod_a * prod_b

        self.assertEqual(repr(prod._history),
                         "<Unit Prod A: 1 A = 1 m s> * "
                         "<Unit Prod B: 1 B = 1 kg K>")

    def test_history_mul_second_level(self):
        """
        Check that multiplying a unit with number propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 2
        other_unnamed = some_unit * metre

        self.assertEqual(repr(other_unnamed._history),
                         "<Unit Sec: 1 s = 1 s> * 2 * "
                         "<Unit Metre: 1 m = 1 m>")

    def test_history_rmul_second_level(self):
        """
        Check that right-multiplying a unit with another unit propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = 3 * second
        other_unnamed = metre * some_unit

        self.assertEqual(repr(other_unnamed._history),
                         "<Unit Metre: 1 m = 1 m> * 3 * <Unit Sec: 1 s = 1 s>")

    def test_history_mul_second_level_number(self):
        """
        Check that multiplying a unit with number propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 2
        other_unnamed = some_unit * 3

        self.assertEqual(repr(other_unnamed._history),
                         "<Unit Sec: 1 s = 1 s> * 2 * 3")

    def test_history_rmul_second_level_number(self):
        """
        Check that right-multiplying a unit with number propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = 3 * second
        other_unnamed = 2 * some_unit

        self.assertEqual(repr(other_unnamed._history),
                         "2 * 3 * <Unit Sec: 1 s = 1 s>")

    ############################################################
    # Arithmetic history: Division
    def test_history_div_storage(self):
        """
        Check that dividing two units stores a fraction.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        speed = metre * second
        self.assertEqual(repr(speed._history),
                         "<Unit Metre: 1 m = 1 m> * <Unit Sec: 1 s = 1 s>")

    def test_history_div_storage_number(self):
        """
        Check that dividing a unit with a number does store this operation.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        car = metre / 5
        self.assertEqual(repr(car._history), "<Unit Metre: 1 m = 1 m> / 5")

        speed_limit = car / second
        self.assertEqual(repr(speed_limit._history),
                         "(<Unit Metre: 1 m = 1 m> / 5) / " 
                         "<Unit Sec: 1 s = 1 s>")

    def test_history_div_product(self):
        """
        Check that dividing a unit with a product of units creates a new
        fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")
        volt = sam.create_base_unit(2, "Volt", "V")

        coulomb = ampere * second
        inv_farad = volt / coulomb
        self.assertEqual(repr(inv_farad._history), "<Unit Volt: 1 V = 1 V> / "
                         "(<Unit Amp: 1 A = 1 A> * <Unit Sec: 1 s = 1 s>)")

    def test_history_div_fraction(self):
        """
        Check that dividing a unit with a fraction of units creates a new
        fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        joule = sam.create_base_unit(2, "Joule", "J")

        speed = metre / second
        energy_per_speed = joule / speed
        self.assertEqual(repr(energy_per_speed._history),
                         "<Unit Joule: 1 J = 1 J> / "
                         "(<Unit Metre: 1 m = 1 m> / <Unit Sec: 1 s = 1 s>)")

    def test_history_div_power(self):
        """
        Check that dividing a unit with a power of units creates a new
        fraction.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        second_2 = second**2
        acceleration = metre / second_2
        self.assertEqual(repr(acceleration._history),
                         "<Unit Metre: 1 m = 1 m> / "
                         "(<Unit Sec: 1 s = 1 s>^2)")

    def test_history_div_named_product(self):
        """
        Check that dividing a unit with a named product of units does not
        copy the whole history of the named product.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        second = sam.create_base_unit(1, "Sec", "s")
        volt = sam.create_base_unit(2, "Volt", "V")

        coulomb = sam.register_unit(ampere * second, "Coulomb", "C")
        inv_farad = volt / coulomb
        self.assertEqual(repr(inv_farad._history), "<Unit Volt: 1 V = 1 V> / "
                         "<Unit Coulomb: 1 C = 1 A s>")

    def test_history_div_named_fraction(self):
        """
        Check that dividing a unit with a named fraction of units does not
        copy the whole history of the named fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        joule = sam.create_base_unit(2, "Joule", "J")

        speed = sam.register_unit(metre / second, "Walk", "w")
        energy_per_speed = joule / speed
        self.assertEqual(repr(energy_per_speed._history),
                         "<Unit Joule: 1 J = 1 J> / "
                         "<Unit Walk: 1 w = 1 m s^(-1)>")

    def test_history_div_named_power(self):
        """
        Check that dividing a unit with a named power of units does not copy
        the whole history of the named power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        second_2 = sam.register_unit(second**2, "SecondSecond", "s2")
        acceleration = metre / second_2
        self.assertEqual(repr(acceleration._history),
                         "<Unit Metre: 1 m = 1 m> / "
                         "<Unit SecondSecond: 1 s2 = 1 s^2>")

    def test_history_div_named_prefix_named_unit(self):
        """
        Check that dividing a named unit by a named prefix creates a fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        kilo_amp = ampere / kilo
        self.assertEqual(repr(kilo_amp._history), "<Unit Amp: 1 A = 1 A> / "
                         "<Prefix Kilo: k = 1000>")

    def test_history_div_unnamed_prefix_named_unit(self):
        """
        Check that dividing a named unit by an unnamed prefix creates a
        fraction with a product in the denominator.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        fuse_amp = ampere / (0.016 * kilo)
        self.assertEqual(repr(fuse_amp._history), "<Unit Amp: 1 A = 1 A> / "
                         "(0.016 * <Prefix Kilo: k = 1000>)")

    def test_history_div_named_prefix_unnamed_unit(self):
        """
        Check that dividing a unnamed unit by an named prefix creates a
        fraction with a product in the numerator.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        kilo_amp = watt / kilo
        self.assertEqual(repr(kilo_amp._history), "(<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V>) / "
                         "<Prefix Kilo: k = 1000>")

    def test_history_div_unnamed_prefix_unnamed_unit(self):
        """
        Check that dividing a unnamed unit by an unnamed prefix creates a
        fraction with a product in the numerator and the denoninator.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        power_rating = watt / (0.25 * kilo)
        self.assertEqual(repr(power_rating._history), "(<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V>) / "
                         "(0.25 * <Prefix Kilo: k = 1000>)")

    def test_history_rdiv_storage_number(self):
        """
        Check that right-dividing a units with a number stores a fraction.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        car = 5 / metre
        self.assertEqual(repr(car._history), "5 / <Unit Metre: 1 m = 1 m>")

    def test_history_rdiv_product(self):
        """
        Check that right-dividing a unit with a product of units creates a new
        fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        something = kilogram * metre
        momentum = something / second
        self.assertEqual(repr(momentum._history),
                         "(<Unit Kilogram: 1 kg = 1 kg> * <Unit Metre: 1 m = 1 m>) / "
                         "<Unit Sec: 1 s = 1 s>")

    def test_history_rdiv_fraction(self):
        """
        Check that right-dividing a unit with a fraction of units places a new
        produce or appends the unit in the denominator.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        joule = sam.create_base_unit(2, "Joule", "J")

        speed = metre / second
        acceleration = speed / second
        self.assertEqual(repr(acceleration._history),
                         "(<Unit Metre: 1 m = 1 m> / <Unit Sec: 1 s = 1 s>) / "
                         "<Unit Sec: 1 s = 1 s>")

    def test_history_rdiv_power(self):
        """
        Check that right-dividing a unit with a power of units creates a new
        fraction.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        second_2 = second**2
        inv_acceleration = second_2 / metre
        self.assertEqual(repr(inv_acceleration._history),
                         "(<Unit Sec: 1 s = 1 s>^2) / "
                         "<Unit Metre: 1 m = 1 m>")

    def test_history_rdiv_named_product(self):
        """
        Check that right-dividing a unit with a named product of units does
        not copy the whole history of the named product.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        something = sam.register_unit(kilogram * metre, "Something", "S")
        momentum = something / second
        self.assertEqual(repr(momentum._history),
                         "<Unit Something: 1 S = 1 m kg> / "
                         "<Unit Sec: 1 s = 1 s>")

    def test_history_rdiv_named_fraction(self):
        """
        Check that right-dividing a unit with a named fraction of units
        does not copy the whole history of the named fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        joule = sam.create_base_unit(2, "Joule", "J")

        speed = sam.register_unit(metre / second, "Walk", "w")
        acceleration = speed / second
        self.assertEqual(repr(acceleration._history),
                         "<Unit Walk: 1 w = 1 m s^(-1)> / "
                         "<Unit Sec: 1 s = 1 s>")

    def test_history_rdiv_named_power(self):
        """
        Check that right-dividing a unit with a named power of units
        creates does not copy the whole history of the named power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        second_2 = sam.register_unit(second**2, "SecondSecond", "s2")
        inv_acceleration = second_2 / metre
        self.assertEqual(repr(inv_acceleration._history),
                         "<Unit SecondSecond: 1 s2 = 1 s^2> / "
                         "<Unit Metre: 1 m = 1 m>")

    def test_history_rdiv_named_prefix_named_unit(self):
        """
        Check that dividing an named prefix by an named unit creates a
        fraction.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        coef = kilo / ampere
        self.assertEqual(repr(coef._history), "<Prefix Kilo: k = 1000> / "
                         "<Unit Amp: 1 A = 1 A>")

    def test_history_rdiv_unnamed_prefix_named_unit(self):
        """
        Check that dividing an unnamed prefix by a named unit creates a
        fraction with a product in the numerator.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        coef = (0.016 * kilo) / ampere
        self.assertEqual(repr(coef._history), "(0.016 * <Prefix Kilo: k = 1000>) / "
                         "<Unit Amp: 1 A = 1 A>")
    def test_history_rdiv_named_prefix_unnamed_unit(self):
        """
        Check that dividing a named prefix by an unnamed unit creates a
        fraction with a product in the denominator.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        heat_coef = kilo / watt
        self.assertEqual(repr(heat_coef._history), "<Prefix Kilo: k = 1000> / "
                         "(<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V>)")

    def test_history_rdiv_unnamed_prefix_unnamed_unit(self):
        """
        Check that dividing a unnamed prefix by an unnamed unit creates a
        fraction with a product in the numerator and the denoninator.
        """
        sam = UnitSystem("systeme a moi", 3)
        ampere = sam.create_base_unit(0, "Amp", "A")
        volt = sam.create_base_unit(1, "Volt", "V")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        watt = ampere * volt
        heat_coef = (0.016 * kilo) / watt
        self.assertEqual(repr(heat_coef._history), "(0.016 * <Prefix Kilo: k = 1000>) / "
                         "(<Unit Amp: 1 A = 1 A> * "
                         "<Unit Volt: 1 V = 1 V>)")

    def test_history_rdiv_fractions(self):
        """
        Check that dividing a two fractions creates a new fraction with a
        fraction in the numerator and denominator.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilo", "kg")

        inv_speed = second / metre
        fuel_consumption = kilogram  / second
        thrust = fuel_consumption / inv_speed
        self.assertEqual(repr(thrust._history),
                         "(<Unit Kilo: 1 kg = 1 kg> / "
                         "<Unit Sec: 1 s = 1 s>) / "
                         "(<Unit Sec: 1 s = 1 s> / "
                         "<Unit Metre: 1 m = 1 m>)")

    def test_history_div_named_fractions(self):
        """
        Check that dividing a two named fractions does not copy any history.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")
        kilogram = sam.create_base_unit(2, "Kilo", "kg")

        inv_speed = sam.register_unit(second / metre, "InvWalk", "iw")
        fuel_consumption = sam.register_unit(kilogram  / second, "Kilo/Sec",
                                             "kgps")
        thrust = fuel_consumption / inv_speed
        self.assertEqual(repr(thrust._history),
                         "<Unit Kilo/Sec: 1 kgps = 1 s^(-1) kg> / "
                         "<Unit InvWalk: 1 iw = 1 m^(-1) s>")

    def test_history_div_second_level(self):
        """
        Check that dividing a unit with number propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 2
        other_unnamed = some_unit / metre

        self.assertEqual(repr(other_unnamed._history),
                         "(<Unit Sec: 1 s = 1 s> * 2) / "
                         "<Unit Metre: 1 m = 1 m>")

    def test_history_rdiv_second_level(self):
        """
        Check that right-dividing a unit with another unit propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = 3 * second
        other_unnamed = metre / some_unit

        self.assertEqual(repr(other_unnamed._history),
                         "<Unit Metre: 1 m = 1 m> / "
                         "(3 * <Unit Sec: 1 s = 1 s>)")

    def test_history_div_second_level_number(self):
        """
        Check that dividing a unit with number propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second / 2
        other_unnamed = some_unit / 3

        self.assertEqual(repr(other_unnamed._history),
                         "(<Unit Sec: 1 s = 1 s> / 2) / 3")

    def test_history_rdiv_second_level_number(self):
        """
        Check that right-dividing a unit with number propagates the history if
        the unit has already a history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = 3 / second
        other_unnamed = 2 / some_unit

        self.assertEqual(repr(other_unnamed._history),
                         "2 / (3 / <Unit Sec: 1 s = 1 s>)")

    ############################################################
    # Arithmetic history: Power
    def test_history_pow_storage(self):
        """
        Check that raising a unit stores a power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        area = metre**2
        self.assertEqual(repr(area._history),
                         "<Unit Metre: 1 m = 1 m>^2")

    def test_history_pow_product(self):
        """
        Check that raising a product of units creates a new power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        Newton = sam.create_base_unit(1, "Newton", "N")

        joule = (Newton * metre)**2
        self.assertEqual(repr(joule._history),
                         "(<Unit Newton: 1 N = 1 N> * "
                         "<Unit Metre: 1 m = 1 m>)^2")

    def test_history_pow_fraction(self):
        """
        Check that raising a fraction of units creates a new power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        speed2 = (metre / second)**2
        self.assertEqual(repr(speed2._history),
                         "(<Unit Metre: 1 m = 1 m> / "
                         "<Unit Sec: 1 s = 1 s>)^2")

    def test_history_pow_power(self):
        """
        Check that raising a power of units creates a new power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        four = (metre**2)**2
        self.assertEqual(repr(four._history),
                         "(<Unit Metre: 1 m = 1 m>^2)^2")

    def test_history_pow_named_product(self):
        """
        Check that raising a named product of units does not copy the whole
        history of the named product.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        Newton = sam.create_base_unit(1, "Newton", "N")

        joule = sam.register_unit(Newton * metre, "Joule", "J")
        joule2 = joule**2
        self.assertEqual(repr(joule2._history),
                         "<Unit Joule: 1 J = 1 m N>^2")

    def test_history_pow_named_fraction(self):
        """
        Check that raising a named fraction of units does not copy the whole
        history of the named fraction.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        speed = sam.register_unit(metre / second, "Walk", "w")
        speed2 = speed**2
        self.assertEqual(repr(speed2._history),
                         "<Unit Walk: 1 w = 1 m s^(-1)>^2")

    def test_history_pow_named_power(self):
        """
        Check that raising a named power of a unit does not copy the whole
        history of the named power.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        area = sam.register_unit(metre**2, "Area", "a")
        four = area**2
        self.assertEqual(repr(four._history),
                         "<Unit Area: 1 a = 1 m^2>^2")

    ############################################################
    # History sanity-checks

    def test_history_mul_unnamed_none(self):
        """
        Check that an exception is raised if self is unnamed and the history
        is None.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 1
        some_unit._history = None

        self.assertRaises(Exception, lambda a, b: a * b, some_unit, second)

#     def test_history_mul_number_history(self):
#         """
#         Check that an exception is raised if the history is a number.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         some_unit._history = 3.14
# 
#         self.assertRaises(Exception, lambda a, b: a * b, some_unit, second)
# 
#     def test_history_mul_unnamed_history(self):
#         """
#         Check that an exception is raised if the history is an unnamed unit.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         other_unnamed = metre * 2
#         some_unit._history = other_unnamed
# 
#         self.assertRaises(Exception, lambda a, b: a * b, some_unit, second)

    def test_history_mul_unnamed_prefix_wo_history(self):
        """
        Check that an exception is raised if other is an unnamed prefix wihtout
        history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        unnamed_prefix = 1000 * kilo
        unnamed_prefix._history = None

        self.assertRaises(Exception, lambda a, b: a * b, metre, unnamed_prefix)

    def test_history_rmul_unnamed_none(self):
        """
        Check that an exception is raised if self is unnamed and the history
        is None.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 1
        some_unit._history = None

        self.assertRaises(Exception, lambda a, b: a * b, second, some_unit)

#     def test_history_rmul_number_history(self):
#         """
#         Check that an exception is raised if the history is a number.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         some_unit._history = 3.14
# 
#         self.assertRaises(Exception, lambda a, b: a * b, second, some_unit)
# 
#     def test_history_rmul_unnamed_history(self):
#         """
#         Check that an exception is raised if the history is a unnamed unit.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         other_unnamed = metre * 2
#         some_unit._history = other_unnamed
# 
#         self.assertRaises(Exception, lambda a, b: a * b, second, some_unit)

    def test_history_rmul_unnamed_prefix_wo_history(self):
        """
        Check that an exception is raised if other is an unnamed prefix wihtout
        history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        unnamed_prefix = 1000 * kilo
        unnamed_prefix._history = None

        self.assertRaises(Exception, lambda a, b: a * b, unnamed_prefix, metre)

    def test_history_div_unnamed_none(self):
        """
        Check that an exception is raised if self is unnamed and the history
        is None.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 1
        some_unit._history = None

        self.assertRaises(Exception, lambda a, b: a / b, some_unit, second)

#     def test_history_div_number_history(self):
#         """
#         Check that an exception is raised if the history is a number.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         some_unit._history = 3.14
# 
#         self.assertRaises(Exception, lambda a, b: a / b, some_unit, second)
# 
#     def test_history_div_unnamed_history(self):
#         """
#         Check that an exception is raised if the history is an unnamed unit.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         other_unnamed = metre * 2
#         some_unit._history = other_unnamed
# 
#         self.assertRaises(Exception, lambda a, b: a / b, some_unit, second)

    def test_history_div_unnamed_prefix_wo_history(self):
        """
        Check that an exception is raised if other is an unnamed prefix wihtout
        history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        unnamed_prefix = 1000 * kilo
        unnamed_prefix._history = None

        self.assertRaises(Exception, lambda a, b: a / b, metre, unnamed_prefix)

    def test_history_rdiv_unnamed_none(self):
        """
        Check that an exception is raised if self is unnamed and the history
        is None.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Sec", "s")

        some_unit = second * 1
        some_unit._history = None

        self.assertRaises(Exception, lambda a, b: a / b, second, some_unit)

#     def test_history_rdiv_number_history(self):
#         """
#         Check that an exception is raised if the history is a number.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         some_unit._history = 3.14
# 
#         self.assertRaises(Exception, lambda a, b: a / b, second, some_unit)
# 
#     def test_history_rdiv_unnamed_history(self):
#         """
#         Check that an exception is raised if the history is a unnamed unit.
#         """
#         sam = UnitSystem("systeme a moi", 2)
#         metre = sam.create_base_unit(0, "Metre", "m")
#         second = sam.create_base_unit(1, "Sec", "s")
# 
#         some_unit = second * 1
#         other_unnamed = metre * 2
#         some_unit._history = other_unnamed
# 
#         self.assertRaises(Exception, lambda a, b: a / b, second, some_unit)

    def test_history_rdiv_unnamed_prefix_wo_history(self):
        """
        Check that an exception is raised if other is an unnamed prefix wihtout
        history.
        """
        sam = UnitSystem("systeme a moi", 2)
        metre = sam.create_base_unit(0, "Metre", "m")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        unnamed_prefix = 1000 * kilo
        unnamed_prefix._history = None

        self.assertRaises(Exception, lambda a, b: a / b, unnamed_prefix, metre)


    ############################################################
    # String representation

    def test_history_str(self):
        """
        Check that history_str() calls str() on the history object.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        newton = (kilogram * metre) / second**2

        self.assertEqual(newton.history_str(), "kg * m / s^2")

        newton._history.str = mock.MagicMock()
        newton.history_str()
        newton._history.str.assert_called_once_with(latex=False)

    def test_history_str_none(self):
        """
        Check that history_str() returns None, if the history is None.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        newton = (kilogram * metre) / second**2

        self.assertIsNone(metre.history_str())

        newton._history = None
        self.assertIsNone(newton.history_str())

    def test_history_str_latex(self):
        """
        Check that history_str() calls str() on the history object when
        latex=True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        newton = (kilogram * metre) / second**2

        self.assertEqual(newton.history_str(latex=True), r"\frac{kg m}{s^{2}}")

        newton._history.str = mock.MagicMock()
        newton.history_str(latex=True)
        newton._history.str.assert_called_once_with(latex=True)

    def test_history_str_latex_none(self):
        """
        Check that history_str() returns None, if the history is None and
        latex=True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        newton = (kilogram * metre) / second**2

        self.assertIsNone(metre.history_str(latex=True))

        newton._history = None
        self.assertIsNone(newton.history_str(latex=True))

    def test_base_representation(self):
        """
        Check that base_representation() returns a string including the factor
        and a product of base units.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        milli_newton = 0.001 * (kilogram * metre) / second**2
        self.assertEqual(milli_newton.base_representation(), 
                         "0.001 m s^(-2) kg")

    def test_base_representation_latex(self):
        """
        Check that base_representation() returns a string including the factor
        and a product of base units when latex=True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        milli_newton = 0.001 * (kilogram * metre) / second**2
        self.assertEqual(milli_newton.base_representation(latex=True), 
                         "0.001 m s^{-2} kg")

    def test_base_representation_suppress(self):
        """
        Check that base_representation() returns a string without the factor
        when suppress_factor is True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        milli_newton = 0.001 * (kilogram * metre) / second**2
        self.assertEqual(milli_newton.base_representation(suppress_factor=True),
                         "m s^(-2) kg")

    def test_base_representation_latex_suppress(self):
        """
        Check that base_representation() returns a string without the factor
        when suppress_factor and latex is True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        milli_newton = 0.001 * (kilogram * metre) / second**2
        self.assertEqual(milli_newton.base_representation(latex=True,
                                                          suppress_factor=True),
                         "m s^{-2} kg")

    def test_str_named(self):
        """
        Check that str() returns the symbol of a named unit.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        micro_newton = 1e-6 * (kilogram * metre) / second**2
        micro_newton = sam.register_unit(micro_newton, "Micro-Newton", "uN",
                                         r"\mu N")

        self.assertEqual(micro_newton.str(), "uN")

    def test_str_named_latex(self):
        """
        Check that str() returns the latex symbol of a named unit when
        latex=True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        micro_newton = 1e-6 * (kilogram * metre) / second**2
        micro_newton = sam.register_unit(micro_newton, "Micro-Newton", "uN",
                                         r"\mu N")

        self.assertEqual(micro_newton.str(latex=True), r"\mu N")


    def test_str_unnamed(self):
        """
        Check that str() returns the factor and the history string of the
        unnamed unit.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        micro_newton = 1e-6 * (kilogram * metre) / second**2

        self.assertEqual(micro_newton.str(), "1e-06 * kg * m / s^2")

    def test_str_unnamed_latex(self):
        """
        Check that str() returns the factor and the latex history string of
        the unnamed unit if latex=True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        micro_newton = 1e-6 * ((kilogram * metre) / second**2)

        self.assertEqual(micro_newton.str(latex=True),
                         r"1e-06 \frac{kg m}{s^{2}}")

    def test_str_prefixed_unit(self):
        """
        Check that str() returns the factor of the prefix and the symbol of
        the unit.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        kilometre = kilo * metre
        self.assertEqual(kilometre.str(), "1000 * m")

    def test_str_prefixed_unit_latex(self):
        """
        Check that str() returns the factor of the prefix and the latex of
        the unit when latex=True.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilo = sam.create_prefix(1000, "Kilo", "k")

        kilometre = kilo * metre
        self.assertEqual(kilometre.str(latex=True), "1000 m")

    def test_str_operator(self):
        """
        Check that __str__() calls str().
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m")
        second = sam.create_base_unit(1, "Second", "s")
        kilogram = sam.create_base_unit(2, "Kilogram", "kg")

        micro_newton = 1e-6 * (kilogram * metre) / second**2

        self.assertEqual(str(micro_newton), "1e-06 * kg * m / s^2")

        micro_newton.str = mock.MagicMock(side_effect="hello")
        str(micro_newton)
        micro_newton.str.assert_called_once_with()
