from .core.transform_core import Transform

from datamode.utils.utils import get_logger
log = get_logger(__name__)


class TwoColTransform(Transform):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.options['colname1'] = args[0]
    self.options['colname1'] = args[1]


  def get_cols(self):
    colname1, colname2 = self.get_colnames()
    return self.result.df[colname1], self.result.df[colname2]

    self.result.set_source_cols.update([colname1, colname2])

  def process_table(self):
    context = None
    col1, col2 = self.get_cols()

    if not self.validate_columns(col1, col2):
      return

    vals = []

    # make a zip of the two cols
    for index, (oldval1, oldval2) in enumerate(zip( col1.tolist(), col2.tolist() )):
      try:
        val = self.transform_values(context, index, oldval1, oldval2)
      except (ValueError, TypeError):
        val = self.handle_invalid(context, index, oldval1, oldval2)

      vals.append(val)

    colname = self.options['col_new']
    # log.debug(f'Generated new column {colname}, adding to result.')
    # Also, any invalids/drops need to be properly masked

    self.result.add_new_col(name=colname,
                            vals=vals,
                            dtype=self.new_dtype)



  def handle_invalid(self, context, index, *args):
    # self.result.invalid_idxs.append(index)
    oldval1, oldval2 = args
    return self.get_invalid_replacement(oldval1, oldval2)


  ### Overridable
  def get_colnames(self):
    return self.options['col1'], self.options['col2']

  def validate_columns(self, col1, col2):
    return True

