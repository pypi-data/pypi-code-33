# -*- coding: utf-8 -*-
"""
Testcases data from Polarion SVN repo.
"""

from __future__ import absolute_import, unicode_literals

import logging
import os
import re

from cfme_testcases.exceptions import TestcasesException
from dump2polarion import svn_polarion

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class PolarionTestcases(object):
    """Loads and access Polarion testcases."""

    TEST_PARAM = re.compile(r"\[.*\]")

    def __init__(self, repo_dir):
        self.repo_dir = repo_dir
        self.wi_cache = svn_polarion.WorkItemCache(repo_dir)
        self.available_testcases = {}

    def load_active_testcases(self, lookup_by="title"):
        """Creates dict of all active testcase's names and ids."""
        cases = {}
        for item in self.wi_cache.get_all_items():
            if item.get("type") != "testcase":
                continue
            case_status = item.get("status")
            if not case_status or case_status == "inactive":
                continue

            case_title = item.get(lookup_by)
            case_id = item.get("work_item_id")
            try:
                cases[case_title].append(case_id)
            except KeyError:
                cases[case_title] = [case_id]

        self.available_testcases = cases

    def __getitem__(self, item):
        return self.available_testcases[item]

    def __iter__(self):
        return iter(self.available_testcases)

    def __len__(self):
        return len(self.available_testcases)

    def __contains__(self, item):
        return item in self.available_testcases

    def __repr__(self):
        return "<Testcases {}>".format(self.available_testcases)


def get_missing(repo_dir, testcase_identifiers, lookup_by="title"):
    """Gets set of testcases missing in Polarion."""
    polarion_testcases = PolarionTestcases(os.path.expanduser(repo_dir))
    try:
        polarion_testcases.load_active_testcases(lookup_by=lookup_by)
    except Exception as err:
        raise TestcasesException(
            "Failed to load testcases from SVN repo `{}`: {}".format(repo_dir, err)
        )
    if not polarion_testcases:
        raise TestcasesException("No testcases loaded from SVN repo `{}`.".format(repo_dir))
    missing = set(testcase_identifiers) - set(polarion_testcases)
    return missing
