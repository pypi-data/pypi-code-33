
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

import logging
import traceback

from pentagon_datadog.rodd import Rodd


class Monitor(Rodd):
    template_file_name = 'monitor.tf.jinja'
    _item_type = 'monitors'


class Monitors(Rodd):

    def add(self, destination, overwrite=False):
        logging.debug("Adding monitor .tf files")
        global_definitions = self._data.get('definitions', {})
        monitors = self._data.get('monitors', {})
        exceptions = self._data.get('exceptions', [])

        try:
            for monitor in monitors:
                logging.debug(monitor)
                m = Monitor(monitor)
                m._exceptions = exceptions
                m._global_definitions = global_definitions
                m.add(destination, overwrite=True)
        except TypeError, e:
            logging.debug(e)
            logging.debug(traceback.format_exc())
            logging.error("No monitors declared or no file argument passed.")
