from selectors import EVENT_READ, EVENT_WRITE
from threading import RLock

from bgez.network.easysocket import TCPSocket, DEFAULT_HOST
from bgez.network.tcp import TCPChannel
from bgez.network import ChannelState

__all__ = [
    'TCPClient',
]

class TCPClient(TCPChannel):
    '''
    A TCPClient is TCPChannel able to connect itself to a destination. It does everything a TCPChannel
    does and emits its "connect" event when the connection is made. See TCPChannel for
    detail about `is_stream`.
    '''

    def __init__(self, network_selector, *, host=DEFAULT_HOST, is_stream=True, buffer_size=4096):
        socket = TCPSocket(host=host, buffer_size=buffer_size)
        super().__init__(None, socket, is_stream=is_stream)
        self.__selector = network_selector

    def connect(self, destination):
        '''Starts the connection to `destination`.'''
        self._destination = destination
        self.__selector.register(self._socket, EVENT_WRITE, self.__on_connection)
        self._socket.connect_ex(destination)

    def __on_connection(self, *args, **kargs):
        '''Triggered when the connection is made. Emits a "connect" event with self as arguments.'''
        self.__selector.modify(self._socket, EVENT_READ, self.on_read)
        self._state = ChannelState.CONNECTED
        self.emit("connect", self)
