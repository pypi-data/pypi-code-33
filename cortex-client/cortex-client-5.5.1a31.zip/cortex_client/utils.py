"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
import logging
from pathlib import Path


def get_logger(name):
    """
    Gets a logger with the given name.
    """
    log = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s/%(module)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log

def json_str(val):
    """
    Get the string representation of a json object.
    """
    try:
        return json.dumps(val)
    except TypeError:
        return str(val)


def current_cortex_cli_profile_config(cortex_config_path="{}/.cortex/config".format(Path.home())):
    # TODO Make the path configurable to cortex config
    cortex_config_file = Path(cortex_config_path)
    if not cortex_config_file.is_file():
        return None
    cortex_config = json.loads(cortex_config_file.read_bytes().decode('utf-8'))
    current_profile = cortex_config["currentProfile"]
    current_profile_config = cortex_config["profiles"][current_profile]
    return current_profile_config