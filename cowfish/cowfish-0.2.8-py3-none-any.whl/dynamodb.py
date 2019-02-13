import time
import logging
from .worker import BatchWorker
logger = logging.getLogger(__name__)


class DyanmodbWriter:
    def __init__(self, table, *, worker_params=None):
        self.table = table
        worker_params = worker_params or {}
        self.worker = BatchWorker(self.write_batch, **worker_params)

    def __repr__(self):
        return '<{}: table={}, worker={!r}>'.format(
                self.__class__.__name__, self.table, self.worker)

    async def stop(self):
        timestamp = time.time()
        await self.worker.stop()
        cost = time.time() - timestamp
        logger.info('{0!r} stopped in {1:.1f} seconds'.format(self, cost))

    async def write_one(self, Item):
        await self.worker.put(Item)

    async def write_batch(self, obj_list):
        async with self.table.batch_writer() as batch:
            for Item in obj_list:
                await batch.put_item(Item=Item)
