# MIT License
#
# Copyright (c) 2019 Max Kuznetsov <syhpoon@syhpoon.ca>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import requests

from .types import *
from .errors import ClientError
from .env import Env


class Client(object):
    """
    Client interface to xenvman server
    """

    def __init__(self, address: str = "http://localhost:9876"):
        """
        Server address can be overriden by env variable
        XENV_API_SERVER

        :param address: xenvman API server address
        """

        env_addr = os.getenv("XENV_API_SERVER")

        self.server_address = env_addr or address

        if self.server_address.endswith("/"):
            self.server_address = self.server_address[:-1]

    def new_env(self, input_env: InputEnv) -> Env:
        """
        Create a new environment

        :return: Environment instance
        :raises: ClientError
        """

        url = "{}/api/v1/env".format(self.server_address)

        r = requests.post(url, json=input_env.to_json())

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))

        out_env = OutputEnv.from_json(r.json()["data"])

        return Env(out_env, self.server_address)

    def list_envs(self) -> List[OutputEnv]:
        """
        Return list of active environments

        :raises: ClientError
        """

        url = "{}/api/v1/env".format(self.server_address)

        r = requests.get(url)

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))

        return [OutputEnv.from_json(x) for x in r.json()["data"]]

    def list_templates(self) -> Dict[str, TplInfo]:
        """
        Return available templates

        :raises: ClientError
        """

        url = "{}/api/v1/tpl".format(self.server_address)

        r = requests.get(url)

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))

        return {k: TplInfo.from_json(v) for k, v in r.json()["data"].items()}

    def get_env_info(self, id: str) -> OutputEnv:
        """
        Get info for a given environment id

        :param id: Environment id
        :return: Environment information
        :raises: ClientError
        """

        url = "{}/api/v1/env/{}".format(self.server_address, id)

        r = requests.get(url)

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))

        return OutputEnv.from_json(r.json()["data"])
