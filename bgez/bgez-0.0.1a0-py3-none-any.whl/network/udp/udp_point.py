from selectors import EVENT_READ
from threading import RLock

from bgez.network import ChannelState, DEFAULT_HOST
from bgez.core.events import EventEmitter
from bgez.network.udp import UDPChannel
from bgez.network import UDPSocket
from bgez import logger

__all__ = [
    'UDPPoint',
]

class UDPPoint(EventEmitter):
    '''
    A UDPPoint is client-side entity made to create multiple channels from the same socket.
    Since a UDP socket isn't really "connected", it can send/receive messages to/from any
    peer. The UDPPoint binds itself to a socket on `host` and can give channels on demand
    (see `get_channel` and UDPChannel). When it receives a message, it routes it to the
    corresponding channel, or drops it if there wasn't a channel to give it to.
    '''

    EVENTS = ("connect", "close") # Events emittable by the UDPPoint

    def __init__(self, network_selector, *, host=DEFAULT_HOST, buffer_size=4096):
        super().__init__(self.EVENTS)
        self.__selector = network_selector
        self.__socket = self.__host = None
        self.__lock = RLock()
        self.__channels = {}
        self.__init_point(host, buffer_size)

    def get_channel(self, destination):
        '''
        Creates a channel between the UDPPoint and `destination`. The returned channel is
        used exactly like a UDPClient, except it's already "connected".

        Note: If a channel already exists for `destination`, it is returned
        '''
        if self.closed:
            logger.error("Can't create channels on a closed UDPPoint.", stack_info=True)
            return None

        with self.__lock:
            channel = self.__channels.get(destination, None)
            if channel is not None:
                return channel

            channel = UDPChannel(destination, self.__socket)
            self.__channels[destination] = channel
            channel.once("close", self._close_channel)

        channel._state = ChannelState.CONNECTED
        return channel

    def close(self):
        '''Closes every channel then closes the UDPPoint itself.'''
        if self.closed:
            logger.warning("A UDPPoint can only be closed once.")
            return

        with self.__lock:
            for channel in self.channels:
                channel.close()
            self.__selector.unregister(self.__socket)

            self.__socket.close()
            self.__socket = None
            self.emit("close", self)

    def __init_point(self, host, buffer_size):
        '''
        Initialize the UDPPoint on given host. The `buffer_size` defines the size of the buffer used
        when reading an upcoming message.
        '''
        self.__socket = UDPSocket(host=host, buffer_size=buffer_size)
        self.__selector.register(self.__socket, EVENT_READ, self._on_message)
        self.__host = self.__socket.getsockname()

    def _close_channel(self, channel):
        '''Removes the given channel from the channels registry.'''
        with self.__lock:
            del self.__channels[channel.destination]

    def _on_message(self, *args, **kargs):
        '''
        Gets the upcoming message and its sender, and gives the message to the corresponding channel.
        If the sender isn't linked to any channel, the message is dropped.
        '''
        message, sender = self.__socket.recvfrom("raw")
        with self.__lock:
            channel = self.__channels.get(sender, None)
            if channel is None: return

            channel.on_read(message)

    def __repr__(self):
        haddr, hport = self.__host
        state = "closed" if self.closed else "running"
        return f"<{self.__class__.__name__} [{state}] host={haddr}:{hport}>"

    @property
    def closed(self):
        '''Returns whether the UDPPoint is closed or not.'''
        return self.__socket is None

    @property
    def host(self):
        '''Returns the UDPPoint's host.'''
        return self.__host

    @property
    def channels(self):
        '''Returns the list of current channels.'''
        with self.__lock:
            return list(self.__channels.values())

    @property
    def buffer_size(self):
        return self.__socket.buffer_size
    @buffer_size.setter
    def buffer_size(self, new_buffer):
        self.__socket.buffer_size = new_buffer
