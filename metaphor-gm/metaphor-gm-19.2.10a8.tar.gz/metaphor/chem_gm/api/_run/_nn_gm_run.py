#! python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# $Id$
#
# Copyright 2016 Jean-Luc PLOIX
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
#-------------------------------------------------------------------------------
'''
Created on 19 déc. 2018

@author: jeanluc
'''

import sys

from metaphor.nn1.api.run import nn_run
from metaphor.nn1.api import _api_service as nn_api_service
from ...api import _api_service

#nn_run.createTrainigModule = _api_service.createTrainingModuleExtendedToGM
# nn_api_service.compute_transferBS = _api_service.compute_transferBS
# nn_api_service.singleCoreUsageAction = _api_service.singleCoreUsageActionGM
# nn_api_service.multiCoreUsageAction = _api_service.multiCoreUsageActionGM

def run(argv):
    if not "--caller" in argv:
        argv = argv + ["--caller", _api_service]
    nn_run.run(argv)

if __name__ == '__main__':
    run(sys.argv)
    print("Done")