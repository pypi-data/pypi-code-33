import csv
import pandas
from abc import ABC, abstractmethod
from sdhpy.sdhtoolkit.serving import serve


class Dataset(ABC):
    def __init__(self, tokens, dataset, resource_id, **kwargs):
        self._data = None
        self._dataset = dataset
        self._resource_id = resource_id
        self._tokens = tokens

    @property
    def data(self):
        if not self._data:
            self._data = self.get_data_from_source()
        return self._data
    @data.setter
    def data(self, value):
        self._data = value

    @property
    def dataset(self):
        return self._dataset

    @property
    def resource_id(self):
        return self._resource_id

    @property
    def tokens(self):
        return self._tokens

    @abstractmethod
    def get_data_from_source(self):
        pass


class PandasDataset(Dataset):
    def get_data_from_source(self):
        serving_response = serve(self.tokens, self.dataset, self.resource_id, "http", "csv_headers")
        url = str(serving_response["connectionInfo"]["url"])
        return pandas.read_csv(url, header=0, sep=",",
                                    quoting=csv.QUOTE_ALL, quotechar="\"", escapechar="\\",
                                    doublequote=False, error_bad_lines=False, warn_bad_lines=True)
