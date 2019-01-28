import matplotlib.pyplot as plt
import numpy as np
from .mass_spectrometer_file_reader import MassSpectrometerFileReader
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot
import warnings


class MassSpectrometer:

    def __init__(self, filename=None,gridfs=None):
        if filename is not None:
            self.filename = filename
            data = MassSpectrometerFileReader.read_data_from_file(filename)
        elif gridfs is not None:
            self.filename = 'Gridfs'
            data = MassSpectrometerFileReader.read_data_from_gridfs(gridfs)
        self.start_time = data['start time']
        self.end_time = data['end time']
        self.gases = data['gases']
        self.acquired_data = data['acquired data']
        self.is_corrected_for_drifting = False

    def plot(self, gas, ax, color=None):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        x = self.acquired_data[gas]['Time Relative [s]']
        y = self.acquired_data[gas]['Ion Current [A]']
        if ax is not None:
            ax.plot(x, y, color=color)
            ax.set_yscale('log')
            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Ion Current [A]')
            return ax
        ax = plt.plot(x, y, color=color)
        plt.gca().set_yscale('log')
        plt.gca().set_xlabel('Time [s]')
        plt.gca().set_ylabel('Ion Current [A]')
        return ax

    def plot_all(self, ax=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        for gas in self.gases:
            ax = self.plot(gas=gas,ax=ax)
        ax.set_yscale('log')
        ax.set_xlabel('Time [s]')
        ax.set_xlabel('Ion Current [A]')
        ax.legend(self.gases)
        return ax

    def get_ion_current(self, gas,range=None):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        ion_current = self.acquired_data[gas]['Ion Current [A]']
        if range:
            time = self.get_time_relative(gas)
            start_index = MassSpectrometer._find_index_of_nearest(time,range[0])
            end_index = MassSpectrometer._find_index_of_nearest(time,range[1])
            return np.array(ion_current[start_index:end_index])
        return np.array(ion_current)

    def get_time_relative(self, gas,range=None):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        time_relative = self.acquired_data[gas]['Time Relative [s]']
        if range:
            start_index = MassSpectrometer._find_index_of_nearest(time_relative,range[0])
            end_index = MassSpectrometer._find_index_of_nearest(time_relative,range[1])
            return np.array(time_relative[start_index:end_index])
        return np.array(time_relative)

    def get_time(self, gas):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        return np.array(self.acquired_data[gas]['Time'])

    def shift_start_time_back(self, time):
        self.start_time = self.start_time - time
        self.end_time = self.end_time - time
        for gas in self.gases:
            for index in range(0, len(self.acquired_data[gas]['Time Relative [s]'])):
                self.acquired_data[gas]['Time Relative [s]'][index] = self.acquired_data[gas]['Time Relative [s]'][
                                                                          index] + time

    def plotly_all(self,title=''):
        init_notebook_mode(connected=True)
        data = []
        for gas in self.gases:
            x = self.acquired_data[gas]['Time Relative [s]']
            y = self.acquired_data[gas]['Ion Current [A]']
            trace = MassSpectrometer._create_x_y_trace(x, y, gas)
            data.append(trace)
        layout = MassSpectrometer._get_plotly_layout(title)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)

    def correct_for_drifting(self,correction_gas='Ar'):
        if self.is_corrected_for_drifting:
            warnings.warn('Ion current is already corrected for drifting. No further correctrion was performed.')
            return
        correction_current = self.get_ion_current(correction_gas)
        mean_correction_current = np.mean(correction_current)
        for gas in self.gases:
            min_length =int(min(len(correction_current),len(self.acquired_data[gas]['Ion Current [A]'])))
            for n in range(0,min_length-1):
                self.acquired_data[gas]['Ion Current [A]'][n] = self.acquired_data[gas]['Ion Current [A]'][n]*mean_correction_current/correction_current[n]
        self.is_corrected_for_drifting = True

    def get_ion_current_at_time(self,time,gas):
        index = self._find_index_of_nearest(self.get_time_relative(gas),time)
        return self.get_ion_current(gas)[index]

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(np.array(array) - value)).argmin()

    @staticmethod
    def _create_x_y_trace(x, y, name):
        return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
            title=title,
            xaxis=dict(
                title='Time [s]',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title='Ion Current [A]',
                type='log',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                ),
                exponentformat='e',
                showexponent='all'
            )
        )
