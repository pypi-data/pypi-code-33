# -*- coding: utf-8 -*-
"""
Generates XML files for importers.
"""

from __future__ import absolute_import, unicode_literals

import io
import json
import logging

import six

from cfme_testcases.exceptions import TestcasesException
from dump2polarion.requirements_exporter import RequirementExport
from dump2polarion.testcases_exporter import TestcaseExport
from dump2polarion.xunit_exporter import ImportedData, XunitExport

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


def _load_json(json_file):
    with io.open(json_file, encoding="utf-8") as input_json:
        return json.load(input_json)


def _resolve_requirements(requirements_mapping, testcases_data):
    for testcase_rec in testcases_data:
        requirement_names = testcase_rec.get("linked-items")
        if not requirement_names:
            continue
        if not requirements_mapping:
            del testcase_rec["linked-items"]
            continue
        if isinstance(requirement_names, (dict, six.string_types)):
            requirement_names = [requirement_names]

        requirement_ids = [requirements_mapping.get(req_name) for req_name in requirement_names]
        if requirement_ids:
            testcase_rec["linked-items"] = requirement_ids
        else:
            del testcase_rec["linked-items"]


def gen_testcases_xml_str(
    testcases_json_filename, requirements_mapping, config, transform_func=None
):
    """Generates the testcases XML string."""
    try:
        testcases_data = _load_json(testcases_json_filename)["testcases"]
    except Exception as err:
        raise TestcasesException(
            "Cannot load test cases from `{}`: {}".format(testcases_json_filename, err)
        )
    _resolve_requirements(requirements_mapping, testcases_data)
    testsuites = TestcaseExport(testcases_data, config, transform_func)
    return testsuites.export()


def gen_testsuites_xml_str(testsuites_json_filename, testrun_id, config, transform_func=None):
    """Generates the testcases XML string."""
    assert testrun_id
    try:
        results = _load_json(testsuites_json_filename)["results"]
    except Exception as err:
        raise TestcasesException(
            "Cannot load results from `{}`: {}".format(testsuites_json_filename, err)
        )
    testsuites_data = ImportedData(results, testrun_id)
    testsuites = XunitExport(testrun_id, testsuites_data, config, transform_func)
    return testsuites.export()


def gen_requirements_xml_str(requirements_data, config, transform_func=None):
    """Generates the requirements XML string."""
    requirements = RequirementExport(requirements_data, config, transform_func)
    return requirements.export()
