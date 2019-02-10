from bgez.network.channel import IPChannel

__all__ = [
    'UDPChannel',
]

class UDPChannel(IPChannel):
    '''
    Creates a UDPChannel from `host` to `destination` with an already created UDP socket. UDPChannels
    are supposed to emulate a UDP "connections" since, on a UDPChannel, only communications between
    `host` and `destination` are allowed. UDPChannels are made to work alongside the UDPClient and
    UDPPoint, so you shouldn't instantiate one yourself unless you know what you're doing.
    '''

    # Emitable events
    EVENTS = ("read", "connect", "close")

    def __init__(self, destination, socket):
        super().__init__(destination, socket, self.EVENTS)

    def on_read(self, message):
        '''
        Triggers callbacks set on read events for this channel, with the channel itself and the
        message as arguments.
        '''
        if self.paused: return
        self.emit("read", self, message)

    def _send(self, message):
        return self._socket.sendto(message, self._destination)

    @property
    def buffer_size(self):
        return self._socket.buffer_size
