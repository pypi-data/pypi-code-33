#!/usr/bin/env python
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

import sys
import subprocess

from . import xanity
from .setup_env import main as setup
from .initialize import main as initialize
from .constants import COMMANDS, ENV_COMMANDS
from .common import XanityNoProjectRootError

xanity._parse_args()

if xanity.action == COMMANDS.INIT:
    initialize()

elif xanity.action == COMMANDS.SETUP:
    xanity._orient()
    setup()

elif xanity.action in COMMANDS.RUN + COMMANDS.ANAL:
    xanity._orient()
    xanity._absolute_trigger()

elif xanity.action in COMMANDS.STATUS:
    xanity.report_status()

elif xanity.action in COMMANDS.ENV:
    if xanity.args.env_action in ENV_COMMANDS.REMOVE:
        print('removing conda env: {}...'.format(xanity.uuid))
        subprocess.check_call(['bash', '-lc', 'conda env remove -n {}'.format(xanity.uuid)])
        print('removed.')

elif xanity.action in dir(xanity):
    try:
        xanity._orient()
    except XanityNoProjectRootError:
        pass

    obj = getattr(xanity, xanity.action)

    if callable(obj):
        print(obj())
    else:
        print(obj)

raise SystemExit(0)
