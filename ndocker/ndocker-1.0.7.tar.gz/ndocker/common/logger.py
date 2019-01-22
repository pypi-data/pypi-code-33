# Copyright (C) 2018  Sean Z <sean.z.ealous@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import logging.handlers

logger = logging.getLogger('ndocker')
if len(logger.handlers) == 0:
    # create console handler and set level
    handler = logging.StreamHandler()
    logger.setLevel(logging.ERROR)

    # create formatter
    formatter = logging.Formatter("%(asctime)s %(filename)s:%(lineno)d [%(levelname)s]: %(message)s", '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

debug = logger.debug
info = logger.info
warning = logger.warn
error = logger.error
critical = logger.critical
