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

"""
Parsers for command outputs.
"""

def line_parser(buf):
    """
    Parses the given `buf` as str representation of list of values
    (e.g. 'ovs-vsctl list-br' command or 'docker ps' command).

    :param buf: str type value containing values list.
    :return:  list of parsed values.
    """
    values = []
    for line in buf.split('\n'):
        if line:
            values.append(line.strip())
    return values
