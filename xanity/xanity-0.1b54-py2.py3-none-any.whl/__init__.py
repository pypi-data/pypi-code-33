# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of xanity.
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

__version__ = "0.1b54"            # this is the definitive version for distribution
__author__ = "Barry Muldrey"
__copyright__ = "Copyright 2018"
__license__ = "GNU Affero GPL"
__maintainer__ = "Barry Muldrey"
__email__ = "barry@muldrey.net"
__status__ = "Alpha"
__credits__ = []


import sys
import traceback
from .Xanity import Xanity
from .constants import ACTIVITIES
from .common import get_external_caller

thismodule = sys.modules[__name__]

# items_to_expose = [
#         'experiment_parameters',
#         'associated_experiments',
#         'log',
#         'save_variable',
#         'load_variable',
#         'analyze_this',
#         'load_checkpoint',
#         'save_checkpoint',
#         'persistent',
#         'report_status',
#         'run',
#         'find_recent_data',
#         'status',
#         'project_root',
#         'trials',
#         '_rcfile',
#         '_env_path',
#         'find_data',
#         'subdir',
# ]


# # def _log_and_get(item_name):
# #     if not _xanity.status.act_tags:
# #         _xanity._register_external_access(get_external_caller())
# #     return getattr(_xanity, item_name)
# #
# #
# # def _xanity_getter(item_name):
# #     if callable(getattr(_xanity, item_name)):
# #         return lambda *args, **kwargs: _log_and_get(item_name)(*args, **kwargs)
# #     else:
# #             return lambda: _log_and_get(item_name)
# #
# #
# # for fn in items_to_expose:
# #     setattr(thismodule, fn, _xanity_getter(fn))


def experiment_parameters(*args, **kwargs):
    return xanity.experiment_parameters(*args, **kwargs)


def associated_experiments(*args, **kwargs):
    return xanity.associated_experiments(*args, **kwargs)


def log(*args, **kwargs):
    return xanity.log(*args, **kwargs)


def save_variable(*args, **kwargs):
    return xanity.save_variable(*args, **kwargs)


def load_variable(*args, **kwargs):
    return xanity.load_variable(*args, **kwargs)


def analyze_this(*args, **kwargs):
    return xanity.analyze_this(*args, **kwargs)


def checkpoint(*args, **kwargs):
    return xanity.checkpoint(*args, **kwargs)


def load_checkpoint(checkpoint_name, variables=None, overwrite=False):
    return xanity.load_checkpoint(checkpoint_name, variables, overwrite)


def save_checkpoint(checkpoint_name, variables=None, cwd=True, overwrite=False):
    return xanity.save_checkpoint(checkpoint_name, variables, cwd, overwrite)


def persistent(*args, **kwargs):
    return xanity.persistent(*args, **kwargs)


def report_status(*args, **kwargs):
    return xanity.report_status(*args, **kwargs)


def run(*args, **kwargs):
    return xanity.run(*args, **kwargs)


def find_recent_data(*args, **kwargs):
    return xanity.find_recent_data(*args, **kwargs)


def status():
    return xanity.status


def project_root():
    return xanity.project_root


def trials(*args, **kwargs):
    return xanity.trials(*args, **kwargs)


# def _rcfile():
#     return xanity._rcfile


# def _env_path(*args, **kwargs):
#     return xanity._env_path


def find_data(*args, **kwargs):
    return xanity.find_data(*args, **kwargs)


def subdir(*args, **kwargs):
    return xanity.subdir(*args, **kwargs)


def shell_prelude(value=None):
    if value is None:
        return xanity.shell_prelude
    else:
        xanity.shell_prelude = value


def subprocess(call):
    return xanity.subprocess(call)


def interactive_session():
    return xanity._interactive_session()


if 'xanity' not in globals():

    # have to set placeholders because modules which import
    # xanity might have to be imported during the creation of the Xanity object

    xanity = Xanity()

    # # the following will replace the 'xanity' module with the _xanity object:

    # del sys.modules['xanity']
    # sys.modules['xanity'] = _xanity


run_id = str(xanity.run_id)
rcfile = str(xanity._rcfile)
env_path = str(xanity._env_path)

# check frame, register import, check_invocation
tb = traceback.extract_stack(limit=15)
for frame in tb:
    if 'import xanity' in frame[3]:
        xanity._register_import(frame[0])
        break


