import socket
from autest.api import AddWhenFunction
import hosts.output as host
import psutil

def PortsOpen(ports):
    portlst = []

    for port in ports:
        portlst.append(PortOpen(port))

    return all(portlst)

def PortsReady(ports):
    portlst = []

    for port in ports:
        portlst.append(PortReady(port))

    return all(portlst)


def PortOpen(port, address=None, timeout=None, address_family="inet4"):
    '''
    This function is more like a stat test. The value of it is that no traffic happens.
    The issue with it is that the source of the port might not be ready to accept data.
    If for some reason psutil fails here, we will fall back on the PortReady logic
    '''
    ret = False

    try:
        netstate = psutil.net_connections(address_family)
    except:
        netstate = None

    # if no port are being read.. we probally have some system issue with the library
    # and should fall back to older logic
    if netstate:
        # Address/port only ready to use if it is in LISTEN or NONE state
        connections = [i.laddr for i in netstate if i.status == 'LISTEN' or i.status == 'NONE']
        ports = [i.port for i in connections if i.ip == address or address is None]
        if port in ports:
            ret = True
        else:
          ret = PortReady(port, address=address, timeout=timeout)
    else:
        ret = PortReady(port, address=address, timeout=timeout)

    return ret


def PortOpenv4(port, address=None, timeout=None):
    return PortOpen(port=port, address=address, timeout=timeout, address_family='inet4')


def PortOpenv6(port, address=None, timeout=None):
    return PortOpen(port=port, address=address, timeout=timeout, address_family='inet6')


def PortReady(port, address=None, timeout=None):
    '''
    The logic here is to open a port. this causes some traffic on the host of the port
    however this also means that the host is more likely to be ready to get traffic.

    This does not mean the host is "ready". In such cases a different test of state maybe 
    needed, such as sending a test packet/message of some kind that the application understand.
    '''

    ret = False

    if address is None:
        address = "localhost"
    if timeout is None:
        timeout = .5
    address = (address, port)
    try:
        s = socket.create_connection(address, timeout=timeout)
        s.close()
        ret = True
    except socket.error:
        s = None
        ret = False
    except socket.timeout:
        s = None
    host.WriteDebug(["portReady", "when"],
                    "checking port {0} = {1}".format(port, ret))

    return ret

AddWhenFunction(PortsOpen)
AddWhenFunction(PortsReady)
AddWhenFunction(PortOpen)
AddWhenFunction(PortOpenv4)
AddWhenFunction(PortOpenv6)
AddWhenFunction(PortReady)
