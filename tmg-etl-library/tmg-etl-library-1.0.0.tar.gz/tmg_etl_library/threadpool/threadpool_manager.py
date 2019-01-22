from concurrent.futures import ThreadPoolExecutor
import uuid


class ThreadpoolManager:
    # Function specific conditions for success - add option to pass parameters.
    def __init__(self, log, functions, pool_size=4, ensure_successful_execution=True):
        """

        :param log: Logger
        :param pool_size: Number of desired threads
        :param functions: Array of functions to run in parallel
        """
        self.logger = log
        self.id = uuid.uuid4()
        self.pool_size = pool_size
        self.functions = functions
        self.ensure_successful_execution = ensure_successful_execution

    def run(self):
        executors_list = []

        self.logger.info("Started parallel execution")
        with ThreadPoolExecutor(max_workers=self.pool_size) as executor:
            for function in self.functions:
                executors_list.append(executor.submit(function))

        results = []
        for x in executors_list:
            if x.exception():
                if self.ensure_successful_execution:
                    self.logger.error("Parallel execution of ThreadPoolManager with id {} failed due to Exception: {}"
                                      .format(self.id, x.exception()))
                    raise Exception("Parallel execution of ThreadPoolManager with id {} failed due to Exception: {}"
                                    .format(self.id, x.exception())
                                    )
                else:
                    self.logger.error(x.exception())
                    self.logger.error("An exception has been raised in one of the threads, the execution will continue")
                    continue
            results.append(x.result())
        self.logger.info("Parallel execution terminated")

        return results


