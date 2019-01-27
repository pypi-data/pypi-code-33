import abc
from typing import List

from puradouga.core import PluginBase
from puradouga.plugins import data as d
from puradouga.plugins.data import TorrentResponse


class FilenameParser(PluginBase):
    def filename_parser(self, parent: d.FilenameParsed, filename: str) -> d.FilenameParsed:
        pass


class TvMetaProvider(PluginBase):
    def series_from_filename(self, filename_parsed: d.FilenameParsed) -> d.SeriesResponse:
        pass

    def season_from_filename(self, filename_parsed: d.FilenameParsed, series: d.SeriesResponse) -> d.SeasonResponse:
        pass

    def episode_from_filename(self, filename_parsed: d.FilenameParsed, season: d.SeasonResponse) -> d.EpisodeResponse:
        pass

    def series_from_id(self, identifier: str) -> d.SeriesResponse:
        pass

    def season_from_id(self, identifier: str) -> d.SeasonResponse:
        pass

    def episode_from_id(self, identifier: str) -> d.EpisodeResponse:
        pass

    def series_from_title(self, title: str) -> d.SeriesResponse:
        pass


class TorrentFinder(PluginBase):
    @abc.abstractmethod
    def is_searchable(self):
        pass

    @abc.abstractmethod
    def find_torrent(self, name: str, tags: List[str]) -> List[TorrentResponse]:
        pass

    @abc.abstractmethod
    def update_local_storage(self) -> List[TorrentResponse]:
        pass
