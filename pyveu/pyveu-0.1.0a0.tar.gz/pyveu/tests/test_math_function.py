
# Copyright (C) 2019 Frank Sauerburger

from __future__ import division  # Compatibility with 2.7
import unittest
import mock
import math

import pyveu.si as si
from pyveu import Quantity, _generic_function, UncertaintyIllDefined
import pyveu

class GenericFunctionTestCase(unittest.TestCase):
    """
    Test the _generic_function method.
    """

    def test_return_type(self):
        """
        Check that the generic_function returns a quantity.
        """
        input = Quantity("13 +- 1 m")
        output = _generic_function(input,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertIsInstance(output, Quantity)


    def test_new(self):
        """
        Check that the generic_function returns a new quantity.
        """
        input = Quantity("13 +- 1 m")
        qid = input.qid()

        output = _generic_function(input,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertNotEqual(output.qid(), qid)

    def test_int(self):
        """
        Check that generic_function can be called with an int.
        """

        output = _generic_function(1,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output), "<Quantity: 42>")

    def test_float(self):
        """
        Check that generic_function can be called with an float.
        """
        output = _generic_function(3.14,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output), "<Quantity: 42>")

    def test_prefix(self):
        """
        Check that the generic_function can be called with a prefix.
        """
        output = _generic_function(si.kilo,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output), "<Quantity: 42>")

    def test_unit(self):
        """
        Check that the generic_function can be called with a unit.
        """
        output = _generic_function(si.metre,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output), "<Quantity: 42 m^(-1)>")

    def test_value(self):
        """
        Check that the value handler is called with the properties from the
        quantity. The returned quantity must have the value returned by
        the handler.
        """
        input = Quantity("13 +- 1 s")
        qid = input.qid()
        value_handler = mock.Mock(return_value=42)

        output = _generic_function(input,
                                   value_handler,
                                   lambda i, j: 12,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output),
                         "<Quantity: (42 +- 12) s^(-1) | depends=[%d]>" % qid)
        self.assertEqual(output._variances, {qid: 1})
        self.assertEqual(output._derivatives, {qid: 12})
        value_handler.assert_called_once_with(13)

    def test_derivatives(self):
        """
        Check that the the derivative handler is called with the properties
        from the quantity. The returned quantity must include the returned
        derivative.
        """
        input = Quantity("13 +- 1 s")
        qid = input.qid()
        d_dx_handler = mock.Mock(return_value=12)

        output = _generic_function(input,
                                   lambda i: 42,
                                   d_dx_handler,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output),
                         "<Quantity: (42 +- 12) s^(-1) | depends=[%d]>" % qid)
        self.assertEqual(output._variances, {qid: 1})
        self.assertEqual(output._variances, {qid: 1})
        self.assertEqual(output._derivatives, {qid: 12})
        d_dx_handler.assert_called_once_with(13, 1)

    def test_derivatives_no_error(self):
        """
        Check that the derivates handler is not called if the quantity has no
        error. 
        """
        input = Quantity("13 s")
        qid = input.qid()
        d_dx_handler = mock.Mock(return_value=12)

        output = _generic_function(input,
                                   lambda i: 42,
                                   d_dx_handler,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output), "<Quantity: 42 s^(-1)>")
        self.assertEqual(output._variances, {})
        self.assertEqual(output._derivatives, {})
        d_dx_handler.assert_not_called()

    def test_derivatives_ignore_zero_derivative(self):
        """
        Check that the dependency is dropped if the derivative handler returns
        zero.
        """
        input = Quantity("13 +- 1s")
        qid = input.qid()
        d_dx_handler = mock.Mock(return_value=0)

        output = _generic_function(input,
                                   lambda i: 42,
                                   d_dx_handler,
                                   lambda u, i, j: -u)

        self.assertEqual(repr(output), "<Quantity: 42 s^(-1)>")
        self.assertEqual(output._variances, {})
        self.assertEqual(output._derivatives, {})
        d_dx_handler.assert_called_once_with(13, 1)

    def test_unit_handler(self):
        """
        Check that the unit handler is called with the properties from the
        quantity. The returned quantity must have the returned unit vector.
        """
        input = Quantity("13 +- 1 s")
        qid = input.qid()
        unit_handler = mock.Mock(return_value=si.kilogram.unit_vector())

        output = _generic_function(input,
                                   lambda i: 42,
                                   lambda i, j: 12,
                                   unit_handler)

        self.assertEqual(repr(output),
                         "<Quantity: (42 +- 12) kg | depends=[%d]>" % qid)
        self.assertEqual(output._variances, {qid: 1})
        self.assertEqual(output._derivatives, {qid: 12})
        unit_handler.assert_called_once()
        args, kwds = unit_handler.call_args
        self.assertTrue( (args[0] == si.second.unit_vector()).all())
        self.assertEqual(args[1], 13)
        self.assertIs(args[2], si.unit_system)
        self.assertEqual(kwds, {})

    def test_dependent(self):
        """
        Test that calling _generic_function honors dependencies between
        quantities. As an example, the identity-handlers are used.
        """
        quantity_a = Quantity("13 +- 1 s")
        quantity_b = quantity_a * 10
        qid_a = quantity_a.qid()

        output = _generic_function(quantity_b,
                                   lambda i: i,
                                   lambda i, j: j,
                                   lambda i, j, k: i)

        self.assertEqual(repr(output),
                         "<Quantity: (130 +- 10) s | depends=[%d]>" % qid_a)
        self.assertEqual(output._variances, {qid_a: 1})
        self.assertEqual(output._derivatives, {qid_a: 10})

class ExpTestCase(unittest.TestCase):
    """
    Test the exp() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns exp() of the argument.
        """
        self.assertAlmostEqual(pyveu._exp_value_handler(0), 1)
        self.assertAlmostEqual(pyveu._exp_value_handler(1), math.exp(1))
        self.assertAlmostEqual(pyveu._exp_value_handler(12), math.exp(12))
        self.assertAlmostEqual(pyveu._exp_value_handler(-1), math.exp(-1))
        self.assertAlmostEqual(pyveu._exp_value_handler(-17), math.exp(-17))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._exp_d_dx_handler(0, 1), 1)
        self.assertAlmostEqual(pyveu._exp_d_dx_handler(0, 0), 0)
        self.assertAlmostEqual(pyveu._exp_d_dx_handler(1, 0), 0)
        self.assertAlmostEqual(pyveu._exp_d_dx_handler(-1, 12),
                               12 * math.exp(-1))
        self.assertAlmostEqual(pyveu._exp_d_dx_handler(3, -1), -1 * math.exp(3))
        self.assertAlmostEqual(pyveu._exp_d_dx_handler(-17, 100), 100 *math.exp(-17))

    def test_unit_handler_dimensionless(self):
        """
        Check that the unit handler returns an empty unit vector.
        """
        unity = si.metre.unit_vector() * 0

        self.assertTrue((pyveu._no_unit_handler(unity, -3, si.unit_system)
                         == unity).all())

        self.assertTrue((pyveu._no_unit_handler(unity, 0, si.unit_system)
                         == unity).all())



    def test_unit_handler_not_dimensionless(self):
        """
        Check that the unit handler raises an exception when the exponent is
        not dimensionless.
        """
        self.assertRaises(ValueError, pyveu._no_unit_handler,
                          si.metre.unit_vector(), 2, si.unit_system)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.03")
        qid = quantity.qid()

        power = pyveu.exp(quantity)

        self.assertEqual(repr(power),
                         "<Quantity: 5.47395 +- 0.164218 | depends=[%d]>" % qid)
        self.assertEqual(power._variances, {qid: 0.0009})
        self.assertEqual(power._derivatives, {qid: math.exp(1.7)})

class LogTestCase(unittest.TestCase):
    """
    Test the log() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns log() of the argument.
        """
        self.assertAlmostEqual(pyveu._log_value_handler(1), 0)
        self.assertAlmostEqual(pyveu._log_value_handler(1), math.log(1))
        self.assertAlmostEqual(pyveu._log_value_handler(12), math.log(12))

    def test_value_handler_negative(self):
        """
        Check that the value handler raises an exception if the argument is
        negative.
        """
        self.assertRaises(ValueError, pyveu._log_value_handler, -1)
        self.assertRaises(ValueError, pyveu._log_value_handler, -17)

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._log_d_dx_handler(0.1, 2), 20)
                               
        self.assertAlmostEqual(pyveu._log_d_dx_handler(1, 3), 3)
        self.assertAlmostEqual(pyveu._log_d_dx_handler(2, 0), 0)
        self.assertAlmostEqual(pyveu._log_d_dx_handler(2, -5), -2.5) 
        self.assertAlmostEqual(pyveu._log_d_dx_handler(17, 100), 100 / 17)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("17 +- 0.3")
        qid = quantity.qid()

        logarithm = pyveu.log(quantity)

        self.assertEqual(repr(logarithm),
                         "<Quantity: 2.83321 +- 0.0176471 | depends=[%d]>" % qid)
        self.assertEqual(logarithm._variances, {qid: 0.09})
        self.assertEqual(logarithm._derivatives, {qid: 1 / 17})

    def test_example_log_exp(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("-11 +- 0.3")
        qid = quantity.qid()

        same = pyveu.log(pyveu.exp(quantity))

        self.assertEqual(repr(same),
                         "<Quantity: -11 +- 0.3 | depends=[%d]>" % qid)
        self.assertEqual(same._variances, {qid: 0.09})
        self.assertEqual(same._derivatives, {qid: 1})

class Log2TestCase(unittest.TestCase):
    """
    Test the log2() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("17 +- 0.3")
        qid = quantity.qid()

        logarithm = pyveu.log2(quantity)

        self.assertEqual(repr(logarithm),
                         "<Quantity: 4.08746 +- 0.0254593 | depends=[%d]>" % qid)
        self.assertEqual(logarithm._variances, {qid: 0.09})
        self.assertAlmostEqual(logarithm._derivatives[qid], 
                               1 / 17 / math.log(2))

    def test_example_log_exp(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("-11 +- 0.3")
        qid = quantity.qid()

        same = pyveu.log2(2**quantity)

        self.assertEqual(repr(same),
                         "<Quantity: -11 +- 0.3 | depends=[%d]>" % qid)
        self.assertEqual(same._variances, {qid: 0.09})
        self.assertAlmostEqual(same._derivatives[qid], 1)

class Log10TestCase(unittest.TestCase):
    """
    Test the log10() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("100 +- 0.5")
        qid = quantity.qid()

        logarithm = pyveu.log10(quantity)

        self.assertEqual(repr(logarithm),
                         "<Quantity: 2 +- 0.00217147 | depends=[%d]>" % qid)
        self.assertEqual(logarithm._variances, {qid: 0.25})
        self.assertAlmostEqual(logarithm._derivatives[qid], 
                               0.01 / math.log(10))

    def test_example_log_exp(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("-11 +- 0.3")
        qid = quantity.qid()

        same = pyveu.log10(10**quantity)

        self.assertEqual(repr(same),
                         "<Quantity: -11 +- 0.3 | depends=[%d]>" % qid)
        self.assertEqual(same._variances, {qid: 0.09})
        self.assertAlmostEqual(same._derivatives[qid], 1)

class PowTestCase(unittest.TestCase):
    """
    Test the pow() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("4 +- 0.5")
        qid = quantity.qid()

        power = pyveu.pow(quantity, 3)

        self.assertEqual(repr(power),
                         "<Quantity: 64 +- 24 | depends=[%d]>" % qid)

class Sqrt(unittest.TestCase):
    """
    Test the pow() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("4 +- 0.1")
        qid = quantity.qid()

        root = pyveu.sqrt(quantity)

        self.assertEqual(repr(root),
                         "<Quantity: 2 +- 0.025 | depends=[%d]>" % qid)

class SinTestCase(unittest.TestCase):
    """
    Test the sin() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns sin() of the argument.
        """
        self.assertAlmostEqual(pyveu._sin_value_handler(0), 0)
        self.assertAlmostEqual(pyveu._sin_value_handler(1), math.sin(1))
        self.assertAlmostEqual(pyveu._sin_value_handler(2), math.sin(2))
        self.assertAlmostEqual(pyveu._sin_value_handler(-4), math.sin(-4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._sin_d_dx_handler(0, 2), 2)
        self.assertAlmostEqual(pyveu._sin_d_dx_handler(1, 3), 3 * math.cos(1))
        self.assertAlmostEqual(pyveu._sin_d_dx_handler(-2, 1), math.cos(-2))
        self.assertAlmostEqual(pyveu._sin_d_dx_handler(-4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        sine = pyveu.sin(quantity)

        self.assertEqual(repr(sine),
                         "<Quantity: 0.991665 +- 0.0128844 | depends=[%d]>" % qid)
        self.assertEqual(len(sine._variances), 1)
        self.assertAlmostEqual(sine._variances[qid], 0.01)
        self.assertAlmostEqual(sine._derivatives[qid], math.cos(1.7))

class CosTestCase(unittest.TestCase):
    """
    Test the cos() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns cos() of the argument.
        """
        self.assertAlmostEqual(pyveu._cos_value_handler(0), 1)
        self.assertAlmostEqual(pyveu._cos_value_handler(1), math.cos(1))
        self.assertAlmostEqual(pyveu._cos_value_handler(2), math.cos(2))
        self.assertAlmostEqual(pyveu._cos_value_handler(-4), math.cos(-4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._cos_d_dx_handler(0, 2), 0)
        self.assertAlmostEqual(pyveu._cos_d_dx_handler(1, 3), -3 * math.sin(1))
        self.assertAlmostEqual(pyveu._cos_d_dx_handler(-2, 1), math.sin(2))
        self.assertAlmostEqual(pyveu._cos_d_dx_handler(-4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        cosine = pyveu.cos(quantity)

        self.assertEqual(repr(cosine),
                         "<Quantity: -0.128844 +- 0.0991665 | depends=[%d]>" % qid)
        self.assertEqual(len(cosine._variances), 1)
        self.assertAlmostEqual(cosine._variances[qid], 0.01)
        self.assertAlmostEqual(cosine._derivatives[qid], -math.sin(1.7))

class TanTestCase(unittest.TestCase):
    """
    Test the tan() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1 +- 0.1")
        qid = quantity.qid()

        tangent = pyveu.tan(quantity)

        self.assertEqual(repr(tangent),
                         "<Quantity: 1.55741 +- 0.342552 | depends=[%d]>" % qid)
        self.assertEqual(len(tangent._variances), 1)
        self.assertAlmostEqual(tangent._variances[qid], 0.01)
        self.assertAlmostEqual(tangent._derivatives[qid], 1 / math.cos(1)**2)

class SinhTestCase(unittest.TestCase):
    """
    Test the sinh() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns sinh() of the argument.
        """
        self.assertAlmostEqual(pyveu._sinh_value_handler(0), 0)
        self.assertAlmostEqual(pyveu._sinh_value_handler(1), math.sinh(1))
        self.assertAlmostEqual(pyveu._sinh_value_handler(2), math.sinh(2))
        self.assertAlmostEqual(pyveu._sinh_value_handler(-4), math.sinh(-4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._sinh_d_dx_handler(0, 2), 2)
        self.assertAlmostEqual(pyveu._sinh_d_dx_handler(1, 3), 3 * math.cosh(1))
        self.assertAlmostEqual(pyveu._sinh_d_dx_handler(-2, 1), math.cosh(-2))
        self.assertAlmostEqual(pyveu._sinh_d_dx_handler(-4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        sine = pyveu.sinh(quantity)

        self.assertEqual(repr(sine),
                         "<Quantity: 2.64563 +- 0.282832 | depends=[%d]>" % qid)
        self.assertEqual(len(sine._variances), 1)
        self.assertAlmostEqual(sine._variances[qid], 0.01)
        self.assertAlmostEqual(sine._derivatives[qid], math.cosh(1.7))

class CoshTestCase(unittest.TestCase):
    """
    Test the cosh() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns cosh() of the argument.
        """
        self.assertAlmostEqual(pyveu._cosh_value_handler(0), 1)
        self.assertAlmostEqual(pyveu._cosh_value_handler(1), math.cosh(1))
        self.assertAlmostEqual(pyveu._cosh_value_handler(2), math.cosh(2))
        self.assertAlmostEqual(pyveu._cosh_value_handler(-4), math.cosh(-4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._cosh_d_dx_handler(0, 2), 0)
        self.assertAlmostEqual(pyveu._cosh_d_dx_handler(1, 3), 3 * math.sinh(1))
        self.assertAlmostEqual(pyveu._cosh_d_dx_handler(-2, 1), math.sinh(-2))
        self.assertAlmostEqual(pyveu._cosh_d_dx_handler(-4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        cosine = pyveu.cosh(quantity)

        self.assertEqual(repr(cosine),
                         "<Quantity: 2.82832 +- 0.264563 | depends=[%d]>" % qid)
        self.assertEqual(len(cosine._variances), 1)
        self.assertAlmostEqual(cosine._variances[qid], 0.01)
        self.assertAlmostEqual(cosine._derivatives[qid], math.sinh(1.7))

class TanhTestCase(unittest.TestCase):
    """
    Test the tanh() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        tangent = pyveu.tanh(quantity)

        self.assertEqual(repr(tangent),
                         "<Quantity: 0.935409 +- 0.012501 | depends=[%d]>" % qid)
        self.assertEqual(len(tangent._variances), 1)
        self.assertAlmostEqual(tangent._variances[qid], 0.01)
        self.assertAlmostEqual(tangent._derivatives[qid],
                               1 - math.tanh(1.7)**2)

class AsinTestCase(unittest.TestCase):
    """
    Test the asin() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns asin() of the argument.
        """
        self.assertAlmostEqual(pyveu._asin_value_handler(0), 0)
        self.assertAlmostEqual(pyveu._asin_value_handler(0.1), math.asin(0.1))
        self.assertAlmostEqual(pyveu._asin_value_handler(0.2), math.asin(0.2))
        self.assertAlmostEqual(pyveu._asin_value_handler(-0.4), math.asin(-0.4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._asin_d_dx_handler(0, 2), 2)
        self.assertAlmostEqual(pyveu._asin_d_dx_handler(0.1, 3),
                               3 / math.sqrt(1 - 0.01))
        self.assertAlmostEqual(pyveu._asin_d_dx_handler(-0.2, 1),
                               1 / math.sqrt(1 - 0.04))
        self.assertAlmostEqual(pyveu._asin_d_dx_handler(-0.4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("0.6 +- 0.01")
        qid = quantity.qid()

        sine = pyveu.asin(quantity)

        self.assertEqual(repr(sine),
                         "<Quantity: 0.643501 +- 0.0125 | depends=[%d]>" % qid)
        self.assertEqual(len(sine._variances), 1)
        self.assertAlmostEqual(sine._variances[qid], 0.0001)
        self.assertAlmostEqual(sine._derivatives[qid],
                               1 / math.sqrt(1 - 0.6**2))

class AcosTestCase(unittest.TestCase):
    """
    Test the acos() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns acos() of the argument.
        """
        self.assertAlmostEqual(pyveu._acos_value_handler(0), math.acos(0))
        self.assertAlmostEqual(pyveu._acos_value_handler(0.1), math.acos(0.1))
        self.assertAlmostEqual(pyveu._acos_value_handler(0.2), math.acos(0.2))
        self.assertAlmostEqual(pyveu._acos_value_handler(-0.4), math.acos(-0.4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._acos_d_dx_handler(0, 2), -2)
        self.assertAlmostEqual(pyveu._acos_d_dx_handler(0.1, 3),
                               -3 / math.sqrt(1 - 0.01))
        self.assertAlmostEqual(pyveu._acos_d_dx_handler(-0.2, 1),
                               -1 / math.sqrt(1 - 0.04))
        self.assertAlmostEqual(pyveu._acos_d_dx_handler(-0.4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("0.6 +- 0.01")
        qid = quantity.qid()

        cosine = pyveu.acos(quantity)

        self.assertEqual(repr(cosine),
                         "<Quantity: 0.927295 +- 0.0125 | depends=[%d]>" % qid)
        self.assertEqual(len(cosine._variances), 1)
        self.assertAlmostEqual(cosine._variances[qid], 0.0001)
        self.assertAlmostEqual(cosine._derivatives[qid],
                               -1 / math.sqrt(1 - 0.6**2))

class Atan(unittest.TestCase):
    """
    Test the atan() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns atan() of the argument.
        """
        self.assertAlmostEqual(pyveu._atan_value_handler(0), math.atan(0))
        self.assertAlmostEqual(pyveu._atan_value_handler(0.1), math.atan(0.1))
        self.assertAlmostEqual(pyveu._atan_value_handler(0.2), math.atan(0.2))
        self.assertAlmostEqual(pyveu._atan_value_handler(-0.4), math.atan(-0.4))

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._atan_d_dx_handler(0, 2), 2)
        self.assertAlmostEqual(pyveu._atan_d_dx_handler(0.1, 3),
                               3 / (1 + 0.01))
        self.assertAlmostEqual(pyveu._atan_d_dx_handler(-0.2, 1),
                               1 / (1 + 0.04))
        self.assertAlmostEqual(pyveu._atan_d_dx_handler(-0.4, 0), 0)

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("0.6 +- 0.01")
        qid = quantity.qid()

        tangent = pyveu.atan(quantity)

        self.assertEqual(repr(tangent),
                         "<Quantity: 0.54042 +- 0.00735294 | depends=[%d]>" % qid)
        self.assertEqual(len(tangent._variances), 1)
        self.assertAlmostEqual(tangent._variances[qid], 0.0001)
        self.assertAlmostEqual(tangent._derivatives[qid],
                               1 / (1 + 0.6**2))

class Asinh(unittest.TestCase):
    """
    Test the asinh() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        inverse = pyveu.asinh(quantity)

        self.assertEqual(repr(inverse),
                         "<Quantity: 1.30082 +- 0.050702 | depends=[%d]>" % qid)
        self.assertEqual(len(inverse._variances), 1)
        self.assertAlmostEqual(inverse._variances[qid], 0.01)
        self.assertAlmostEqual(inverse._derivatives[qid],
                               1 / math.sqrt(1.7**2 + 1))

class Acosh(unittest.TestCase):
    """
    Test the acosh() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("1.7 +- 0.1")
        qid = quantity.qid()

        inverse = pyveu.acosh(quantity)

        self.assertEqual(repr(inverse),
                         "<Quantity: 1.12323 +- 0.0727393 | depends=[%d]>" % qid)
        self.assertEqual(len(inverse._variances), 1)
        self.assertAlmostEqual(inverse._variances[qid], 0.01)
        self.assertAlmostEqual(inverse._derivatives[qid],
                               1 / math.sqrt(1.7**2 - 1))

class Atanh(unittest.TestCase):
    """
    Test the atanh() implementation.
    """
    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("0.7 +- 0.1")
        qid = quantity.qid()

        inverse = pyveu.atanh(quantity)

        self.assertEqual(repr(inverse),
                         "<Quantity: 0.867301 +- 0.196078 | depends=[%d]>" % qid)
        self.assertEqual(len(inverse._variances), 1)
        self.assertAlmostEqual(inverse._variances[qid], 0.01)
        self.assertAlmostEqual(inverse._derivatives[qid],
                               1 / (1 - 0.7**2))

class AbsTestCase(unittest.TestCase):
    """
    Test the abs() implementation.
    """

    def test_value_handler(self):
        """
        Check that the value handler returns abs() of the argument.
        """
        self.assertAlmostEqual(pyveu._abs_value_handler(0), 0)
        self.assertAlmostEqual(pyveu._abs_value_handler(+1), 1)
        self.assertAlmostEqual(pyveu._abs_value_handler(-12), 12)

    def test_derivative_handler(self):
        """
        Check that the derivative handler returns the chained derivative.
        """
        self.assertAlmostEqual(pyveu._abs_d_dx_handler(1, 0), 0)
        self.assertAlmostEqual(pyveu._abs_d_dx_handler(-1, 12), -12)
        self.assertAlmostEqual(pyveu._abs_d_dx_handler(3, -1), -1)
        self.assertAlmostEqual(pyveu._abs_d_dx_handler(17, 100), 100)

    def test_derivative_handler_zero(self):
        """
        Check that the derivative handler raises an exception if the value is
        zero.
        """
        self.assertRaises(UncertaintyIllDefined, pyveu._abs_d_dx_handler, 0, 1)
        self.assertRaises(UncertaintyIllDefined, pyveu._abs_d_dx_handler, 0, 0)

    def test_unit_handler(self):
        """
        Check that the unit handler returns the same unit_vector.
        """
        unit_vector = si.metre.unit_vector() - si.kilogram.unit_vector()

        abs_unit_vector = pyveu._abs_unit_handler(unit_vector, -3, si.unit_system)
        self.assertTrue((abs_unit_vector == unit_vector).all())

    def test_example(self):
        """
        Check that an example quantity is calculated correctly.
        """
        quantity = Quantity("-1.7 +- 0.03")
        qid = quantity.qid()

        absolute_value = pyveu.abs(quantity)

        self.assertEqual(repr(absolute_value),
                         "<Quantity: 1.7 +- 0.03 | depends=[%d]>" % qid)
        self.assertEqual(absolute_value._variances, {qid: 0.0009})
        self.assertEqual(absolute_value._derivatives, {qid: -1})
