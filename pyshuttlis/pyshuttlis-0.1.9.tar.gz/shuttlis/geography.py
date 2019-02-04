from dataclasses import dataclass
from typing import List
from shapely.geometry import Point, LineString


@dataclass
class Location:
    def __init__(self, lat: float, lng: float):
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180
        self.lat = lat
        self.lng = lng

    def __eq__(self, o: object) -> bool:
        return (self.lat, self.lng) == (o.lat, o.lng)

    def __hash__(self) -> int:
        return hash((self.lat, self.lng))

    def as_point(self):
        return Point(self.lng, self.lat)


@dataclass
class Path:
    def __init__(self, locations: List[Location]):
        assert len(locations) > 2
        points = [location.as_point() for location in locations]
        self._path = LineString([[p.x, p.y] for p in points])

    def as_list(self):
        return [Location(lat=y, lng=x) for x, y in self._path.coords]
