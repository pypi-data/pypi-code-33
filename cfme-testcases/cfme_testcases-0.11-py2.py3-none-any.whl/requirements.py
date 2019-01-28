# -*- coding: utf-8 -*-
"""
Create missing requirements and create list of requirements names and IDs.
"""

from __future__ import absolute_import, unicode_literals

import io
import json
import logging

from cfme_testcases import cfme_parsereq
from cfme_testcases.exceptions import TestcasesException
from dump2polarion import utils as d2p_utils
from dump2polarion.exporters import requirements_exporter

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class RequirementsXML(object):
    """Creates requirements XML."""

    def __init__(self, config, testcases_json, requirements_data=None, transform_func=None):
        self.config = config
        self.testcases_json = testcases_json
        self.transform_func = transform_func
        self._requirements_data = requirements_data

    def get_requirements_from_testcases(self):
        """Gets requirements used in test cases."""
        with io.open(self.testcases_json, encoding="utf-8") as input_json:
            testcases = json.load(input_json)["testcases"]

        requirements = set()
        for testcase in testcases:
            linked_items = testcase.get("linked-items")
            if linked_items:
                requirements.update(linked_items)

        requirements_data = [{"title": req} for req in requirements]
        return requirements_data

    @property
    def requirements_data(self):
        """Gets requirements data."""
        if self._requirements_data:
            return self._requirements_data

        try:
            self._requirements_data = cfme_parsereq.get_requirements()
        except TestcasesException:
            self._requirements_data = self.get_requirements_from_testcases()
        return self._requirements_data

    def gen_requirements(self):
        """Generates the requirements XML string using requirements data."""
        return gen_requirements_xml_str(self.requirements_data, self.config, self.transform_func)

    def get_requirements_xml_root(self):
        """Gets the requirements XML root."""
        req_xml_str = self.gen_requirements()
        return d2p_utils.get_xml_root_from_str(req_xml_str)


def gen_requirements_xml_str(requirements_data, config, transform_func=None):
    """Generates the requirements XML string."""
    requirements = requirements_exporter.RequirementExport(
        requirements_data, config, transform_func
    )
    return requirements.export()


def get_requirements_xml_root(config, testcases_json, requirements_data=None, transform_func=None):
    """Gets the requirements XML root."""
    return RequirementsXML(
        config, testcases_json, requirements_data=requirements_data, transform_func=transform_func
    ).get_requirements_xml_root()
