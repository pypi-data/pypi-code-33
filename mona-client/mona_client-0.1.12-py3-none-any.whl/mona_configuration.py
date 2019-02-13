# ----------------------------------------------------------------------------
#    Copyright 2018 MonaLabs.io
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ----------------------------------------------------------------------------
"""
Module in charge of providing updated configurations for the Mona client
according to a given configuration file under the env var
MONA_CLIENT_CONFIG_FILE.
"""
import atexit
import json
import os
import sys

import pkg_resources
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .logger import LOGGER

_MONA_CLIENT_CONFIG_FILE_PATH = os.environ.get(
    'MONA_CLIENT_CONFIG_FILE') or pkg_resources.resource_filename(
        'mona_client', 'config/mona_client_config.json')

DEFAULT_CONFIGURATION = {'disable_all': False}

configuration = {}


def _read_config_file():
    # TODO(itai): Consider getting host and port from config file as well.
    # Might not be something we want to enable (changing host and port during
    # run).
    LOGGER.info('Updating mona configuration file.')

    configuration.update(DEFAULT_CONFIGURATION)
    try:
        with open(_MONA_CLIENT_CONFIG_FILE_PATH) as f:
            configuration.update(json.load(f))
    except Exception:
        LOGGER.warning("Couldn't read mona configuration file, using default "
                       "configuration")
    finally:
        LOGGER.info('New mona configuration: %s', str(configuration))


class _ConfigFileChangeHandler(PatternMatchingEventHandler):
    def __init__(self):
        super(_ConfigFileChangeHandler,
              self).__init__(patterns=[_MONA_CLIENT_CONFIG_FILE_PATH])

    def on_any_event(self, event):
        _read_config_file()


_read_config_file()

try:
    OBSERVER = Observer()
    OBSERVER.schedule(
        _ConfigFileChangeHandler(),
        os.path.split(_MONA_CLIENT_CONFIG_FILE_PATH)[0],
        recursive=True)
    OBSERVER.start()
    LOGGER.info("Started observing configuration file under: %s",
                _MONA_CLIENT_CONFIG_FILE_PATH)

    def _finish_observer():
        OBSERVER.stop()
        OBSERVER.join()

    atexit.register(_finish_observer)
except Exception:
    LOGGER.warning(
        """Exception when trying to observe changes in Mona configuration
        file: %s""", str(sys.exc_info))
