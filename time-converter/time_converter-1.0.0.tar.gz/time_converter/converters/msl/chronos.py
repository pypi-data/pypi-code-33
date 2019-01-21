# -*- coding: utf-8 -*-
"""Replicates functionality of NASA NAIF's chronos tool to convert MSL SCLK time to UTC

It uses the msl.tsc file, which was downloaded from
https://naif.jpl.nasa.gov/pub/naif/MSL/kernels/sclk/msl.tsc
and might be updated regularly

Author: Johan von Forstner <forstner@physik.uni-kiel.de>, January 2018
"""

import datetime as dt
import os

import numpy as np

sclk_data = None


def _load_sclk_data(filename=os.path.join(os.path.dirname(__file__), 'msl.tsc')):
    """
    Loads the data from the "Source SCLKvSCET File" section of the msl.tsc file

    :rtype: tuple
    :type filename: str
    :param filename: the file name (default: msl.tsc)
    :return: data from the four columns: sclk, utc, dut, sclkrate
    """
    global sclk_data
    if sclk_data is None:
        file = open(filename)
        correct_section = False
        skip_header = None
        max_rows = None
        for i, line in enumerate(file):
            if skip_header is not None and line.lstrip().startswith('CCSD'):
                max_rows = i - skip_header
                break
            elif correct_section and line.lstrip().startswith('*'):
                skip_header = i + 1
            elif line.startswith('Source SCLKvSCET File'):
                correct_section = True
        data = np.genfromtxt(filename, dtype=(float, dt.datetime, float, float), skip_header=skip_header, max_rows=max_rows,
                             unpack=True,
                             converters={
                                 0: np.float,
                                 1: lambda x: dt.datetime.strptime(x.decode('ascii'), "%Y-%jT%H:%M:%S.%f"),
                                 2: np.float,
                                 3: np.float
                             })
        sclk, utc, dut, sclkrate = data['f0'], data['f1'], data['f2'], data['f3']
        sclk_data = sclk, utc, dut, sclkrate
    return sclk_data


def sclk_to_dt(sclk):
    """
    Accurately converts spacecraft clock (SCLK) to UTC datetime using the chronos data

    :rtype: dt.datetime
    :type sclk: Real
    :param sclk: SCLK to convert
    :return: datetime as UTC
    """
    sclks, dts, dut, sclkrate = _load_sclk_data()
    # find index of last position with sclk smaller or equal to the given one
    index = np.searchsorted(sclks, sclk, side='right') - 1
    # extrapolate using sclkrate given in table
    seconds = (sclk - sclks[index]) * sclkrate[index]
    return dts[index] + dt.timedelta(seconds=seconds)


def dt_to_sclk(dt):
    """
    Accurately converts UTC datetime to spacecraft clock (SCLK) using the chronos data

    :type: dt: dt.datetime
    :rtype float
    :param dt: UTC datetime to convert
    :return: corresponding SCLK value
    """
    sclks, dts, dut, sclkrate = _load_sclk_data()
    # find index of last position with sclk smaller or equal to the given one
    index = np.searchsorted(dts, dt, side='right') - 1
    # extrapolate using sclkrate given in table
    return sclks[index] + (dt - dts[index]).total_seconds() / sclkrate[index]