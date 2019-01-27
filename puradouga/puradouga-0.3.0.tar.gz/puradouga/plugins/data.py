import inspect
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


class BaseData:
    __meta_data__: dict = None

    def __init__(self):
        self.__meta_data__ = dict()

    def get_meta_field(self, name, plugin_name=None, default=None):
        if not self.__meta_data__:
            self.__meta_data__ = {}

        if not plugin_name:
            caller_frame = inspect.getouterframes(inspect.currentframe(), 2)
            plugin_name = caller_frame[1].frame.f_locals["self"].__class__.__name__
        return self.__meta_data__.get(plugin_name, {}).get(name, default)

    def set_meta_field(self, name, value, plugin_name=None):
        if not self.__meta_data__:
            self.__meta_data__ = {}

        if not plugin_name:
            caller_frame = inspect.getouterframes(inspect.currentframe(), 2)
            plugin_name = caller_frame[1].frame.f_locals["self"].__class__.__name__

        self.__meta_data__.setdefault(plugin_name, {})[name] = value


@dataclass
class FilenameParsed:
    title: str = None
    season: str = None
    episode: str = None
    source: str = None


@dataclass
class Title:
    english: str = None
    romaji: str = None
    native: str = None


@dataclass
class Image:
    title: str = None
    description: str = None
    file: str = None
    type: str = None


@dataclass
class SeriesResponse(BaseData):
    title: Title = None
    description: str = None
    images: List[Image] = field(default_factory=list)
    start_date: datetime = None
    end_date: datetime = None
    nsfw: bool = None
    homepage: str = None
    genres: List[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.get_meta_field("id")

    @id.setter
    def id(self, value: str):
        self.set_meta_field("id", value)


@dataclass
class SeasonResponse(BaseData):
    series: SeriesResponse = None
    season: int = None
    air_date: datetime = None
    name: str = None
    description: str = None
    images: List[Image] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.get_meta_field("id")

    @id.setter
    def id(self, value: str):
        self.set_meta_field("id", value)


@dataclass
class EpisodeResponse(BaseData):
    season: SeasonResponse = None
    title: Title = None
    episode: int = None
    description: str = None
    images: List[Image] = field(default_factory=list)
    air_date: datetime = None
    length: float = None

    @property
    def id(self) -> str:
        return self.get_meta_field("id")

    @id.setter
    def id(self, value: str):
        self.set_meta_field("id", value)


@dataclass
class TorrentResponse(BaseData):
    link: str = None
    tags: List[str] = field(default_factory=list)
