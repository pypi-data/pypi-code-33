# -*- coding: utf-8 -*-
"""
Methods for generating and working with testcases XML files.
"""

from __future__ import absolute_import, unicode_literals

import datetime
import io
import json
import logging

import six

from cfme_testcases.exceptions import TestcasesException
from dump2polarion import utils as d2p_utils
from dump2polarion.exporters import testcases_exporter, xunit_exporter

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class TestcasesXML(object):
    """Generate XML for Testcases Importer."""

    def __init__(self, config, requirements_mapping, tests_data_json, transform_func=None):
        self.config = config
        self.requirements_mapping = requirements_mapping
        self.tests_data_json = tests_data_json
        self.transform_func = transform_func

    def resolve_requirements(self, testcases_data):
        """Resolves requirements names to IDs."""
        for testcase_rec in testcases_data:
            requirement_names = testcase_rec.get("linked-items")
            if not requirement_names:
                continue
            if not self.requirements_mapping:
                del testcase_rec["linked-items"]
                continue
            if isinstance(requirement_names, (dict, six.string_types)):
                requirement_names = [requirement_names]

            requirement_ids = [
                self.requirements_mapping.get(req_name) for req_name in requirement_names
            ]
            if requirement_ids:
                testcase_rec["linked-items"] = requirement_ids
            else:
                del testcase_rec["linked-items"]

    def gen_testcases_xml_str(self):
        """Generates the testcases XML string."""
        try:
            testcases_data = _load_json(self.tests_data_json)["testcases"]
        except Exception as err:
            raise TestcasesException(
                "Cannot load test cases from `{}`: {}".format(self.tests_data_json, err)
            )
        self.resolve_requirements(testcases_data)
        testcases = testcases_exporter.TestcaseExport(
            testcases_data, self.config, self.transform_func
        )
        return testcases.export()


def _load_json(json_file):
    with io.open(json_file, encoding="utf-8") as input_json:
        return json.load(input_json)


def gen_testsuites_xml_str(config, testrun_id, tests_data_json, transform_func=None):
    """Generates the testsuites XML string."""
    assert testrun_id
    try:
        results = _load_json(tests_data_json)["results"]
    except Exception as err:
        raise TestcasesException("Cannot load results from `{}`: {}".format(tests_data_json, err))
    testsuites_data = xunit_exporter.ImportedData(results, testrun_id)
    testsuites = xunit_exporter.XunitExport(testrun_id, testsuites_data, config, transform_func)
    return testsuites.export()


def get_testsuites_xml_root(config, testrun_id, tests_data_json, transform_func=None):
    """Returns content of XML files for importers."""
    testrun_id = (
        testrun_id
        or d2p_utils.get_testrun_id_config(config)
        or "IMPORT_{:%Y%m%d%H%M%S}".format(datetime.datetime.now())
    )
    testsuites_str = gen_testsuites_xml_str(
        config, testrun_id, tests_data_json, transform_func=transform_func
    )
    return d2p_utils.get_xml_root_from_str(testsuites_str)


def get_testcases_xml_root(config, requirements_mapping, tests_data_json, transform_func=None):
    """Returns content of XML files for importers."""
    testcases_xml = TestcasesXML(
        config, requirements_mapping, tests_data_json, transform_func=transform_func
    )
    testcases_str = testcases_xml.gen_testcases_xml_str()
    return d2p_utils.get_xml_root_from_str(testcases_str)


def get_all_testcases(testcases_root):
    """Gets all testcases from XML."""
    if testcases_root.tag != "testcases":
        raise TestcasesException("XML file is not in expected format.")

    testcase_instances = testcases_root.findall("testcase")
    # Expect that in ID is the value we want.
    # In case of "lookup-method: name" it's test case title.
    attr = "id"

    for testcase in testcase_instances:
        tc_id = testcase.get(attr)
        if tc_id:
            yield tc_id
