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
import re

import collections

from fake_ubersmith.api.base import Base
from fake_ubersmith.api.utils.response import response
from fake_ubersmith.api.utils.utils import a_random_id


class IWeb(Base):
    def __init__(self, data_store):
        super().__init__(data_store)

    def hook_to(self, entity):
        entity.register_endpoints(
            ubersmith_method='iweb.log_event',
            function=self.log_event
        )
        entity.register_endpoints(
            ubersmith_method='iweb.acl_admin_role_add',
            function=self.acl_admin_role_add
        )
        entity.register_endpoints(
            ubersmith_method='iweb.user_role_assign',
            function=self.user_role_assign
        )

    def log_event(self, form_data):
        self.data_store.event_log.append(form_data.to_dict())
        return response(data="1")

    def acl_admin_role_add(self, form_data):
        if self._does_role_name_exist(form_data.get('name')):
            return response(
                error_code=1,
                message="The specified Role Name is already in use"
            )

        role_id = str(a_random_id())
        role_data = {}
        acls = collections.defaultdict(dict)
        for key, value in form_data.to_dict().items():
            if 'acls' in key:
                rule, level = list(filter(None, re.split(r"\[|\]", key)))[1:]
                acls[rule][level] = value
            else:
                role_data[key] = value
        role_data.update({'role_id': role_id, 'acls': acls})

        self.data_store.roles[role_id] = role_data
        return response(data=role_id)

    def _does_role_name_exist(self, role_name):
        return any(
            role_name == data['name']
            for _, data in self.data_store.roles.items()
        )

    def user_role_assign(self, form_data):
        user_id = form_data.get('user_id')
        role_id = str(form_data.get('role_id'))
        roles = self.data_store.user_mapping.get(user_id, {}).get('roles', {})
        if role_id in roles:
            return response(
                error_code=1,
                message="Can't assign role with id '{}' "
                        "to user with id '{}'".format(role_id, user_id)
            )
        self.data_store.user_mapping[user_id]['roles'].add(role_id)
        return response(data=1)
