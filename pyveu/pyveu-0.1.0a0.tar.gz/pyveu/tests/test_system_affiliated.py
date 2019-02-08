
# Copyright (C) 2018 Frank Sauerburger

import unittest

from pyveu import SystemAffiliatedMixin

class SystemAffiliatedTestCase(unittest.TestCase):
    """
    This class implements test cases for the SystemAffiliatedMixin.
    """

    def test_init(self):
        """
        Check that the passed parameter is stored internally.
        """
        sa = SystemAffiliatedMixin("systeme-international")
        self.assertEqual(sa._unit_system, "systeme-international")

    def test_get(self):
        """
        Check that unit_system() returns the internal value.
        """
        sa = SystemAffiliatedMixin("systeme-international")
        self.assertEqual(sa.unit_system(), "systeme-international")

    def test_set(self):
        """
        Check that unit_system() can not be used to set the unit system after
        the creation of the object.
        """
        sa = SystemAffiliatedMixin("systeme-international")
        self.assertRaises(TypeError, sa.unit_system, "cm-gram-second")

