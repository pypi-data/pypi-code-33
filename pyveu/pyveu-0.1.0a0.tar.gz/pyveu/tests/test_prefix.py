
# Copyright (C) 2018-19 Frank Sauerburger

import unittest
import mock

import pyveu
from pyveu import Named, SystemAffiliatedMixin, Prefix

class Unknown(object):
    """
    This helper class is used to check that arithmetic operations return
    NotImplemented if they operate on a unknown object.
    """
    pass


class PrefixTest(unittest.TestCase):
    """
    This class implements test cases for the prefix class.
    """

    def test_init_store(self):
        """
        Check that all the values passed to the constructor are saved
        internally.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        self.assertEqual(micro._factor, 1e-6)
        self.assertEqual(micro._label, "Micro")
        self.assertEqual(micro._symbol, "u")
        self.assertEqual(micro._latex, r"\mu")
        self.assertEqual(micro._unit_system, "systeme-international")

    def test_init_type(self):
        """
        Check that a prefix inherits from Named and ModifiableNamedMixin.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        self.assertIsInstance(micro, Prefix)
        self.assertIsInstance(micro, Named)
        self.assertIsInstance(micro, SystemAffiliatedMixin)

    def test_get_factor(self):
        """
        Check that factor() returns the internal factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        self.assertEqual(micro.factor(), 1e-6)

    def test_repr_named(self):
        """
        Check the representation of a named prefix. The presentation should
        contain the label, symbol and factor.
        """

        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        self.assertEqual(repr(micro), "<Prefix Micro: u = 1e-06>")

    def test_repr_named_decimal(self):
        """
        Check the representation of a named prefix. The presentation should
        contain the label, symbol and factor. The factor should be displayed
        as a decimal, if it is close to 1.
        """

        som = "systeme-a-moi"  # use a simple string for now
        pi = Prefix(3.14, "Pie", "pi", r"\pi", som)

        self.assertEqual(repr(pi), "<Prefix Pie: pi = 3.14>")

    def test_repr_no_label(self):
        """
        If a label is None but symbol is non-None, the label should be
        omitted in the representation.
        """

        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, None, "u", r"\mu", si)

        self.assertEqual(repr(micro), "<Prefix: u = 1e-06>")

    def test_repr_no_symbol(self):
        """
        If a label is None but symbol is non-None, the label should be
        omitted in the representation.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", None, r"\mu", si)

        self.assertEqual(repr(micro), "<Prefix Micro: 1e-06>")

    def test_repr_anonymous(self):
        """
        If the prefix is anonymous (even if it has a latex symbol) the string
        representation should only contain the factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, None,  None, r"\mu", si)

        self.assertEqual(repr(micro), "<Prefix: 1e-06>")

        micro = Prefix(1e-6, None,  None, None, si)

        self.assertEqual(repr(micro), "<Prefix: 1e-06>")

    ############################################################
    # Multiplication 
    def test_mul_number_return_type(self):
        """
        Check that multiplying a prefix with a scalar returns a simple number.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = micro * 1e-3

        self.assertIsInstance(nano, float)

    def test_mul_float(self):
        """
        Check that multiplying a prefix with a float returns the scaled factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = micro * 1e-3
        self.assertEqual(nano, 1e-9)
        
    def test_mul_int(self):
        """
        Check that multiplying a prefix with a float returns the scaled factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        milli = micro * 1000
        self.assertEqual(milli, 1e-3)

    def test_mul_Prefix(self):
        """
        Check that multiplying a prefix with another Prefix returns the
        multiplied factors.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        milli = micro * kilo
        self.assertEqual(milli, 1e-3)

    def test_mul_Prefix_return_type(self):
        """
        Check that multiplying a prefix with another Prefix returns a simple
        number.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        milli = micro * kilo
        self.assertIsInstance(milli, float)

    def test_mul_Prefix_diff_us(self):
        """
        Check that multiplying a prefix with a Prefix assigned to a
        different unit system fails.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, "other")

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a * b,
                          micro, kilo)

    def test_mul_long(self):
        """
        Check that multiplication works with Python 2 long integers.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        try:
            huge = kilo * 1000000000000000000000
        except TypeError:
            self.fail("Multiplication of a Prefix with a long int failed.")

    def test_mul_unknown(self):
        """
        Check that multiplication with an unknown class returns
        NotImplemented.
        """

        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a * b, micro, unknown)

    ############################################################
    # Right-multiplication
    def test_rmul_number_new(self):
        """
        Check that right-multiplying a prefix with a scalar creates a new prefix.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = 1e-3 * micro
        self.assertIsNot(micro, nano)

    def test_rmul_number_return_type(self):
        """
        Check that right-multiplying a prefix with a scalar creates a new prefix.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = 1e-3 * micro
        self.assertIsInstance(nano, Prefix)

    def test_rmul_number_us(self):
        """
        Check that right-multiplying a prefix with a scalar propagates the unit
        system.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = 1e-3 * micro
        self.assertEqual(nano.unit_system(), si)
        
    def test_rmul_float(self):
        """
        Check that right-multiplying a prefix with a float scales the factor.
        The scaled prefix should be anonymous.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = 1e-3 * micro
        self.assertEqual(repr(nano), "<Prefix: 1e-09>")
        
    def test_rmul_int(self):
        """
        Check that right-multiplying a prefix with an integer scales the
        factor. The scaled prefix should be anonymous.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        milli = 1000 * micro
        self.assertEqual(repr(milli), "<Prefix: 0.001>")

    def test_rmul_Prefix(self):
        """
        Check that right-multiplying a prefix with another Prefix returns the
        product of the factors as a number.

        This operation occurs when the right operand is an object of a sub
        class.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        milli = kilo.__rmul__(micro)
        self.assertEqual(milli, 1e-3)

    def test_rmul_Prefix_return_type(self):
        """
        Check that right-multiplying a prefix with another Prefix returns a
        number.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        milli = kilo.__rmul__(micro)
        self.assertIsInstance(milli, float)

    def test_rmul_Prefix_diff_us(self):
        """
        Check that right-multiplying a prefix with a Prefix assigned to a
        different unit system fails.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, "other")

        self.assertRaises(pyveu.DifferentUnitSystem,
                          lambda a, b: b.__rmul__(a),
                          micro, kilo)

    def test_rmul_unknown(self):
        """
        Check that right-multiplication with an unknown class returns
        NotImplemented.
        """

        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a * b, unknown, micro)


    def test_rmul_long(self):
        """
        Check that right-multiplication works with Python 2 long integers.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        try:
            huge = 1000000000000000000000 * kilo
        except TypeError:
            self.fail("Right-multiplication of a Prefix with a long int failed.")
        
    ############################################################
    # Division
    def test_div_number_return_type(self):
        """
        Check that dividing a prefix by a scalar returns a scalar.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = micro / 1000

        self.assertIsInstance(nano, float)

    def test_div_float(self):
        """
        Check that dividing a prefix by a float scales the factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        milli = micro / 1e-3
        self.assertEqual(milli, 1e-3)
        
    def test_div_int(self):
        """
        Check that dividing a prefix by an integer scales the factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = micro / 1000
        self.assertAlmostEqual(nano, 1e-9)

    def test_div_Prefix(self):
        """
        Check that dividing a prefix with another Prefix scales the factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        nano = micro / kilo
        self.assertAlmostEqual(nano, 1e-9)

    def test_div_Prefix_return_type(self):
        """
        Check that dividing a prefix by another Prefix returns a scalar.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        nano = micro / kilo
        self.assertIsInstance(nano, float)

    def test_div_Prefix_diff_us(self):
        """
        Check that dividing a prefix by a Prefix assigned to another unit
        system fails.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, "other")

        self.assertRaises(pyveu.DifferentUnitSystem, lambda a, b: a / b,
                          micro, kilo)

    def test_div_unknown(self):
        """
        Check that dividing by an unknown class returns
        NotImplemented.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a * b, micro, unknown)

    def test_div_long(self):
        """
        Check that division works with Python 2 long integers.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        try:
            tiny = kilo / 1000000000000000000000
        except TypeError:
            self.fail("Division of a Prefix by a long int failed.")

    ############################################################
    # True division / Python 2 division compatibility
    def test_trudiv_py2(self):
        """
        Check that dividing an integer Prefix performs a true-division.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        milli = kilo.__div__(1000000)

        self.assertEqual(milli, 1e-3)

    ############################################################
    # Right-division
    def test_rdiv_number_return_type(self):
        """
        Check that right-dividing a prefix with a scalar returns a scalar.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        nano = 1e-3 / micro

        self.assertIsInstance(nano, float)

    def test_rdiv_float(self):
        """
        Check that right-dividing a prefix with a float scales the factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        kilo = 1e-3 / micro
        self.assertAlmostEqual(kilo, 1000)
        
    def test_rdiv_int(self):
        """
        Check that right-dividing a prefix with an integer scales the
        factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        giga = 1000 / micro
        self.assertEqual(giga, 1e9)

    def test_rdiv_Prefix(self):
        """
        Check that right-dividing a prefix with another Prefix scales the
        factor.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        nano = kilo.__rtruediv__(micro)
        self.assertAlmostEqual(nano, 1e-9)

    def test_rdiv_Prefix_return_type(self):
        """
        Check that right-dividing a prefix with another Prefix returns a
        scalar.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, si)

        nano = kilo.__rtruediv__(micro)
        self.assertIsInstance(nano, float)

    def test_rdiv_Prefix_diff_us(self):
        """
        Check that right-dividing a prefix with a Prefix assigned to another
        unit system fails.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)
        kilo = Prefix(1000, "Kilo", "k", None, "other")

        self.assertRaises(pyveu.DifferentUnitSystem,
                          lambda a, b: b.__rtruediv__(a),
                          micro, kilo)

    def test_rdiv_unknown(self):
        """
        Check that right-dividing with an unknown class returns
        NotImplemented.
        """
        si = "systeme-international"  # use a simple string for now
        micro = Prefix(1e-6, "Micro", "u", r"\mu", si)

        unknown = Unknown()

        self.assertRaises(TypeError, lambda a, b: a / b, unknown, micro)

    def test_rdiv_long(self):
        """
        Check that right-division works with Python 2 long integers.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        try:
            not_so_huge = 1000000000000000000000 / kilo
        except TypeError:
            self.fail("Right-division of a Prefix by a long int failed.")

    ############################################################
    # True right-division / Python 2 division compatibility
    def test_rtrudiv_py2(self):
        """
        Check that right-dividing an integer Prefix performs a true-division.
        """

        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000000, "Kilo", "k", None, si)

        milli = kilo.__rdiv__(1000)

        self.assertEqual(milli, 1e-3)

    ############################################################
    # Arithmetic history
    def test_history_init(self):
        """
        Check that the initial history is None.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        self.assertIsNone(kilo._history)

    def test_history_mul_storage_number(self):
        """
        Check that multiplying a prefix with a number stores this
        operation in the history.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        mega = 1000 * kilo
        self.assertEqual(repr(mega._history), "1000 * <Prefix Kilo: k = 1000>")

    def test_history_mul_product(self):
        """
        Check that multiplying a scaled prefix with a number appends the number
        to the product.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        mega = 1000 * kilo
        answer = 42 * mega
        self.assertEqual(repr(answer._history), "42 * 1000 * <Prefix Kilo: k = 1000>")

    ############################################################
    # String representation
    def test_history_str(self):
        """
        Check that history_str() calls str() on the history object.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        mega = 1000 * kilo
        self.assertEqual(mega.history_str(),
                         "1000 * 1000")

        mega._history.str = mock.MagicMock()
        mega.history_str()
        mega._history.str.assert_called_once_with(latex=False)

    def test_history_str_none(self):
        """
        Check that history_str() returns None, if the history is None.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        self.assertIsNone(kilo.history_str())

    def test_history_str_latex(self):
        """
        Check that history_str() calls str() on the history object when
        latex=True.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        mega = 1000 * kilo
        self.assertEqual(mega.history_str(latex=True),
                         "1000 1000")

        mega._history.str = mock.MagicMock()
        mega.history_str(latex=True)
        mega._history.str.assert_called_once_with(latex=True)

    def test_history_str_latex_none(self):
        """
        Check that history_str() returns None, if the history is None and
        latex=True.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        self.assertIsNone(kilo.history_str(latex=True))

    ############################################################
    # History sanity-checks

    def test_history_rmul_unnamed_wo_history(self):
        """
        Check that an exception is raised if self is unnamed and the history
        is None.
        """
        si = "systeme-international"  # use a simple string for now
        kilo = Prefix(1000, "Kilo", "k", None, si)

        some_prefix = 1000 * kilo
        some_prefix._history = None

        self.assertRaises(Exception, lambda a, b: a * b, 1000, some_prefix)
