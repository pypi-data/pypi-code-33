from selectors import EVENT_READ
from threading import RLock

from bgez.network import UDPSocket, ChannelState
from bgez.core.events import EventEmitter
from bgez.network.udp import UDPChannel
from bgez import logger

__all__ = [
    'UDPServer',
]

class UDPServer(EventEmitter):
    '''
    A UDPserver is bound on a socket and listens for messages. When a message is received,
    it's given to the channel "connected" to the sender. If there wasn't already a channel
    for this sender, one is created and the "connect" event is emitted, with the new channel
    as only argument.
    '''

    EVENTS = ("connect", "close") # Events emittable by the UDPServer

    def __init__(self, network_selector, host):
        super().__init__(self.EVENTS)
        self.__selector = network_selector
        self.__socket = self.__host = None
        self.__paused = True
        self.__lock = RLock()
        self.__channels = {}
        self.__init_server(host)

    def start(self):
        '''Starts the server by allowing it to accept new "connections".'''
        self.__paused = False

    def close(self):
        '''Closes every channel then closes the UDPServer itself.'''
        if self.__socket is None:
            logger.warning("A UDPServer can only be closed once.")
            return

        with self.__lock:
            for channel in self.channels:
                channel.close()
            self.__selector.unregister(self.__socket)

            self.__socket.close()
            self.__socket = None
            self.emit("close", self)

    def pause(self):
        '''Pauses the server, preventing it from accepting "connections".'''
        self.__paused = True

    def resume(self):
        '''Resumes the server, allowing it to accept "connections".'''
        self.__paused = False

    def __init_server(self, host):
        '''Initialize the UDPServer on given host.'''
        self.__socket = UDPSocket(host=host)
        self.__selector.register(self.__socket, EVENT_READ, self.__on_message)
        self.__host = self.__socket.getsockname()

    def __close_channel(self, channel):
        '''Closes the given channel and stops tracking it.'''
        with self.__lock:
            del self.__channels[channel.destination]

    def __on_message(self, *args, **kargs):
        '''
        Gets the upcoming message and its sender, and gives the message to the corresponding channel. If
        the sender isn't linked to any channel and the server is activated, a new channel is created and
        the "connect" event is emitted.
        '''
        message, sender = self.__socket.recvfrom("raw")
        with self.__lock:
            channel = self.__channels.get(sender, None)

            if self.__paused:
                if channel is not None:
                    channel.on_read(message)
                return

            if channel is None:
                channel = self.__create_channel(sender)
                self.emit("connect", channel)
            channel.on_read(message)

    def __create_channel(self, destination):
        channel = UDPChannel(destination, self.__socket)
        self.__channels[destination] = channel
        channel.once("close", self.__close_channel)

        channel._state = ChannelState.CONNECTED
        return channel

    def __repr__(self):
        haddr, hport = self.__host
        state = "closed" if self.closed else "paused" if self.__paused else "running"
        return f"<{self.__class__.__name__} [{state}] host={haddr}:{hport}>"

    @property
    def closed(self):
        '''Returns whether the UDPServer is closed or not.'''
        return self.__socket is None

    @property
    def paused(self):
        '''Returns whether the UDPServer is paused or not.'''
        return self.__paused

    @property
    def host(self):
        '''Returns the UDPServer's host.'''
        return self.__host

    @property
    def channels(self):
        '''Returns the list of current channels.'''
        with self.__lock:
            return list(self.__channels.values())
