# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fake_ubersmith.api.base import Base
from fake_ubersmith.api.ubersmith import FakeUbersmithError
from fake_ubersmith.api.utils.response import response
from fake_ubersmith.api.utils.utils import a_random_id


class Client(Base):
    def __init__(self, data_store):
        super().__init__(data_store)

        self.credit_card_response = 1
        self.credit_card_delete_response = True

    def hook_to(self, entity):
        entity.register_endpoints(
            ubersmith_method='client.cc_add',
            function=self.client_cc_add
        )
        entity.register_endpoints(
            ubersmith_method='client.cc_update',
            function=self.client_cc_update
        )
        entity.register_endpoints(
            ubersmith_method='client.cc_info',
            function=self.client_cc_info
        )
        entity.register_endpoints(
            ubersmith_method='client.cc_delete',
            function=self.client_cc_delete
        )
        entity.register_endpoints(
            ubersmith_method='client.get',
            function=self.client_get
        )
        entity.register_endpoints(
            ubersmith_method='client.add',
            function=self.client_add
        )
        entity.register_endpoints(
            ubersmith_method='client.update',
            function=self.client_update
        )
        entity.register_endpoints(
            ubersmith_method='client.contact_add',
            function=self.contact_add
        )
        entity.register_endpoints(
            ubersmith_method='client.contact_get',
            function=self.contact_get
        )
        entity.register_endpoints(
            ubersmith_method='client.contact_list',
            function=self.contact_list
        )
        entity.register_endpoints(
            ubersmith_method='client.contact_update',
            function=self.contact_update
        )

    def client_add(self, form_data):
        client_id = str(a_random_id())

        client_data = form_data.copy()
        client_data["clientid"] = client_id
        client_data["contact_id"] = str(0)

        if client_data.get("uber_login"):
            client_data["login"] = client_data.get("uber_login")
            del client_data["uber_login"]

        self.logger.info("Adding client data: {}".format(client_data))

        self.data_store.clients.append(client_data)
        self.contact_add(
            dict(
                client_id=client_id,
                description="Primary Contact",
                login="so_much_invalid_username",
                password="so_much_invalid_password"
            )
        )

        return response(data=client_id)

    def client_update(self, form_data):
        client_id = form_data.get("client_id")

        client = next(iter(filter(lambda e: e["clientid"] == client_id, self.data_store.clients)))
        self.logger.info("Updating client {} with {}".format(client["clientid"], form_data))

        self._update_if_present(client, "first", form_data, "first")
        self._update_if_present(client, "last", form_data, "last")
        self._update_if_present(client, "email", form_data, "email")
        self._update_if_present(client, "login", form_data, "uber_login")

        return response(data=True)

    def client_get(self, form_data):
        client_id = form_data.get("client_id") or form_data.get("user_login")
        client = self._client_get(client_id)
        if client is not None:
            client.pop("contact_id")
            if "uber_pass" in client:
                client.pop("uber_pass")
            if form_data.get("acls") == "1":
                client["acls"] = []

            self.logger.info("client data being returned {}".format(client))
            return response(data=client)
        else:
            self.logger.info("Can't find client ID - {}".format(client_id))
            return response(
                error_code=1,
                message="Client ID '{}' not found.".format(client_id)
            )

    def _client_get(self, client_id):
        client = next(
            (
                _format_client_get(client.copy()) for client in self.data_store.clients
                if client["clientid"] == client_id
            ),
            None
        )
        return client

    def contact_add(self, form_data):
        contact_id = str(a_random_id())

        contact_data = form_data.copy()
        contact_data["contact_id"] = contact_id
        self.data_store.contacts.append(contact_data)

        self.logger.info("Contact info added: {}".format(contact_data))

        return response(data=contact_id)

    def contact_get(self, form_data):
        if "user_login" in form_data:
            self.logger.info("Looking up contact info by user_login")
            return self._get_contact_response(
                "login", 'user_login', form_data['user_login']
            )
        elif "contact_id" in form_data:
            self.logger.info("Looking up contact info by contact_id")
            return self._get_contact_response(
                "contact_id", 'contact_id', form_data['contact_id']
            )

        self.logger.error("No valid user_login or contact_id specified")
        return response(error_code=1, message="No contact ID specified")

    def contact_list(self, form_data):
        if "client_id" in form_data:
            self.logger.info("Retrieving contact list by client_id")
            return self._get_all_contacts_response(
                "client_id", 'client_id', form_data['client_id']
            )

        self.logger.error("No valid client_id specified")
        return response(error_code=1, message="No valid client ID specified")

    def contact_update(self, form_data):
        contact_id = form_data.get("contact_id")

        contact = next(iter(filter(lambda e: e["contact_id"] == contact_id, self.data_store.contacts)))
        self.logger.info("Updating contact {} with {}".format(contact["contact_id"], form_data))

        self._update_if_present(contact, "real_name", form_data, "real_name")
        self._update_if_present(contact, "description", form_data, "description")
        self._update_if_present(contact, "phone", form_data, "phone")
        self._update_if_present(contact, "email", form_data, "email")
        self._update_if_present(contact, "login", form_data, "login")
        self._update_if_present(contact, "password", form_data, "password")

        return response(data=True)

    def client_cc_add(self, form_data):
        if isinstance(self.credit_card_response, FakeUbersmithError):
            return response(
                error_code=self.credit_card_response.code,
                message=self.credit_card_response.message
            )
        return response(data=self.credit_card_response)

    def client_cc_update(self, form_data):
        if isinstance(self.credit_card_response, FakeUbersmithError):
            return response(
                error_code=self.credit_card_response.code,
                message=self.credit_card_response.message
            )
        return response(data=True)

    def client_cc_info(self, form_data):
        # returns no error if providing parameters, only an empty list
        if "billing_info_id" in form_data:
            return response(
                data={
                    cc["billing_info_id"]: cc
                    for cc in self.data_store.credit_cards
                    if cc["billing_info_id"] == form_data["billing_info_id"]
                }
            )
        elif "client_id" in form_data:
            return response(
                data={
                    cc["billing_info_id"]: cc
                    for cc in self.data_store.credit_cards
                    if cc["clientid"] == form_data["client_id"]
                }
            )
        else:
            return response(
                error_code=1,
                message="request failed: client_id parameter not supplied"
            )

    def client_cc_delete(self, form_data):
        if isinstance(self.credit_card_delete_response, FakeUbersmithError):
            return response(
                error_code=self.credit_card_delete_response.code,
                message=self.credit_card_delete_response.message
            )
        return response(data=True)

    def _get_all_contacts_response(self, lookup_key, matcher_key, matcher_value):
        contacts = {
            contact['contact_id']: contact
            for contact in self.data_store.contacts
            if contact[lookup_key] == matcher_value
        }

        return response(data=contacts) if contacts else response(
            error_code=1, message="Invalid {} specified.".format(matcher_key)
        )

    def _get_contact_response(self, lookup_key, matcher_key, matcher_value):
        contact = next(
            (
                contact for contact in self.data_store.contacts
                if contact[lookup_key] == matcher_value
            ),
            None
        )
        if contact:
            client = self._client_get(contact["client_id"])

            self.logger.info("Getting contact info: {} for client {}".format(contact, client))

            return response(data=_format_contact_get(contact, client))
        else:
            return response(
                error_code=1, message="Invalid {} specified.".format(matcher_key)
            )

    def _update_if_present(self, target, target_key, source, source_key):
        try:
            value = source[source_key]
        except KeyError:
            return

        self.logger.debug("Setting {} to {}".format(target_key, value))
        target[target_key] = value


def _format_contact_get(contact, client):
    output = contact.copy()
    if "@" in output.get("email", ""):
        email_fields = output["email"].split("@")
    else:
        email_fields = "", ""

    output["email_name"], output["email_domain"] = email_fields

    output["password"] = "{ssha1}whatver it's hashed"
    output["password_timeout"] = "0"
    output["password_changed"] = "1549657344"

    output["first"] = output.get("real_name", "")
    output["last"] = ""

    if client is not None:
        output["listed_company"] = client["listed_company"]

    return output


def _format_client_get(client):
    client["listed_company"] = client.get("company", "") \
                               or "{}, {}".format(client.get("last", ""), client.get("first", ""))
    return client
