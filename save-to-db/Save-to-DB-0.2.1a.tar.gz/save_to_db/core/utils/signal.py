class Signal(object):
    """ This class is used to emit signals.
    
    :ivar name: Signal name.
    """
    
    def __init__(self, name):
        self.name = name
        self.__listeners = []
    
    def register(self, listener):
        """ Registers listener to the signal.
        
            .. note::
                This method can be also used as a decorator:
                
                .. code-block:: Python
                
                    signal = Signal('MySignal')
                    
                    @signal.register
                    def signal_listener(value):
                        print('Signal value: {}'.format(value))
                    
                    # Output: "Signal value: Demo Value"
                    signal.emit('Demo Value')
        """
        if listener not in self.__listeners:
            self.__listeners.append(listener)
        # returning listener makes it possible to use this function as
        # a decorator
        return listener
    
    def unregister(self, listener):
        """ Unregisters listener from the signal. """
        if listener in self.__listeners:
            self.__listeners.remove(listener)
    
    def clear(self):
        """ Removes all listeners from the signal. """
        self.__listeners.clear()
    
    def emit(self, *args, **kwargs):
        """ Emits the signal. All listeners will be called with the same
        arguments as this method.
        """
        for listener in self.__listeners:
            listener(*args, **kwargs)
    
    def __repr__(self):
        return '<Signal(\'{}\')>'.format(self.name)