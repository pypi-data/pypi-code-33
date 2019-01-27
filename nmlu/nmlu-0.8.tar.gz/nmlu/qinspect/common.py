import numpy as np
import pandas as pd
from sparklines import sparklines


def sparklines_str(col, bins=10):
    bins = np.histogram(col[col.notnull()], bins=bins)[0]
    return "".join(sparklines(bins))


def df_types_and_stats(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isnull().sum().sort_index()
    missing_pc = (missing / len(df) * 100).round(2)
    types_and_missing = pd.DataFrame(
        {
            'type': df.sort_index().dtypes,
            '#nas': missing,
            '%nas': missing_pc,
            'card': df.agg('nunique').sort_index(),

        },
        index=df.columns.sort_values()
    )
    dist = df.agg([sparklines_str]).T.sort_index()
    desc = df.describe(include='all').T.sort_index()
    return pd.concat([dist, types_and_missing, desc], axis=1, sort=True)
