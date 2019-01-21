from abc import ABC, abstractmethod
from logging import Logger, getLogger
from typing import List, Optional

from aliceplex.schema import Episode

from aliceplex.scrap.utils import default


class EpisodeScraper(ABC):
    def __init__(self, logger: Logger = None):
        self.logger = default(logger, getLogger(__name__))

    @abstractmethod
    def scrap(self, episode_num: int, episode: Episode) -> Episode:
        raise NotImplementedError()

    def thumbnail(self, episode_num: int) -> Optional[str]:
        return None


class CombineEpisodeScraper(EpisodeScraper):
    def __init__(self, scrapers: List[EpisodeScraper] = None, **kwargs):
        super().__init__(**kwargs)
        self._scrapers: List[EpisodeScraper] = default(scrapers, [])

    def scrap(self, episode_num: int, episode: Episode = None) -> Episode:
        if episode is None:
            episode = Episode()
        for scraper in self._scrapers:
            scraper.scrap(episode_num, episode)
        return episode

    def thumbnail(self, episode_num: int) -> Optional[str]:
        thumbnail = None
        for scraper in self._scrapers:
            new_thumbnail = scraper.thumbnail(episode_num)
            if new_thumbnail is not None:
                thumbnail = new_thumbnail
        return thumbnail
