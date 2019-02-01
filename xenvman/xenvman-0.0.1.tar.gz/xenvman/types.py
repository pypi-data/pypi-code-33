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

from typing import List, Dict

from .errors import ClientError


class EnvOptions(object):
    """
    Environment options
    """

    @staticmethod
    def from_json(data):
        return EnvOptions(data.get("keep_alive", "2m"),
                          data.get("disable_discovery", False))

    def to_json(self):
        return {
            "keep_alive": self.keep_alive,
            "disable_discovery": self.disable_discovery,
        }

    def __init__(self,
                 keep_alive: str = "2m",
                 disable_discovery: bool = False):
        self.keep_alive = keep_alive
        self.disable_discovery = disable_discovery


class Tpl(object):
    """
    Template definition
    """

    @staticmethod
    def from_json(data):
        return Tpl(data["tpl"], data["parameters"])

    def to_json(self):
        return {
            "tpl": self.tpl,
            "parameters": self.parameters
        }

    def __init__(self, tpl: str, parameters: dict = None):
        self.tpl = tpl
        self.parameters = parameters or {}


class InputEnv(object):
    """
    Input environment definition
    """

    @staticmethod
    def from_json(data):
        opts = None

        if "options" in data:
            opts = EnvOptions.from_json(data["options"])

        return InputEnv(
            data["name"],
            data.get("description", ""),
            [Tpl.from_json(x) for x in data.get("templates", [])],
            opts)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "templates": [x.to_json() for x in self.templates],
            "options": self.options.to_json() if self.options else None
        }

    def __init__(self, name: str,
                 description: str = "",
                 templates: List[Tpl] = None,
                 options: EnvOptions = None):
        self.name = name
        self.description = description
        self.templates = templates or []
        self.options = options


class ContainerData(object):
    """
    Container data and ports mapping
    """

    @staticmethod
    def from_json(data):
        return ContainerData(
            data["id"],
            data["hostname"],
            data["ports"]
        )

    def __init__(self,
                 id: str,
                 hostname: str,
                 ports: Dict[str, int]):
        self.id = id
        self.hostname = hostname
        self.ports = ports


class TplData(object):
    @staticmethod
    def from_json(data):
        return TplData({k: ContainerData.from_json(v)
                        for k, v in data["containers"].items()})

    def __init__(self, containers: Dict[str, ContainerData]):
        self.containers = containers


class OutputEnv(object):
    """
    Output environment definition
    """

    @staticmethod
    def from_json(data):
        return OutputEnv(
            data["id"],
            data.get("name", ""),
            data.get("description", ""),
            data.get("ws_dir", ""),
            data.get("mount_dir", ""),
            data.get("net_id", ""),
            data.get("created", ""),
            data.get("keep_alive", ""),
            data["external_address"],
            {k: [TplData.from_json(x) for x in v] for
             k, v in data["templates"].items()},
        )

    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 ws_dir: str,
                 mount_dir: str,
                 net_id: str,
                 created: str,
                 keep_alive: str,
                 external_address: str,
                 templates: Dict[str, List[TplData]]
                 ):
        self.id = id
        self.name = name
        self.description = description
        self.ws_dir = ws_dir
        self.mount_dir = mount_dir
        self.net_id = net_id
        self.created = created
        self.keep_alive = keep_alive
        self.external_address = external_address
        self.templates = templates

    def get_container(self, tpl_name: str, tpl_idx: int,
                      cont_name: str) -> ContainerData:
        """
        Return container definition

        :param tpl_name: Template name
        :param tpl_idx: Template index
        :param cont_name: Container name
        """

        if tpl_name not in self.templates:
            raise ClientError("Template not found: {}".format(tpl_name))

        tpls = self.templates[tpl_name]

        if tpl_idx >= len(tpls):
            raise ClientError("Template {} index {} not found".format(
                tpl_name, tpl_idx))

        cont = tpls[tpl_idx].containers.get(cont_name, None)

        if cont is None:
            raise ClientError("Container not found: {}".format(cont_name))

        return cont


class TplInfoParam(object):
    """
    Template parameter metadata
    """

    @staticmethod
    def from_json(data):
        return TplInfoParam(
            data.get("description", ""),
            data.get("type", ""),
            data.get("mandatory", False),
            data.get("default", None),
        )

    def __init__(self,
                 description: str,
                 type: str,
                 mandatory: bool,
                 default=None):
        self.description = description
        self.type = type
        self.mandatory = mandatory
        self.default = default


class TplInfo(object):
    """
    Template metadata
    """

    @staticmethod
    def from_json(data):
        return TplInfo(
            data.get("description", ""),
            {k: TplInfoParam.from_json(v) for k, v in
             data.get("parameters", {}).items()},
            data.get("data_dir", None) or []
        )

    def __init__(self,
                 description: str,
                 parameters: Dict[str, TplInfoParam],
                 data_dir: List[str]):
        self.description = description
        self.parameters = parameters
        self.data_dir = data_dir


class PatchEnv(object):
    """
    Patch
    """

    def __init__(self,
                 stop_containers: List[str] = None,
                 restart_containers: List[str] = None,
                 templates: List[Tpl] = None
                 ):
        self.stop_containers = stop_containers or []
        self.restart_containers = restart_containers or []
        self.templates = templates or []

    def to_json(self) -> dict:
        return {
            "stop_containers": self.stop_containers,
            "restart_containers": self.restart_containers,
            "templates": [x.to_json() for x in self.templates]
        }
