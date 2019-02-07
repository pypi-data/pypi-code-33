# -*- coding: utf-8 -*-
# copyright 2018 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os.path
import shutil

import celery
from cubicweb import ConfigurationError
from cubicweb.devtools import testlib
from cubicweb_celerytask.hooks import CeleryTaskStartupHook


class CeleryTaskStartupHookTC(testlib.CubicWebTC):

    def test_create_log_dir(self):
        """hook should set a celerytask-log-dir by default and create it"""
        logdir = self.config['celerytask-log-dir']
        self.assertEqual(
            self.config['celerytask-log-dir'],
            os.path.join(self.config.appdatahome, 'logs'))
        shutil.rmtree(logdir, ignore_errors=True)
        CeleryTaskStartupHook.setup_celerytask_logdir(self.config)
        self.assertTrue(os.path.isdir(logdir))

    def test_celeryconfig_log_dir(self):
        """when CUBICWEB_CELERYTASK_LOGDIR is set in celeryconfig and no
        celerytask-log-dir is set we must use value from
        CUBICWEB_CELERYTASK_LOGDIR"""
        conf = celery.current_app.conf
        logdir = os.path.join(self.config.appdatahome, 'testhook')
        old = (self.config['celerytask-log-dir'],
               conf['CUBICWEB_CELERYTASK_LOGDIR'])
        (self.config['celerytask-log-dir'],
         conf['CUBICWEB_CELERYTASK_LOGDIR']) = None, logdir
        try:
            CeleryTaskStartupHook.setup_celerytask_logdir(self.config)
            self.assertEqual(self.config['celerytask-log-dir'], logdir)
        finally:
            (self.config['celerytask-log-dir'],
             conf['CUBICWEB_CELERYTASK_LOGDIR']) = old
            os.rmdir(logdir)

    def test_mismatching_dirs(self):
        """hook should raise in case os mistmaching configuration"""
        conf = celery.current_app.conf
        old = conf['CUBICWEB_CELERYTASK_LOGDIR']
        conf['CUBICWEB_CELERYTASK_LOGDIR'] = '/some/dir'
        try:
            with self.assertRaises(ConfigurationError) as cm:
                CeleryTaskStartupHook.setup_celerytask_logdir(self.config)
            self.assertIn('You misconfigured your application',
                          str(cm.exception))
        finally:
            conf['CUBICWEB_CELERYTASK_LOGDIR'] = old
