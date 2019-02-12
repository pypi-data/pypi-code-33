#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
** This module defines the operator_actor and its scope of responsibility **

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
from ..actor import Actor
from ...general.optimisation.elements import ExternalConstraint, \
    ExtDynConstraint


class RegulatorActor(Actor):
    """
    **Description**
        RegulatorActor class inherits from the the basic class Actor. It
        enables one to model an actor who can add constraints on all
        energy units of the study case.

    **Attributes**
        - name : name of the actor
    """

    def __init__(self, name):
        Actor.__init__(self, name=name)

        self.description = 'Regulator Actor Unit'

    def co2_emission_maximum(self, max_co2, time, cst_unit_list):
        """
        To create the actor constraint of a maximum of CO2 emission.

        :param max_co2: Minimum of the CO2 emission. May be an int,
        float or a list with the size of the period study
        :param time: period of the study
        :param cst_unit_list: List of units on which the constraint
        will be applied.

        """

        production_name_string = ''
        for production_unit in cst_unit_list:
            production_name_string += '_{}'.format(
                production_unit.name)

        production_p_string = ''
        for production_unit in cst_unit_list[:-1]:
            production_p_string += '{}_p[t] + '.format(production_unit.name)
        production_p_string += '{}_p[t] '.format(
            cst_unit_list[-1].name)

        cst_name = 'max_co2_emission_{}'.format(production_name_string)

        if isinstance(max_co2, (int, float)):
            exp = '{0} <= {1}'.format(production_p_string, max_co2)
            setattr(self, cst_name, ExternalConstraint(exp=exp,
                                                       name=cst_name))

        elif isinstance(max_co2, list):
            if len(max_co2) != time.LEN:
                raise IndexError(
                    "Your maximal power should be the size of the time "
                    "period : {} but equals {}.".format(time.LEN,
                                                        len(max_co2)))
            else:
                exp_t = '{0} <= {1}[t]'.format(production_p_string, max_co2)
                setattr(self, cst_name, ExtDynConstraint(exp_t=exp_t,
                                                         name=cst_name,
                                                         t_range='for t in '
                                                                 'time.I'))
        else:
            raise TypeError('Your maximal power should be an int, '
                            'a float or a list.')


class LocalAuthorities(RegulatorActor):
    """
    **Description**
        LocalAuthorities class inherits from the basic class RegulatorActor. It
        focuses on local Authorities constraints

    """

    def __init__(self, name):
        RegulatorActor.__init__(self, name=name)


class PublicAuthorities(RegulatorActor):
    """
    **Description**
        PublicAuthorities class inherits from the basic class RegulatorActor. It
        focuses on local Authorities constraints

    """

    def __init__(self, name):
        RegulatorActor.__init__(self, name=name)
