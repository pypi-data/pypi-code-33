
# Copyright 2018 ReactiveOps

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
from pentagon.component import ComponentBase
from monitor import Monitor, Monitors
from dashboard import Dashboard, Dashboards


class Datadog(ComponentBase):
    _environment = [{'aws_region': 'AWS_DEFAULT_REGION'}, 'infrastructure_bucket']
    _defaults = {'backend': 'datadog/tf.state'}

    def add(self, destination):
        super(Datadog, self).add(destination, overwrite=True)
        os.remove("{}/monitor.tf".format(self._destination_directory_name))
        os.remove("{}/dashboard.tf".format(self._destination_directory_name))
