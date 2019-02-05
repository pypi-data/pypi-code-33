# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of pyspectre.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

__version__ = "0.1b10"  # this version is used as the definitive version for distribution
__author__ = "Barry Muldrey"
__copyright__ = "Copyright 2018"
__license__ = "GNU Affero GPL"
__maintainer__ = "Barry Muldrey"
__email__ = "barry@muldrey.net"
__status__ = "Alpha"
__credits__ = []

import os
import tempfile

avail_output_modes = ['psfbin', 'nutmeg', 'psfascii', 'decida']

default_spectre_binary = 'spectre'

default_rcfile = '$HOME/.spectre.rc'

default_spectre_env = (
    ('CDS_INST', '/opt/cadence'),
    ('MMSIMHOME', '$CDS_INST/mmsim141'),
    ('LD_LIBRARY_PATH', "$LD_LIBRARY_PATH:/usr/lib/x86_64-linux-gnu"
                        ":/usr/lib/x86_64-linux-gnu:/usr/lib:/usr/bin/gcc"),
    ('LD_LIBRARY_PATH', '$LD_LIBRARY_PATH:$MMSIMHOME/tools/bin:$MMSIMHOME/tools/lib/64bit'),
    ('CPATH', "/usr/include/`gcc -print-multiarch`"),
    ('CDS_AUTO_64BIT', 'ALL'),
    ('CDS_AUTO_32BIT', 'NONE'),
    ('CDS_LIC_FILE', '5280@ecelinsvcs.ece.gatech.edu'),
    ('CDS_LOAD_ENV', 'addCWD'),
    ('CDS_Netlisting_Mode', 'Analog'),
    ('CLS_CDSD_COMPATIBILITY_LOCKING', 'NO'),
    ('LANG', 'C'),
    ('OA_UNSUPPORTED_PLAT', 'linux_rhel40_gcc44x'),
    ('PATH', '$MMSIMHOME/bin:$MMSIMHOME/tools/bin/64bit:$MMSIMHOME/tools/dfII/bin:$MMSIMHOME/tools/bin:$PATH'),
)

tmp_path = tempfile.gettempdir()
pyspectre_path = os.path.join(tmp_path, 'pyspectre')

pyspectre_ahdl_lib = os.path.join(pyspectre_path, 'ahdl_lib')
pyspectre_sim_dir = os.path.join(pyspectre_path, 'simulation')
pyspectre_ckt_dir = os.path.join(pyspectre_path, 'circuits')

from .Pyspectre import Pyspectre, PwlInput, Circuit
from .Pyspectre import set_spectre_binary, set_spectre_env, set_rcfile
# from .server import run_batch

set_rcfile()
# set_spectre_env()
set_spectre_binary()
