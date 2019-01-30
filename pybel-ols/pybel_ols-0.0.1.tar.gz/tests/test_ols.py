# -*- coding: utf-8 -*-

"""Tests for PyBEL-OLS."""

import unittest

from pybel.constants import NAMESPACE_DOMAIN_OTHER
from pybel_ols import OlsNamespaceOntology


class TestWrapper(unittest.TestCase):
    """Tests the wrappers of the OLS."""

    def test_import_ols(self):
        """Test a namespace can be imported."""
        OlsNamespaceOntology('uberon', NAMESPACE_DOMAIN_OTHER, encoding='A')
