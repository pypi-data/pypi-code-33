# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.behaviors.testing import COLLECTIVE_BEHAVIORS_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.behaviors is properly installed."""

    layer = COLLECTIVE_BEHAVIORS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.behaviors is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.behaviors'))

    def test_browserlayer(self):
        """Test that ICollectiveBehaviorsLayer is registered."""
        from collective.behaviors.interfaces import (
            ICollectiveBehaviorsLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveBehaviorsLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIORS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.behaviors'])

    def test_product_uninstalled(self):
        """Test if collective.behaviors is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.behaviors'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveBehaviorsLayer is removed."""
        from collective.behaviors.interfaces import ICollectiveBehaviorsLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveBehaviorsLayer, utils.registered_layers())
