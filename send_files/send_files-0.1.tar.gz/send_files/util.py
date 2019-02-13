from uuid import uuid4
from netifaces import (
    ifaddresses, interfaces,
    AF_INET, AF_INET6,
)

def hosts():
    return _hosts(ifaddresses(if_) for if_ in interfaces())
def _hosts(data):
    for if_ in data:
        if AF_INET6 in if_:
            for addr in if_[AF_INET6]:
                yield '[%(addr)s]' % addr
        if AF_INET in if_:
            for addr in if_[AF_INET]:
                yield addr['addr']

def new_password():
    return uuid4().hex

def urls(port, password, ssl=False):
    template = '%(protocol)s://%(host)s:%(port)d/%(password)s'
    for host in hosts():
        params = {
            'protocol': 'https' if ssl else 'http',
            'host': host,
            'port': port,
            'password': password,
        }
        yield template % params

