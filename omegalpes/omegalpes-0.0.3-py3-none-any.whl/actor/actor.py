#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
** This modules define the basic Actor object **

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
from ..general.optimisation.units import Unit
from ..general.optimisation.elements import ExternalConstraint, \
    ExtDynConstraint, Objective


class Actor(Unit):
    """
    **Description**
        Actor class is the basic class to model an actor. The basic actor
        is defined by its name and description.
        An actor is then defined by its constraints and objectives.

    **Attributes**
        - name : name of the actor
    """

    def __init__(self, name):
        Unit.__init__(self, name=name)

        self.description = 'Actor Unit'

    def add_external_constraint(self, cst_name, exp):
        setattr(self, cst_name, ExternalConstraint(exp=exp,
                                                   name=cst_name))

    def add_external_dynamic_constraint(self, cst_name, exp_t,
                                        t_range='for t in time.I'):
        setattr(self, cst_name, ExtDynConstraint(exp_t=exp_t,
                                                 name=cst_name,
                                                 t_range=t_range))

    def remove_external_constraint(self, external_cst):
        external_cst.deactivate_constraint()

    def add_objective(self, obj_name, exp):
        setattr(self, obj_name, Objective(exp=exp, name=obj_name))
