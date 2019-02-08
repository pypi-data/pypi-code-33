
# Copyright (C) 2018 Frank Sauerburger

import unittest

from pyveu import Named, ModifiableNamedMixin

class Helper(ModifiableNamedMixin, Named):
    """
    This helper class is used in the test cases below to check that the mix-in
    works.
    """
    pass

class HelperTestCase(unittest.TestCase):
    """
    This class implements test cases for the ModifiableNamedMixin class. The
    tests use an helper class defined above. The helper class inherits from
    ModifiableNamedMixin and Helper. This makes it possible to test whether the
    mix-in works.
    """

    def test_get_label(self):
        """
        Check that retrieving the label is possible.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.label(), "electric constant")

    def test_get_symbol(self):
        """
        Check that retrieving the symbol is possible.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.symbol(), "e_0")
        
    def test_get_latex(self):
        """
        Check that retrieving the latex symbol is possible.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.latex(), r"\epsilon_0")

    def test_set_label(self):
        """
        Check that setting the label is possible.
        """
        epsilon_0 = Helper("magnetic constant", "e_0", r"\epsilon_0")
        epsilon_0.label("electric constant")
        self.assertEqual(epsilon_0.label(), "electric constant")

    def test_set_symbol(self):
        """
        Check that setting the symbol is possible.
        """
        epsilon_0 = Helper("electric constant", "mu_0", r"\epsilon_0")
        epsilon_0.symbol("e_0")
        self.assertEqual(epsilon_0.symbol(), "e_0")
        
    def test_set_latex(self):
        """
        Check that setting the latex is possible.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\mu_0")
        epsilon_0.latex(r"\epsilon_0")
        self.assertEqual(epsilon_0.latex(), r"\epsilon_0")
        
    def test_get_lors(self):
        """
        Check that setting the lors returns the latex symbol after replacing
        None.
        """
        epsilon_0 = Helper("electric constant", "e_0", None)
        self.assertEqual(epsilon_0.lors(), "e_0")
        epsilon_0.latex(r"\epsilon_0")
        self.assertEqual(epsilon_0.lors(), r"\epsilon_0")
        
    def test_set_lors_fail(self):
        """
        Check that an exception is raised when on tries to update the lors.
        """
        epsilon_0 = Helper("electric constant", "e_0", None)
        self.assertRaises(TypeError, epsilon_0.lors, r"\epsilon_0")

    def test_label_more_args(self):
        """
        Check that an exception is raised, if more than one argument is passed
        to the method.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\epsilon_0")
        self.assertRaises(TypeError, epsilon_0.label, "one", "two")

    def test_symbol_more_args(self):
        """
        Check that an exception is raised, if more than one argument is passed
        to the method.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\epsilon_0")
        self.assertRaises(TypeError, epsilon_0.symbol, "one", "two")

    def test_latex_more_args(self):
        """
        Check that an exception is raised, if more than one argument is passed
        to the method.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\epsilon_0")
        self.assertRaises(TypeError, epsilon_0.latex, "one", "two")

    def test_set_label_none(self):
        """
        Check that the label can be set to None.
        """
        epsilon_0 = Helper("magnetic constant", "e_0", r"\epsilon_0")
        epsilon_0.label(None)
        self.assertIsNone(epsilon_0.label())

    def test_set_symbol_none(self):
        """
        Check that the symbol can be set to None.
        """
        epsilon_0 = Helper("electric constant", "mu_0", r"\epsilon_0")
        epsilon_0.symbol(None)
        self.assertIsNone(epsilon_0.symbol())
        
    def test_set_latex_none(self):
        """
        Check that the latex can be set to None.
        """
        epsilon_0 = Helper("electric constant", "e_0", r"\mu_0")
        epsilon_0.latex(None)
        self.assertIsNone(epsilon_0.latex())
