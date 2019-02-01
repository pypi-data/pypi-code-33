import json
import pandas as pd
import numpy as np

# from datamode.utils.perf import do_profile, profiler_singleton
from pandas.api.types import is_string_dtype, is_numeric_dtype, is_bool_dtype


import gensim.utils
import gensim.parsing.preprocessing

# import Levenshtein

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from .core.transform_core import Transform
from .core.transform_result import TransformResult
from .columnartransform import ColumnarTransform
from .twocoltransform import TwoColTransform

from datamode.utils.wordvecs import WordVecLoader
from datamode.utils.data import ensure_matched_vector_dimensions, is_col_vector, vstack_col_to_array, is_val_none_equivalent
from datamode.utils.timer import CustomTimer


from datamode.utils.utils import get_logger
log = get_logger(__name__)


class PreprocessText(ColumnarTransform):
  def __init__(self, cols, lowercase=False, aggregation=None, remove_punctuation=False, remove_stopwords=False, *args, **kwargs):
    super().__init__(cols, *args, **kwargs)

    self.options['lowercase'] = lowercase
    self.options['aggregation'] = aggregation
    self.options['remove_stopwords'] = remove_stopwords
    self.options['remove_punctuation'] = remove_punctuation


  def validate_column(self, col):
    return is_string_dtype(col)


  def transform_values(self, context, index, *args):
    val = args[0]

    if is_val_none_equivalent(val):
      return None

    if self.options['lowercase']:
      val = val.lower()

    if self.options['remove_stopwords']:
      val = gensim.parsing.preprocessing.remove_stopwords(val)

    if self.options['remove_punctuation']:
      val = gensim.parsing.preprocessing.strip_punctuation(val)

    if self.options['aggregation'] == 'stem':
      val = gensim.parsing.preprocessing.stem(val)

    # gensim doesn't support lemmatization right now in Python3 - it depends on 'pattern' which is a python2 lib. pattern3 exists, but is fairly heavyweight, and gensim doesn't point to that anyways.
    # elif self.options['aggregation'] == 'lemmatize':
    #   val = gensim.utils.lemmatize(val)

    return val



# we can take care of downloading the files you need (but it will take a long time)
# Need to add caching so we don't redo the same thing twice. We can maintain a scratch folder with that data.
class VectorizeText(ColumnarTransform):
  def __init__(self, cols, vectorizer='tfidf', max_dims=None, *args, **kwargs):
    super().__init__(cols, *args, **kwargs)
    self.options['vectorizer'] = vectorizer
    self.options['max_dims'] = max_dims
    self.wvl = WordVecLoader.instance()


  def validate_column(self, col):
    return is_string_dtype(col)

  def process_single_column(self, col, colname):
    self.timer = CustomTimer(log, f'VectorizeText')

    vectorizer = self.options['vectorizer']
    if vectorizer == 'tfidf':
      vals = self.handle_tfidf(col)

    elif vectorizer == 'fasttext':
      vals = self.handle_fasttext(col)

    self.result.add_new_col(colname, vals, 'object')


  def handle_tfidf(self, col):
    self.vectorizer = TfidfVectorizer()
    vector_array = self.vectorizer.fit_transform(col.values)

    # Sum up the vectors by total tfidf and keep the top ones.
    # To do this, we build an interim vector which saves the indices to keep (the highest tfidf sums)
    # and then uses that to reindex into the larger array.
    max_dims = self.options.get('max_dims')
    if max_dims:
      vector_array = take_top_n_cols(vector_array, max_dims)

    vals = [vector for vector in vector_array]
    return vals


  def handle_fasttext(self, col):
    ft_model = self.wvl.get_ft_model()
    self.timer.report('Got model')

    col = col.dropna()

    vals = []
    for input_val in col.values:
      val = build_document_vector(input_val, ft_model)
      vals.append(val)

    # profiler_singleton.print_stats()

    return vals



class NamedEntityRecognition(ColumnarTransform):
  def __init__(self, cols, dataset='spacy', *args, **kwargs):
    super().__init__(*args, **kwargs)


# Calculate the distance between two vectors of equal dimensions.
# https://stackoverflow.com/questions/17627219/whats-the-fastest-way-in-python-to-calculate-cosine-similarity-given-sparse-mat/20687984
class VectorCosineDistance(TwoColTransform):
  def __init__(self, colname1, colname2, col_new, *args, **kwargs):
    super().__init__(colname1, colname2, *args, **kwargs)
    self.options['col_new'] = col_new

  def get_colnames(self):
    return self.options['colname1'], self.options['colname2']

  def validate_columns(self, col1, col2):
    return is_col_vector(col1) and is_col_vector(col2)


  def process_table(self):
    col1, col2 = self.get_cols()

    if not self.validate_columns(col1, col2):
      return


    distances = []
    for vector1, vector2 in zip(col1, col2):
      # Make the vectors 2D, required for cosine_similarity.
      vector1 = vector1.reshape(1, -1)
      vector2 = vector2.reshape(1, -1)

      # This is a no-op when the cols have the same dimensions, obviously
      vector1, vector2 = ensure_matched_vector_dimensions(vector1, vector2)

      distance = cosine_similarity(vector1, vector2)
      distances.append(distance[0][0])

    # For now, get the diagonal, which is just col1[x] paired with col2[x] - we don't need the other calculations.
    self.result.add_new_col(name=self.options['col_new'],
                            vals=distances,
                            dtype='float64')


  def set_new_dtype(self):
    self.new_dtype = 'int64'


# # Best for working with columns that are only a single word.
# class TextEditDistance(TwoColTransform):
#   def __init__(self, colname1, colname2, alg='levenshtein', *args, **kwargs):
#     super().__init__(colname1, colname2, *args, **kwargs)
#     self.options['alg'] = alg

#   def get_colnames(self):
#     return self.options['colname1'], self.options['colname2']

#   def validate_column(self, col):
#     return is_string_dtype(col)


#   def process_table(self):
#     col1, col2 = self.get_cols()

#     if not self.validate_columns(col1, col2):
#       return

#     fn = None
#     if self.options['alg'] == 'levenshtein':
#       fn = Levenshtein.distance

#     vals = []
#     for input1, input2 in zip(col1.values, col2.values):
#       val = fn(input1, input2)
#       vals.append(val)

#     self.result.add_new_col(name=self.options['col_new'],
#                             vals=vals,
#                             dtype='float64')


#   def validate_columns(self, col1, col2):
#     if is_string_dtype(col1) and is_string_dtype(col2):
#       return True

#   def set_new_dtype(self):
#     self.new_dtype = 'int64'


class KMeansClusterer(Transform):
  def __init__(self, include_cols=None, exclude_cols=None, col_new='kmeans', kmeans_options={}, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.options['include_cols'] = include_cols
    self.options['exclude_cols'] = exclude_cols
    self.options['kmeans_options'] = kmeans_options
    self.options['col_new'] = col_new


  def determine_colnames(self):
    include_colnames = self.options['include_cols']
    if include_colnames is None:
      include_colnames = self.result.df.columns

    if type(include_colnames) != list:
      include_colnames = [include_colnames]

    exclude_colnames = self.options['exclude_cols']
    if exclude_colnames:
      include_colnames = set(include_colnames) - set(exclude_colnames)
      include_colnames = list(include_colnames)

    return include_colnames

  def validate_columns(self, colnames):
    for colname in colnames:
      col = self.result.df[colname]

      # All columns should be coercible to a number, or be an existing vector already.
      if not (is_col_vector(col) or is_numeric_dtype(col) or is_bool_dtype(col)):
        raise Exception(f'All k-means input columns must be numerical, but column={colname} is not. All columns selected: {colnames}.')


  def process_table(self):
    colnames = self.determine_colnames()
    self.validate_columns(colnames)

    # Add defaults to kmeans_options
    kmeans_options = self.options['kmeans_options']
    if kmeans_options.get('n_clusters') is None:
      kmeans_options['n_clusters'] = 5

    # Combine the numerical columns and any vector columns into a single array.
    # Todo: perf?
    df = self.result.df[colnames]
    arrays = []
    for colname in df.columns:
      col = df[colname]
      if is_bool_dtype(col):
        col = col.as_int()
        arrays.append(col.values)
      elif is_numeric_dtype(col):
        arrays.append(col.values)
      else:
        colarray = vstack_col_to_array(col)
        arrays.append(colarray)

    train = np.hstack(arrays)

    # Run the alg
    kmeans = KMeans(**kmeans_options).fit(train)

    # Attach kmeans labels to each row
    # clustervals = kmeans.predict(train)

    # Add the new column
    col_newname = self.options['col_new']
    self.result.add_new_col(name=col_newname,
                            vals=kmeans.labels_.tolist(),
                            dtype='int64')


# Take the top n cols based on the sum of each column.
def take_top_n_cols(vectors, max_dims):
  counts = np.sum(vectors, axis=0)  # Sum each column across all rows

  # https://stackoverflow.com/questions/2828059/sorting-arrays-in-numpy-by-column
  # Sort the counts
  cols_keep = np.flip(counts.argsort())  # flip -> reverse

  # Take the top <max_dims> entries.
  cols_keep = cols_keep[:, :max_dims]

  # Then select only those columns from the main array.
  return vectors[:, cols_keep.A1]


# Vectorize a whole document by averaging its word vectors.
# @do_profile(profiler=profiler_singleton)
def build_document_vector(doc, model):
  # Get the sentences (currently, fastText
  sentences = doc.split('\n')

  # Preinit the array
  dims = model.get_dimension()
  sentence_count = len(sentences)
  sentence_vectors = np.zeros( (sentence_count, dims) )

  # Store the vectors for each word in the array
  for index, sentence in enumerate(sentences):
    sentence_vectors[index] = model.get_sentence_vector(sentence)

  # Average all the values to get a single vector for this document.
  single_vector = np.mean(sentence_vectors, axis=0)

  return single_vector
