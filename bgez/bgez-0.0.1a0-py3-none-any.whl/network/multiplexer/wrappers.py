from threading import RLock

from bgez.network.multiplexer.subchannel import SubChannel
from bgez.core.events import EventEmitter

__all__ = [
    'MultiplexedChannel', 'MultiplexedServer',
]

class MultiplexedChannel(EventEmitter):
    '''
    Wrapper over an IPChannel subclass that allows you to create SubChannels (see SubChannel).
    The MultiplexedChannel automatically routes messages to the targetted SubChannel. To
    do so, it creates SubChannels with a unique ID which is sent alongside the message.
    On receive, the ID is extracted from the payload and the message is given to corresponding
    SubChannel. When a new SubChannel is auto-created, the "subchannel" event is emitted.

    `Protocol: "id_size + id + message"`. With id_size being encoded on a byte, the maximum size
    of id is 256 characters.

    Important: For TCP, it only works in message mode (is_stream=False).
    '''

    EVENTS = ("subchannel",)

    def __init__(self, channel):
        super().__init__(channel.events + self.EVENTS)
        channel.on("read", self._on_message)
        channel.once("close", self._close)
        self._channel = channel
        self.__lock = RLock()
        self._subchannels = {}
        self._channel.any(self.emit)

    def get_subchannel(self, sub_id):
        '''Gives the SubChannel with ID `sub_id`. If it doesn't exist yet, it's created.'''
        sub_id = sub_id.encode()
        with self.__lock:
            sub = self._subchannels.get(sub_id, None)
            if sub is not None:
                return sub

            sub = self._create_sub(sub_id)
        return sub

    def _create_sub(self, sub_id):
        '''Returns a freshly created SubChannel.'''
        with self.__lock:
            sub = SubChannel(self, sub_id)
            sub.once("close", self._close_sub)
            self._subchannels[sub_id] = sub
            return sub

    def _close(self, channel):
        '''Closes the MultiplexedChannel by closing all its SubChannels.'''
        with self.__lock:
            for sub in self._subchannels:
                sub.close()

    def _close_sub(self, sub):
        '''Removes the given SubChannel from the registry.'''
        with self.__lock:
            del self._subchannels[sub.get_id(as_string=False)]

    def _on_message(self, channel, payload):
        '''
        Routes `payload` to the targetted SubChannel which ID is extracted from `payload`. If
        no SubChannel had the extrated ID, a new SubChannel is created with this ID and a the
        "subchannel" event is emitted.
        '''
        if not payload:
            return
        length = int(payload[0])
        sub_id = payload[1:length + 1]
        message = payload[length + 1:]

        with self.__lock:
            sub = self._subchannels.get(sub_id, None)
            if not message:
                if sub is not None:
                    sub.close()
                return

            if sub is None:
                sub = self._create_sub(sub_id)
                self.emit("subchannel", sub)
        sub._on_read(message)

    def __call__(self):
        # __getattr__ can't handle this one, we need to add it
        self._channel()

    def __getattr__(self, name):
        return getattr(self._channel, name)

    def __repr__(self):
        return f"<{self.__class__.__name__} on {self._channel}>"

    @property
    def subchannels(self):
        '''Returns the list of current subchannels.'''
        return list(self._subchannels.values())

class MultiplexedServer(EventEmitter):
    '''
    Wrapper over server (either UDPServer or TCPServer) that makes it create MultiplexedChannels
    instead of regular IPChannels. A part from that, it behaves exactly like a regular server.
    See MultiplexedChannel for more detail.

    Important: For TCP, it only works in message mode (is_stream=False).
    '''

    def __init__(self, server):
        super().__init__(server.events)
        server.any(self.__route_events)
        self._server = server

    def __route_events(self, subject, *args):
        '''
        Simply re-remits any events emitted by the underlying server. However, if this event
        is "connect", the channel given is wrapped in a MultiplexedChannel before the event is
        re-emitted.
        '''
        if subject == "connect":
            wrapped = MultiplexedChannel(args[0])
            args = (wrapped, ) + args[1:]
        self.emit(subject, *args)

    def __call__(self):
        # __getattr__ can't handle this one, we need to add it
        self._server()

    def __getattr__(self, name):
        return getattr(self._server, name)
