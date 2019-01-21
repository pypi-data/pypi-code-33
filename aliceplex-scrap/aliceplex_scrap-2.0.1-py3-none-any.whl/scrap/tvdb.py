from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional

import requests
from aliceplex.schema import Episode

from aliceplex.scrap.base import EpisodeScraper
from aliceplex.scrap.utils import default

__all__ = ["TvDbScrapper", "TvDbCredential", "TvDbFields"]


@dataclass
class TvDbCredential:
    api_key: str
    user_key: str
    user_name: str

    def json(self) -> Dict[str, str]:
        return {
            "apikey": self.api_key,
            "userkey": self.user_key,
            "username": self.user_name
        }


class TvDbFields(Enum):
    Title = "title"
    Aired = "aired"
    Summary = "summary"
    Thumbnail = "thumbnail"


class TvDbScrapper(EpisodeScraper):
    def __init__(self, show_id: str,
                 credential: TvDbCredential,
                 usage: List[TvDbFields] = None,
                 language: str = "ja",
                 **kwargs):
        super().__init__(**kwargs)
        self.language = language
        self.credential = credential

        self.show_id = show_id
        # noinspection PyTypeChecker
        self.usage = default(usage, list(TvDbFields))

    @lru_cache(maxsize=None)
    def auth_token(self) -> str:
        url = "https://api.thetvdb.com/login"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.post(url,
                                 headers=headers,
                                 json=self.credential.json())
        return response.json()["token"]

    def auth_header(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token()}",
            "Accept-Language": self.language
        }

    def scrap(self, episode_num: int, episode: Episode):
        episode_json = self.episode(episode_num)
        if TvDbFields.Title in self.usage:
            episode.title = [episode_json["episodeName"]]
        if TvDbFields.Summary in self.usage:
            episode.summary = episode_json["overview"]
        if TvDbFields.Aired in self.usage:
            try:
                episode.aired = datetime.strptime(
                    episode_json["firstAired"],
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                self.logger.warning("Fail to parse date on episode")

    @lru_cache(maxsize=None)
    def thumbnail(self, episode_num: int) -> Optional[str]:
        episode_json = self.episode(episode_num)
        thumbnail = episode_json.get("filename")
        if thumbnail and TvDbFields.Thumbnail in self.usage:
            return f"https://www.thetvdb.com/banners/{thumbnail}"
        return None

    @lru_cache(maxsize=None)
    def episodes(self, page: int = 1):
        url = f"https://api.thetvdb.com/series/{self.show_id}/episodes"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token()}",
            "Accept-Language": self.language
        }
        params = {
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        content = response.json()
        episodes = content["data"]
        next_page = content["links"]["next"]
        if next_page is not None:
            episodes.extend(self.episodes(next_page))
        return episodes

    def season_num(self, episode_num: int) -> int:
        return 1

    def episode_num(self, episode_num: int) -> int:
        return episode_num

    @lru_cache(maxsize=None)
    def episode(self, episode_num: int) -> Dict[str, Any]:
        season_num = self.season_num(episode_num)
        episode_num = self.episode_num(episode_num)
        episodes = self.episodes()
        for episode in episodes:
            if (episode["airedSeason"] == season_num and
                    episode["airedEpisodeNumber"] == episode_num):
                episode_id = episode["id"]
                url = f"https://api.thetvdb.com/episodes/{episode_id}"
                response = requests.get(url, headers=self.auth_header())
                return response.json()["data"]
        raise RuntimeError(f"Cannot find episode {episode_num}")
