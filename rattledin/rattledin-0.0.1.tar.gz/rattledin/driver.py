from asyncio import get_event_loop
from functools import partial
from time import time

from linkedin_api import Linkedin

from aiohttp import ClientSession
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from .results import ResultManager, Result
from .errors import ExecutorError
from .commands.chat import ChatCommands


class LinkedinDriver:
    def __init__(self, logger, config, loop):
        self._logger = logger
        self._config = config
        self.loop = loop or get_event_loop()

        self._linkedin = None

        self._start_fut = None
        self._pool_executor = ThreadPoolExecutor(max_workers=1)
        self.result_manager = ResultManager()

        self._commands = {}

        self._pendant = []
        self._delayed_pendant = []

    @property
    def logger(self):
        return self._logger

    @property
    def config(self):
        return self._config

    @property
    def api(self):
        return self._linkedin

    async def _run_async(self, executor, method, *args, **kwargs):
        self.logger.info('[+] Running async method [{}] | [{}]'.format(method, kwargs))

        fn = self._commands[executor].commands[method]
        return await self.loop.run_in_executor(self._pool_executor, partial(fn, *args, **kwargs))

    def start_driver(self):
        self.logger.info('[+] Connecting into Linkedin account')

        try:
            self._linkedin = Linkedin(self.config['username'], self.config['password'])
            self.logger.info('[+] Success authenticating!')

            self.populate_commands()

        except Exception as ex:
            self.logger.error('[-] Error connecting into Linkedin\n{}'.format(ex))

    def populate_commands(self):
        self.logger.info('[+] Creating commands dictionary')

        self._commands['chats'] = ChatCommands()

    def execute_command(self, command, params=None, result_class=Result):
        self.logger.info('[+] Enqueueing command [{}] w/ params [{}]'.format(command, params))

        if params is None:
            params = {}

        result = self.result_manager.request_result(result_class)

        params['linkedin'] = self._linkedin
        params['exId'] = result.result_id

        self._pendant.append({
            'exId': result.result_id,
            'command': command,
            'params': params or {}
        })

        return result

    def verify_delayed_pendant(self):
        exclude_indexes = []

        for index in range(len(self._delayed_pendant)):
            job, delay_time = self._delayed_pendant[index]

            if delay_time <= time():
                self.logger.info('[+] Delayed job found [{}]'.format(job['command']))

                self._pendant.append(job)
                exclude_indexes.append(index)

        for index in exclude_indexes:
            self._delayed_pendant.pop(index)

    async def poll(self):
        pendants = self._pendant
        self._pendant = []
        results = []

        for job in pendants:
            executor = job['command'].split('|')[0]
            command = job['command'].split('|')[1]

            try:
                self.logger.info('[+] Polling command [{}] in executor [{}] | [{}]'
                                 .format(command, executor, job['params']))

                value = await self._run_async(executor, command, None, **job['params'])
                results.append(value)

                if 'keep_polling' in job['params'].keys() and job['params']['keep_polling']:
                    self.logger.info('[+] Keep polling job found')
                    self.logger.info('[+] Delaying command [{}] w/ params [{}]'.format(command, job['params']))
                    self._delayed_pendant.append((job, time() + job['params']['delay_sec']))

            except ExecutorError as ex:
                self.logger.error('[+] Error executing command\n{}'.format(ex))
                results.append(ex)

        try:
            for result in results:
                try:
                    if result['type'] == 'FINAL':
                        await self.result_manager.set_final_result(result['exId'], result['params'])
                    elif result['type'] == 'PARTIAL':
                        await self.result_manager.set_partial_result(result['exId'], result['params'])
                    elif result['type'] == 'ERROR':
                        await self.result_manager.set_error_result(result['exId'], result['params'])
                except Exception as ex:
                    self.logger.error('[-] Error getting results\n {}'.format(ex))

        except KeyError as ex:
            self.logger.error('[-] Error iterating over results\n{}'.format(ex))

    async def cancel_iterators(self):
        self.logger.info('[+] Canceling all iterators')

        for it in self.result_manager.get_iterators():
            await it.set_error_result({'name': 'StopIterator'})

    async def cancel_monitors(self):
        self.logger.info('[+] Canceling all monitors')

        for it in self.result_manager.get_monitors():
            await it.set_error_result({'name': 'StopIterator'})

    async def download_file(self, url):
        self.logger.info('[+] Downloading file from {}'.format(url))

        async with ClientSession() as session:
            async with session.get(url) as resp:
                return BytesIO(await resp.read())
