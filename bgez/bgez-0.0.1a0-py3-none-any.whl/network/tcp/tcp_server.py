from selectors import EVENT_READ
from threading import RLock

from bgez.core.events import EventEmitter
from bgez.network.tcp import TCPChannel
from bgez.network import ChannelState
from bgez.network import TCPSocket
from bgez import logger

__all__ = [
    'TCPServer',
]

class TCPServer(EventEmitter):
    '''
    A TCPServer binds itself to a host (address, port) and uses TCPChannels to represent its clients.
    Once started, it will accept any connection and emit a "connect" event. You can pause and resume
    the server by calling pause() and resume(). A paused server will accept and immediately close
    new connections. See TCPChannel for detail about `is_stream`.
    '''

    EVENTS = ("connect", "close") # Events emittable by the server

    def __init__(self, network_selector, host, *, is_stream=True):
        super().__init__(self.EVENTS)
        self.__selector = network_selector
        self.__socket = self.__host = None
        self.__is_stream = is_stream
        self.__lock = RLock()
        self.__paused = False
        self.__channels = {} # Stores connected channels
        self.__init_server(host)

    def start(self, *, max_pending=8):
        '''
        Starts the server by putting it in listening state. There can be at most `max_pending`
        connections in wait of being accepted.
        '''
        self.__paused = False
        self.__selector.register(self.__socket, EVENT_READ, self._accept_connection)
        self.__socket.listen(max_pending)

    def close(self):
        '''
        Closes the TCPServer by closing all its channels, its underlying socket and selector, then
        becomes unavailable.
        '''
        if self.__socket is None:
            logger.warning("A TCPServer can only be closed once.")
            return True

        with self.__lock:
            for channel in self.channels:
                channel.close()
            self.__selector.unregister(self.__socket)

            self.__socket.close()
            self.__socket = None
            self.emit("close", self)
        return True

    def pause(self):
        '''Pauses the server to prevent it from accepting new connections.'''
        self.__paused = True

    def resume(self):
        '''Resumes the server hence allowing it to accepting new connections again.'''
        self.__paused = False

    def __init_server(self, host):
        '''Initialize the TCPServer by creating its underlying socket.'''
        self.__socket = TCPSocket(host=host, encoding="raw")
        self.__host = self.__socket.getsockname()

    def _close_channel(self, channel):
        '''
        Closes the given channel. Once closed, the last messages to send or read in the buffer are
        handled and the channel becomes unusable.
        '''
        with self.__lock:
            self.__selector.unregister(channel._socket)
            channel._socket.close()
            del self.__channels[channel]

    def _accept_connection(self, *args, **kargs):
        '''
        Accepts any incoming connection request. If the server is paused, connections are
        accepted and instantly closed to prevent the buffer from storing pending connections.
        '''
        client_socket, sender = self.__socket.accept()
        if self.__paused:
            client_socket.close()
            return
        self._add_accepted_channel(client_socket, sender)

    def _add_accepted_channel(self, new_socket, sender):
        '''
        Creates a TCPChannel with `new_socket` as host and `sender` as destination, then emits a
        "connect" event with the newly created channel as argument.
        '''
        host = new_socket.getsockname()

        with self.__lock:
            if self.closed: return

            channel = TCPChannel(sender, socket=new_socket, is_stream=self.__is_stream)
            self.__channels[sender] = channel

            self.__selector.register(new_socket, EVENT_READ, channel.on_read)
            channel._state = ChannelState.CONNECTED
            self.emit("connect", channel)

    def __repr__(self):
        haddr, hport = self.__socket.getsockname()
        state = "paused" if self.paused else "running"
        return (f"<{self.__class__.__name__} [{state}] host={haddr}:{hport}>"
            f" mode={self.__is_stream}")

    @property
    def closed(self):
        '''Returns whether the server is closed or not.'''
        return self.__socket is None

    @property
    def paused(self):
        '''Returns whether the serve is paused or not.'''
        return self.__paused

    @property
    def host(self):
        '''Returns the server's host.'''
        return self.__host

    @property
    def channels(self):
        '''Returns the list of channels connected to this server.'''
        with self.__lock:
            return list(self.__channels.values())
