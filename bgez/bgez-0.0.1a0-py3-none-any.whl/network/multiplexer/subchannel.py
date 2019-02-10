from bgez.core.events import EventEmitter

class SubChannel(EventEmitter):
    '''
    Virtual network object meant to be used alongside MultiplexedChannels. SubChannels are
    identified via ther unique ID and only read messages addressed to them.

    Note: `sub_id` must be a string and will stored as a byte-object for performance purposes.
    '''

    # Emitable events
    EVENTS = ("read", "close")

    def __init__(self, parent, sub_id):
        super().__init__(self.EVENTS)
        self._parent = parent
        self._id = sub_id
        # Store the ID's length so it doesn't have to be recomputed for each send
        self._id_len = len(self._id).to_bytes(1, "big")

    def send(self, message):
        '''Sends `messages` on the SubChannel.'''
        payload = b"".join((self._id_len, self._id, message))
        return self._parent.send(payload)

    def _on_read(self, message):
        '''
        Emits a "read" event on the SubChannel, with the SubChannel and the message as arguments.
        '''
        self.emit("read", self, message)

    def close(self):
        '''Closes this SubChannel by sending an empty message and emits a "close" event.'''
        self.send(b"")
        self.emit("close", self)

    def get_id(self, *, as_string=True):
        '''
        Returns the SubChannel's ID. If `as_string` is specified (defaults to True) and doesn't
        evaluate to True, it returns the ID as a byte-object, which is the way it's stored.
        '''
        return self._id.decode() if as_string else self._id

    def __repr__(self):
        return f"<{self.__class__.__name__} ID='{self.get_id()}' child of {self._parent}>"
