# **************************************************************************
# *
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk)
# *
# * MRC Laboratory of Molecular Biology (MRC-LMB)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import pyworkflow.em
from pyworkflow.utils import Environ

from cryoef.constants import CRYOEF_HOME, V1_1_0

_logo = "cryoEF_logo.png"
_references = ['Naydenova2017']


class Plugin(pyworkflow.em.Plugin):
    _homeVar = CRYOEF_HOME
    _pathVars = [CRYOEF_HOME]
    _supportedVersions = [V1_1_0]

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(CRYOEF_HOME, 'cryoEF-1.1.0')

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch cryoEF. """
        environ = Environ(os.environ)
        environ.update({'PATH': cls.getHome('bin')}, position=Environ.BEGIN)
        return environ

    @classmethod
    def getProgram(cls):
        """ Return the program binary that will be used. """
        cmd = cls.getHome('bin', 'cryoEF')
        return str(cmd)

    @classmethod
    def defineBinaries(cls, env):
        env.addPackage('cryoEF', version='1.1.0',
                       tar='cryoEF_v1.1.0.tgz',
                       default=True)

pyworkflow.em.Domain.registerPlugin(__name__)
