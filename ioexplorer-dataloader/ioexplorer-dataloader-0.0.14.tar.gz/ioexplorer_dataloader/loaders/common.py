import pandas as pd
from tqdm import tqdm
from io import StringIO


class _AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(_AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def cbio_tsv(path):
    return pd.read_csv(path, sep="\t", low_memory=False, keep_default_na=False)


loaders = _AttrDict(cbio_tsv=cbio_tsv)


def _chunker(seq, size):
    # from http://stackoverflow.com/a/434328
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def df_to_sql(df, table_name, engine):
    if not df.empty:
        # Make a string buffer
        output = StringIO()
        # Wrap column names with double quotes for SQL
        df.columns = map(lambda c: '"{}"'.format(c), df.columns.values)
        # Write dataframe to the string buffer as raw .tsv
        df.to_csv(output, sep="\t", header=False, index=False)
        output.getvalue()
        output.seek(0)
        curs = engine.raw_connection().cursor()
        columns = df.columns.values
        res = curs.copy_from(
            output, '"{}"'.format(table_name), null="", columns=columns
        )
        curs.connection.commit()
        curs.close()


def df_to_sql_with_progress(df, table_name, engine, chunksize):
    with tqdm(total=len(df)) as pbar:
        for cdf in _chunker(df, chunksize):
            df_to_sql(cdf, table_name, engine)
            pbar.update(chunksize)


ingesters = _AttrDict(df_with_progress=df_to_sql_with_progress)


def df_lowercase_columns_transform(D):
    # Doesn't lowercase foreign keys, with end with 'Id'.
    D.columns = map(
        lambda x: x.lower() if not x.endswith("Id") else x, D.columns.values
    )
    return D


def melted_gene_matrix(D, value_name):
    melt_ids = {"Hugo_Symbol", "Entrez_Gene_Id"}.intersection(set(D.columns.values))
    D = pd.melt(D, id_vars=melt_ids)
    D.columns = map(lambda x: x.lower(), D.columns.values)
    D.rename(columns={"variable": "sample_label", "value": value_name}, inplace=True)
    return D


transformers = _AttrDict(
    df_lowercase_columns=df_lowercase_columns_transform,
    melted_gene_matrix=melted_gene_matrix,
)
