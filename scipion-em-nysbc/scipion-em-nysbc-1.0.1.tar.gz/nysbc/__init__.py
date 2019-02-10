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

_logo = "salk_logo.jpg"
_references = ['tan2017']

NYSBC_3DFSC_HOME = 'NYSBC_3DFSC_HOME'


class Plugin(pyworkflow.em.Plugin):
    _homeVar = NYSBC_3DFSC_HOME
    _pathVars = [NYSBC_3DFSC_HOME]
    _supportedVersions = ['2.5', '3.0']

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(NYSBC_3DFSC_HOME, 'nysbc3DFSC-2.5')

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch 3DFSC. """
        environ = Environ(os.environ)
        environ.update({'PATH': cls.getHome('ThreeDFSC')},
                       position=Environ.BEGIN)

        return environ

    @classmethod
    def getProgram(cls):
        """ Return the program binary that will be used. """
        cmd = cls.getHome('ThreeDFSC', 'ThreeDFSC_Start.py')
        return str(cmd)

    @classmethod
    def defineBinaries(cls, env):
        fsc_commands = [('./install.sh',
                         'IS_INSTALLED')]

        envPath = os.environ.get('PATH', "")  # keep path since conda likely in there
        installEnvVars = {'PATH': envPath} if envPath else None
        env.addPackage('nysbc3DFSC', version='2.5',
                       tar='nysbc3DFSC-2.5.tgz',
                       commands=fsc_commands,
                       neededProgs=['conda'],
                       default=True,
                       vars=installEnvVars)

        env.addPackage('nysbc3DFSC', version='3.0',
                       tar='nysbc3DFSC-3.0.tgz',
                       commands=fsc_commands,
                       neededProgs=['conda'],
                       vars=installEnvVars)


pyworkflow.em.Domain.registerPlugin(__name__)
