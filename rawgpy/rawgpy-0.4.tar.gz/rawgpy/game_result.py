from .charts import *
from .id_name_slug import *
from .platform_ import *
from .rating import *
from .store import *
import requests
import json as jsonopen


def del_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(del_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((del_none(k), del_none(v))
                         for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj


class GameResult():
    def __init__(self, json, user_agent):
        self.user_agent = user_agent
        json = del_none(json)
        print(type(json))
        [setattr(self, key, json[key])
            for key in json.keys()
            if not isinstance(json[key], (list, dict, tuple))
         ]
        self.alternative_names = [
            p for p in json.get("alternative_names", [])
        ]
        self.platforms = [
            SimplePlatform(
                p.get("platform", {}).get("id", ""),
                p.get("platform", {}).get("name", ""),
                p.get("platform", {}).get("slug", "")
            )
            for p in json.get("platforms", [])
        ]
        self.stores = [
            SimpleStore(
                p.get("platform", {}).get("id", ""),
                p.get("platform", {}).get("name", ""),
                p.get("platform", {}).get("slug", "")
            )
            for p in json.get("platforms", [])
        ]
        self.genres = [g for g in json.get("genres", "")]
        self.ratings = [
            Rating(
                r.get("id", ""),
                r.get("title", ""),
                r.get("count", ""),
                r.get("percent", "")
            )
            for r in json.get("ratings", [])
        ]
        self.parent_platforms = [
            SimplePlatform(
                p.get("platform", {}).get("id", ""),
                p.get("platform", {}).get("name", ""),
                p.get("platform", {}).get("slug", "")
            )
            for p in json.get("parent_platforms", [])
        ]

    def __getattr__(self, name):
        return ""

    def populate(self):
        headers = {
            'User-Agent': self.user_agent
        }
        response = requests.get(
            "https://api.rawg.io/api/games/{}".format(self.slug), headers=headers)
        print(response)
        json = jsonopen.loads(response.text)
        json = del_none(json)
        [setattr(self, key, json[key])
            for key in json.keys()
            if not isinstance(json[key], (list, dict, tuple))
         ]

        self.reactions = [
            {"id": r, "amount": num}
            for r, num in json.get("reactions", {}).items()
        ]
        self._genrechart = GenreChart(
            json.get("charts", {}).get("genre", {}).get("name", ""),
            json.get("charts", {}).get("genre", {}).get("position", ""),
            json.get("charts", {}).get("genre", {}).get("change", ""))
        self._yearchart = YearChart(
            json.get("charts", {}).get("year", {}).get("year", ""),
            json.get("charts", {}).get("year", {}).get("position", ""),
            json.get("charts", {}).get("year", {}).get("change", ""))
        self.charts = (
            self._genrechart,
            self._yearchart
        )

        self.requirements = [
            Platform(
                p.get("platform", {}).get("id", ""),
                p.get("platform", {}).get("name", ""),
                p.get("platform", {}).get("slug", ""),
                p.get("platform", {}).get("image", ""),
                p.get("platform", {}).get("year_end", ""),
                p.get("platform", {}).get("year_start", ""),
                p.get("platform", {}).get("games_count", ""),
                p.get("released_at", ""),
                p.get("requirements", {}).get("minimum", ""),
                p.get("requirements", {}).get("maximum", "")
            )
            for p in json.get("platforms", [])
        ]
        self.stores = [
            Store(
                s.get("id", ""),
                s.get("url", ""),
                s.get("store", {}).get("id", ""),
                s.get("store", {}).get("name", ""),
                s.get("store", {}).get("slug", ""),
                s.get("store", {}).get("domain", "")
            )
            for s in json.get("stores", [])
        ]
        self.developers = [
            Developer(
                d.get("id", ""),
                d.get("name", ""),
                d.get("slug", ""),
                d.get("games_count", "")
            )
            for d in json.get("developers", [])
        ]
        self.categoreis = [
            Category(
                d.get("id", ""),
                d.get("name", ""),
                d.get("slug", ""),
                d.get("games_count", "")
            )
            for d in json.get("categories", [])
        ]
        self.genres = [
            Genre(
                d.get("id", ""),
                d.get("name", ""),
                d.get("slug", ""),
                d.get("games_count", "")
            )
            for d in json.get("genres", [])
        ]
        self.tags = [
            Tag(
                d.get("id", ""),
                d.get("name", ""),
                d.get("slug", ""),
                d.get("games_count", "")
            )
            for d in json.get("tags", [])
        ]
        self.publishers = [
            Publisher(
                d.get("id", ""),
                d.get("name", ""),
                d.get("slug", ""),
                d.get("games_count", "")
            )
            for d in json.get("publishers", [])
        ]

        self.esrb = ESRB(
            json.get("esrb_rating", "").get("id", ""),
            json.get("esrb_rating", "").get("name", ""),
            json.get("esrb_rating", "").get("slug", "")
        )
