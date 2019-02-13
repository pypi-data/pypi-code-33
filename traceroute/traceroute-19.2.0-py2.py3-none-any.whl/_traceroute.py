from __future__ import division

from pprint import pprint, pformat
from subprocess import Popen, PIPE
import re
import socket
import sys
import itertools

from ._data import Traceroute, Hop, Route


def _traceroute_call(target, **kwargs):
    """
    Get tracert output.
    
    Args:
        target (str): Name of target.
    
    Returns:
        str: Output from tracert command.
    """
    cmd = ['traceroute', target]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate()
    return stdout


def _traceroute(target, **kwargs):
    """
    Get traceroute data from traceroute call.

    Args:
        target (str): Name of target for traceroute command.

    Returns:
        Traceroute: A Traceroute data object.
    """
    stdout = _traceroute_call(target, **kwargs)
    lines = re.split(r'[\r\n]+', stdout.strip())
    lines = [line for line in lines if line.strip()]
    m = re.match(r'^traceroute to (?P<host>\S+) \((?P<ip>[\d\.]+)\).*$', lines[0])
    traceroute = Traceroute(
        raw_traceroute=stdout,
        target=target,
        host=m.group('host'),
        ip=m.group('ip'),
        hops=[],
    )
    hop_pattern = r"""
        ^\s*                                            # Start of line
        (?:(?P<number>\d+)\s+)?                         # Hop number (optional)
        (?:(?P<host>\S+)\s+\((?P<ip>[\d\.]+)\)\s+)?     # Host and IP
        (?:(?P<t1>\d+\.\d+)\ ms|(?P<to1>\*))\s*         # First time/out
        (?:(?:(?P<t2>\d+\.\d+)\ ms|(?P<to2>\*))\s*)?    # Second time/out
        (?:(?:(?P<t3>\d+\.\d+)\ ms|(?P<to3>\*))\s*)?    # Third time/out
        $                                               # End of line
    """
    for line in itertools.islice(lines, 1, None):
        m = re.match(hop_pattern, line, re.VERBOSE)
        if m:
            d = m.groupdict()
            if d['number']:
                hop = Hop(number=int(d['number']), routes=[])
                traceroute.hops.append(hop)
            else:
                hop = traceroute.hops[-1]
            for grp in ['t1', 't2', 't3']:
                if d[grp]:
                    route = Route(
                        host=d['host'], 
                        ip=d['ip'], 
                        time=float(d[grp]),
                    )
                    hop.routes.append(route)
        else:
            break
    return traceroute
