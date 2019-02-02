"""Map functionality for aiohttp requests."""

import asyncio
import logging

import aiohttp

logger = logging.getLogger(__name__)


class AiohttpMap:
    """
    Asynchronously handle bulk HTTP requests.

    Args:
        kwargs: Any aiohttp.ClientSession optional keyword argument.

    """

    def __init__(self, **kwargs):
        self._session_parameters = kwargs
        self._success_queue = None
        self._error_queue = None

    def map(self, urls, request_type='get', **kwargs):
        """
        Performs the given request type on urls.

        Args:
            urls (list of str): List of urls.
            request_type (str, optional): The type of request being made. This is any
                available request type defined in aiohttp. Defaults to 'get'.
            **kwargs: Any optional keyword arguments for the given request type.

        Returns:
            tuple: Succeeded requests and failed requests.

        """

        # Create the queues.
        self._success_queue = asyncio.Queue()
        self._error_queue = asyncio.Queue()

        loop = asyncio.get_event_loop()
        future = self._map(urls, request_type, **kwargs)
        loop.run_until_complete(future)

        succeeded = self._get_all_items(self._success_queue)
        failed = self._get_all_items(self._error_queue)

        return succeeded, failed

    @staticmethod
    def _get_all_items(queue):
        """
        Gets all items off a queue.

        Args:
            queue (asyncio.Queue): Queue to get items from.

        Returns:
            list: Items from the queue.

        """
        items = []
        while True:
            try:
                items.append(queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return items

    async def _map(self, urls, request_type, **kwargs):
        """
        Asynchronous alias for map.

        Gathers all the tasks.

        """
        futures = []
        async with aiohttp.ClientSession(**self._session_parameters) as session:
            for url in urls:
                future = asyncio.ensure_future(
                    self._handle_request(url, request_type, session, **kwargs))
                futures.append(future)
            _ = await asyncio.gather(*futures)

    async def _handle_request(self, url, request_type, session, **kwargs):
        """
        Handles an individual request.

        Args:
            url (str): Request URL.
            request_type (str): Any aiohttp request type. E.g. 'get'.
            session (aiohttp.ClientSession): ClientSession instance.

        Returns:

        """

        logger.info('Handling request: url=%s, request_type=%s, kwargs=%s',
                    url, request_type, kwargs)
        func = getattr(session, request_type)
        async with func(url, **kwargs) as response:
            try:
                response.raise_for_status()
                await response.read()
            except aiohttp.ClientError:
                logger.exception('Failed to handle request: url=%s', url)
                await self._error_queue.put(response)
            await self._success_queue.put(response)
        logger.info('Completed request: url=%s', url)
