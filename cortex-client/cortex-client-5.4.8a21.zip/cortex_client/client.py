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
from functools import lru_cache
from typing import Dict, TypeVar, Type, Optional

import requests
from cortex_client.utils import current_cortex_cli_profile_config

from .serviceconnector import ServiceConnector
from .types import InputMessage, JSONType
from .utils import get_logger

log = get_logger(__name__)


T = TypeVar('T', bound='_Client')


class _Client:
    """
    A client.
    """

    URIs = {} # type: Dict[str, str]

    def __init__(self, url, version, token):
        self._serviceconnector = ServiceConnector(url, version, token)

    def _post_json(self, uri, obj: JSONType):
        body_s = json.dumps(obj)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, body_s, headers)
        if r.status_code != requests.codes.ok:
            log.info(r.text)
        r.raise_for_status()
        return r.json()

    def _get_json(self, uri):
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.json()

    def _request_json(self, uri, method='GET'):
        r = self._serviceconnector.request(method, uri)
        r.raise_for_status()
        return r.json()

    @classmethod
    @lru_cache(maxsize=100)
    def from_current_cli_profile(cls: Type[T], version:str="3", **kwargs) -> Optional[T]:
        cli_cfg = current_cortex_cli_profile_config()
        url, token = cli_cfg["url"], cli_cfg["token"]
        return cls(url, version, token, **kwargs)

    @classmethod
    def from_cortex_message(cls, message, version:str="3", **kwargs):
        return cls(message["apiEndpoint"], version, message["token"], **kwargs)


def build_client(type, input_message: InputMessage, version):
    """
    Builds a client.
    """
    return type(input_message.api_endpoint, version, input_message.token)
