from lbCVMFSTools.Injector import inject, injector
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface
from contextlib import contextmanager
import logging
from lbCVMFSTools import Audit
import time
from multiprocessing import Process, Queue
import errno


@inject(taskHandler=TaskHandlerInterface,
        transactionHandler=TransactionHandlerInterface)
class Scheduler():
    def __init__(self, taskHandler=None, transactionHandler=None):
        self.taskHandler = taskHandler
        self.transactionHandler = transactionHandler
        self.stop_timeout = False
        if hasattr(self.taskHandler, 'no_auto_start'):
            if self.taskHandler.no_auto_start:
                return
        self.start()

    def _execute(self, task, queue):
        try:
            self.taskHandler.perform_task(task)
        except Exception as e:
            queue.put(e)

    def start(self):
        if not self.taskHandler.should_run():
            return
        tasks = self.taskHandler.get_list_of_tasks()
        self.taskHandler.preTransaction()
        all_ok = True
        for task in tasks:
            current_task_id = self.taskHandler.__class__.__name__
            Audit.write(Audit.COMMAND_START, command=current_task_id)
            logging.info("Starting executing: %s" % str(task))
            error = self.execute(task=task)
            if error:
                all_ok = False
                logging.info("Fail executing: %s" % str(task))
                logging.error(error)
            else:
                logging.info("Successfully executed: %s" % str(task))
            Audit.write(Audit.COMMAND_END)
        if all_ok:
            self.taskHandler.update_last_run()
        self.taskHandler.postTransaction()

    def execute(self, task):
        try:
            with self.transaction():
                if self.taskHandler.timeout:
                    counter = 0
                    proc_done = False
                    error_queue = Queue()
                    executor = Process(target=self._execute,
                                       args=(task, error_queue))
                    executor.start()
                    while counter < self.taskHandler.timeout:
                        proc_done = not executor.is_alive()
                        if proc_done:
                            break
                        time.sleep(1)
                        counter += 1
                    if not proc_done:
                        logging.error("Terminating process due to timeout")
                        executor.terminate()
                        raise OSError(errno.ETIMEDOUT)
                    if not error_queue.empty():
                        raise error_queue.get()
                else:
                    self.taskHandler.perform_task(task)
            return None
        except UserWarning as e:
            return None
        except Exception as e:
            return e

    @contextmanager
    def transaction(self):
        logging.info("Starting transaction")
        self.transactionHandler.transactionStart()
        try:
            yield
            logging.info("Sending transaction")
            Audit.write(Audit.TRANSACTION_START)
            self.transactionHandler.transactionPublish()
            Audit.write(Audit.TRANSACTION_END)
        except Exception as e:
            logging.info("Aborting transaction")
            logging.error(e)
            self.transactionHandler.transactionAbort()
            raise e
