import csv
import pandas
from abc import ABC, abstractmethod

from sdhpy.sdhstore.ckanhelper import serve_resource


class Dataset(ABC):
    def __init__(self, api_key, resource_id, **kwargs):
        self._data = None
        self._resource_id = resource_id
        self._api_key = api_key

    @property
    def data(self):
        if not self._data:
            self._data = self.get_data_from_source()
        return self._data
    @data.setter
    def data(self, value):
        self._data = value


    @property
    def resource_id(self):
        return self._resource_id

    @property
    def api_key(self):
        return self._api_key

    @abstractmethod
    def get_data_from_source(self):
        pass


class PandasDataset(Dataset):
    def get_data_from_source(self):
        serving_response = serve_resource(self.api_key, self.resource_id, "http", "csv_headers")
        url = str(serving_response["connectionInfo"]["url"])
        return pandas.read_csv(url, header=0, sep=",",
                                    quoting=csv.QUOTE_ALL, quotechar="\"", escapechar="\\",
                                    doublequote=False, error_bad_lines=False, warn_bad_lines=True)
