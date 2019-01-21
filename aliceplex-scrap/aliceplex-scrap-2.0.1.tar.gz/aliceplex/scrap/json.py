from functools import lru_cache
from json import loads
from typing import Any, Dict, List, Optional, Union

from aliceplex.schema import Episode

from aliceplex.scrap.base import EpisodeScraper
from aliceplex.scrap.utils import load_page

__all__ = ["JsonScraper"]
Json = Union[Dict[str, Any], List[Dict[str, Any]]]


class JsonScraper(EpisodeScraper):
    def __init__(self, selenium: bool = False,
                 encoding: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.selenium = selenium
        self.encoding = encoding

    def scrap(self, episode_num: int, episode: Episode):
        json = self.json(episode_num)
        self._episode(episode_num, episode, json)

    @lru_cache(maxsize=None)
    def thumbnail(self, episode_num: int) -> Optional[str]:
        json = self.json(episode_num)
        return self._thumbnail(episode_num, json)

    @lru_cache(maxsize=None)
    def url(self, episode_num: int) -> str:
        raise NotImplementedError()

    @lru_cache(maxsize=None)
    def json(self, episode_num: int) -> Json:
        url = self.url(episode_num)
        content = load_page(url, self.selenium, self.encoding)
        return loads(content)

    def _thumbnail(self, episode_num: int,
                   json: Json) -> Optional[str]:
        return None

    def _episode(self, episode_num: int,
                 episode: Episode,
                 json: Json):
        raise NotImplementedError()
