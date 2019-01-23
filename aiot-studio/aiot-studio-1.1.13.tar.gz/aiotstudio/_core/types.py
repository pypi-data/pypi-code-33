
import pandas as pd
import numpy as np


def mql_result_to_pandas_dataframe(result):
    # type: (dict) -> pd.DataFrame
    _columns = result.get('columns', [])
    _rows = result.get('rows', [])

    columns = [col['label'] for col in _columns]
    dataframe = pd.DataFrame(_rows, columns=columns)
    for column in _columns:
        if column['type'] == 'datetime':
            id_col = column['label']
            dataframe[id_col] = pd.to_datetime(dataframe[id_col], utc=True)
    dataframe = dataframe.fillna(value=np.nan)
    return dataframe
