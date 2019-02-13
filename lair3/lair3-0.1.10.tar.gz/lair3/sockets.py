import bombfuse
import amncore.compat as compat
import copy
import ctypes
import errno
import httplib
import http_packet
import amncore.mixins as mixins
import os
import paynspray.rando
import random
import re
import select
import socket
import SocketServer
import struct
import threading
import amncore.xcepts as xcepts

MATCH_IPV6 = r'^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$'
MATCH_IPV4 = r'^\s*(?:(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2}))\s*$'
MATCH_IPV4_PRIVATE = r'^\s*(?:10\.|192\.168|172.(?:1[6-9]|2[0-9]|3[01])\.|169\.254)'
MATCH_MAC_ADDR = r'^(?:[0-9a-fA-F]{2}([-:]))(?:[0-9a-fA-F]{2}\1){4}[0-9a-fA-F]{2}$'

ipv6_support = None

def supports_ipv6():
    global ipv6_support
    if ipv6_support is not None:
        return ipv6_support

    ipv6_support = False

    if hasattr(socket, "AF_INET6") == True:
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            s.close()
            ipv6_support = True
        except Exception as e:
            pass

    return (ipv6_support and socket.has_ipv6)

class SocketParams(object):
    def __init__(self, **kwargs):
        if 'PeerHost' in kwargs:
            self.peerhost = kwargs['PeerHost']
        elif 'PeerAddr' in kwargs:
            self.peerhost = kwargs['PeerAddr']
        else:
            self.peerhost = None
            
        if 'LocalHost' in kwargs:
            self.localhost = kwargs['LocalHost']
        elif 'LocalAddr' in kwargs:
            self.localhost = kwargs['LocalAddr']
        else:
            self.localhost = '0.0.0.0'
            
        if 'PeerPort' in kwargs and kwargs['PeerPort'] is not None:
            self.peerport = int(kwargs['PeerPort'])
        else:
            self.peerport = 0
        
        if 'LocalPort' in kwargs and kwargs['LocalPort'] is not None:
            self.localport = int(kwargs['LocalPort'])
        else:
            self.localport = 0
            
        if 'Bare' in kwargs:
            self.bare = kwargs['Bare']
        else:
            self.bare = False
            
        if 'SSL' in kwargs:
            self.ssl = kwargs['SSL']
        else:
            self.ssl = False
            
        if 'SSLContext' in kwargs:
            self.sslctx = kwargs['SSLContext']
        else:
            self.sslctx = None
            
        SSLv2 = 1
        SSLv3 = 2
        SSLv23 = 3
        TLSv1 = 4
        TLSv1_1 = 5
        TLSv1_2 = 6

        supported_ssl_versions = ['Auto', 'SSL2', 'SSL23', 'TLS1', 'SSL3', SSLv2, SSLv3, SSLv23, TLSv1]
        if 'SSLVersion' in kwargs and kwargs['SSLVersion'] in supported_ssl_versions:
            self.ssl_version = kwargs['SSLVersion']
        else:
            self.ssl_version = None
            
        supported_ssl_verifiers = ['CLIENT_ONCE', 'FAIL_IF_NO_PEER_CERT', 'NONE', 'PEER']
        if 'SSLVerifyMode' in kwargs and kwargs['SSLVerifyMode'] in supported_ssl_verifiers:
            self.ssl_verify_mode = kwargs['SSLVerifyMode']
        else:
            self.ssl_verify_mode = None

        if 'SSLCompression' in kwargs:
            self.ssl_compression = kwargs['SSLCompression']
        else:
            self.ssl_compression = None

        if 'SSLCipher' in kwargs:
            self.ssl_cipher = kwargs['SSLCipher']
        else:
            self.ssl_cipher = None
            
        if 'SSLCert' in kwargs and kwargs['SSLCert'] is not None and os.path.isfile(kwargs['SSLCert']) == True:
            try:
                fd = file(kwargs['SSLCert'], 'rb')
                self.ssl_cert = fd.read()
                fd.close()
            except Exception as e:
                pass
        else:
            self.ssl_cert = None
            
        if 'SSLClientCert' in kwargs and kwargs['SSLClientCert'] is not None and os.path.isfile(kwargs['SSLClientCert']) == True:
            try:
                fd = file(kwargs['SSLClientCert'], 'rb')
                self.ssl_client_cert = fd.read()
                fd.close()
            except Exception as e:
                pass
        else:
            self.ssl_client_cert = None
            
        if 'SSLClientKey' in kwargs and kwargs['SSLClientKey'] is not None and os.path.isfile(kwargs['SSLClientKey']) == True:
            try:
                fd = file(kwargs['SSLClientKey'], 'rb')
                self.ssl_client_key = fd.read()
                fd.close()
            except Exception as e:
                pass
        else:
            self.ssl_client_key = None

        if 'Proxies' in kwargs and kwargs['Proxies'] is not None:
            self.proxies = map(lambda a: map(lambda b: b.strip(), a.split(':')), map(lambda a: a.strip(), kwargs['Proxies'].split(',')))
        else:
            self.proxies = None
            
        if 'Proto' in kwargs:
            self.proto = kwargs['Proto'].lower()
        else:
            self.proto = 'tcp'
        
        if 'Server' in kwargs:
            self.server = kwargs['Server']
        else:
            self.server = False
        
        if 'Comm' in kwargs and kwargs['Comm'] is not None:
            if issubclass(kwargs['Comm'], SocketComm) == True:
                self.comm = kwargs['Comm']()
            else:
                self.comm = None
        else:
            self.comm = None
            
        if 'Context' in kwargs:
            self.context = kwargs['Context']
        else:
            self.context = {}

        if self.comm is None:
            self.comm = LocalComm()

        if self.server == True and self.proto == 'udp':
            self.server = False

        if 'Retries' in kwargs:
            self.retries = int(kwargs['Retries'])
        else:
            self.retries = 0

        # proposed change for 0.1.5
        if 'Timeout' in kwargs:
            if kwargs['Timeout'] is None:
                # handle None cast
                self.timeout = None
            else:
                # we set a timeout of 0 to None to disable timeout (instead of making socket non-blocking)
                # this value is ONLY used for socket.connect()
                self.timeout = int(kwargs['Timeout'])
                if self.timeout == 0:
                    self.timeout = None
        else:
            self.timeout = 5

        if 'IPv6' in kwargs:
            self.v6 = kwargs['IPv6']
        else:
            self.v6 = False

    @classmethod
    def from_kwargs(self, **kwargs):
        return self(**kwargs)
        
    @property
    def is_server(self):
        return (self.server == True)
        
    @property
    def is_client(self):
        return (self.server == False)
        
    @property
    def is_tcp(self):
        return (self.proto == 'tcp')
        
    @property
    def is_udp(self):
        return (self.proto == 'udp')
        
    @property
    def is_ip(self):
        return (self.proto == 'ip')

    @property
    def is_bare(self):
        return (self.bare == True)

    @property
    def is_ssl(self):
        return (self.ssl == True)
        
    @property
    def is_v6(self):
        return (self.v6)
        
    @property
    def peeraddr(self):
        return self.peerhost
        
    @property
    def localaddr(self):
        return self.localhost
        
def create_sock(**kwargs):
    return create_param(SocketParams.from_kwargs(**kwargs))
    
def create_param(param):
    return param.comm.create(param)
    
def create_tcp(**kwargs):
    kwargs.update({'Proto': 'tcp'})
    return create_param(SocketParams.from_kwargs(**kwargs))
    
def create_tcp_server(**kwargs):
    kwargs.update({'Server': True})
    return create_tcp(**kwargs)
    
def create_udp(**kwargs):
    kwargs.update({'Proto': 'udp'})
    return create_param(SocketParams.from_kwargs(**kwargs))
    
def create_ip(**kwargs):
    kwargs.update({'Proto': 'ip'})
    return create_param(SocketParams.from_kwargs(**kwargs))
    
def is_ipv4(addr):
    if addr is None:
        return False
    return (re.search(MATCH_IPV4, addr) is not None)

def is_ipv6(addr):
    if addr is None:
        return False
    return (re.search(MATCH_IPV6, addr) is not None)
        
def is_mac_addr(addr):
    if addr is None:
        return False
    return (re.search(MATCH_MAC_ADDR, addr) is not None)

def is_dotted_ip(addr):
    if addr is None:
        return False
    return ((supports_ipv6() == True and (re.search(MATCH_IPV6, addr) is not None)) or (re.search(MATCH_IPV4, addr) is not None))

def is_internal(addr):
    if addr is None:
        return False
    return (re.search(MATCH_IPV4_PRIVATE, addr) is not None)
    
def getaddresses(hostname, accept_ipv6 = True):
    if hostname is None:
        return []
    if (is_ipv4(hostname) == True) or ((accept_ipv6 == True) and (is_ipv6(hostname) == True)):
        return [hostname]
        
    addrlist = []
    res = socket.getaddrinfo(hostname, None)
    
    if res is None:
        return []
    
    for i in res:
        if (is_ipv4(i[4][0]) == True) or ((accept_ipv6 == True) and (is_ipv6(i[4][0]) == True)):
            addrlist.append(i[4][0])

    return addrlist
    
def getaddress(hostname, accept_ipv6 = True):
    retval = getaddresses(hostname, accept_ipv6)
    
    if len(retval) > 0:
        return retval[0]
    else:
        return None
    
def getaddrinfo(host, port = 0):
    """
    Wrapper for socket.getaddrinfo() that skips dotted IPv4 resolution
    """
    if is_ipv4(host) == True:
        return [(socket.AF_INET, 0, 0, '', (host, port))]
        
    return socket.getaddrinfo(host, port)
    
def getsockaddr(host, port):
    """
    Returns a tuple as (host, port) for IPv4 hosts and (host, port, flow-info, scope-id) for IPv6 hosts
    """
    if host == '::ffff:0.0.0.0':
        if supports_ipv6() == True:
            host = '::'
        else:
            host = '0.0.0.0'
            
    retval = getaddrinfo(host, port)
    if retval is not None and len(retval) > 0:
        return retval[0][4]
    else:
        return None

def parsesockaddr(saddr):
    """
    Returns a list of [family, host, port] from a Pythonic sock address
    """
    if is_ipv6(saddr[0]) == True:
        af = socket.AF_INET6
        host, port, _, _ = saddr
    elif is_ipv4(saddr[0]) == True:
        af = socket.AF_INET
        host, port = saddr

    return [af, host, port]

def getsrcaddr(dest = '8.8.8.8'):
    """
    Attempts to get the localhost address by establishing a bogus connection
    """
    try:
        s = create_udp(PeerHost = dest, PeerPort = 31337)
        r = s.getsockname()
        s.close()
        
        return r[0]
        
    except Exception as e:
        return '127.0.0.1'

def ipv6_link_address(iface):
    r = getsrcaddr("FF02::1%{}".format(iface))
    if r is None or re.search(r'^fe80', r, re.IGNORECASE) is None:
        return None
    return r
    
class sockaddr(ctypes.Structure):
    _fields_ = [("sa_family", ctypes.c_ushort),
                ("__pad1", ctypes.c_ushort),
                ("ipv4_addr", ctypes.c_byte * 4),
                ("ipv6_addr", ctypes.c_byte * 16),
                ("__pad2", ctypes.c_ulong)]

# little workaround for Windows (fixed in python3)
if hasattr(socket, "inet_pton") == False and compat.is_windows() == True:
    WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
    WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA
    
    # packs an IP string (IPv4 or IPv6) into a binary string
    def inet_pton(address_family, ip_string):
        addr = sockaddr()
        addr.sa_family = address_family
        addr_size = ctypes.c_int(ctypes.sizeof(addr))
        
        if WSAStringToAddressA(ip_string, address_family, None, ctypes.byref(addr), ctypes.byref(addr_size)) != 0:
            raise socket.error(ctypes.FormatError())
            
        if address_family == socket.AF_INET:
            return ctypes.string_at(addr.ipv4_addr, 4)
        elif address_family == socket.AF_INET6:
            return ctypes.string_at(addr.ipv6_addr, 16)
        else:
            raise ValueError("Invalid address family provided")
            
    setattr(socket, "inet_pton", inet_pton)
    
def addr_itoa(addr, v6 = False):
    nboa = addr_iton(addr, v6)
    return addr_ntoa(nboa)
    
def addr_atoi(addr):
    return resolv_nbo_i(addr)
    
def addr_aton(addr):
    return resolv_nbo(addr)
    
def resolv_nbo(host):
    # getaddrinfo returns IPv4 or IPv6 address of host
    res = getaddrinfo(getaddress(host, True))[0]
    if res is not None:
        if res[0] == socket.AF_INET:
            return socket.inet_pton(socket.AF_INET, res[4][0])
        elif res[0] == socket.AF_INET6:
            return socket.inet_pton(socket.AF_INET6, res[4][0])
        else:
            return ""
    else:
        return ""
    
def resolv_nbo_i(host):
    return addr_ntoi(resolv_nbo(host))
    
def resolv_nbo_list(host):
    return map(lambda addr: resolv_nbo(addr), getaddresses(host))
    
def resolv_nbo_i_list(host):
    return map(lambda addr: addr_ntoi(addr), resolv_nbo_list(host))
    
def resolv_to_dotted(host):
    res = addr_ntoa(addr_aton(host))
    return res
    
def addr_atoc(mask):
    if is_ipv6(mask) == True:
        bits = 128
    else:
        bits = 32
    mask_i = resolv_nbo_i(mask)
    cidr = None
    for i in range(0, bits + 1):
        if ((1 << i) - 1) << (bits - i) == mask_i:
            cidr = i
            break
    return cidr
    
def addr_ctoa(cidr):
    if not (0 <= cidr <= 32):
        return None
        
    return addr_itoa(((1 << cidr) - 1) << 32 - cidr)
    
def compress_address(addr):
    if not is_ipv6(addr):
        return addr

    _addr = copy.copy(addr)

    while True:
        addr = re.sub(r'\A0:0:0:0:0:0:0:0\Z', '::', _addr)
        if (addr != _addr):
            break
        addr = re.sub(r'\b0:0:0:0:0:0:0\b', ':', _addr)
        if (addr != _addr):
            break
        addr = re.sub(r'\b0:0:0:0:0:0\b', ':', _addr)
        if (addr != _addr):
            break
        addr = re.sub(r'\b0:0:0:0:0\b', ':', _addr)
        if (addr != _addr):
            break
        addr = re.sub(r'\b0:0:0:0\b', ':', _addr)
        if (addr != _addr):
            break
        addr = re.sub(r'\b0:0:0\b', ':', _addr)
        if (addr != _addr):
            break
        addr = re.sub(r'\b0:0\b', ':', _addr)
        if (addr != _addr):
            break
        break
    return re.sub(r':{3,}', '::', addr)
    
def addr_ntoa(addr):
    """Converts a NBO address to an ASCII string (with IPv6 support)"""
    if len(addr) == 4:
        retval = '.'.join(str(oct) for oct in struct.unpack('4B', addr))
        return retval
        
    if len(addr) == 16:
        retval = ':'.join(('%x' % int(i)) for i in struct.unpack('>8H', addr))
        return compress_address(retval)
        
    raise RuntimeError("Invalid address format")
    
def addr_iton(addr, v6 = False):
    """Converts an integer to a NBO address"""
    if addr < 0x100000000 and v6 is False:
        return struct.pack('>L', addr)
    else:
        w = []
        w[0] = (addr >> 96) & 0xffffffff
        w[1] = (addr >> 64) & 0xffffffff
        w[2] = (addr >> 32) & 0xffffffff
        w[3] = addr & 0xffffffff
        return struct.pack('>4L', *w)
    
def addr_ntoi(addr):
    """Converts a NBO address to an integer"""
    bits = struct.unpack(">{}L".format(len(addr) / 4), addr)
    
    if len(bits) == 1:
        return bits[0]
        
    if len(bits) == 4:
        val = 0
        for i in bits:
            val += (bits[i] << (96 - (i * 32)))
            
        return val
        
    raise RuntimeError("Invalid address format")

def eth_aton(mac):
    return struct.pack("6B", *map(lambda c: int(c, 16), str(mac).split(':')))

def eth_ntoa(binary): 
    return ':'.join(map(lambda x: "%.2x" % x, struct.unpack("6B", binary))).upper()
    
def cidr_crack(cidr, v6 = False):
    tmp = cidr.split('/')
    
    try:
        tst, scope = tmp[0].split("%", 1)
    except ValueError:
        # "need more than 1 value to unpack"
        tst = tmp[0].split("%", 1)[0]
        scope = ""
        
    addr = addr_atoi(tst)
    
    bits = 32
    mask = 0
    use6 = False
    
    if (addr > 0xffffffff or v6 or re.search(r':', cidr) is not None):
        use6 = True
        bits = 128
        
    mask = (2 ** bits) - (2 ** (bits - int(tmp[1])))
    base = addr & mask
    
    stop = base + (2 ** (bits - int(tmp[1]))) - 1
    return [addr_itoa(base, use6) + scope, addr_itoa(stop, use6) + scope]
    
def net2bitmask(netmask):
    nmask = resolv_nbo(netmask)
    imask = addr_ntoi(nmask)
    bits = 32

    if imask > 0xFFFFFFFF:
        bits = 128

    for bit in range(0, bits):
        p = 2 ** bit
        if ((imask & p) == p):
            return (bits - bit)

    return 0

def bit2netmask(bitmask, ipv6 = False):
    if bitmask > 32 or ipv6:
        i = ((~((2 ** (128 - bitmask)) - 1)) & (2 ** 128 - 1))
        n = addr_iton(i, True)
        return addr_ntoa(n)
    else:
        tmp1 = struct.pack('>L', *[(~((2 ** (32 - bitmask)) - 1)) & 0xFFFFFFFF])
        octets = struct.unpack('4B', tmp1)
        octets = map(lambda octet: str(octet), octets)
        return '.'.join(octets)

class TcpSocketPairHelper(object):
    def __init__(self):
        self.lsock = None
        self.rsock = None
        self.laddr = '127.0.0.1'
        self.lport = 0
        self.threads = []
        self.mutex = threading.Lock()
        
    def server_thread(self):
        server = None
        
        with self.mutex:
            server = SocketServer.TCPServer((self.laddr, 0), None)
            caddr, self.lport = server.socket.getsockname()
            
            thred = threading.Thread(target = self.client_thread, name = "TcpSocketPairClient")
            thred.daemon = True
            self.threads.append(thred)
            thred.start()
            
        self.lsock, _ = server.socket.accept()
        server.server_close()
        
    def client_thread(self):
        with self.mutex:
            self.rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            self.rsock.connect((self.laddr, self.lport))
            
    def make_socket_pair(self):
        thred = threading.Thread(target = self.server_thread, name = "TcpSocketPairServer")
        thred.daemon = True
        self.threads.append(thred)
        thred.start()
        
        for t in self.threads:
            t.join()
            
        return [self.lsock, self.rsock]
        
def tcp_socket_pair():
    return TcpSocketPairHelper().make_socket_pair()
    
def udp_socket_pair():
    laddr = '127.0.0.1'
    lsock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM, proto = 0)
    lsock.bind((laddr, 0))
    
    rsock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM, proto = 0)
    rsock.bind((laddr, 0))
    
    raddr, rport = lsock.getsockname()
    rsock.connect((raddr, rport))
    
    saddr, sport = rsock.getsockname()
    lsock.connect((saddr, sport))
    
    return [lsock, rsock]

class SocketEvents(object):
    def __init__(self):
        pass
        
    def on_before_socket_create(self, comm, param):
        pass
        
    def on_socket_created(self, comm, sock, param):
        pass
        
class SocketComm(object):
    def __init__(self):
        self.handlers_rwlock = None
        self.handlers = None
        pass
        
    def create(self, param):
        raise NotImplementedError
        
    def register_event_handler(self, handler):
        try:
            if self.handlers is None:
                self.handlers = []
            
            self.handlers.append(handler)
        except Exception as e:
            pass
        
    def deregister_event_handler(self, handler):
        try:
            if self.handlers is not None:
                self.handlers.remove(handler)
        except Exception as e:
            pass
            
    def each_event_handler(self, func=None):
        try:
            if self.handlers is not None:
                if func is not None:
                    [func(handler) for handler in self.handlers]
                return self.handlers
        except Exception as e:
            pass
    
    def notify_before_socket_create(self, comm, param):
        try:
            if self.each_event_handler() is not None:
                for handler in self.each_event_handler():
                    handler.on_before_socket_create(comm, param)
        except Exception as e:
            pass
            
    def notify_socket_created(self, comm, sock, param):
        try:
            if self.each_event_handler() is not None:
                for handler in self.each_event_handler():
                    handler.on_socket_created(comm, sock, param)
        except Exception as e:
            pass


class SockBase(object):
    def __init__(self, *args, **kwargs):
        if 'sock' in kwargs:
            self.sock = kwargs['sock']
        else:
            raise RuntimeError("SockBase did not wrap socket object!")
        if 'sslsock' in kwargs:
            self.sslsock = kwargs['sslsock']
        else:
            self.sslsock = None
        if 'sslctx' in kwargs:
            self.sslctx = kwargs['sslctx']
        else:
            self.sslctx = None
        if hasattr(self, "context") == False:
            self.context = None

    def bind(self, *args, **kwargs):
        return self.sock.bind(*args, **kwargs)

    def close(self):
        return self.sock.close()

    def connect(self, *args, **kwargs):
        return self.sock.connect(*args, **kwargs)

    def connect_to(self, *args, **kwargs):
        return self.sock.connect_to(*args, **kwargs)

    @property
    def fd(self):
        return self

    def fileno(self):
        try:
            return self.sock.fileno()
        except socket.error as e:
            if (e.errno == socket.EBADF):
                return -1
        except Exception as e:
            return -1

    def getpeername(self):
        return self.sock.getpeername()
        
    def getsockname(self):
        return self.sock.getsockname()

    def getsockopt(self, *args, **kwargs):
        return self.sock.getsockopt(*args, **kwargs)

    def initsock(self, params = None):
        if params is not None:
            self.peerhost = params.peerhost
            self.peerport = params.peerport
            self.localhost = params.localhost
            self.localport = params.localport
            self.context = params.context or {}
            if params.v6 == True:
                self.ipv = 6
            else:
                self.ipv = 4
        
    def ioctl(self, *args, **kwargs):
        return self.sock.ioctl(*args, **kwargs)
        
    def listen(self, *args, **kwargs):
        return self.sock.listen(*args, **kwargs)
        
    def makefile(self, *args, **kwargs):
        return self.sock.makefile(*args, **kwargs)
        
    def recv(self, *args, **kwargs):
        return self.sock.recv(*args, **kwargs)
        
    def recvfrom(self, *args, **kwargs):
        return self.sock.recvfrom(*args, **kwargs)
        
    def recvfrom_into(self, *args, **kwargs):
        return self.sock.recvfrom_into(*args, **kwargs)
        
    def recv_into(self, *args, **kwargs):
        return self.sock.recv_into(*args, **kwargs)
        
    def send(self, *args, **kwargs):
        return self.sock.send(*args, **kwargs)
        
    def sendall(self, *args, **kwargs):
        return self.sock.sendall(*args, **kwargs)
        
    def sendto(self, *args, **kwargs):
        return self.sock.sendto(*args, **kwargs)
            
    def setblocking(self, *args, **kwargs):
        return self.sock.setblocking(*args, **kwargs)
        
    def settimeout(self, *args, **kwargs):
        return self.sock.settimeout(*args, **kwargs)
        
    def gettimeout(self):
        return self.sock.gettimeout()
        
    def setsockopt(self, *args, **kwargs):
        return self.sock.setsockopt(*args, **kwargs)
        
    def shutdown(self, *args, **kwargs):
        return self.sock.shutdown(*args, **kwargs)
        
    @property
    def family(self):
        return self.sock.family
        
    @property
    def type(self):
        return self.sock.type
        
    @property
    def proto(self):
        return self.sock.proto
        
class TcpSock(SockBase, mixins.StreamMixin):
    def __init__(self, *args, **kwargs):
        return super(TcpSock, self).__init__(*args, **kwargs)

    @classmethod
    def create(self, **kwargs):
        kwargs['Proto'] = 'tcp'
        return self.create_param(SocketParams.from_kwargs(**kwargs))

    @classmethod
    def create_param(self, param):
        param.proto = 'tcp'
        return create_param(param)

    def shutdown(how = socket.SHUT_RDWR):
        try:
            return super(TcpSock, self).shutdown(how)
        except Exception as e:
            pass

    @property
    def type(self):
        return 'tcp'
        
class UdpSock(SockBase):
    def __init__(self, *args, **kwargs):
        return super(UdpSock, self).__init__(*args, **kwargs)

    @classmethod
    def create(self, **kwargs):
        kwargs['Proto'] = 'udp'
        if 'LocalHost' in kwargs:
            kwargs['Server'] = True
        
        return self.create_param(SocketParams.from_kwargs(**kwargs))

    @classmethod
    def create_param(self, param):
        param.proto = 'udp'
        return create_param(param)

    def write(self, gram):
        try:
            return self.send(gram)
        except socket.error as e:
            if (e.errno == errno.EHOSTUNREACH or e.errno == errno.ENETDOWN or e.errno == errno.ENETUNREACH or e.errno == errno.ENETRESET or e.errno == errno.EHOSTDOWN or e.errno == errno.EACCES or e.errno == errno.EINVAL or e.errno == errno.EADDRNOTAVAIL):
                return None

    def put(self, gram):
        return self.write(gram)

    def read(self, length = 65535):
        if length < 0:
            length = 65535
        return self.recv(length)

    def timed_read(self, length = 65535, timeout = 10):
        try:
            rv = select.select([self.fd], [], [], timeout)
            if (rv is not None) and (rv != ([], [], [])) and (len(rv[0]) > 0) and (rv[0][0] == self.fd):
                return self.read(length)
            else:
                return ''
        except Exception as e:
            return ''

    def sendto(self, gram, peerhost, peerport, flags = 0):
        peer = resolv_nbo(peerhost)
        if (len(peer) == 4 and self.ipv == 6):
            peerhost = getaddress(peerhost, True)
            if peerhost[0:7].lower() != '::ffff:':
                peerhost = '::ffff:' + peerhost

        try:
            return self.sock.sendto(gram, flags, getsockaddr(peerhost, peerport))
        except socket.error as e:
            if (e.errno == errno.EHOSTUNREACH or e.errno == errno.ENETDOWN or e.errno == errno.ENETUNREACH or e.errno == errno.ENETRESET or e.errno == errno.EHOSTDOWN or e.errno == errno.EACCES or e.errno == errno.EINVAL or e.errno == errno.EADDRNOTAVAIL):
                return None

    def recvfrom(self, length = 65535, timeout = 10):
        try:
            rv = select.select([self.fd], [], [], timeout)
            if (rv is not None) and (rv != ([], [], [])) and (len(rv[0]) > 0) and (rv[0][0] == self.fd):
                self.sock.setblocking(0)
                data, saddr = self.sock.recvfrom(length)
                af, host, port = parsesockaddr(saddr)
                
                return [data, host, port]
            else:
                return ['', None, None]
        except socket.error as e:
            return ['', None, None]
        except bombfuse.TimeoutError:
            return ['', None, None]
        except Exception as e:
            return ['', None, None]
            
    def get(self, timeout=None):
        data, saddr, sport = self.recvfrom(65535, timeout)
        return data

    @property
    def type(self):
        return 'udp'
        
class IpSock(SockBase):
    def __init__(self, *args, **kwargs):
        return super(IpSock, self).__init__(*args, **kwargs)

    @classmethod
    def create(self, **kwargs):
        kwargs['Proto'] = 'ip'
        return self.create_param(SocketParams.from_kwargs(**kwargs))

    @classmethod
    def create_param(self, param):
        param.proto = 'ip'
        return create_param(param)

    def write(self, gram):
        raise RuntimeError("IP sockets must use sendto(), not write()")
        
    def read(self, length = 65535):
        raise RuntimeError("IP sockets must use recvfrom(), not read()")
        
    def sendto(self, gram, peerhost, flags = 0):
        dest = getsockaddr(peerhost, 0)
        
        if (compat.is_freebsd() == True or compat.is_netbsd() == True or compat.is_macosx() == True):
            # byteswap
            tmp_unpakt = struct.unpack(">H", gram[2:4])
            tmp_pakt = struct.pack("@h", *tmp_unpakt)
            
            tmp_unpakt2 = struct.unpack(">H", gram[6:8])
            tmp_pakt2 = struct.pack("@h", *tmp_unpakt2)
            
            gram[2] = tmp_pakt[0]
            gram[3] = tmp_pakt[1]
            gram[6] = tmp_pakt2[0]
            gram[7] = tmp_pakt2[1]

        try:
            return self.sock.sendto(gram, flags, dest)
        except socket.error as e:
            return None
            
    def recvfrom(self, length = 65535, timeout = 10):
        try:
            rv = select.select([self.sock], [], [], timeout)
            if rv != ([],[],[]) and rv[0][0] == self.sock:
                data, saddr = super(IpSock, self).recvfrom(length)
                af, host, port = parsesockaddr(saddr)
                
                return [data, host]
            else:
                return ['', None]
        except Exception as e:
            return ['', None]
            
    def get(self, timeout = None):
        data, saddr = self.recvfrom(65535, timeout)
        return data

    def put(self, gram):
        return self.write(gram)

    @property
    def type(self):
        return 'ip'
        
class TcpServer(SockBase, mixins.StreamServerMixin):
    def __init__(self, *args, **kwargs):
        return super(TcpServer, self).__init__(*args, **kwargs)
    
    @classmethod
    def create(self, **kwargs):
        kwargs['Proto'] = 'tcp'
        kwargs['Server'] = True
        return self.create_param(SocketParams.from_kwargs(**kwargs))

    @classmethod
    def create_param(self, param):
        param.proto = 'tcp'
        param.server = True
        return create_param(param)

    def accept(self, **kwargs):
        try:
            r, _, _ = select.select([self.fd], [], [], 0.5)
            if (r is not None) and (r != []) and (self.fd in r):
                _sock, addr = self.sock.accept()
            else:
                return None
        except socket.error as e:
            return None

        retval = None
        if _sock is not None:
            retval = TcpSock(sock = _sock)
            if addr is not None:
                retval.peerhost = addr[0]
                retval.peerport = addr[1]

        return retval

class LocalComm(SocketComm):
    def __init__(self):
        return super(SocketComm, self).__init__()

    def create(self, param):
        if param.proto == 'tcp':
            return self.create_by_type(param, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        elif param.proto == 'udp':
            return self.create_by_type(param, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        elif param.proto == 'ip':
            return self.create_ip(param)
        else:
            raise NotImplementedError("Unknown protocol: {}".format(param.proto))

    def create_ip(self, param):
        self.notify_before_socket_create(self, param)
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        if param.bare == False:
            # wrap socket in IpSock class object
            _sock = sock
            sock = IpSock(sock = _sock)
            sock.initsock(param)

        self.notify_socket_created(self, sock, param)

        return sock
    
    def create_by_type(self, param, type, proto = 0):
        if socket.has_ipv6 == True:
            if param.localhost is not None:
                local = resolv_nbo(param.localhost)
            else:
                local = None

            if param.peerhost is not None:
                peer = resolv_nbo(param.peerhost)
            else:
                peer = None

            if type == socket.SOCK_DGRAM and compat.is_linux() == True and local is None and peer is None:
                param.v6 = True
            elif (local is not None and len(local) == 16) or (peer is not None and len(peer) == 16):
                param.v6 = True

            if param.v6 == True:
                if local is not None and len(local) == 4:
                    if local == "\x00\x00\x00\x00":
                        param.localhost = '::'
                    elif local == "\x7f\x00\x00\x01":
                        param.localhost = "::1"
                    else:
                        param.localhost = "::ffff:" + getaddress(param.localhost, True)
                if peer is not None and len(peer) == 4:
                    if peer == "\x00\x00\x00\x00":
                        param.peerhost = '::'
                    elif peer == "\x7f\x00\x00\x01":
                        param.peerhost = "::1"
                    else:
                        param.peerhost = "::ffff:" + getaddress(param.peerhost, True)
        else:
            param.v6 = False

        self.notify_before_socket_create(self, param)

        sock = None
        if param.v6 == True:
            sock = socket.socket(socket.AF_INET6, type, proto)
        else:
            sock = socket.socket(socket.AF_INET, type, proto)
        bare_sock = sock

        if ((param.localport is not None) and (param.localport != 0)) or (param.localhost is not None):
            try:
                if compat.is_windows() == False:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(getsockaddr(param.localhost, param.localport))
            except socket.error as e:
                if e.errno == errno.EADDRNOTAVAIL or e.errno == errno.EADDRINUSE:
                    sock.close()
                    raise xcepts.BindError(param.localhost, param.localport)

        if type == socket.SOCK_DGRAM:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        if param.server == True:
            sock.listen(256)
            
            if param.bare == False:
                cls = TcpServer
                if param.ssl == True:
                    import securesocket
                    cls = securesocket.SslTcpServer
                sock = cls(sock = bare_sock)
                sock.initsock(param)
        else:
            chain = []

            if param.peerhost is not None:
                ip = param.peerhost
                port = param.peerport

                if param.proxies is not None:
                    chain = copy.copy(param.proxies)
                    chain.append(['host', param.peerhost, param.peerport])
                    ip = chain[0][1]
                    port = int(chain[0][2])

                try:
                    sock.settimeout(param.timeout)
                    sock.connect(getsockaddr(ip, port))
                except socket.timeout as e:
                    sock.close()
                    raise xcepts.ConnectionTimeout(ip, port)
                except socket.error as e:
                    if (e.errno == errno.EHOSTUNREACH or e.errno == errno.ENETDOWN or e.errno == errno.ENETUNREACH or e.errno == errno.ENETRESET or e.errno == errno.EHOSTDOWN or e.errno == errno.EACCES or e.errno == errno.EINVAL or e.errno == errno.ENOPROTOOPT):
                        sock.close()
                        raise xcepts.HostUnreachable(ip, port)
                    elif (e.errno == errno.EADDRNOTAVAIL or e.errno == errno.EADDRINUSE):
                        sock.close()
                        raise xcepts.InvalidDestination(ip, port)
                    elif (e.errno == errno.ETIMEDOUT or e.message == 'timed out'):
                        sock.close()
                        raise xcepts.ConnectionTimeout(ip, port)
                    elif (e.errno == errno.ECONNRESET or e.errno == errno.ECONNREFUSED or e.errno == errno.ENOTCONN or e.errno == errno.ECONNABORTED):
                        sock.close()
                        raise xcepts.ConnectionRefused(ip, int(port))
                finally:
                    sock.settimeout(None)
            
            if param.bare == False:
                if param.proto == 'tcp':
                    cls = TcpSock
                    sock = cls(sock = bare_sock)
                    sock.initsock(param)
                elif param.proto == 'udp':
                    cls = UdpSock
                    sock = cls(sock = bare_sock)
                    sock.initsock(param)

            if len(chain) > 1:
                for i, proxy in enumerate(chain):
                    try:
                        next_hop = chain[i + 1]
                    except Exception as e:
                        next_hop = None
                    if next_hop is not None:
                        self.proxy(sock, proxy[0], next_hop[1], next_hop[2])
            
            if (param.bare == False and param.ssl == True):
                import securesocket
                cls = securesocket.SslTcpSock
                sock = cls(sock = bare_sock)
                sock.initsock(param)

        self.notify_socket_created(self, sock, param)
        return sock

    def proxy(self, sock, type, host, port):
        if type.lower() == 'sapni':
            packet_type = 'NI_ROUTE'
            route_info_ver = 2
            ni_ver = 39
            num_entries = 2
            talk_mode = 1
            num_rest_nodes = 1
            
            shost, sport = sock.getpeername()
            first_route_item = shost + struct.pack("B", 0) + str(sport) + struct.pack("bb", 0, 0)
            route_data = struct.pack(">L", len(first_route_item)) + first_route_item
            route_data += (host + struct.pack("B", 0) + str(port) + struct.pack("bb", 0, 0))
            
            ni_packet = packet_type + struct.pack("8b", 0, route_info_ver, ni_ver, num_entries, talk_mode, 0, 0, num_rest_nodes)
            
            ni_packet += (struct.pack(">L", len(route_data) - 4) + route_data)
            
            ni_packet = (struct.pack(">L", len(ni_packet)) + ni_packet)
            
            size = sock.put(ni_packet)
            
            if size != len(ni_packet):
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to send the entire packet to the proxy server")
                
            try:
                ret_len = struct.unpack(">L", sock.get_once(4, 30))[0]
                if ret_len and ret_len != 0:
                    ret = sock.get_once(ret_len, 30)
            except IOError:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a response from the proxy server")
            except struct.error:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to parse a response from the proxy server")
                
            if ret and len(ret) < 4:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a complete response from the proxy server")
                
            if re.search(r'NI_RTERR', ret) is not None:
                if re.search(r'timed out', ret) is not None:
                    raise xcepts.ConnectionProxyError(host, port, type, "Connection to remote host {} timed out".format(host))
                elif re.search(r'refused', ret) is not None:
                    raise xcepts.ConnectionProxyError(host, port, type, "Connection to remote port {} refused".format(port))
                elif re.search(r'denied', ret) is not None:
                    raise xcepts.ConnectionProxyError(host, port, type, "Connection to {}:{} blocked by ACL".format(host, port))
                else:
                    raise xcepts.ConnectionProxyError(host, port, type, "Connection to {}:{} failed (unknown error)".format(host, port))
            elif re.search(r'NI_PONG', ret) is not None:
                pass
            else:
                raise xcepts.ConnectionProxyError(host, port, type, "Connection to {}:{} failed (unknown error)".format(host, port))
        elif type.lower() == 'http':
            setup = "CONNECT {}:{} HTTP/1.0\r\n\r\n".format(host, port)
            size = sock.put(setup)
            if size != len(setup):
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to send the entire packet to the proxy server")
                
            try:
                ret = sock.get_once(39, 30)
            except IOError:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a response from the proxy server")
                
            if ret is None:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a response from the proxy server")
                
            resp = http_packet.HttpResponse()
            resp.update_cmd_parts(re.split(r'\r?\n', ret)[0])
            
            if resp.code != 200:
                raise xcepts.ConnectionProxyError(host, port, type, "Proxy server responded with non-OK code ({} {})".format(resp.code, resp.message))
        elif type.lower() == 'socks4':
            setup = struct.pack(">BBH", 4, 1, int(port)) + addr_aton(host) + paynspray.rando.rand_text_alpha(random.randrange(8) + 1) + "\x00"
            size = sock.put(setup)
            if size != len(setup):
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to send the entire packet to the proxy server")
            
            try:
                ret = sock.get_once(8, 30)
            except IOError:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a response from the proxy server")
                
            if ret is None or len(ret) < 8:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a complete response from the proxy server")
                
            if ret[1:2] != '\x5a':
                raise xcepts.ConnectionProxyError(host, port, type, "Proxy server responded with error code {}".format(struct.unpack("B", ret[0:1])[0]))
        elif type.lower() == 'socks5':
            auth_methods = struct.pack("BBB", 5, 1, 0)
            size = sock.put(auth_methods)
            if size != len(auth_methods):
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to send the entire packet to the proxy server")
                
            ret = sock.get_once(2, 30)
            if ret is not None and ret[1:2] == "\xff":
                raise xcepts.ConnectionProxyError(host, port, type, "The proxy server requires authentication")
            elif ret is None:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a response from the proxy server")
            
            if is_ipv4(host):
                addr = socket.inet_pton(socket.AF_INET, host)
                setup = struct.pack("4B", 5, 1, 0, 1) + addr + struct.pack(">H", int(port))
            elif supports_ipv6() == True and is_ipv6(host):
                addr = socket.inet_pton(socket.AF_INET6, host)
                setup = struct.pack("4B", 5, 1, 0, 4) + addr + struct.pack(">H", int(port))
            else:
                setup = struct.pack("4B", 5, 1, 0, 3) + struct.pack("B", len(host)) + host + struct.pack(">H", int(port))
                
            size = sock.put(setup)
            if size != len(setup):
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to send the entire packet to the proxy server")
                
            try:
                response = sock.get_once(10, 30)
            except IOError:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a response from the proxy server")
                
            if response is None or len(response) < 10:
                raise xcepts.ConnectionProxyError(host, port, type, "Failed to receive a complete response from the proxy server")
            
            if response[1:2] != "\x00":
                raise xcepts.ConnectionProxyError(host, port, type, "Proxy server responded with error code {}".format(struct.unpack("B", ret[1:2])[0]))
        else:
            raise ValueError("Invalid proxy type '{}' specified".format(type))
            
            

