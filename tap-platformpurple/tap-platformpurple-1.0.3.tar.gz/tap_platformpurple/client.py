import time
import requests
import singer

from tap_framework.client import BaseClient


LOGGER = singer.get_logger()


class PlatformPurpleClient(BaseClient):

    def __init__(self, config):
        super().__init__(config)

        self.user_agent = self.config.get('user_agent')

    def get_headers(self):
        headers = {
            'API-Key': self.config.get('api_key'),
        }

        if self.config.get('user_agent'):
            headers['User-Agent'] = self.config.get('user_agent')

        return headers

    def make_request(self, url, method, base_backoff=15,
                     body=None):
        LOGGER.info("Making {} request to {}".format(method, url))

        response = requests.request(
            method,
            url,
            headers=self.get_headers(),
            json=body)

        if response.status_code == 429:
            if base_backoff > 120:
                raise RuntimeError('Backed off too many times, exiting!')

            LOGGER.warn('Got a 429, sleeping for {} seconds and trying again'
                        .format(base_backoff))

            time.sleep(base_backoff)

            return self.make_request(url, method, base_backoff * 2, body)

        if response.status_code != 200:
            raise RuntimeError(response.text)

        return response.json()
