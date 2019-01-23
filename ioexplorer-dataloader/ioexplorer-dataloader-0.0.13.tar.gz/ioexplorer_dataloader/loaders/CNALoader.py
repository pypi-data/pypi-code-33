import os
import pandas as pd
from functools import reduce
from sqlalchemy import MetaData, Table

from .BaseLoader import BaseMultiLoader
from .common import ingesters, transformers


class CNALoader(BaseMultiLoader):
    file_names = ["data_discrete_CNA.txt", "data_continuous_CNA.txt"]
    chunksize = 1000000

    def __init__(self, *args, sample_label_to_id=None, **kwargs):
        self.sample_label_to_id = sample_label_to_id
        super(CNALoader, self).__init__(*args, **kwargs)

    def load(self):
        return [
            pd.read_csv(p, sep="\t") if os.path.exists(p) else None for p in self.paths
        ]

    def pre_ingest_transform(self, datas):
        names = ["_".split(fn)[1] for fn in self.file_names]
        melted_datas = [
            transformers.melted_gene_matrix(D, name)
            for D, name in zip(datas, names)
            if D is not None
        ]
        return reduce(
            lambda A, B: A.merge(B, how="outer", on=["Hugo_Symbol", "Entrez_Gene_Id"]),
            melted_datas,
        )

    def ingest(self, D):
        ingesters.df_with_progress(D, "cnas", self.engine, self.chunksize)
