import numpy as np
import pandas as pd
import scipy.sparse
import math


def downsample_dataframe(df, sample_ratio=42, sample_seed=None):

  try:
    # Set the seed
    np.random.seed(sample_seed)

    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.rand.html#numpy.random.rand
    num_rows = df.shape[0]
    randoms = np.random.rand(num_rows)

    # Use percentiles to downsample df
    if 0 < sample_ratio < 1:
      perc = np.percentile(randoms, sample_ratio*100)
    elif sample_ratio < 0:
      perc = 0
    else:
      perc = 1

    sample_indices = np.argwhere(randoms <= perc)
    sample_indices = sample_indices.transpose()[0]

    # Create sampled df from indices
    df_sampled = df.iloc[ sample_indices.tolist() ]

    # We have to reset the index, otherwise downstream indexing won't work properly
    df_sampled = df_sampled.reset_index(drop=True)

    return df_sampled

  finally:
    # Reset the seed no matter what
    np.random.seed()



# Abstraction to handle numpy or scipy.sparse arrays.
# Turns an entire pandas Series into a single numpy.ndarray or scipy.sparse matrix.
def vstack_col_to_array(col):
  arrays = col.values

  # Peek at the first element to see what kind of arrays we have.
  try:
    _type = type(arrays[0])
    if _type == np.ndarray:
      return np.vstack(arrays)
    elif _type == scipy.sparse.csr_matrix:
      return scipy.sparse.vstack(arrays)
    else:
      raise (f'vstack_col_to_array: Array type {_type} not yet supported.')

  except:
    raise Exception('vstack_col_to_array: Arrays should be all of the same type')


# Dictionary: dict keys are the unique dataset values; dict values are the counts.
def get_distinct_counts(col):
  # Don't calculate distinct counts for vectors.
  if is_col_vector(col):
    return None

  try:
    return col.value_counts(dropna=False)
  except TypeError:
    # This means we can't calculate distinct_counts, which is fine.
    return None



# Todo: make this more robust than just looking at the first value.
def is_col_vector(col):
  valids = col.dropna()
  if valids.shape[0] == 0:
    return False

  return is_obj_fancy_array(valids.iloc[0])


def is_obj_fancy_array(obj):
  return type(obj) in (np.ndarray, scipy.sparse.csr_matrix)

# https://docs.python.org/3/library/stdtypes.html
def is_basic_type(value):
  return isinstance(value, (int, float, bool, str))


def is_val_none_equivalent(val):
  if val is None:
    return True
  elif type(val) == float:
    return math.isnan(val) or val is np.NaN or val is np.Inf
  else:
    return val is pd.NaT


def is_value_nan_equivalent(value):
  return (
    value is pd.NaT
    or isinstance(value, float) and np.isnan(value)
    or type(value) == float and math.isnan(value)
  )


# https://stackoverflow.com/questions/40745180/stacking-two-sparse-matrices-with-different-dimensions
def ensure_2d_array_has_same_cols(array1, array2):
  delta = array2.shape[1] - array1.shape[1]

  # If there's a difference in rows, hstack both arrays with a zeroed array so that they're the same size.
  if delta > 0:
    array1 = pad_csr_matrix(array1, abs(delta))
  elif delta < 0:
    array2 = pad_csr_matrix(array2, abs(delta))

  return array1, array2

def ensure_matched_vector_dimensions(vector1, vector2):
  if vector1.shape[1] == vector2.shape[1]:
    return vector1, vector2

  delta = vector2.shape[1] - vector1.shape[1]

  # If there's a difference in rows, hstack both vectors with a zeroed vector so that they're the same size.
  if delta > 0:
    vector1 = np.pad(vector1, (0, abs(delta)), 'constant')
  elif delta < 0:
    vector2 = np.pad(vector2, (0, abs(delta)), 'constant')

  return vector1, vector2


def pad_csr_matrix(mat, pad):
  rowcount = mat.shape[0]
  zeros = scipy.sparse.csr_matrix(  (rowcount, pad)  )
  return scipy.sparse.hstack([mat, zeros])
