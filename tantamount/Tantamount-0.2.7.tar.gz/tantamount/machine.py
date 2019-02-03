from threading import Lock, Thread
from sched import scheduler
from time import time
from threading import Event
from collections import namedtuple


class Machine:
    _start = None
    _state = None
    _states = {}
    _transitions = {}
    _timeoutevent = None
    _timeoutevents = {}
    _schedulerthread = None
    _firststartdone = False
    _delayfunc = None
    _scheduler = None
    _lock_operate = None

    def __init__(self):
        # usually scheduler is initialized with timefunc=time and
        # delayfunc=sleep. the problem is when using sleep, that if the
        # last event has been removed from scheduler using scheduler.cancel(),
        # the scheduler continues to sleep until the set delay has passed
        # altough no event exists that will be processed. the quick fix for
        # this is to use threading.Event.wait() instead. if Event.set() is
        # never called, the loop in scheduler.run behaves exactly like when
        # using sleep(). But with Event.set() a recalculation of the delay to
        # the next event can always be enforced. Thereafter, if Event.set() is
        # called after scheduler.cancel() the scheduler can adapt to the
        # new situation.
        self._delayfunc = Event()
        self._scheduler = scheduler(time, self._delayfunc.wait)
        self._lock_operate = Lock()

    def setstartstate(self, stateid):
        self._state = self._states[stateid]
        self._start = self._state

    def addstate(self, stateid, state, groupid="_"):
        state.id = stateid
        state.groupid = groupid
        self._states[stateid] = state

    def addtransition(self, startstateid, transitionid, targetstateid, actionFunc=None, actionArgs=()):
        Entry = namedtuple('Entry', ['targetstateid', 'actionFunc', 'actionArgs'])
        transition = Entry(targetstateid=targetstateid, actionFunc=actionFunc, actionArgs=actionArgs)
        try:
            self._transitions[startstateid][transitionid] = transition
        except KeyError:
            self._transitions[startstateid] = {}
            self._transitions[startstateid][transitionid] = transition

    def addtimeoutevent(self, stateid, eventid, seconds):
        try:
            if self._transitions[stateid][eventid]:
                self._timeoutevents[stateid] = (eventid, seconds)
        except KeyError as e:
            print("Machine.addtimeoutevent KeyError. stateid=" +
                  str(stateid) + ", eventid=" + str(eventid))
            raise e

    def firststart(self):
        if not self._firststartdone:
            self._firststartdone = True
            with self._lock_operate:
                self._starttimeoutevent()
                event_id = self._state.on_entry()
            if event_id:
                self.operate(event_id)

        else:
            raise Exception("context.start must only be called once.")

    def _gettransition(self, stateid, eventid):
        try:
            transition = self._transitions[stateid][eventid]
        except KeyError as e:
            print("Machine.getnextstate KeyError. stateid=" +
                  str(stateid) + ", eventid=" + str(eventid))
            self._lock_operate.release()
            raise e
        try:
            nextstate = self._states[transition.targetstateid]
        except KeyError as e:
            print("Machine.getnextstate KeyError. transition=" +
                  str(transition.targetstateid))
            self._lock_operate.release()
            raise e

        return nextstate, transition.actionFunc, transition.actionArgs

    def _starttimeoutevent(self):
        if self._timeoutevent is not None:
            raise Exception("context._starttimeoutevent has been called while "
                            "another timeoutevent has been still active.")

        try:
            (eventid, seconds) = self._timeoutevents[self._state.id]
            self._timeoutevent = self._scheduler.enter(seconds,
                                                       1, self.operate,
                                                       [eventid, ])
            threadname = type(self).__name__ + "|" + \
                         type(self._timeoutevent).__name__ + " (" + \
                         str(self._state.id) + ", " + str(eventid) + ")"
            self._schedulerthread = Thread(target=self._scheduler.run,
                                           name=threadname)
            self._schedulerthread.daemon = True
            self._schedulerthread.start()
        except KeyError:
            pass

    def _stoptimeoutevent(self):
        if self._timeoutevent is not None:
            try:
                self._scheduler.cancel(self._timeoutevent)
                self._delayfunc.set()
            except ValueError as x:
                pass
            self._timeoutevent = None

    def restarttimeoutevent(self):
        self._stoptimeoutevent()
        self._starttimeoutevent()

    def get_active_state(self):
        return self._state

    def operate(self, eventid):
        # three sources may call context.operate():
        #    - external events
        #    - states that immediately trigger an event transition in on_entry
        #    - timeouts
        with self._lock_operate:
            while eventid:
                self._stoptimeoutevent()
                self._state.on_exit()
                nextState, actionFunc, actionArgs = self._gettransition(self._state.id, eventid)
                if actionFunc:
                    actionFunc(*actionArgs)
                self._state = nextState
                self._starttimeoutevent()
                eventid = self._state.on_entry()

    def stop(self):
        self._stoptimeoutevent()
