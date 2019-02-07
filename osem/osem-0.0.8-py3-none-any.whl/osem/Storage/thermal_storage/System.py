from __future__ import division
from Storage import Storage
from scipy.integrate import odeint
from numpy import linspace
from math import pi, cos


class System:
    """
    Simulate the behaviour of a stratified thermal storage.
    """
    def __init__(self, args):
        self.storage = None
        self.system_parameters = args
        self.results = None
        self.results_step = None

    # Create a thermocline between maximum and minimum initial temperature values
    @staticmethod
    def create_init_values_for_layers_temperatures(nbr_layer, t_min, t_max):
        x_values = linspace(0, pi, num=nbr_layer)
        coef = [(1 - cos(x)) / 2 for x in x_values]
        t_init = [(1 - c) * t_min + c * t_max for c in coef]
        t_init.reverse()
        return t_init

    # Check if there are any temperature inversions, and mix the concerned layers if there are inversions
    @staticmethod
    def check_mixing_algorithm(sol):
        # Ascending approach to find inversions and mix inverted layers
        for idt, sto_temp in enumerate(sol):
            layers_max_idx = len(sol[0]) - 1
            for idx, temp in enumerate(sto_temp):
                if idx == 0:
                    if sto_temp[layers_max_idx - idx] - sto_temp[layers_max_idx - (idx + 1)] > 0.001:
                        avg_temp = (sto_temp[layers_max_idx - idx] + sto_temp[layers_max_idx - (idx + 1)]) / 2
                        sto_temp[layers_max_idx - idx] = avg_temp
                        sto_temp[layers_max_idx - (idx + 1)] = avg_temp
                elif idx != layers_max_idx:
                    if sto_temp[layers_max_idx - idx] - sto_temp[layers_max_idx - (idx + 1)] > 0.001:
                        nb_inv = 1
                        list_idd = []
                        for idd in range(layers_max_idx - idx, layers_max_idx):
                            if sto_temp[layers_max_idx - idx] == sto_temp[idd + 1]:
                                nb_inv += 1
                                list_idd.append(idd + 1)
                        avg_temp = (nb_inv * sto_temp[layers_max_idx - idx] + sto_temp[layers_max_idx - (idx + 1)]) \
                            / (1 + nb_inv)
                        sto_temp[layers_max_idx - (idx + 1)] = avg_temp
                        sto_temp[layers_max_idx - idx] = avg_temp
                        for idd in list_idd:
                            sto_temp[idd] = avg_temp
        # Descending approach to check if there are still inversions, and in this case mix the concerned layers
        for idt, sto_temp in enumerate(sol):
            layers_max_idx = len(sol[0]) - 1
            for idx, temp in enumerate(sto_temp):
                if idx != layers_max_idx:
                    if sto_temp[idx] < sto_temp[idx + 1]:
                        nb_inv = 1
                        list_idd = []
                        for idd in range(0, idx):
                            if sto_temp[idx] == sto_temp[idd]:
                                nb_inv += 1
                                list_idd.append(idd)
                        avg_temp = (nb_inv * sto_temp[idx] + sto_temp[idx + 1]) / (1 + nb_inv)
                        sto_temp[idx + 1] = avg_temp
                        sto_temp[idx] = avg_temp
                        for idd in list_idd:
                            sto_temp[idd] = avg_temp

    # Create the storage entity from system parameters
    def create_storage(self):
        self.storage = Storage(self.system_parameters)

        layer_height = self.storage.layer_height
        storage_height = self.storage.height
        layer_pct = layer_height / storage_height
        nb_of_layers = self.system_parameters["nb_of_layers"]
        self.system_parameters["nb_time_step"] = len(self.system_parameters["ports_in"]["port_1"]["temp_in"])
        nb_time_step = self.system_parameters["nb_time_step"]
        ports_in = self.system_parameters["ports_in"]
        ports_out = self.system_parameters["ports_out"]
        inlet_water_temp = self.system_parameters["inlet_water_temp"]

        # Add layers to the storage and initialize them
        self.storage.add_and_instantiate_layers(nb_of_layers, nb_time_step)

        # Match ports' height with layers
        self.storage.match_ports_height_with_layers(ports_in, ports_out, layer_pct)

        # Calculate a possible missing flow (to respect storage mass balance)
        self.storage.calculate_missing_flow(nb_time_step)
        self.storage.add_missing_flow_to_bottom_layer(nb_time_step, inlet_water_temp)

        # Calculate flows between layers
        self.storage.calculate_hydraulic_balance(nb_time_step)

    # Simulate behaviour of the stratified storage by solving layers' energy equations for each time step
    def simulate_storage(self):
        lambda_fluid = self.system_parameters["lambda_fluid"]
        wall_thick = self.system_parameters["wall_thick"]
        lambda_wall = self.system_parameters["lambda_wall"]
        diameter = self.system_parameters["diameter"]
        lambda_corr = lambda_fluid + lambda_wall * ((diameter + 2 * wall_thick)**2 - diameter**2) / diameter**2

        rho_fluid = self.system_parameters["rho_fluid"]
        cp_mass = self.system_parameters["cp_mass_fluid"]
        layer_height = self.storage.layer_height
        layer_mass = self.storage.layer_volume * rho_fluid
        nb_layers = self.system_parameters["nb_of_layers"]
        t_min = self.system_parameters["temp_init_min"]
        t_max = self.system_parameters["temp_init_max"]

        self.system_parameters["nb_time_step"] = len(self.system_parameters["ports_in"]["port_1"]["temp_in"])

        for idt, temp in enumerate(self.system_parameters["ports_in"]["port_1"]["temp_in"]):
            if idt == 0:
                y0 = self.create_init_values_for_layers_temperatures(nb_layers, t_min, t_max)
                self.results = [[i] for i in y0]
            else:
                y0 = [layer[-1] for layer in self.results]

            flows_in_vect = [lay.q_in[idt] for lay in self.storage.layers]
            temp_flows_in_vect = [lay.temp_in[idt] for lay in self.storage.layers]
            flows_out_vect = [lay.q_out[idt] for lay in self.storage.layers]
            up_down_flows_vect = self.storage.up_down_flows[idt]

            t = linspace(idt * self.system_parameters["time_step"], (idt + 1) * self.system_parameters["time_step"],
                         self.system_parameters["nb_points_by_step"])

            syst = self.storage.create_dynamic_energy_equations_system(layer_mass, layer_height, rho_fluid, cp_mass,
                                                                       lambda_corr)
            sol = odeint(syst, y0, t, args=(flows_in_vect, temp_flows_in_vect, flows_out_vect, up_down_flows_vect)).tolist()
            self.check_mixing_algorithm(sol)

            for idx, layer in enumerate(self.results):
                layer.pop()
                layer += [round(dt[idx], 2) for dt in sol]

    # Change the results from lists of temperature by layer to lists of temperature by time step
    def layer_to_step(self):
        self.results_step = [[t_layer[idt] for t_layer in self.results] for idt, t in enumerate(self.results[0])]
