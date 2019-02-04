#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**Description**
    This module includes the utils
        - To save results

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

import csv
import pandas as pd
from pulp import LpBinary
from .optimisation.elements import Quantity
from .optimisation.elements import Constraint, DynamicConstraint

__docformat__ = "restructuredtext en"


def save_energy_flows(*nodes, file_name=None, sep='\t', decimal_sep='.'):
    if decimal_sep != '.' and decimal_sep != ',':
        raise ValueError("The decimal separator should be either a dot "
                         "or a comma but is {0}".format(decimal_sep))
    if file_name is None:
        file_name = 'energy_flows_results.csv'
    else:
        file_name += '.csv'

    time = getattr(nodes[0], 'time')

    energy_flows = [
        ['date'] + [date.to_pydatetime() for date in time.DATES] + ['hour']]
    for node in nodes:
        for energy_flow in node.get_flows:
            v = getattr(energy_flow, 'value')
            parent = getattr(energy_flow, 'parent')
            name = getattr(parent, 'name')

            if isinstance(v, list):
                # Using european format
                if decimal_sep == ',':
                    v_euro = [str(el).replace('.', ',')
                              if isinstance(el, float) else el for el in v]
                    energy_flows.append([name] + v_euro)
                else:
                    energy_flows.append([name] + v)
            elif isinstance(v, dict):
                if decimal_sep == ',':
                    v_values_euro = [str(el).replace('.', ',')
                                     if isinstance(el, float) else el for el
                                     in list(v.values())]
                    energy_flows.append([name] + v_values_euro)
                else :
                    energy_flows.append([name] + list(v.values()))
            else:
                pass

    with open(file_name, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=sep)
        writer.writerows(zip(*energy_flows))


def select_csv_file_between_dates(file_path=None, start='DD/MM/YYYY HH:MM',
                                  end='DD/MM/YYYY HH:MM', sep=';'):
    # Read CSV file from path and store into dataframe df
    df = pd.read_csv(file_path, sep=sep, usecols=[0, 1], header=0,
                     names=['date', 'value'])

    # Ensure that the 'date' column is at the format datetime
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)

    # Set the date as index
    df = df.set_index(['date'])
    df.sort_index()

    # Convert start and end into the format datetime
    start = pd.to_datetime(start, dayfirst=True)
    end = pd.to_datetime(end, dayfirst=True)

    # Select from start to end
    selected_df = df.loc[start: end]

    return selected_df['value']


def def_abs_value(quantity, q_min, q_max):
    """

    :param quantity: Quantity whose absolute value is wanted
    :param q_min: Minimal value of the quantity (negative value)
    :param q_max: Maximal value of the quantity (positive value)

    :return: A new Quantity whose values equal absolute values of the
    initial Quantity
    """

    if q_max <= 0:
        raise ValueError('If q_max <= 0, the absolute value of your quantity '
                         'is -1 * quantity.')
    if q_min >= 0:
        raise ValueError('If q_min >= 0, the absolute value of your quantity '
                         'is your quantity.')

    q_name = getattr(quantity, 'name')
    q_len = getattr(quantity, 'vlen')
    parent = getattr(quantity, 'parent')

    abs_value = Quantity(name='{}_abs'.format(q_name), opt=True, lb=0,
                         ub=q_max, vlen=q_len, parent=parent)
    value_pos = Quantity(name='{}_pos'.format(q_name), opt=True, lb=0, ub=q_max,
                         vlen=q_len, parent=parent)
    value_neg = Quantity(name='{}_neg'.format(q_name), opt=True, lb=0,
                         ub=-q_min, vlen=q_len, parent=parent)
    is_pos = Quantity(name='is_{}_pos'.format(q_name), opt=True, vtype=LpBinary,
                      vlen=q_len, parent=parent)

    setattr(parent, '{}_abs'.format(q_name), abs_value)
    setattr(parent, '{}_pos'.format(q_name), value_pos)
    setattr(parent, '{}_neg'.format(q_name), value_neg)
    setattr(parent, 'is_{}_pos'.format(q_name), is_pos)

    if q_len == 1:
        set_decomp = Constraint(
            exp='{0}_{1} == {0}_{1}_pos - {0}_{1}_neg'.format(parent.name,
                                                              q_name),
            name='set_{}_decomp'.format(q_name), parent=parent)

        set_if_pos = Constraint(
            exp='{0}_{1}_pos <= {2} * {0}_is_{1}_pos'.format(parent.name,
                                                             q_name, q_max),
            name='set_if_{}_pos'.format(q_name), parent=parent)

        set_if_neg = Constraint(
            exp='{0}_{1}_neg <= {2} * ({0}_is_{1}_pos - 1)'.format(parent.name,
                                                                   q_name,
                                                                   q_min),
            name='set_if_{}_neg'.format(q_name), parent=parent)
        set_abs = Constraint(
            exp='{0}_{1}_abs == {0}_{1}_pos + {0}_{1}_neg'.format(parent.name,
                                                                  q_name),
            name='set_{}_abs'.format(q_name), parent=parent)

    elif q_len > 1:
        set_decomp = DynamicConstraint(
            exp_t='{0}_{1}[t] == {0}_{1}_pos[t] - {0}_{1}_neg[t]'.format(
                parent.name, q_name),
            name='set_{}_decomp'.format(q_name), parent=parent)

        set_if_pos = DynamicConstraint(
            exp_t='{0}_{1}_pos[t] <= {2} * {0}_is_{1}_pos[t]'.format(
                parent.name, q_name, q_max),
            name='set_if_{}_pos'.format(q_name), parent=parent)

        set_if_neg = DynamicConstraint(
            exp_t='{0}_{1}_neg[t] <= {2} * ({0}_is_{1}_pos[t] - 1)'.format(
                parent.name, q_name, q_min),
            name='set_if_{}_neg'.format(q_name), parent=parent)

        set_abs = DynamicConstraint(
            exp_t='{0}_{1}_abs[t] == {0}_{1}_pos[t] + {0}_{1}_neg[t]'.format(
                parent.name, q_name),
            name='set_{}_abs'.format(q_name), parent=parent)

    setattr(parent, 'set_{}_decomp'.format(q_name), set_decomp)
    setattr(parent, 'set_if_{}_pos'.format(q_name), set_if_pos)
    setattr(parent, 'set_if_{}_neg'.format(q_name), set_if_neg)
    setattr(parent, 'set_{}_abs'.format(q_name), set_abs)

    return abs_value