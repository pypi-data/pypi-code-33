#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""""
** This module defines the conversion units, with at least a production unit
and a consumption unit and using one or several energy types**

 The conversion_units module defines various classes of conversion units,
 from generic to specific ones. It includes :
    - ConversionUnit : simple conversion unit. It inherits from Unit.
    - ElectricalToHeatConversionUnit : Electrical to heat Conversion unit with
 an electricity consumption and a heat production linked by and electrical
 to heat ratio. It inherits from ConversionUnit
    - HeatPump : Simple Heat Pump with an electricity consumption, a heat
    production and a heat consumption. It has a theoretical coefficient of
    performance COP and inherits from ConversionUnit.

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


from .consumption_units import ConsumptionUnit
from .production_units import ProductionUnit
from ...general.optimisation.elements import Quantity, DynamicConstraint
from ...general.optimisation.units import Unit

__docformat__ = "restructuredtext en"


class ConversionUnit(Unit):
    """
    **Description**
        Simple Conversion unit

    **Attributes**
        * time : TimeUnit describing the studied time period
        * prod_units : list of the production units
        * cons_units : list of the consumption units
        * operator : stakeholder who owns the conversion unit
        * poles : dictionary of the poles of the conversion unit
    """

    def __init__(self, time, name, prod_units=None, cons_units=None,
                 operator=None):
        Unit.__init__(self, name=name, description='Conversion unit')

        self.time = time
        self.operator = operator  # Operator of the conversion unit
        self.prod_units = []  # Initialize an empty list for the
        # production units
        self.cons_units = []  # Initialize an empty list for the consumption
        # units
        self.poles = {}  # Initialize an empty dictionary for the poles

        # A conversion unit is created with at least a production unit and a
        # consumption unit
        if not prod_units:
            raise IndexError('You have to fill at least a production unit.')
        elif not isinstance(prod_units, list):
            raise TypeError('prod_units should be a list.')
        else:
            for prod_unit in prod_units:
                # prod_units should only contain ProductionUnit objects
                if not isinstance(prod_unit, ProductionUnit):
                    raise TypeError('The elements in prod_units have to be the'
                                    ' type "ProductionUnit".')
                else:
                    self._add_production_unit(prod_unit)

        if not cons_units:
            raise IndexError('You have to fill at least a consumption unit.')
        elif not isinstance(cons_units, list):
            raise TypeError('cons_units should be a list.')
        else:
            for cons_unit in cons_units:
                # cons_units should only contain ConsumptionUnit
                if not isinstance(cons_unit, ConsumptionUnit):
                    raise TypeError('The elements in cons_units have to be the'
                                    ' type "ConsumptionUnit".')
                else:
                    self._add_consumption_unit(cons_unit)

    def _add_production_unit(self, prod_unit):
        """
        :param prod_unit: production unit to be added to the
        production_units list
        """
        if prod_unit not in self.prod_units:
            poles_nb = len(self.poles)
            self.poles[poles_nb + 1] = prod_unit.poles[1]
            self.prod_units.append(prod_unit)
            prod_unit.parent = self
        else:
            print('Production unit {0} already in the production_units '
                  'list'.format(prod_unit.name))

    def _add_consumption_unit(self, cons_unit):
        """
        :param cons_unit: consumption unit to be added to the
        consumption_units list
        """
        if cons_unit not in self.cons_units:
            poles_nb = len(self.poles)
            self.poles[poles_nb + 1] = cons_unit.poles[1]
            self.cons_units.append(cons_unit)
            cons_unit.parent = self
        else:
            print('Consumption unit {0} already in the consumption_units '
                  'list'.format(cons_unit.name))


class ElectricalToHeatConversionUnit(ConversionUnit):
    """
    **Description**
        Electrical to heat Conversion unit with an electricity consumption
        and a heat production

    **Attributes**
        * heat_production_unit : heat production unit (heat output)
        * elec_consumption_unit : electricity consumption unit (electrical
        input)
        * conversion : Dynamic Constraint linking the electrical input to
        the heat output through the electrical to heat ratio
    """

    def __init__(self, time, name, pmin_in_elec=1e-5, pmax_in_elec=1e+5,
                 p_in_elec=None, pmin_out_heat=1e-5, pmax_out_heat=1e+5,
                 p_out_heat=None, elec_to_heat_ratio=1, operator=None):
        """
        :param time: TimeUnit describing the studied time period
        :param name: name of the electrical to heat conversion unit
        :param pmin_in_elec: minimal incoming electrical power
        :param pmax_in_elec: maximal incoming electrical power
        :param p_in_elec: power input for the electrical consumption unit
        :param pmin_out_heat: minimal power output (heat)
        :param pmax_out_heat: maximal power output (heat)
        :param p_out_heat: power output (heat)
        :param elec_to_heat_ratio: electricity to heat ratio <=1
        :param operator : operator of the electrical to heat conversion unit
        """

        self.heat_production_unit = ProductionUnit(time, name + '_heat_prod',
                                                   p=p_out_heat,
                                                   energy_type='Heat',
                                                   p_min=pmin_out_heat,
                                                   p_max=pmax_out_heat,
                                                   operator=operator)

        self.elec_consumption_unit = ConsumptionUnit(time, name + '_elec_cons',
                                                     p_min=pmin_in_elec,
                                                     p_max=pmax_in_elec,
                                                     p=p_in_elec,
                                                     energy_type='Electrical',
                                                     operator=operator)

        ConversionUnit.__init__(self, time, name,
                                prod_units=[self.heat_production_unit],
                                cons_units=[self.elec_consumption_unit],
                                operator=operator)

        if isinstance(elec_to_heat_ratio, (int, float)):  # e2h_ratio is a
            # mean value
            if elec_to_heat_ratio <= 1:
                self.conversion = DynamicConstraint(
                    exp_t='{0}_p[t] == {1} * {2}_p[t]'.format(
                        self.heat_production_unit.name,
                        elec_to_heat_ratio,
                        self.elec_consumption_unit.name),
                    t_range='for t in time.I', name='conversion', parent=self)
            else:
                raise ValueError('The elec_to_heat_ratio should be lower '
                                 'than 1 (heat_production<elec_consumption)')

        elif isinstance(elec_to_heat_ratio, list):  # e2h_ratio is a list of
            # values
            if len(elec_to_heat_ratio) == self.time.LEN:  # it must have the
                #  right size, i.e. the TimeUnit length.
                if all(e <= 1 for e in elec_to_heat_ratio):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.heat_production_unit.name,
                            elec_to_heat_ratio,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                else:
                    raise ValueError('The elec_to_heat_ratio values should be '
                                     'lower than 1 (heat_production<elec_'
                                     'consumption)')
            else:
                raise IndexError('The length of the elec_to_heat_ratio '
                                 'vector should be of the same length as the '
                                 'TimeUnit of the studied period')

        elif isinstance(elec_to_heat_ratio, dict):  # e2h_ratio is a dict of
            # values
            if len(elec_to_heat_ratio) == self.time.LEN:
                if all(e <= 1 for e in elec_to_heat_ratio.values()):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.heat_production_unit.name,
                            elec_to_heat_ratio,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                else:
                    raise ValueError('The elec_to_heat_ratio values should be '
                                     'lower than 1 (heat_production<elec_'
                                     'consumption)')
            else:
                raise IndexError('The length of the elec_to_heat_ratio '
                                 'dictionary should be of the same length as '
                                 'the TimeUnit of the studied period')
        else:
            raise TypeError(
                "Electricity to heat ratio should be a mean value or a "
                "vector (list or dict) for each time period !")


class HeatPump(ConversionUnit):
    """
    **Description**
        Simple Heat Pump with an electricity consumption, a heat production
        and a heat consumption. It has a theoretical coefficient of
    performance COP and inherits from ConversionUnit.

    **Attributes**

        * heat_production_unit : heat production unit (condenser)
        * elec_consumption_unit : electricity consumption unit (electrical
        input)
        * heat_consumption_unit : heay consumption unit (evaporator)
        * COP : Quantity describing the coefficient of performance of the
        heat pump
        * conversion : Dynamic Constraint linking the electrical input to
        the heat output through the electrical to heat ratio
        * power_flow : Dynamic constraint linking the heat output to the
        electrical and heat inputs in relation to the losses.

    """

    def __init__(self, time, name, pmin_in_elec=1e-5, pmax_in_elec=1e+5,
                 p_in_elec=None, pmin_in_heat=1e-5, pmax_in_heat=1e+5,
                 p_in_heat=None, pmin_out_heat=1e-5, pmax_out_heat=1e+5,
                 p_out_heat=None, cop=3, losses=0, operator=None):
        """
        :param time: TimeUnit describing the studied time period
        :param name: name of the heat pump
        :param pmin_in_elec:  minimal incoming electrical power
        :param pmax_in_elec: maximal incoming electrical power
        :param p_in_elec: power input for the electrical consumption unit
        :param pmin_in_heat: minimal incoming thermal power
        :param pmax_in_heat: maximal incoming thermal power
        :param p_in_heat: power input for the heat consumption unit
        :param pmin_out_heat: minimal power output (heat)
        :param pmax_out_heat: maximal power output (heat)
        :param p_out_heat: power output (heat)
        :param cop: Coefficient Of Performance of the Heat Pump (cop>1)
        :param losses: losses as a percentage of Pheat produced (p_out)
        :param operator: operator of the heat pump
        """

        self.heat_production_unit = ProductionUnit(time, name + '_heat_prod',
                                                   p=p_out_heat,
                                                   energy_type='Heat',
                                                   p_min=pmin_out_heat,
                                                   p_max=pmax_out_heat,
                                                   operator=operator)
        self.heat_consumption_unit = ConsumptionUnit(time, name + '_heat_cons',
                                                     p_min=pmin_in_heat,
                                                     p_max=pmax_in_heat,
                                                     p=p_in_heat,
                                                     energy_type='Heat',
                                                     operator=operator)
        self.elec_consumption_unit = ConsumptionUnit(time, name + '_elec_cons',
                                                     p_min=pmin_in_elec,
                                                     p_max=pmax_in_elec,
                                                     p=p_in_elec,
                                                     energy_type='Electrical',
                                                     operator=operator)

        self.COP = Quantity(name='COP', opt=False, value=cop, parent=self)

        ConversionUnit.__init__(self, time, name,
                                prod_units=[self.heat_production_unit],
                                cons_units=[self.heat_consumption_unit,
                                            self.elec_consumption_unit],
                                operator=operator)

        if isinstance(self.COP.value, (int, float)):  # The cop has a single
            #  value
            if self.COP.value >= 1:  # The cop value should be greater than 1
                self.conversion = DynamicConstraint(
                    exp_t='{0}_p[t] == {1} * {2}_p[t]'.format(
                        self.heat_production_unit.name,
                        self.COP.value,
                        self.elec_consumption_unit.name),
                    t_range='for t in time.I', name='conversion', parent=self)

                self.power_flow = DynamicConstraint(
                    exp_t='{0}_p[t]*(1+{1}) == {2}_p[t] + {3}_p[t]'
                        .format(self.heat_production_unit.name, losses,
                                self.heat_consumption_unit.name,
                                self.elec_consumption_unit.name),
                    t_range='for t in time.I',
                    name='power_flow', parent=self)
            else:
                raise ValueError("The COP value should be greater than 1")

        elif isinstance(self.COP.value, list):  # The cop has a list of values
            if len(self.COP.value) == self.time.LEN:
                if all(c >= 1 for c in self.COP.value):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.heat_production_unit.name,
                            self.COP.value,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                    self.power_flow = DynamicConstraint(
                        exp_t='{0}_p[t]*(1+{1}) == {2}_p[t] + {3}_p[t]'
                            .format(self.heat_production_unit.name, losses,
                                    self.heat_consumption_unit.name,
                                    self.elec_consumption_unit.name),
                        t_range='for t in time.I',
                        name='power_flow', parent=self)
                else:
                    raise ValueError("The COP values should be greater than 1")
            else:
                raise IndexError("The COP should have the same length as the "
                                 "studied time period")

        elif isinstance(self.COP.value, dict):  # The cop has a dict
            # referencing its values.
            if len(self.COP.value) == self.time.LEN:
                if all(c >= 1 for c in self.COP.value.values()):
                    self.conversion = DynamicConstraint(
                        exp_t='{0}_p[t] == {1}[t] * {2}_p[t]'.format(
                            self.heat_production_unit.name,
                            self.COP.value,
                            self.elec_consumption_unit.name),
                        t_range='for t in time.I', name='conversion',
                        parent=self)
                    self.power_flow = DynamicConstraint(
                        exp_t='{0}_p[t]*(1+{1}) == {2}_p[t] + {3}_p[t]'
                            .format(self.heat_production_unit.name, losses,
                                    self.heat_consumption_unit.name,
                                    self.elec_consumption_unit.name),
                        t_range='for t in time.I',
                        name='power_flow', parent=self)
                else:
                    raise ValueError("The COP values should be greater than 1")
            else:
                raise IndexError("The COP should have the same length as the "
                                 "studied time period")
        else:
            raise TypeError(
                "The assigned cop should be a mean value or a vector "
                "(dict or list) over the studied time period !")
