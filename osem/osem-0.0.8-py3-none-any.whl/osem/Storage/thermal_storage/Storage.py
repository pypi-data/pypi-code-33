from __future__ import division
from Layer import Layer
from math import pi


class Storage:
    """
    Create a storage entity divided in layers. Each layer is matched to associated flows and energy equation.
    Ports can either correspond to an inlet or an outlet of water. There are physical entities described by a height and
    a flow (and a temperature for inlet ports).
    """
    def __init__(self, system_parameters):
        
        self.system_parameters = system_parameters
        
        self.diameter = system_parameters["diameter"]
        self.height = system_parameters["height"]
        self.lateral_surface_area = pi * self.diameter * self.height
        self.circle_surface_area = pi * self.diameter ** 2 / 4
        self.volume = self.height * self.circle_surface_area

        # We assume that the tank is insulated the same on each side
        self.u_tot = system_parameters["U_tot"]
        self.t_env = system_parameters["env_temp"]

        self.nb_of_layers = system_parameters["nb_of_layers"]
        self.layer_height = self.height / self.nb_of_layers
        self.layer_volume = self.volume / self.nb_of_layers
        self.layer_lateral_surface = self.lateral_surface_area / self.nb_of_layers

        self.up_down_flows = None

        self.layers = []

        self.q_inj = []    # Nm3/s

    def add_layer(self, layer_name):
        lay = Layer(self.layer_volume, layer_name)
        self.layers.append(lay)
        return self.layers

    # Create a function that returns a matrix of temperature variation expression for each layer
    def create_dynamic_energy_equations_system(self, layer_mass, layer_height, rho_fluid, cp_mass, lambda_corr):
        def equations_system(y, t, flows_in_vect, temp_in_vect, flows_out_vect, up_down_flows_vect):
            # t is the time parameter, representing the time step
            # flows_in_vect is the list of inlet flows in the tank during a time step
            # temp_in_vect is the list of inlet temperatures (corresponding to flows_in_vect) during a time step
            # flows_out_vect is the list of outlet flows in the tank during a time step
            # up_down_flows_vect is the list of flows circulating between layers during a time step
            dydt = []

            for idx, x in enumerate(zip(flows_in_vect, temp_in_vect, flows_out_vect)):
                # Energy variations due to ports' flows
                delta_ener_port = (x[0] * x[1] + x[2] * y[idx])

                # Energy variation due to flows inside the storage
                if up_down_flows_vect[idx] >= 0:
                    if up_down_flows_vect[idx + 1] > 0:
                        eq = y[idx + 1] * up_down_flows_vect[idx + 1] - y[idx] * up_down_flows_vect[idx]
                    else:
                        eq = y[idx] * up_down_flows_vect[idx + 1] - y[idx] * up_down_flows_vect[idx]

                else:
                    if up_down_flows_vect[idx + 1] > 0:
                        eq = y[idx + 1] * up_down_flows_vect[idx + 1] - y[idx - 1] * up_down_flows_vect[idx]
                    else:
                        eq = y[idx] * up_down_flows_vect[idx + 1] - y[idx - 1] * up_down_flows_vect[idx]

                # Energy variations due to convection with the environment and conduction between layers
                if idx == 0:
                    phi_conv = (self.circle_surface_area + self.layer_lateral_surface) * self.u_tot * (self.t_env - y[idx])
                    phi_cond = - lambda_corr * self.circle_surface_area * (y[idx] - y[idx + 1]) / layer_height
                elif idx == len(self.layers) - 1:
                    phi_conv = (self.circle_surface_area + self.layer_lateral_surface) * self.u_tot * (self.t_env - y[idx])
                    phi_cond = lambda_corr * self.circle_surface_area * (y[idx - 1] - y[idx]) / layer_height
                else:
                    phi_conv = self.layer_lateral_surface * self.u_tot * (self.t_env - y[idx])
                    phi_cond = lambda_corr * self.circle_surface_area * (y[idx - 1] - 2 * y[idx] + y[idx + 1]) \
                        / layer_height

                eq += delta_ener_port
                eq *= rho_fluid * cp_mass
                eq += phi_conv + phi_cond
                eq /= layer_mass * cp_mass
                dydt.append(eq)
            return dydt
        return equations_system

    # Add layers to the storage and initialize their parameters with zeros
    def add_and_instantiate_layers(self, nb_of_layers, nb_time_step):
        for idx in range(0, nb_of_layers):
            self.add_layer('lay_{0}'.format(idx))
            new_layer = self.layers[idx]

            new_layer.temp_in = [0] * nb_time_step
            new_layer.q_in = [0] * nb_time_step
            new_layer.q_out = [0] * nb_time_step
            new_layer.q_top = [0] * nb_time_step
            new_layer.q_bot = [0] * nb_time_step

    # Match inlet temperatures and flows to the corresponding layer depending on inlet ports heights
    # Match outlet flows depending on outlet ports heights
    def match_ports_height_with_layers(self, port_in, port_out, layer_pct):
        for idx, lay in enumerate(self.layers):

            for idt, temp in enumerate(lay.temp_in):
                list_temp = []
                list_q = []
                for key, dict_port in port_in.items():
                    if dict_port["height"] <= 1 - idx * layer_pct:
                        if dict_port["height"] > 1 - (idx + 1) * layer_pct:
                            list_q.append(dict_port["flow_in"][idt])
                            list_temp.append(dict_port["temp_in"][idt])
                    lay.q_in[idt] = sum(list_q)

                    # if there are several inlets at the same height, add flows together and calculate resulting
                    # average temperature
                    if lay.q_in[idt] != 0:
                        lay.temp_in[idt] = sum([q * t / lay.q_in[idt] for q, t in zip(list_q, list_temp)])
        for key, dict_port in port_out.items():
            for idx, lay in enumerate(self.layers):
                for idt, flow in enumerate(lay.q_out):
                    if dict_port["height"] <= 1 - idx * layer_pct:
                        if dict_port["height"] > 1 - (idx + 1) * layer_pct:
                            lay.q_out[idt] += -dict_port["flow_out"][idt]  # sign '-' to respect convention 'out <-> <0'

    # if the storage mass balance is not respected, calculate the injected or rejected flow
    def calculate_missing_flow(self, nb_time_step):
        for idt in range(0, nb_time_step):
            sum_in = 0
            sum_out = 0
            for idx, lay in enumerate(self.layers):
                sum_in += lay.q_in[idt]
                sum_out += lay.q_out[idt]
            missing_flow = -round(sum_out + sum_in, 7)
            self.q_inj.append(missing_flow)

    # if the injected or rejected flow is not zero, add it to the bottom layer
    def add_missing_flow_to_bottom_layer(self, nb_time_step, water_temp_in):
        for idt in range(0, nb_time_step):
            bot_layer = self.layers[-1]
            if self.q_inj[idt] > 0:
                # if there is already a flow at the bottom layer, calculate the average injected temperature
                # and sum the flows
                bot_layer.temp_in[idt] = (bot_layer.temp_in[idt] * bot_layer.q_in[idt] + self.q_inj[idt] * water_temp_in) / \
                                         (bot_layer.q_in[idt] + self.q_inj[idt])
                bot_layer.q_in[idt] += self.q_inj[idt]
            elif self.q_inj[idt] < 0:
                bot_layer.q_out[idt] += self.q_inj[idt]

    # Calculate the flows that occur in the storage between layers (due to inlet and outlet flows)
    def calculate_hydraulic_balance(self, nb_time_step):
        self.up_down_flows = []
        for idt in range(0, nb_time_step):
            up_down = [0.0]
            for idx, lay in enumerate(self.layers):
                new_flow = round(up_down[idx] - lay.q_in[idt] - lay.q_out[idt], 7)
                up_down.append(new_flow)
                lay.q_top[idt] = up_down[idx]
                lay.q_bot[idt] = up_down[idx + 1]
            self.up_down_flows.append(up_down)
