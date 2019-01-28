# -*- coding: utf-8 -*-
"""
Create missing requirements and create list of requirements names and IDs.
"""

from __future__ import absolute_import, unicode_literals

import io
import json
import logging
import os

from cfme_testcases import cfme_parsereq, cli_utils, gen_xmls
from cfme_testcases.exceptions import TestcasesException
from dump2polarion import parselogs, properties, submit
from dump2polarion import utils as d2p_utils

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class RequirementsUpdater(object):
    """Updates requirements."""

    def __init__(self, args, submit_args, config, req_xml_root):
        self.args = args
        self.submit_args = submit_args
        self.config = config
        self.req_xml_root = req_xml_root

    def get_req_logname(self):
        """Returns filename of the message bus log file."""
        req_log = "req-job-{}.log".format(cli_utils.get_filename_str(self.args))
        req_log = os.path.join(self.args.output_dir or "", req_log)
        return req_log

    def submit_requirements_xml(self, log):
        """Submits the pre-generated requirements file to the importer."""
        properties.remove_response_property(self.req_xml_root)

        if not submit.submit_and_verify(
            xml_root=self.req_xml_root, config=self.config, log_file=log, **self.submit_args
        ):
            raise TestcasesException("Failed to do the requirements submit.")

    def update_requirements(self):
        """Updates the requirements in Polarion."""
        if self.args.no_submit:
            return None

        req_logname = self.get_req_logname()
        self.submit_requirements_xml(req_logname)
        return req_logname

    @staticmethod
    def get_requirements_from_log(req_logname):
        """Generates the requirements mapping using importer log file."""
        if req_logname:
            req_logname = os.path.expanduser(req_logname)
        if not (req_logname and os.path.isfile(req_logname)):
            logger.warning("No requirements log file supplied, skipping requirements generation.")
            return None
        with io.open(req_logname, encoding="utf-8") as input_file:
            return parselogs.RequirementsParser(input_file, req_logname).parse()

    def get_requirements_mapping(self):
        """Generates the requirements mapping."""
        req_logname = self.update_requirements()
        requirements = self.get_requirements_from_log(req_logname)
        new_items = {req.name: req.id for req in requirements.new_items if req.id}
        existing_items = {req.name: req.id for req in requirements.existing_items if req.id}
        existing_items.update(new_items)
        return existing_items


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
        return gen_xmls.gen_requirements_xml_str(
            self.requirements_data, self.config, self.transform_func
        )

    def get_requirements_xml_root(self):
        """Gets the requirements XML root."""
        req_xml_str = self.gen_requirements()
        return d2p_utils.get_xml_root_from_str(req_xml_str)


def get_requirements_mapping(args, submit_args, config, req_xml_root):
    """Generates the requirements mapping."""
    return RequirementsUpdater(args, submit_args, config, req_xml_root).get_requirements_mapping()


def get_requirements_xml_root(config, testcases_json, requirements_data=None, transform_func=None):
    """Gets the requirements XML root."""
    return RequirementsXML(
        config, testcases_json, requirements_data=requirements_data, transform_func=transform_func
    ).get_requirements_xml_root()
