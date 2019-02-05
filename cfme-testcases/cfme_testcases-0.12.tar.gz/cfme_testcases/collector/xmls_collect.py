# -*- coding: utf-8 -*-
"""
Collects all the XML files needed for import.
"""

from __future__ import absolute_import, unicode_literals

import copy
import logging

from cfme_testcases import utils
from cfme_testcases.collector import filters, missing
from cfme_testcases.exceptions import NothingToDoException, TestcasesException
from dump2polarion import properties, submit

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class XMLsCollector(object):
    """Methods for collecting XML files for import."""

    # pylint: disable=too-many-arguments
    def __init__(self, args, submit_args, config, testsuites_root, testcases_root):
        self.args = args
        self.submit_args = submit_args
        self.config = config
        self.testsuites_root = testsuites_root
        self.testcases_root = testcases_root

    def _initial_submit(self):
        """Submits XML to Polarion and saves the log file returned by the message bus."""
        if self.args.use_svn and not self.args.testrun_init:
            # no need to submit, SVN is used to generate list of missing testcases
            return None, None
        if not self.submit_args:
            raise NothingToDoException(
                "Instructed not to submit and as the import log is missing, "
                "there's nothing more to do"
            )
        elif self.testsuites_root is None:
            raise TestcasesException("Cannot init testrun, testsuites XML not generated.")

        xml_root = copy.deepcopy(self.testsuites_root)

        if self.args.testrun_init:
            # want to init new test run
            dry_run = self.submit_args.get("dry_run") or False
            if self.args.testrun_title:
                properties.xunit_fill_testrun_title(xml_root, self.args.testrun_title)
        else:
            # want to just get the log file without changing anything
            dry_run = True
            # don't want to use template with dry-run
            properties.remove_property(xml_root, "polarion-testrun-template-id")

        properties.remove_response_property(xml_root)

        log = utils.get_job_logname("init_testsuites", self.args.output_dir)
        init_sargs = self.submit_args.copy()
        init_sargs["dry_run"] = dry_run
        if not submit.submit_and_verify(
            xml_root=xml_root, config=self.config, log_file=log, **init_sargs
        ):
            raise TestcasesException("Failed to do the initial submit.")

        return log, xml_root

    def _get_filtered_xmls(self):
        init_logname, init_testsuites = self._initial_submit()
        missing_testcases = missing.get_missing(
            self.config, self.testcases_root, init_logname, self.args.use_svn
        )

        xmls_container = filters.get_filtered_xmls(
            self.testcases_root,
            self.testsuites_root if self.args.testrun_id else None,
            missing_testcases,
            data_in_code=self.args.data_in_code,
        )

        if self.args.no_testcases_update:
            xmls_container.updated_testcases = None

        if init_testsuites is not None:
            xmls_container.init_testsuites = init_testsuites

        return xmls_container

    def _get_complete_xmls(self):
        xmls_container = utils.XMLsContainer()
        xmls_container.testcases = self.testcases_root

        if not self.args.testrun_init:
            return xmls_container

        if self.args.testrun_title:
            properties.xunit_fill_testrun_title(self.testsuites_root, self.args.testrun_title)

        xmls_container.testsuites = self.testsuites_root

        return xmls_container

    def get_xmls(self):
        """Returns XMLsContainer object with all relevant XML files."""
        if self.args.no_testcases_update or not self.args.data_in_code:
            return self._get_filtered_xmls()
        return self._get_complete_xmls()


def get_xmls(args, submit_args, config, testsuites_root, testcases_root):
    """Returns XMLsContainer object with all relevant XML files."""
    return XMLsCollector(args, submit_args, config, testsuites_root, testcases_root).get_xmls()
