'''
Class for interfacing between the calculator and the user.

MAGIC
@author: Isobel
'''
import matplotlib.pyplot as plt
import seaborn as sns
from copy import deepcopy
import numpy as np
import datetime as dt
import h5py
import os
import matplotlib.backends.backend_pdf as plt_pdf
from inspect import getfile

from magic import Calculator
import magic.tools.defaultstrings as defaultstrings
import magic.tools.jsonhelper as jsonhelper
import magic.tools.parameter_tracking as parameter_tracking


class Interface:

    # Initialisation
    def __init__(self, ifo, new_parameters={}):

        self.ifo = ifo
        self.calculator = Calculator(ifo)
        self.ifo_name = ifo.__class__.__name__
        # Get noise names and curves
        curves = self.calculator.get_noise_curves(
            parameters=new_parameters)

        self.names = list(curves.keys())
        self.curves = list(curves.values())

        # Initialise output file folder
        self.output_file = './output/'
        if not os.path.exists(self.output_file):
            os.makedirs(self.output_file)
        # Unit of frequency
        self.x_unit = 'Frequency f ($Hz$)'
        # Unit of strain
        self.y_unit = 'Strain h $(1/\sqrt{Hz})$'

        # Plotting attributes
        self.plotting = {}
        self.plotting['ylim'] = ifo.plotting['ylim']
        self.plotting['xlim'] = ifo.plotting['xlim']

        print(defaultstrings.flagInterfacing(self.ifo_name))

        if new_parameters:
            self.addNew(parameters=new_parameters)

    # Loop over detector changes and show the noise on each loop
    def loopDetectorChanges(self):

        # Set up empty dictionary to carry all changes
        new_parameters = {}
        loop = input(defaultstrings.instruction['make_changes'])

        while loop == 'y':
            self.makeDetectorChanges(new_parameters)
            self.showNoise()
            self.printBestSensitivity()
            loop = input(defaultstrings.instruction['make_changes'])

        print(defaultstrings.flag['final_plot'])
        self.showNoise()

    # Change user-input detector parameters
    def makeDetectorChanges(self, new_parameters={}):

        choice = input(defaultstrings.instruction['changes_or_additions'])

        if choice == 'p':
            variables = sorted(list(self.ifo.variable_keys))
            for v in variables:
                print(v)
            choice = 'y'

        while choice == 'y':

            name = input(defaultstrings.instruction['enter_param_name'])

            print(
                defaultstrings.flagOldParameter(
                    str(name), self.ifo.parameters[name]))

            value = input(defaultstrings.instruction['enter_param_val'])

            if value.startswith('B '):

                print(defaultstrings.flag['boolean_entry'])
                value = value.replace('B ', '')
                if value == 'True' or value == 'true':
                    value = True
                elif value == 'False' or value == 'false':
                    value = False

                else:
                    print(defaultstrings.flag['invalid_boolean'])

            elif value == 'l':

                print(defaultstrings.flag['list_entry'])
                value = [
                    float(x) for x in input(defaultstrings.instruction[
                        'enter_list']).split()
                ]
            else:

                print(defaultstrings.flag['single_number'])
                value = float(value)

            # Set up the new value
            new_parameters[name] = value
            choice = input(
                defaultstrings.instruction['add_or_change_or_continue'])

            # Print old values to be changed
            for key in new_parameters:
                print(
                    defaultstrings.flagOldParameter(key,
                                                    self.ifo.parameters[key]))

            # Actually do the changes
            self.addNew(parameters=new_parameters)

            # Print the new values
            for key in new_parameters:
                print(
                    defaultstrings.flagNewParameter(key,
                                                    self.ifo.parameters[key]))

    # Print properties to the screen or a text file
    def printProperties(self, toScreen=True, to_file=True):
        tab = '\t\t'
        space = ' '
        line_end = '\n'
        if to_file:
            parameter_file_name = self.output_file + self.ifo_name
            parameter_file_name += '_parameters.txt'
            parameterFile = open(parameter_file_name, 'w')
        for key in self.ifo.parameters:
            seperator = space * (25 - len(key)) + ' :' + tab
            value = self.ifo.parameters[key]

            if type(value) == tuple and len(value) > 4:
                value = 'Value length: ' + str(len(value))

            if type(value) == int \
            or type(value) == tuple \
            or type(value) == list \
            or type(value) == float:
                value = np.round(value, 3)

            value_string = str(value)
            info_string = tab + key + seperator + value_string + line_end
            if toScreen:
                print(info_string)
            if to_file:
                parameterFile.write(info_string)

    # Add new parameters or noise models to the detector
    def addNew(self, parameters=None, noise_models=None):

        if parameters is None:
            parameters = {}
        if noise_models is None:
            noise_models = {}

        print('old parameters: ')
        for key in parameters.keys():
            print(key + ' : ' + str(self.ifo.parameters[key]))

        self.ifo.reset_noise(parameters=parameters, noise_models=noise_models)

        print('new parameters: ')
        for key in parameters.keys():
            print(key + ' : ' + str(self.ifo.parameters[key]))

        # Reset names and curves
        curves = self.calculator.get_noise_curves(
            parameters=parameters)

        self.names = list(curves.keys())
        self.curves = list(curves.values())

    # Print the lowest sensitivity, and the frequency at which it occurs,
    # to the screen
    def printBestSensitivity(self):

        # Get total noise curve
        total = self.curves[-1]
        # Get best sensitivity index
        best_index = np.argmin(total.asd)
        # Get best sensitivity
        best_s = total.asd[best_index]
        # Get frequency corresponding to best sensitivity
        best_f = total.f[best_index]

        print(defaultstrings.flagBestSensitivity(best_s, best_f))

    # Display the noise plot
    def showNoise(self):

        # Set up plot
        fig = self.noisePlot()
        # Save the figure to pdf
        plt.savefig(self.output_file + self.ifo_name + '.pdf', dpi=400)
        plt.show()

    # Find the detector's range based upon a full IMR merger signal
    # (full=True) or just the inspiral section (full=False)
    def interactDetectorRange(self, full=False):

        if not full:
            print(defaultstrings.flag['inspiral_estimate'])
        else:
            print(defaultstrings.flag['imr_estimate'])

        m1 = float(input(defaultstrings.instruction['first_mass']))
        m2 = float(input(defaultstrings.instruction['second_mass']))

        D = self.calculator.calculateDetectorRange(m1, m2, full)

        print(defaultstrings.flagRange(m1, m2, D))

    # Write detector to HDF5
    def toHDF5(self, version, name):

        # Path to HDF5 file
        path = self.output_file + self.ifo_name + '_' + version + '_' + name + '.hdf5'

        # ifo model to store
        params = deepcopy(self.calculator.ifo.parameters)

        with h5py.File(path, 'w') as store:

            store.attrs['schema'] = self.ifo_name + ' Noise Budget'
            store.attrs['version'] = version
            store.attrs['name'] = name
            store.attrs['date'] = str(dt.datetime.now().isoformat())
            store.attrs['parameters'] = jsonhelper.toJSON(params)
            store.attrs['x_unit'] = self.x_unit
            store.attrs['y_unit'] = self.y_unit

            # Store an array of frequency
            store.create_dataset('frequency', data=params['frequency'])

            # Store each data set, including the total
            for n, name in enumerate(self.names):
                store.create_dataset('traces/' + name, data=self.curves[n].asd)
                # Also store separate sum for ease of later extraction
                if n == (len(self.names) - 1):
                    store.create_dataset('sum', data=self.curves[n].asd)

            print(defaultstrings.flagPath(path))

    # Read detector from HDF5, print its properties and return its parameters
    def fromHDF5(self, path):

        get = h5py.File(path, 'r')
        attrs = get.attrs
        params_json = attrs['parameters']

        for attr in attrs.keys():
            if attr != 'parameters':
                print(attr + ' : ' + str(attrs[attr]))

        for name in get:
            print(name + ' : ' + str(type(get[name])))
            if 'Group' in str(type(get[name])):
                for key in get[name].keys():
                    print('\t' + key + ' : ' + str(type(get[name][key])))
        # Parameters
        params = jsonhelper.fromJSON(params_json)

        return params

    # Print the total plot, plus individual noise plots, to a single PDF.
    # Each individual noise plot also prints, on the following page, a list of the
    # parameters that it depends on.
    def toPDF(self):

        fig = []
        dependencies = []
        models = self.ifo.noise_models
        parameters = self.ifo.parameters
        path = './'

        # Find where all of the detector's parameters are used
        noise_parameters, noise_map, utils_parameters, utils_map \
        = parameter_tracking.findParameterUses(path, parameters)

        # First plot everything
        fig.append(self.noisePlot())
        dependency_message = 'Total noise is the sum of the following noises: \n'
        for i, n in enumerate(self.names):
            if n != 'Total':
                dependency_message += n + '     '
            # Word wrap at 3 names
            if (i + 1) % 3 == 0:
                dependency_message += '\n'

        dependencies.append(dependency_message)
        # Then plot individual noises
        for name in self.names:
            if name == 'Total':
                pass
            else:
                fig.append(self.noisePlot(names=[name]))
                dependency_message = name
                dependency_message += ' noise depends on the following parameters: \n'
                path = getfile(models[name].__class__)
                path = path.split('Code')[-1]
                path = '.' + path.replace('\\', '/')

                for nmap in noise_map.keys():
                    if path == noise_map[nmap]:
                        dps = noise_parameters[nmap]

                for i, p in enumerate(dependencies):
                    dependency_message += p + '    '
                    # Word wrap at 3 parameters
                    if (i + 1) % 3 == 0:
                        dependency_message += '\n'
                dependencies.append(dependency_message)

        pdf_name = self.output_file + self.ifo_name + '_all.pdf'
        ifo_pdf = plt_pdf.PdfPages(pdf_name)

        for i, f in enumerate(fig):
            text = dependencies[i]
            # Add dependency notes on a blank plot
            t = plt.figure()
            t.text(.07, .1, text)
            ifo_pdf.savefig(f)
            ifo_pdf.savefig(t)
            plt.close(f)
            plt.close(t)

        ifo_pdf.close()
        print('Plots saved to file ' + pdf_name + '.')

    # The noise plotting itself, which will plot whichever noise curves
    # correspond to the names it's been given
    def noisePlot(self, names=None):

        if names == None:
            names = self.names
        # Set up plot
        fig = plt.figure()

        # Plot styling
        plt.style.use('seaborn-whitegrid')
        current_palette = sns.color_palette('tab20', len(self.names))

        # Now sort into alphabetical order to preserve colouring
        alpha_names = sorted(names, key=str.lower)
        # For ITM names - TODO make this more generic
        alpha_names_second = deepcopy(alpha_names)
        beta_names = []

        for a in alpha_names:
            # TODO make this more generic
            if 'ITM' in a:
                beta_names.append(a)
                alpha_names_second.remove(a)

        alpha_names = alpha_names_second

        for i, name in enumerate(alpha_names):

            curve = self.curves[self.names.index(name)]

            if i == len(alpha_names) - 1:
                lsz = 3
                lsty = '-'
                lclr = 'grey'
            else:
                lsz = 3
                lsty = '-'
                lclr = current_palette[i]

            plt.loglog(curve.f, \
                 curve.asd, \
                 label=name, \
                 lw=lsz, \
                 ls=lsty, \
                 color=lclr)

        for j, name in enumerate(beta_names):

            curve = self.curves[names.index(name)]

            lsz = 3
            lsty = '-'
            lclr = current_palette[len(alpha_names) + j]

            plt.loglog(curve.f, \
                 curve.asd, \
                 label=name, \
                 lw=lsz, \
                 ls=lsty, \
                 color=lclr)

        plt.legend(loc=1, ncol=2, fontsize=10)
        plt.xlabel(self.x_unit, fontsize=14)
        plt.ylabel(self.y_unit, fontsize=14)
        plt.grid(True, which='both')
        plt.tight_layout()
        plt.ylim(self.plotting['ylim'])
        plt.xlim(self.plotting['xlim'])

        return fig
