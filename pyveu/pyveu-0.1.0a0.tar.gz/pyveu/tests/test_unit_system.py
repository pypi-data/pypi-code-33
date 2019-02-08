
# Copyright (C) 2018 Frank Sauerburger

import unittest

import numpy as np

import pyveu
from pyveu import Prefix, Unit, UnitSystem

class UnitSystemTests(unittest.TestCase):
    """
    The UnitSystemTests class implements unit tests for the UnitSystem class.
    """

    ############################################################
    # __init__
    def test_init_storage(self):
        """
        Check that the constructor stores its arguments.
        """
        # positional arguments
        us = UnitSystem("systeme-a-moi", 3, 1)

        self.assertEqual(us._name, "systeme-a-moi")
        self.assertEqual(us._n_base, 3)
        self.assertEqual(us._n_dimensionless, 1)

        # keyword arguments
        us = UnitSystem(name="systeme-a-moi", n_base=3, n_dimensionless=1)

        self.assertEqual(us._name, "systeme-a-moi")
        self.assertEqual(us._n_base, 3)
        self.assertEqual(us._n_dimensionless, 1)

    def test_init_default(self):
        """
        Check that the constructor has a default value of n_dimensionless, but
        not for the other two. The default value for n_dimensionless should be
        0.
        """
        us = UnitSystem("systeme-a-moi", 3)

        self.assertEqual(us._name, "systeme-a-moi")
        self.assertEqual(us._n_base, 3)
        self.assertEqual(us._n_dimensionless, 0)

        self.assertRaises(TypeError, UnitSystem, "systeme-a-moi")

    def test_init_registies(self):
        """
        Check that the constructor creates all local registries.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

        self.assertEqual(us._reg_base, [None, None, None, None])

    def test_init_dimensionless_mask(self):
        """
        Check that the constructor creates the mask which flags dimensionless
        base units.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        self.assertEqual(list(us._dimensionless_mask), [0, 0, 0, 1])
        self.assertIsInstance(us._dimensionless_mask, np.ndarray)

        us = UnitSystem("systeme-a-moi", 7, 3)
        self.assertEqual(list(us._dimensionless_mask), [0, 0, 0, 0, 1, 1, 1])
        self.assertIsInstance(us._dimensionless_mask, np.ndarray)
        
    ############################################################
    # create_base_unit
    def test_create_base_mandatory_args(self):
        """
        Check that create_base_unit requires the following arguments:
          - index
          - label
          - symbol
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        self.assertRaises(TypeError, us.create_base_unit, 
                          1, "Label")

        try:
            us.create_base_unit(1, "Label", "symbol")
        except TypeError as e:
            self.fail(e)

    def test_create_base_return(self):
        """
        Check that create_base_unit() returns a unit object which has the
        given label, symbol, latex symbol.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_base_unit(0, "Meter", "m", None)

        self.assertIsInstance(meter, Unit)
        self.assertEqual(repr(meter), "<Unit Meter: 1 m = 1 m>")

    def test_create_base_stored_in_base_registry_default(self):
        """
        Check that the base unit is placed into the base registry. Perform
        this test with the default value for the register parameter.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        meter = us.create_base_unit(2, "Meter", "m", None)
        self.assertEqual(us._reg_base, [None, None, meter, None])

        second = us.create_base_unit(1, "Second", "s", None)
        self.assertEqual(us._reg_base, [None, second, meter, None])

    def test_create_base_stored_in_base_registry_True(self):
        """
        Check that the base unit is placed into the base registry. Perform
        this test with the register parameter set to True.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        meter = us.create_base_unit(2, "Meter", "m", None, register=True)
        self.assertEqual(us._reg_base, [None, None, meter, None])

        second = us.create_base_unit(1, "Second", "s", None, register=True)
        self.assertEqual(us._reg_base, [None, second, meter, None])

    def test_create_base_stored_in_base_registry_False(self):
        """
        Check that the base unit is placed into the base registry. Perform
        this test with the register parameter set to False. Registering base
        units should be independent of registering them as regular units.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        meter = us.create_base_unit(2, "Meter", "m", None, register=False)
        self.assertEqual(us._reg_base, [None, None, meter, None])

        second = us.create_base_unit(1, "Second", "s", None, register=False)
        self.assertEqual(us._reg_base, [None, second, meter, None])

    def test_create_base_overwrite_base(self):
        """
        Check that overwriting a base unit fails.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        us.create_base_unit(2, "Meter", "m", None)
        self.assertRaises(pyveu.BaseUnitExists, us.create_base_unit, 2,
                          "Second", "s", None)

    def test_create_base_unit_vector(self):
        """
        Check that the units are annotated with the correct base unit vectors
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        meter = us.create_base_unit(2, "Meter", "m", None)
        self.assertEqual(list(meter.unit_vector()), [0, 0, 1, 0])
        
        second = us.create_base_unit(1, "Second", "s", None)
        self.assertEqual(list(second.unit_vector()), [0, 1, 0, 0])
        
        rad = us.create_base_unit(3, "Radian", "rad", None)
        self.assertEqual(list(rad.unit_vector()), [0, 0, 0, 1])

    def test_create_base_unit_system(self):
        """
        Check that the units are annotated with this unit system.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)

        meter = us.create_base_unit(2, "Meter", "m", None)
        self.assertIs(meter.unit_system(), us)

    def test_create_base_stored_in_registry_default(self):
        """
        Check that the base unit NOT is placed into the registry if the
        'register' parameter is omitted.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_base_unit(2, "Meter", "m", "tex")

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

    def test_create_base_stored_in_registry_False(self):
        """
        Check that the base unit NOT is placed into the registry if the
        'register' parameter is set to False.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_base_unit(2, "Meter", "m", "tex", False)

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

    def test_create_base_stored_in_registry_True(self):
        """
        Check that the base unit is placed into the registry if the
        'register' parameter is set to True.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_base_unit(2, "Meter", "m", "tex", True)

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(repr(us._reg_units_all), "[<Unit Meter: 1 m = 1 m>]")
        self.assertEqual(repr(us._reg_units_label),
            "{'Meter': <Unit Meter: 1 m = 1 m>}")
        self.assertEqual(repr(us._reg_units_symbol),
            "{'m': <Unit Meter: 1 m = 1 m>}")
        self.assertEqual(repr(us._reg_units_latex),
            "{'tex': <Unit Meter: 1 m = 1 m>}")

    def test_create_base_stored_in_registry_no_latex(self):
        """
        Check that the base unit is placed into the registry if the
        'register' parameter is set to True. Furthermore, check that 'None'
        registry entries do not occur, if the symbol latex is missing.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_base_unit(2, "Meter", "m", register=True)

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(repr(us._reg_units_all), "[<Unit Meter: 1 m = 1 m>]")
        self.assertEqual(repr(us._reg_units_label),
            "{'Meter': <Unit Meter: 1 m = 1 m>}")
        self.assertEqual(repr(us._reg_units_symbol),
            "{'m': <Unit Meter: 1 m = 1 m>}")
        self.assertEqual(us._reg_units_latex, {})
        
    ############################################################
    # Base representation
    def get_toy_unit_system(self):
        """
        Returns a unit system with the following registered base units:
          - Kilogram, kg 
          - Second, s, \\int
          - Meter, m

        The second unit has (nonsensical) a latex symbol, to test the latex
        functions of the base representation.
        """
        us = UnitSystem("ToyUnitSystem", 3)
        us.create_base_unit(0, "Kilogram", "kg")
        us.create_base_unit(1, "Second", "s", r"\int")
        us.create_base_unit(2, "Meter", "m")

        return us


    def test_get_toy_unit_system(self):
        """
        Check that the above toy unit system has the appropriate base units
        are registered. THe appropriate base units are listed in the above
        comment.
        """
        us = self.get_toy_unit_system()

        self.assertEqual(len(us._reg_base), 3)
        self.assertEqual(repr(us._reg_base[0]),
                         "<Unit Kilogram: 1 kg = 1 kg>")
        self.assertEqual(repr(us._reg_base[1]),
                         "<Unit Second: 1 s = 1 s>")
        self.assertEqual(repr(us._reg_base[2]),
                         "<Unit Meter: 1 m = 1 m>")

    def test_base_repr_all(self):
        """
        Check that units all base units are included in the base
        representation.
        """
        us = self.get_toy_unit_system()

        self.assertEqual(us.base_representation([4, 3, 2]), "kg^4 s^3 m^2")

    def test_base_repr_zero(self):
        """
        Check that units with vanishing exponents are removed from the
        representation.
        """
        us = self.get_toy_unit_system()

        self.assertEqual(us.base_representation([0, 3, 2]), "s^3 m^2")
        self.assertEqual(us.base_representation([4, 0, 2]), "kg^4 m^2")
        self.assertEqual(us.base_representation([4, 3, 0]), "kg^4 s^3")

        self.assertEqual(us.base_representation([4, 0, 0]), "kg^4")
        self.assertEqual(us.base_representation([0, 3, 0]), "s^3")
        self.assertEqual(us.base_representation([0, 0, 2]), "m^2")

        self.assertEqual(us.base_representation([0, 0, 0]), "")

    def test_base_repr_half(self):
        """
        Check that units with 1/2 exponents are printed with exponent.
        """
        us = self.get_toy_unit_system()

        self.assertEqual(us.base_representation([0.5, 3, 2]),
                         "kg^0.5 s^3 m^2")
        self.assertEqual(us.base_representation([4, 0.5, 2]),
                         "kg^4 s^0.5 m^2")
        self.assertEqual(us.base_representation([4, 3, 0.5]),
                         "kg^4 s^3 m^0.5")

        self.assertEqual(us.base_representation([4, 0.5, 0.5]),
                         "kg^4 s^0.5 m^0.5")
        self.assertEqual(us.base_representation([0.5, 3, 0.5]),
                         "kg^0.5 s^3 m^0.5")
        self.assertEqual(us.base_representation([0.5, 0.5, 2]),
                         "kg^0.5 s^0.5 m^2")

        self.assertEqual(us.base_representation([0.5, 0.5, 0.5]),
                         "kg^0.5 s^0.5 m^0.5")

    def test_base_repr_one(self):
        """
        Check that units with unit exponents are printed without exponent.
        """
        us = self.get_toy_unit_system()

        self.assertEqual(us.base_representation([1, 3, 2]), "kg s^3 m^2")
        self.assertEqual(us.base_representation([4, 1, 2]), "kg^4 s m^2")
        self.assertEqual(us.base_representation([4, 3, 1]), "kg^4 s^3 m")

        self.assertEqual(us.base_representation([4, 1, 1]), "kg^4 s m")
        self.assertEqual(us.base_representation([1, 3, 1]), "kg s^3 m")
        self.assertEqual(us.base_representation([1, 1, 2]), "kg s m^2")

        self.assertEqual(us.base_representation([1, 1, 1]), "kg s m")

    def test_base_repr_negative(self):
        """
        Check that negative exponents are in parenthesis.
        """
        us = self.get_toy_unit_system()

        self.assertEqual(us.base_representation([-1, 3, 2]), "kg^(-1) s^3 m^2")
        self.assertEqual(us.base_representation([4, -3, 2]), "kg^4 s^(-3) m^2")
        self.assertEqual(us.base_representation([4, 3, -2]), "kg^4 s^3 m^(-2)")

    def test_base_repr_length(self):
        """
        Check that an assertion error is raised if the length of the unit
        vector is not three.
        """
        us = self.get_toy_unit_system()

        self.assertRaises(AssertionError, us.base_representation, [-1, 3])
        self.assertRaises(AssertionError, us.base_representation, [])
        self.assertRaises(AssertionError, us.base_representation,
                          [-1, 3, 2, 0])

    def test_base_repr_lors(self):
        """
        Check that units latex symbols are used when available 
        """
        us = self.get_toy_unit_system()

        self.assertEqual(us.base_representation([4, 3, 2], lors=True),
                         "kg^{4} \\int^{3} m^{2}")
        self.assertEqual(us.base_representation([4, 1, 2], lors=True),
                         "kg^{4} \\int m^{2}")
        self.assertEqual(us.base_representation([1, 0, 2], lors=True),
                         "kg m^{2}")
        self.assertEqual(us.base_representation([0, 0.5, 2], lors=True),
                         "\\int^{0.5} m^{2}")
        self.assertEqual(us.base_representation([0, -0.5, 2], lors=True), "\\int^{-0.5} m^{2}")

    def test_base_repr_uninit_base(self):
        """
        Check the base representation if not all base unit are created.
        """
        us = UnitSystem("system-a-moi", 3, 0)

        self.assertEqual(us.base_representation([4, 3, 2]),
                         "[base#0]^4 [base#1]^3 [base#2]^2")

    ############################################################
    # Register unit
    def test_register_unit_mandatory_args(self):
        """
        Check that register_unit() requires the following arguments:
          - unit
          - label
          - symbol
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], "Meter", "m", None, us)

        self.assertRaises(TypeError, us.register_unit, 
                          meter, "Meter")

        try:
            us.register_unit(meter, "Meter", "m")
        except TypeError as e:
            self.fail(e)

    def test_register_unit_stored_in_registry(self):
        """
        Check that the unit is placed into the registry.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], "Meter", "m", None, us)

        us.register_unit(meter, "Meter", "m", "tex")

        self.assertEqual(us._reg_prefixes_all, [])

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(repr(us._reg_units_all),
                         "[<Unit Meter: 1 m = 1 [base#2]>]")
        self.assertEqual(repr(us._reg_units_label),
                         "{'Meter': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(repr(us._reg_units_symbol),
                         "{'m': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(repr(us._reg_units_latex),
                         "{'tex': <Unit Meter: 1 m = 1 [base#2]>}")

    def test_register_unit_stored_in_registry_anonymous(self):
        """
        Check that a non-anonymous unit is placed into the registry.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], None, None, None, us)

        us.register_unit(meter, "Meter", "m", "tex")

        self.assertEqual(us._reg_prefixes_all, [])

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(repr(us._reg_units_all),
                         "[<Unit Meter: 1 m = 1 [base#2]>]")
        self.assertEqual(repr(us._reg_units_label),
                         "{'Meter': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(repr(us._reg_units_symbol),
                         "{'m': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(repr(us._reg_units_latex),
                         "{'tex': <Unit Meter: 1 m = 1 [base#2]>}")

    def test_register_unit_stored_in_registry_no_latex(self):
        """
        Furthermore, check that 'None' registry entries do not occur, if the
        symbol latex is missing.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], "Meter", "m", None, us)

        us.register_unit(meter, "Meter", "m")

        self.assertEqual(us._reg_prefixes_all, [])

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(repr(us._reg_units_all),
                         "[<Unit Meter: 1 m = 1 [base#2]>]")
        self.assertEqual(repr(us._reg_units_label),
                         "{'Meter': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(repr(us._reg_units_symbol),
                         "{'m': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(us._reg_units_latex, {})

    def test_register_unit_return_value(self):
        """
        Check that the return value is a non-anonymous unit.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], None, None, None, us)

        retval = us.register_unit(meter, "Meter", "m", "tex")

        self.assertEqual(repr(retval), "<Unit Meter: 1 m = 1 [base#2]>")

    def test_register_unit_collision_with_unit(self):
        """
        Check that a collision exception is raised when a unit with the same
        symbol exists.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        hour = Unit(3600, [0, 1, 0, 0], "Hour", "h", None, us)
        planck = Unit(1, [0, 0, 0, 1], "Planck", "h", None, us)

        us.register_unit(hour, "Hour", "h")

        self.assertRaises(pyveu.SymbolCollision, us.register_unit, planck,
                          "Planck", "h")

    def test_register_unit_collision_with_prefixed_unit(self):
        """
        Check that a collision exception is raised when a conflicting prefixed
        unit exists.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        inch = Unit(0.0254, [0, 0, 1, 0], "Inch", "in", None, us)
        minute = Unit(60, [0, 1, 0, 0], "Minute", "min", None, us)
        milli = Prefix(1e-3, "Milli", "m", None, us)

        us.register_unit(inch, "Inch", "in")
        us.register_prefix(milli, "Milli", "m")

        self.assertRaises(pyveu.SymbolCollision, us.register_unit, minute,
                          "Minute", "min")

    def test_register_unit_collision_with_unit_when_prefixed(self):
        """
        Check that a collision exception is raised when the added symbol
        conflicts with an existing unit when the added unit is prefixed.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        inch = Unit(0.0254, [0, 0, 1, 0], "Inch", "in", None, us)
        minute = Unit(60, [0, 1, 0, 0], "Minute", "min", None, us)
        milli = Prefix(1e-3, "Milli", "m", None, us)

        us.register_unit(minute, "Minute", "min")
        us.register_prefix(milli, "Milli", "m")

        self.assertRaises(pyveu.SymbolCollision, us.register_unit, inch,
                          "Inch", "in")

    def test_register_unit_collision_with_prefixed_unit_when_prefixed(self):
        """
        Check that a collision exception is raised when the added symbol
        conflicts with an existing prefixed unit when the added unit is
        prefixed.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        bc = Unit(1, [0, 0, 1, 0], "B-C-Unit", "bc", None, us)
        c = Unit(1, [0, 1, 0, 0], "C-Unit", "c", None, us)

        a = Prefix(1e-3, "A-Prefix", "a", None, us)
        ab = Prefix(1e-3, "A-B-Prefix", "ab", None, us)

        us.register_unit(bc, "B-C-Unit", "bc")
        us.register_prefix(a, "A-Prefix", "a")
        us.register_prefix(ab, "A-B-Prefix", "ab")

        # Conflict: ab-c vs. a-bc
        self.assertRaises(pyveu.SymbolCollision, us.register_unit, c,
                          "C-Unit", "c")

    def test_register_unit_unit_system_propagation(self):
        """
        Check that the returned unit has the correct unit system.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], None, None, None, us)

        retval = us.register_unit(meter, "Meter", "m", "tex")

        self.assertIs(retval.unit_system(), us)

    def test_register_unit_unit_system_check(self):
        """
        Check that registering a unit from a different unit system fails.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = Unit(1, [0, 0, 1, 0], None, None, None, us)

        other = UnitSystem("other", 4, 1)
        self.assertRaises(pyveu.DifferentUnitSystem, other.register_unit,
                          meter, "Meter", "m", "tex")

    ############################################################
    # Register prefix
    def test_register_prefix_mandatory_args(self):
        """
        Check that register_prefix() requires the following arguments:
          - prefix
          - label
          - symbol
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        micro = Prefix(1e-06, "Micro", "u", "\\mu", us)

        self.assertRaises(TypeError, us.register_prefix, 
                          micro, "Micro")

        try:
            us.register_prefix(micro, "Micro", "u")
        except TypeError as e:
            self.fail(e)

    def test_register_prefix_stored_in_registry(self):
        """
        Check that the prefix is placed into the registry.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        micro = Prefix(1e-06, "Micro", "u", "\\mu", us)

        us.register_prefix(micro, "Micro", "u", "\\mu")

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

        self.assertEqual(repr(us._reg_prefixes_all),
                         "[<Prefix Micro: u = 1e-06>]")
        self.assertEqual(repr(us._reg_prefixes_label),
                         "{'Micro': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_symbol),
                         "{'u': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_latex),
                         r"{'\\mu': <Prefix Micro: u = 1e-06>}")

    def test_register_prefix_stored_in_registry_anonymous(self):
        """
        Check that a non-anonymous prefix is placed into the registry.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        micro = Prefix(1e-06, None, None, None, us)

        us.register_prefix(micro, "Micro", "u", "\\mu")

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

        self.assertEqual(repr(us._reg_prefixes_all),
                         "[<Prefix Micro: u = 1e-06>]")
        self.assertEqual(repr(us._reg_prefixes_label),
                         "{'Micro': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_symbol),
                         "{'u': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_latex),
                         r"{'\\mu': <Prefix Micro: u = 1e-06>}")

    def test_register_prefix_stored_in_registry_no_latex(self):
        """
        Furthermore, check that 'None' registry entries do not occur, if the
        symbol latex is missing.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        micro = Prefix(1e-06, "Micro", "u", "\\mu", us)

        us.register_prefix(micro, "Micro", "u")

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

        self.assertEqual(repr(us._reg_prefixes_all),
                         "[<Prefix Micro: u = 1e-06>]")
        self.assertEqual(repr(us._reg_prefixes_label),
                         "{'Micro': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_symbol),
                         "{'u': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(us._reg_prefixes_latex, {})

    def test_register_prefix_return_value(self):
        """
        Check that the return value is a non-anonymous prefix.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        micro = Prefix(1e-06, None, None, None, us)

        retval = us.register_prefix(micro, "Micro", "u", "\\mu")

        self.assertEqual(repr(retval), "<Prefix Micro: u = 1e-06>")

    def test_register_prefix_collision_with_prefix(self):
        """
        Check that a collision exception is raised when a prefix with the same
        symbol exists (even when there are no units).
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        dozen = Prefix(12, "Dozen", "d", None, us)
        deci = Prefix(0.1, "Deci", "d", None, us)

        us.register_prefix(deci, "Deci", "d")

        self.assertRaises(pyveu.SymbolCollision, us.register_prefix, dozen,
                          "Dozen", "d")

    def test_register_prefix_collision_with_two_units(self):
        """
        Check that a collision exception is raised when a there is a unit,
        which when prefixed is identical to another unprefixed unit.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        inch = Unit(0.0254, [0, 0, 1, 0], "Inch", "in", None, us)
        minute = Unit(60, [0, 1, 0, 0], "Minute", "min", None, us)
        milli = Prefix(1e-3, "Milli", "m", None, us)

        us.register_unit(inch, "Inch", "in")
        us.register_unit(inch, "Minute", "min")

        self.assertRaises(pyveu.SymbolCollision, us.register_prefix, milli,
                          "Milli", "m")

    def test_register_prefix_no_collision_pure_prefix(self):
        """
        Check that a pure prefix does not cause collisions.
        """
        # pico first
        us = UnitSystem("systeme-a-moi", 4, 1)
        re = Unit(1, [1, 0, 0, 0], "Re", "re", None, us)
        p = Prefix(1e-12, "Pico", "p", None, us)

        pre = Prefix(1e-1, "Pre", "pre", None, us)

        us.register_unit(re, "Re", "re")
        us.register_prefix(p, "Pico", "p")

        try:
            us.register_prefix(pre, "Pre", "pre")
        except pyveu.SymbolCollision as e:
            self.fail(e)

        # pre first
        us = UnitSystem("systeme-a-moi", 4, 1)
        re = Unit(1, [1, 0, 0, 0], "Re", "re", None, us)
        p = Prefix(1e-12, "Pico", "p", None, us)

        pre = Prefix(1e-1, "Pre", "pre", None, us)

        us.register_unit(re, "Re", "re")
        us.register_prefix(pre, "Pre", "pre")

        try:
            us.register_prefix(p, "Pico", "p")
        except pyveu.SymbolCollision as e:
            self.fail(e)

    def test_register_prefix_collision_with_prefixed_unit_when_prefixed(self):
        """
        Check that a collision exception is raised when the added symbol
        conflicts with an existing prefixed unit when the added prefix is
        used on a different unit.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        bc = Unit(1, [0, 0, 1, 0], "B-C-Unit", "bc", None, us)
        c = Unit(1, [0, 1, 0, 0], "C-Unit", "c", None, us)

        a = Prefix(1e-3, "A-Prefix", "a", None, us)
        ab = Prefix(1e-3, "A-B-Prefix", "ab", None, us)

        us.register_unit(bc, "B-C-Unit", "bc")
        us.register_unit(c, "C-Unit", "c")
        us.register_prefix(ab, "A-B-Prefix", "ab")

        # Conflict: ab-c vs. a-bc
        self.assertRaises(pyveu.SymbolCollision, us.register_prefix, a,
                          "A-Prefix", "a")

    def test_register_prefix_unit_system_propagation(self):
        """
        Check that the returned prefix has the correct unit system.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        milli = Prefix(1e-3, "Milli", "m", None, us)

        retval = us.register_prefix(milli, "Milli", "m")

        self.assertIs(retval.unit_system(), us)

    def test_register_prefix_unit_system_check(self):
        """
        Check that registering a prefix from a different unit system fails.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        milli = Prefix(1e-3, "Milli", "m", None, us)

        other = UnitSystem("other", 4, 1)
        self.assertRaises(pyveu.DifferentUnitSystem, other.register_prefix,
                          milli, "Milli", "m")

    ############################################################
    # Create prefix/unit
    #
    # The tests are kept to a minimum, since these methods are rather
    # trivial. 

    def test_create_prefix_unit_system_propagation(self):
        """
        Check that the returned prefix has the correct unit system.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        milli = us.create_prefix(1e-3, "Milli", "m")
        self.assertIs(milli.unit_system(), us)

    def test_create_prefix_registered(self):
        """
        Check that the prefix is registered.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        micro = us.create_prefix(1e-06, "Micro", "u", "\\mu")

        self.assertEqual(us._reg_units_all, [])
        self.assertEqual(us._reg_units_label, {})
        self.assertEqual(us._reg_units_symbol, {})
        self.assertEqual(us._reg_units_latex, {})

        self.assertEqual(repr(us._reg_prefixes_all),
                         "[<Prefix Micro: u = 1e-06>]")
        self.assertEqual(repr(us._reg_prefixes_label),
                         "{'Micro': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_symbol),
                         "{'u': <Prefix Micro: u = 1e-06>}")
        self.assertEqual(repr(us._reg_prefixes_latex), 
                         r"{'\\mu': <Prefix Micro: u = 1e-06>}")

    def test_create_prefix_return_value(self):
        """
        Check that the returned prefix has the correct values.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        milli = us.create_prefix(0.001, "Milli", "m")
        self.assertEqual(repr(milli), "<Prefix Milli: m = 0.001>")

    def test_create_unit_unit_system_propagation(self):
        """
        Check that the returned unit has the correct unit system.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_unit(1e-3, [0, 0, 1, 0], "Meter", "m")
        self.assertIs(meter.unit_system(), us)

    def test_create_unit_registered(self):
        """
        Check that the unit is registered.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_unit(1, [0, 0, 1, 0], "Meter", "m")

        self.assertEqual(us._reg_prefixes_all, [])
        self.assertEqual(us._reg_prefixes_label, {})
        self.assertEqual(us._reg_prefixes_symbol, {})
        self.assertEqual(us._reg_prefixes_latex, {})

        self.assertEqual(repr(us._reg_units_all),
                         "[<Unit Meter: 1 m = 1 [base#2]>]")
        self.assertEqual(repr(us._reg_units_label),
                         "{'Meter': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(repr(us._reg_units_symbol),
                         "{'m': <Unit Meter: 1 m = 1 [base#2]>}")
        self.assertEqual(us._reg_prefixes_latex, {})

    def test_create_unit_return_value(self):
        """
        Check that the returned unit has the correct values.
        """
        us = UnitSystem("systeme-a-moi", 4, 1)
        meter = us.create_unit(1, [0, 0, 1, 0], "Meter", "m")
        self.assertEqual(repr(meter), "<Unit Meter: 1 m = 1 [base#2]>")

    ############################################################
    #  Dimensionless
    def test_dimensionless_dl_base(self):
        """
        Check that a dimensionless base unit is dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        radian = us.create_unit(1, [0, 0, 0, 1, 0], "Radian", "rad")
        self.assertTrue(us.dimensionless(radian))

        steradian = us.create_unit(1, [0, 0, 0, 0, 1], "Steradian", "sr")
        self.assertTrue(us.dimensionless(steradian))

    def test_dimensionless_ndl_base(self):
        """
        Check that a non-dimensionless base unit is not dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        meter = us.create_unit(1, [0, 0, 1, 0, 0], "Meter", "m")
        self.assertFalse(us.dimensionless(meter))

    def test_dimensionless_dl_combination(self):
        """
        Check that a dimensionless linear combination is dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        comb = us.create_unit(2, [0, 0, 0, 1, 2], "comb", "c")
        self.assertTrue(us.dimensionless(comb))

    def test_dimensionless_pndl_combination(self):
        """
        Check that a pure non-dimensionless linear combination is not
        dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        comb = us.create_unit(2, [1, 0, 1, 0, 0], "comb", "c")
        self.assertFalse(us.dimensionless(comb))

    def test_dimensionless_mndl_combination(self):
        """
        Check that a mix non-dimensionless linear combination is not
        dimensionless.
        """
        us = UnitSystem("systeme-a-moi", 5, 2)

        comb = us.create_unit(2, [1, 0, 1, 0, 1], "comb", "c")
        self.assertFalse(us.dimensionless(comb))

    ############################################################
    # parse_unit
    def test_parse_unit_no_prefix(self):
        """
        Test that a unit is parsed when the unit is not prefixed.
        """
        us = UnitSystem("systeme-a-moi", 3)

        ampere = us.create_base_unit(0, "Ampere", "A", register=True)
        meter = us.create_base_unit(1, "Meter", "m", register=True)
        second = us.create_base_unit(2, "Second", "s", register=True)
        kilo = us.create_prefix(1000, "Kilo", "k")
        milli = us.create_prefix(0.001, "Milli", "m")

        parsed = us.parse_unit("m")

        self.assertEqual(repr(parsed), "<Unit Meter: 1 m = 1 m>")

    def test_parse_unit_unit_system(self):
        """
        Check that the parsed unit has the correct unit system.
        """
        us = UnitSystem("systeme-a-moi", 3)

        ampere = us.create_base_unit(0, "Ampere", "A", register=True)
        meter = us.create_base_unit(1, "Meter", "m", register=True)
        second = us.create_base_unit(2, "Second", "s", register=True)
        kilo = us.create_prefix(1000, "Kilo", "k")
        milli = us.create_prefix(0.001, "Milli", "m")

        parsed = us.parse_unit("m")

        self.assertIs(parsed.unit_system(), us)

    def test_parse_unit_with_prefix(self):
        """
        Test that a unit is parsed when the unit is prefixed.
        """
        us = UnitSystem("systeme-a-moi", 3)

        ampere = us.create_base_unit(0, "Ampere", "A", register=True)
        meter = us.create_base_unit(1, "Meter", "m", register=True)
        second = us.create_base_unit(2, "Second", "s", register=True)
        kilo = us.create_prefix(1000, "Kilo", "k")
        milli = us.create_prefix(0.001, "Milli", "m")

        parsed = us.parse_unit("km")
        self.assertEqual(repr(parsed), "<Unit KiloMeter: 1 km = 1000 m>")

        parsed = us.parse_unit("ms")
        self.assertEqual(repr(parsed), "<Unit MilliSecond: 1 ms = 0.001 s>")

    def test_parse_unit_unknown_unit(self):
        """
        Check that an exception is raised when the unit is not found.
        """
        us = UnitSystem("systeme-a-moi", 3)

        ampere = us.create_base_unit(0, "Ampere", "A", register=True)
        meter = us.create_base_unit(1, "Meter", "m", register=True)
        second = us.create_base_unit(2, "Second", "s", register=True)
        kilo = us.create_prefix(1000, "Kilo", "k")
        milli = us.create_prefix(0.001, "Milli", "m")

        self.assertRaises(pyveu.UnitNotFound, us.parse_unit, "V")

    def test_parse_unit_unknown_prefixed(self):
        """
        Check that an exception is raised when the prefixed unit is not found.
        """
        us = UnitSystem("systeme-a-moi", 3)

        ampere = us.create_base_unit(0, "Ampere", "A", register=True)
        meter = us.create_base_unit(1, "Meter", "m", register=True)
        second = us.create_base_unit(2, "Second", "s", register=True)
        kilo = us.create_prefix(1000, "Kilo", "k")

        self.assertRaises(pyveu.UnitNotFound, us.parse_unit, "mA")

    def test_parse_unit_unit_starts_with_prefix(self):
        """
        Check that parsing works when the unit starts with a prefix.
        """
        us = UnitSystem("systeme-a-moi", 3)

        ampere = us.create_base_unit(0, "Ampere", "A", register=True)
        meter = us.create_base_unit(1, "Meter", "met", register=True)
        second = us.create_base_unit(2, "Second", "s", register=True)
        kilo = us.create_prefix(1000, "Kilo", "k")
        milli = us.create_prefix(0.001, "Milli", "m")

        parsed = us.parse_unit("met")
        self.assertEqual(repr(parsed), "<Unit Meter: 1 met = 1 met>")
