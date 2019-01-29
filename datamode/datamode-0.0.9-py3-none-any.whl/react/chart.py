import io
import json

import pprint
import numpy as np
import scipy
import pandas as pd
import statsmodels.api as sm
import seaborn as sns

from .arrow import serialize_to_arrow
from .altair import build_altair_spec, build_altair_subset, build_groupedbar_altair_spec
from sklearn.feature_extraction.text import CountVectorizer


from .reactdata import unpack_filterset


from datamode.utils.utils import get_logger
log = get_logger(__name__)


MAX_WORDCLOUD_WORDS = 150

class ChartBuilder():
  def __init__(self, reactdata, *args, **kwargs):
    super(*args, **kwargs)
    self.reactdata = reactdata

  def build_chart(self, msg_data):
    transform_id, facets, sort = unpack_filterset(msg_data['filterset'])
    df = self.reactdata.get_filtered_df(transform_id, facets)
    chart_type = msg_data['chart_type']
    chartset = msg_data['chartset']

    # log.debug(f'Chartset={chartset}')

    comm_data = {
      'msgtype': 'chart_response',
      'chart_type': chart_type,
      'chartdata': {},
    }

    buffers = None
    if chart_type == 'scatter':
      buffers = self.build_altair(comm_data, df, chartset, chart_type)
    elif chart_type == 'kde':
      self.build_kde(comm_data, df, chartset)
    elif chart_type == 'pairplot':
      buffers = self.build_pairplot(comm_data, df, chartset)
    elif chart_type == 'crosstab':
      buffers = self.build_crosstabs(comm_data, df, chartset)
    elif chart_type == 'groupedbar':
      buffers = self.build_altair(comm_data, df, chartset, chart_type)
    elif chart_type == 'wordcloud':
      self.build_wordcloud(comm_data, df, chartset)
    else:
      log.error(f'Chart_type {chart_type} not supported')

    return comm_data, buffers


  def build_altair(self, comm_data, df, chartset, chart_type):
    # Subset for altair - only take the top 5000 rows, and only return the column data that was requested.
    picks = chartset['picks']
    if chart_type == 'scatter':
      df = build_altair_subset(df, picks)
      comm_data['chartdata']['altair_spec'] = build_altair_spec(df, picks)
    elif chart_type == 'groupedbar':
      comm_data['chartdata']['altair_spec'] = build_groupedbar_altair_spec(df, picks)

    comm_data['compress'] = True
    buffer = serialize_to_arrow(df, compress=True)
    buffers = [buffer]

    log.debug(f'comm_data:\n{pprint.pformat(comm_data)}')

    return buffers


  def build_crosstabs(self, comm_data, df, chartset):
    # had to convert certain fields to string in order
    # for bools to render properly on the frontend
    picks = chartset['picks']
    rowvar = picks.get('rowvar', None)
    colvar = picks.get('colvar', None)
    comm_data['chartdata']['picks'] = {
      'rowvar': rowvar,
      'colvar': colvar,
    }
    buffers = []

    # for crosstab table
    crstab = pd.crosstab(df[rowvar], df[colvar])
    crstab_cnt = crstab.to_dict('index')
    crstab_pct = crstab.apply(lambda c: c/c.sum(), axis=0).to_dict('index')
    crstab_array = [{'index': str(index_cnt), 'values_cnt': values_cnt, 'values_pct': values_pct} for (index_cnt, values_cnt), (index_pct, values_pct) in zip(crstab_cnt.items(), crstab_pct.items())]

    # for totals row
    coltotals_cnt = crstab.sum()
    coltotals_pct = crstab.apply(lambda c: c/c.sum(), axis=0).sum()
    coltotals_cnt_dict = coltotals_cnt.to_dict()
    coltotals_pct_dict = coltotals_pct.to_dict()
    coltotals_array = [{'colname': str(k_cnt), 'total_cnt': v_cnt, 'total_pct': v_pct} for (k_cnt, v_cnt), (k_pct, v_pct) in zip(coltotals_cnt_dict.items(), coltotals_pct_dict.items())]

    comm_data['chartdata']['crosstab'] = {
      'data': crstab_array,
      'colnames': [str(i) for i in list(crstab.columns)],
      'coltotals': coltotals_array,

    }
    comm_data['compress'] = True
    buffer = serialize_to_arrow(df, compress=True)
    buffers = [buffer]

    log.debug(pprint.pformat(comm_data))

    return buffers

  # Creates a pairplot with seaborn.
  def build_pairplot(self, comm_data, df, chartset):
    columns = chartset.get('columns')
    hue = chartset.get('hue')
    # log.debug(columns)

    if len(columns) == 0:
      return None

    # Subset of data
    _vars = columns if columns else None

    grid = sns.pairplot(df, hue=hue, vars=_vars, dropna=True, diag_kind='kde', diag_kws=dict(shade=True), size=2)
    buf = io.BytesIO()
    grid.fig.savefig(buf, format='png')
    buf.seek(0)
    # todo: will this leak memory?
    return [buf.getbuffer()]
    # buf.close()




  def build_wordcloud(self, comm_data, df, chartset):
    from datamode.utils.timer import CustomTimer
    timer = CustomTimer(log, 'wordcloud')

    colname = chartset['wordcloud']
    col = df[colname]
    col = col.dropna()

    # Vectorize each string in the column.
    # This will produce a sparse matrix of words - one row per source row, and one column for each unique word.
    vectorizer = CountVectorizer()
    wordcount_vectors = vectorizer.fit_transform(col)
    # timer.report('Finished vectorization')

    # Each row has the count of words for that input row.
    # Squash the columns into a single row to get the total word counts for the whole dataset.
    squashed = wordcount_vectors.sum(axis=0)
    words = vectorizer.get_feature_names()
    # timer.report('Got feature names')

    # Convert to ndarray and get first element (the only row)
    counts = squashed.A[0]

    # Word for word?
    wordcounts = [ {'word': word, 'count': count} for word, count in zip(words, counts) ]
    # timer.report('Built dict')

    # Sort by count
    wordcounts = sorted(wordcounts, key=lambda wordcount: wordcount['count'], reverse=True)

    # Reduce the size
    wordcounts = wordcounts[:MAX_WORDCLOUD_WORDS]

    comm_data['chartdata']['wordcounts'] = wordcounts
