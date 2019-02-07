from asyncio import Future, ensure_future, wait, sleep
from .managers import BaseManager
from .driver import LinkedinDriver

from .managers.chat import ChatManagerCollection

__version__ = '0.0.1'


class LinkedinCore(BaseManager):
    def __init__(self, config, logger, loop=None):
        super(LinkedinCore, self).__init__(LinkedinDriver(logger, config, loop), logger)

        self._submanagers['chats'] = ChatManagerCollection(self._driver, logger, manager='chats')

        self._logger = logger
        self._config = config

        self._fut_running = None
        self._fut_polling = None

    @property
    def loop(self):
        return self._driver.loop

    @property
    def logger(self):
        return self._logger

    @property
    def driver(self):
        return self._driver

    async def start(self, beat_ms=0.5):
        if self._fut_running:
            return

        self.logger.info('[+] Starting Linkedin Core')

        self._fut_running = Future()

        self._driver.start_driver()

        self._fut_polling = ensure_future(self._polling(beat_ms), loop=self.loop)

    async def stop(self):
        self.logger.info('[+] Stopping Linkedin')

        self._fut_running.set_result(None)
        await self.wait_until_stop()

    async def wait_until_stop(self):
        if self._fut_polling:
            await self._fut_polling

    async def _polling(self, beat_ms):
        try:
            self.logger.info('[+] Starting futures polling')

            while not self._fut_running.done():
                self._driver.verify_delayed_pendant()
                await self._driver.poll()
                await sleep(beat_ms)
        except Exception as ex:
            self.logger.info('[+] Finishing futures polling because of\n:{}'.format(ex))

            if not self._fut_running.done():
                self._fut_running.set_result(None)

            await wait([self._driver.cancel_iterators(),
                        self._driver.cancel_monitors()])
            self._driver.result_manager.cancel_all()

    async def cancel_iterators(self):
        return await self._driver.cancel_iterators()

    async def download_file(self, url):
        return await self._driver.download_file(url)
