# -*- coding: utf-8 -*-
# Copyright 2019 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" Main logic. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import os.path

# 3rd party imports
from . import util
from .route import Route


def extract_api_spec(config, out_dir):
    """ Create OpenAPI spec using the given configuration. """

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for url, route_info in config.items():
        route = Route.load(url, route_info)
        route_spec = route.build_spec()
        res_file = os.path.join(out_dir, route.res_cls.name + '.yaml')

        print("-- \x1b[32mWriting \x1b[34m{}\x1b[0m".format(res_file))
        util.yaml_write(route_spec, res_file)
