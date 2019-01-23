import xmlrpclib
import logging
import re


def versionKey(v):
    """
    For a version string with numbers alternated by alphanumeric separators,
    return a tuple containing the separators and the numbers.

    For example:
    >>> versionKey('1.2.3')
    (1, '.', 2, '.', 3)
    >>> versionKey('v10r0')
    ('v', 10, 'r', 0)
    >>> versionKey('1.2-a')
    (1, '.', 2, '-a')
    """
    v = re.findall(r'[-a-zA-Z_.]+|\d+', v)
    return tuple([int(x) if x.isdigit() else x for x in v])


def sortVersions(versionlist, reverse=False):
    return sorted(versionlist, key=versionKey, reverse=reverse)


class CustomTransportXMLRPC(xmlrpclib.Transport):

    def __init__(self, cookie=None, *args, **kwargs):
        self.cookie = cookie
        xmlrpclib.Transport.__init__(self, *args, **kwargs)

    def send_content(self, connection, request_body):
        if self.cookie:
            connection.putheader("Cookie", self.cookie)
        xmlrpclib.Transport.send_content(self, connection, request_body)


class SoftConfDB():
    def __init__(self, address, cookie=None):

        self.mTransportLayer = CustomTransportXMLRPC(cookie=cookie)
        self.mProxy = xmlrpclib.ServerProxy(address,
                                            transport=self.mTransportLayer,
                                            allow_none=True)

        self.mSupportedMethods = [m for m in self.mProxy.system.listMethods()
                                  if 'system.' not in m]
        self.log = logging.getLogger()

    def __getattr__(self, name):
        if name in self.mSupportedMethods:
            def wrapper(*args, **kwargs):
                m = getattr(self.mProxy, name)
                return m(*args, **kwargs)
            return wrapper
