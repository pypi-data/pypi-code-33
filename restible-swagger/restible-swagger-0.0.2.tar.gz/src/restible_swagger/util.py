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
""" Various general purpose utilities. """
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pygments
import pygments.lexers
import pygments.formatters
import yaml
from pygments.lexers.data import YamlLexer
from pygments.formatters.terminal256 import Terminal256Formatter


RESPONSE_401 = {
    "description": "User needs to sign in",
    "schema": {
        "type": "object",
        "properties": {
            "detail": {
                "type": "string",
                "example": "Login required",
            }
        }
    }
}


def make_name(*words):
    """ Build a SnakeCase name out of words. """
    import itertools

    words = itertools.chain.from_iterable(w.split() for w in words)

    return ''.join(w.lower().capitalize() for w in words)


def yaml_dumps(data):
    """ Dump data as a YAML string. """
    return yaml.safe_dump(data, default_flow_style=False)


def yaml_render(data):
    """ Render data as YAML with shell colors syntax highlighting"""
    yaml_str = yaml_dumps(data)
    print(pygments.highlight(
        yaml_str,
        YamlLexer(),
        Terminal256Formatter()
    ))


def yaml_write(data, path):
    """ Write data as YAML to the file under given path. """
    with open(path, 'w') as fp:
        fp.write(yaml_dumps(data))
