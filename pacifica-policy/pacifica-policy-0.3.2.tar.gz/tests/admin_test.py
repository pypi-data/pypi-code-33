#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the uploader policy."""
from cherrypy.test import helper
from pacifica.policy.admin import AdminPolicy
from common_test import CommonCPSetup


class TestAdminBase(helper.CPWebCase, CommonCPSetup):
    """Test the uploader policy service."""

    PORT = 8181
    HOST = '127.0.0.1'
    headers = [('Content-Type', 'application/json')]

    def test_ingest_coverage(self):
        """Validate uploader returning xref validation."""
        adm_policy = AdminPolicy()
        valid_pairs = [
            (100, 54),
            (10, 54)
        ]
        # pylint: disable=protected-access
        for user_id, inst_id in valid_pairs:
            for prop_id in adm_policy._proposals_for_user_inst(user_id, inst_id):
                self.assertTrue(
                    inst_id in adm_policy._instruments_for_user_prop(user_id, prop_id))
        # pylint: enable=protected-access

    def test_base_queries(self):
        """Test the base class queries."""
        adm_policy = AdminPolicy()
        # pylint: disable=protected-access
        res = adm_policy._proposals_for_custodian(10)
        # pylint: enable=protected-access
        self.assertTrue('1234a' in res)
