# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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


from cubicweb.devtools import testlib
from cubicweb_celery import app, init_repo


class DefaultTC(testlib.CubicWebTC):
    def setUp(self):
        super(DefaultTC, self).setUp()
        app.cwrepo = init_repo(app.cwconfig)

    def test_cwtask(self):
        eid = app.tasks['newgroup'](u'test')
        with self.admin_access.cnx() as cnx:
            self.assertEqual(cnx.entity_from_eid(eid).name, u'test')

    def test_cnx(self):
        with self.admin_access.cnx() as cnx:
            user_eid = self.create_user(cnx, u'testuser',
                                        groups=('managers',)).eid
            admin_eid = cnx.find('CWUser', login=u'admin').one().eid
            cnx.commit()

        groups = {app.tasks['newgroup'](name, eid): name for name, eid in (
            (u'test_group_user', user_eid),
            (u'test_group_admin', admin_eid),
            (u'test_group_internal', -1),
        )}

        with self.admin_access.cnx() as cnx:
            for group_eid, expected_name in groups.items():
                self.assertEqual(cnx.entity_from_eid(group_eid).name,
                                 expected_name)

    def test_default_config(self):
        self.assertTrue(app.conf.enable_utc)
        self.assertEqual('Indian/Maldives',
                         app.conf.timezone)

    def test_propagate_exception_in_test_mode(self):
        # by default propagate exception
        with self.assertRaises(ValueError) as excinfo:
            app.tasks['newgroup'].delay(u'magic')
        self.assertEqual(str(excinfo.exception), 'Cannot add a magic group')

        app.conf.task_eager_propagates = False
        try:
            # should not raise
            app.tasks['newgroup'].delay(u'magic')
        finally:
            app.conf.task_eager_propagates = True


if __name__ == '__main__':
    import unittest
    unittest.main()
