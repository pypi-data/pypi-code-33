from threading import Thread, Timer as threadTimer
from pygame import event as pyEvent, register_quit
from math import floor

# By Gudni Natan Gunnarsson, 2017


class Timer(object):
    """This is an internal class that handles individual timers.
    Use the BetterTimers class instead."""
    def __init__(self, event, rate):
        '''Create the timer object'''
        self.__running = False
        self.__event = event
        self.__rate = rate
        self.__t = None

    def _eventPoster(self, event, rate):
        '''Posts events at the specified rate via a threadTimer.'''
        e = pyEvent

        def post(event):
            if self.__running:
                if type(event) is e.EventType:
                    e.post(event)
                else:
                    e.post(e.Event(event))
                postThread.run()
                if not postThread.daemon:
                    postThread.daemon = True

        postThread = threadTimer(float(rate - 1) / 1000.0, post, args=(event,))
        postThread.daemon = True
        postThread.start()

    def start_timer(self):
        '''Start the event timer.  Object will start to post events at a
        regular rate.
        '''
        if not self.__running:
            self.__t = Thread(
                target=self._eventPoster,
                args=(self.__event, self.__rate)
            )
            self.__t.daemon = True
            self.__running = True
            self.__t.start()

    def stop_timer(self):
        '''Stop the event timer if it was running'''
        if self.__running:
            self.__running = False
            self.__t.join()

    def change_rate(self, rate):
        '''Changes the timer rate and restarts it.'''
        self.__rate = rate

        self.stop_timer()
        self.start_timer()

    def get_event(self):
        return self.__event


class BetterTimers():
    def __init__(self):
        '''Makes a BetterTimers object. Call pygame.quit to end all timers.'''
        self.__timers = list()
        register_quit(self.end_all_timers)

    def set_timer(self, event, rate, delay=0):
        '''Sets a timer for an event. Each event object will only have one
        timer associated with it. Setting a timers rate to 0 will stop it.'''
        if floor(delay) > 0:
            delayTimer = threadTimer(
                float(delay - 1) / 1000.0,
                self.set_timer,
                args=(event, rate)
            )
            delayTimer.daemon = True
            delayTimer.start()
            return

        t = Timer(event, rate)
        for e in self.__timers:
            if e.get_event() == event:
                if floor(rate) > 0:
                    e.change_rate(rate)
                else:
                    e.stop_timer()
                    self.__timers.remove(e)
                return
        if floor(rate) > 0:
            t.start_timer()
            self.__timers.append(t)

    def stop_timer(self, event):
        '''Stops any timer associated to the given event.'''
        self.set_timer(event, 0)

    def end_all_timers(self):
        '''Stops all the timers'''
        for t in self.__timers:
            t.stop_timer()

        self.__timers = list()

timers = BetterTimers()
