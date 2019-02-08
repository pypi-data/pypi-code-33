
# Copyright (C) 2018 Frank Sauerburger

import unittest
import mock

from pyveu import _Arithmetic, _Product, _Fraction, _Power, UnitSystem

class ArithmeticTestCase(unittest.TestCase):
    """
    Test the implementation of the arithmetic history storage classes.
    """

    def test_inheritance(self):
        """
        Check that _Product, _Product and _Power inherit from _Arithmetic.
        """
        self.assertTrue(issubclass(_Product, _Arithmetic))
        self.assertTrue(issubclass(_Fraction, _Arithmetic))
        self.assertTrue(issubclass(_Power, _Arithmetic))

    def test_storage_product(self):
        """
        Check that the product class stores all objects given to the
        constructor.
        """
        product = _Product(42, "pi", 3.14)
        self.assertEqual(len(product.factors), 3)
        self.assertEqual(product.factors[0], 42)
        self.assertEqual(product.factors[1], "pi")
        self.assertEqual(product.factors[2], 3.14)

    def test_storage_zero_factors(self):
        """
        Check that the product class raises an exception if no factor is
        given.
        """
        self.assertRaises(TypeError, _Product)

    def test_storage_one_factors(self):
        """
        Check that the product class raises an exception if only one factor is
        given.
        """
        self.assertRaises(TypeError, _Product, 2)

    def test_storage_num_factors_modify(self):
        """
        Check that the product class raises an exception if only one/zero
        factors are set and str() is called.
        """
        product = _Product(2, 3)
        product.factors = [1]
        self.assertRaises(ValueError, str, product)

    def test_storage_fraction(self):
        """
        Check that the fraction class stores the numerator and denominator
        object passed to the constructor.
        """
        fraction = _Fraction(180, "pi")
        self.assertEqual(fraction.numerator, 180)
        self.assertEqual(fraction.denominator, "pi")

        fraction = _Fraction(numerator=180, denominator="pi")
        self.assertEqual(fraction.numerator, 180)
        self.assertEqual(fraction.denominator, "pi")

    def test_storage_power(self):
        """
        Check that the power class stores the base and exponent objects passed
        to the constructor.
        """
        power = _Power("e", -1)
        self.assertEqual(power.base, "e")
        self.assertEqual(power.exponent, -1)

        power = _Power(base=2, exponent=64)
        self.assertEqual(power.base, 2)
        self.assertEqual(power.exponent, 64)

    def test_fraction_zero_element(self):
        """
        Check that creating a fraction with zero factors raises an error.
        """
        self.assertRaises(TypeError, _Fraction)

    def test_fraction_one_element(self):
        """
        Check that creating a fraction with one factors raises an error.
        """
        self.assertRaises(TypeError, _Fraction, 1)

    def test_modify_product(self):
        """
        Check that product objects provide write modify via the factor
        property.
        """
        product = _Product(42, "pi", 3.14)
        self.assertEqual(len(product.factors), 3)
        self.assertEqual(product.factors[0], 42)
        self.assertEqual(product.factors[1], "pi")
        self.assertEqual(product.factors[2], 3.14)

        product.factors.append(0)
        product.factors[0] *= 2

        self.assertEqual(len(product.factors), 4)
        self.assertEqual(product.factors[0], 84)
        self.assertEqual(product.factors[1], "pi")
        self.assertEqual(product.factors[2], 3.14)
        self.assertEqual(product.factors[3], 0)

    def test_modify_fraction(self):
        """
        Check that fraction objects provide write modify via the
        numerator and denominator properties.
        """
        fraction = _Fraction(180, "pi")
        self.assertEqual(fraction.numerator, 180)
        self.assertEqual(fraction.denominator, "pi")

        fraction.numerator = 2
        fraction.denominator = 3

        self.assertEqual(fraction.numerator, 2)
        self.assertEqual(fraction.denominator, 3)

    def test_modify_power(self):
        """
        Check that power objects provide write modify via the base and
        exponent properties.
        """
        power = _Power("e", -1)
        self.assertEqual(power.base, "e")
        self.assertEqual(power.exponent, -1)

        power.base = 2
        power.exponent = 32

        self.assertEqual(power.base, 2)
        self.assertEqual(power.exponent, 32)

    def test_str_product(self):
        """
        Check that the representation of product calls all str() on all its
        factors.
        """
        product = _Product("e", 3.14, self)
        self.assertEqual(product.str(), "e * 3.14 * %s" % str(self))

    def test_str_zero_element(self):
        """
        Check str() raises an exception is raised if there is no factor in
        the product.
        """
        product = _Product("e", 3.14, self)
        product.factors = []
        self.assertRaises(ValueError, lambda x: x.str(), product)

    def test_str_one_element(self):
        """
        Check str() raises an exception is raised if there is one factor in
        the product.
        """
        product = _Product("e", 3.14, self)
        product.factors = [1]
        self.assertRaises(ValueError, lambda x: x.str(), product)

    def test_str_fraction(self):
        """
        Check that the representation of product calls all str() on the
        numerator and denominator.
        """
        fraction = _Fraction(5, self)
        self.assertEqual(fraction.str(), "5 / %s" % str(self))

    def test_str_power(self):
        """
        Check that the representation of power calls all str() on the base
        and exponent.
        """
        power = _Power(self, 3.14)
        self.assertEqual(power.str(), "%s^3.14" % str(self))

    def test_str_product_in_product(self):
        """
        Check that str(product) does not add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(product.str(), "42 * 3.14 * 37 * 0.21")

    def test_str_product_in_fraction(self):
        """
        Check that str(fraction) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(fraction.str(), "42 / (3.14 * 37)")

        fraction = _Fraction(inner, 42)
        self.assertEqual(fraction.str(), "3.14 * 37 / 42")

        fraction = _Fraction(inner, inner)
        self.assertEqual(fraction.str(), "3.14 * 37 / (3.14 * 37)")

    def test_str_product_in_power(self):
        """
        Check that str(power) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(power.str(), "42^(3.14 * 37)")

        power = _Power(inner, 42)
        self.assertEqual(power.str(), "(3.14 * 37)^42")

        power = _Power(inner, inner)
        self.assertEqual(power.str(), "(3.14 * 37)^(3.14 * 37)")
        
    def test_str_fraction_in_product(self):
        """
        Check that str(product) does add parenthesis for sub fractions.
        """
        inner = _Fraction(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(product.str(), "42 * 3.14 / 37 * 0.21")

    def test_str_fraction_in_fraction(self):
        """
        Check that str(fraction) does add parenthesis for sub fraction.
        """
        inner = _Fraction(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(fraction.str(), "42 / (3.14 / 37)")

        fraction = _Fraction(inner, 42)
        self.assertEqual(fraction.str(), "3.14 / 37 / 42")

        fraction = _Fraction(inner, inner)
        self.assertEqual(fraction.str(), "3.14 / 37 / (3.14 / 37)")

    def test_str_fraction_in_power(self):
        """
        Check that str(power) does add parenthesis for sub fractions.
        """
        inner = _Fraction(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(power.str(), "42^(3.14 / 37)")

        power = _Power(inner, 42)
        self.assertEqual(power.str(), "(3.14 / 37)^42")

        power = _Power(inner, inner)
        self.assertEqual(power.str(), "(3.14 / 37)^(3.14 / 37)")
        
    def test_str_power_in_product(self):
        """
        Check that str(product) does not add parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(product.str(), "42 * 3.14^37 * 0.21")

    def test_str_power_in_fraction(self):
        """
        Check that str(fraction) does not add parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(fraction.str(), "42 / 3.14^37")

        fraction = _Fraction(inner, 42)
        self.assertEqual(fraction.str(), "3.14^37 / 42")

        fraction = _Fraction(inner, inner)
        self.assertEqual(fraction.str(), "3.14^37 / 3.14^37")

    def test_str_power_in_power(self):
        """
        Check that str(power) does add parenthesis for sub powers when
        necessary.
        """
        inner = _Power(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(power.str(), "42^3.14^37")

        power = _Power(inner, 42)
        self.assertEqual(power.str(), "(3.14^37)^42")

        power = _Power(inner, inner)
        self.assertEqual(power.str(), "(3.14^37)^3.14^37")

    def test_str_latex_product(self):
        """
        Check that the representation of product calls all str() on all its
        factors.
        """
        product = _Product("e", 3.14, self)
        self.assertEqual(product.str(latex=True), "e 3.14 %s" % str(self))

    def test_str_latex_zero_element(self):
        """
        Check str() raises an exception is raised if there is no factor in
        the product.
        """
        product = _Product("e", 3.14, self)
        product.factors = []
        self.assertRaises(ValueError, lambda x: x.str(latex=True), product)

    def test_str_latex_one_element(self):
        """
        Check str() raises an exception is raised if there is one factor in
        the product.
        """
        product = _Product("e", 3.14, self)
        product.factors = [1]
        self.assertRaises(ValueError, lambda x: x.str(latex=True), product)

    def test_str_latex_fraction(self):
        """
        Check that the representation of product calls all str() on the
        numerator and denominator.
        """
        fraction = _Fraction(5, self)
        self.assertEqual(fraction.str(latex=True), r"\frac{5}{%s}" % str(self))

    def test_str_latex_power(self):
        """
        Check that the representation of power calls all str() on the base
        and exponent.
        """
        power = _Power(self, 3.14)
        self.assertEqual(power.str(latex=True), "%s^{3.14}" % str(self))

    def test_str_latex_product_in_product(self):
        """
        Check that str(product) does not add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(product.str(True), "42 3.14 37 0.21")

    def test_str_latex_product_in_fraction(self):
        """
        Check that str(fraction) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(fraction.str(True), r"\frac{42}{3.14 37}")

        fraction = _Fraction(inner, 42)
        self.assertEqual(fraction.str(True), r"\frac{3.14 37}{42}")

        fraction = _Fraction(inner, inner)
        self.assertEqual(fraction.str(True), r"\frac{3.14 37}{3.14 37}")

    def test_str_latex_product_in_power(self):
        """
        Check that str(power) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(power.str(True), "42^{3.14 37}")

        power = _Power(inner, 42)
        self.assertEqual(power.str(True), r"\left(3.14 37\right)^{42}")

        power = _Power(inner, inner)
        self.assertEqual(power.str(True), r"\left(3.14 37\right)^{3.14 37}")
        
    def test_str_latex_fraction_in_product(self):
        """
        Check that str(product) does add parenthesis for sub fractions.
        """
        inner = _Fraction(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(product.str(True), r"42 \frac{3.14}{37} 0.21")

    def test_str_latex_fraction_in_fraction(self):
        """
        Check that str(fraction) does add parenthesis for sub fraction.
        """
        inner = _Fraction(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(fraction.str(True), r"\frac{42}{\frac{3.14}{37}}")

        fraction = _Fraction(inner, 42)
        self.assertEqual(fraction.str(True), r"\frac{\frac{3.14}{37}}{42}")

        fraction = _Fraction(inner, inner)
        self.assertEqual(fraction.str(True),
                         r"\frac{\frac{3.14}{37}}{\frac{3.14}{37}}")

    def test_str_latex_fraction_in_power(self):
        """
        Check that str(power) does add parenthesis for sub fractions.
        """
        inner = _Fraction(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(power.str(True), r"42^{\frac{3.14}{37}}")

        power = _Power(inner, 42)
        self.assertEqual(power.str(True), r"\left(\frac{3.14}{37}\right)^{42}")

        power = _Power(inner, inner)
        self.assertEqual(power.str(True),
                         r"\left(\frac{3.14}{37}\right)^{\frac{3.14}{37}}")
        
    def test_str_latex_power_in_product(self):
        """
        Check that str(product) does not add parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(product.str(True), "42 3.14^{37} 0.21")

    def test_str_latex_power_in_fraction(self):
        """
        Check that str(fraction) does not add parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(fraction.str(True), r"\frac{42}{3.14^{37}}")

        fraction = _Fraction(inner, 42)
        self.assertEqual(fraction.str(True), r"\frac{3.14^{37}}{42}")

        fraction = _Fraction(inner, inner)
        self.assertEqual(fraction.str(True), r"\frac{3.14^{37}}{3.14^{37}}")

    def test_str_latex_power_in_power(self):
        """
        Check that str(power) does add parenthesis for sub powers when
        necessary.
        """
        inner = _Power(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(power.str(True), "42^{3.14^{37}}")

        power = _Power(inner, 42)
        self.assertEqual(power.str(True), r"\left(3.14^{37}\right)^{42}")

        power = _Power(inner, inner)
        self.assertEqual(power.str(True), r"\left(3.14^{37}\right)^{3.14^{37}}")

    def test_repr_product(self):
        """
        Check that the representation of product calls all repr() on all its
        factors.
        """
        product = _Product("e", 3.14, self)
        self.assertEqual(repr(product), "'e' * 3.14 * %s" % repr(self))

    def test_repr_zero_element(self):
        """
        Check repr() raises an exception is raised if there is no factor in
        the product.
        """
        product = _Product("e", 3.14, self)
        product.factors = []
        self.assertRaises(ValueError, repr, product)

    def test_repr_one_element(self):
        """
        Check repr() raises an exception is raised if there is one factor in
        the product.
        """
        product = _Product("e", 3.14, self)
        product.factors = [1]
        self.assertRaises(ValueError, repr, product)

    def test_repr_fraction(self):
        """
        Check that the representation of product calls all repr() on the
        numerator and denominator.
        """
        fraction = _Fraction(5, self)
        self.assertEqual(repr(fraction), "5 / %s" % repr(self))

    def test_repr_power(self):
        """
        Check that the representation of power calls all repr() on the base
        and exponent.
        """
        power = _Power(self, 3.14)
        self.assertEqual(repr(power), "%s^3.14" % repr(self))

    def test_repr_product_in_product(self):
        """
        Check that repr(product) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(repr(product), "42 * (3.14 * 37) * 0.21")

    def test_repr_product_in_fraction(self):
        """
        Check that repr(fraction) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(repr(fraction), "42 / (3.14 * 37)")

        fraction = _Fraction(inner, 42)
        self.assertEqual(repr(fraction), "(3.14 * 37) / 42")

        fraction = _Fraction(inner, inner)
        self.assertEqual(repr(fraction), "(3.14 * 37) / (3.14 * 37)")

    def test_repr_product_in_power(self):
        """
        Check that repr(power) does add parenthesis for sub products.
        """
        inner = _Product(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(repr(power), "42^(3.14 * 37)")

        power = _Power(inner, 42)
        self.assertEqual(repr(power), "(3.14 * 37)^42")

        power = _Power(inner, inner)
        self.assertEqual(repr(power), "(3.14 * 37)^(3.14 * 37)")
        
    def test_repr_fraction_in_product(self):
        """
        Check that repr(product) does add parenthesis for sub fractions.
        """
        inner = _Fraction(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(repr(product), "42 * (3.14 / 37) * 0.21")

    def test_repr_fraction_in_fraction(self):
        """
        Check that repr(fraction) does add parenthesis for sub fraction.
        """
        inner = _Fraction(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(repr(fraction), "42 / (3.14 / 37)")

        fraction = _Fraction(inner, 42)
        self.assertEqual(repr(fraction), "(3.14 / 37) / 42")

        fraction = _Fraction(inner, inner)
        self.assertEqual(repr(fraction), "(3.14 / 37) / (3.14 / 37)")

    def test_repr_fraction_in_power(self):
        """
        Check that repr(power) does add parenthesis for sub fractions.
        """
        inner = _Fraction(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(repr(power), "42^(3.14 / 37)")

        power = _Power(inner, 42)
        self.assertEqual(repr(power), "(3.14 / 37)^42")

        power = _Power(inner, inner)
        self.assertEqual(repr(power), "(3.14 / 37)^(3.14 / 37)")
        
    def test_repr_power_in_product(self):
        """
        Check that repr(product) does not parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        product = _Product(42, inner, 0.21)
        self.assertEqual(repr(product), "42 * (3.14^37) * 0.21")

    def test_repr_power_in_fraction(self):
        """
        Check that repr(fraction) does add parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        fraction = _Fraction(42, inner)
        self.assertEqual(repr(fraction), "42 / (3.14^37)")

        fraction = _Fraction(inner, 42)
        self.assertEqual(repr(fraction), "(3.14^37) / 42")

        fraction = _Fraction(inner, inner)
        self.assertEqual(repr(fraction), "(3.14^37) / (3.14^37)")

    def test_repr_power_in_power(self):
        """
        Check that repr(power) does add parenthesis for sub powers.
        """
        inner = _Power(3.14, 37)
        power = _Power(42, inner)
        self.assertEqual(repr(power), "42^(3.14^37)")

        power = _Power(inner, 42)
        self.assertEqual(repr(power), "(3.14^37)^42")

        power = _Power(inner, inner)
        self.assertEqual(repr(power), "(3.14^37)^(3.14^37)")

    ############################################################
    # Tests with units

    def test_str_latex_fraction_with_units(self):
        """
        Check that the representation of product calls all str() on the
        numerator and denominator.
        """
        sam = UnitSystem("systeme a moi", 3)
        metre = sam.create_base_unit(0, "Metre", "m", "M")
        second = sam.create_base_unit(1, "Second", "s")

        fraction = _Fraction(metre, second)
        self.assertEqual(fraction.str(latex=True), r"\frac{M}{s}")

    def test_str_latex_power_with_units(self):
        """
        Check that the representation of product calls all str() on the
        base and exponent.
        """
        sam = UnitSystem("systeme a moi", 3, 1)
        metre = sam.create_base_unit(0, "Metre", "m", "M")
        second = sam.create_base_unit(1, "Second", "s")
        rad = sam.create_base_unit(2, "Radian", "rad")

        real = _Power(2, rad)
        self.assertEqual(real.str(), "2^rad")
        self.assertEqual(real.str(latex=True), r"2^{rad}")

    ############################################################
    # __str__
    def test_str_operator_product(self):
        """
        Check that the __str__ calls str().
        """
        product = _Fraction(3, 4)
        self.assertEqual(str(product), "3 / 4")

        product.str = mock.MagicMock(side_effect="hello")
        str(product)
        product.str.assert_called_once_with()

    def test_str_operator_fraction(self):
        """
        Check that the __str__ calls str().
        """
        fraction = _Fraction(3, 4)
        self.assertEqual(str(fraction), "3 / 4")

        fraction.str = mock.MagicMock(side_effect="hello")
        str(fraction)
        fraction.str.assert_called_once_with()


    def test_str_operator_power(self):
        """
        Check that the __str__ calls str().
        """
        power = _Power(3, 4)
        self.assertEqual(str(power), "3^4")

        power.str = mock.MagicMock(side_effect="hello")
        str(power)
        power.str.assert_called_once_with()
