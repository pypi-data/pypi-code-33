#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
** This module defines the consumption units**

 The consumption_units module defines various classes of consumption units,
 from generic to specific ones.

 It includes :
    - ConsumptionUnit : simple consumption unit. It inherits from EnergyUnit,
      its power flow direction is always 'in'.
        3 Objectives are also available :
            * minimize consumption, maximize consumption and minimize
            consumption costs.

    - FixedConsumptionUnit :  consumption with a fixed load profile. It
      inherits from ConsumptionUnit.

    - VariableConsumptionUnit : consumption unit allowing for a variation of
      power between pmin et pmax. It inherits from ConsumptionUnit.
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
from .energy_units import EnergyUnit
from ...general.optimisation.elements import Objective, Quantity, \
    Constraint, DynamicConstraint

__docformat__ = "restructuredtext en"


class ConsumptionUnit(EnergyUnit):
    """
    **Description**
        Simple Consumption unit

    **Attributes**

        * p : instantaneous power demand (kW)
        * pmax : maximal instantaneous power demand (kW)
        * pmin : minimal instantaneous power demand (kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * consumption_cost : cost associated to the energy consumption
        * operator : stakeholder how owns the consumption unit
    """

    def __init__(self, time, name, p_min=1e-5, p_max=1e+5, p=None,
                 energy_type=None, consumption_cost=None, operator=None):
        EnergyUnit.__init__(self, time, name=name, flow_direction='in', p=p,
                            p_min=p_min, e_min=0, p_max=p_max,
                            energy_type=energy_type, operator=operator)

        # No objective when initialized
        self.min_consumption = None
        self.max_consumption = None
        self.min_consumption_cost = None

        self.consumption_cost = Quantity(name='consumption_cost',
                                         description='Dynamic cost for the '
                                                     'consumption of the '
                                                     'ConsumptionUnit',
                                         vlen=self.time.LEN, parent=self)
        self.calc_consumption_cost = \
            self._def_consumption_cost_calc(consumption_cost)

    def _def_consumption_cost_calc(self, cons_cost):
        """ Defines the consumption cost equation """
        if cons_cost is None:
            calc_consumption_cost = None
            self.consumption_cost = None
        else:
            if isinstance(cons_cost, (int, float)):
                calc_consumption_cost = DynamicConstraint(
                    name='calc_consumption_cost',
                    exp_t='{0}_consumption_cost[t] == {1} * '
                          '{0}_p[t] * time.DT'.format(self.name,
                                                      cons_cost),
                    t_range='for t in time.I', parent=self)
            elif isinstance(cons_cost, list):
                if len(cons_cost) != self.time.LEN:
                    raise IndexError(
                        "Your consumption cost should be the size of the time "
                        "period : {} but equals {}.".format(self.time.LEN,
                                                            len(cons_cost)))
                else:
                    calc_consumption_cost = DynamicConstraint(
                        name='calc_consumption_cost',
                        exp_t='{0}_consumption_cost[t] == {1}[t] * '
                              '{0}_p[t] * time.DT'.format(self.name,
                                                          cons_cost),
                        t_range='for t in time.I', parent=self)
            else:
                raise TypeError('Your consumption cost should be an int, '
                                'a float or a list.')

        return calc_consumption_cost

    # OBJECTIVES#
    def minimize_consumption(self, weight=1):
        """
        :param weight: Weight coefficient for the objective
        """
        self.min_consumption = Objective(name='min_consumption',
                                         exp='lpSum({0}_p[t] for t in time.I)'
                                         .format(self.name), weight=weight,
                                         parent=self)

    def maximize_consumption(self, weight=1):
        """
        :param weight: Weight coefficient for the objective
        """
        self.max_consumption = Objective(name='max_consumption',
                                         exp='-lpSum({0}_p[t] for t in time.I)'
                                         .format(self.name), weight=weight,
                                         parent=self)

    def minimize_consumption_cost(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.min_consumption_cost = Objective(
            exp='lpSum({}_consumption_cost[t] for t in '
                'time.I)'.format(self.name),
            name='min_consumption_cost', weight=weight, parent=self)


class FixedConsumptionUnit(ConsumptionUnit):
    """
    **Description**

        Consumption with a fixed load profile.

    **Attributes**

        * p : instantaneous power demand known in advance (kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * consumption_cost : cost associated to the energy consumption
        * operator : stakeholder how owns the consumption unit

    """

    def __init__(self, time, name='FCU1', p=None, energy_type=None,
                 consumption_cost=None, operator=None):
        ConsumptionUnit.__init__(self, time=time, name=name, p=p,
                                 p_min=min(p), p_max=max(p),
                                 energy_type=energy_type,
                                 consumption_cost=consumption_cost,
                                 operator=operator)

        if p is None:
            raise ValueError("You have to define the load profile (p) for the "
                             "FixedConsumptionUnit !")


class VariableConsumptionUnit(ConsumptionUnit):
    """
    **Description**

        Consumption unit with a variation of power between pmin et pmax.

    **Attributes**

        * pmax : maximal instantaneous power demand (kW)
        * pmin : minimal instantaneous power demand (kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * consumption_cost : cost associated to the energy consumption
        * operator : stakeholder how owns the consumption unit

    """

    def __init__(self, time, name='VCU1', pmin=1e-5, pmax=1e+5,
                 energy_type=None, consumption_cost=None, operator=None):
        ConsumptionUnit.__init__(self, time=time, name=name, p_min=pmin,
                                 p_max=pmax, energy_type=energy_type,
                                 consumption_cost=consumption_cost,
                                 operator=operator)


class ShiftableConsumptionUnit(VariableConsumptionUnit):
    """
    **Description**

        Consumption unit with shiftable production profile.

    **Attributs**

        * power_values : production profile to shift (kW)
        * mandatory : indicates if the production is mandatory : True
                      or not : False
        * starting_cost : cost of the starting of the production
        * operating_cost : cost of the operation (€/kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * owner : stakeholder how owns the production unit

    """

    def __init__(self, time, name: str, power_values, mandatory=True,
                 energy_type=None, owner=None):

        VariableConsumptionUnit.__init__(self, time=time, name=name,
                                         pmin=1e-5, pmax=max(power_values),
                                         energy_type=energy_type,
                                         owner=owner)
        # Add a variable for start/switch off
        self.start_up = Quantity(name='start_up',
                                 description='The ProductionUnit is '
                                             'starting :1 or not :0',
                                 vtype=LpBinary, vlen=time.LEN, parent=self)

        self.switch_off = Quantity(name='switch_off',
                                   description='The ProductionUnit is '
                                               'switching off :1 or not :0',
                                   vtype=LpBinary, vlen=time.LEN,
                                   parent=self)

        # When u[t] = 0 and u[t+1] = 1, start_up[t+1] = 1
        self.def_start_up = DynamicConstraint(
            exp_t='{0}_u[t+1] - {0}_u[t] <= '
                  '{0}_start_up[t+1]'.format(self.name),
            t_range='for t in time.I[:-1]', name='def_start_up')

        # Else start_up[t+1] = 0
        self.def_no_start_up = DynamicConstraint(
            exp_t='{0}_start_up[t+1] <= ({0}_u[t+1] - {0}_u[t]'
                  ' + 1)/2'.format(self.name),
            t_range='for t in time.I[:-1]',
            name='def_no_start_up')

        # When u[t} = 1 and u[t+1] = 0, switch_off[t+1] = 0
        self.def_switch_off = DynamicConstraint(
            exp_t='{0}_switch_off[t+1] == {0}_start_up[t+1] '
                  '+ {0}_u[t] - {0}_u[t+1]'.format(self.name),
            t_range='for t in time.I[:-1]',
            name='def_switch_off')

        # Def initial start_up
        self.def_init_start_up = Constraint(
            exp='{0}_start_up[0] == {0}_u[0]'.format(self.name),
            name='def_init_start_up', parent=self)

        # Set initial switch_off to 0
        self.def_init_switch_off = Constraint(
            exp='{0}_switch_off[0] == 0'.format(self.name),
            name='def_init_switch_off', parent=self)

        e_max = sum(power_values) * time.DT

        if mandatory:
            self.duration = Constraint(exp='lpSum({0}_u[t] for t in time.I) '
                                           '== {1}'.format(self.name,
                                                           len(power_values)),
                                       name='duration', parent=self)
            e_min = e_max

        else:
            self.duration = Constraint(exp='lpSum({0}_u[t] for t in time.I) '
                                           '<= {1}'.format(self.name,
                                                           len(power_values)),
                                       name='duration', parent=self)
            e_min = 0

        self.set_energy_limits_on_time_period(e_min=e_min, e_max=e_max)

        self.power_values = Quantity(name='power_values', opt=False,
                                     value=power_values,
                                     parent=self)

        for i, _ in enumerate(power_values):
            cst_name = 'def_{}_power_value'.format(i)

            exp_t = "{0}_p[t] >= {0}_power_values[{1}] * " \
                    "{0}_start_up[t-{1}]".format(self.name, i)

            cst = DynamicConstraint(name=cst_name, exp_t=exp_t,
                                    t_range="for t in time.I[{}:-1]".format(i),
                                    parent=self)
            setattr(self, cst_name, cst)
