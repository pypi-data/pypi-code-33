import os

from sdhpy.errors import DatasetNotProvidedError
from sdhpy.sdhstore.ckanhelper import get_store_user, get_ckan, search_resources_by_db
from sdhpy.sdhtoolkit.dataset import PandasDataset
from sdhpy.utils.utils import get_resource_id


def get_pandas_dataframe(**kwargs):
    store_apikey = kwargs.get("store_apikey", None)
    resource_url = kwargs.get("resource_url" , None)
    db_and_tbl = kwargs.get("db_and_tbl", None)
    dataset = kwargs.get("dataset", None)
    dataset_id = kwargs.get("dataset_id", None)
    resource_id = kwargs.get("resource_id", None)

    if not store_apikey:
        raise ValueError("Please provide SDH store API Key")

    # Dataset
    resource_id = get_resource_id(store_apikey, resource_url=resource_url, db_and_tbl=db_and_tbl,
                                                       dataset=dataset, dataset_id=dataset_id, resource_id=resource_id)
    ds = PandasDataset(store_apikey, resource_id)
    return ds


class SdhPandasDatabase(object):
    def __init__(self, db_name, sdh_pandas):
        self.sdh_pandas = sdh_pandas
        self.db_name = db_name

    def show_tables(self):
        return search_resources_by_db(self.sdh_pandas.store_apikey, self.db_name)["results"]

    def __getattr__(self, name):
        return get_pandas_dataframe(tokens=self.sdh_pandas.tokens, store_apikey=self.sdh_pandas.store_apikey, db_and_tbl=(self.db_name + "." + name))


class SdhPandas(object):
    def __init__(self, **kwargs):
        self._tokens = kwargs.get("tokens", None)
        self._store_apikey = kwargs.get("store_apikey", os.environ.get("SDH_API_KEY", None))
        self._ckan = get_ckan(self._store_apikey)

    @property
    def tokens(self):
        return self._tokens

    @property
    def store_apikey(self):
        return self._store_apikey

    @property
    def ckan(self):
        return self._ckan

    def url(self, url):
        return get_pandas_dataframe(tokens=self.tokens, store_apikey=self.store_apikey, resource_url=url)

    def __getattr__(self, name):
        return SdhPandasDatabase(name, self)

