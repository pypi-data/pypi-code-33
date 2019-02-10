from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_TYPE
from socket import socket as create_socket, timeout

__all__ = [
    'EasySocket', 'UDPSocket', 'TCPSocket', 'DEFAULT_HOST',
]

DEFAULT_HOST = ("127.0.0.1", 0)

class EasySocket:

    '''
    Simple socket wrapper that offers auto-encoding and auto-decoding of messages. Can take a regular
    socket as argument to wrap it into an EasySocket, thus ignoring the protocol and host parameters.
    '''

    def __init__(self, *, protocol=SOCK_STREAM, socket=None, host=DEFAULT_HOST, encoding="raw", buffer_size=4096):
        if socket is None:
            socket = create_socket(AF_INET, protocol)
            socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            socket.bind(host)
        self._socket = socket
        self.buffer_size = buffer_size
        self.encoding = encoding

    def send(self, message, encoding=None):
        '''
        Sends a message to the peer it's connected to, with either the given encoding or
        the socket's encoding.
        '''
        encoding = encoding or self.encoding
        message = self._encode_msg(message, encoding)
        return self._socket.send(message)

    def sendto(self, message, destination, encoding=None):
        '''
        Sends a message to destination, with either the given encoding or the socket's encoding.
        The destination argument must be a tuple (destination address, destination_port).
        '''
        encoding = encoding or self.encoding
        message = self._encode_msg(message, encoding)
        return self._socket.sendto(message, destination)

    def recv(self, encoding=None):
        '''
        Reads a message if one is available and decodes it with either the given encoding
        or the socket's encoding, blocks otherwise.
        '''
        encoding = encoding or self.encoding
        message = self._socket.recv(self.buffer_size)
        return self._decode_msg(message, encoding)

    def recvfrom(self, encoding=None):
        '''
        Reads a message if one is available and decodes it with either the given encoding
        or the socket's encoding, blocks otherwise. Returns two values, message and sender,
        where sender is a tuple (sender_address, sender_port).
        '''
        encoding = encoding or self.encoding
        message, sender = self._socket.recvfrom(self.buffer_size)
        sender = self._socket.getpeername() if sender is None or sender[0] == 0 else sender
        return self._decode_msg(message, encoding), sender

    def _encode_msg(self, message, encoding):
        return message if encoding == "raw" else message.encode(encoding)

    def _decode_msg(self, message, encoding):
        return message if encoding == "raw" else message.decode(encoding)

    def __getattr__(self, attr_name):
        return getattr(self._socket, attr_name)

    def __repr__(self):
        if self._socket.fileno() == -1:
            return f"<{self.__class__.__name__} [closed]>"
        else:
            addr, port = self.getsockname()
            return f"<{self.__class__.__name__} [active] host={addr}:{port}>"

    @property
    def host(self):
        return self.getsockname()

class UDPSocket(EasySocket):

    '''
    Creates an instance of UDPSocket. Can take a regular socket as argument to wrap it into
    a UDPSocket but raises a ValueError exception if this socket's protocol isn't SOCK_DGRAM.
    '''

    def __init__(self, *, encoding="raw", socket=None, host=DEFAULT_HOST, buffer_size=4096):
        if socket is not None and socket.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_DGRAM:
            raise ValueError("The socket's protocol must be SOCK_DGRAM to be wrapped into a UDPSocket.")
        super().__init__(protocol=SOCK_DGRAM, socket=socket, host=host, encoding=encoding, buffer_size=buffer_size)

    def send(self, *args, **kargs):
        raise NotImplementedError("The method 'send' doesn't exist on UDPSocket. Try 'sendto'.")

class TCPSocket(EasySocket):

    '''
    Creates an instance of TCPSocket. Can take a regular socket as argument to wrap it into
    a TCPSocket but raises a ValueError exception if this socket's protocol isn't SOCK_STREAM.
    '''

    def __init__(self, *, encoding="raw", socket=None, host=DEFAULT_HOST, buffer_size=4096):
        if socket is not None and socket.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_STREAM:
            raise ValueError("The socket's protocol must be SOCK_STREAM to be wrapped into a TCPSocket.")
        super().__init__(protocol=SOCK_STREAM, socket=socket, host=host, encoding=encoding, buffer_size=buffer_size)

    def sendto(self, *args, **kargs):
        raise NotImplementedError("The method 'sendto' doesn't exist on TCPSocket. Try 'send'")

    def accept(self):
        '''
        Accepts a pending connection on the socket if one is available, blocks otherwise. Returns
        two values, an instance of TCPSocket initialized with the parent socket settings and the
        address of the newly connected peer.
        '''
        sock, addr = self._socket.accept()
        socket = TCPSocket(socket=sock, encoding=self.encoding, buffer_size=self.buffer_size)
        return socket, addr
