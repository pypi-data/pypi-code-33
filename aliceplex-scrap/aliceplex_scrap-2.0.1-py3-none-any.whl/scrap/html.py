from functools import lru_cache
from typing import Optional

from aliceplex.schema import Episode
from bs4 import BeautifulSoup

from aliceplex.scrap.base import EpisodeScraper
from aliceplex.scrap.utils import load_page

__all__ = ["HtmlScraper"]


class HtmlScraper(EpisodeScraper):
    def __init__(self, selenium: bool = False,
                 encoding: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.selenium = selenium
        self.encoding = encoding

    def scrap(self, episode_num: int, episode: Episode):
        soup = self.html(episode_num)
        self._episode(episode_num, episode, soup)

    @lru_cache(maxsize=None)
    def thumbnail(self, episode_num: int) -> Optional[str]:
        soup = self.html(episode_num)
        return self._thumbnail(episode_num, soup)

    @lru_cache(maxsize=None)
    def url(self, episode_num: int) -> str:
        raise NotImplementedError()

    @lru_cache(maxsize=None)
    def html(self, episode_num: int) -> BeautifulSoup:
        url = self.url(episode_num)
        return self._soup(url)

    def _soup(self, url: str) -> BeautifulSoup:
        html = load_page(url, self.selenium, self.encoding)
        return BeautifulSoup(html, "html5lib")

    def _thumbnail(self, episode_num: int,
                   soup: BeautifulSoup) -> Optional[str]:
        return None

    def _episode(self, episode_num: int,
                 episode: Episode,
                 soup: BeautifulSoup):
        raise NotImplementedError()
