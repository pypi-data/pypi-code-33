# -*- coding: utf-8 -*-

"""
Module that provides argparse-compatible conversion functions for a variety 
of value formats, including:
 * positive integers, 
 * ephem.hours instances, and
 * lists of integers from a comma-separated list.

.. versionadded:: 1.2.4
"""

import re
import ephem
from argparse import ArgumentTypeError
from datetime import datetime

from lsl.common.constants import c
from lsl.common.mcs import datetime2mjdmpm, mjdmpm2datetime

__version__ = '0.1'
__revision__ = '$Rev: 2640 $'
__all__ = ['positive_or_zero_int', 'positive_int', 'positive_or_zero_float', 
           'positive_float', 'frequency', 'frequency_range', 'wavelength', 
           'wavelength_range', 'date', 'mjd', 'time', 'mpm', 'hours', 
           'csv_hours_list', 'degrees', 'csv_degrees_list', 'csv_int_list', 
           'csv_baseline_list', 'csv_hostname_list']


def positive_or_zero_int(string):
    """
    Convert a string to a positive (>=0) integer.
    """
    
    try:
        value = int(string, 10)
    except ValueError:
        msg = "%r is a non-integer value" % string
        raise ArgumentTypeError(msg)
    if value < 0:
        msg = "%r < 0" % string
        raise ArgumentTypeError(msg)
    return value


def positive_int(string):
    """
    Convert a string to a positive (>0) integer.
    """
    
    value = positive_or_zero_int(string)
    if value <= 0:
        msg = "%r <= 0" % string
        raise ArgumentTypeError(msg)
    return value


def positive_or_zero_float(string):
    """
    Convert a string to a positive (>=0.0) float.
    """
    
    try:
        value = float(string)
    except ValueError:
        msg = "%r is a non-float value" % string
        raise ArgumentTypeError(msg)
    if value < 0.0:
        msg = "%r < 0.0" % string
        raise ArgumentTypeError(msg)
    return value


def positive_float(string):
    """
    Convert a string to a positive (>0.0) float.
    """
    
    value = positive_or_zero_float(string)
    if value <= 0.0:
        msg = "%r <= 0.0" % string
        raise ArgumentTypeError(msg)
    return value


# Prefix conversion factors for _prefix_to_scale()
_PREFIX_SCALES = {'y': 1e-24, 'z': 1e-21, 'a': 1e-18, 'f': 1e-15, 'p': 1e-12, 
                  'n': 1e-9,  'u': 1e-6,  'm': 1e-3,  'c': 1e-2,  'd': 1e-1, 
                  '':  1e0,   'da': 1e1,  'h': 1e2,   'k': 1e3,   'M': 1e6, 
                  'G': 1e9,   'T': 1e12,  'P': 1e15,  'E': 1e18,  'Z': 1e21, 
                  'Y': 1e24}


def _prefix_to_scale(prefix):
    """
    Function to convert a metric prefix to a scale for the base unit.
    """
    
    try:
        scale = _PREFIX_SCALES[prefix]
    except KeyError:
        raise ValueError("Unknown prefix '%s'" % prefix)
    return scale


def _quantitiy_to_hz(value, unit):
    """
    Convert a value/pair into a frequency.  If no unit is provided, MHz is 
    assumed.
    """
    
    value = float(value)
    if unit is None:
        unit = 'MHz'
        
    if unit[-8:] == 'Angstrom' or unit[-2:] == 'AA':
        ## Angstroms
        pscale = 1e-10
        value *= pscale
        value = c/value
    elif unit[-1] == 'm':
        ## Some version of meters
        pscale = _prefix_to_scale(unit[:-1])
        value *= pscale
        value = c/value
    elif unit[-2:] == 'Hz':
        ## Some version of frequency
        pscale = _prefix_to_scale(unit[:-2])
        value *= pscale
    return value


def _quantitiy_to_m(value, unit):
    """
    Convert a value/pair into a wavelength.  If no unit is provided, m is 
    assumed.
    """
    
    value = float(value)
    if unit is None:
        unit = 'm'
        
    if unit[-8:] == 'Angstrom' or unit[-2:] == 'AA':
        ## Angstroms
        pscale = 1e-10
        value *= pscale
    elif unit[-1] == 'm':
        ## Some version of meters
        pscale = _prefix_to_scale(unit[:-1])
        value *= pscale
    elif unit[-2:] == 'Hz':
        ## Some version of frequency
        pscale = _prefix_to_scale(unit[:-2])
        value *= pscale
        value = c/value
    return value


# Regular expression for frequency()
_FREQUENCY_RE = re.compile('^(?P<start>\d*(\.\d*)?)\s*(?P<unit1>(([yzafpnumcdhkMGTPEZY]|(da))?Hz)|(([yzafpnumcdhkMGTPEZY]|(da))?m)|(AA)|(Angstrom))?(\~(?P<stop>\d*(\.\d*)?))?\s*(?P<unit2>(([yzafpnumcdhkMGTPEZY]|(da))?Hz)|(([yzafpnumcdhkMGTPEZY]|(da))?m)|(AA)|(Angstrom))?$')


def _frequency_conversion_base(string):
    """
    Convert a frequency to a float Hz value.  This function accepts a variety 
    of string formats:
     * pure float values are intepreted to be in MHz (45.0 -> 45e6)
     * number/unit pairs are allowed so long as they are in:
        * [prefix]m, A, or ang for wavelength and 
        * [prefix]Hz for frequency
     * a 'number~number' is interpretted as a range in MHz
     * a 'number/unit~number/unit' is converted to a range in Hz
    
    .. note::
        For ranges, a two-element list is returned where the first value
        is less than the second.
    """
    
    try:
        value = float(string)*1e6
    except ValueError:
        mtch = _FREQUENCY_RE.match(string)
        if mtch is None:
            msg = "%r cannot be interpretted as a frequency" % string
            raise ArgumentTypeError(msg)
        else:
            start, stop = mtch.group('start'), mtch.group('stop')
            unit1, unit2 = mtch.group('unit1'), mtch.group('unit2')
            if string.find('~') != -1 and stop is None:
                msg = "%r cannot be parsed as a range" % string
                raise ArgumentTypeError(msg)
            if unit1 is None:
                unit1 = unit2
            elif stop is not None and unit2 is None:
                msg = "%r must have units specified for the second value" % string
                raise ArgumentTypeError(msg)
            value = _quantitiy_to_hz(start, unit1)
            if stop is not None:
                value = [value, _quantitiy_to_hz(stop, unit2)]
                if value[1] < value[0]:
                    value.reverse()
    return value


def frequency(string):
    """
    Convert a frequency to a float Hz value.  This function accepts a variety 
    of string formats:
     * pure float values are intepreted to be in MHz (45.0 -> 45e6)
     * number/unit pairs are allowed so long as they are in:
        * [prefix]m, A, or ang for wavelength and 
        * [prefix]Hz for frequency
    """
    
    value = _frequency_conversion_base(string)
    try:
        len(value)
        msg = "%r does not appear to be a single frequency" % string
        raise ArgumentTypeError(msg)
    except TypeError:
        pass
    return value


def frequency_range(string):
    """
    Convert a frequency to a float Hz value.  This function accepts a variety 
    of string formats:
     * a 'number~number' is interpretted as a range in MHz
     * a 'number/unit~number/unit' is converted to a range in Hz
    
    .. note::
        For ranges, a two-element list is returned where the first value
        is less than the second.
    """
    
    value = _frequency_conversion_base(string)
    try:
        len(value)
    except TypeError:
        msg = "%r does not appear to be a frequency range" % string
        raise ArgumentTypeError(msg)
    return value


def _wavelength_conversion_base(string):
    """
    Convert a wavelength to a float m value.  This function accepts a variety 
    of string formats:
     * pure float values are intepreted to be in m (45.0 -> 45.0)
     * number/unit pairs are allowed so long as they are in:
        * [prefix]m, A, or ang for wavelength and 
        * [prefix]Hz for frequency
     * a 'number~number' is interpretted as a range in m
     * a 'number/unit~number/unit' is converted to a range in m
    
    .. note::
        For ranges, a two-element list is returned where the first value
        is less than the second.
    """
    
    try:
        value = float(string)
    except ValueError:
        mtch = _FREQUENCY_RE.match(string)
        if mtch is None:
            msg = "%r cannot be interpretted as a frequency" % string
            raise ArgumentTypeError(msg)
        else:
            start, stop = mtch.group('start'), mtch.group('stop')
            unit1, unit2 = mtch.group('unit1'), mtch.group('unit2')
            if string.find('~') != -1 and stop is None:
                msg = "%r cannot be parsed as a range" % string
                raise ArgumentTypeError(msg)
            if unit1 is None:
                unit1 = unit2
            elif stop is not None and unit2 is None:
                msg = "%r must have units specified for the second value" % string
                raise ArgumentTypeError(msg)
            value = _quantitiy_to_m(start, unit1)
            if stop is not None:
                value = [value, _quantitiy_to_m(stop, unit2)]
                if value[1] < value[0]:
                    value.reverse()
    return value


def wavelength(string):
    """
    Convert a wavelength to a float m value.  This function accepts a variety 
    of string formats:
     * pure float values are intepreted to be in m (45.0 -> 45.0)
     * number/unit pairs are allowed so long as they are in:
        * [prefix]m, A, or ang for wavelength and 
        * [prefix]Hz for frequency
    """
    
    value = _wavelength_conversion_base(string)
    try:
        len(value)
        msg = "%r does not appear to be a single wavelength" % string
        raise ArgumentTypeError(msg)
    except TypeError:
        pass
    return value


def wavelength_range(string):
    """
    Convert a wavelength to a float m value.  This function accepts a variety 
    of string formats:
     * a 'number~number' is interpretted as a range in m
     * a 'number/unit~number/unit' is converted to a range in m
    
    .. note::
        For ranges, a two-element list is returned where the first value
        is less than the second.
    """
    
    value = _wavelength_conversion_base(string)
    try:
        len(value)
    except TypeError:
        msg = "%r does not appear to be a wavelength range" % string
        raise ArgumentTypeError(msg)
    return value


def date(string):
    """
    Convert a data as either a YYYY[-/]MM[-/]DD or MJD string into a 
    YYYY/MM/DD string.
    """
    
    try:
        mjd = int(string, 10)
        dt = mjdmpm2datetime(mjd, 0)
    except ValueError:
        cstring = string.replace('-', '/')
        try:
            dt = datetime.strptime("%s 00:00:00" % cstring, "%Y/%m/%d %H:%M:%S")
        except ValueError:
            msg = "%r cannot be interpretted as an MJD or date string" % string
            raise ArgumentTypeError(msg)
            
    date = dt.strftime('%Y/%m/%d')
    return date


def mjd(string):
    """
    Convert a data as either a YYYY[-/]MM[-/]DD or MJD string into an integer
    MJD.
    """
    
    try:
        mjd = int(string, 10)
    except ValueError:
        cstring = string.replace('-', '/')
        try:
            dt = datetime.strptime("%s 00:00:00" % cstring, "%Y/%m/%d %H:%M:%S")
            mjd, mpm = datetime2mjdmpm(dt)
        except ValueError:
            msg = "%r cannot be interpretted as an MJD or date string" % string
            raise ArgumentTypeError(msg)
            
    return mjd


def time(string):
    """
    Covnert a time as HH:MM:SS[.SSS] or MPM string into a HH:MM:SS.SSSSSS 
    string.
    """
    
    try:
        mpm = int(string, 10)
        if mpm < 0 or mpm > (86400*1000 + 999):
            msg = "%r is out of range for an MPM value"
            raise ArgumentTypeError(msg)
        s, f = mpm/1000, mpm%1000
        h = s / 3600
        m = (s / 60) % 60
        s = s % 60
        stime = "%i:%02i:%02i.%06i" % (h, m, s, f*1000)
    except ValueError:
        try:
            dt = datetime.strptime("2000/1/1 %s" % string, "%Y/%m/%d %H:%M:%S.%f")
        except ValueError:
            try:
                dt = datetime.strptime("2000/1/1 %s" % string, "%Y/%m/%d %H:%M:%S")
            except ValueError:
                msg = "%r cannot be interpretted as a time string" % string
                raise ArgumentTypeError(msg)
        stime = "%i:%02i:%02i.%06i" % (dt.hour, dt.minute, dt.second, dt.microsecond)
    return stime


def mpm(string):
    """
    Covnert a time as HH:MM:SS[.SSS] or MPM string into an MPM integer.
    """
    
    try:
        mpm = int(string, 10)
        if mpm < 0 or mpm > (86400*1000 + 999):
            msg = "%r is out of range for an MPM value"
            raise ArgumentTypeError(msg)
    except ValueError:
        try:
            dt = datetime.strptime("2000/1/1 %s" % string, "%Y/%m/%d %H:%M:%S.%f")
        except ValueError:
            try:
                dt = datetime.strptime("2000/1/1 %s" % string, "%Y/%m/%d %H:%M:%S")
            except ValueError:
                msg = "%r cannot be interpretted as a time string" % string
                raise ArgumentTypeError(msg)
        mjd, mpm = datetime2mjdmpm(dt)
    return mpm


def hours(string):
    """
    Convert a 'HH[:MM[:SS[.SSS]]]' string into an ephem.hours instance.
    """
    
    try:
        value = ephem.hours(string)
    except ValueError as e:
        msg = str(e) % string
        raise ArgumentTypeError(msg)
    return value


def csv_hours_list(string):
    """
    Convert a comma-separated list of 'HH[:MM[:SS.[SSS]]]' string into a list 
    of ephem.hours instances.
    """
    
    string = string.rstrip()
    if string[-1] == ',':
        string = string[:-1]
        
    value = []
    for item in string.split(','):
        value.append( hours(item) )
    return value


def degrees(string):
    """
    Convert a 'sDD[:MM[:SS[.SSS]]]' string into an ephem.degrees instance.
    """
    
    try:
        value = ephem.degrees(string)
    except ValueError as e:
        msg = str(e) % string
        raise ArgumentTypeError(msg)
    return value


def csv_degrees_list(string):
    """
    Convert a comma-separated list of 'sDD[:MM[:SS.[SSS]]]' string into a list 
    of ephem.degrees instances.
    """
    
    string = string.rstrip()
    if string[-1] == ',':
        string = string[:-1]
        
    value = []
    for item in string.split(','):
        value.append( degrees(item) )
    return value


def _int_item_or_range(string):
    if string.find('~') != -1:
        start, stop = string.split('~', 1)
        start, stop = int(start, 10), int(stop, 10)
        value = list(range(start, stop+1))
    else:
        value = [int(string, 10),]
    return value


def csv_int_list(string):
    """
    Convert a comma-separated list of integers into a list of integers.  This 
    function also allows for ranges to be specifed using the '~' character.  
    This formatting converts 'start~stop' to 'range(start, stop+1)'.
    """
    
    if string in ('all', '*'):
        value = 'all'
    elif string in ('none', ''):
        value = 'none'
    else:
        value = []
        for item in string.split(','):
            item = item.strip().rstrip()
            if item == '':
                continue
            try:
                subvalue = _int_item_or_range(item)
            except ValueError:
                msg = "%r contains non-integer values" % string
                raise ArgumentTypeError(msg)
            value.extend(subvalue)
    return value


def csv_baseline_list(string):
    """
    Convert a comma-separated list of baslines pairs into a list of baseline
    pairs.  Baseline pairs are defined as 'antenna1-antenna2' where 'antenna1'
    and 'antenna2' are both integers or ranges denoted by the '~' character.
    """
    
    if string in ('all', '*'):
        value = 'all'
    elif string in ('none', ''):
        value = 'none'
    else:
        value = []
        for item in string.split(','):
            item = item.strip().rstrip()
            if item == '':
                continue
            try:
                ant1, ant2 = item.split('-', 1)
            except ValueError:
                msg = "%s contains non-baseline or non-integer values" % string
                raise ArgumentTypeError(msg)
            try:
                ant1 = _int_item_or_range(ant1)
                ant2 = _int_item_or_range(ant2)
            except ValueError:
                msg = "%r contains non-integer values" % string
                raise ArgumentTypeError(msg)
            for i in ant1:
                for j in ant2:
                    value.append( (i,j) )
    return value


_IPV4_RANGE_RE = re.compile('^(?P<byte1>\d{1,3})(~(?P<byte1e>\d{1,3}))?\.(?P<byte2>\d{1,3})(~(?P<byte2e>\d{1,3}))?\.(?P<byte3>\d{1,3})(~(?P<byte3e>\d{1,3}))?\.(?P<byte4>\d{1,3})(~(?P<byte4e>\d{1,3}))?$')

_HOSTNAME_RE = re.compile('^(?P<hostname>[a-zA-Z\-0-9]*?)$')
_HOSTNAME_RANGE_RE=re.compile('^(?P<hostbase>[a-zA-Z\-]*?)(?P<start>[0-9]+)~(?P<stop>[0-9]+)$')
    

def csv_hostname_list(string):
    """
    Convert a comma-separated list of IPv4 addresses/hostnames into a list 
    IPv4 addresses/hostnames.  This function support indexing with the '~' 
    character so long as:
     * the character is in any one of the IPv4 bytes or
     * the character is at the end of a hostname which ends with a number
    """
    
    value = []
    for item in string.split(','):
        item = item.strip().rstrip()
        if item == '':
            continue
        mtch = _IPV4_RANGE_RE.match(item)
        if mtch is not None:
            ## IPv4 address or IPv4 address range
            b1b = int(mtch.group('byte1'), 10)
            b1e = mtch.group('byte1e')
            b1e = int(b1e, 10) if b1e is not None else b1b
            
            b2b = int(mtch.group('byte2'), 10)
            b2e = mtch.group('byte2e')
            b2e = int(b2e, 10) if b2e is not None else b2b
            
            b3b = int(mtch.group('byte3'), 10)
            b3e = mtch.group('byte3e')
            b3e = int(b3e, 10) if b3e is not None else b3b
            
            b4b = int(mtch.group('byte4'), 10)
            b4e = mtch.group('byte4e')
            b4e = int(b4e, 10) if b4e is not None else b4b
            
            items = []
            for b1 in range(b1b, b1e+1):
                for b2 in range(b2b, b2e+1):
                    for b3 in range(b3b, b3e+1):
                        for b4 in range(b4b, b4e+1):
                            items.append( '%i.%i.%i.%i' % (b1, b2, b3, b4) )
        else:
            mtch = _HOSTNAME_RANGE_RE.match(item)
            if mtch is not None:
                ## Hostname range
                hostbase = mtch.group('hostbase')
                try:
                    start = int(mtch.group('start'), 10)
                    stop = int(mtch.group('stop'), 10)
                except ValueError:
                    msg = "%r contains non-integer hostname values" % string
                    raise ArgumentTypeError(msg)
                items = ['%s%i' % (hostbase, i) for i in range(start, stop+1)]
            else:
                mtch = _HOSTNAME_RE.match(item)
                if mtch is not None:
                    ## Single hostname
                    items = [mtch.group('hostname'),]
                else:
                    msg = "%r contains invalid hostname values" % string
                    raise ArgumentTypeError(msg)
        value.extend( items )
    return value
