import asyncio
import requests
from functools import partial
from concurrent.futures import ThreadPoolExecutor


class ConcurrentRequests():
    """
    An object that makes it easy to queue and process requests that need to be executed concurrently.
    """
    def __init__(self, max_workers=None):
        # Get loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop = asyncio.get_event_loop()

        # Caps how many workers we can have
        # Defaults to the number of processors on the machine, multiplied by 5
        self.max_workers = max_workers

        # Unprocessed requests
        self.request_list = []

        # Processed requests
        self.processed_requests = []

    async def _run_requests(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                self.loop.run_in_executor(
                    executor,
                    partial(self._wrapped_request, *item['args'], **item['kwargs'])
                )
                for item in self.request_list
            ]

            for response in await asyncio.gather(*futures):
                self.processed_requests.append(response)

    @staticmethod
    def _wrapped_request(method, url, meta=None, **kwargs):
        out = {
            'response': requests.request(method, url, **kwargs),
            'meta': meta,
        }
        return out

    def add_request(self, method, url, meta=None, **kwargs):
        """
        Queue a request to be sent by requests.  Execute via `self.process()`
         - `method`: The method to be sent.
         - `url`: url that request is sent to.
         - `meta`: gets passed through to `processed_requests`.
         - `kwargs`: Identical to requests.
        """
        kwargs['meta'] = meta
        self.request_list.append({
            'args': [method, url],
            'kwargs': kwargs,
        })

    def get(self, url, meta=None, **kwargs):
        """
        Queue a get to be sent by requests.  Execute via `self.process()`
         - `url`: url that request is sent to.
         - `meta`: gets passed through to `processed_requests`.
         - `kwargs`: Identical to requests.
        """
        self.add_request('get', url, meta, **kwargs)

    def post(self, url, meta=None, **kwargs):
        """
        Queue a post to be sent by requests.  Execute via `self.process()`
         - `url`: url that request is sent to.
         - `meta`: gets passed through to `processed_requests`.
         - `kwargs`: Identical to requests.
        """
        self.add_request('post', url, meta, **kwargs)

    def put(self, url, meta=None, **kwargs):
        """
        Queue a put to be sent by requests.  Execute via `self.process()`
         - `url`: url that request is sent to.
         - `meta`: gets passed through to `processed_requests`.
         - `kwargs`: Identical to requests.
        """
        self.add_request('put', url, meta, **kwargs)

    def patch(self, url, meta=None, **kwargs):
        """
        Queue a patch to be sent by requests.  Execute via `self.process()`
         - `url`: url that request is sent to.
         - `meta`: gets passed through to `processed_requests`.
         - `kwargs`: Identical to requests.
        """
        self.add_request('patch', url, meta, **kwargs)

    def delete(self, url, meta=None, **kwargs):
        """
        Queue a delete to be sent by requests.  Execute via `self.process()`
         - `url`: url that request is sent to.
         - `meta`: gets passed through to `processed_requests`.
         - `kwargs`: Identical to requests.
        """
        self.add_request('delete', url, meta, **kwargs)

    def process(self):
        """
        Concurrently process all queued requests.  Results are appended to
        `self.processed_requests`
        """
        self.loop.run_until_complete(self._run_requests())
