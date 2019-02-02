""" Outlines UI behaviour.

UI is presented by outputting the same number of columns and rows as the connected
tty.

The UI is constructed of several :class:`pingstats.ui.PingsPane` derivative classes.
Each of these classes outputs different types of information to the display. Each
type of derivative class has similar output:

  Where objects with the following in their names have the listed effect:

    - ``Status``

      - A single line display of simple information. For example, the number of
        packets being displayed for a given measure (:class:`pingstats.ui.RealtimeStatus`
        or :ref`pingstats.ui.AverageStatus`) or a simple display of ping target
        and program version.

    - ``Plot``

      - A plot based on :class:`hipsterplot` plotting functionality. Each plot
        displays particular information (:class:`pingstats.ui.RealtimePlot` displays
        a plot of realtime ping data, :class:`pingstats.ui.AveragePlot` displays
        a plot of the average of those realtime data points.

    - ``Pane``

      - Some combination of ``Status`` and ``Plot`` widgets.

The :class:`pingstats.ui.Runner` class provides functionality for dynamically executing
the UI. For example, given the command line argument ``-l realtimepane,progstatus,averagepane``
produces the default display of the software.

---
"""
from . import Pings
from . import PROG_NAME, __version__, X_COLUMN_SCALE, Y_ROW_SCALE
from . import plot_pings

import inspect
import sys
from shutil import get_terminal_size
from argparse import ArgumentParser
from time import sleep
from os import name


class Pane:
    """ Base class for all UI elements. Defines columns and rows. """
    def __init__(self, columns, rows):
        """ Instantiates self.columns and self.rows

        :columns: The total number of columns available for display.
        :rows: The total number of rows available for display.
        """
        self.columns = columns
        self.rows = rows  # - Y_ROW_SCALE


class PingsPane(Pane):
    """ Adds realtime and average data objects to self """
    def __init__(self, columns, rows, pings_object):
        """ Instantiate self.columns, self.rows, self.realtime_data, self.average_data

        :columns: The total number of columns available for display.
        :rows: The total number of rows available for display.
        :pings_object: An instance of :meth:`pingstats.Pings`
        """
        super(PingsPane, self).__init__(columns, rows)
        self.address = pings_object.address
        self.realtime_data = pings_object.realtime_data
        self.average_data = pings_object.average_data
        self.current_line = pings_object.current_line


class ProgStatus(PingsPane):
    """ Displays Program information, and a separator bar.

    Example output:
        >>> "pingstats V0.9 ------------------------ ping data from 127.0.0.1
    """
    def __init__(self, *args):
        super(ProgStatus, self).__init__(*args)
        left = '%s %s ' % (PROG_NAME, __version__)
        right = ' ping data from %s' % self.address

        for i in range(self.columns - (len(left) + len(right))):
            left += '-'

        print(left + right)


class RealtimeStatus(PingsPane):
    """ Displays information about real-time data, and packets dropped.

    Example output:
        >>> "Displaying 12 packets from 127.0.0.1"
                                     - OR -
        >>> "3 packets dropped of 12"
    """
    def __init__(self, *args):
        super(RealtimeStatus, self).__init__(*args)
        status_string = ''
        if self.realtime_data.count(-1) == 1:
            status_string += '1 packet dropped of %s' % len(self.realtime_data)
        elif self.realtime_data.count(-1) > 1:
            status_string += '%s packets dropped of %s' % (self.realtime_data.count(-1), len(self.realtime_data))
        else:
            status_string += 'Displaying %s total packets from %s' % (len(self.realtime_data), self.address)

        print(status_string.center(self.columns))


class AverageStatus(PingsPane):
    """ Displays information about average data, and if the connection was dropped.

    Example output:
        >>> "Displaying the average of 12 total packets from 127.0.0.1"
                                     - OR -
        >>> "Connection dropped!"
    """
    def __init__(self, *args):
        super(AverageStatus, self).__init__(*args)
        if sum(self.average_data) / len(self.average_data) < 0:
            print('Connection dropped!'.center(self.columns))
        else:
            string = ('Displaying the average of %s total packets from %s'
                      % (len(self.average_data), self.address))
            print(string.center(self.columns))


class RawStatus(PingsPane):
    """ Displays the current data line from the original call to ping. """
    def __init__(self, *args):
        super(RawStatus, self).__init__(*args)
        print(self.current_line.center(self.columns, '-'))


class DroppedStatus(PingsPane):
    """ Displays how many packets have been dropped if any, otherwise the program name.
    """
    def __init__(self, *args):
        super(DroppedStatus, self).__init__(*args)
        if self.realtime_data.count(-1):
            status_string = '%i packets dropped of %i from %s' % (
                self.realtime_data.count(-1), len(self.realtime_data), self.address
            )
        else:
            status_string = '%s %s - %s' % (PROG_NAME, __version__, self.address)

        print(status_string.center(self.columns, '-'))


class PlotPane(PingsPane):
    """ Applies :py:data:`pingstats.X_COLUMN_SCALE` to self.columns. """
    def __init__(self, *args):
        super(PlotPane, self).__init__(*args)
        self.columns -= X_COLUMN_SCALE
        self.rows -= Y_ROW_SCALE


class RealtimePlot(PlotPane):
    """ Displays real-time data on a plot. """
    def __init__(self, *args):
        super(RealtimePlot, self).__init__(*args)
        plot_pings(self.realtime_data, self.columns, self.rows)


class AveragePlot(PlotPane):
    """ Displays average data on a plot. """
    def __init__(self, *args):
        super(AveragePlot, self).__init__(*args)
        plot_pings(self.average_data, self.columns, self.rows)


class RealtimePane(PlotPane):
    """ Displays real-time data on a plot, along with the output of
    :py:meth:`pingstats.ui.RealtimeStatus`. """
    def __init__(self, columns, rows, pings):
        columns, rows, pings = columns, rows, pings
        super(RealtimePane, self).__init__(columns, rows, pings)
        rows = rows - 1
        RealtimePlot(columns, rows, pings)
        RealtimeStatus(columns, rows, pings)


class AveragePane(PlotPane):
    """ Displays average data on a plot, along with the output of
    :py:meth:`pingstats.ui.AverageStatus`. """
    def __init__(self, columns, rows, pings):
        columns, rows, pings = columns, rows, pings
        super(AveragePane, self).__init__(columns, rows, pings)
        rows = rows - 1
        AveragePlot(columns, rows, pings)
        AverageStatus(columns, rows, pings)


def print_widgets():
    widgets_string = 'Available Widgets are as follows:\n'
    for member in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(member[1], PingsPane):
            if not member[0].count('PingsPane') and not member[0].count('PlotPane'):
                widgets_string += '\n    %s - %s' % (member[0], str(member[1].__doc__).split('\n')[0])

    return widgets_string


parser = ArgumentParser(prog=PROG_NAME)

parser.add_argument('address', help='The address to ping. This could be either '
                    'a web address (i.e, "google.ca") or an IP address.')

parser.add_argument('-l', '--layout', default='realtimepane,progstatus,averagepane',
                    help="Specify a UI layout by listing ui elements in a comma "
                    "separated list where 'realtimepane,progstatus,averagepane' "
                    "displays the default layout. See the docs for more "
                    "information. ")

parser.add_argument('--list-widgets', action='store_true',
                    help="Output a list of available widgets for '-l'")

parser.add_argument('-V', '--version', action='version',
                    version='%(prog)s {}'.format(__version__))


class Runner:
    """ Layout strings can be constructed by a comment separated list of class names.
    For example, the following:
    ::

        realtimeplot,progstatus,averageplot

    Yields the following classes:
    ::

        [pingstats.ui.RealtimePlot, pingstats.ui.ProgStatus, pingstats.ui.AveragePlot]

    Please note. These class names must be exact, a misspelled class name will result in none being returned.
    """

    def __init__(self, argv=None):
        if sys.argv.count('--list-widgets'):
            print(print_widgets())
            exit(0)

        if argv is not None:

            parsed = parser.parse_args(argv)

        else:
            parsed = parser.parse_args()

        pings = Pings(parsed.address)
        try:
            for ping in pings:
                columns, rows = get_terminal_size()

                num_plots = parsed.layout.count('pane') + parsed.layout.count('plot')
                num_status = parsed.layout.count('status')

                num_status = num_status if name != 'nt' else num_status * 2
                modifier = 1 if name != 'nt' else 2  # account for input line, modified by os

                if num_plots < 1:
                    plot_rows = 1
                else:
                    plot_rows = int((rows - num_status - modifier) / num_plots)

                for member in self.yield_layout(parsed.layout):
                    if member[0].lower().count('status'):
                        member[1](columns, 1, pings)
                    else:
                        member[1](columns, int(plot_rows), pings)

                # If, on round down, we have displayed fewer rows than there are
                # available on the STDOUT, print lines to make up for difference
                for i in range(rows - (plot_rows * num_plots) - num_status - modifier):
                    print('')

                sleep(0.5)
        except KeyboardInterrupt:
            pass

    def yield_layout(self, layout_str):
        """ Returns objects for each object in the layout string.

        Yields a tuple with the following layout:
        ::

            [0] = Class name as string
            [1] = Class object
        """
        for layout_class in layout_str.split(','):
            for member in inspect.getmembers(sys.modules[__name__], inspect.isclass):
                if member[0].lower() == layout_class.lower():
                    yield member


def _run(argv=None):  # DEBUG: NEEDS TESTING
    Runner(argv)
