import altair as alt
from pandas.api.types import is_numeric_dtype, is_bool_dtype, is_object_dtype, is_datetime64_any_dtype

from datamode.utils.data import get_distinct_counts

from datamode.utils.utils import get_logger
log = get_logger(__name__)


MAX_NUMERICAL_CATEGORIES = 10

def get_altair_encoding(col):
  dtype = col.dtype

  # quantitative - can use nominal for low-cardinality numerics.
  # Nominal and ordinal are both categorical, but nominal is unordered, whereas ordinal is, well, ordered.
  # https://altair-viz.github.io/user_guide/encoding.html#encoding-data-types
  if is_numeric_dtype(dtype):
    distinct_counts = get_distinct_counts(col)
    if distinct_counts is not None and distinct_counts.shape[0] <= MAX_NUMERICAL_CATEGORIES:
      return 'N'
    return 'Q'

  # ordinal
  if is_bool_dtype(dtype):
    return 'O'

  # nominal
  if is_object_dtype(dtype):
    return 'N'

  # temporal
  if is_datetime64_any_dtype(dtype):
    return 'T'

  raise Exception('Pandas dtype not mapped for altair.')

def build_x(encode_options, **kwargs):
  encode_options.append(alt.X(**kwargs))
  return encode_options

def build_y(encode_options, **kwargs):
  encode_options.append(alt.Y(**kwargs))
  return encode_options

def build_color(encode_options, **kwargs):
  encode_options.append(alt.Color(**kwargs))
  return encode_options

def build_size(encode_options, **kwargs):
  encode_options.append(alt.Size(**kwargs))
  return encode_options

def build_column(encode_options, **kwargs):
  encode_options.append(alt.Column(**kwargs))
  return encode_options