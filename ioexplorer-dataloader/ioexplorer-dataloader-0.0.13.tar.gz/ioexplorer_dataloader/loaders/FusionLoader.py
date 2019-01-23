import pandas as pd
from sqlalchemy import MetaData, Table

from .BaseLoader import BaseLoader
from .common import ingesters


class FusionLoader(BaseLoader):
    file_name = "data_fusions.txt"

    def __init__(self, *args, sample_label_to_id=None, **kwargs):
        self.sample_label_to_id = sample_label_to_id
        super(FusionLoader, self).__init__(*args, **kwargs)

    def load(self):
        return pd.read_csv(self.path, low_memory=False, sep="\t")

    def pre_ingest_transform(self, data):
        data.columns = map(lambda x: x.lower(), data.columns.values)
        data.rename(columns={"tumor_sample_barcode": "sampleId"}, inplace=True)
        return data

    def ingest(self, D):
        table = Table("fusions", MetaData(), autoload=True, autoload_with=self.engine)
        columns = [column.name for column in table.c if column.name in D.columns.values]
        ingesters.df_with_progress(D[columns], "fusions", self.engine, self.chunksize)
