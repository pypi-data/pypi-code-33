
# Copyright (C) 2018 Frank Sauerburger

import unittest

from pyveu import Named

class NamedTestCase(unittest.TestCase):
    """
    This class implements test cases for the Named class.
    """

    def test_init(self):
        """
        Check that named object can be created and that the given values are
        stored internally. The parameters are given as keywords arguments.
        """
        epsilon_0 = Named(label="electric constant", symbol="e_0",
                          latex=r"\epsilon_0")

        self.assertIsInstance(epsilon_0, Named)

        self.assertEqual(epsilon_0._label, "electric constant")
        self.assertEqual(epsilon_0._symbol, "e_0")
        self.assertEqual(epsilon_0._latex, r"\epsilon_0")

    def test_init_order(self):
        """
        Check that named object can be created and that the given values are
        stored internally. The parameters are given as positional arguments.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")

        self.assertIsInstance(epsilon_0, Named)

        self.assertEqual(epsilon_0._label, "electric constant")
        self.assertEqual(epsilon_0._symbol, "e_0")
        self.assertEqual(epsilon_0._latex, r"\epsilon_0")

    def test_label(self):
        """
        Check that label() returns the label of the named object.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.label(), "electric constant")
        
    def test_symbol(self):
        """
        Check that symbol() returns the symbol of the named object.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.symbol(), "e_0")
        
    def test_latex(self):
        """
        Check that latex() returns the latex symbol of the named object.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.latex(), r"\epsilon_0")
        
    def test_label_None(self):
        """
        Check that label() returns None, if the None was passed to the
        constructor.
        """
        epsilon_0 = Named(None, "e_0", r"\epsilon_0")
        self.assertIsNone(epsilon_0.label())
        
    def test_symbol_None(self):
        """
        Check that symbol() returns None, if the None was passed to the
        constructor.
        """
        epsilon_0 = Named("electric constant", None, r"\epsilon_0")
        self.assertIsNone(epsilon_0.symbol())
        
    def test_latex_None(self):
        """
        Check that latex() returns None, if the None was passed to the
        constructor.
        """
        epsilon_0 = Named("electric constant", "e_0", None)
        self.assertIsNone(epsilon_0.latex())

    def test_lors_symbol(self):
        """
        Check that lors() returns the symbol if the latex symbol is None.
        """ 
        epsilon_0 = Named("electric constant", "e_0", None)
        self.assertEqual(epsilon_0.lors(), "e_0")

    def test_lors_latex(self):
        """
        Check that lors() returns the latex symbol if it is not None.
        """ 
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertEqual(epsilon_0.lors(), r"\epsilon_0")

    def test_lors_empty_string(self):
        """
        Check that lors() returns an empty string, if the latex symbol is an
        empty string.
        """ 
        epsilon_0 = Named("electric constant", "e_0", "")
        self.assertEqual(epsilon_0.lors(), "")

    def test_lors_None(self):
        """
        Check that lors() returns None if neither symbol nor latex symbol are
        set.
        """ 
        epsilon_0 = Named("electric constant", None, None)
        self.assertIsNone(epsilon_0.lors())

    def test_label_ro(self):
        """
        Check that the label symbol cannot be set via the label() method.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertRaises(TypeError, epsilon_0.label, "magnetic constant")
        
    def test_symbol_ro(self):
        """
        Check that the symbol cannot be set via the symbol() method.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertRaises(TypeError, epsilon_0.symbol, "mu_0")
        
    def test_latex_ro(self):
        """
        Check that the latex symbol cannot be set via the latex() method.
        """
        epsilon_0 = Named("electric constant", "e_0", r"\epsilon_0")
        self.assertRaises(TypeError, epsilon_0.latex, r"\mu_0")
        
        
