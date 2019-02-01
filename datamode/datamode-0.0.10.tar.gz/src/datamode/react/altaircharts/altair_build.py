import altair as alt
import pandas as pd

from .altair_utils import *

from datamode.utils.utils import get_logger
log = get_logger(__name__)


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

def build_altair_counts(df, picks):
  current_record_count = None
  rdict = {}
  i = 0
  x = picks.get('x', None)
  group = picks.get('group', False)

  if (group and x) and (group != x):
    df = df.groupby(group)[x].value_counts()
    current_record_count = df.sum()
    dict1 = df.to_dict()
    for k,v in dict1.items():
      rdict[i] = [k[0], k[1], v]
      i += 1
    rdf = pd.DataFrame.from_dict(rdict, orient='index',
                            columns=[group, x, 'counts'],
    )

    return rdf, current_record_count

  elif (group or x) or (group == x):
    if group:
      df = df[group].value_counts()
      colname = group
    elif x:
      df = df[x].value_counts()
      colname = x
    current_record_count = df.sum()
    dict1 = df.to_dict()
    for k,v in dict1.items():
      rdict[i] = [k, v]
      i += 1
    rdf = pd.DataFrame.from_dict(rdict, orient='index',
                            columns=[colname, 'counts'],
    )

    return rdf, current_record_count

  else:
    return df, current_record_count


# Decorate the dataset for specific dtypes.
def decorate_altair_picks(df, picks):
  for key, colname in picks.items():
    col = df[colname]
    picks[key] = colname + ':' + get_altair_encoding(col)
  return picks


def build_altair_spec(df, chart_type, chartset):
  picks = chartset['picks']
  picks = decorate_altair_picks(df, picks)


  if chart_type == 'multi':
    chart = build_altair_multi(chartset['subtype'], picks)
  elif chart_type == 'barchart':
    chart = build_altair_barchart(picks)

  chart = chart.configure(**{
    'autosize': 'fit',
    'background': 'white',
  })

  chart = chart.configure_axis(**{
    'labelOverlap': 'parity',
  })

  spec = chart.to_dict()

  return spec

def build_altair_multi(subtype, picks):
  encode_options = []

  axis=alt.Axis(
    tickCount=9,
  )

  # Encode
  if 'x' in picks:
    encode_options = build_x(encode_options,
      shorthand=picks['x'],
      axis=axis,
      scale=alt.Scale(zero=False),
    )

  if 'y' in picks:
    encode_options = build_y(encode_options,
      shorthand=picks['y'],
      axis=axis,
      scale=alt.Scale(zero=False),
    )

  if 'color' in picks:
    encode_options = build_color(encode_options,
      shorthand=picks['color'],
    )


  if 'size' in picks:
    encode_options = build_size(encode_options,
      shorthand=picks['size']
    )

  # dummy_url.json is intended to make Altair think we're passing in a url later.
  # Instead, we'll pass the data into vega-lite directly.
  chart = alt.Chart('dummy_url.json')

  if subtype == 'scatter':
    chart_marked = chart.mark_circle()
  elif subtype == 'line':
    chart_marked = chart.mark_line()
  else:
    log.debug('build_altair_multi: Couldn\'t process subtype={subtype} ')

  chart_encoded = chart_marked.encode( *encode_options )

  return chart_encoded


def build_altair_barchart(picks):
  encode_options = []

  if 'x' in picks:
    encode_options = build_x(encode_options,
      shorthand=picks['x'],
      scale=alt.Scale(rangeStep=None),
    )

    encode_options = build_y(encode_options,
      shorthand='counts:Q',
    )

    encode_options = build_color(encode_options,
      shorthand=picks['x'],
    )

  if 'group' in picks:
    encode_options = build_column(encode_options,
      shorthand=picks['group'],
    )

  chart = alt.Chart('dummy_url.json').mark_bar().encode( *encode_options )

  return chart


