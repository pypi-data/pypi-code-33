from selectors import EVENT_READ

from bgez.network import ChannelState, DEFAULT_HOST
from bgez.network.udp import UDPChannel
from bgez.network import UDPSocket

__all__ = [
    'UDPClient',
]

class UDPClient(UDPChannel):
    '''
    A UDPClient manages a UDPChannel and is bound to a host (address, port). It does everything
    a UDPChannel does but manages its own sends/receives, meaning it doesn't need a dedicated
    manager to work (like a UDPChannel would). Like any other manager, it needs to be called
    regularly in order to work.
    '''

    def __init__(self, network_selector, *, host=DEFAULT_HOST, buffer_size=4096):
        socket = UDPSocket(host=host, buffer_size=buffer_size)
        super().__init__(None, socket)
        self.__selector = network_selector

    def connect(self, destination):
        '''
        "Connects" the UDPClient to the server at `destination`, meaning that it will only
        process messages coming from `destination`. Emits a "connect" event.
        '''
        if self._state == ChannelState.PENDING:
            self._destination = destination
            self.__selector.register(self._socket, EVENT_READ, self._on_message)
            self._state = ChannelState.CONNECTED
            self.emit("connect", self)

    def close(self):
        '''Closes the underlying socket and calls the UDPChannel's close() method.'''
        if self._state != ChannelState.CLOSED:
            self.__selector.unregister(self._socket)
            self._socket.close()
            super().close()

    def _on_message(self, *args, **kargs):
        '''
        Gets the upcoming message and check its sender. The message is processed only if the sender
        is the client's destination, otherwise it's ignored.
        '''
        message, sender = self._socket.recvfrom("raw")
        if sender == self._destination:
            self.on_read(message)
