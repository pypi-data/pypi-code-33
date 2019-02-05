# -*- coding: utf-8 -*-
"""
Filter missing testcases and testcases for update.
"""

from __future__ import absolute_import, unicode_literals

import copy
from collections import namedtuple

from cfme_testcases.exceptions import TestcasesException
from dump2polarion import properties

FilteredXMLs = namedtuple("FilteredXMLs", "missing_testcases missing_testsuites updated_testcases")


class XMLFilters(object):
    """Filters for testcases in Importer's XML files."""

    def __init__(self, testcases_root, testsuites_root, missing, data_in_code=False):
        self.testcases_root = testcases_root
        self.testsuites_root = testsuites_root
        self.missing = missing or set()
        self.data_in_code = data_in_code

    def get_missing_testcases(self):
        """Gets testcases missing in Polarion."""
        xml_root = copy.deepcopy(self.testcases_root)
        properties.remove_response_property(xml_root)

        testcase_instances = xml_root.findall("testcase")
        # Expect that in ID is the value we want.
        # In case of "lookup-method: name" it's test case title.
        attr = "id"

        for testcase in testcase_instances:
            tc_id = testcase.get(attr)
            if tc_id and tc_id not in self.missing:
                xml_root.remove(testcase)

        if not xml_root.findall("testcase"):
            return None

        return xml_root

    def get_missing_testsuites(self):
        """Gets testcases missing in testrun."""
        xml_root = copy.deepcopy(self.testsuites_root)

        properties.remove_response_property(xml_root)
        # don't want to use/update any of these properties when adding tests to testrun
        for prop in (
            "polarion-group-id",
            "polarion-testrun-status-id",
            "polarion-testrun-template-id",
            "polarion-testrun-title",
        ):
            properties.remove_property(xml_root, prop)

        testsuite = xml_root.find("testsuite")
        testcase_parent = testsuite
        testcase_instances = testcase_parent.findall("testcase")
        attr = "name"

        for testcase in testcase_instances:
            # try to get test case ID first and if it fails, get name
            try:
                tc_id_prop = testcase.xpath('.//property[@name = "polarion-testcase-id"]')[0]
                tc_id = tc_id_prop.get("value")
            except IndexError:
                tc_id = testcase.get(attr)
            if tc_id and tc_id not in self.missing:
                testcase_parent.remove(testcase)

        if not testcase_parent.findall("testcase"):
            return None

        testcase_parent.set("tests", str(len(testcase_parent.findall("testcase"))))
        testcase_parent.attrib.pop("errors", None)
        testcase_parent.attrib.pop("failures", None)
        testcase_parent.attrib.pop("skipped", None)

        return xml_root

    def get_updated_testcases(self):
        """Gets testcases that will be updated in Polarion."""
        xml_root = copy.deepcopy(self.testcases_root)

        properties.remove_response_property(xml_root)
        properties.set_lookup_method(xml_root, "name")

        testcase_instances = xml_root.findall("testcase")
        attr = "id"

        for testcase in testcase_instances:
            tc_id = testcase.get(attr)
            if tc_id is not None and tc_id in self.missing:
                xml_root.remove(testcase)
                continue

            if self.data_in_code:
                continue

            # source not authoritative, don't update custom-fields
            cfields_parent = testcase.find("custom-fields")
            cfields_instances = cfields_parent.findall("custom-field")
            for field in cfields_instances:
                field_id = field.get("id")
                if field_id not in ("automation_script", "caseautomation"):
                    cfields_parent.remove(field)

        if not xml_root.findall("testcase"):
            return None

        return xml_root

    def get_filtered_xmls(self):
        """Returns modified XMLs with testcases and testsuites."""
        missing_testcases, missing_testsuites, updated_testcases = None, None, None

        if self.missing:
            if self.testcases_root is not None:
                missing_testcases = self.get_missing_testcases()
            if self.testsuites_root is not None:
                missing_testsuites = self.get_missing_testsuites()

        if self.testcases_root is not None:
            updated_testcases = self.get_updated_testcases()

        return FilteredXMLs(missing_testcases, missing_testsuites, updated_testcases)


def check_xml_roots(testcases_root, testsuites_root):
    """Checks that the XML files are in expected format."""
    if testcases_root is not None and testcases_root.tag != "testcases":
        raise TestcasesException("XML file is not in expected format.")
    if testsuites_root is not None and testsuites_root.tag != "testsuites":
        raise TestcasesException("XML file is not in expected format.")


def get_filtered_xmls(testcases_root, testsuites_root, missing, data_in_code=False):
    """Returns modified XMLs with testcases and testsuites."""
    check_xml_roots(testcases_root, testsuites_root)
    return XMLFilters(
        testcases_root, testsuites_root, missing, data_in_code=data_in_code
    ).get_filtered_xmls()
