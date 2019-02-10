from selectors import DefaultSelector

__all__ = [
    'NetworkManager',
]

class NetworkManager(DefaultSelector):
    '''
    An enhanced selector that "selects" on all registered sockets when called, and so
    until there is no more data to process. You can use multiple NetworkManagers, but
    if you're using BGEz's event-loop, you should only use one.
    '''

    def __call__(self, timeout=0):
        self.select(timeout=timeout)

    def select(self, timeout=0):
        while True:
            items = super().select(timeout)
            if not items: break
            for key, _ in items:
                key.data(key.fileobj)
