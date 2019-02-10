# -*- coding: ISO-8859-1 -*-
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
Created on 23 juil. 2017

@author: jeanluc
'''
import sys
from ..run import nn_gm_run
nn_gm_run.run(sys.argv)


# from metaphor.monal.util.monaltoolbox import yesNoQuestion
# from metaphor import chem_gm
# from metaphor.chem_gm.api.run.nn_gm_run import runOnce
# import sys, os
# 
# res = runOnce(sys.argv)
# if isinstance(res, tuple) and len(res) >= 2:
#     options = res[0]
#     argname = res[1]
#     if argname and os.path.exists(argname):
#         mess = "do you want to run the new project ?"
#         if yesNoQuestion(mess, default="y", outfile=sys.stdout, 
#             forceyes=options.yesyes):  #, verbose=verbose)
#             argumentfile = "@{0}".format(argname)
#             res = runOnce(["", argumentfile], options)
# print("nn_gm_run Done")