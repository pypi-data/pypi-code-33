from __future__ import division

from pprint import pprint, pformat
from subprocess import Popen, PIPE
import re
import socket
import sys
import itertools

from ._data import Traceroute, Hop, Route


def _tracert_call(target, **kwargs):
    """
    Get tracert output.
    
    Args:
        target (str): Name of target.
    
    Returns:
        str: Output from tracert command.
    """
    cmd = ['tracert', target]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate()
    return stdout


def _tracert(target, **kwargs):
    """
    Get traceroute data from tracert call.

    Args:
        target (str): Name of target for traceroute command.

    Returns:
        Traceroute: A Traceroute data object.
    """
    stdout = _tracert_call(target, **kwargs)
    lines = re.split(r'[\r\n]+', stdout.strip())
    lines = [line for line in lines if line.strip()]
    m = re.match(r'^Tracing route to (?P<host>\S+) \[(?P<ip>[\d\.]+)\]\s*$', lines[0])
    traceroute = Traceroute(
        raw_traceroute=stdout,
        target=target,
        host=m.group('host'),
        ip=m.group('ip'),
        hops=[],
    )
    hop_pattern = r"""
        ^\s*                                        # Start of line
        (?P<number>\d+)\s+                          # Hop number
        (?:(?P<t1><?\d+)\ ms|(?P<to1>\*))\s+          # Time or timout 1
        (?:(?P<t2><?\d+)\ ms|(?P<to2>\*))\s+          # Time or timout 2
        (?:(?P<t3><?\d+)\ ms|(?P<to3>\*))\s+          # Time or timout 3
        (?:
          (?:(?P<host>\S+)\s+)?\[?(?P<ip>\d+\.\d+\.\d+\.\d+)\]?  # Host (optional) and IP
          |                                         # OR
          (?P<timeout>Request\ timed\ out\.)        # Timeout message
        )         
        \s*$                                        # End of line
    """
    for line in itertools.islice(lines, 2, None):
        m = re.match(hop_pattern, line, re.VERBOSE)
        if m:
            d = m.groupdict()
            hop = Hop(number=int(d['number']), routes=[])
            traceroute.hops.append(hop)
            for grp in ['t1', 't2', 't3']:
                if d[grp]:
                    route = Route(
                        host=d['host'], 
                        ip=d['ip'], 
                        time=0.0 if d[grp].startswith('<') else float(d[grp]),
                    )
                    hop.routes.append(route)
            
        else:
            pass
    return traceroute
