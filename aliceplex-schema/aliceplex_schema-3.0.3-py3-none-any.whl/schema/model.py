from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

__all__ = ["Actor", "Show", "Episode", "Movie", "Album", "Artist", "Person"]


@dataclass
class Person:
    """
    Represent a person.
    """
    name: Optional[str] = None
    photo: Optional[str] = None


@dataclass
class Actor(Person):
    """
    Represent an actor.
    """
    name: Optional[str] = None
    role: Optional[str] = None
    photo: Optional[str] = None


@dataclass
class Show:
    """
    Represent a show.
    """
    title: Optional[str] = None
    sort_title: Optional[str] = None
    original_title: Optional[str] = None
    content_rating: Optional[str] = None
    tagline: List[str] = field(default_factory=list)
    studio: List[str] = field(default_factory=list)
    aired: Optional[date] = None
    summary: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    actors: List[Actor] = field(default_factory=list)
    season_summary: Dict[int, str] = field(default_factory=dict)


@dataclass
class Episode:
    """
    Represent an episode.
    """
    title: List[str] = field(default_factory=list)
    aired: Optional[date] = None
    content_rating: Optional[str] = None
    summary: Optional[str] = None
    directors: List[Person] = field(default_factory=list)
    writers: List[Person] = field(default_factory=list)
    rating: Optional[float] = None


@dataclass
class Movie:
    """
    Represent an movie.
    """
    title: Optional[str] = None
    sort_title: Optional[str] = None
    original_title: Optional[str] = None
    content_rating: Optional[str] = None
    tagline: List[str] = field(default_factory=list)
    studio: List[str] = field(default_factory=list)
    aired: Optional[date] = None
    summary: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = field(default_factory=list)
    collections: List[str] = field(default_factory=list)
    actors: List[Actor] = field(default_factory=list)
    writers: List[Person] = field(default_factory=list)
    directors: List[Person] = field(default_factory=list)


@dataclass
class Artist:
    """
    Represent an artist of an album.
    """
    collections: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    similar: List[str] = field(default_factory=list)


@dataclass
class Album:
    """
    Represent an album.
    """
    aired: Optional[date] = None
    collections: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    summary: Optional[str] = None
