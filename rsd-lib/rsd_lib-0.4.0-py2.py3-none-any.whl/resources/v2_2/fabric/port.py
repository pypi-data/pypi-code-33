# Copyright 2019 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from rsd_lib.resources.v2_1.fabric import port as v2_1_port
from rsd_lib import utils as rsd_lib_utils

from sushy.resources import base

LOG = logging.getLogger(__name__)


class IntelRackScaleField(base.CompositeField):
    metrics = base.Field("Metrics",
                         adapter=rsd_lib_utils.get_resource_identity)


class OemField(base.CompositeField):
    intel_rackScale = IntelRackScaleField("Intel_RackScale")
    """The oem intel rack scale"""


class Port(v2_1_port.Port):
    oem = OemField("Oem")
    """The port oem"""
