# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Rattail Tempmon Settings
"""

from __future__ import unicode_literals, absolute_import

from rattail.settings import Setting


##############################
# TempMon
##############################

class rattail_tempmon_probe_default_critical_max_timeout(Setting):
    """
    Default value to be used as Critical High Timeout value, for any probe
    which does not have this timeout defined.
    """
    group = "TempMon"
    namespace = 'rattail_tempmon'
    name = 'probe.default.critical_max_timeout'
    data_type = int


class rattail_tempmon_probe_default_critical_min_timeout(Setting):
    """
    Default value to be used as Critical Low Timeout value, for any probe which
    does not have this timeout defined.
    """
    group = "TempMon"
    namespace = 'rattail_tempmon'
    name = 'probe.default.critical_min_timeout'
    data_type = int


class rattail_tempmon_probe_default_error_timeout(Setting):
    """
    Default value to be used as Error Timeout value, for any probe which does
    not have this timeout defined.
    """
    group = "TempMon"
    namespace = 'rattail_tempmon'
    name = 'probe.default.error_timeout'
    data_type = int


class rattail_tempmon_probe_default_good_max_timeout(Setting):
    """
    Default value to be used as High Timeout value, for any probe which does
    not have this timeout defined.
    """
    group = "TempMon"
    namespace = 'rattail_tempmon'
    name = 'probe.default.good_max_timeout'
    data_type = int


class rattail_tempmon_probe_default_good_min_timeout(Setting):
    """
    Default value to be used as Low Timeout value, for any probe which does not
    have this timeout defined.
    """
    group = "TempMon"
    namespace = 'rattail_tempmon'
    name = 'probe.default.good_min_timeout'
    data_type = int
