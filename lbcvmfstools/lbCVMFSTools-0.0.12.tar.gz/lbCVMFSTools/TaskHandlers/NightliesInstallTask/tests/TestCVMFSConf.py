###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Test of the version path manager functionality in the model classes.

@author: Stefan-Gabriel CHITIC
'''
import json
import logging
import shutil
import subprocess
import unittest

import os

from lbCVMFSTools.Injector import injector
from lbCVMFSTools.TaskHandlers.NightliesInstallTask.NightliesInstallTask \
    import NightliesInstallTask
from lbCVMFSTools.TaskHandlers.NightliesInstallTask.Utils import \
    SlotsManager, PathManager, InstalledManager
from lbCVMFSTools.tests.MockLogger import MockLoggingHandler


class TestManager(unittest.TestCase):

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1235")
        os.mkdir("/tmp/foo/")
        os.mkdir("/tmp/foo/conf/")
        os.mkdir("/tmp/foo/var/")

        with open(
                "/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1235/.installed",
                'w') as f:
            f.write("1234\n")
        self.pManager = PathManager(
            installArea="/tmp/toto/cvmfstest.cern.ch/nightlies",
            workspace="/tmp/foo/")
        injector.provide_instance(PathManager, self.pManager)
        self.iManager = InstalledManager(pathManager=self.pManager)
        self.manager = NightliesInstallTask()
        self.args = None
        self.kwargs = None
        self.mocked_return_code = 0
        self.return_data_slots = {
            'afs': [],
            'cvmfs': [
                 {'slot': 'slot1',
                  'build_id': 1235,
                  'platform': 'centos7_x64_opt',
                  'completed': True},
                 {'slot': 'slot2',
                  'build_id': 1243,
                  'platform': 'centos7_x64_opt',
                  'completed': False},
                 {'slot': 'slot1',
                  'build_id': 1235,
                  'platform': 'centos7_x86_opt',
                  'completed': False},
             ]}
        # Mock Suprocess :
        subprocess.call = self.mocked_call
        SlotsManager.getSlots = self.mocked_getSlots

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def mocked_call(self, *a, **kw):
        self.args = a
        self.kwargs = kw
        return self.mocked_return_code

    def mocked_getSlots(self, *a, **kw):
        self.args = a
        self.kwargs = kw
        return self.return_data_slots

    def test_get_list_of_tasks(self):
        # Test with all slots not install
        todos = self.manager.get_list_of_tasks()
        parsed_slots = []
        for c in self.return_data_slots['cvmfs']:
            parsed_slots.append((c['slot'], c['build_id'], c['platform'],
                                 c['completed']))
        self.assertEqual(todos, parsed_slots)

        # Mark 1 slot as installed
        parsed_slots = []
        for c in self.return_data_slots['cvmfs']:
            if c['completed']:
                self.iManager.addInstalled([(c['slot'], c['build_id'],
                                            c['platform'])])
                continue
            parsed_slots.append((c['slot'], c['build_id'], c['platform']))
        todos = self.manager.get_list_of_tasks()
        self.assertEqual(todos, parsed_slots)

        # Mark all as completed, check log
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        parsed_slots = []
        for c in self.return_data_slots['cvmfs']:
            if not c['completed']:
                self.iManager.addInstalled([(c['slot'], c['build_id'],
                                             c['platform'])])
        todos = self.manager.get_list_of_tasks()
        self.assertEqual(todos, parsed_slots)
        logs = []
        for c in self.return_data_slots['cvmfs']:
            logs.append("%s, %s, %s is already installed for today, "
                        "skipping" % (c['slot'], c['build_id'], c['platform']))
        logs.append('All slots installed, nothing to do')
        self.assertEqual(sorted(logs),
                         sorted(self.handler.messages['info']))

    def test_perform_task_dry_run(self):
        self.manager = NightliesInstallTask(dry_run=True)

        todos = self.manager.get_list_of_tasks()

        # Perform 1 installation
        self.manager.perform_task(todos[0])
        logs = [
            'IN DRY-RUN MODE: Need to fix the links for slot1 1235',
            'IN DRY-RUN MODE: Updating slot1 1235 centos7_x64_opt',
            'IN DRY-RUN MODE: Invoking: lbn-install '
            '--dest=/tmp/toto/cvmfstest.cern.ch/'
            'nightlies/slot1/1235 --platforms=centos7_x64_opt slot1 1235',
            'IN DRY-RUN MODE: Install has changed - copying list of '
            'installed tars']
        self.assertEqual(logs, self.handler.messages['info'])

    def test_perform_task(self):
        todos = self.manager.get_list_of_tasks()

        # Perform 1 installation
        self.manager.perform_task(todos[0])
        logs = [
            'Need to fix the links for slot1 1235',
            'Updating slot1 1235 centos7_x64_opt',
            'Invoking: lbn-install --dest=/tmp/toto/cvmfstest.cern.ch/'
            'nightlies/slot1/1235 --platforms=centos7_x64_opt slot1 1235',
            'Install has changed - copying list of installed tars']
        self.assertEqual(logs, self.handler.messages['info'])
        self.handler.messages['info'] = []
        # Perform the same installation, should fail
        self.assertRaises(Exception, self.manager.perform_task, todos[0])
        logs = [
            'Updating slot1 1235 centos7_x64_opt',
            'Invoking: lbn-install --dest=/tmp/toto/cvmfstest.cern.ch/'
            'nightlies/slot1/1235 --platforms=centos7_x64_opt slot1 1235',
            'No new files to install - aborting transaction']
        self.assertEqual(logs, self.handler.messages['info'])

    def test_lbn_install_call(self):
        todos = self.manager.get_list_of_tasks()

        # Perform 1 installation with error
        self.mocked_return_code = 1
        self.manager.perform_task(todos[0])
        logs = [
            'Need to fix the links for slot1 1235',
            'Updating slot1 1235 centos7_x64_opt',
            'Invoking: lbn-install --dest=/tmp/toto/cvmfstest.cern.ch/'
            'nightlies/slot1/1235 --platforms=centos7_x64_opt slot1 1235',
            'Installation problem. Ignoring to avoid transaction rollback',
            'Install has changed - copying list of installed tars']
        self.assertEqual(sorted(logs),
                         sorted(self.handler.messages['info']))
        values = " ".join(str(v) for v in self.args[0])
        self.assertEqual(values,
                         'lbn-install --dest=/tmp/toto/cvmfstest.cern.ch/'
                         'nightlies/slot1/1235 --platforms=centos7_x64_opt '
                         'slot1 1235')

if __name__ == "__main__":
    unittest.main()
