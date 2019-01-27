import pandas as pd
import numpy as np
from numpy.testing import *

import nmlu.etl as etl


def test_arr_split():
    # 1D
    a = np.arange(5) * 10
    a1, a2 = etl.arr_split(a, 3)
    assert_array_equal(a1, np.array([0, 10, 20]))
    assert_array_equal(a2, np.array([30, 40]))
    # 2D
    m = np.arange(15).reshape((5, 3))
    m1, m2 = etl.arr_split(m, 4)
    assert_array_equal(m1, np.array(
        [[0, 1, 2],
         [3, 4, 5],
         [6, 7, 8],
         [9, 10, 11]]
    ))
    assert_array_equal(m2, np.array([[12, 13, 14]]))


def test_get_sample():
    df = pd.DataFrame({
        'A': [50, 40, 30, 20, 10],
        'B': ['a', 'b', 'c', 'd', 'e'],
    })
    s = etl.get_sample(df, 2)
    for _, s_row in s.iterrows():  # each row of s matches exactly 1 row in df
        assert 1 == sum(
            1 for _, df_row in df.iterrows()
            if np.array_equal(s_row.values, df_row.values)
        )
    s2 = etl.get_sample(df, len(df))
    for _, s2_row in s2.iterrows():  # each row of s2 matches exactly 1 row in df
        assert 1 == sum(
            1 for _, df_row in df.iterrows()
            if np.array_equal(s2_row.values, df_row.values)
        )


def test_train_cats():
    df = pd.DataFrame({
        'A': [50, 40, 30, 20, 10],
        'B': ['a', 'b', 'c', 'd', 'e'],
    })
    etl.train_cats(df)
    assert pd.api.types.is_categorical(df['B'])
    assert not pd.api.types.is_categorical(df['A'])


def test_apply_cats():
    df1 = pd.DataFrame({'C': ['a', 'c', 'd', 'e']})
    df2 = pd.DataFrame({'C': ['c', 'c', 'e', 'b']})
    etl.train_cats(df1)
    assert np.array_equal(df1['C'].cat.codes.values, [0, 1, 2, 3])
    etl.apply_cats(df2, df1)
    assert np.array_equal(df2['C'].cat.codes.values, [1, 1, 3, -1])


def test_fill_missing():
    # 0 1 2 3 7 7 => median = 2.5
    df = pd.DataFrame({'C': [7, 3, None, 2, 0, None, 7, 1]})
    nas = {}  # test it gets *both* modified and returned
    returned_nas = etl.fill_missing(df, 'C', nas)
    assert np.array_equal(df['C'].values, [7, 3, 2.5, 2, 0, 2.5, 7, 1])
    assert np.array_equal(df['C_na'].values,
                          [False, False, True, False, False, True, False, False])
    assert nas == {'C': 2.5}
    assert returned_nas is nas


def test_numericalize():
    df = pd.DataFrame({
        'A': [50, 40, 30, 20, 10],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': ['m', 'f', 'f', None, 'm'],
    })
    df['B'] = df.B.astype('category').cat.as_ordered()
    df['C'] = df.C.astype('category').cat.as_ordered()
    etl.numericalize(df, 'A', max_n_cat=4)
    etl.numericalize(df, 'B', max_n_cat=4)
    etl.numericalize(df, 'C', max_n_cat=4)
    assert np.array_equal(df.B.values, [1, 2, 3, 4, 5])
    assert list(df.C.values) == ['m', 'f', 'f', np.nan, 'm']


def test_proc_df():
    df = pd.DataFrame({
        'A': [50, 40, 30, None, 10],
        'B': ['a', 'b', 'c', 'd', 'e'],
        'C': ['m', 'f', 'f', None, 'm'],  # to be one-hot-encoded
        'Y': ['foo', 'bar', 'foo', 'foo', 'baz'],
        'Z': [0, 0, 0, 0, 0],  # to be skipped
        'N': ['do', 'not', 'touch', 'this', '!']
    })
    etl.train_cats(df)
    nas = dict(A=-42)
    df_trn, y, returned_nas = etl.proc_df(
        df,
        'Y',
        skip_flds=['Z'],
        ignore_flds=['N'],
        na_dict=nas,
        max_n_cat=2
    )
    assert set(df_trn.columns) == {'A', 'A_na', 'B', 'C_f', 'C_m', 'C_nan', 'N'}
    for col_name in df_trn.columns:
        if col_name != 'N':
            assert pd.api.types.is_numeric_dtype(df_trn[col_name])
    assert pd.api.types.is_categorical(df_trn.N.dtype)
    assert_array_equal(df_trn.A.values, [50, 40, 30, -42, 10])
    assert_array_equal(df_trn.A_na.values, [False, False, False, True, False])
    assert_array_equal(y, [2, 0, 2, 2, 1])


def test_add_datepart():
    df = pd.DataFrame({
        'T': pd.date_range('2013-01-02', periods=4),
        'A': 1.,
        'D': np.array([3] * 4, dtype='int32'),
        'E': pd.Categorical(["test", "train", "test", "train"]),
        'F': 'foo'}
    )
    etl.add_datepart(df, 'T')
    assert set(df.columns) == {
        'A',
        'D',
        'E',
        'F',
        'TDay',
        'TDayofweek',
        'TDayofyear',
        'TElapsed',
        'TIs_month_end',
        'TIs_month_start',
        'TIs_quarter_end',
        'TIs_quarter_start',
        'TIs_year_end',
        'TIs_year_start',
        'TMonth',
        'TWeek',
        'TYear'
    }
