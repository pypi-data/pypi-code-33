#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################


import os
import sys
from contextlib import contextmanager

if sys.version_info >= (3, 2):
    import tempfile
else:
    from backports import tempfile


@contextmanager
def reroot_cvm(root):
    from LbPlatformUtils import inspect
    try:
        bkup = inspect.SINGULARITY_ROOTS
        inspect.SINGULARITY_ROOTS = [
            (os.path.join(root, os.path.basename(path)), os_id)
            for path, os_id in inspect.SINGULARITY_ROOTS
        ]
        yield
    finally:
        inspect.SINGULARITY_ROOTS = bkup


def test_singularity():
    from LbPlatformUtils import inspect
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['PATH'] = temp_dir + os.pathsep + os.environ['PATH']
        with open(os.path.join(temp_dir, 'singularity'), 'wb') as script:
            script.writelines([
                b'#!/bin/sh\n',
                b'exit ${TEST_SING_EXIT:-0}'
            ])
        os.chmod(os.path.join(temp_dir, 'singularity'), 0o775)
        os.mkdir(os.path.join(temp_dir, 'cvm4'))
        os.mkdir(os.path.join(temp_dir, 'cvm3'))
        with reroot_cvm(temp_dir):
            # test no singularity
            os.environ['TEST_SING_EXIT'] = '1'
            assert inspect.singularity_os_ids() == []

            del os.environ['TEST_SING_EXIT']
            assert inspect.singularity_os_ids() == inspect.SINGULARITY_ROOTS
