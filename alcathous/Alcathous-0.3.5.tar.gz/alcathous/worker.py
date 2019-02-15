import threading
import queue
from pelops import mylogger


class Worker:
    """
    Creates n worker threads that wait for functions to be executed. Thus, a simple way of parallelizing
    processing of many different tasks. A single queue is filled and the worker threads take the oldest
    entry and executes them.
    """

    _list = None  # list containing the worker thread references.
    queue = None  # queue of to be processed tasks
    _number = None  # number of worker threads that should be created.
    _logger = None  # logger instance

    def __init__(self, number_worker, parent_logger):
        """
        Constructor.

        :param number_worker: number of worker threads that should be created.
        :param parent_logger: logger instance from the parent. a child will be spawned
        """

        self._logger = mylogger.get_child(parent_logger, self.__class__.__name__)
        self._logger.info("Worker.__init__ - initializing")
        self._logger.debug("Worker.__init__ - config: number_worker={}.".format(number_worker))
        self.queue = queue.Queue()
        self._list = []
        self._number = int(number_worker)

    def _worker_thread(self):
        self._logger.info("Worker._worker_thread - started worker")
        while True:
            item = self.queue.get()
            self._logger.info("Worker._worker_thread - worker received item '{}'.".format(item))
            if item is None:
                self._logger.info("Worker._worker_thread - worker received stop signal")
                break
            func, parameter = item
            func(parameter)
            self.queue.task_done()
        self._logger.info("Worker._worker_thread - stopped worker")

    def start(self):
        """
        Starts all worker threads.
        """

        self._logger.info("Worker.start - starting {} worker.".format(self._number))
        for i in range(self._number):
            w = threading.Thread(target=self._worker_thread)
            w.start()
            self._list.append(w)
        self._logger.info("Worker.start - {} worker started.".format(len(self._list)))

    def stop(self):
        """
        Stops all worker threads.
        """

        self._logger.info("Worker.stop - stopping {} worker.".format(len(self._list)))
        for i in range(len(self._list)):
            self.queue.put(None)
        for t in self._list:
            t.join()
        self._list = []
        self._logger.info("Worker.stop - worker stopped.")
