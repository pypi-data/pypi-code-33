from .base import Service


class MyAnimeList(Service):
    ALIAS = 'myanimelist'

    def export_list(self, list_type: str) -> dict:
        pass

    def import_list(self, list_type: str, data: dict):
        pass
