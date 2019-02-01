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
from collections import defaultdict


class DataStore:
    def __init__(self):
        self.credit_cards = []
        self.countries = {}
        self.clients = []
        self.contacts = []
        self.coupons = []
        self.order = {}
        self.order_submit = {}
        self.order_cancel = {}
        self.service_plans = []
        self.service_plans_list = None
        self.event_log = []
        self.roles = {}
        self.acl_resources = {}
        self.acl_resources_inc_id = 0
        self.user_mapping = defaultdict(lambda: defaultdict(set))

    def flush(self):
        self.__init__()
