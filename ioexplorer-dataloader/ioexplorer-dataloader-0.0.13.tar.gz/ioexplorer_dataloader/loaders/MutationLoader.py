import pandas as pd
from sqlalchemy import MetaData, Table

from .BaseLoader import BaseLoader
from .common import ingesters


class MutationLoader(BaseLoader):
    file_name = "data_mutations_extended.txt"
    chunksize = 100000

    def __init__(self, *args, sample_label_to_id=None, **kwargs):
        self.sample_label_to_id = sample_label_to_id
        super(MutationLoader, self).__init__(*args, **kwargs)

    def load(self):
        return pd.read_csv(self.path, low_memory=False, sep="\t", skiprows=1)

    def pre_ingest_transform(self, data):
        data.columns = map(lambda x: x.lower(), data.columns.values)
        data.rename(columns={"tumor_sample_barcode": "sampleId"}, inplace=True)
        data["protein_position"] = data["protein_position"].apply(
            lambda x: x if pd.isnull(x) else str(int(x))
        )
        return data

    def ingest(self, D):
        table = Table("mutations", MetaData(), autoload=True, autoload_with=self.engine)
        columns = [column.name for column in table.c if column.name in D.columns.values]
        ingesters.df_with_progress(D[columns], "mutations", self.engine, self.chunksize)
