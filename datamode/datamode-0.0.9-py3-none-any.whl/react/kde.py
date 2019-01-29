import numpy as np
import statsmodels as sm
from datamode.utils.data import get_distinct_counts


from datamode.utils.utils import get_logger
log = get_logger(__name__)


# The maximum number of variables to build KDE plots for.
MAX_KDE_DISTINCTS = 5
MAX_KDE_SAMPLES = 5000

# This class should be passed the target variable column.
# It should generate the distinct values for that column, and subsequently row masks.
#
# Then, it can be passed an arbitrary column, mask that column based on the row masks,
# and return a KDE density plot for each category.
#
# If no target variable is passed, this class will generate a single KDE using all rows.
class KdeBuilder():
  def __init__(self, num_rows, col_target=None, *args, **kwargs):
    super(*args, **kwargs)

    self.num_rows = num_rows
    self.random_indexes = None

    # Target variable - can be None
    self.col_target = col_target

    # Row masks
    self.row_masks = None
    self.distincts = None


    # Generate random sample of row indexes
    # This is to keep the kernel set manageable
    if self.num_rows > MAX_KDE_SAMPLES:
      self.generate_random_row_sample_indexes()


    # Don't build KDEs unless we have a column and it
    # only has a few distinct values.
    # breakpoint()
    if self.col_target is not None:
      self.distincts = self.col_target.unique()

      if self.can_build():
        self.build_row_masks()

  # https://docs.scipy.org/doc/numpy-1.14.1/reference/generated/numpy.random.choice.html
  def generate_random_row_sample_indexes(self):
    try:
      # Set the seed
      # Arbitrary value - just want to keep it deterministic
      np.random.seed(42)

      # num_rows should be greater than MAX_KDE_SAMPLES
      self.random_indexes = np.random.choice(self.num_rows, MAX_KDE_SAMPLES, replace=False)

      # Downsample the target column if it's available
      if self.col_target is not None:
        self.col_target = self.col_target.iloc[self.random_indexes]

    finally:
      # Reset the seed no matter what
      np.random.seed()



  # We can build a kde when we're not striping by the target variable.
  # If are striping (col_target exists), then it should have a low number of distincts.
  def can_build(self):
    return self.col_target is None or self.distincts.shape[0] <= MAX_KDE_DISTINCTS


  def build_row_masks(self):
    self.row_masks = {}

    # log.debug(f'distincts: {self.distincts}')
    for distinct in self.distincts:
      distinct_str = str(distinct)
      self.row_masks[distinct_str] = self.col_target == distinct


  # Build a KDE density graph from either all the values, or striped by category if
  # the target variable is available.
  def build_kde(self, col):
    # log.debug(f'before sample shape={col.shape}')

    # Downsample column if necessary (for perf)
    if self.random_indexes is not None:
      col = col.iloc[self.random_indexes]

    log.debug(f'Downsampled kde input to shape={col.shape}')


    # log.debug(f'build_kde col={col}')
    # log.debug(f'build_kde self.col_target={self.col_target}')
    # log.debug(f'build_kde self.row_masks={self.row_masks}')
    # log.debug(f'build_kde self.distincts={self.distincts}')
    if self.col_target is not None:
      return self.build_multi_kde(col)
    else:
      return self.build_single_kde(col)


  # Vega expects all the points to be put in the same array, striped by the category value.
  # So we separate the data by the target variable value.
  def build_multi_kde(self, col):
    # self.valids = self.col.dropna()
    points = []

    # log.debug(f'distincts: {self.distincts}')

    # Create a column mask for each distinct value.
    for index, distinct in enumerate(self.distincts):

      distinct_str = str(distinct)
      # Boolean mask
      row_mask = self.row_masks[distinct_str]
      # log.debug(f'distinct={distinct}, row_mask={row_mask}')
      col_distinct = col[row_mask]

      # log.debug(col_distinct)

      if col_distinct.shape[0] > 0:
        points += self.build_single_kde(col_distinct, index, distinct)

    return points


  # cat_index is 0 so that Vega doesn't choke on a None value.
  def build_single_kde(self, col, cat_index=0, cat=None):
    # log.debug(f'cat: {cat}\n{col}')

    # Get rid of Nones
    col = col.dropna()
    if col.shape[0] == 0:
      return []


    # Statsmodels requires floats (for now)
    # See https://github.com/statsmodels/statsmodels/issues/1915
    col = col.astype(np.float64)

    kde = sm.nonparametric.kde.KDEUnivariate(col)
    kde.fit()

    y = kde.density
    y = np.amax(np.c_[np.zeros_like(y), y], axis=1)

    # if col.name == 'Parch':
      # yp = y
      # yp = np.select(y <= 0, y)
      # log.debug(f'kde.density is type {type(kde.density)}')

      # Set negative density values to 0
      # yp = np.select(y <= 0, y)
      # log.debug(f'kde={yp.tolist()}')
      # log.debug(f'info: {yp.shape}')


    cat_col = None
    if self.col_target is not None:
      cat_col = self.col_target.name

    # Take a single array and turn it into x, y values.
    return [{ 'x': support, 'y': density, 'cat': cat, 'cat_col': cat_col,  'cat_index': cat_index } for support, density in zip(kde.support, y)]
