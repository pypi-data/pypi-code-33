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

import json

from flask import make_response


def response(data="", error_code=None, message=""):
    r = json.dumps({
        "status": False if error_code else True,
        "error_code": error_code,
        "error_message": message,
        "data": _phpize_empty_dict_to_arrays(data)
    })
    return make_response((r, 200, {'Content-Type': 'application/json'}))


def _phpize_empty_dict_to_arrays(data):
    if isinstance(data, dict):
        if len(data) == 0:
            return []
        return {k: _phpize_empty_dict_to_arrays(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_phpize_empty_dict_to_arrays(v) for v in data]
    else:
        return data
