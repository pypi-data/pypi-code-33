#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
** This module defines the production units**

 The production_units module defines various kinds of production units with
 associated attributes and methods. It includes :
    - ProductionUnit : simple production unit inheriting from EnergyUnit and
 with an outer flow direction. The outside CO2 emissions, the starting cost,
 the operating cost, the minimal operating time, the minimal non-operating time,
 the maximal increasing ramp and the maximal decreasing ramp can be filled.

        3 Objectives are also available :
            * minimize starting cost, operating cost or production.

    - FixedProductionUnit : Production unit with a fixed production profile.
    - VariableProductionUnit : Production unit with a variation of power between
     pmin et pmax.

     but also
     - SeveralProductionUnit: Production unit based on a fixed production curve
     enabling to multiply several times (nb_unit) the same production curve
     - SeveralImaginaryProductionUnit: Production unit based on a fixed
     production curve enabling to multiply several times (nb_unit) the same
     production curve. Be careful, the solution may be imaginary as nb_unit
     can be continuous. The accurate number of the production unit should be
     calculated later
     - SquareProductionUnit: Production unit with a fixed value and fixed
     duration.
     - ShiftableProductionUnit: Production unit with shiftable production
     profile.

..

    Copyright 2018 G2Elab / MAGE

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

import warnings
from pulp import LpBinary, LpInteger, LpContinuous

from .energy_units import EnergyUnit
from ...general.optimisation.elements import Constraint, DynamicConstraint, \
    ExtDynConstraint
from ...general.optimisation.elements import Objective
from ...general.optimisation.elements import Quantity

__docformat__ = "restructuredtext en"


class ProductionUnit(EnergyUnit):
    """
     **Description**
        Simple Production unit

    **Attributes**
        * co2_out: outside CO2 emissions
        * starting_cost: the starting cost
        * operating_cost: the operating cost
        * min_time_on : the minimal operating time
        * min_time_off : the minimal non-operating time
        * max_ramp_up : the  maximal increasing ramp
        * max_ramp_down ; the maximal decreasing ramp
    """

    def __init__(self, time, name, p=None, p_min=1e-5, p_max=1e+5, co2_out=None,
                 starting_cost=None, operating_cost=None, min_time_on=None,
                 min_time_off=None, max_ramp_up=None, max_ramp_down=None,
                 availability_hours=None, energy_type=None, operator=None):

        EnergyUnit.__init__(self, time, name, flow_direction='out', p=p,
                            p_min=p_min, p_max=p_max, e_min=0,
                            energy_type=energy_type, operator=operator)

        if starting_cost is not None or min_time_on is not None or \
                min_time_off is not None:
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

        # Adding CO2 emissions from production
        self.co2_emissions = Quantity(
            name='co2_emissions', description='Dynamic CO2 emissions '
                                              'generated by the ProductionUnit',
            lb=0, vlen=self.time.LEN, parent=self)
        self.calc_co2_emissions = self._def_co2_emissions_calc(co2_out)

        # Adding starting cost
        self.starting_cost = Quantity(name='starting_cost',
                                      description='Dynamic cost for the start'
                                                  ' of production unit',
                                      lb=0, vlen=self.time.LEN, parent=self)
        self.calc_start_cost = self._def_starting_cost_calc(starting_cost)

        # Adding operating cost
        self.operating_cost = Quantity(name='operating_cost',
                                       description='Dynamic cost for the '
                                                   'operation '
                                                   'of the production unit',
                                       lb=0,
                                       vlen=self.time.LEN, parent=self)
        self.calc_operating_cost = self._def_op_cost_calc(operating_cost)

        # Adding a maximal ramp up
        self.set_max_ramp_up = self._def_max_ramp_up_cst(max_ramp_up)

        # Adding a maximal ramp down
        self.set_max_ramp_down = self._def_max_ramp_down_cst(max_ramp_down)

        # Adding a minimum operating time
        self.set_min_up_time = self._def_min_up_time_cst(min_time_on)

        # Adding a minimum non-operating time
        self.set_min_down_time = self._def_min_down_time_cst(min_time_off)

        # Adding an number of available hours of operation
        self.set_availability = self._def_availability_cst(availability_hours)

        self.min_start_cost = None
        self.min_operating_cost = None
        self.min_production = None
        self.min_time_of_use = None

    # CONSTRAINTS #
    def _def_availability_cst(self, av_hours):
        """" Returns the constraint of available hours of operation for the
        ProductionUnit or None if no av_hours set"""
        if av_hours is not None:
            # The units is available during a number of hours during
            # the time period
            set_availability = Constraint(
                exp='lpSum({dt} * {name}_u[t] for t in time.I) <= '
                    '{av_h}'.format(dt=self.time.DT, name=self.name,
                                    av_h=av_hours),
                name='set_availability', parent=self)
        else:
            set_availability = None

        return set_availability

    def _def_min_up_time_cst(self, min_time_on):
        """ Returns the constraint of a minimal duration of the operation
        when the ProductionUnit starts up or None if no min_time_on """
        if min_time_on is not None:
            # When the unit starts, it should be on during min_time_on
            set_min_up_time = ExtDynConstraint(
                exp_t='{0}_u[t] >= lpSum({0}_start_up[i] for i in range('
                      'max(t - {1} + 1, 0), t))'.format(self.name, min_time_on),
                t_range='for t in time.I', name='set_min_up_time')
        else:
            set_min_up_time = None

        return set_min_up_time

    def _def_min_down_time_cst(self, min_time_off):
        """ Returns the constraint of a minimal duration between two
        operations or None if no min_time_off """
        if min_time_off is not None:
            # When the unit switches off, it should be off during min_time_off
            set_min_down_time = ExtDynConstraint(
                exp_t='1 - {0}_u[t] >= lpSum({0}_switch_off[i] for i in range('
                      'max(t - {1} + 1, 0), t))'.format(self.name,
                                                        min_time_off),
                t_range='for t in time.I', name='set_min_down_time')
        else:
            set_min_down_time = None

        return set_min_down_time

    def _def_max_ramp_up_cst(self, max_ramp_up):
        """ Returns the constraint of a maximal ramp between two time steps for
        power increase or None if no constraint """
        if max_ramp_up is not None:
            set_max_ramp_up = ExtDynConstraint(
                exp_t='{0}_p[t+1] - {0}_p[t] <= {1}'.format(self.name,
                                                            max_ramp_up),
                t_range='for t in time.I[:-1]', name='set_max_ramp_up')
        else:
            set_max_ramp_up = None

        return set_max_ramp_up

    def _def_max_ramp_down_cst(self, max_ramp_down):
        """ Returns the constraint of a maximal ramp between two time steps for
        power decrease or None if no constraint """
        if max_ramp_down is not None:
            set_max_ramp_down = ExtDynConstraint(
                exp_t='{0}_p[t] - {0}_p[t+1] <= {1}'.format(self.name,
                                                            max_ramp_down),
                t_range='for t in time.I[:-1]', name='set_max_ramp_down')
        else:
            set_max_ramp_down = None

        return set_max_ramp_down

    def _def_co2_emissions_calc(self, co2_out):
        """ Returns the constraint that allows the dynamic calculation of
        the CO2 emissions generated by the ProductionUnit or None if no CO2
        emissions defined """
        if co2_out is None:
            calc_co2_emissions = None
            self.co2_emissions = None
        else:
            if isinstance(co2_out, (int, float)):
                calc_co2_emissions = DynamicConstraint(
                    exp_t='{0}_co2_emissions[t] == {1} * '
                          '{0}_p[t]'.format(self.name, co2_out),
                    name='calc_co2_emissions', parent=self)
            elif isinstance(co2_out, list):
                if len(co2_out) != self.time.LEN:
                    raise IndexError(
                        "Your CO2 emissions (CO2_out should be the size of the "
                        "time period.")
                else:
                    calc_co2_emissions = DynamicConstraint(
                        exp_t='{0}_co2_emissions[t] == {1}[t] * '
                              '{0}_p[t]'.format(self.name, co2_out),
                        name='calc_co2_emissions', parent=self)
            else:
                raise TypeError('co2_out should be an int, a float or a list.')

        return calc_co2_emissions

    def _def_starting_cost_calc(self, start_cost):
        """"
            Adds to the ProductionUnit :
                * the Constraint calc_start_cost, which define how the
                starting cost is calculated
        """
        if start_cost is None:
            calc_start_cost = None
            self.starting_cost = None
        else:
            calc_start_cost = DynamicConstraint(
                exp_t='{0}_starting_cost[t] == {1} * {0}_start_up[t]'.format(
                    self.name, start_cost),
                t_range='for t in time.I[:-1]', name='calc_start_cost')

        return calc_start_cost

    def _def_op_cost_calc(self, operating_cost):
        """
            Adds to the ProductionUnit :
                * the Constraint calc_operating_cost, which define how the
                operating cost cost is calculated
        """
        if operating_cost is None:
            calc_operating_cost = None
            self.operating_cost = None

        else:
            if isinstance(operating_cost, (int, float)):
                calc_operating_cost = DynamicConstraint(
                    name='calc_operating_cost',
                    exp_t='{0}_operating_cost[t] == {1} * '
                          '{0}_p[t] * time.DT'.format(self.name,
                                                      operating_cost),
                    t_range='for t in time.I', parent=self)

            elif isinstance(operating_cost, list):
                if len(operating_cost) != self.time.LEN:
                    raise IndexError(
                        "Your operating cost should be the size of the time "
                        "period.")
                else:
                    calc_operating_cost = DynamicConstraint(
                        name='calc_operating_cost',
                        exp_t='{0}_operating_cost[t] == {1}[t] * '
                              '{0}_p[t] * time.DT'.format(self.name,
                                                          operating_cost),
                        t_range='for t in time.I', parent=self)
            else:
                raise TypeError('The operating_cost should be an int, a float '
                                'or a list.')

        return calc_operating_cost

    # OBJECTIVES #
    def minimize_starting_cost(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.min_start_cost = Objective(name='min_start_cost',
                                        exp='lpSum({0}_starting_cost[t] for t '
                                            'in time.I)'
                                        .format(self.name), weight=weight,
                                        parent=self)

    def minimize_operating_cost(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.min_operating_cost = Objective(name='min_operating_cost',
                                            exp='lpSum({0}_operating_cost[t] '
                                                'for t in time.I)'
                                            .format(self.name), weight=weight,
                                            parent=self)

    def minimize_costs(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        if self.starting_cost is not None:
            self.minimize_starting_cost(weight)

        if self.operating_cost is not None:
            self.minimize_operating_cost(weight)

    def minimize_production(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.min_production = Objective(name='min_production',
                                        exp='lpSum({0}_p[t] for t in time.I)'
                                        .format(self.name), weight=weight,
                                        parent=self)

    def minimize_time_of_use(self, weight=1):
        """

        :param weight: Weight coefficient for the objective
        """
        self.min_time_of_use = Objective(name='min_time_of_use',
                                         exp='lpSum({0}_u[t] for t in time.I)'
                                         .format(self.name), weight=weight,
                                         parent=self)


class FixedProductionUnit(ProductionUnit):
    """
    **Description**

        Production unit with a fixed production profile.

    **Attributs**

        * p : instantaneous power production known by advance (kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * operator : stakeholder how owns the production unit

    """

    def __init__(self, time, name: str = 'FPU1', p: list = None, co2_out=None,
                 starting_cost=None, operating_cost=None, min_time_on=None,
                 min_time_off=None, max_ramp_up=None, max_ramp_down=None,
                 energy_type=None, operator=None):
        ProductionUnit.__init__(self, time=time, name=name, p=p,
                                p_min=min(p), p_max=max(p), co2_out=co2_out,
                                starting_cost=starting_cost,
                                operating_cost=operating_cost,
                                min_time_on=min_time_on,
                                min_time_off=min_time_off,
                                max_ramp_up=max_ramp_up,
                                max_ramp_down=max_ramp_down,
                                energy_type=energy_type, operator=operator)

        if p is None:
            raise ValueError(
                "You have to define the production profile (p) for the "
                "FixedProductionUnit !")


class VariableProductionUnit(ProductionUnit):
    """
    **Description**

        Production unit with a variation of power between pmin et pmax.

    **Attributs**

        * pmax : maximal instantaneous power production (kW)
        * pmin : minimal instantaneous power production (kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * operator : stakeholder how owns the production unit

    """

    def __init__(self, time, name='VPU1', pmin=1e-5, pmax=1e+5, co2_out=None,
                 starting_cost=None, operating_cost=None, min_time_on=None,
                 min_time_off=None, max_ramp_up=None, max_ramp_down=None,
                 energy_type=None, operator=None):
        ProductionUnit.__init__(self, time=time, name=name, p_min=pmin,
                                p_max=pmax, co2_out=co2_out,
                                starting_cost=starting_cost,
                                operating_cost=operating_cost,
                                min_time_on=min_time_on,
                                min_time_off=min_time_off,
                                max_ramp_up=max_ramp_up,
                                max_ramp_down=max_ramp_down,
                                energy_type=energy_type, operator=operator)


class SeveralProductionUnit(VariableProductionUnit):
    """
    **Description**

        Production unit based on a fixed production curve enabling to multiply
        several times (nb_unit) the same production curve

    **Attributs**

        * fixed_prod : fixed production curve

    """

    def __init__(self, time, name, fixed_prod, pmin=1e-5, pmax=1e+5,
                 co2_out=None,
                 starting_cost=None, operating_cost=None, min_time_on=None,
                 min_time_off=None, max_ramp_up=None, max_ramp_down=None,
                 energy_type=None, operator=None):
        ProductionUnit.__init__(self, time=time, name=name, p_min=pmin,
                                p_max=pmax, co2_out=co2_out,
                                starting_cost=starting_cost,
                                operating_cost=operating_cost,
                                min_time_on=min_time_on,
                                min_time_off=min_time_off,
                                max_ramp_up=max_ramp_up,
                                max_ramp_down=max_ramp_down,
                                energy_type=energy_type, operator=operator)

        self.production_curve = Quantity(name='fixed_p', opt=False,
                                         value=fixed_prod, vlen=time.LEN)

        self.nb_unit = Quantity(name='nb_unit', opt=True,
                                vtype=LpInteger,
                                vlen=1)

        self.calc_prod_with_nb_unit_cst = DynamicConstraint(
            exp_t='{0}_p[t] == {0}_nb_unit * {0}_fixed_p[t]'.format(
                self.name), name='calc_prod_with_nb_unit',
            t_range='for t in time.I', parent=self)


class SeveralImaginaryProductionUnit(VariableProductionUnit):
    """
    **Description**

        Production unit based on a fixed production curve enabling to multiply
        several times (nb_unit) the same production curve.
        Be careful, the solution may be imaginary as nb_unit can be
        continuous. The accurate number of the production unit should be
        calculated later

    **Attributs**
        * fixed_prod : fixed production curve

    """

    def __init__(self, time, name, fixed_prod, pmin=1e-5, pmax=1e+5,
                 co2_out=None,
                 starting_cost=None, operating_cost=None, min_time_on=None,
                 min_time_off=None, max_ramp_up=None, max_ramp_down=None,
                 energy_type=None, operator=None):
        ProductionUnit.__init__(self, time=time, name=name, p_min=pmin,
                                p_max=pmax, co2_out=co2_out,
                                starting_cost=starting_cost,
                                operating_cost=operating_cost,
                                min_time_on=min_time_on,
                                min_time_off=min_time_off,
                                max_ramp_up=max_ramp_up,
                                max_ramp_down=max_ramp_down,
                                energy_type=energy_type, operator=operator)

        self.production_curve = Quantity(name='fixed_p', opt=False,
                                         value=fixed_prod, vlen=time.LEN)

        self.nb_unit = Quantity(name='nb_unit', opt=True, vtype=LpContinuous,
                                vlen=1)
        warnings.warn('The solution may be imaginary as nb_unit is continuous')

        self.calc_prod_with_nb_unit_cst = DynamicConstraint(
            exp_t='{0}_p[t] == {0}_nb_unit * {0}_fixed_p[t]'.format(
                self.name), name='calc_prod_with_nb_unit',
            t_range='for t in time.I', parent=self)


class SquareProductionUnit(VariableProductionUnit):
    """
    **Description**

        Production unit with a fixed value and fixed duration.
            >> Only the time of beginning can be modified
            >> Operation can be mandatory or not

    **Attributs**

        * p : instantaneous power production (kW)
        * duration : duration of the power delivery (hours)
        * mandatory : indicates if the power delivery is mandatory or not
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * operator : stakeholder how owns the production unit

    """

    def __init__(self, time, name, p, duration, mandatory=True, co2_out=None,
                 starting_cost=None, operating_cost=None, energy_type=None,
                 operator=None):
        duration /= time.DT
        if duration < 1:
            raise ValueError('The duration of operation of the '
                             'SquareProductionUnit should be longer than the '
                             'time step.')
        VariableProductionUnit.__init__(self, time=time, name=name,
                                        pmin=p, pmax=p, co2_out=co2_out,
                                        starting_cost=starting_cost,
                                        operating_cost=operating_cost,
                                        min_time_on=duration,
                                        min_time_off=None,
                                        max_ramp_up=None,
                                        max_ramp_down=None,
                                        energy_type=energy_type,
                                        operator=operator)
        if mandatory:
            self.duration = Constraint(exp='lpSum({0}_u[t] for t in time.I) '
                                           '== {1}'.format(self.name, duration),
                                       name='duration', parent=self)
        else:
            self.duration = Constraint(exp='lpSum({0}_u[t] for t in time.I) '
                                           '<= {1}'.format(self.name, duration),
                                       name='duration', parent=self)


class ShiftableProductionUnit(VariableProductionUnit):
    """
    **Description**

        Production unit with shiftable production profile.

    **Attributs**

        * power_values : production profile to shift (kW)
        * mandatory : indicates if the production is mandatory : True
                      or not : False
        * starting_cost : cost of the starting of the production
        * operating_cost : cost of the operation (€/kW)
        * energy_type : type of energy ('Electrical', 'Heat', ...)
        * operator : stakeholder how owns the production unit

    """

    def __init__(self, time, name: str, power_values, mandatory=True,
                 co2_out=None, starting_cost=None, operating_cost=None,
                 energy_type=None, operator=None):

        VariableProductionUnit.__init__(self, time=time, name=name,
                                        pmin=1e-5, pmax=max(power_values),
                                        co2_out=co2_out,
                                        starting_cost=starting_cost,
                                        operating_cost=operating_cost,
                                        min_time_on=len(power_values),
                                        min_time_off=None,
                                        max_ramp_up=None,
                                        max_ramp_down=None,
                                        energy_type=energy_type,
                                        operator=operator)

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
