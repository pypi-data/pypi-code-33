# Copyright 2018 British Broadcasting Corporation
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

from nmosquery.common.routes import RoutesCommon

from nmosquery.v1_3.query import Query

class Routes(RoutesCommon):
    def __init__(self, logger, config):
        super(Routes, self).__init__(logger, config, "v1.3")
        self.query = Query(logger=logger)
