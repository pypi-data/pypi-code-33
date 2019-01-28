# -*- coding: utf-8 -*-
"""
Utils for CLI.
"""

from __future__ import absolute_import, unicode_literals

import datetime
import logging
import os
import random
import string

from cfme_testcases import consts
from dump2polarion import utils as d2p_utils

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


def get_submit_args(args):
    """Gets arguments for the `submit_and_verify` method."""
    submit_args = dict(
        testrun_id=args.testrun_id,
        user=args.user,
        password=args.password,
        no_verify=args.no_verify,
        verify_timeout=args.verify_timeout,
        dry_run=args.dry_run,
    )
    return {k: v for k, v in submit_args.items() if v is not None}


def get_filename_str(args):
    """Generates part of the filename with timestamp or testrun id."""
    return "{}-{:%Y%m%d%H%M%S}".format(
        args.testrun_id or "".join(random.sample(string.ascii_lowercase, 5)),
        datetime.datetime.now(),
    )


def get_import_file_name(args, file_name, path, key):
    """Generates filename for file saving."""
    return os.path.join(path, "import-{}-{}-{}".format(get_filename_str(args), key, file_name))


def save_generated_xmls(args, filtered_xmls, requirements_xml):
    """Saves the generated XML files if instructed to do so."""
    if not (args.no_submit or args.output_dir):
        return

    path = args.output_dir or "."

    if filtered_xmls.missing_testcases is not None:
        filter_testcases_file = get_import_file_name(args, consts.TEST_CASE_XML, path, "missing")
        d2p_utils.write_xml_root(filtered_xmls.missing_testcases, filter_testcases_file)

    if filtered_xmls.missing_testsuites is not None:
        filter_testsuites_file = get_import_file_name(args, consts.TEST_RUN_XML, path, "missing")
        d2p_utils.write_xml_root(filtered_xmls.missing_testsuites, filter_testsuites_file)

    if filtered_xmls.updated_testcases is not None:
        filter_testcases_file = get_import_file_name(args, consts.TEST_CASE_XML, path, "update")
        d2p_utils.write_xml_root(filtered_xmls.updated_testcases, filter_testcases_file)

    if requirements_xml is not None:
        requirements_file = get_import_file_name(args, consts.REQUIREMENTS_XML, path, "create")
        d2p_utils.write_xml_root(requirements_xml, requirements_file)


def is_testsuites_xml_needed(args):
    """Check if it's necessary to generate the XUnit XML."""
    if args.use_svn and not args.testrun_init and not args.testrun_id:
        return False
    return True
