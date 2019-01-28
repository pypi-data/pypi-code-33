# -*- coding: utf-8 -*-
"""
Upload missing testcases and update existing testcases.
"""

from __future__ import absolute_import, unicode_literals

import logging
import threading


from cfme_testcases import utils
from cfme_testcases.exceptions import NothingToDoException
from dump2polarion import submit

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


def _get_job_log(output_dir, prefix):
    if not output_dir:
        return None
    return utils.get_job_logname(prefix, output_dir)


def create_missing_testcases(submit_args, config, filtered_xmls, output_dir=None):
    """Creates missing testcases in Polarion."""
    if filtered_xmls.missing_testcases is None:
        raise NothingToDoException("No data to import.")

    job_log = _get_job_log(output_dir, "testcases")
    return submit.submit_and_verify(
        xml_root=filtered_xmls.missing_testcases, config=config, log_file=job_log, **submit_args
    )


def update_existing_testcases(submit_args, config, filtered_xmls, output_dir=None):
    """Updates existing testcases in new thread."""
    if filtered_xmls.updated_testcases is None:
        raise NothingToDoException("No data to import.")

    job_log = _get_job_log(output_dir, "update")
    all_submit_args = dict(
        xml_root=filtered_xmls.updated_testcases, config=config, log_file=job_log, **submit_args
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


def add_missing_testcases_to_testrun(submit_args, config, filtered_xmls, output_dir=None):
    """Adds missing testcases to testrun."""
    if filtered_xmls.missing_testsuites is None:
        raise NothingToDoException("No data to import.")

    job_log = _get_job_log(output_dir, "testrun")
    return submit.submit_and_verify(
        xml_root=filtered_xmls.missing_testsuites, config=config, log_file=job_log, **submit_args
    )
