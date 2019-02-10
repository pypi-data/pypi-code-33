from bgez.core.events import EventEmitter
from bgez import logger

__all__ = [
    'ChannelState',
]

class ChannelState:
    '''Simple class defining the possible states of an IPChannel.'''
    CLOSED = 0
    CONNECTED = 1
    PENDING = 2

    state_to_str = {
        CLOSED : "closed",
        CONNECTED : "connected",
        PENDING : "pending"
    }

# "host" and "destination" are tuples of (address, port)

class IPChannel(EventEmitter):
    '''You shouldn't instantiate an IPChannel unless you know exactly what you're doing '''

    def __init__(self, destination, socket, events):
        super().__init__(events)
        self._socket = socket
        self._host = socket.getsockname()
        self._state = ChannelState.PENDING
        self._destination = destination
        self.paused = False

    def send(self, message):
        '''
        Sends the given message to the channel's destination. Returns the amount of bytes sent;
        if it's 0, the connection is probably no longer valid.
        '''
        addr, port = self.host
        if self.paused:
            logger.warning("Send attempt on a paused channel running on host %s:%d.", addr, port)
            return 0
        if self._state != ChannelState.CONNECTED:
            logger.warning("Send attempt on an unconnected channel running on host %s:%d.", addr, port)
            return 0
        return self._send(message)

    def pause(self):
        '''
        Pauses the current channel, hence preventing it from sending and receving data.
        Equivalent to setting its paused property to True.
        '''
        self.paused = True

    def resume(self):
        '''
        Resumes the current channel, hence re-allowing it to send and receive data.
        Equivalent to setting its paused property to False.
        '''
        self.paused = False

    def close(self):
        '''
        Makes the channel emit a "close" event. It relies on a "manager" to change its state to
        CLOSED and close the underlying socket.
        '''
        if self._state == ChannelState.CLOSED:
            addr, port = self.host
            logger.warning("Close attempt on an already closed channel on host '%s:%d'.", addr, port)
            return
        self._state = ChannelState.CLOSED
        self.emit("close", self)

    def __repr__(self):
        haddr, hport = self.host
        daddr, dport = self.destination
        state = ChannelState.state_to_str[self._state]
        return f"<{self.__class__.__name__} [{state}] host={haddr}:{hport} destination={daddr}:{dport}>"

    @property
    def state(self):
        return self._state

    @property
    def destination(self):
        return self._destination

    @property
    def host(self):
        return self._host
