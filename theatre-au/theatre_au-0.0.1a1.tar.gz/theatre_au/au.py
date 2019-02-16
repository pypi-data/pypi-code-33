from copy import copy

def default_cost(cost=0):
    def _inner_cost(func):
        func.default_cost = cost
        return func
    return _inner_cost


def construct_task(func):
    '''
    Constructs a task from a function.
    A task is a function object with the attribute `is_task` set to True.
    If the function provided has a duration (or "cost") associated with it, it will run once per `cost` invocations.
    A task has an attribute, `completed`, which will be False unless the target function has just executed.
    :param func: the function to be transformed into a task. Cost is added to this function via the default_cost decorator.
    :return: A Task, which is a function object which may run every `cost` invocations.
    '''
    func = copy(func)

    # Mutable value here lets us break out of `invoker`'s closure. Format is [expected_duration, ticks_passed]
    completion_status = [0, 0]
    def max_ticks(): return completion_status[0]
    def ticks_passed(): return completion_status[1]
    def sufficient_time_passed(): return ticks_passed() == max_ticks()
    def just_ran(): return completion_status[1] is 0

    # If there's no cost set up, just run the target function, but remember to set func.completed to True when we do.
    if 'default_cost' not in dir(func):
        func.default_cost = 1

    # The function has a cost associated with it, so only run after a limited number of invocations.
    completion_status[0] = func.default_cost

    def invoker(*args, **kwargs):
        completion_status[1] += 1

        if sufficient_time_passed():
            completion_status[1] = 0
            return func(*args, **kwargs)

        # Didn't return function result; must not have enough invocations yet.
        return None

    invoker.invocations = completion_status[1]
    invoker.just_ran = just_ran
    return invoker


class Clock(object):
    def __init__(self, max_ticks=-1):
        self.max_ticks = max_ticks  # -1 => runs indefinitely
        self.ticks_passed = 0
        self.listeners = []

    @property
    def time_exhausted(self):
        if self.max_ticks is None:
            return False
        return self.ticks_passed >= self.max_ticks

    def add_listener(self, actor):
        # We need things to be able to `perform()` so we can `tick()` properly.
        if 'perform' not in dir(actor):
            class BadListenerException(Exception):
                pass
            raise BadListenerException("Listener provided must adhere to the actor spec expected; specifically, it should have a `perform()` method which returns a generator of functions.")

        self.listeners.append(actor.perform())

    def tick(self, ticks_remaining=None):
        '''
        Allow time to pass for the actors attached to this clock
        :param ticks_remaining: The number of ticks to pass. If None, ticks until max_ticks passed.
        Note that if max_ticks is None and ticks_remaining is None, simulation runs indefinitely.
        Default: None.
        :return: None.
        '''
        if ticks_remaining is None:
            ticks_remaining = self.max_ticks
            
        while not self.time_exhausted and ticks_remaining is not 0:
            for performance in self.listeners:
                next(performance)
            self.ticks_passed += 1
            ticks_remaining -= 1
