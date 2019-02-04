#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**Description**
    This  module includes the display tools

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

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from ..energy.energy_nodes import EnergyNode
from ..energy.units.production_units import ProductionUnit
from ..energy.units.storage_units import StorageUnit
from ..energy.units.consumption_units import ConsumptionUnit

__docformat__ = "restructuredtext en"


def plot_node_energetic_flows(node):
    """
    ** Description **
        This function allows to plot the energy flows through an EnergyNode
        The display is realized :
            - with histograms for production and storage flow
            - with dashed curve for consumption flow

    :param node: EnergyNode
    """
    matplotlib.style.use('seaborn')

    if not isinstance(node, EnergyNode):
        raise TypeError('The element {0} should be an EnergyNode.'.format(node))
    energy_fig = plt.figure()

    print(
        "\nPreparing to plot the energetic flows through the node {0}.".format(
            node.name))

    cons = energy_fig.add_subplot(111)
    previous_energy_production = [0] * node.time.LEN  # Build the base to the
    # bar graph

    # For all production units connected to the node
    prod_colors = ['aqua', 'maroon', 'azure', 'tomato', 'darkblue',
                   'orange', 'green', 'fuchsia', 'darkgreen', 'gold',
                   'coral', 'chocolate', 'salmon', 'saddlebrown', 'crimson',
                   'mediumvioletred']
    color_nb = 0
    flows = node.get_flows
    for flow in flows:
        print(("\tAdd power from {0}.".format(flow.parent.name)))

        label = flow.parent.name
        parent = flow.parent

        # Get the power profiles
        if isinstance(flow.value, list):
            energy_flow = flow.value
        elif isinstance(flow.value, dict):
            energy_flow = list(flow.value.values())

        # If production or import
        if isinstance(parent, ProductionUnit) or node.is_import_flow(flow):
            try:
                plt.bar(node.time.I, energy_flow,
                        bottom=[previous_energy_production[t] for t
                                in range(node.time.LEN)],
                        label=label, color=prod_colors[color_nb])
                color_nb += 1

            except IndexError:
                plt.bar(node.time.I, energy_flow,
                        bottom=[previous_energy_production[t] for t
                                in range(node.time.LEN)],
                        label=label)

            for t in range(node.time.LEN):
                previous_energy_production[t] += energy_flow[t]

        # If consumption or export
        elif isinstance(parent, ConsumptionUnit) or node.is_export_flow(flow):
            cons.plot(energy_flow, marker='.', label=label,
                      linewidth=0.8, color=prod_colors[color_nb],
                      linestyle='--')
            color_nb += 1

        # If storage
        elif isinstance(parent, StorageUnit):
            energy_discharge = list(max(-1 * p, 0) for p in energy_flow)
            energy_charge = list(min(-1 * p, 0) for p in energy_flow)

            # Plot the discharge
            try:
                plt.bar(node.time.I, energy_discharge,
                        bottom=[previous_energy_production[t] for t
                                in range(node.time.LEN)],
                        label=label + 'discharge', color=prod_colors[color_nb])
                color_nb += 1

            except IndexError:
                plt.bar(node.time.I, energy_discharge,
                        bottom=[previous_energy_production[t] for t
                                in range(node.time.LEN)],
                        label=label)

            for t in range(node.time.LEN):
                previous_energy_production[t] += energy_discharge[t]

            # Plot the charge
            plt.bar(node.time.I, energy_charge, label=label + ' charge',
                    color=prod_colors[color_nb])
            color_nb += 1

    # for flow in node._exports:
    #     export = list(flow.value.values())
    #     cons.plot(export, marker='x', label='export')

    plt.title(
        'Power flow for the units connected to the node {0}'.format(node.name))
    if node.time.DT == 1:
        plt.xlabel('Time (hours)')
        plt.ylabel("Hourly mean power (kW)")
    elif node.time.DT == 24:
        plt.xlabel('Time (days)')
        plt.ylabel("Daily total energy (kWh)")

    plt.legend()
    return plt


def plot_energy_mix(node):
    if not isinstance(node, EnergyNode):
        raise TypeError('The element {0} should be an EnergyNode.'.format(node))
    data = []
    legend = []

    _, ax = plt.subplots()
    plt.axis('equal')  # Should be a circle

    flows = node.get_flows()
    for flow in flows:
        if isinstance(flow.parent, ProductionUnit):
            energy_prod = sum(flow.value.values())
            data.append(energy_prod)
            legend.append(flow.parent.name)

    ax.pie(data, labels=legend, autopct='%1.1f%%')

    plt.title('Energy mix of the node {0}'.format(node.name))


def plot_quantity(time, q, fig=None, ax=None, color=None):
    """
    **Description**
        Function that plots a OMEGALPES.general.optimisation.elements.Quantity

    **Attributes**
        - q is the Quantity
        - fig could be None, a matplotlib.pyplot.Figure or Axes for multiple
        plots

    **Returns**
        - arg1 the matplotlib.pyplot.Figure handle object
        - arg2 the matplotlib.pyplot.Axes handle object
        - arg3 the matplotlib.pyplot.Line2D handle object
    """

    v = getattr(q, 'value')

    if fig is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    if isinstance(fig, plt.Figure):
        if ax is None:
            ax = fig.add_subplot(111)
        elif not isinstance(ax, plt.Axes):
            raise ValueError(
                'ax should be either NoneType or matplotlib.pyplot.Axes')

    if isinstance(v, (list, np.ndarray)):
        try:
            ld = ax.plot(time.I, v, 'x-', color=color)
            fig.canvas.draw()

        except ValueError:
            ld = ax.plot(np.arange(0, len(v) * time.DT, time.DT), v, 'x-',
                         color=color)

    elif isinstance(v, dict):
        ind = list(v.keys())
        val = list(v.values())
        lst = np.array([ind, val]).transpose()
        # lst = np.array([ind, val], ndmin=2)
        lst = lst[lst[:, 0].argsort()]
        ind = lst[:, 0]
        val = lst[:, 1]
        ld = ax.plot(ind * time.DT, val, 'x-', color=color)

    else:
        raise TypeError(
            'Type {0} is not supported for the plot'.format(
                type(v)))

    return ld, ax, fig
