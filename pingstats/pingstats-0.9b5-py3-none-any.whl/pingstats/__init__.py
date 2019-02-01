""" Written under the MIT license. See LICENSE for more details. For authors, refer
to AUTHORS.rst.

Example Usage:
    >>> import pingstats
    >>> for pings_real, pings_average in pingstats.get_pings('google.ca'):
    ...     pingstats.plot_pings(pings_average)
    ...
    # HIPSTERPLOT OUTPUT
"""
# For authors refer to AUTHORS.rst
# PY 2 TO 3 IMPORTS
from __future__ import print_function, with_statement

# STANDARD LIBRARY PACKAGES
from subprocess import Popen, PIPE
from shutil import get_terminal_size
from os import system, name
from argparse import ArgumentParser

import warnings
import time

# NON STANDARD LIBRARY PACKAGES
from hipsterplot import plot


__version__ = "0.9b5"
PROG_NAME = 'pingstats'

# PARSER CONFIG
parser = ArgumentParser(prog=PROG_NAME)

parser.add_argument('address', help='The address to ping. This could be either '
                    'a web address (i.e, "google.ca") or an IP address.')

parser.add_argument('-V', '--version', action='version',
                    version='%(prog)s {}'.format(__version__))

X_COLUMN_SCALE = 11 if name != 'nt' else 13
Y_ROW_SCALE = 0

# __all__ = ['Pings', 'plot_pings']


class Pings:
    """ Main logic object for obtaining ping data.

    Example Usage:
        >>> from pingstats import Pings
        >>> pings = Pings('127.0.0.1')
        >>> for realtime_times in pings:
        ...     print(pings.realtime_data)  # print the last 20 (by default) realtime samples
        ...     print(pings.average_data)
        0.1  # return time data for this iteration.
        [0.1]  # REALTIME DATA
        [0.1]  # AVERAGE DATA
        [0.1, 0.2]  # REALTIME DATA
        0.2  # return time data for this iteration.
        [0.1, 0.15000000000000002]  # AVERAGE DATA
        [0.1, 0.2, ...]  # REALTIME DATA
        0.3  # return time data for this iteration.
        [0.1, 0.15000000000000002, ...]  # AVERAGE DATA
    """
    def __init__(self, address, realtime_data=[], average_data=[], realtime_data_length=20, average_data_length=200):
        """ Instantiates data used during the ping retrieval process.

        :address: The address to send ICMP ECHO requests to.
        :realtime_data: A python list object to continue to append data to.
        :average_data: A python list object to continue to append data to.
        :realtime_data_length: The maximum size of the realtime_data list
        :average_data_length: The maximum size of the average_data list
        """

        # NOTE: Must create data copy of argument lists to ensure new instances
        # have new lists.

        self.address = address
        self.realtime_data, self.average_data = realtime_data[:], average_data[:]
        self._realtime_data_length, self._average_data_length = realtime_data_length, average_data_length
        self.current_line = ''

    def _decode_line(self, line):
        """ Decodes a line from internal ping call, returning the connection time.

        ..note: This function also correctly handles switching between POSIX
                standard ``ping.c`` and Windows NT ``ping.c`` formats.

        :line: A line returned from `get_ping.process`.
        :returns: Either the return time in milliseconds (as float), -1 on timeout,
                or None.
        """
        if line.lower().count('ttl'):
            if name != "nt":
                return float(line.split('time=')[1].split(' ')[0])
            else:
                if line.count('time<'):
                    return float(line.split('time<')[1].split(' ')[0].strip('<ms'))
                else:
                    return float(line.split('time=')[1].split(' ')[0].strip('ms'))

        elif line.lower().count('0 received' if name != 'nt' else '100% loss'):
            return -1

    def _run_subprocess(self, address):
        """ Runs a ping subprocess, passing the user specified address to the command.

        ..note: This function also correctly handles switching between POSIX standard ``ping.c``
                and Windows NT ``ping.c`` formats.

        :address: The address to request ``ICMP ECHO`` requests to (i.e 'google.ca')
        :returns: The output of the sub process (POSIX standard or Windows NT ping output)
        """
        if name != 'nt':
            process = Popen(['ping', '-c 1', address], stdout=PIPE)
        else:
            process = Popen(['ping', '-n', '1', address], stdout=PIPE)

        process.wait()
        stdout, stderr = process.communicate()
        return stdout.decode('UTF-8').splitlines()

    def __iter__(self):
        """ Iteratively spawns ``ICMP`` requests for ``self.address``.

        :yields: The return time in milliseconds
        """
        # init data
        this_time = 0
        while 1:

            for line in self._run_subprocess(self.address):
                if len(self.realtime_data) > self._realtime_data_length:  # enforce max length
                    self.realtime_data.pop(0)

                line_value = self._decode_line(line)  # get float return length from line

                if line_value is not None:
                    this_time = line_value
                    self.current_line = line
                    self.realtime_data.append(line_value)

            else:  # On end of for loop, calculate average and append it
                if len(self.average_data) == self._average_data_length:
                    self.average_data.pop(0)

                self.average_data.append(sum(self.realtime_data) / len(self.realtime_data if self.realtime_data != 0 else 1))

            yield this_time


def get_pings(address):  # TODO Needs additional Testing
    """ Yields the last set of realtime and average data points, according to user
    specified maximum.

    :address: The address to send ``ICMP ECHO`` requests to.
    """
    pings = Pings(address)
    for ping in pings:
        yield pings.realtime_data[-1], pings.average_data[-1]


def plot_pings(pings, columns=70, rows=15):
    """ Provides high level bindings to ``hipsterplot.plot`` for use with :ref:get_pings.

    :pings: A list object containing ping return times as float values, normally from :ref:get_pings
    :columns: The number of columns to draw for the plot
    :rows: The number of rows to draw for the plot
    """
    plot(pings, num_x_chars=columns, num_y_chars=rows)


def _construct_middle_line(address, columns):  # DEBUG: DEPRECATED
    """ Builds a separator line for visual prettiness.

    :address: The address currently being sent ping requests
    :columns: The total columns of the current terminal (from ``_get_tty_size``
    :returns: The separator line in string form
    """
    warnings.warn("This function will be deprecated in V0.9!", DeprecationWarning)  # DEBUG
    right_display = '%s %s ' % (PROG_NAME, __version__)
    right_display_string = ' ping data from %s' % address

    for i in range(columns - (len(right_display) + len(right_display_string))):
        right_display += '-'
    right_display += right_display_string

    return right_display


def _output_top_status(address, y, columns):  # DEBUG: DEPRECATED
    """ Outputs a status line based on standard *y* collection.

    :address: The address currently being sent ping requests
    :y: The python list tracking ping data
    :columns: The total columns of the current terminal (from ``_get_tty_size``
    :returns: None. Instead, prints data to terminal
    """
    warnings.warn("This function will be deprecated in V0.9!", DeprecationWarning)  # DEBUG
    if y.count(-1) == 1:
        print('1 packet dropped of %s'.center(columns) % len(y))
    elif y.count(-1) > 1:
        print('%s packets dropped of %s'.center(columns)
              % (y.count(-1), len(y)))
    else:
        print('Displaying %s total packets from %s'.center(columns)
              % (len(y), address))


def _output_average_status(address, y_average, columns):  # DEBUG: DEPRECATED
    """ Outputs a status line based on standard *y* collection.

    :address: The address currently being sent ping requests
    :y_average: The python list tracking average ping data
    :columns: The total columns of the current terminal (from ``_get_tty_size``
    :returns: None. Instead, prints data to terminal
    """
    warnings.warn("This function will be deprecated in V0.9!", DeprecationWarning)  # DEBUG
    if sum(y_average) / len(y_average) < 0:
        print('Connection dropped!'.center(columns))
    else:
        print('Displaying the average of %s total packets from %s'.center(columns)
              % (len(y_average), address))


def _run(argv=None):  # DEBUG: DEPRECATED
    """ Actually runs the logic. Uses ``subprocess.Popen`` to run system ``ping``
    and plots the results to ``hipsterplot.plot``.

    :address: A system ``ping`` compatible address, either web or IP.  """
    warnings.warn("This function will be deprecated in V0.9!")  # DEBUG.
    if type(argv) is list:
        parsed = parser.parse_args(argv)
    else:
        parsed = parser.parse_args()

    print('Waiting for first ping...')  # Notify user in case of high ping

    try:
        for realtime_pings, average_pings in get_pings(parsed.address):
            time_start = time.time()

            if time.time() - time_start < 0.5:  # Wait for time if no time elapsed
                time.sleep(0.5 - (time.time() - time_start))

            system('clear' if not name == 'nt' else 'cls')

            columns, rows = get_terminal_size()

            # Write current plot
            plot_pings(realtime_pings, columns=columns - X_COLUMN_SCALE,
                       rows=int((rows - Y_ROW_SCALE) / 2))

            _output_top_status(parsed.address, realtime_pings, columns)

            # write middle
            print(_construct_middle_line(parsed.address, columns))

            # write average plot
            plot(average_pings, num_x_chars=columns - X_COLUMN_SCALE,
                 num_y_chars=int((rows - Y_ROW_SCALE) / 2))

            _output_average_status(parsed.address, average_pings, columns)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    try:
        _run()
    except KeyboardInterrupt:
        pass
