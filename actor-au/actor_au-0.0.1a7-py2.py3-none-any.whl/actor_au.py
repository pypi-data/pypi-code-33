from abc import ABCMeta, abstractmethod
from Queue import Queue


class AbstractActor(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self.task_list = Queue()
        self.idle = lambda: None
        self.troupes = []

    def schedule_task(self, task):
        self.task_list.put(task)

    def recieve_message(self, message):
        self.schedule_task(message)

    @abstractmethod
    def get_next_task(self):
        '''
        Gets the next task from relevant work queues.
        Tasks are assumed to:
            - be functions
            - have any necessary arguments passed in _already_ via functools.partial
        :return: function representing the next task for this actor to execute
        '''
        # If we can get something from any available task queue, prioritise that work.
        for task_list in self.available_task_lists:
            if not task_list.empty():
                return task_list.get()

        # No work found in any relevant queue. Return an idle process.
        return self.idle

    @abstractmethod
    def perform(self):
        '''
        AU actors produce generators which yield tasks in the order the actor will execute them in.
        Intended for use with theatre_au as a timing model.
        :return: generator yielding tasks.
        '''

        while True:
            yield self.get_next_task()

    @property
    def available_task_lists(self):
        return [self.task_list] + list(map(lambda troupe: troupe.work_queue, self.troupes))


class BaseActor(AbstractActor):
    '''
    A concrete implementation of AbstractActor.
    Runs with the default implementations of its abstract methods.
    '''

    def get_next_task(self):
        return super(BaseActor, self).get_next_task()
        
    def perform(self):
        return super(BaseActor, self).perform()


class PatternMatchingActor(BaseActor):
    '''
    The concrete implementation of the AbstractActor (via BaseActor), but with pattern matching implemented.
    '''

    def __init__(self):
        super(PatternMatchingActor, self).__init__()
        self.message_patterns = {}

    def get_next_task(self):
        task = super(PatternMatchingActor, self).get_next_task()

        # Return whatever the task is mapped to in message mappings. If not mapping to anything, `get` defaults to task.
        return self.message_patterns.get(task, task)

    def register_message_to_task(self, message, task):
        self.message_patterns[message] = task


class Troupe(object):
    def __init__(self):
        self.troupe_work_queue = Queue()

    def add_member(self, actor):
        actor.troupes.append(self)

    def recieve_message(self, message):
        self.troupe_work_queue.put(message)
