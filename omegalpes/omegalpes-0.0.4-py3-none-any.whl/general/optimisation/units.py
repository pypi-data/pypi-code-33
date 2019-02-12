#! usr/bin/env python3
#  -*- coding: utf-8 -*-

""""
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

from .elements import Quantity, Constraint, Objective

__docformat__ = "restructuredtext en"


class Unit:
    """
    **Description**
            Unit class is used as an "abstract class", i.e. it defines some
            general attributes and methods but doesn't contain variable,
            constraint nor objective. In the OMEGAlpes package, all the
            subsystem models are represented by a unit. A model is then
            generated adding Unit to it.
            Variable, objective and constraints declarations are usually done
            using the __init__ method of the Unit class.

        **Attributes**
            - name
            - description

        **Methods**
            - __str__: defines the
            - __repr__: defines the unit with its name

        .. note::
            The Unit class shouldn't be instantiated in a python script,
            except if you want to create your own model from the beginning.
            In this case, one should consider creating a new class
            NewModel(Unit).
    """

    def __init__(self, name='U0', description="General unit"):
        self.name = name
        self.description = description
        self.units_list = []
        self.quantities_list = []
        self.constraints_list = []
        self.objectives_list = []

        print(("Creating the {0}.".format(name)))

    def __str__(self):
        """"
        Add in the expression of the unit the variables, constraints and
        objectives
        :return: string
        """
        import numpy
        var = {}
        cst = {}
        cstr = {}
        obj = {}
        exp = '<OMEGALPES.general.units.Unit: \nname: {0} \ndescription: {1}' \
              '\n'.format(self.name, self.description)
        for u_key in list(self.__dict__.keys()):
            key: (Quantity, Constraint, Objective) = getattr(self, u_key)
            if isinstance(key, Quantity):
                if isinstance(key.opt, bool):
                    if key.opt:
                        var[u_key] = key
                    else:
                        cst[u_key] = key
                elif isinstance(key.opt, dict):
                    if numpy.array(list(key.opt.values())).all():
                        var[u_key] = key
                    else:
                        cst[u_key] = key
            elif isinstance(key, Constraint):
                cstr[u_key] = key
            elif isinstance(key, Objective):
                obj[u_key] = key
        exp += '\nOptimization variables:\n'
        for u_key in list(var.keys()):
            exp += 'name: ' + getattr(self, u_key).name + '\n'
        exp += '\nConstants:\n'
        for u_key in list(cst.keys()):
            exp += 'name: ' + getattr(self, u_key).name + ',  value: ' + \
                   str(getattr(self, u_key).value) + '\n'
        exp += '\nConstraints:\n'
        for u_key in list(cstr.keys()):
            exp += '[' + str(getattr(self, u_key).active) + ']' + ' name: ' + \
                   getattr(self, u_key).name + ' exp: ' + \
                   str(getattr(self, u_key).exp) + '\n'
        exp += '\nObjective:\n'
        for u_key in list(obj.keys()):
            exp += '[' + str(getattr(self, u_key).active) + ']' + 'name: ' \
                   + getattr(self, u_key).name + ' exp: ' + \
                   str(getattr(self, u_key).exp) + '\n'
        return exp

    def __repr__(self):
        """
        Return the description of the unit considering the name
        :return: string
        """
        return "<OMEGALPES.general.optimisation.units.Unit: name:\'{0}\'>" \
            .format(self.name)

    def add_unit_attributes_in_lists(self) -> None:
        """
            Adds :
                - The name of the Quantity elements contained in the unit to
                the list of quantities self.quantities_list
                - The name of the Constraint elements contained in the unit to
                the list of constraints self.constraints_list
                - The name of the Objective elements contained in the unit to
                the list of objectives self.objectives_list
        """
        try:
            for key in list(self.__dict__.keys()):
                child = getattr(self, key)
                if isinstance(child, Quantity) and child not in \
                        self.quantities_list:
                    self.quantities_list.append(child)
                elif isinstance(child, Constraint) and child.active and \
                        child not in self.constraints_list:
                    self.constraints_list.append(child)
                elif isinstance(child, Objective) and child not in \
                        self.objectives_list:
                    self.objectives_list.append(child)

        except AttributeError:
            pass

    def get_constraints_list(self):
        """ Get the constraints associated with the unit """
        return self.constraints_list

    def get_constraints_name_list(self):
        """ Get the names of the constraints associated with the unit """
        constraints_name_list = []
        for constraint in self.constraints_list:
            constraints_name_list.append(constraint.name)
        return constraints_name_list

    def get_objectives_list(self):
        """ Get objectives associated with the unit """
        return self.objectives_list

    def get_objectives_name_list(self):
        """ Get the names of the objectives associated with the unit """
        objectives_name_list = []
        for objective in self.objectives_list:
            objectives_name_list.append(objective.name)
        return objectives_name_list

    def get_quantities_list(self):
        """ Get the quantities associated with the unit """
        return self.quantities_list

    def get_quantities_name_list(self):
        """ Get the names of the quantities associated with the unit """
        quantities_name_list = []
        for quantity in self.quantities_list:
            quantities_name_list.append(quantity.name)
        return quantities_name_list
