# -*- coding: utf-8 -*-
"""
Submits collected XML files to appropriate Importers in appropriate order.
"""

from __future__ import absolute_import, unicode_literals

import logging
import threading

from cfme_testcases import utils
from cfme_testcases.exceptions import NothingToDoException, TestcasesException
from dump2polarion import properties, submit
from dump2polarion import utils as d2p_utils

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


class CollectedDataSubmitter(object):
    """Submitter of collected XMLs."""

    def __init__(self, submit_args, config, xmls_container, output_dir=None):
        self.submit_args = submit_args
        self.config = config
        self.xmls_container = xmls_container
        self.output_dir = output_dir

    @staticmethod
    def _get_job_log(file_type, output_dir):
        if not output_dir:
            return None
        return utils.get_job_logname(file_type, output_dir)

    @staticmethod
    def _append_msg(retval, msg, succeeded, failed):
        if retval:
            succeeded.append(msg)
        else:
            failed.append(msg)

    @staticmethod
    def _log_outcome(succeeded, failed):
        if succeeded and failed:
            logger.info("SUCCEEDED to %s", ", ".join(succeeded))
        if failed:
            raise TestcasesException("FAILED to {}.".format(", ".join(failed)))

        logger.info("DONE - RECORDS SUCCESSFULLY UPDATED!")

    def _submit_xml(self, xml_root, file_type):
        if xml_root is None:
            raise NothingToDoException("No data to import.")

        job_log = self._get_job_log(file_type, self.output_dir)
        properties.remove_response_property(xml_root)
        return submit.submit_and_verify(
            xml_root=xml_root, config=self.config, log_file=job_log, **self.submit_args
        )

    def update_existing_testcases(self):
        """Updates existing testcases in new thread."""
        if self.xmls_container.updated_testcases is None:
            raise NothingToDoException("No data to import.")

        job_log = self._get_job_log("updated_testcases", self.output_dir)
        properties.remove_response_property(self.xmls_container.updated_testcases)
        all_submit_args = dict(
            xml_root=self.xmls_container.updated_testcases,
            config=self.config,
            log_file=job_log,
            **self.submit_args
        )

        # run it in separate thread so we can continue without waiting
        # for the submit to finish
        def _run_submit(results, args_dict):
            retval = submit.submit_and_verify(**args_dict)
            results.append(retval)

        output = []
        updating_testcases_t = threading.Thread(target=_run_submit, args=(output, all_submit_args))
        updating_testcases_t.start()

        return updating_testcases_t, output

    def _import_missing(self, succeeded, failed):
        # create missing testcases in Polarion
        testcases_submitted = False
        try:
            testcases_submitted = self._submit_xml(
                self.xmls_container.missing_testcases, "missing_testcases"
            )
            self._append_msg(testcases_submitted, "add missing testcases", succeeded, failed)
        except NothingToDoException:
            pass

        testrun_id = self.submit_args.get("testrun_id") or d2p_utils.get_testrun_id_config(
            self.config
        )

        # add missing testcases to testrun
        if testcases_submitted and testrun_id:
            try:
                testcases_added = self._submit_xml(
                    self.xmls_container.missing_testsuites, "missing_testsuites"
                )
                self._append_msg(testcases_added, "update testrun", succeeded, failed)
            except NothingToDoException:
                pass
        elif not testrun_id and self.xmls_container.missing_testcases is not None:
            logger.warning("Not updating testrun, testrun ID not specified.")

    def _import_unfiltered(self, succeeded, failed):
        # import unfiltered testcases into Polarion
        testcases_submitted = False
        try:
            testcases_submitted = self._submit_xml(self.xmls_container.testcases, "testcases")
            self._append_msg(testcases_submitted, "add all testcases", succeeded, failed)
        except NothingToDoException:
            pass

        testrun_id = self.submit_args.get("testrun_id") or d2p_utils.get_testrun_id_config(
            self.config
        )

        # add all testcases to testrun
        if testcases_submitted and testrun_id:
            try:
                testcases_added = self._submit_xml(self.xmls_container.testsuites, "testsuites")
                self._append_msg(testcases_added, "create testrun", succeeded, failed)
            except NothingToDoException:
                pass
        elif not testrun_id and self.xmls_container.testcases is not None:
            logger.warning("Not updating testrun, testrun ID not specified.")

    def submit_all(self):
        """Submits all outstanding XMLs to Polarion Importers.

        There should be only filtered XMLs or complete XMLs in the `self.xmls_container`.
        """
        if not self.submit_args:
            return

        succeeded, failed = [], []

        # requirements are needed by testcases, update them first
        try:
            requirements_updated = self._submit_xml(
                self.xmls_container.requirements, "requirements"
            )
            self._append_msg(requirements_updated, "update requirements", succeeded, failed)
        except NothingToDoException:
            pass

        # update existing testcases in new thread
        updating_testcases_t = None
        try:
            updating_testcases_t, output = self.update_existing_testcases()
        except NothingToDoException:
            pass

        # import missing data
        self._import_missing(succeeded, failed)

        # wait for update of existing testcases to finish
        if updating_testcases_t:
            updating_testcases_t.join()
            self._append_msg(output.pop(), "update existing testcases", succeeded, failed)

        # import complete data
        self._import_unfiltered(succeeded, failed)

        self._log_outcome(succeeded, failed)


def submit_all(submit_args, config, xmls_container, output_dir):
    """Submits collected XML files to Polarion Importers."""
    return CollectedDataSubmitter(submit_args, config, xmls_container, output_dir).submit_all()
