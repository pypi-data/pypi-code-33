import numpy as np
from sqlalchemy import MetaData, Table
from sqlalchemy.types import Numeric

from .BaseLoader import BaseLoader
from .common import loaders, ingesters, transformers


class ClinicalSampleLoader(BaseLoader):
    file_name = "data_clinical_sample.txt"

    def __init__(self, *args, subject_label_to_id=None, **kwargs):
        self.subject_label_to_id = subject_label_to_id
        super(ClinicalSampleLoader, self).__init__(*args, **kwargs)

    def load(self):
        return loaders.cbio_tsv(self.path)

    def inspect(self):
        D = self.load().dropna(axis="columns", how="all")
        D.columns = map(lambda x: x.lower(), D.columns.tolist())
        table = Table("samples", MetaData(), autoload=True, autoload_with=self.engine)
        loadable_columns = [
            str(column.name) for column in table.c if column.name in D.columns.values
        ]
        not_loadable_columns = list(set(D.columns.tolist()) - set(loadable_columns))
        info = {
            "num_samples": D.shape[0],
            "num_variables": len(loadable_columns),
            "num_excluded_variables": len(not_loadable_columns),
            "variables": loadable_columns,
        }
        return info

    def pre_ingest_transform(self, D):
        return transformers.df_lowercase_columns(D)

    def validate(self):
        if not self.validate_file_exists():
            return False
        D = self.load()
        if "sample_label" not in D.columns:
            print(
                'No column named "sample_label". This is required, and must be the unique sample label.'
            )
            return False
        if "subject_label" not in D.columns:
            print(
                'No column named "subject_label". '
                "This is required, and must be the unique "
                "label of the subject from which this sample was derived."
            )
            return False
        return self.validate_file_exists()

    def ingest(self, D):
        D["subject_id"] = [
            self.subject_label_to_id[label] for label in D["subject_label"]
        ]
        table = Table("samples", MetaData(), autoload=True, autoload_with=self.engine)
        columns = [column.name for column in table.c if column.name in D.columns.values]
        types = [column.type for column in table.c if column.name in D.columns.values]
        for c, t in zip(columns, types):
            if isinstance(t, Numeric):
                if str(D[c].dtype) == 'object':
                    D[c][D[c] == 'NA'] = ''
        ingesters.df_with_progress(D[columns], "samples", self.engine, self.chunksize)
        res = self.conn.execute(
            "SELECT id FROM samples WHERE sample_label in {};".format(
                tuple(D["sample_label"])
            )
        )
        sample_ids = [r[0] for r in res]
        return {label: id for label, id in zip(D["sample_label"], sample_ids)}
