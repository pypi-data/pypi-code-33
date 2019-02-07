import datetime
from fetcher import Session


class Diploma:
    def __init__(self, identifier):
        self.id = identifier

    @property
    def name(self) -> str:
        raise NotImplemented()

    @property
    def date(self) -> datetime.date:
        raise NotImplemented()

    def __str__(self):
        return self.name


class Publication:
    def __init__(self, identifier):
        self.id = identifier

    @property
    def name(self) -> str:
        raise NotImplemented()

    @property
    def date(self) -> datetime.date:
        raise NotImplemented()

    @property
    def diplomas(self) -> [Diploma]:
        raise NotImplemented()

    def __str__(self):
        return self.name


class Reader:
    def __init__(self):
        self.session = Session()

    def get_publications(self, date_start: datetime.date, date_end: datetime.date) -> [Publication]:
        raise NotImplemented()

    def get_publication(self, identifier) -> Publication:
        raise NotImplemented()

    def get_diploma(self, identifier) -> Diploma:
        raise NotImplemented()
