# coding=utf-8
'''
Custom thread objects for some kinds of loop thread, like listening thread.
In other words, the thread usually loop regularly and check for a signal
to stop its work.

Using the threading.Event object as a 'stop event' to tell the thread to stop.
'''

import threading
import inspect

def _setDaemon(thread):
    thread.setDaemon(True)

class StoppableThread(threading.Thread):
    '''
    Thread with a stop() method.

    A threading.Event will be set as an attribute,
    and passed to the target function if possible.
    with default name 'stop_event'. The thread itself has to
    check the event regularly and stop itself 
    when the event is set e.g. stop_event.is_set().

    Note: you should not change the event.
    '''

    def __init__(self, group=None, target=None, name=None, args=(),
                 kwargs=None, event_name=None, **kw):
        '''
        Arguments are same as threading.Thread with additional 'event_name',
        which specify the argument's name for the stop event.

        The event name defaults None indicate a non-strict mode, 
        and it use 'stop_event' as the name.
        Otherwise it is strict mode using the specified name.

        It check whether the target function can receive the event.

        In non-strict mode, it try using 'kwargs' first, then 'args'.
        It may replace the value in 'kwargs', 
        and do nothing when it is impossible to pass the event.

        In strict mode, it only use 'kwargs' and raise a ValueError 
        when there is an key confliction or it is impossible to pass the event.
        '''
        strict = event_name != None
        if not event_name:
            event_name = 'stop_event'
        self._stop_event = threading.Event()
        self.__setattr__(event_name, self._stop_event)
        if target != None:
            if kwargs == None:
                kwargs = {}
            spec = inspect.getargspec(target)
            # if it is possible to pass the event
            if spec.keywords != None or \
            (len(spec.args) > len(args) and event_name in spec.args[len(args):]):
                if strict and event_name in kwargs:
                    raise ValueError('the name \'' + event_name +
                        '\' for stop event already exists in the \'kwargs\'')
                else:
                    kwargs[event_name] = self._stop_event
            elif strict:
                raise ValueError('impossible to pass the stop event (strict mode)')
            elif spec.varargs != None or len(spec.args) > len(args):
                args = args + self._stop_event
        super(StoppableThread, self).__init__(group, target, name, args,
                                              kwargs, **kw)
        return

    def stop(self, timeout=0):
        '''set the stop event to notify the thread to stop.
        and invoke join(timeout) unless the timeout is 0.
        @return whether it is alive'''
        self._stop_event.set()
        if timeout != 0:
            self.join(timeout)
        return self.isAlive()

    def stopped(self):
        '''whether the stop event is set'''
        return self._stop_event.is_set()

class ReStartableThread(object):
    '''
    Provide restartable feature in addition to StoppableThread.

    Note: start() and stop() must be called by pair, 
    otherwise there is no effect.

    Because new instance of Thread will be used after stop(),
    you should set your properties again yourself or use the processor.
    
    For convenience, you can set properties for the new instance directly
    after stop(). However, three methods are called on the old instance:
    join(), isAlive(), is_alive().

    The default processor will call setDaemon(True).
    '''
    _old_methods = ['join', 'isAlive', 'is_alive']
    def __init__(self, group=None, target=None, name=None, args=(),
        kwargs=None, event_name=None, processor=_setDaemon, **kw):
        '''
        @parameter processor  a function to process the Thread after created, 
                                maybe set some properties. can be None.
                                defaults to call setDaemon(True).
        '''
        self._args = (group, target, name, args, kwargs, event_name)
        self._kw = kw
        self._processor = processor
        self._rlock = threading.RLock()
        self._thread0 = None
        self._create()

    def _create(self):
        '''create new instance of Thread and mark not started'''
        # false: the thread is a new one, not started
        # true: the thread start() was called, but may be died
        self._started = False
        self._thread = StoppableThread(*self._args, **self._kw)
        if self._processor:
            self._processor(self._thread)

    def start(self):
        '''start the thread (after stop() or just at the first time).
        @return whether it start a thread.'''
        self._rlock.acquire()
        try:
            if self._started:
                return False
            self._started = True
            self._thread.start()
            return True
        finally:
            self._rlock.release()

    def stop(self, timeout=0):
        '''set the stop event and create new instance after start().
        @return whether it is alive'''
        self._rlock.acquire()
        try:
            if not self._started:
                return False
            rtn = self._thread.stop(timeout)
            self._thread0 = self._thread
            self._create()
            return rtn
        finally:
            self._rlock.release()

    def __getattr__(self, name):
        '''get method or attributes (e.g. the event) from the thread instance if not found.'''
        self._rlock.acquire()
        try:
            if self._started or not self._thread0 or name not in self._old_methods:
                return self._thread.__getattribute__(name)
            else:
                return self._thread0.__getattribute__(name)
        finally:
            self._rlock.release()
