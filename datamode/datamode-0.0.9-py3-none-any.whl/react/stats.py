import math, itertools, pprint
import pandas as pd
import numpy as np


# https://pandas.pydata.org/pandas-docs/stable/api.html#data-types-related-functionality
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_numeric_dtype
from sklearn.feature_extraction.text import TfidfVectorizer

from datamode.utils.data import is_value_nan_equivalent, is_col_vector, pad_csr_matrix, get_distinct_counts
from datamode.utils.timer import CustomTimer


from datamode.utils.utils import get_logger
log = get_logger(__name__)

# Currently, the Vega object expects data in this format (jsonl):
# data = {
#   'table': [
#     { label: 'Terminator', value_count: 21 },
#     { label: 'Commando', value_count: 81 },
#   ]
# }

BIN_COUNT = 8
BARCHART_MAX_ITEMS = 10


class StatsBuilder():
  def __init__(self, col, colname, timer, kde_builder, *args, **kwargs):
    super(*args, **kwargs)
    self.col = col
    self.colname = colname
    self.colviz_type = None
    self.distinct_counts = None

    # KDE and target variables
    # Can be None
    self.kde_builder = kde_builder


    self.timer = timer

  def build_column_stats(self):
    self.valids = self.col.dropna()
    self.distinct_counts = get_distinct_counts(self.col)
    self.colviz_type = self.determine_colviz_type()

    null_count = self.col.isna().sum()

    stats = {
      'col_stats': {
        'count': self.col.shape[0],
        'valids': self.col.shape[0] - null_count,
        'nulls': null_count,
      },
    }

    if self.distinct_counts is not None:
      stats['col_stats']['distincts'] = self.distinct_counts.shape[0]


    # If we don't have any colviz, just build summary stats.
    stats['summary'] = self.build_summary_stats()


    # Calculate KDE for any numerical columns
    if self.kde_builder and is_numeric_dtype(self.col) and self.kde_builder.can_build():
      timer = CustomTimer(log, f'KDE Builder: {self.col.name}')
      stats['density'] = self.kde_builder.build_kde(self.col)
      timer.end()


    if self.colviz_type == 'histogram':
      stats['bins'] = self.build_bins()
    elif self.colviz_type == 'vector':
      stats['vector_stats'] = self.build_vector_stats()
    elif self.colviz_type == 'wordcloud':
      stats['wordcounts'] = self.build_wordcloud_stats()

    if self.distinct_counts is not None:
      stats['distinct_counts'] = self.build_distinct_counts_jsonl()

    # log.debug(pprint.pformat(stats))

    # self.timer.report(f'col={colname} stats built: {self.distinct_counts.shape[0]}')
    # self.timer.report(f'col={colname} colviz_type={colviz_type}')

    return stats


  # https://pandas.pydata.org/pandas-docs/version/0.23.4/generated/pandas.cut.html
  # Note: Pandas extends the range by 0.1% on each side to include the entire dataset.
  # This means you can have a bin starting negative if the values start close to 0.
  def build_bins(self):
    # We can't work with null values, whether it's a numerical or datetime histogram.
    # If we only have null values, bail.
    if self.col.count() == 0:  # Count explicitly excludes nulls
      return []

    # Get rid of infinite values
    # See https://github.com/pandas-dev/pandas/issues/24314 for why this fails
    self.col = self.col.replace([np.inf, -np.inf], np.nan)

    cat = pd.cut(self.col, BIN_COUNT, include_lowest=True, duplicates='drop')
    counts_by_bins = cat.value_counts().sort_index() # In-place sort

    bins_jsonl = []
    for interval, count in counts_by_bins.iteritems():
      _bin = {
        'min': interval.left,
        'max': interval.right,
        'count': count,
      }

      bins_jsonl.append(_bin)

    return bins_jsonl


  # See https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.describe.html
  def build_summary_stats(self):
    if is_col_vector(self.col):
      return None

    ss_dict = self.col.describe(include='all').to_dict()
    if ss_dict.get('mean', None):
      # renaming these into friendlier keynames so Vega can read them
      try:
        ss_dict['q1'] = ss_dict.pop('25%')
        ss_dict['q2'] = ss_dict.pop('50%')
        ss_dict['q3'] = ss_dict.pop('75%')
      except:
        pass

    # Numpy arrays shouldn't be serialized/returned.
    # Todo: should we build stats for numpy arrays at all?
    if isinstance(ss_dict.get('top'), np.ndarray):
      nda = ss_dict['top']
      ss_dict['top'] = str(f'ndarray ({nda.shape})')

    return ss_dict


  def build_distinct_counts_jsonl(self):
    distinct_counts_jsonl = []

    # Itertools.islice returns the first N items of the iterator.
    for label, count in itertools.islice(self.distinct_counts.items(), BARCHART_MAX_ITEMS):
      # Patch for NaT - neither pandas nor jupyter want to fix the NaT issue
      # Also guard against Pandas nan and Python float nan
      # breakpoint()

      if is_value_nan_equivalent(label):
        label = None

      entry = {
        'label': label,
        'count': count
      }

      distinct_counts_jsonl.append(entry)

    return distinct_counts_jsonl



  def determine_colviz_type(self):
    # aak hack just for demo
    # TODO: REMOVE
    if self.col.name.lower() == 'state':
      return 'geo'

    if is_col_vector(self.col):
      return 'vector'

    # Datetimes will always get a histogram.
    if is_datetime64_any_dtype(self.col):
      return 'histogram'

    # if self.colname == 'reviewText_':
    #   return 'wordcloud'

    # If the values are all unique (except nulls), don't bother showing a histogram, just give the stats.
    # pandas .count() explicitly excludes nulls and null-equivalents
    if self.distinct_counts is not None:
      if (self.get_distinct_nonnulls() == self.col.count()) and is_numeric_dtype(self.col.dtype):
        return 'boxplot'

      if self.get_distinct_nonnulls() == self.col.count():
        return 'summary'

      # If we have a categorical variable (including low-ordinal numerics and bools), just use a barchart.
      if self.distinct_counts.shape[0] <= BARCHART_MAX_ITEMS:
        return 'barchart'

    if is_numeric_dtype(self.col.dtype):
      return 'histogram'


    if self.col.dtype == 'object':
      # todo: avoid nulls for this check
      # if type(self.col.iloc[0]) == str:
      #   return 'wordcloud'

      return 'barchart'
    else:
      raise Exception(f'Couldn\'t determine colviz type, locals={locals()}')


  # Todo: change back to countvectorizer.
  def build_wordcloud_stats(self):
    vectorizer = TfidfVectorizer()
    wordcount_vectors = vectorizer.fit_transform(self.valids)
    squashed = wordcount_vectors.toarray().sum(axis=0)
    words = vectorizer.get_feature_names()

    wordcounts = [{'text': word, 'count': count} for (word, count) in zip(words, squashed.tolist() ) if count > 0.2]
    return wordcounts


  def get_distinct_nonnulls(self):
    has_nulls = self.distinct_counts.index.isnull().any()
    counts = self.distinct_counts.shape[0]

    # Strip one from the total if it has nulls.
    return (counts - 1) if has_nulls else counts

  def build_vector_stats(self):
    dims = 0

    # breakpoint()
    if self.valids.shape[0] > 0:
      dims = self.valids.iloc[0].shape[0]

    vector_stats = {
      'dims': dims
    }

    return vector_stats
