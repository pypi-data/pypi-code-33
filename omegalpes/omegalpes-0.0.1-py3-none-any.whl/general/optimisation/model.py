#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
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

import os
import warnings
import glob

from pulp import LpProblem, LpStatus, LpVariable, lpSum, LpVariableDict
from pulp.solvers import LpSolver, COIN_CMD

from ..optimisation.units import Unit
from ..time import TimeUnit
from ...energy.energy_nodes import EnergyNode
from ..optimisation.elements import Constraint, DynamicConstraint
from ..optimisation.elements import Objective
from ..optimisation.elements import Quantity

__docformat__ = "restructuredtext en"


class OptimisationModel(LpProblem):
    """
    ** Description **
        This module includes the optimization model formulated in LP or MILP
        - based on the package PuLP (LpProblem)
    **

    """

    def __init__(self, name='optimisation_model'):
        """
        :param name: Name of your optimisation model (str)
        """
        LpProblem.__init__(self, name)
        self.verbose = 1
        self.noOverlap = False

        self.units_list = []
        self.quantities_list = []
        self.constraints_list = []
        self.objectives_list = []

    def add_nodes(self, *nodes):
        """
        Add nodes and all connected units to the model

        :param nodes: EnergyNode
        """
        for node in nodes:
            if not isinstance(node, EnergyNode):
                raise TypeError('You have to add nodes from type "EnergyNode".')
            self.units_list.append(node)
            node.set_power_balance()

            for unit in node.get_connected_energy_units:
                if unit not in self.units_list:
                    self.units_list.append(unit)
            self._get_all_units()

        self._add_quantities()
        self._add_objectives(nodes[0].time)
        self._add_constraints(nodes[0].time)

    def _get_all_units(self) -> None:
        """
            Gets all units linked to the units directly
            connected to the units in self.units_list
        """
        for unit in self.units_list:
            self._add_unit_parent(unit)
            self._add_unit_attributes(unit)

    def _add_unit_parent(self, unit: Unit) -> None:
        """
            If the parent of the unit is a Unit, the method adds it to the
        list of units : self.units_list
            Else : nothing happens

            :param unit: Unit whose parent will be added to the list of units
            if also a Unit
        """

        try:
            parent = getattr(unit, 'parent')
            if isinstance(parent, Unit) and parent not in self.units_list:
                self.units_list.append(parent)
        except AttributeError:
            check_if_unit_could_have_parent(unit)

    def _add_unit_attributes(self, unit: Unit) -> None:
        """
            Adds :
                - The Unit elements contained in the unit to the list of units
                self.units_list
                - The Quantity elements contained in the unit to the list of
                quantities self.quantities_list
                - The Constraint elements contained in the unit to the list of
                constraints self.constraints_list
                - The Objective elements contained in the unit to the list of
                objectives self.objectives_list

        :param unit: Unit whose attributes (Unit, Quantity, Constraint
        and Objective) will be added to the respective lists
        """
        try:
            for key in list(unit.__dict__.keys()):
                child = getattr(unit, key)
                if isinstance(child, Unit) and child not in self.units_list:
                    self.units_list.append(child)
                elif isinstance(child, Quantity) and child not in \
                        self.quantities_list:
                    child.parent = unit
                    self.quantities_list.append(child)
                elif isinstance(child, Constraint) and child.active and child \
                        not in self.constraints_list:
                    child.parent = unit
                    self.constraints_list.append(child)
                elif isinstance(child, Objective) and child not in \
                        self.objectives_list:
                    child.parent = unit
                    self.objectives_list.append(child)

        except AttributeError:
            pass

    def _add_quantities(self) -> None:
        """
        Adds all quantities as LpVariable to the list self.variables_list
        """

        print('\n--- Adding all variables to the model ---')
        for quantity in self.quantities_list:
            q_name = getattr(quantity, 'name')
            val = getattr(quantity, 'value')
            opt = getattr(quantity, 'opt')
            vtyp = getattr(quantity, 'vtype')
            lb, ub = getattr(quantity, 'lb'), getattr(quantity, 'ub')
            try:
                parent = getattr(quantity, 'parent')
                p_name = parent.name
            except AttributeError:
                raise ValueError('Each Quantity object should have a parent')

            new_name = p_name + '_' + q_name

            self._add_quantity(q_name=new_name, q_val=val, q_type=vtyp,
                               q_lb=lb, q_ub=ub, q_opt=opt,
                               parent=quantity.parent)

    def _add_quantity(self, q_name, q_val, q_type, q_lb, q_ub, q_opt,
                      parent=None):
        """
        Adds a quantity as LpVariable to the list self.variables_list
        """
        if self.verbose:
            print('Adding variable : {0}'.format(q_name))

        # Static or dynamic bounds
        if isinstance(q_lb, list):
            lb_cst_exp = q_name + '[t] >= ' + str(q_lb) + '[t]'
            setattr(parent, 'set_lb', DynamicConstraint(exp_t=lb_cst_exp,
                                                        name='set_lb',
                                                        parent=parent))
            q_lb = min(q_lb)

        if isinstance(q_ub, list):
            ub_cst_exp = q_name + '[t] <= ' + str(q_ub) + '[t]'
            setattr(parent, 'set_ub', DynamicConstraint(exp_t=ub_cst_exp,
                                                        name='set_ub',
                                                        parent=parent))
            q_ub = max(q_ub)

        # If the values are stored in a dictionary
        if isinstance(q_val, dict):
            globals()[q_name] = LpVariable.dict(name=q_name,
                                                indexs=q_val.keys(),
                                                lowBound=q_lb, upBound=q_ub,
                                                cat=q_type)

        # If the values are stored in a list
        elif isinstance(q_val, list):
            for ind, opt in enumerate(q_opt):
                if opt:
                    var_name = q_name + '_{0}'.format(ind)
                    globals()[var_name] = LpVariable(name=var_name,
                                                     lowBound=q_lb,
                                                     upBound=q_ub,
                                                     cat=q_type)
                else:
                    if ind == 0:
                        globals()[q_name] = q_val

        # If the values are stored in a int/float
        elif isinstance(q_val, (int, float)):
            if q_opt:
                globals()[q_name] = LpVariable(name=q_name,
                                               lowBound=q_lb,
                                               upBound=q_ub,
                                               cat=q_type)
            else:
                globals()[q_name] = q_val

        else:
            raise TypeError('Value type of the quantity {0} of unit {1} '
                            'is not taken into account'.format(q_name,
                                                               parent.name))

    def _add_constraints(self, time: TimeUnit) -> None:
        """
            Add all constraints to the model
        :param time: TimeUnit
        """
        print('\n--- Adding all constraints to the model ---')
        for cst in self.constraints_list:
            cst_name = cst.parent.name + '_' + cst.name
            cst_exp = cst.exp

            # Print the constraint expression
            if self.verbose:
                print('Adding constraint : {0} , exp = {1}'.format(cst_name,
                                                                   cst_exp))

            if isinstance(cst, DynamicConstraint):
                loop_exp = "".join([cst.t_range, ':\n'
                                                 '\ttry:\n'
                                                 '\t\tself += {0}, '
                                                 ''.format(cst.exp_t),
                                    '"{0}_{1}".format(cst_name, t)\n'
                                    '\texcept TypeError:\n'
                                    '\t\twarnings.warn("Possible error")'])
                exec(loop_exp)

            else:
                try:
                    # Add the constraint to the optimization model
                    self += eval(cst_exp), cst_name
                    # self.addConstraint(eval(cst_exp), cst_name)
                except TypeError:
                    warnings.warn('Possible error')

    def _add_objectives(self, time: TimeUnit) -> None:
        """
            Adds all objectives to the model
        :param time: TimeUnit
        """
        print('\n--- Adding all objectives to the model ---')
        objective = 0
        for obj in self.objectives_list:
            obj_name = obj.parent.name + '_' + obj.name
            obj_exp = obj.exp
            obj_weight = str(obj.weight)

            if self.verbose:
                print('Adding objective : {0}'.format(obj_name))
            objective += eval(obj_weight + ' * (' + obj_exp + ')')
        self += objective, "obj_tot"

    def update_units(self):
        """
            Updates all units values with optimization results
        """
        var_dict = self.variablesDict()
        for unit in self.units_list:
            print("Updating unit : {0}".format(unit.name))
            for key in list(unit.__dict__.keys()):
                quantity = getattr(unit, key)
                if isinstance(quantity, Quantity):
                    q_name = getattr(quantity, 'name')
                    q_opt = getattr(quantity, 'opt')
                    q_value = getattr(quantity, 'value')

                    print("\tQuantity : {0}".format(q_name))

                    if isinstance(q_value, (float, int)) and q_opt:
                        quantity.value = var_dict[
                            "{0}_{1}".format(unit.name, q_name)].varValue

                    elif isinstance(q_value, list):
                        for i, _ in enumerate(q_opt):
                            if quantity.opt[i]:
                                quantity.value[i] = var_dict[
                                    "{0}_{1}_{2}".format(unit.name,
                                                         q_name, i)].varValue

                    elif isinstance(q_value, dict):
                        for i in list(q_value.keys()):
                            try:
                                quantity.value[i] = var_dict[
                                    "{0}_{1}_{2}".format(unit.name,
                                                         q_name, i)].varValue
                            except KeyError:
                                pass

    def solve_and_update(self, solver: LpSolver = None) -> None:
        """
            Solves the optimization model and updates all variables values.
        :param solver: Optimization solver
        :type solver: LpSolver
        """
        print("\n - - - - - RUN OPTIMIZATION - - - - - ")
        if solver is None:
            self.solve(solver=solver, use_mps=False)
        else:
            self.solve(solver=solver)

        if LpStatus[self.status] == 'Optimal':
            print("\n - - - - - UPDATE RESULTS - - - - - ")
            self.update_units()
        else:
            warnings.warn("Your optimization failed with status : {}.".format(
                LpStatus[self.status]))
            if LpStatus[self.status] == 'Not Solved':
                print('If you are a Gurobi user and you want to catch the '
                      'source of infeasibility, please refer to the method '
                      '"compute_gurobi_IIS()" in general\optimation\model.')


def check_if_unit_could_have_parent(unit):
    import gc
    ref = gc.get_referrers(unit)
    attributes = gc.get_referents(unit)[0]

    for parent in ref:
        try:
            parent_name = parent['name']
            if parent_name not in attributes:
                warnings.warn('The unit {} seems to have as parent {} which '
                              'was not declared as parent.'.format(unit.name,
                                                                   parent_name))
        except (TypeError, KeyError):
            pass


def compute_gurobi_IIS(gurobi_exe_path=r'C:\gurobi800\win64\bin',
                       opt_model=None, MPS_model=None):
    """

    :param gurobi_exe_path: Path to the gurobi solver "gurobi_cl.exe"
    :param opt_model: OptimisationModel to whom compute IIS
    :param MPS_model: name of the mps model
    :return:
    """
    try:
        # Remove all the existing .mps in your directory
        os.system('"del ' + str('*.mps') + '"')
    except:
        pass

    if MPS_model is None:
        # Create the .mps  in order to get the .mps
        if opt_model is None:
            raise ValueError('You should provide either the OptimisationModel '
                             'or the MPS model')
        opt_model.solve()
        opt_model.writeMPS('{}.mps'.format(opt_model.name))
        MPS_file = glob.glob("*.mps")

    else:
        if MPS_model[-4:] == '.mps':
            MPS_file = [MPS_model]
        else:
            MPS_file = [MPS_model + '.mps']

    # Transform the .mps into a .ilp'
    cmd = '"' + gurobi_exe_path + '\gurobi_cl.exe ResultFile=IISresults.ilp ' \
          + MPS_file[0] + '"'
    os.system(cmd)
