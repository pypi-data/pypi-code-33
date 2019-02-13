"""
Data representation of Trace Data.

Trace
{
    'target': 'google.com',
    'hops': [
        {
            'number': 1,
            'routes': [
                {
                    'host': 'test.com',
                    'ip': '1.1.1.1',
                    'time': 20.0
                },
                {
                    'host': 'test.com',
                    'ip': '1.1.1.1',
                    'time': 19.0
                }
            ]
        }
    ]
}
    
"""

from pprint import pformat


class Data(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        # return "{}({})".format(
        #     self.__class__.__name__,
        #     ', '.join('{}={}'.format(k, v) for k, v in self.__dict__.items()),
        # )
        return "{}({})".format(
            self.__class__.__name__,
            pformat(self.__dict__),
        )


class Traceroute(Data):
    raw_traceroute = None
    target = None
    host = None
    ip = None
    hops = None


class Hop(Data):
    number = None
    routes = None

    @property
    def hosts(self):
        return set([r.host for r in self.routes if r.host])

    @property
    def ips(self):
        return set([r.ip for r in self.routes if r.ip])

    @property
    def times(self):
        return [r.time for r in self.routes if r.time]


class Route(Data):
    host = None
    ip = None
    time = None