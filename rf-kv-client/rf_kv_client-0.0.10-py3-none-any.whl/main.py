import sys
import traceback
import aiohttp
import asyncio
import dateutil.parser
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Optional, Callable

from acapelladb import Session


class BatchException(Exception):
    pass


class BatchDoesNotExist(BatchException):
    pass


class BatchSendError(BatchException):
    pass


class Batch:
    def __init__(self, session: Session):
        self.__session = session
        self.__batch = session.batch_manual()
        self.__cas_keys = []

    def send_sync(self):
        async def send(batch):
            await batch.send()

        for entry in self.__cas_keys:
            self.cas_sync(**entry)

        asyncio.get_event_loop().run_until_complete(send(self.__batch))

    async def send(self):
        for entry in self.__cas_keys:
            await self.cas(**entry)

        await self.__batch.send()

    def set(self, partition_key: List[str], new_value: object, clustering_key: Optional[List[str]]=None):
        entry = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(KVClient.get_entry(self.__session, partition_key, clustering_key))
        )[0]

        entry.set(new_value=new_value, batch=self.__batch)

        return self

    def cas_sync(self, partition_key: List[str], new_value: object, clustering_key: Optional[List[str]]=None):
        entry = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(KVClient.get_entry(self.__session, partition_key, clustering_key))
        )[0]

        entry.cas(new_value=new_value, batch=self.__batch)

        return self

    async def cas(self, partition_key: List[str], new_value: object, clustering_key: Optional[List[str]]=None):
        entry = await KVClient.get_entry(self.__session, partition_key, clustering_key)

        # noinspection PyAsyncCall
        entry.cas(new_value=new_value, batch=self.__batch)

        return self

    def add_to_cas_keys(self, partition_key: List[str], new_value: object, clustering_key: Optional[List[str]]=None):
        entry = None
        for e in self.__cas_keys:
            if e['partition_key'] == partition_key and e['clustering_key'] == clustering_key:
                entry = e
                break

        if not entry:
            entry = {
                'partition_key': partition_key,
                'clustering_key': clustering_key
            }
            self.__cas_keys += [entry]

        entry['new_value'] = new_value


batches = {}
batch_id = 0


class KVClient:
    def __init__(self, session: Session, logger: object):
        self._batch = None
        self._session = session
        self.logger = logger

    @staticmethod
    def session(host, port) -> Session:
        return Session(
            host=host,
            port=port,
            api_prefix=''  # empty for rf version of kv
        )

    @staticmethod
    async def get_entry(session: Session, partition_key: List[str], clustering_key: Optional[List[str]]):
        return await session.get_entry(
            partition=partition_key,
            clustering=clustering_key
        )

    @staticmethod
    def make_batch(session: Session) -> int:
        global batch_id
        global batches

        _batch_id = batch_id
        batches[_batch_id] = Batch(session)
        batch_id += 1
        return _batch_id

    @staticmethod
    def get_batch(b_id: int) -> Batch:
        global batches
        try:
            return batches[b_id]
        except KeyError:
            raise BatchDoesNotExist()

    @staticmethod
    def remove_batch(b_id: int):
        global batches
        try:
            del batches[b_id]
        except KeyError:
            raise BatchDoesNotExist()

    @staticmethod
    def execute_batch(b_id: int):
        global batches

        if b_id not in batches:
            return

        batch = batches[b_id]

        try:
            batch.send_sync()
        except Exception:
            raise BatchSendError()
        finally:
            del batches[b_id]

    @contextmanager
    def batch(self):
        try:
            self._batch = Batch(self._session)
            yield self._batch
            self._batch.send_sync()
        except Exception as e:
            if self.logger:
                self.logger.error(e)
            raise BatchSendError()
        finally:
            pending = asyncio.Task.all_tasks()
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*pending))

    async def __aenter__(self):
        self._batch = Batch(self._session)
        return self._batch

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._batch.send()
        except Exception as e:
            if self.logger:
                self.logger.error(e)

    @staticmethod
    async def listen(session: Session, partition_key: List[str], clustering_key: Optional[List[str]],
                     action: Callable, timeout: Optional[int]=3, logger: Optional[object]=None, backoff: int=2):
        async def listen_for(entry, action):
            can_call_action = False
            backoff_timeout = 1

            while True:
                try:
                    if can_call_action:
                        can_call_action = False

                        if asyncio.iscoroutinefunction(action):
                            await action(entry.value, entry.partition, entry.clustering)
                        else:
                            action(entry.value, entry.partition, entry.clustering)

                    await entry.listen(timeout=timedelta(seconds=timeout))

                except TimeoutError:
                    if logger:
                        logger.warn(f'partition {entry.partition} | clustering {entry.clustering}: timeout')
                    await asyncio.sleep(1)
                except (aiohttp.client_exceptions.ClientResponseError,
                        aiohttp.client_exceptions.ClientOSError,
                        aiohttp.client_exceptions.ServerDisconnectedError,
                        aiohttp.client_exceptions.ServerTimeoutError,
                        asyncio.TimeoutError) as e:
                    try:
                        code = e.code
                    except AttributeError:
                        code = ''

                    if logger:
                        logger.warn(f'{e.__class__.__name__}: {code}')

                    await asyncio.sleep(backoff_timeout)
                    backoff_timeout *= backoff
                except Exception as e:
                    if logger:
                        lines = []
                        for line in traceback.format_exception(*sys.exc_info()):
                            lines.append(line)

                        logger.error(e, exc_info=True)
                    break
                else:
                    backoff_timeout = 1
                    can_call_action = True

        if not action:
            if logger:
                logger.error('no action, listen is pointless')
            return

        try:
            entry = await KVClient.get_entry(
                session,
                partition_key if type(partition_key) == list else partition_key.split(':'),
                clustering_key if type(clustering_key) == list else clustering_key.split(':') if clustering_key else None
            )

            # noinspection PyAsyncCall
            asyncio.ensure_future(listen_for(entry, action))

        except Exception as e:
            if logger:
                logger.error('partition {} | clustering {}: {}'.format(partition_key, clustering_key, str(e)))

    @staticmethod
    def timestamp(time: Optional[str]=None):
        return str(int((dateutil.parser.parse(time) if time else datetime.now()).timestamp() * 1000))

    @staticmethod
    def to_kv_timestamp(timestamp: Optional[str] = None):
        return str(int((dateutil.parser.parse(timestamp) if timestamp else datetime.now()).timestamp() * 1000))

    @staticmethod
    def from_kv_timestamp(timestamp: Optional[str] = None):
        return datetime.fromtimestamp(int(timestamp) / 1000) if timestamp else datetime.now()
