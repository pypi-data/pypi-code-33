# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ubersmith_client.exceptions import UbersmithException

from tests.integration.base import Base
from tests.utils import a_random_string


class TestVendorModulesIWeb(Base):
    def test_log_event(self):
        result = self.ub_client.iweb.log_event(
            event_type="ADMIN_CLIENT_EDITED",
            reference_type="client",
            action="A Message",
            clientid="123456",
            user="username",
            reference_id="123456"
        )

        self.assertEqual(result, "1")

    def test_add_admin_role_successfully(self):
        name = a_random_string()
        descr = a_random_string()

        role_id = self.ub_client.iweb.acl_admin_role_add(
            **{
                'name': name,
                'descr': descr,
                'acls[admin.portal][read]': 1
            }
        )

        role_result = self.ub_client.uber.acl_admin_role_get(role_id=role_id)

        self.assertEqual(
            role_result,
            {
                'role_id': role_id,
                'name': name,
                'descr': descr,
                'acls': {
                    'admin.portal': {'read': '1'}
                }
            }
        )

    def test_assign_role_to_user_successfully(self):
        name = a_random_string()
        descr = a_random_string()

        role_id = self.ub_client.iweb.acl_admin_role_add(
            **{
                'name': name,
                'descr': descr,
                'acls[admin.portal][read]': 1
            }
        )

        self.ub_client.iweb.user_role_assign(
            user_id='some_user_id', role_id=role_id
        )

        role_result = self.ub_client.uber.acl_admin_role_get(
            userid='some_user_id',
            role_id=str(role_id)
        )

        self.assertEqual(
            role_result,
            {
                str(role_id): {
                    'role_id': str(role_id),
                    'name': name,
                    'descr': descr,
                    'acls': {
                        'admin.portal': {'read': '1'}
                    }
                }
            }
        )

    def test_assign_same_role_to_user_fails(self):
        user_id = 'some_user_id'
        name = a_random_string()
        descr = a_random_string()

        role_id = self.ub_client.iweb.acl_admin_role_add(
            **{
                'name': name,
                'descr': descr,
                'acls[admin.portal][read]': 1
            }
        )

        self.ub_client.iweb.user_role_assign(
            user_id=user_id, role_id=role_id
        )

        with self.assertRaises(UbersmithException) as e:
            self.ub_client.iweb.user_role_assign(
                user_id=user_id, role_id=role_id
            )

        self.assertEqual(
            e.exception.message,
            "Can't assign role with id '{}' to user with id '{}'".format(
                role_id, user_id
            )
        )
