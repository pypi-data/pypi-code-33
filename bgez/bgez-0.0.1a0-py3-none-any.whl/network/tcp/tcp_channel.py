from bgez.network.channel import IPChannel, ChannelState

__all__ = [
    'TCPChannel',
]

SIZE_B = 2

class TCPChannel(IPChannel):
    '''
    Creates a TCPChannel from `host` to `destination` with an already created TCP socket. TCPChannels
    work like regular connected TCP sockets, so they can't be used to accept connections. They are
    to be used alongside the TCPServer so you shouldn't instantiate a TCPChannel yourself unless
    you've created your own server. Depending on the boolean value of `is_stream`, the
    TCPChannel will either send/read data as a stream or as independant messages.
    '''

    # Emitable events
    EVENTS = ("read", "connect", "close")

    def __init__(self, destination, socket, *, is_stream=True, buffer_size=4096):
        super().__init__(destination, socket, self.EVENTS)
        self.__handler = StreamHandler() if is_stream else MessageHandler()
        self.buffer_size = buffer_size

    def _send(self, payload):
        '''Processes `payload` through its handler then sends it.'''
        payload = self.__handler.process_send(payload)
        return self._socket.send(payload)

    def on_read(self, *args, **kargs):
        '''
        Reads the upcoming payload and processes it through its handler, then triggers
        callbacks set on read events for this channel, with the channel itself and the
        message as arguments.
        '''
        payload = self._socket.recv()
        if not payload:
            self.emit("closed", self)
        elif not self.paused:
            for payload in self.__handler.process_read(payload):
                self.emit("read", self, payload)

    def __repr__(self):
        haddr, hport = self.host
        daddr, dport = self.destination
        state = ChannelState.state_to_str[self.state]
        return (f"<{self.__class__.__name__} [{state}] host={haddr}:{hport}"
            f" destination={daddr}:{dport} mode={self.__handler.mode}>")

    @property
    def timeout(self):
        return self._socket.gettimeout()
    @timeout.setter
    def timeout(self, new_timeout):
        self._socket.settimeout(new_timeout)

    @property
    def buffer_size(self):
        return self._socket.buffer_size
    @buffer_size.setter
    def buffer_size(self, buffer):
        self._socket.buffer_size = buffer

class StreamHandler:
    '''
    Processes payloads for stream-based channels. As streaming is the default behaviour
    of TCP sockets (and therefore TCPChannels), this class is mainly a placeholder.
    '''

    def __init__(self):
        self.mode = "stream"

    def process_send(self, payload):
        '''In stream mode, the payload doesn't need special processing.'''
        return payload

    def process_read(self, payload):
        '''In stream mode, the payload doesn't need special processing.'''
        yield payload

class MessageHandler:
    '''
    Processes payloads for message-based channels. When sending data, the size of the
    data is added to the beggining of the payload so that the process_read() method
    knows how big the message is.
    '''

    def __init__(self):
        self.__message = b""
        self.mode = "message"

    def process_send(self, payload):
        '''Puts the size of the payload at its beginning before sending it.'''
        msg_size = len(payload).to_bytes(SIZE_B, "big")
        return b"".join((msg_size, payload))

    def process_read(self, payload):
        '''Adds `payload` to the already accumulated message and yields all full messages.'''
        while True:
            payload = self.__message = self.__message + payload
            expected_size = payload[:SIZE_B]
            if len(expected_size) != SIZE_B: return

            expected_size = int.from_bytes(expected_size, "big")
            message = payload[SIZE_B : SIZE_B + expected_size]
            if len(message) != expected_size: return

            self.__message = payload[SIZE_B + expected_size:]
            payload = b"" # DO NOT REMOVE
            yield message
