import numpy as np
from sqlalchemy import MetaData, Table

from .BaseLoader import BaseLoader
from .common import loaders, ingesters, transformers


class ClinicalSubjectLoader(BaseLoader):
    file_name = "data_clinical_patient.txt"

    def __init__(self, *args, **kwargs):
        self.dataset_id = kwargs.pop("dataset_id", None)
        super(ClinicalSubjectLoader, self).__init__(*args, **kwargs)

    def load(self):
        return loaders.cbio_tsv(self.path)

    def inspect(self):
        D = self.load().dropna(axis="columns", how="all")
        D.columns = map(lambda x: x.lower(), D.columns.tolist())
        table = Table("subjects", MetaData(), autoload=True, autoload_with=self.engine)
        loadable_columns = [
            str(column.name) for column in table.c if column.name in D.columns.values
        ]
        not_loadable_columns = list(set(D.columns.tolist()) - set(loadable_columns))
        info = {
            "num_subjects": D.shape[0],
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
        if "subject_label" not in D.columns:
            print(
                'No column named "subject_label". This is required, and must be the unique subject label.'
            )
            return False
        return self.validate_file_exists()

    def ingest(self, D):
        table = Table("subjects", MetaData(), autoload=True, autoload_with=self.engine)
        columns = [column.name for column in table.c if column.name in D.columns.values]
        columns.append("dataset_id")
        D["dataset_id"] = self.dataset_id
        ingesters.df_with_progress(D[columns], "subjects", self.engine, self.chunksize)
        res = self.conn.execute(
            "SELECT id FROM subjects WHERE subject_label in {} and dataset_id={};".format(
                str(D["subject_label"].tolist()).replace("[", "(").replace("]", ")"),
                self.dataset_id,
            )
        )
        subject_ids = [r[0] for r in res]
        return {label: id for label, id in zip(D["subject_label"], subject_ids)}
