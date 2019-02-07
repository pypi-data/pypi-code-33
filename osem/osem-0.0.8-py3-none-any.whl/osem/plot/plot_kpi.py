"""
This functions plot different kpi
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import osem.general.conf as conf
from osem.access_data import kpi


def plot_c02(data_kpi, fig_name, title_name='', ylabel=conf.ylabelco2, color=None, xlabel=conf.xlabel,
                       fontsize=conf.fontsize, width=conf.width, figsize=conf.figsize, show=True):
    """
    This function creates a stacked bar plot with bar grouped by scenarios for different years. It is used to plot
    c02 emission.

    It needs a pandas dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
    The value in the dataframe are the useful energy

    :param data_kpi: the data for useful energy as described above.
    :param fig_name: the name of the figure (with path if necessary)
    :param ylabel: the label for the y-axis (depends on the kpi plotted)
    :param color: the color of the plot (must be of of len > number of technology)
    :param titlelabel: the title of the plot
    :param xlabel: the label for the xaxis
    :param fontsize: the size of the font
    :param width: the width of the bar
    :param show: If True the figure is shown otherwise not
    """

    # compute value
    mykpi = kpi.Kpi()
    co2emission = mykpi.get_co2_emission(data_kpi)

    # create figure
    _scenarios_kpi_plot(co2emission, fig_name, title_name, ylabel, color, xlabel, fontsize, width, figsize, show)


def plot_final_energy(data_kpi, fig_name, title_name='', ylabel=conf.ylabelfinal, color=None, xlabel=conf.xlabel,
                       fontsize=conf.fontsize, width=conf.width, figsize=conf.figsize, show=True):
    """
        This function creates a stacked bar plot with bar grouped by scenarios for different years. It is used to plot
        the final energy.

        It needs a pandas dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
        The value in the dataframe are the useful energy.

        :param data_kpi: the data for useful energy formatted as described above.
        :param fig_name: the name of the figure (with path if necessary)
        :param ylabel: the label for the y-axis (depends on the kpi plotted)
        :param color: the color of the plot (must be of of len > number of technology)
        :param titlelabel: the title of the plot
        :param xlabel: the label for the xaxis
        :param fontsize: the size of the font
        :param width: the width of the bar
        :param show: If True the figure is shown otherwise not
        """

    # compute value
    mykpi = kpi.Kpi()
    final_energy = mykpi.get_energy_final(data_kpi)

    # make figure
    _scenarios_kpi_plot(final_energy, fig_name, title_name, ylabel, color, xlabel, fontsize, width, figsize, show)


def plot_primary_energy(data_kpi, fig_name, title_name='', ylabel=conf.ylabelprimary, color=None, xlabel=conf.xlabel,
                      fontsize=conf.fontsize, width=conf.width, figsize=conf.figsize, show=True):
    """
    This function creates a stacked bar plot with bar grouped by scenarios for different years. It is used to plot
    primary energy.

    It needs a pandas dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
    The value in the dataframe are the usefule energy.

    :param data_kpi: the data for useful energy as described above.
    :param fig_name: the name of the figure (with path if necessary)
    :param ylabel: the label for the y-axis (depends on the kpi plotted)
    :param color: the color of the plot (must be of of len > number of technology)
    :param titlelabel: the title of the plot
    :param xlabel: the label for the xaxis
    :param fontsize: the size of the font
    :param width: the width of the bar
    :param show: If True the figure is shown otherwise not
    """
    # compute value
    mykpi = kpi.Kpi()
    primary_energy = mykpi.get_energy_primary(data_kpi)

    _scenarios_kpi_plot(primary_energy, fig_name, title_name, ylabel, color, xlabel, fontsize, width, figsize, show)


def plot_renewable_energy(data_kpi, fig_name, title_name='', ylabel=conf.ylabelrenew, color=None, xlabel=conf.xlabel,
                      fontsize=conf.fontsize, width=conf.width, figsize=conf.figsize, show=True, return_fig=True):
    """
    This function creates a stacked bar plot with bar grouped by scenarios for different years. It is used to plot
    primary emission.

    It needs a pandas dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
    The value in the dataframe are the kpi which needs plotting.

    :param data_kpi: the data for thec02 emission formated as described above.
    :param fig_name: the name of the figure (with path if necessary)
    :param ylabel: the label for the y-axis (depends on the kpi plotted)
    :param color: the color of the plot (must be of of len > number of technology)
    :param titlelabel: the title of the plot
    :param xlabel: the label for the xaxis
    :param fontsize: the size of the font
    :param width: the width of the bar
    :param show: If True the figure is shown otherwise not
    """
    # create renewable dataframe
    renew_out = pd.DataFrame(0, index=data_kpi.index, columns=conf.renew_colname)
    renew_out['years'] = data_kpi['years']
    renew_out['scenarios'] = data_kpi['scenarios']

    # compute value
    mykpi = kpi.Kpi()
    primary_energy = mykpi.get_energy_primary(data_kpi).iloc[:,2:]
    renew_data = mykpi.get_renewable_part(data_kpi).iloc[:,2:]

    # sum for all tech and spearate between renew and not renew
    renew_data = renew_data.sum(axis=1)
    primary_energy = primary_energy.sum(axis=1)
    renew_out.iloc[:, 2] = renew_data
    renew_out.iloc[:, 3] = primary_energy - renew_data

    _scenarios_kpi_plot(renew_out, fig_name, title_name, ylabel, color, xlabel, fontsize, width, figsize, show)


def _scenarios_kpi_plot(data_kpi, fig_name, title_name, ylabel, color=None, xlabel=conf.xlabel,
                       fontsize=conf.fontsize, width=conf.width, figsize=conf.figsize, show=True):
    """
    This function creates a stacked bar plot with bar grouped by scenarios for different years. It is used to plot
    c02 emission, final energy and so forth.

    It needs a pandas dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
    The value in the dataframe are the kpi which needs plotting.

    :param data_kpi: the data for the  kpi formated as described above.
    :param fig_name: the name of the figure (with path if necessary)
    :param ylabel: the label for the y-axis (depends on the kpi plotted)
    :param color: the color of the plot (must be of of len > number of technology)
    :param titlelabel: the title of the plot
    :param xlabel: the label for the xaxis
    :param fontsize: the size of the font
    :param width: the width of the bar
    :param show: If True the figure is shown otherwise not
    """

    # manage data
    scenarios = data_kpi['scenarios'].unique()
    years = data_kpi['years'].unique()
    tech_name = data_kpi.columns[2:]
    year_ind = np.arange(len(years), dtype=float)

    # get color and font size
    if color is None:
        color = np.random.rand(len(tech_name), 3)
    plt.rcParams.update({'font.size': fontsize})

    # check that each years is present in all scenarios
    for sce in scenarios:
        years_sce = data_kpi.loc[data_kpi['scenarios'] == sce, 'years']
        if np.any(years != years_sce.values):
            raise ValueError('Each scenarios must be computed for the same years')

    # create figure
    plt.figure(figsize=figsize)
    ax1 = plt.subplot(1, 1, 1)
    plt.title(title_name)
    plt.ylabel(ylabel)

    # position axis ticks
    pos_year = year_ind + (width * len(scenarios)) / 2 + width / 2
    pos_sce = []

    # stacked bar plot
    for sce in scenarios:
        year_ind += width
        pos_sce.extend(year_ind)
        bottom_col = np.zeros(len(years))
        for i, t in enumerate(tech_name):
            data_sce_t = data_kpi.loc[data_kpi['scenarios'] == sce, t]
            if color is not None:
                plt.bar(year_ind, data_sce_t, width=width * 0.9, color=color[i], bottom=bottom_col)
            else:
                plt.bar(year_ind, data_sce_t, width=width * 0.9, color=color[:, i], bottom=bottom_col)
            bottom_col += data_sce_t
    plt.legend(tech_name)

    # Set second x-axis
    plt.xlim(0, len(year_ind))
    ax1.set_xticks(pos_sce)
    ax1.set_xticklabels(data_kpi['scenarios'], fontsize=fontsize)
    ax2 = ax1.twiny()
    ax2.set_xticks(pos_year)
    ax2.set_xticklabels(years, fontsize=fontsize)
    ax2.xaxis.set_ticks_position('bottom')  # set the position of the second x-axis to bottom
    ax2.xaxis.set_label_position('bottom')
    ax2.spines['bottom'].set_position(('outward', 36))
    ax2.set_xlim(ax1.get_xlim())
    plt.xlabel(xlabel)
    plt.xlim([0, len(year_ind)])
    plt.tight_layout()

    # show and save
    plt.savefig(fig_name)
    if show:
        plt.show()