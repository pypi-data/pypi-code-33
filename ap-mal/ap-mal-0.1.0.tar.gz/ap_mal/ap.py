import logging
import re

import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

try:
    import browsercookie
except ImportError:
    from . import browsercookie
from .base import Service


class AnimePlanet(Service):
    EXPORT_URL = 'https://www.anime-planet.com/api/export'
    LIST_TYPES = ['anime', 'manga']
    ALIAS = 'anime-planet'

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.cookies = RequestsCookieJar()
        self.update_cookies()
        self.uid = self._get_export_uid()

    def update_cookies(self):
        chrome_cookies = browsercookie.chrome()
        self.cookies.update(chrome_cookies)

    def import_list(self, list_type: str, data: dict):
        pass

    def export_list(self, list_type: str) -> dict:
        self.log.info(f"Exporting {list_type} from {self.__class__.__name__}")
        response = self._get(f'{self.EXPORT_URL}/{list_type}/{self.uid}')
        if response:
            return response.json()
        else:
            self.log.error(f"Could not get the {list_type} list")
            return {}

    def _get_export_uid(self) -> str:
        page = self._get('https://www.anime-planet.com/users/export_list.php')
        if page:
            return self._parse_export_page_uid(page.text)
        else:
            self.log.error(f"Couldn't get the export page")
            return ''

    @staticmethod
    def _parse_export_page_uid(text: str) -> str:
        soup = BeautifulSoup(text, 'html.parser')
        tag = soup.find('form', action=re.compile('/api/export/anime'))
        uid = tag['action'].rpartition('/')[2]
        return uid

    def _get(self, url: str) -> requests.Response:
        response = requests.get(url, cookies=self.cookies)
        if response.status_code != 200:
            self.log.error(f"Failed to get URL '{url}': status "
                           f"code {response.status_code}")
            return None
        return response
