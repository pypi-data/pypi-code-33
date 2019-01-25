#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# This file is part of the NNGT project to generate and analyze
# neuronal networks and their activity.
# Copyright (C) 2015-2017  Tanguy Fardet
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Use NNGT to analyze NEST-simulated activity taking the underlying network
structure into account.
"""

import nngt
import nngt.generation as ng


'''
Create a network oscillatory neurons
'''

#~ param_oscillators = {
    #~ 'E_L': -65., 'V_th': -55., 'b': 30., 'tau_w': 500.,
    #~ 'V_reset': -65., 't_ref': 1., 'g_L': 10., 'C_m': 250., 'I_e': 300.
#~ }
param_adaptive = {
    'E_L': -60., 'V_th': -55., 'b': 30., 'tau_w': 500.,
    'V_reset': -65., 't_ref': 1., 'g_L': 10., 'C_m': 250., 'I_e': 0.
}

pop = nngt.NeuralPop.uniform(
    #~ size=1000, neuron_model='aeif_psc_alpha', neuron_param=param_oscillators)
    size=1000, neuron_model='aeif_psc_alpha', neuron_param=param_adaptive)

net = ng.distance_rule(scale=400., avg_deg=100, population=pop, weights=70.)

'''
Send the network to NEST, set noise and randomize parameters
'''

if nngt.get_config('with_nest'):
    import nngt.simulation as ns
    import nest

    nest.SetKernelStatus({'local_num_threads': 4})

    gids = net.to_nest()

    ns.randomize_neural_states(
        net, {"w": ("uniform", 50., 200.), "I_e": ("uniform", 60., 70.)})

    ns.set_minis(net, base_rate=0.1, weight=30.)

    recorder, record = ns.monitor_nodes(gids, network=net)

    nest.Simulate(5000.)

    if nngt.get_config('with_plot'):
        ns.plot_activity(
            recorder, record, network=net, sort="I_e", show=False)
        ns.plot_activity(
            recorder, record, network=net, sort="in-degree", show=False)
        sort  = net.get_degrees("in")
        ns.plot_activity(recorder, record, network=net, sort=sort, show=True)
