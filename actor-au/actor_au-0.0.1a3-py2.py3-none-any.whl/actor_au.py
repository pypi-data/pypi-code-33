from abc import ABCMeta, abstractmethod
from queue import Queue


class Actor(metaclass=ABCMeta):

    def __init__(self):
        self.task_list = Queue()
        self.idle = lambda: None
        self.troupes = []

    def schedule_task(self, task):
        self.task_list.put(task)

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
        for task in self.available_task_lists:
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


class Troupe(object):
    def __init__(self):
        self.troupe_work_queue = Queue()

    def add_member(self, actor):
        actor.troupes.append(self)

    def recieve_message(self, message):
        self.troupe_work_queue.put(message)


class PatternMatchingActor(metaclass=Actor):
    def __init__(self):
        Actor.__init__(self)
        self.message_mappings = {}

    @abstractmethod
    def __init__

    @abstractmethod
    def get_next_task(self):
        for task_list in self.available_task_lists:
            if not task_list.empty():
                task = task_list.get()
                if task in self.message_mappings.keys():
                    return self.message_mappings[task]
                else:
                    return task

        return self.idle