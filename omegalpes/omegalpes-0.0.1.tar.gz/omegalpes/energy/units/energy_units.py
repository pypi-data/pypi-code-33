#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
** This module defines the energy units of OMEGALPES. The production,
consumption and storage unit will inherit from it. **

 The energy_units module defines the basic attributes and methods of an
 energy unit in OMEGALPES.
 It includes the following attributes and quantities:
 - p : instantaneous power of the energy unit (kW)
 - p_min : minimal power (kW)
 - p_max : maximal power (kW)
 - e_tot : total energy during the time period (kWh)
 - e_min : minimal energy of the unit (kWh)
 - e_max : maximal energy of the unit (kWh)
 - u : binary describing if the unit is operating or not at t (delivering or
 consuming P)

..

    Copyright 2018 G2ELab / MAGE

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from pulp import LpBinary

from ..io.poles import Epole
from ...general.optimisation.elements import Quantity, Constraint, \
    DynamicConstraint
from ...general.optimisation.units import Unit

__docformat__ = "restructuredtext en"


class EnergyUnit(Unit):
    """
        ** Description **
            Module dedicated to the parent class (EnergyUnit) of :
                - production units
                - consumption units
                - storage units
    """

    def __init__(self, time, name, flow_direction='in', p=None, p_min=-1e+5,
                 p_max=1e+5, e_min=-1e10, e_max=1e10, energy_type=None,
                 operator=None):

        Unit.__init__(self, name=name, description='Energy unit')

        self.parent = None
        self.time = time  # Time unit
        self.energy_type = energy_type
        self.operator = operator

        self.set_e_min = None
        self.set_e_max = None

        if isinstance(p_max, (int, float)):
            p_ub = max(0, p_max)  # Could be 0 when turn off
        elif isinstance(p_max, list):
            p_ub = [max(0, p) for p in p_max]  # Could be 0 when turn off

        if isinstance(p_min, (int, float)):
            p_lb = min(0, p_min)  # Could be 0 when turn off
        elif isinstance(p_min, list):
            p_lb = [min(0, p) for p in p_min]  # Could be 0 when turn off

        self.p = Quantity(name='p',
                          description='instantaneous power of the energy unit',
                          value=p, lb=p_lb, ub=p_ub, vlen=time.LEN, unit='kW',
                          parent=self)

        self.e_tot = Quantity(name='e_tot',
                              description='total energy during the time period',
                              lb=e_min, ub=e_max, vlen=1, unit='kWh',
                              parent=self)

        self.u = Quantity(name='u',
                          description='indicates if the unit is operating at t',
                          vtype=LpBinary, vlen=time.LEN, parent=self)

        # CONSTRAINTS
        if isinstance(p_max, (int, float)):
            self.on_off_max = DynamicConstraint(
                exp_t='{0}_p[t] <= {0}_u[t] * {p_M}'.format(self.name,
                                                            p_M=p_max),
                t_range='for t in time.I', name='on_off_max', parent=self)
        elif isinstance(p_max, list):
            self.on_off_max = DynamicConstraint(
                exp_t='{0}_p[t] <= {0}_u[t] * {p_M}[t]'.format(self.name,
                                                               p_M=p_max),
                t_range='for t in time.I', name='on_off_max', parent=self)

        if isinstance(p_min, (int, float)):
            self.on_off_min = DynamicConstraint(
                exp_t='{0}_p[t] >= {0}_u[t] * {p_m}'.format(self.name,
                                                            p_m=p_min),
                t_range='for t in time.I', name='on_off_min',
                parent=self)
        elif isinstance(p_min, list):
            self.on_off_min = DynamicConstraint(
                exp_t='{0}_p[t] >= {0}_u[t] * {p_m}[t]'.format(self.name,
                                                               p_m=p_min),
                t_range='for t in time.I', name='on_off_min',
                parent=self)

        self.calc_e_tot = Constraint(name='calc_e_tot', parent=self,
                                     exp='{0}_e_tot == time.DT * lpSum({0}_p[t]'
                                         ' for t in time.I)'.format(self.name))

        # Poles of the energy unit
        self.poles = {1: Epole(self.p, flow_direction, energy_type)}

    def set_energy_limits_on_time_period(self, e_min=0, e_max=None,
                                         start='YYYY-MM-DD HH:MM:SS',
                                         end='YYYY-MM-DD HH:MM:SS'):
        """

        :param e_min: Minimal energy set during the time period (int or float)
        :param e_max: Maximal energy set during the time period (int or float)
        :param start: Date of start of the time period  YYYY-MM-DD HH:MM:SS (
        str)
        :param end: Date of end of the time period   YYYY-MM-DD HH:MM:SS (str)
        """
        if start == 'YYYY-MM-DD HH:MM:SS':
            index_start = ''
        else:
            index_start = self.time.get_index_for_date(start)

        if end == 'YYYY-MM-DD HH:MM:SS':
            index_end = ''
        else:
            index_end = self.time.get_index_for_date(end)

        period_index = 'time.I[{start}:{end}]'.format(start=index_start,
                                                      end=index_end)

        if e_min != 0:
            self.set_e_min = Constraint(
                exp='time.DT * lpSum({0}_p[t] for t in {1}) '
                    '>= {2}'.format(self.name, period_index, e_min),
                name='set_e_min')

        if e_max is not None:
            self.set_e_max = Constraint(
                exp='time.DT * lpSum({0}_p[t] for t in {1}) '
                    '<= {2}'.format(self.name, period_index, e_max),
                name='set_e_max')
