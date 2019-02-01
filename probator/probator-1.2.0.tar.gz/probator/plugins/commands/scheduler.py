import threading
import time
from abc import ABC

from flask_script import Option

from probator import PROBATOR_PLUGINS
from probator.config import dbconfig
from probator.plugins.commands import BaseCommand


class BaseSchedulerCommand(BaseCommand, ABC):
    ns = None
    option_list = [
        Option('--scheduler', dest='scheduler', metavar='name', type=str, help='Overrides the scheduler configured in the UI'),
        Option('--list-schedulers', dest='list_schedulers', action='store_true', default=False, help='List the available schedulers'),
    ]

    def __init__(self):
        super().__init__()
        self.scheduler_plugins = {}
        self.active_scheduler = dbconfig.get('scheduler')

    def load_scheduler_plugins(self):
        """Refresh the list of available schedulers

        Returns:
            `list` of :obj:`BaseScheduler`
        """
        if not self.scheduler_plugins:
            for entry_point in PROBATOR_PLUGINS['probator.plugins.schedulers']['plugins']:
                cls = entry_point.load()
                self.scheduler_plugins[cls.__name__] = cls
                if cls.__name__ == self.active_scheduler:
                    self.log.debug(f'Scheduler loaded: {cls.__name__} in module {cls.__module__}')
                else:
                    self.log.debug(f'Scheduler disabled: {cls.__name__} in module {cls.__module__}')

    def run(self, *, scheduler, list_schedulers, **kwargs):
        self.load_scheduler_plugins()

        if scheduler:
            self.active_scheduler = scheduler

        if self.active_scheduler not in self.scheduler_plugins:
            self.log.error(f'Unable to locate the {self.active_scheduler} scheduler plugin')
            return False

        return True


class Scheduler(BaseSchedulerCommand):
    """Execute the selected scheduler"""
    name = 'Scheduler'

    def run(self, *, list_schedulers, **kwargs):
        """Execute the scheduler.

        Returns:
            `None`
        """
        if not super().run(list_schedulers=list_schedulers, **kwargs):
            return

        if list_schedulers:
            self.log.info('--- List of Scheduler Modules ---')
            for name, scheduler in list(self.scheduler_plugins.items()):
                if self.active_scheduler == name:
                    self.log.info(f'{name} (active)')

                else:
                    self.log.info(name)
            self.log.info('--- End list of Scheduler Modules ---')
            return

        scheduler = self.scheduler_plugins[self.active_scheduler]()
        scheduler.execute_scheduler()


class Worker(BaseSchedulerCommand):
    """Execute the selected worker"""
    name = 'Worker'
    option_list = BaseSchedulerCommand.option_list + [
        Option(
            '--no-daemon',
            default=False,
            action='store_true',
            help='Do not execute in daemon mode (if supported). Execution stops as soon as the worker returns'
        ),
        Option(
            '--delay',
            default=10,
            type=int,
            help='Delay between executions in daemon mode, in seconds. Default: 10'
        ),
        Option(
            '--threads',
            default=5,
            type=int,
            help='Number of worker threads to spawn. --no-daemon only uses a single thread. Default: 5'
        ),
    ]

    def run(self, no_daemon, delay, threads, **kwargs):
        """Execute the worker thread.

        Returns:
            `None`
        """
        super().run(**kwargs)
        scheduler = self.scheduler_plugins[self.active_scheduler]()

        if not no_daemon:
            self.log.info(f'Starting {scheduler.name} worker with {threads} threads checking for new messages every {delay} seconds')

            for i in range(threads):
                thd = threading.Thread(
                    target=self.execute_worker_thread,
                    args=(scheduler.execute_worker, delay)
                )
                thd.start()
        else:
            self.log.info('Starting {scheduler.name} worker for a single non-daemon execution')
            scheduler.execute_worker()

    @staticmethod
    def execute_worker_thread(func, delay):
        while True:
            func()
            time.sleep(delay)
