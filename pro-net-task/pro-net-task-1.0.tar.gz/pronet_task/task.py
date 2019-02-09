"""
A task is a meta object for tracking of long running algorithms.
It provides utilities to forward the state and updates of the
current algorithm progress.
"""

from enum import Enum


class State(Enum):
    """
    Possible states of a Task.
    """
    WAITING = 0
    RUNNING = 1
    DONE = 2
    ERROR = 3


class Task(object):
    """
    Meta data object for algorithm progress tracking.
    """

    def __init__(self, id, algorithm=None, input=None, state=State.WAITING):
        """
        Prepare a new task.

        :param id: Task id
        :type id: string or number
        :param algorithm: algorithm object
        :type algorithm: object which must support obj.execute(data, task)
        :param input: the input data of the algorithm
        :type input: input data as dict
        :param state: current task state
        :type state: State enum
        """
        self.__id = id
        self._algorithm = algorithm
        self._input = input
        self._state = state
        self._message = None
        self._progress = None
        self._steps = []
        self._result = None
        self._update_queue = None

    def id(self):
        """
        Returns the id of this task.
        """
        return self.__id

    def steps(self):
        """
        Retruns an list decribing the executed steps.
        The last step is the current executed step.
        """
        return self._steps

    def result(self):
        """
        The algorithm result or error message.

        This is None until the algorithm was successful of failed.
        """
        return self._result

    def state(self):
        """
        Get the current state of the algorithm as
        (<last log>, <progress>, <state>)
        """
        return (self._message, self._progress, self._state)

    def running(self):
        """
        Is the algorithm still running or waiting?
        """
        return self._state == State.WAITING\
            or self._state == State.RUNNING

    def run(self):
        """
        Run the task.

        Call this method to execute the algorithm.
        """
        self._state = State.RUNNING
        self._algorithm.execute(self._input, self)

    def update(self, message=None, progress=None, step=None):
        """
        Updates the current task state.

        Forwards the current state to the update queue if available.
        """
        if message:
            self._message = message
        if progress:
            self._progress = progress
        if step:
            if len(self._steps) == 0 or not self._steps[-1] == step:
                self._steps.append(step)
        if self._update_queue is not None:
            self._update_queue.put((self.__id, message, progress, step))

    def done(self, result=None):
        """
        Finish the task as success.

        Updates the task state as done and sets the result.
        """
        self._result = result
        self._state = State.DONE

    def error(self, message=None):
        """
        Finish the task as failed.

        Updates the task state as failed and sets the error message
        as result.
        """
        self._result = message
        self._state = State.ERROR

    def set_update_queue(self, queue):
        """
        Inject the update queue.

        If the tasks is used with multi processing the queue has to set to
        None before giving the task back to the calling process.
        """
        self._update_queue = queue
