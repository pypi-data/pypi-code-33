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


class TestUbersmithClient(Base):
    def test_client_creation_works(self):
        client_id = self.ub_client.client.add(uber_login='username')

        result = self.ub_client.client.get(client_id=client_id)
        self.assertDictEqual(result, {'clientid': client_id, 'login': 'username', 'listed_company': ', '})

        result = self.ub_client.client.contact_list(client_id=client_id)

        contacts = list(result.values())

        self.assertEqual(contacts[0].get('client_id'), client_id)
        self.assertEqual(contacts[0].get('description'), 'Primary Contact')

    def test_list_all_contacts_works(self):
        self.ub_client.client.contact_add(client_id='1234')
        self.ub_client.client.contact_add(client_id='1234')
        self.ub_client.client.contact_add(client_id='1235')

        result = self.ub_client.client.contact_list(client_id='1234')
        contacts = list(result.values())

        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].get('client_id'), '1234')
        self.assertEqual(contacts[1].get('client_id'), '1234')

    def test_list_all_contacts_raises_if_client_id_not_found(self):
        with self.assertRaises(UbersmithException) as exc:
            self.ub_client.client.contact_list(client_id='1234')

        self.assertEqual(exc.exception.code, 1)
        self.assertEqual(exc.exception.message, 'Invalid client_id specified.')
