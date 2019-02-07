import importlib
from fetcher import Session


class Pyrlamento:
    def __init__(self, country_package):
        self.country = importlib.import_module(country_package)
        self.session = Session()
        self.reader = self.country.Reader(self.session)

    def publications(self, start_date, end_date):
        return self.reader.get_publications(start_date, end_date)

    def publication(self, identifier):
        return self.reader.get_publication(identifier)

    def diploma(self, identifier):
        return self.reader.get_diploma(identifier)
