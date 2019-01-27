import pandas as pd
import numpy as np
from pandas.api.types import is_string_dtype, is_numeric_dtype
from typing import Tuple


def arr_split(a: np.ndarray, n: int) -> Tuple[np.ndarray, np.ndarray]:
    """Split array into n and len-n."""
    return a[:n].copy(), a[n:].copy()


def get_sample(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Gets a random sample of n rows from df, without replacement."""
    idxs = sorted(np.random.permutation(len(df))[:n])
    return df.iloc[idxs].copy()


def train_cats(df: pd.DataFrame):
    """Convert string columns to categorical columns.

    Parameters
    ----------
    df: MODIFIED
    """
    for col_name, col in df.items():
        if is_string_dtype(col):
            df[col_name] = col.astype('category').cat.as_ordered()


def apply_cats(df: pd.DataFrame, df_train: pd.DataFrame):
    """Convert string columns to categorical columns, using same category codes ad in df_train.

    Parameters
    ----------
    df: MODIFIED

    df_train: checks that each string column also exists in this dataframe, and use the same category codes
    """
    for col_name, col in df.items():
        if (col_name in df_train.columns) and (df_train[col_name].dtype.name == 'category'):
            df[col_name] = pd.Categorical(
                col, categories=df_train[col_name].cat.categories, ordered=True)


def fill_missing(df: pd.DataFrame, col_name: str, na_dict: dict = None):
    """Fill missing data for numeric columns.

    Parameters
    ----------
    df: MODIFIED

    col_name

    na_dict: { col_name (str) -> filler } MODIFIED
    """
    na_dict = {} if na_dict is None else na_dict
    col = df[col_name]
    if (
            is_numeric_dtype(col) and
            (pd.isnull(col).sum() or (col_name in na_dict))
    ):
        df[col_name + '_na'] = pd.isnull(col)
        filler = na_dict[col_name] if col_name in na_dict else col.median()
        df[col_name] = col.fillna(filler)
        na_dict[col_name] = filler
    return na_dict


def numericalize(df: pd.DataFrame, col_name, max_n_cat=-1, nans_to_zero=True, no_binary_dummies=False):
    """Numericalize categories.

    Parameters
    ----------
    df: MODIFIED

    nans_to_zero: if true add 1 to categories to make NaNs turned to -1 be 0

    max_n_cat: max number of categories for a categorical column to be left
        un-transformed; if it has more than this it get numericalized; by
        default it's -1 so *all columns get numericalized*
    """
    col = df[col_name]
    if not is_numeric_dtype(col):
        if (
                len(col.cat.categories) > max_n_cat or
                (no_binary_dummies and len(col.cat.categories) == 2)
        ):
            df[col_name] = col.cat.codes
            if nans_to_zero:
                df[col_name] += 1


def numericalized_df(df, fill_missing=False, nans_to_zero=False):
    ndf = df.copy()
    for col_name, col in ndf.items():
        is_col_numeric = is_numeric_dtype(col)
        if not is_col_numeric:
            ndf[col_name] = col.cat.codes
        if fill_missing and pd.isnull(df[col_name]).sum():
            if is_col_numeric:
                filler = ndf[col_name].median()
            else:
                filler = ndf[col_name].mode()
            df[col_name] = df[col_name].fillna(filler)
        if nans_to_zero:
            ndf[col_name] += 1
    return ndf


def proc_df(df: pd.DataFrame,
            y_fld: str = None,
            na_dict: dict = None,
            skip_flds: list = None,
            ignore_flds: list = None,
            max_n_cat: int = -1,
            no_binary_dummies=False):
    """Split response variable, numericalizes df and fill missing values.
    """
    if skip_flds is None:
        skip_flds = []
    if ignore_flds is None:
        ignore_flds = []
    if na_dict is None:
        na_dict = {}
    na_dict_initial = na_dict.copy()

    assert sum(
        1 if (
                is_string_dtype(df[col_name]) and
                col_name not in skip_flds and
                col_name not in ignore_flds
        ) else 0
        for col_name in df.columns
    ) == 0, "Expected df to have all string columns converted to categories"

    df = df.copy()  # do not modify passed df

    # set aside ignored fields (to be re-added to result at the end, untouched)
    ignored_cols = df.loc[:, ignore_flds]
    df.drop(ignore_flds, axis=1, inplace=True)

    # split off y (and numericalize it if needed)
    y = None
    if y_fld:
        if not is_numeric_dtype(df[y_fld]):
            df[y_fld] = df[y_fld].cat.codes
        y = df[y_fld].values
        skip_flds.append(y_fld)

    df.drop(skip_flds, axis=1, inplace=True)  # drop skip fields

    for col_name in df.columns:
        # fill missing values
        fill_missing(df, col_name, na_dict)
        # numericalize
        numericalize(df, col_name, max_n_cat=max_n_cat, no_binary_dummies=no_binary_dummies)
    # if na_dict was passed, make sure result doesn't contain extra _na
    # columns even if there were missing values in them (otherwise model
    # would crash on predict since it wasn't expecting them)
    if len(na_dict_initial.keys()) > 0:
        df.drop([
            a + '_na'
            for a in list(set(na_dict.keys()) - set(na_dict_initial.keys()))
        ], axis=1, inplace=True)

    # 1-hot encode categorical cols that were not numericalized
    # (those with <= max_n_cat categories)
    df = pd.get_dummies(df, dummy_na=True)

    df = pd.concat([ignored_cols, df], axis=1)  # re-add untouched ignored cols

    return df, y, na_dict


def add_datepart(df: pd.DataFrame,
                 fld_name: str,
                 drop: bool = True,
                 time: bool = False):
    """Add extra features derived from date(time).
    """
    fld = df[fld_name]
    fld_dtype = fld.dtype
    if isinstance(fld_dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
        fld_dtype = np.datetime64
    if not np.issubdtype(fld_dtype, np.datetime64):
        df[fld_name] = fld = pd.to_datetime(fld, infer_datetime_format=True)

    attr = ['Year', 'Month', 'Week', 'Day', 'Dayofweek', 'Dayofyear', 'Is_month_end',
            'Is_month_start', 'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start']
    if time:
        attr = attr + ['Hour', 'Minute', 'Second']

    for n in attr:
        df[fld_name + n] = getattr(fld.dt, n.lower())

    df[fld_name + 'Elapsed'] = fld.astype(np.int64) // 10 ** 9

    if drop:
        df.drop(fld_name, axis=1, inplace=True)
