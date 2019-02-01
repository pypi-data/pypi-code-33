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

import requests

from .types import OutputEnv, PatchEnv, ContainerData
from .errors import ClientError


class Env(object):
    """
    Instance represents a live xenvman environment
    """

    def __init__(self, out_env: OutputEnv, server_address: str):
        self.out_env = out_env
        self.server_address = server_address

    def id(self):
        """
        Return environment id
        """

        return self.out_env.id

    def external_address(self) -> str:
        """
        Return external address
        """

        return self.out_env.external_address

    def get_container(self, tpl_name: str, tpl_idx: int,
                      cont_name: str) -> ContainerData:
        """
        Return container definition

        :param tpl_name: Template name
        :param tpl_idx: Template index
        :param cont_name: Container name
        """

        return self.out_env.get_container(tpl_name, tpl_idx, cont_name)

    def terminate(self):
        """
        Terminate/delete environment

        :raises: ClientError
        """

        url = "{}/api/v1/env/{}".format(self.server_address, self.out_env.id)

        r = requests.delete(url)

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))

    def patch(self, patch: PatchEnv):
        """
        Patch environment

        :raises: ClientError
        """

        url = "{}/api/v1/env/{}".format(self.server_address, self.out_env.id)

        r = requests.patch(url, json=patch.to_json())

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))

        out_env = OutputEnv.from_json(r.json()["data"])

        self.out_env = out_env

    def keepalive(self):
        """
        Send a keepalive message
        """

        url = "{}/api/v1/env/{}/keepalive".format(self.server_address,
                                                  self.out_env.id)

        r = requests.post(url)

        if r.status_code != 200:
            raise ClientError("Unexpected HTTP response {}: {}".format(
                r.status_code, r.reason
            ))
