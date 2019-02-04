import os
import pandas as pd
from functools import reduce
from sqlalchemy import MetaData, Table

from .BaseLoader import BaseMultiLoader
from .common import ingesters, transformers


class TCRSequenceLoader(BaseMultiLoader):
    file_names = [
        "data_tcrseq.aaCDR3.txt",
        "data_tcrseq.ntCDR3.txt",
        "data_tcrseq.totCDR3.txt",
        "data_tcrseq.VJ.txt",
    ]
    chunksize = 1000000

    def __init__(self, *args, sample_label_to_id=None, **kwargs):
        self.sample_label_to_id = sample_label_to_id
        print(sample_label_to_id)
        super(TCRSequenceLoader, self).__init__(*args, **kwargs)

    def load(self):
        datas = [
            pd.read_csv(
                n,
                sep="\t",
                index_col=None,
                dtype={
                    'sample_label': str,
                    'sequence': str,
                    'sequence_type': str,
                    'reads': str
                },
            ) for n in self.file_names]
        for d in datas:
            d['reads'] = pd.to_numeric(d['reads'])
        return datas

    def pre_ingest_transform(self, datas):
        sequence_names = [fn.split(".")[1] for fn in self.file_names]
        for d in datas:
            sums = d.groupby('sample_label').sum()
            totals = sums.ix[d['sample_label']]
            d = d.set_index('sample_label')
            d['freq'] = d['reads'].values.flatten() / totals.values.flatten()
        D = pd.concat(datas)
        D["sample_id"] = [self.sample_label_to_id[x] for x in D["sample_label"].str.slice(0, -6)]
        del D["sample_label"]
        return D

    def ingest(self, D):
        ingesters.df_with_progress(D, "tcrsequences", self.engine, self.chunksize)
