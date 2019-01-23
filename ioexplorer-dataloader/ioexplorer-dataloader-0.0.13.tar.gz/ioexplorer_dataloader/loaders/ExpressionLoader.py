import os
import pandas as pd
from functools import reduce
from sqlalchemy import MetaData, Table

from .BaseLoader import BaseMultiLoader
from .common import ingesters, transformers


class ExpressionLoader(BaseMultiLoader):
    file_names = [
        "data_expression.fpkm.txt",
        "data_expression.rld.txt",
        "data_expression.raw.txt",
    ]
    chunksize = 1000000

    def __init__(self, *args, sample_label_to_id=None, **kwargs):
        self.sample_label_to_id = sample_label_to_id
        super(ExpressionLoader, self).__init__(*args, **kwargs)

    def load(self):
        datas = [
            pd.read_csv(p, sep="\t") if os.path.exists(p) else None for p in self.paths
        ]
        return datas

    def pre_ingest_transform(self, datas):
        names = [fn.split(".")[1] for fn in self.file_names]
        melted_datas = [
            transformers.melted_gene_matrix(D, name)
            for D, name in zip(datas, names)
            if D is not None
        ]
        D = reduce(
            lambda A, B: A.merge(
                B,
                how="outer",
                on=list(
                    {"sample_label", "hugo_symbol", "entrez_gene_id"}
                    .intersection(set(A.columns))
                    .intersection(set(B.columns))
                ),
            ),
            melted_datas,
        )
        D["sample_id"] = [self.sample_label_to_id[x] for x in D["sample_label"]]
        del D["sample_label"]
        return D

    def ingest(self, D):
        ingesters.df_with_progress(D, "expressions", self.engine, self.chunksize)
