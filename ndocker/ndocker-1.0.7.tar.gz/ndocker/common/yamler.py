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

import yaml


class Yaml(object):
    def __init__(self, yaml_file):
        instream = file(yaml_file, 'r')
        self.__dict__ = yaml.safe_load(instream)

    @property
    def infos(self):
        return self.__dict__

    def update(self, **kwargs):
        if kwargs:
            self.__dict__.update(kwargs)

    def dump(self, to_path_file, flow_style=False):
        outstream = file(to_path_file, 'w')
        yaml.dump(self.__dict__, outstream, default_flow_style=flow_style)
        outstream.close()
