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


def build_altair_spec(df, picks):
  # log.debug(picks)

  axis=alt.Axis(
    tickCount=9,
  )

  # Decorate the dataset for specific dtypes.
  for key, colname in picks.items():
    col = df[colname]
    picks[key] = colname + ':' + get_altair_encoding(col)

  encode_options = []

  # Encode
  if 'x' in picks:
    encode_options.append(
      alt.X(
        picks['x'],
        axis=axis,
        scale=alt.Scale(zero=False),
      )
    )

  if 'y' in picks:
    encode_options.append(
      alt.Y(
        picks['y'],
        axis=axis,
        scale=alt.Scale(zero=False),
      )
    )


  if 'color' in picks:
    encode_options.append(
      alt.Color(
        picks['color'],
      )
    )

  if 'size' in picks:
    encode_options.append(
      alt.Size(
        picks['size'],

      )
    )


  # dummy_url.json is intended to make Altair think we're passing in a url later.
  # Instead, we'll pass the data into vega-lite directly.
  chart = alt.Chart('dummy_url.json').mark_circle().encode( *encode_options )

  chart = chart.configure(**{
    'autosize': 'fit',
    'background': 'white',
  })

  chart = chart.configure_axis(**{
    'labelOverlap': 'parity',
  })

  spec = chart.to_dict()
  # log.debug(f'Altair spec:\n{spec}')

  return spec

def build_groupedbar_altair_spec(df, picks):
  # Decorate the dataset for specific dtypes.
  for key, colname in picks.items():
    col = df[colname]
    picks[key] = colname + ':' + get_altair_encoding(col)

  encode_options = []

  if 'x' in picks:
    encode_options.append(
      alt.X(
        picks['x'],
        scale=alt.Scale(rangeStep=None),
      )
    )
    encode_options.append(
      alt.Y(
        picks['x'],
        aggregate='count',
      )
    )
    encode_options.append(
      alt.Color(
        picks['x']
      )
    )

  if 'group' in picks:
    encode_options.append(
      alt.Column(
        picks['group']
      )
    )
  chart = alt.Chart('dummy_url.json').mark_bar().encode( *encode_options )

  chart = chart.configure(**{
    'autosize': 'fit',
    'background': 'white',
  })

  chart = chart.configure_axis(**{
    'labelOverlap': 'parity',
  })

  spec = chart.to_dict()

  return spec


MAX_ALTAIR_ITEMS = 5000

def build_altair_subset(df, picks):
  # log.debug(df.head())
  # log.debug(picks)

  # Only return the columns that were requested.
  # Altair options are e.g. { 'x': 'title', 'y': 'runtime' }, etc.
  # So we can get the columns from the values of that dict.
  # Also, we have to use set to dedupe the values, because the user could pick the same column name multiple times.
  columns = list( set(picks.values()) )
  df = df[columns]

  # If the dataframe is bigger than MAX_ALTAIR_ITEMS, sample it.
  if MAX_ALTAIR_ITEMS < df.shape[0]:
    df = df.sample(n=MAX_ALTAIR_ITEMS, random_state=0)

  return df
