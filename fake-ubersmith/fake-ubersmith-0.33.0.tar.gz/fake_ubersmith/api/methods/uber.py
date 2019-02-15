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


class Uber(Base):
    def __init__(self, data_store):
        super().__init__(data_store)
        self.service_plan_error = None

    def hook_to(self, entity):
        entity.register_endpoints(
            ubersmith_method='uber.service_plan_get',
            function=self.service_plan_get
        )
        entity.register_endpoints(
            ubersmith_method='uber.service_plan_list',
            function=self.service_plan_list
        )
        entity.register_endpoints(
            ubersmith_method='uber.check_login',
            function=self.check_login
        )
        entity.register_endpoints(
            ubersmith_method='uber.acl_admin_role_get',
            function=self.acl_admin_role_get
        )
        entity.register_endpoints(
            ubersmith_method='uber.acl_resource_add',
            function=self.acl_resource_add
        )
        entity.register_endpoints(
            ubersmith_method='uber.acl_resource_list',
            function=self.acl_resource_list
        )

    def check_login(self, form_data):
        data = self._get_login_info(form_data['login'], form_data['pass'])

        if data:

            self.logger.info("Login successful. Client info: {}".format(data))
            return response(data=data)

        self.logger.error("Login failed")

        return response(
            error_code=3, message="Invalid login or password."
        )

    def service_plan_get(self, form_data):
        if isinstance(self.service_plan_error, FakeUbersmithError):
            self.logger.info("Error retrieving service plan")
            return response(
                error_code=self.service_plan_error.code,
                message=self.service_plan_error.message
            )

        service_plan = next(
            (
                plan for plan in self.data_store.service_plans
                if plan["plan_id"] == form_data["plan_id"]
            ),
            None
        )

        if service_plan is not None:
            self.logger.info("Service plan found: {}".format(service_plan))
            return response(data=service_plan)
        else:
            self.logger.error("Service plan not found.")
            return response(
                error_code=3,
                message="No Service Plan found"
            )

    def service_plan_list(self, form_data):
        if 'code' in form_data:
            plan_code = form_data['code']
            self.logger.info("Getting service plans for code: {}".format(
                plan_code
            ))
            return response(
                data={
                    plan['plan_id']: plan
                    for plan in self.data_store.service_plans_list.values()
                    if plan['code'] == plan_code
                }
            )
        self.logger.info("Plan not found by code. Listing all plans")
        return response(data=self.data_store.service_plans_list)

    def acl_admin_role_get(self, form_data):
        user_id = form_data.get('userid')
        role_id = str(form_data.get('role_id', ''))

        if not role_id:
            return response(
                error_code=1,
                message="role_id parameter not specified"
            )

        if user_id:
            self.logger.info(user_id)
            self.logger.info(self.data_store.user_mapping)
            self.logger.info(self.data_store.roles)
            self.logger.info(self.data_store.user_mapping.get(user_id, {}))
            role_ids = self.data_store.user_mapping.get(user_id, {}).get(
                'roles'
            )

            self.logger.info(role_ids)

            if not role_ids:
                return response(error_code=1, message="No User Roles found")

            return response(data={
                role_id: self.data_store.roles.get(role_id)
                for role_id in role_ids
            })

        role_data = self.data_store.roles.get(role_id)

        if not role_data:
            return response(error_code=1, message="No User Roles found")

        return response(data=role_data)

    def acl_resource_add(self, form_data):
        parent_resource_name = form_data.get('parent_resource_name', '')
        resource_name = form_data.get('resource_name', '')
        label = form_data.get('label', '')
        actions = form_data.get('actions', 'create,read,update,delete')

        self.logger.info("Adding role {}; {}; {}; {}".format(parent_resource_name, resource_name, label, actions))

        if not parent_resource_name:
            parent_resource_id = "0"
            target_resource_dict = self.data_store.acl_resources
        else:
            parent_resource = self._find_acl_parent(self.data_store.acl_resources, parent_resource_name)

            if parent_resource is None:
                return response(error_code=1, message="Resource [{}] not found".format(parent_resource_name))

            parent_resource_id = parent_resource["resource_id"]
            target_resource_dict = parent_resource["children"]

        self.data_store.acl_resources_inc_id += 1

        target_resource_dict[str(self.data_store.acl_resources_inc_id)] = {
            "resource_id": str(self.data_store.acl_resources_inc_id),
            "name": resource_name,
            "parent_id": parent_resource_id,
            "lft": "0",
            "rgt": "0",
            "active": "1",
            "label": label,
            "actions": self._to_acl_actions(actions),
            "children": {}
        }

        return response(data="")

    def acl_resource_list(self, _):
        return response(data=self.data_store.acl_resources)

    def _get_login_info(self, username, password):
        def _build_payload(id, client_id, contact_id, login, full_name, email, type):
            return {
                "id": id,
                "client_id": client_id,
                "contact_id": contact_id,
                "login": login,
                "fullname": full_name,
                "email": email,
                "type": type,
                'last_login': None,
                'password_changed': '1549380089',
                'password_timeout': '0',
            }

        def _get_contact():
            return next(
                (
                    _build_payload(
                        id="{}-{}".format(c["client_id"], c["contact_id"]),
                        client_id=c["client_id"],
                        contact_id=c["contact_id"],
                        login=c["login"],
                        full_name=c.get("real_name", ""),
                        email=c.get("email") or "@",
                        type="contact"
                    )
                    for c in self.data_store.contacts
                    if c['login'] == username and c['password'] == password
                ),
                None
            )

        return next(
            (
                _build_payload(
                    id=c['clientid'],
                    client_id=c['clientid'],
                    contact_id=0,
                    login=c["login"],
                    full_name=" ".join(filter(lambda e: e, [c.get("first"), c.get("last")])),
                    email=c.get("email", ""),
                    type="client"
                )
                for c in self.data_store.clients
                if c['login'] == username and c['uber_pass'] == password
            ),
            _get_contact()
        )

    def _find_acl_parent(self, resources, name):
        for resource in resources.values():
            if resource["name"] == name:
                return resource

            in_children = self._find_acl_parent(resource["children"], name)
            if in_children:
                return in_children

        return None

    def _to_acl_actions(self, actions_str):
        actions = {}
        for action in actions_str.split(","):
            actions.update(_ACL_ACTIONS_MAPPING[action])
        return actions


_ACL_ACTIONS_MAPPING = {
    "create": {"1": "Create", },
    "read": {"2": "View", },
    "update": {"3": "Update", },
    "delete": {"4": "Delete", }
}
