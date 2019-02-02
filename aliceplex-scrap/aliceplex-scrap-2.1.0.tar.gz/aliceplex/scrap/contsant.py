from dataclasses import Field, fields
from typing import Any, Dict

from aliceplex.schema import Episode

from aliceplex.scrap.base import EpisodeScraper
from aliceplex.scrap.utils import default

__all__ = ["ConstantScraper"]


class ConstantScraper(EpisodeScraper):
    constant: Dict[str, Any]
    episode: Dict[int, Dict[str, Any]]

    def __init__(self, constant: Dict[str, Any] = None,
                 episode: Dict[int, Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.constant = default(constant, {})
        self.episode = default(episode, {})

    def scrap(self, episode_num: int, episode: Episode) -> Episode:
        for field in fields(Episode):  # type: Field
            try:
                setattr(episode,
                        field.name,
                        self.episode[episode_num][field.name])
            except KeyError:
                self._set_constant(episode, field)
        return episode

    def _set_constant(self, episode: Episode, field: Field):
        try:
            setattr(episode, field.name, self.constant[field.name])
        except KeyError:
            pass
